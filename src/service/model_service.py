# src/service/model_service.py
import pandas as pd
from xgboost import XGBRegressor


class ModelService:
    def __init__(self):
        self.model = None  # placeholder for XGBoost later

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add lag features and any preprocessing.
        This is where you will add lags later.
        """
        df = df.copy()

        # ---- LAG PLACEHOLDER ----
        # Example (you can expand later):
        # df['inflation_lag_2'] = df['inflation'].shift(2)
        # df['gdp_lag_8'] = df['gdp'].shift(8)

        return df

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