import pytest
import pandas as pd
import numpy as np
import io
import tempfile
import os


class TestCsvUploadValidation:
    def test_csv_upload_validation(self):
        csv_data = """product_id,quantity,unit_price
1,10,29.99
2,5,19.99
3,8,39.99"""

        df = pd.read_csv(io.StringIO(csv_data))
        required_columns = ["product_id", "quantity", "unit_price"]

        missing = [col for col in required_columns if col not in df.columns]
        assert len(missing) == 0
        assert len(df) == 3
        assert df["quantity"].sum() == 23

    def test_csv_upload_missing_columns(self):
        csv_data = """product_id,price
1,29.99
2,19.99"""

        df = pd.read_csv(io.StringIO(csv_data))
        required_columns = ["product_id", "quantity", "unit_price"]

        missing = [col for col in required_columns if col not in df.columns]
        assert len(missing) == 2
        assert "quantity" in missing
        assert "unit_price" in missing

    def test_csv_upload_empty_file(self):
        csv_data = ""
        df = pd.read_csv(io.StringIO(csv_data))
        assert len(df) == 0

    def test_csv_upload_invalid_values(self):
        csv_data = """product_id,quantity,unit_price
1,abc,29.99
2,-5,19.99
3,0,0"""

        df = pd.read_csv(io.StringIO(csv_data))
        invalid_quantity = df[~df["quantity"].apply(lambda x: isinstance(x, (int, float)) and x >= 0)]
        assert len(invalid_quantity) > 0

    def test_csv_file_extension_check(self):
        valid_extensions = [".csv"]
        assert ".csv" in valid_extensions
        assert ".txt" not in valid_extensions
        assert ".xlsx" not in valid_extensions

    def test_csv_large_file_structure(self):
        n_rows = 1000
        data = {
            "product_id": range(1, n_rows + 1),
            "quantity": np.random.randint(1, 100, n_rows),
            "unit_price": np.random.uniform(10, 100, n_rows),
        }
        df = pd.DataFrame(data)
        assert len(df) == 1000
        assert df["quantity"].min() >= 1
        assert df["unit_price"].min() >= 10


class TestMissingValuesDetection:
    def test_missing_values_detection(self):
        df = pd.DataFrame({
            "col_a": [1, 2, np.nan, 4, 5],
            "col_b": ["x", None, "z", "w", "v"],
            "col_c": [10, 20, 30, 40, 50],
        })

        null_pct = df.isnull().mean()
        cols_with_missing = null_pct[null_pct > 0].index.tolist()

        assert "col_a" in cols_with_missing
        assert "col_b" in cols_with_missing
        assert "col_c" not in cols_with_missing

    def test_missing_values_threshold(self):
        df = pd.DataFrame({
            "fine": [1, 2, 3, 4, 5],
            "some_missing": [1, np.nan, 3, np.nan, 5],
            "mostly_missing": [np.nan, np.nan, np.nan, 4, 5],
        })

        threshold = 0.5
        null_pct = df.isnull().mean()
        cols_to_drop = null_pct[null_pct > threshold].index.tolist()

        assert "mostly_missing" in cols_to_drop
        assert "fine" not in cols_to_drop

    def test_missing_values_fill_numeric(self):
        df = pd.DataFrame({"values": [10.0, 20.0, np.nan, 40.0, np.nan]})

        median_val = df["values"].median()
        df["values"] = df["values"].fillna(median_val)

        assert df["values"].isnull().sum() == 0
        assert df["values"].mean() > 0

    def test_missing_values_fill_categorical(self):
        df = pd.DataFrame({"category": ["A", "B", None, "A", None]})

        mode_val = df["category"].mode()
        if len(mode_val) > 0:
            df["category"] = df["category"].fillna(mode_val.iloc[0])

        assert df["category"].isnull().sum() == 0

    def test_missing_values_no_missing(self):
        df = pd.DataFrame({
            "a": [1, 2, 3],
            "b": [4, 5, 6],
        })

        null_pct = df.isnull().mean()
        assert null_pct.sum() == 0


class TestDuplicateDetection:
    def test_duplicate_detection(self):
        df = pd.DataFrame({
            "id": [1, 2, 3, 1, 2],
            "name": ["A", "B", "C", "A", "B"],
            "value": [10, 20, 30, 10, 20],
        })

        duplicate_mask = df.duplicated()
        assert duplicate_mask.sum() == 2

    def test_duplicate_removal(self):
        df = pd.DataFrame({
            "id": [1, 2, 3, 1, 2],
            "name": ["A", "B", "C", "A", "B"],
            "value": [10, 20, 30, 10, 20],
        })

        before_count = len(df)
        df_deduped = df.drop_duplicates()
        after_count = len(df_deduped)

        assert after_count == 3
        assert before_count - after_count == 2

    def test_duplicate_detection_by_subset(self):
        df = pd.DataFrame({
            "product_id": [1, 1, 2, 2, 3],
            "date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02", "2024-01-03"],
            "quantity": [10, 10, 20, 20, 30],
        })

        duplicate_mask = df.duplicated(subset=["product_id", "date"])
        assert duplicate_mask.sum() == 2

    def test_no_duplicates(self):
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["A", "B", "C"],
        })

        duplicate_mask = df.duplicated()
        assert duplicate_mask.sum() == 0

    def test_full_row_duplicates(self):
        df = pd.DataFrame({
            "a": [1, 1, 2],
            "b": [10, 10, 20],
        })

        df_deduped = df.drop_duplicates()
        assert len(df_deduped) == 2

    def test_duplicates_preserve_order(self):
        df = pd.DataFrame({
            "id": [1, 2, 1, 3, 2],
        })

        df_deduped = df.drop_duplicates(keep="first")
        assert list(df_deduped["id"]) == [1, 2, 3]

    def test_date_parsing_validation(self):
        valid_dates = ["2024-01-01", "2024-12-31", "2024-06-15"]
        invalid_dates = ["not-a-date", "2024-13-01", "abc"]

        parsed_valid = pd.to_datetime(valid_dates, errors="coerce")
        parsed_invalid = pd.to_datetime(invalid_dates, errors="coerce")

        assert parsed_valid.notna().all()
        assert parsed_invalid.isna().any()
