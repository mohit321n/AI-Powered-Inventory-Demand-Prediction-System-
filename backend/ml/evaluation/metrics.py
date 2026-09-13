import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelEvaluator:
    def __init__(self):
        pass

    def calculate_mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        from sklearn.metrics import mean_absolute_error
        return mean_absolute_error(y_true, y_pred)

    def calculate_rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        from sklearn.metrics import mean_squared_error
        return np.sqrt(mean_squared_error(y_true, y_pred))

    def calculate_mape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)

        mask = y_true != 0
        if not mask.any():
            logger.warning("All y_true values are zero, MAPE is undefined")
            return float("inf")

        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        return float(mape)

    def calculate_r2(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        from sklearn.metrics import r2_score
        return r2_score(y_true, y_pred)

    def evaluate_all(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        metrics = {
            "mae": self.calculate_mae(y_true, y_pred),
            "rmse": self.calculate_rmse(y_true, y_pred),
            "mape": self.calculate_mape(y_true, y_pred),
            "r2": self.calculate_r2(y_true, y_pred)
        }
        logger.info(f"Evaluation results: {metrics}")
        return metrics

    def compare_models_results(self, results_dict: Dict[str, Dict[str, float]]) -> pd.DataFrame:
        if not results_dict:
            raise ValueError("No results provided for comparison")

        rows = []
        for model_name, metrics in results_dict.items():
            row = {"model": model_name}
            row.update(metrics)
            rows.append(row)

        comparison_df = pd.DataFrame(rows)
        comparison_df = comparison_df.sort_values("rmse", ascending=True)
        comparison_df.reset_index(drop=True, inplace=True)

        if "r2" in comparison_df.columns:
            best_idx = comparison_df["r2"].idxmax()
            comparison_df["rank"] = range(1, len(comparison_df) + 1)
            comparison_df.loc[best_idx, "rank"] = 1

        logger.info(f"Model comparison table generated with {len(comparison_df)} models")
        return comparison_df
