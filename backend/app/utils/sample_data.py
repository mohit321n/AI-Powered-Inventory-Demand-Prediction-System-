"""
Sample Dataset Generator for Inventory Management System.
Generates realistic retail sales data for development and testing.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def generate_sample_dataset(num_records=5000, output_path=None):
    np.random.seed(42)

    products = [
        {"id": 1, "name": "Laptop Pro 15", "category": "Electronics", "base_price": 1299.99, "base_demand": 15},
        {"id": 2, "name": "Wireless Mouse", "category": "Electronics", "base_price": 29.99, "base_demand": 80},
        {"id": 3, "name": "USB-C Hub", "category": "Electronics", "base_price": 49.99, "base_demand": 45},
        {"id": 4, "name": "Mechanical Keyboard", "category": "Electronics", "base_price": 149.99, "base_demand": 30},
        {"id": 5, "name": "Monitor 27inch", "category": "Electronics", "base_price": 399.99, "base_demand": 20},
        {"id": 6, "name": "Office Chair", "category": "Furniture", "base_price": 299.99, "base_demand": 12},
        {"id": 7, "name": "Standing Desk", "category": "Furniture", "base_price": 599.99, "base_demand": 8},
        {"id": 8, "name": "Bookshelf", "category": "Furniture", "base_price": 199.99, "base_demand": 15},
        {"id": 9, "name": "Notebook A4", "category": "Stationery", "base_price": 4.99, "base_demand": 200},
        {"id": 10, "name": "Pen Set", "category": "Stationery", "base_price": 12.99, "base_demand": 150},
        {"id": 11, "name": "Printer Paper", "category": "Stationery", "base_price": 8.99, "base_demand": 180},
        {"id": 12, "name": "Markers Pack", "category": "Stationery", "base_price": 6.99, "base_demand": 120},
        {"id": 13, "name": "Backpack Pro", "category": "Accessories", "base_price": 79.99, "base_demand": 25},
        {"id": 14, "name": "Water Bottle", "category": "Accessories", "base_price": 19.99, "base_demand": 100},
        {"id": 15, "name": "Desk Lamp", "category": "Accessories", "base_price": 34.99, "base_demand": 40},
    ]

    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]

    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    records = []
    for _ in range(num_records):
        product = np.random.choice(products)
        date = pd.Timestamp(np.random.choice(date_range))
        day_of_week = date.dayofweek
        month = date.month

        seasonal_factor = 1.0
        if month in [11, 12]:
            seasonal_factor = 1.5
        elif month in [1, 2]:
            seasonal_factor = 0.8

        weekend_factor = 1.3 if day_of_week >= 5 else 1.0

        promotion = np.random.random() < 0.15
        discount = np.random.choice([0, 5, 10, 15, 20, 25]) if promotion else 0

        holiday = np.random.random() < 0.05

        units_sold = max(1, int(
            product["base_demand"]
            * seasonal_factor
            * weekend_factor
            * (1.5 if promotion else 1.0)
            * (1.2 if holiday else 1.0)
            * np.random.normal(1.0, 0.3)
        ))

        selling_price = product["base_price"] * (1 - discount / 100)

        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "product_id": product["id"],
            "product_name": product["name"],
            "category": product["category"],
            "units_sold": units_sold,
            "selling_price": round(selling_price, 2),
            "promotion": promotion,
            "discount": discount,
            "holiday": holiday,
            "store_location": np.random.choice(locations),
            "stock_available": max(0, int(units_sold * np.random.uniform(1.5, 5.0))),
        })

    df = pd.DataFrame(records)
    df = df.sort_values("date").reset_index(drop=True)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Dataset generated: {output_path}")
        print(f"Records: {len(df)}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Products: {df['product_name'].nunique()}")
        print(f"Categories: {df['category'].nunique()}")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nSample:\n{df.head()}")
        print(f"\nMissing values:\n{df.isnull().sum()}")

    return df


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    output = os.path.join(project_root, "data", "raw", "sample_sales_data.csv")
    generate_sample_dataset(num_records=5000, output_path=output)
