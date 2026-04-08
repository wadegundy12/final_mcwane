# src/service/model_service.py
import pandas as pd
import numpy as np
from config.settings import INFLATION_LAGS, ROLLING_WINDOWS, SALES_LAGS, TARGET_COL
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

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:

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

    def train(self, df: pd.DataFrame, target_col: str):
        """
        Train model (placeholder for now).
        """
        df = df.dropna()

        X = df.drop(columns=[target_col])
        y = df[target_col]

        # ---- MODEL PLACEHOLDER ----
        # Later: plug in XGBoost here
        self.model = {
            "trained": True,
            "features": X.columns.tolist()
        }

        return self.model

    def forecast(self, df: pd.DataFrame, periods: int = 3):
        """
        Predict into the future (placeholder).
        """
        # ---- FORECAST PLACEHOLDER ----
        future = pd.DataFrame({
            "forecast": [0] * periods
        })

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