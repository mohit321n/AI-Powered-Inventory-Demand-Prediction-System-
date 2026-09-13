import pandas as pd
import numpy as np
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DataCleaner:
    def __init__(self, date_column: Optional[str] = None):
        self.date_column = date_column
        self.df = None

    def load_data(self, filepath: str) -> pd.DataFrame:
        try:
            self.df = pd.read_csv(filepath)
            logger.info(f"Loaded data from {filepath}: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            return self.df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def handle_missing_values(self, strategy: str = "auto", threshold: float = 0.5) -> pd.DataFrame:
        if self.df is None:
            raise ValueError("No data loaded. Call load_data first.")

        null_pct = self.df.isnull().mean()

        cols_to_drop = null_pct[null_pct > threshold].index.tolist()
        if cols_to_drop:
            logger.info(f"Dropping columns with >{threshold*100}% missing: {cols_to_drop}")
            self.df.drop(columns=cols_to_drop, inplace=True)

        if strategy == "auto":
            for col in self.df.columns:
                if self.df[col].isnull().sum() == 0:
                    continue
                if self.df[col].dtype in ["float64", "int64"]:
                    self.df[col].fillna(self.df[col].median(), inplace=True)
                else:
                    mode_val = self.df[col].mode()
                    if len(mode_val) > 0:
                        self.df[col].fillna(mode_val.iloc[0], inplace=True)
                    else:
                        self.df.dropna(subset=[col], inplace=True)
        elif strategy == "drop":
            self.df.dropna(inplace=True)
        elif strategy == "fill":
            for col in self.df.columns:
                if self.df[col].dtype in ["float64", "int64"]:
                    self.df[col].fillna(self.df[col].mean(), inplace=True)

        logger.info(f"Missing values handled. Remaining shape: {self.df.shape}")
        return self.df

    def handle_duplicates(self) -> pd.DataFrame:
        if self.df is None:
            raise ValueError("No data loaded. Call load_data first.")

        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        removed = before - len(self.df)
        logger.info(f"Removed {removed} duplicate rows")
        return self.df

    def validate_dates(self) -> pd.DataFrame:
        if self.df is None:
            raise ValueError("No data loaded. Call load_data first.")

        date_col = self.date_column
        if date_col is None:
            for col in self.df.columns:
                if "date" in col.lower():
                    date_col = col
                    break

        if date_col is None or date_col not in self.df.columns:
            logger.warning("No date column found or specified")
            return self.df

        try:
            self.df[date_col] = pd.to_datetime(self.df[date_col], infer_datetime_format=True, errors="coerce")
            invalid = self.df[date_col].isnull().sum()
            if invalid > 0:
                logger.warning(f"{invalid} invalid dates found and set to NaT")
                self.df.dropna(subset=[date_col], inplace=True)
            self.df.sort_values(date_col, inplace=True)
            self.df.reset_index(drop=True, inplace=True)
            logger.info(f"Dates validated for column '{date_col}'")
        except Exception as e:
            logger.error(f"Date validation error: {e}")

        return self.df

    def detect_outliers(self, columns: Optional[list] = None, factor: float = 1.5) -> pd.DataFrame:
        if self.df is None:
            raise ValueError("No data loaded. Call load_data first.")

        if columns is None:
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()

        outlier_info = {}
        for col in columns:
            q1 = self.df[col].quantile(0.25)
            q3 = self.df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - factor * iqr
            upper = q3 + factor * iqr
            mask = (self.df[col] < lower) | (self.df[col] > upper)
            count = mask.sum()
            if count > 0:
                self.df.loc[mask, col] = np.clip(self.df.loc[mask, col], lower, upper)
                outlier_info[col] = count

        if outlier_info:
            logger.info(f"Outliers capped using IQR method: {outlier_info}")
        else:
            logger.info("No outliers detected")

        return self.df

    def clean(self, filepath: Optional[str] = None, date_column: Optional[str] = None) -> pd.DataFrame:
        if filepath:
            self.load_data(filepath)
        if date_column:
            self.date_column = date_column

        if self.df is None:
            raise ValueError("No data to clean")

        logger.info("Starting cleaning pipeline")
        self.handle_missing_values()
        self.handle_duplicates()
        self.validate_dates()
        self.detect_outliers()
        logger.info(f"Cleaning complete. Final shape: {self.df.shape}")
        return self.df
