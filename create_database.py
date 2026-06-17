"""
create_database.py
==================
Builds the SQLite relational database schema and loads cleaned datasets.
Applies a Star Schema layout with dimensions for funds and dates,
and fact tables for daily NAV history, performance, transactions, and AUM.
"""

import sys
import datetime
import pathlib
import sqlite3
import pandas as pd

# Force stdout encoding to UTF-8 if supported
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Default base path is the directory containing this script
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DB_FILE = BASE_PATH / "bluestock_mf.db"

SCHEMA_SQL = """
-- Dimension Table: Fund details
CREATE TABLE IF NOT EXISTS dim_fund (
    scheme_code     INTEGER PRIMARY KEY,
    scheme_name     TEXT    NOT NULL,
    fund_house      TEXT    NOT NULL,
    category        TEXT,
    sub_category    TEXT,
    risk_grade      TEXT,
    plan_type       TEXT
);

-- Dimension Table: Date details
CREATE TABLE IF NOT EXISTS dim_date (
    date_id         TEXT    PRIMARY KEY,
    full_date       TEXT    NOT NULL,
    day             INTEGER,
    month           INTEGER,
    month_name      TEXT,
    quarter         INTEGER,
    year            INTEGER,
    is_weekend      INTEGER
);

-- Fact Table: Daily NAV
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code     INTEGER NOT NULL,
    nav_date        TEXT    NOT NULL,
    nav_value       REAL    NOT NULL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);

-- Fact Table: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id  TEXT    PRIMARY KEY,
    scheme_code     INTEGER NOT NULL,
    txn_date        TEXT    NOT NULL,
    txn_type        TEXT    NOT NULL,
    amount          REAL    NOT NULL,
    units           REAL    NOT NULL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);

-- Fact Table: Scheme Performance / Returns
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code     INTEGER NOT NULL,
    return_1m       REAL,
    return_3m       REAL,
    return_6m       REAL,
    return_1y       REAL,
    return_3y       REAL,
    return_5y       REAL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);

-- Fact Table: AUM History
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code     INTEGER NOT NULL,
    aum_date        TEXT    NOT NULL,
    aum_crore       REAL    NOT NULL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);
"""


def create_schema(cursor: sqlite3.Cursor) -> None:
    """
    Executes table definitions to create the SQLite schema structures.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
    """
    print("  * Creating database schema tables...")
    cursor.executescript(SCHEMA_SQL)
    print("  [OK] All schema tables defined successfully.")


def load_tables(conn: sqlite3.Connection, cursor: sqlite3.Cursor, raw_dir: pathlib.Path, processed_dir: pathlib.Path) -> None:
    """
    Loads raw and cleaned CSV structures into their respective database tables.

    Args:
        conn (sqlite3.Connection): SQLite connection object.
        cursor (sqlite3.Cursor): Database cursor.
        raw_dir (pathlib.Path): Path to raw CSV files.
        processed_dir (pathlib.Path): Path to processed clean CSV files.
    """
    print("\n  * Loading datasets into database tables...")

    # 1. dim_fund
    fund_master = pd.read_csv(raw_dir / "fund_master.csv")
    fund_master.to_sql("dim_fund", conn, if_exists="replace", index=False)
    count = cursor.execute("SELECT COUNT(*) FROM dim_fund").fetchone()[0]
    print(f"    - dim_fund loaded: {count} rows")

    # 2. dim_date (Build dynamically from NAV history)
    nav_clean = pd.read_csv(processed_dir / "nav_history_clean.csv")
    all_dates = pd.to_datetime(nav_clean["nav_date"]).dt.date
    all_dates = sorted(set(all_dates))
    date_rows = []
    for d in all_dates:
        dt = datetime.date.fromisoformat(str(d))
        date_rows.append({
            "date_id":    str(dt),
            "full_date":  str(dt),
            "day":        dt.day,
            "month":      dt.month,
            "month_name": dt.strftime("%B"),
            "quarter":    (dt.month - 1) // 3 + 1,
            "year":       dt.year,
            "is_weekend": 1 if dt.weekday() >= 5 else 0,
        })
    dim_date = pd.DataFrame(date_rows)
    dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)
    count = cursor.execute("SELECT COUNT(*) FROM dim_date").fetchone()[0]
    print(f"    - dim_date loaded: {count} rows")

    # 3. fact_nav
    nav_clean.to_sql("fact_nav", conn, if_exists="replace", index=False)
    count = cursor.execute("SELECT COUNT(*) FROM fact_nav").fetchone()[0]
    print(f"    - fact_nav loaded: {count} rows")

    # 4. fact_transactions
    txn_clean = pd.read_csv(processed_dir / "investor_transactions_clean.csv")
    txn_clean.to_sql("fact_transactions", conn, if_exists="replace", index=False)
    count = cursor.execute("SELECT COUNT(*) FROM fact_transactions").fetchone()[0]
    print(f"    - fact_transactions loaded: {count} rows")

    # 5. fact_performance
    perf_clean = pd.read_csv(processed_dir / "scheme_performance_clean.csv")
    perf_clean.to_sql("fact_performance", conn, if_exists="replace", index=False)
    count = cursor.execute("SELECT COUNT(*) FROM fact_performance").fetchone()[0]
    print(f"    - fact_performance loaded: {count} rows")

    # 6. fact_aum
    aum = pd.read_csv(raw_dir / "aum_history.csv")
    aum.to_sql("fact_aum", conn, if_exists="replace", index=False)
    count = cursor.execute("SELECT COUNT(*) FROM fact_aum").fetchone()[0]
    print(f"    - fact_aum loaded: {count} rows")


def verify_tables(cursor: sqlite3.Cursor) -> None:
    """
    Verifies that all tables contain rows and logs the counts.

    Args:
        cursor (sqlite3.Cursor): Database cursor.
    """
    print("\n  * Verifying database structure row counts:")
    tables = ["dim_fund", "dim_date", "fact_nav", "fact_transactions", "fact_performance", "fact_aum"]
    for table in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"    - {table:<25} {count:>6} rows")


def setup_database(base_path: pathlib.Path = BASE_PATH) -> bool:
    """
    Orchestrates the entire SQLite database creation and data loading process.

    Args:
        base_path (pathlib.Path): The root path of the project.

    Returns:
        bool: True if database was built and loaded successfully, False otherwise.
    """
    raw_dir = base_path / "data" / "raw"
    processed_dir = base_path / "data" / "processed"
    db_path = base_path / "bluestock_mf.db"
    sql_dir = base_path / "sql"
    sql_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("  INITIALIZING RELATIONAL DATABASE SETUP")
    print("=" * 60)

    try:
        # Connect to SQLite DB using context manager
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            print(f"  [OK] Database connected: {db_path.name}")

            # Define tables
            create_schema(cursor)

            # Ingest dataset values
            load_tables(conn, cursor, raw_dir, processed_dir)

            # Verify tables row outputs
            verify_tables(cursor)

            # Commit changes
            conn.commit()

        # Save schema sql to file
        schema_file = sql_dir / "schema.sql"
        schema_file.write_text(SCHEMA_SQL, encoding="utf-8")
        print(f"\n  Saved DB Schema catalog to: sql/schema.sql")

        print("\n" + "=" * 60)
        print("  DATABASE INGESTION PIPELINE SUCCEEDED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n  [ERROR] Database setup failed: {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    setup_database()