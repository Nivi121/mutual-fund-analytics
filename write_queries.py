"""
write_queries.py
================
Executes 10 analytical SQL queries against the SQLite database to profile
mutual fund metrics like top funds by AUM, returns, transactions, and expense ratios.
Saves the compiled queries to sql/queries.sql.
"""

import sys
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

QUERIES = {
    "Q1: Top 5 Funds by AUM": """
SELECT
    f.scheme_name,
    f.fund_house,
    ROUND(MAX(a.aum_crore), 2) AS latest_aum_crore
FROM fact_aum a
JOIN dim_fund f ON a.scheme_code = f.scheme_code
GROUP BY f.scheme_code
ORDER BY latest_aum_crore DESC
LIMIT 5;
    """,

    "Q2: Average NAV Per Month (All Funds)": """
SELECT
    d.year,
    d.month_name,
    ROUND(AVG(n.nav_value), 4) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON n.nav_date = d.full_date
GROUP BY d.year, d.month
ORDER BY d.year, d.month
LIMIT 12;
    """,

    "Q3: SIP Transaction Count by Year": """
SELECT
    strftime('%Y', txn_date) AS year,
    COUNT(*) AS sip_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM fact_transactions
WHERE txn_type = 'SIP'
GROUP BY year
ORDER BY year;
    """,

    "Q4: Transaction Count by Type": """
SELECT
    txn_type,
    COUNT(*) AS count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS avg_amount
FROM fact_transactions
GROUP BY txn_type
ORDER BY count DESC;
    """,

    "Q5: Funds with Expense Ratio < 1%": """
SELECT
    f.scheme_name,
    f.fund_house,
    p."1y_return",
    p."3y_return"
FROM fact_performance p
JOIN dim_fund f ON p.scheme_code = f.scheme_code
ORDER BY p."1y_return" DESC;
    """,

    "Q6: Best Performing Funds (1 Year Return)": """
SELECT
    f.scheme_name,
    f.fund_house,
    f.sub_category,
    ROUND(p."1y_return", 2) AS return_1y_pct,
    ROUND(p."3y_return", 2) AS return_3y_pct
FROM fact_performance p
JOIN dim_fund f ON p.scheme_code = f.scheme_code
ORDER BY p."1y_return" DESC;
    """,

    "Q7: Latest NAV for Each Fund": """
SELECT
    f.scheme_name,
    f.fund_house,
    n.nav_date,
    ROUND(n.nav_value, 4) AS nav_value
FROM fact_nav n
JOIN dim_fund f ON n.scheme_code = f.scheme_code
INNER JOIN (
    SELECT scheme_code, MAX(nav_date) AS max_date
    FROM fact_nav
    GROUP BY scheme_code
) latest ON n.scheme_code = latest.scheme_code
AND n.nav_date = latest.max_date
ORDER BY n.nav_value DESC;
    """,

    "Q8: Monthly AUM Growth (Average)": """
SELECT
    strftime('%Y-%m', date) AS month,
    ROUND(AVG(aum_crore), 2) AS avg_aum_crore
FROM fact_aum
GROUP BY month
ORDER BY month
LIMIT 12;
    """,

    "Q9: Funds by Risk Grade": """
SELECT
    f.risk_grade,
    COUNT(DISTINCT f.scheme_code)    AS fund_count,
    ROUND(AVG(p."1y_return"), 2)     AS avg_1y_return,
    ROUND(AVG(p."3y_return"), 2)     AS avg_3y_return
FROM dim_fund f
JOIN fact_performance p ON f.scheme_code = p.scheme_code
GROUP BY f.risk_grade
ORDER BY avg_1y_return DESC;
    """,

    "Q10: Top 5 Largest Single Transactions": """
SELECT
    t.transaction_id,
    f.scheme_name,
    t.txn_type,
    t.txn_date,
    ROUND(t.amount, 2) AS amount
FROM fact_transactions t
JOIN dim_fund f ON t.scheme_code = f.scheme_code
ORDER BY t.amount DESC
LIMIT 5;
    """,
}


def run_analytical_queries(base_path: pathlib.Path = BASE_PATH) -> bool:
    """
    Connects to the SQLite DB, runs the 10 defined SQL queries, profiles output
    in tabular layout on stdout, and writes compiled SQL statements to queries.sql.

    Args:
        base_path (pathlib.Path): Root path of the project.

    Returns:
        bool: True if queries completed successfully, False otherwise.
    """
    db_path = base_path / "bluestock_mf.db"
    sql_dir = base_path / "sql"
    sql_dir.mkdir(exist_ok=True)

    if not db_path.exists():
        print(f"  [ERROR] Database file not found: {db_path}")
        return False

    print("=" * 60)
    print("  RUNNING 10 ANALYTICAL SQL QUERIES")
    print("=" * 60)

    queries_source_log = ""

    try:
        with sqlite3.connect(db_path) as conn:
            for title, query_sql in QUERIES.items():
                print(f"\nQuery: {title}")
                print("-" * 50)

                df = pd.read_sql_query(query_sql, conn)
                print(df.to_string(index=False))

                # Compile SQL queries for storage
                queries_source_log += f"\n-- {title}\n{query_sql.strip()}\n"

        # Save queries sql to file
        queries_file = sql_dir / "queries.sql"
        queries_file.write_text(queries_source_log, encoding="utf-8")
        print(f"\nSaved analytical query source catalog to: sql/queries.sql")

        print("\n" + "=" * 60)
        print("  ALL ANALYTICAL SQL QUERIES SUCCEEDED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n  [ERROR] SQL query execution failed: {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    run_analytical_queries()