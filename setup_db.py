
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "sales.csv"
DB_PATH = BASE_DIR / "data" / "insightiq.db"

REQUIRED_COLUMNS = [
    "Transaction_Id",
    "Order_date",
    "Product",
    "Category",
    "Region",
    "Sales_channel",
    "Quantity",
    "Unit_price",
    "Discount_amount",
    "Status",
]


def setup_database():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing columns: {sorted(missing_columns)}")

    df = df[REQUIRED_COLUMNS].copy()

    # Normalize text fields.
    text_columns = [
        "Transaction_Id", "Product", "Category",
        "Region", "Sales_channel", "Status"
    ]
    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    # Parse dates and numeric fields.
    df["Order_date"] = pd.to_datetime(
        df["Order_date"], format="%d-%m-%Y", errors="coerce"
    )
    for column in ["Quantity", "Unit_price", "Discount_amount"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Reject records with missing or invalid required values.
    valid = (
        df["Transaction_Id"].notna()
        & df["Transaction_Id"].ne("")
        & df["Order_date"].notna()
        & df[["Product", "Category", "Region",
              "Sales_channel", "Status"]].notna().all(axis=1)
        & df[["Quantity", "Unit_price",
              "Discount_amount"]].notna().all(axis=1)
        & df["Quantity"].gt(0)
        & df["Unit_price"].ge(0)
        & df["Discount_amount"].ge(0)
        & df["Discount_amount"].le(
            df["Quantity"] * df["Unit_price"]
        )
    )

    rejected = df.loc[~valid].copy()
    clean = df.loc[valid].copy()

    # Keep the first occurrence of each transaction ID.
    duplicate_mask = clean.duplicated(
        subset=["Transaction_Id"], keep="first"
    )
    rejected = pd.concat(
        [rejected, clean.loc[duplicate_mask]], ignore_index=True
    )
    clean = clean.loc[~duplicate_mask].copy()

    clean["Order_date"] = clean["Order_date"].dt.strftime("%Y-%m-%d")

    # Store imported records in SQLite.
    with sqlite3.connect(DB_PATH) as connection:
        clean.to_sql("sales", connection, if_exists="replace", index=False)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_order_date
            ON sales(Order_date)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_product
            ON sales(Product)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_region
            ON sales(Region)
        """)

    print("Database created successfully!")
    print(f"CSV rows: {len(df)}")
    print(f"Imported records: {len(clean)}")
    print(f"Rejected records: {len(rejected)}")
    print("\nRejected record details:")
    print(rejected.to_string(index=False))
    print(f"Database: {DB_PATH}")


if __name__ == "__main__":
    setup_database()
