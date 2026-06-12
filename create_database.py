import pandas as pd
import pathlib
import sqlite3

BASE = pathlib.Path(__file__).parent.resolve()
RAW  = BASE / "data" / "raw"
PROC = BASE / "data" / "processed"
DB   = BASE / "bluestock_mf.db"

print("=" * 50)
print("  TASK 4: CREATE SQLITE DATABASE SCHEMA")
print("=" * 50)

# Connect to SQLite database
# (creates the file automatically if it doesn't exist)
conn = sqlite3.connect(DB)
cursor = conn.cursor()
print(f"\n  ✅ Database created: bluestock_mf.db")

# ─────────────────────────────────────────────
# CREATE TABLES (Star Schema)
# ─────────────────────────────────────────────
schema_sql = """

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

cursor.executescript(schema_sql)
conn.commit()
print("\n  ✅ All tables created:")
print("     • dim_fund")
print("     • dim_date")
print("     • fact_nav")
print("     • fact_transactions")
print("     • fact_performance")
print("     • fact_aum")

# ─────────────────────────────────────────────
# TASK 5: LOAD DATA INTO SQLITE
# ─────────────────────────────────────────────
print("\n" + "=" * 50)
print("  TASK 5: LOADING DATA INTO DATABASE")
print("=" * 50)

# 1. Load dim_fund
print("\n  Loading dim_fund ...")
fund_master = pd.read_csv(RAW / "fund_master.csv")
fund_master.to_sql("dim_fund", conn,
                   if_exists="replace", index=False)
count = cursor.execute("SELECT COUNT(*) FROM dim_fund").fetchone()[0]
print(f"  ✅ dim_fund loaded — {count} rows")

# 2. Build and load dim_date
print("\n  Loading dim_date ...")
nav_clean = pd.read_csv(PROC / "nav_history_clean.csv")
all_dates = pd.to_datetime(nav_clean["nav_date"]).dt.date
all_dates = sorted(set(all_dates))
date_rows = []
for d in all_dates:
    import datetime
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
dim_date.to_sql("dim_date", conn,
                if_exists="replace", index=False)
count = cursor.execute("SELECT COUNT(*) FROM dim_date").fetchone()[0]
print(f"  ✅ dim_date loaded  — {count} rows")

# 3. Load fact_nav
print("\n  Loading fact_nav ...")
nav_clean.to_sql("fact_nav", conn,
                 if_exists="replace", index=False)
count = cursor.execute("SELECT COUNT(*) FROM fact_nav").fetchone()[0]
print(f"  ✅ fact_nav loaded  — {count} rows")

# 4. Load fact_transactions
print("\n  Loading fact_transactions ...")
txn_clean = pd.read_csv(PROC / "investor_transactions_clean.csv")
txn_clean.to_sql("fact_transactions", conn,
                 if_exists="replace", index=False)
count = cursor.execute(
    "SELECT COUNT(*) FROM fact_transactions").fetchone()[0]
print(f"  ✅ fact_transactions loaded — {count} rows")

# 5. Load fact_performance
print("\n  Loading fact_performance ...")
perf_clean = pd.read_csv(PROC / "scheme_performance_clean.csv")
perf_clean.to_sql("fact_performance", conn,
                  if_exists="replace", index=False)
count = cursor.execute(
    "SELECT COUNT(*) FROM fact_performance").fetchone()[0]
print(f"  ✅ fact_performance loaded — {count} rows")

# 6. Load fact_aum
print("\n  Loading fact_aum ...")
aum = pd.read_csv(RAW / "aum_history.csv")
aum.to_sql("fact_aum", conn,
           if_exists="replace", index=False)
count = cursor.execute("SELECT COUNT(*) FROM fact_aum").fetchone()[0]
print(f"  ✅ fact_aum loaded  — {count} rows")

# ── Verify all tables ─────────────────────────
print("\n" + "=" * 50)
print("  VERIFICATION — ROW COUNTS")
print("=" * 50)
tables = ["dim_fund", "dim_date", "fact_nav",
          "fact_transactions", "fact_performance", "fact_aum"]
for table in tables:
    count = cursor.execute(
        f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<25} {count:>6} rows")

conn.close()

# Save schema to sql/schema.sql
schema_path = BASE / "sql" / "schema.sql"
schema_path.write_text(schema_sql, encoding="utf-8")
print(f"\n  💾 Schema saved to sql/schema.sql")
print("\n" + "=" * 50)
print("  DATABASE READY!")
print("=" * 50)
print("\n  Next → run  py write_queries.py")