import pandas as pd
import numpy as np
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class Predictor:
    def __init__(self):
        pass

    def predict(self, model: Any, features: pd.DataFrame, periods: int = 30) -> np.ndarray:
        try:
            if isinstance(model, dict) and "model" in model:
                return self._predict_lstm(model, features, periods)

            if hasattr(model, "predict"):
                preds = model.predict(features)
                return preds

            raise ValueError(f"Unsupported model type: {type(model)}")
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise

    def _predict_lstm(self, lstm_bundle: Dict, features: pd.DataFrame, periods: int) -> np.ndarray:
        model = lstm_bundle["model"]
        scaler_X = lstm_bundle["scaler_X"]
        scaler_y = lstm_bundle["scaler_y"]

        X_scaled = scaler_X.transform(features)
        preds = []

        current_seq = X_scaled[-30:] if len(X_scaled) >= 30 else X_scaled

        for _ in range(periods):
            input_seq = current_seq.reshape(1, current_seq.shape[0], current_seq.shape[1])
            pred_scaled = model.predict(input_seq, verbose=0)
            pred = scaler_y.inverse_transform(pred_scaled)
            preds.append(pred[0, 0])

            new_row = current_seq[-1].copy()
            new_row[0] = pred_scaled[0, 0]
            current_seq = np.vstack([current_seq[1:], new_row.reshape(1, -1)])

        return np.array(preds)

    def predict_with_confidence(self, model: Any, features: pd.DataFrame,
                                 periods: int = 30, confidence: float = 0.95) -> Dict[str, np.ndarray]:
        try:
            preds = self.predict(model, features, periods)

            if isinstance(model, dict) and "model" in model:
                std = np.std(preds) * 0.5
            elif hasattr(model, "estimators_"):
                tree_preds = np.array([t.predict(features.values.reshape(1, -1)) for t in model.estimators_])
                std = np.std(tree_preds, axis=0).flatten()
                if len(std) < periods:
                    std = np.full(periods, np.mean(std))
                std = std[:periods]
            else:
                std = np.std(preds) * 0.1

            from scipy import stats as scipy_stats
            z_score = scipy_stats.norm.ppf((1 + confidence) / 2)

            lower = preds - z_score * std
            upper = preds + z_score * std

            lower = np.maximum(lower, 0)

            result = {
                "predictions": preds,
                "lower_bound": lower,
                "upper_bound": upper,
                "confidence_level": confidence
            }
            logger.info(f"Predictions with {confidence*100}% confidence generated for {periods} periods")
            return result
        except Exception as e:
            logger.error(f"Confidence prediction error: {e}")
            raise

    def forecast_next_period(self, model: Any, df: pd.DataFrame,
                              periods: Optional[List[int]] = None) -> Dict[int, np.ndarray]:
        if periods is None:
            periods = [7, 30, 60, 90]

        forecasts = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        features = df[numeric_cols].copy()

        for period in periods:
            try:
                if hasattr(model, "predict"):
                    preds = model.predict(features.tail(period))
                    forecasts[period] = preds
                elif isinstance(model, dict) and "model" in model:
                    preds = self._predict_lstm(model, features, period)
                    forecasts[period] = preds
                else:
                    logger.warning(f"Could not forecast for period {period}")
                    forecasts[period] = np.array([])

                logger.info(f"Forecast for {period} periods generated")
            except Exception as e:
                logger.error(f"Error forecasting period {period}: {e}")
                forecasts[period] = np.array([])

        return forecasts
