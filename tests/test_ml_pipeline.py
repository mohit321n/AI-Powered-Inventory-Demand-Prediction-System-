import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class TestDataCleaning:
    def test_data_cleaning(self):
        from ml.preprocessing.data_cleaner import DataCleaner

        cleaner = DataCleaner(date_column="date")
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        quantities = np.random.randint(10, 100, size=100).astype(float)
        df = pd.DataFrame({"date": dates, "demand": quantities})

        df.loc[5, "demand"] = np.nan
        df.loc[10, "demand"] = np.nan
        df.loc[15, "demand"] = np.nan

        cleaner.df = df.copy()
        result = cleaner.handle_missing_values(strategy="auto")
        assert result.isnull().sum().sum() == 0
        assert len(result) == 100

    def test_data_cleaning_drop_duplicates(self):
        from ml.preprocessing.data_cleaner import DataCleaner

        cleaner = DataCleaner()
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=5, freq="D"),
            "demand": [10, 20, 10, 30, 20],
        })
        df = pd.concat([df, df.iloc[[0, 2]]], ignore_index=True)

        cleaner.df = df.copy()
        result = cleaner.handle_duplicates()
        assert len(result) == 5

    def test_data_cleaning_outlier_detection(self):
        from ml.preprocessing.data_cleaner import DataCleaner

        cleaner = DataCleaner()
        values = np.concatenate([np.random.normal(50, 5, 95), [200, 210, 220, 0, -50]])
        df = pd.DataFrame({"value": values})

        cleaner.df = df.copy()
        result = cleaner.detect_outliers(columns=["value"], factor=1.5)
        assert result["value"].max() <= 220

    def test_data_cleaning_no_data_raises(self):
        from ml.preprocessing.data_cleaner import DataCleaner

        cleaner = DataCleaner()
        with pytest.raises(ValueError, match="No data loaded"):
            cleaner.handle_missing_values()


class TestFeatureEngineering:
    def test_feature_engineering(self):
        from ml.feature_engineering.feature_builder import FeatureBuilder

        builder = FeatureBuilder(date_column="date", target_column="demand")
        dates = pd.date_range(start="2024-01-01", periods=90, freq="D")
        df = pd.DataFrame({
            "date": dates,
            "demand": np.random.randint(10, 50, size=90),
        })

        result = builder.create_time_features(df)
        assert "day" in result.columns
        assert "month" in result.columns
        assert "year" in result.columns
        assert "day_of_week" in result.columns
        assert "is_weekend" in result.columns

    def test_lag_features(self):
        from ml.feature_engineering.feature_builder import FeatureBuilder

        builder = FeatureBuilder(date_column="date", target_column="demand")
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=30, freq="D"),
            "demand": range(30),
        })

        result = builder.create_lag_features(df, lags=[1, 7])
        assert "lag_1" in result.columns
        assert "lag_7" in result.columns
        assert result["lag_1"].iloc[1] == 0
        assert result["lag_7"].iloc[7] == 0

    def test_rolling_features(self):
        from ml.feature_engineering.feature_builder import FeatureBuilder

        builder = FeatureBuilder(date_column="date", target_column="demand")
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=30, freq="D"),
            "demand": range(30),
        })

        result = builder.create_rolling_features(df, windows=[7])
        assert "rolling_mean_7" in result.columns
        assert "rolling_std_7" in result.columns

    def test_calendar_features(self):
        from ml.feature_engineering.feature_builder import FeatureBuilder

        builder = FeatureBuilder(date_column="date", target_column="demand")
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=30, freq="D"),
            "demand": range(30),
        })

        result = builder.create_calendar_features(df)
        assert "is_holiday" in result.columns
        assert "is_month_start" in result.columns
        assert "is_weekend" in result.columns


