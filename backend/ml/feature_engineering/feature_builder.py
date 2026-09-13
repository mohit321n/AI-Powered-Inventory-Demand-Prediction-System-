import pandas as pd
import numpy as np
import logging
from typing import Optional, List
from pandas.tseries.holiday import USFederalHolidayCalendar

logger = logging.getLogger(__name__)


class FeatureBuilder:
    def __init__(self, date_column: Optional[str] = None, target_column: Optional[str] = None):
        self.date_column = date_column
        self.target_column = target_column

    def _get_date_column(self, df: pd.DataFrame) -> str:
        if self.date_column and self.date_column in df.columns:
            return self.date_column
        for col in df.columns:
            if "date" in col.lower():
                return col
        raise ValueError("No date column found or specified")

    def _get_target_column(self, df: pd.DataFrame) -> str:
        if self.target_column and self.target_column in df.columns:
            return self.target_column
        for col in df.columns:
            if any(kw in col.lower() for kw in ["demand", "sales", "quantity", "units_sold", "target", "y"]):
                return col
        raise ValueError("No target column found or specified")

    def create_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        date_col = self._get_date_column(df)

        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])

        df["day"] = df[date_col].dt.day
        df["week"] = df[date_col].dt.isocalendar().week.astype(int)
        df["month"] = df[date_col].dt.month
        df["quarter"] = df[date_col].dt.quarter
        df["year"] = df[date_col].dt.year
        df["day_of_week"] = df[date_col].dt.dayofweek
        df["is_weekend"] = (df[date_col].dt.dayofweek >= 5).astype(int)

        logger.info("Time features created: day, week, month, quarter, year, day_of_week, is_weekend")
        return df

    def create_lag_features(self, df: pd.DataFrame, lags: Optional[List[int]] = None) -> pd.DataFrame:
        df = df.copy()
        target_col = self._get_target_column(df)

        if lags is None:
            lags = [1, 7, 14, 30]

        for lag in lags:
            df[f"lag_{lag}"] = df[target_col].shift(lag)

        logger.info(f"Lag features created for lags: {lags}")
        return df

    def create_rolling_features(self, df: pd.DataFrame, windows: Optional[List[int]] = None) -> pd.DataFrame:
        df = df.copy()
        target_col = self._get_target_column(df)

        if windows is None:
            windows = [7, 14, 30]

        for w in windows:
            df[f"rolling_mean_{w}"] = df[target_col].shift(1).rolling(window=w, min_periods=1).mean()
            df[f"rolling_std_{w}"] = df[target_col].shift(1).rolling(window=w, min_periods=1).std()

        logger.info(f"Rolling features created for windows: {windows}")
        return df

    def create_calendar_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        date_col = self._get_date_column(df)

        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])

        try:
            cal = USFederalHolidayCalendar()
            holidays = cal.holidays(start=df[date_col].min(), end=df[date_col].max())
            df["is_holiday"] = df[date_col].isin(holidays).astype(int)
        except Exception:
            df["is_holiday"] = 0
            logger.warning("Could not generate holiday calendar, setting is_holiday=0")

        df["is_month_start"] = df[date_col].dt.is_month_start.astype(int)
        df["is_month_end"] = df[date_col].dt.is_month_end.astype(int)
        df["is_quarter_start"] = df[date_col].dt.is_quarter_start.astype(int)
        df["is_quarter_end"] = df[date_col].dt.is_quarter_end.astype(int)
        df["is_year_start"] = df[date_col].dt.is_year_start.astype(int)
        df["is_year_end"] = df[date_col].dt.is_year_end.astype(int)

        if "promotion" not in df.columns:
            df["promotion"] = 0
        df["is_promotion"] = df["promotion"].astype(int)

        logger.info("Calendar features created: holidays, month/quarter/year boundaries, promotions")
        return df

    def create_demand_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        target_col = self._get_target_column(df)

        if not pd.api.types.is_datetime64_any_dtype(df[self._get_date_column(df)]):
            df[self._get_date_column(df)] = pd.to_datetime(df[self._get_date_column(df)])

        date_col = self._get_date_column(df)
        df_sorted = df.sort_values(date_col).copy()
        df_sorted["prev_month_demand"] = df_sorted[target_col].shift(30)
        df_sorted["prev_year_demand"] = df_sorted[target_col].shift(365)
        df_sorted["prev_month_avg"] = df_sorted[target_col].rolling(window=30, min_periods=1).mean().shift(1)
        df_sorted["prev_year_avg"] = df_sorted[target_col].rolling(window=365, min_periods=1).mean().shift(1)

        df = df_sorted
        logger.info("Demand features created: prev_month_demand, prev_year_demand, prev_month_avg, prev_year_avg")
        return df

    def build_features(self, df: pd.DataFrame, lags: Optional[List[int]] = None,
                       windows: Optional[List[int]] = None) -> pd.DataFrame:
        logger.info("Starting feature engineering pipeline")
        df = self.create_time_features(df)
        df = self.create_lag_features(df, lags)
        df = self.create_rolling_features(df, windows)
        df = self.create_calendar_features(df)
        df = self.create_demand_features(df)
        logger.info(f"Feature engineering complete. Shape: {df.shape}")
        return df
