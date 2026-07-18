import duckdb
import pandas as pd

def load(db_path="data/gpay.duckdb"):
    con = duckdb.connect(db_path)

    # Read the manually categorized CSV
    df = pd.read_csv("data/processed/transactions.csv")
    df = df.rename(columns={"Category": "category"})
    df["date"] = pd.to_datetime(df["date"], dayfirst=True).dt.strftime("%Y-%m-%d")
    df["datetime"] = pd.to_datetime(df["datetime"], dayfirst=True).dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df[df["transaction_id"] != "#NAME?"]
    print(f"Rows after removing bad transaction IDs: {len(df)}")
    print(f"Rows loaded from CSV: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")

    con.execute("DROP TABLE IF EXISTS transactions")

    con.execute("""
        CREATE TABLE transactions (
            transaction_id VARCHAR PRIMARY KEY,
            date DATE,
            month VARCHAR,
            year INTEGER,
            datetime TIMESTAMP,
            merchant VARCHAR,
            amount DOUBLE,
            status VARCHAR,
            day_of_week VARCHAR,
            is_weekend VARCHAR,
            time_of_day VARCHAR,
            category VARCHAR
        )
    """)

    con.execute("INSERT INTO transactions SELECT * FROM df")

    count = con.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    print(f"\nLoaded {count} rows into DuckDB")

    print("\nSpend by category:")
    print(con.execute("""
        SELECT category, COUNT(*) as txns, ROUND(SUM(amount), 2) as total
        FROM transactions
        GROUP BY category
        ORDER BY total DESC
    """).df())

    con.close()

if __name__ == "__main__":
    load()
