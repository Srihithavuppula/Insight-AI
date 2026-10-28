
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "insightiq.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_summary():
    query = """
        SELECT
            COUNT(*) AS total_transactions,
            ROUND(
                SUM(Quantity * Unit_price - Discount_amount), 2
            ) AS total_revenue,
            COUNT(DISTINCT Product) AS total_products,
            COUNT(DISTINCT Region) AS total_regions
        FROM sales
        WHERE LOWER(TRIM(Status)) = 'completed'
    """

    with get_connection() as connection:
        row = connection.execute(query).fetchone()
        return dict(row)
    
def get_top_products(limit=5):
    query = """
        SELECT
            Product,
            ROUND(
                SUM(Quantity * Unit_price - Discount_amount), 2
            ) AS revenue
        FROM sales
        WHERE LOWER(TRIM(Status)) = 'completed'
        GROUP BY Product
        ORDER BY revenue DESC
        LIMIT ?
    """

    with get_connection() as connection:
        rows = connection.execute(query, (limit,)).fetchall()
        return [dict(row) for row in rows]
 
def get_monthly_revenue():
    query = """
        SELECT
            strftime('%Y-%m', Order_date) AS month,
            ROUND(
                SUM(Quantity * Unit_price - Discount_amount), 2
            ) AS revenue
        FROM sales
        WHERE LOWER(TRIM(Status)) = 'completed'
        GROUP BY strftime('%Y-%m', Order_date)
        ORDER BY month
    """

    with get_connection() as connection:
        rows = connection.execute(query).fetchall()
        return [dict(row) for row in rows]


def get_region_revenue():
    query = """
        SELECT
            Region,
            ROUND(
                SUM(Quantity * Unit_price - Discount_amount), 2
            ) AS revenue
        FROM sales
        WHERE LOWER(TRIM(Status)) = 'completed'
        GROUP BY Region
        ORDER BY revenue DESC
    """

    with get_connection() as connection:
        rows = connection.execute(query).fetchall()
        return [dict(row) for row in rows]
   





if __name__ == "__main__":
    print("Sales summary:")
    print(get_summary())

    print("\nTop products by revenue:")
    for product in get_top_products():
        print(product)

    print("\nMonthly revenue:")
    for month in get_monthly_revenue():
        print(month)

    print("\nRevenue by region:")
    for region in get_region_revenue():
        print(region)

