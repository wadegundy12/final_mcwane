# src/service/model_service.py
import pandas as pd
import numpy as np
from config.settings import FUTURE_MONTHS, INFLATION_LAGS, ROLLING_WINDOWS, SALES_LAGS, TARGET_COL
from xgboost import XGBRegressor


class ModelService:
    def __init__(self):
        params = {
            'n_estimators': 397,
            'learning_rate': 0.011,
            'max_depth': 3,
            'min_child_weight': 5,
            'subsample': 0.7,
            'colsample_bytree': 0.9,
            'reg_alpha': 0.075,
            'reg_lambda': 0.05,
            'objective': 'reg:squarederror',
            'random_state': 42
        }
        self.model = XGBRegressor(**params)

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:

        features = df.copy().sort_values("date").reset_index(drop=True)
        features["month"] = features["date"].dt.month
        features["quarter"] = features["date"].dt.quarter
        features["month_sin"] = np.sin(2 * np.pi * features["month"] / 12.0)

        baseline_features = ["quarter", "month", "month_sin"]

        for lag in SALES_LAGS:
            col = f"sales_lag_{lag}"
            features[col] = features[TARGET_COL].shift(lag)
            baseline_features.append(col)

        shifted_target = features[TARGET_COL].shift(1)
        for window in ROLLING_WINDOWS:
            mean_col = f"sales_roll_mean_{window}"
            std_col = f"sales_roll_std_{window}"
            features[mean_col] = shifted_target.rolling(window).mean()
            features[std_col] = shifted_target.rolling(window).std()
            baseline_features.extend([mean_col, std_col])

        
        inflation_features: list[str] = []

        for lag in INFLATION_LAGS:
            feature_name =  f"inflation_lag_{lag}"
            features[feature_name] = features["inflation"].shift(lag)
            inflation_features.append(feature_name)
        

        return features

    def train(self, df: pd.DataFrame):
        df = df.dropna().reset_index(drop=True)
        X = df.drop(columns=[TARGET_COL, "date"])
        y = df[TARGET_COL]

        self.model.fit(X, y)

        return

    def forecast(self, df: pd.DataFrame) -> pd.DataFrame:
        future = df.copy()
        for _ in range(FUTURE_MONTHS):
            last_row = future.iloc[-1:].copy()
            last_row["date"] += pd.DateOffset(months=1)
            last_row["month"] = last_row["date"].dt.month
            last_row["quarter"] = last_row["date"].dt.quarter
            last_row["month_sin"] = np.sin(2 * np.pi * last_row["month"] / 12.0)

            # Update lag features
            for lag in SALES_LAGS:
                last_row[f"sales_lag_{lag}"] = future[TARGET_COL].shift(lag).iloc[-1]

            shifted_target = future[TARGET_COL].shift(1)
            for window in ROLLING_WINDOWS:
                mean_col = f"sales_roll_mean_{window}"
                std_col = f"sales_roll_std_{window}"
                last_row[mean_col] = shifted_target.rolling(window).mean().iloc[-1]
                last_row[std_col] = shifted_target.rolling(window).std().iloc[-1]

            

            for lag in INFLATION_LAGS:
                feature_name =  f"inflation_lag_{lag}"
                last_row[feature_name] = future["inflation"].shift(lag).iloc[-1]
            
            # Predict next value
            X_pred = last_row.drop(columns=[TARGET_COL, "date"])
            next_value = self.model.predict(X_pred)[0]
            last_row[TARGET_COL] = next_value
            future = pd.concat([future, last_row], ignore_index=True)

        return future
    



    def _build_base_features(sales_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        features = sales_df.copy().sort_values("date").reset_index(drop=True)
        features["month"] = features["date"].dt.month
        features["quarter"] = features["date"].dt.quarter
        features["month_sin"] = np.sin(2 * np.pi * features["month"] / 12.0)

        baseline_features = ["quarter", "month", "month_sin"]

        for lag in SALES_LAGS:
            col = f"sales_lag_{lag}"
            features[col] = features[TARGET_COL].shift(lag)
            baseline_features.append(col)

        shifted_target = features[TARGET_COL].shift(1)
        for window in ROLLING_WINDOWS:
            mean_col = f"sales_roll_mean_{window}"
            std_col = f"sales_roll_std_{window}"
            features[mean_col] = shifted_target.rolling(window).mean()
            features[std_col] = shifted_target.rolling(window).std()
            baseline_features.extend([mean_col, std_col])

        return features, baseline_features