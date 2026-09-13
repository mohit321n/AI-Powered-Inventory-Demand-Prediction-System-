import pandas as pd
import numpy as np
import logging
import joblib
import pickle
from typing import Optional, Dict, Any, Tuple

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)


class ModelTrainer:
    def __init__(self):
        self.models = {}
        self.best_model = None

    def train_linear_regression(self, X_train: pd.DataFrame, y_train: pd.Series) -> Any:
        try:
            model = LinearRegression()
            model.fit(X_train, y_train)
            self.models["linear_regression"] = model
            logger.info("Linear Regression trained successfully")
            return model
        except Exception as e:
            logger.error(f"Error training Linear Regression: {e}")
            raise

    def train_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series,
                            n_estimators: int = 100, random_state: int = 42) -> Any:
        try:
            model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state, n_jobs=-1)
            model.fit(X_train, y_train)
            self.models["random_forest"] = model
            logger.info("Random Forest trained successfully")
            return model
        except Exception as e:
            logger.error(f"Error training Random Forest: {e}")
            raise

    def train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series,
                       n_estimators: int = 100, learning_rate: float = 0.1,
                       random_state: int = 42) -> Any:
        try:
            from xgboost import XGBRegressor
            model = XGBRegressor(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                random_state=random_state,
                n_jobs=-1,
                verbosity=0
            )
            model.fit(X_train, y_train)
            self.models["xgboost"] = model
            logger.info("XGBoost trained successfully")
            return model
        except ImportError:
            logger.warning("XGBoost not installed. Skipping XGBoost training.")
            return None
        except Exception as e:
            logger.error(f"Error training XGBoost: {e}")
            raise

    def train_lightgbm(self, X_train: pd.DataFrame, y_train: pd.Series,
                        n_estimators: int = 100, learning_rate: float = 0.1,
                        random_state: int = 42) -> Any:
        try:
            from lightgbm import LGBMRegressor
            model = LGBMRegressor(
                n_estimators=n_estimators,
                learning_rate=learning_rate,
                random_state=random_state,
                n_jobs=-1,
                verbose=-1
            )
            model.fit(X_train, y_train)
            self.models["lightgbm"] = model
            logger.info("LightGBM trained successfully")
            return model
        except ImportError:
            logger.warning("LightGBM not installed. Skipping LightGBM training.")
            return None
        except Exception as e:
            logger.error(f"Error training LightGBM: {e}")
            raise

    def train_lstm(self, X_train: pd.DataFrame, y_train: pd.Series,
                    lookback: int = 30, epochs: int = 50, batch_size: int = 32) -> Any:
        try:
            import tensorflow as tf
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from sklearn.preprocessing import MinMaxScaler

            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()

            X_scaled = scaler_X.fit_transform(X_train)
            y_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1))

            X_seq, y_seq = [], []
            for i in range(lookback, len(X_scaled)):
                X_seq.append(X_scaled[i - lookback:i])
                y_seq.append(y_scaled[i])
            X_seq = np.array(X_seq)
            y_seq = np.array(y_seq)

            model = Sequential([
                LSTM(64, return_sequences=True, input_shape=(X_seq.shape[1], X_seq.shape[2])),
                Dropout(0.2),
                LSTM(32, return_sequences=False),
                Dropout(0.2),
                Dense(16, activation="relu"),
                Dense(1)
            ])
            model.compile(optimizer="adam", loss="mse")
            model.fit(X_seq, y_seq, epochs=epochs, batch_size=batch_size, verbose=0, validation_split=0.1)

            self.models["lstm"] = {"model": model, "scaler_X": scaler_X, "scaler_y": scaler_y}
            logger.info("LSTM trained successfully")
            return self.models["lstm"]
        except ImportError:
            logger.warning("TensorFlow not installed. Skipping LSTM training.")
            return None
        except Exception as e:
            logger.error(f"Error training LSTM: {e}")
            raise

    def train_prophet(self, df: pd.DataFrame, date_column: Optional[str] = None,
                      target_column: Optional[str] = None) -> Any:
        try:
            from prophet import Prophet

            date_col = date_column or next((c for c in df.columns if "date" in c.lower()), None)
            target_col = target_column or next((c for c in df.columns if any(k in c.lower() for k in ["demand", "sales", "quantity"])), None)

            if not date_col or not target_col:
                raise ValueError("Could not identify date and target columns")

            prophet_df = df[[date_col, target_col]].copy()
            prophet_df.columns = ["ds", "y"]
            prophet_df["ds"] = pd.to_datetime(prophet_df["ds"])
            prophet_df.dropna(inplace=True)

            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            model.fit(prophet_df)
            self.models["prophet"] = model
            logger.info("Prophet trained successfully")
            return model
        except ImportError:
            logger.warning("Prophet not installed. Skipping Prophet training.")
            return None
        except Exception as e:
            logger.error(f"Error training Prophet: {e}")
            raise

    def compare_models(self, X_train: pd.DataFrame, y_train: pd.Series,
                       X_val: pd.DataFrame, y_val: pd.Series) -> Dict[str, Dict[str, float]]:
        results = {}

        self.train_linear_regression(X_train, y_train)
        self.train_random_forest(X_train, y_train)
        self.train_xgboost(X_train, y_train)
        self.train_lightgbm(X_train, y_train)

        from ml.evaluation.metrics import ModelEvaluator
        evaluator = ModelEvaluator()

        if "linear_regression" in self.models:
            preds = self.models["linear_regression"].predict(X_val)
            results["linear_regression"] = evaluator.evaluate_all(y_val, preds)

        if "random_forest" in self.models:
            preds = self.models["random_forest"].predict(X_val)
            results["random_forest"] = evaluator.evaluate_all(y_val, preds)

        if "xgboost" in self.models:
            preds = self.models["xgboost"].predict(X_val)
            results["xgboost"] = evaluator.evaluate_all(y_val, preds)

        if "lightgbm" in self.models:
            preds = self.models["lightgbm"].predict(X_val)
            results["lightgbm"] = evaluator.evaluate_all(y_val, preds)

        logger.info(f"Model comparison complete. Models evaluated: {list(results.keys())}")
        return results

    def select_best_model(self, comparison: Dict[str, Dict[str, float]]) -> str:
        if not comparison:
            raise ValueError("No model comparison results available")

        best_model = min(comparison, key=lambda m: comparison[m]["rmse"])
        self.best_model = self.models.get(best_model)
        logger.info(f"Best model selected: {best_model} (RMSE: {comparison[best_model]['rmse']:.4f})")
        return best_model

    def save_model(self, model: Any, path: str) -> None:
        try:
            with open(path, "wb") as f:
                pickle.dump(model, f)
            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise

    def load_model(self, path: str) -> Any:
        try:
            with open(path, "rb") as f:
                model = pickle.load(f)
            logger.info(f"Model loaded from {path}")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