class TestModelEvaluationMetrics:
    def test_model_evaluation_metrics(self):
        from ml.evaluation.metrics import ModelEvaluator

        evaluator = ModelEvaluator()
        y_true = np.array([10, 20, 30, 40, 50])
        y_pred = np.array([12, 18, 32, 38, 52])

        metrics = evaluator.evaluate_all(y_true, y_pred)
        assert "mae" in metrics
        assert "rmse" in metrics
        assert "mape" in metrics
        assert "r2" in metrics
        assert metrics["mae"] > 0
        assert metrics["rmse"] > 0
        assert metrics["r2"] > 0.9

    def test_mape_calculation(self):
        from ml.evaluation.metrics import ModelEvaluator

        evaluator = ModelEvaluator()
        y_true = np.array([100, 200, 300])
        y_pred = np.array([110, 190, 310])

        mape = evaluator.calculate_mape(y_true, y_pred)
        assert 0 < mape < 10

    def test_mape_with_zeros(self):
        from ml.evaluation.metrics import ModelEvaluator

        evaluator = ModelEvaluator()
        y_true = np.array([0, 0, 0])
        y_pred = np.array([1, 2, 3])

        mape = evaluator.calculate_mape(y_true, y_pred)
        assert mape == float("inf")

    def test_compare_models_results(self):
        from ml.evaluation.metrics import ModelEvaluator

        evaluator = ModelEvaluator()
        results = {
            "model_a": {"mae": 5.0, "rmse": 7.0, "r2": 0.95},
            "model_b": {"mae": 3.0, "rmse": 4.5, "r2": 0.98},
            "model_c": {"mae": 8.0, "rmse": 10.0, "r2": 0.90},
        }

        comparison = evaluator.compare_models_results(results)
        assert len(comparison) == 3
        assert comparison.iloc[0]["model"] == "model_b"

    def test_compare_models_empty_raises(self):
        from ml.evaluation.metrics import ModelEvaluator

        evaluator = ModelEvaluator()
        with pytest.raises(ValueError):
            evaluator.compare_models_results({})


class TestLinearRegressionTraining:
    def test_linear_regression_training(self):
        from ml.training.model_trainer import ModelTrainer

        trainer = ModelTrainer()
        np.random.seed(42)
        X = pd.DataFrame({"feature_1": np.random.randn(100), "feature_2": np.random.randn(100)})
        y = pd.Series(2 * X["feature_1"] + 3 * X["feature_2"] + np.random.randn(100) * 0.1)

        model = trainer.train_linear_regression(X, y)
        assert model is not None
        assert hasattr(model, "predict")

        predictions = model.predict(X)
        assert len(predictions) == 100
        assert np.all(np.isfinite(predictions))

    def test_random_forest_training(self):
        from ml.training.model_trainer import ModelTrainer

        trainer = ModelTrainer()
        np.random.seed(42)
        X = pd.DataFrame({"f1": np.random.randn(100), "f2": np.random.randn(100)})
        y = pd.Series(np.sin(X["f1"]) + X["f2"] ** 2)

        model = trainer.train_random_forest(X, y, n_estimators=10, random_state=42)
        assert model is not None
        predictions = model.predict(X)
        assert len(predictions) == 100

    def test_model_comparison_and_selection(self):
        from ml.training.model_trainer import ModelTrainer

        trainer = ModelTrainer()
        np.random.seed(42)
        X = pd.DataFrame({"f1": np.random.randn(100), "f2": np.random.randn(100)})
        y = pd.Series(2 * X["f1"] + X["f2"] + np.random.randn(100) * 0.1)

        trainer.train_linear_regression(X, y)
        trainer.train_random_forest(X, y, n_estimators=10, random_state=42)

        comparison = trainer.compare_models(X, y, X, y)
        assert "linear_regression" in comparison
        assert "random_forest" in comparison
        assert all("mae" in v for v in comparison.values())
        assert all("rmse" in v for v in comparison.values())

        best = trainer.select_best_model(comparison)
        assert best in comparison


class TestForecastGeneration:
    def test_forecast_generation(self):
        from ml.forecasting.predictor import Predictor
        from sklearn.linear_model import LinearRegression

        predictor = Predictor()
        np.random.seed(42)
        X_train = pd.DataFrame({"f1": np.random.randn(100), "f2": np.random.randn(100)})
        y_train = pd.Series(2 * X_train["f1"] + X_train["f2"] + np.random.randn(100) * 0.1)

        model = LinearRegression()
        model.fit(X_train, y_train)

        X_future = pd.DataFrame({"f1": np.random.randn(30), "f2": np.random.randn(30)})
        preds = predictor.predict(model, X_future, periods=30)
        assert len(preds) == 30
        assert np.all(np.isfinite(preds))

    def test_predict_with_confidence(self):
        from ml.forecasting.predictor import Predictor
        from sklearn.ensemble import RandomForestRegressor

        predictor = Predictor()
        np.random.seed(42)
        X = pd.DataFrame({"f1": np.random.randn(100), "f2": np.random.randn(100)})
        y = pd.Series(2 * X["f1"] + X["f2"] + np.random.randn(100) * 0.1)

        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)

        result = predictor.predict_with_confidence(model, X, periods=10, confidence=0.95)
        assert "predictions" in result
        assert "lower_bound" in result
        assert "upper_bound" in result
        assert len(result["predictions"]) == 10
        assert np.all(result["lower_bound"] <= result["predictions"])
        assert np.all(result["upper_bound"] >= result["predictions"])
