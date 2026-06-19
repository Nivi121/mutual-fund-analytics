"""
create_sample_data.py
======================
Loads, parses, and maps client mutual fund CSV datasets from the dataset/
folder into the data/raw/ directory, conforming to the project schema.
"""

import sys
import os
import pathlib
import pandas as pd

# Force stdout encoding to UTF-8 if supported
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Default base path is the directory containing this script
BASE_PATH = pathlib.Path(__file__).parent.resolve()


def generate_sample_data(base_path: pathlib.Path = BASE_PATH) -> None:
    """
    Reads user-provided real CSV files from the dataset directory,
    maps their columns to match the expected ETL/DB schema formats,
    calculates dynamic fields like units and experience, and saves
    them in the raw data directory.

    Args:
        base_path (pathlib.Path): The root folder of the project.
    """
    dataset_dir = base_path / "dataset"
    raw_dir = base_path / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    print("Mapping and copying user CSV datasets...")

    # Helper function to read dataset safely
    def read_dataset(filename: str) -> pd.DataFrame:
        path = dataset_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Required source file not found: {path}")
        return pd.read_csv(path)

    # 1. Fund Master
    # Source: 01_fund_master.csv
    # Target columns: scheme_code, scheme_name, fund_house, category, sub_category, risk_grade, plan_type
    df_fund = read_dataset("01_fund_master.csv")
    fund_master = pd.DataFrame({
        "scheme_code": df_fund["amfi_code"],
        "scheme_name": df_fund["scheme_name"],
        "fund_house": df_fund["fund_house"],
        "category": df_fund["category"],
        "sub_category": df_fund["sub_category"],
        "risk_grade": df_fund["risk_category"],
        "plan_type": df_fund["plan"]
    })
    fund_master.to_csv(raw_dir / "fund_master.csv", index=False)
    print("  [OK] Created: fund_master.csv")

    # 2. NAV History
    # Source: 02_nav_history.csv
    # Target columns: scheme_code, nav_date, nav_value
    df_nav = read_dataset("02_nav_history.csv")
    nav_history = pd.DataFrame({
        "scheme_code": df_nav["amfi_code"],
        "nav_date": df_nav["date"],
        "nav_value": df_nav["nav"]
    })
    nav_history.to_csv(raw_dir / "nav_history.csv", index=False)
    print("  [OK] Created: nav_history.csv")

    # 3. Scheme Returns
    # Source: 07_scheme_performance.csv
    # Target columns: scheme_code, 1m_return, 3m_return, 6m_return, 1y_return, 3y_return, 5y_return
    df_perf = read_dataset("07_scheme_performance.csv")
    scheme_returns = pd.DataFrame({
        "scheme_code": df_perf["amfi_code"],
        "1m_return": 0.0,
        "3m_return": 0.0,
        "6m_return": 0.0,
        "1y_return": df_perf["return_1yr_pct"],
        "3y_return": df_perf["return_3yr_pct"],
        "5y_return": df_perf["return_5yr_pct"]
    })
    scheme_returns.to_csv(raw_dir / "scheme_returns.csv", index=False)
    print("  [OK] Created: scheme_returns.csv")

    # 4. Benchmark Index
    # Source: 10_benchmark_indices.csv
    # Target columns: date, index_name, close
    df_bench = read_dataset("10_benchmark_indices.csv")
    benchmark_index = pd.DataFrame({
        "date": df_bench["date"],
        "index_name": df_bench["index_name"],
        "close": df_bench["close_value"]
    })
    benchmark_index.to_csv(raw_dir / "benchmark_index.csv", index=False)
    print("  [OK] Created: benchmark_index.csv")

    # 5. Fund Manager
    # Source: 01_fund_master.csv
    # Calculate experience_yrs dynamically from launch_date
    df_fund["launch_date_parsed"] = pd.to_datetime(df_fund["launch_date"], errors="coerce")
    reference_date = pd.to_datetime("2026-06-19")
    calculated_exp = ((reference_date - df_fund["launch_date_parsed"]).dt.days / 365.25).fillna(10.0).round().astype(int)
    calculated_exp = calculated_exp.clip(lower=1)

    fund_manager = pd.DataFrame({
        "scheme_code": df_fund["amfi_code"],
        "manager_name": df_fund["fund_manager"].fillna("Unknown Manager"),
        "experience_yrs": calculated_exp
    })
    fund_manager.to_csv(raw_dir / "fund_manager.csv", index=False)
    print("  [OK] Created: fund_manager.csv")

    # 6. Portfolio Holdings
    # Source: 09_portfolio_holdings.csv
    # Target columns: scheme_code, stock_name, weight_pct
    df_hold = read_dataset("09_portfolio_holdings.csv")
    portfolio_holdings = pd.DataFrame({
        "scheme_code": df_hold["amfi_code"],
        "stock_name": df_hold["stock_name"],
        "weight_pct": df_hold["weight_pct"]
    })
    portfolio_holdings.to_csv(raw_dir / "portfolio_holdings.csv", index=False)
    print("  [OK] Created: portfolio_holdings.csv")

    # 7. AUM History
    # Source: 07_scheme_performance.csv (which contains scheme-level aum_crore snapshot)
    # Target columns: scheme_code, date, aum_crore
    # We will use the portfolio snapshot date 2025-12-31 matching NAV history
    aum_history = pd.DataFrame({
        "scheme_code": df_perf["amfi_code"],
        "date": "2025-12-31",
        "aum_crore": df_perf["aum_crore"]
    })
    aum_history.to_csv(raw_dir / "aum_history.csv", index=False)
    print("  [OK] Created: aum_history.csv")

    # 8. Expense Ratio
    # Source: 01_fund_master.csv
    # Target columns: scheme_code, direct_expense_ratio, regular_expense_ratio
    expense_ratio = pd.DataFrame({
        "scheme_code": df_fund["amfi_code"],
        "direct_expense_ratio": df_fund["expense_ratio_pct"],
        "regular_expense_ratio": df_fund["expense_ratio_pct"]
    })
    expense_ratio.to_csv(raw_dir / "expense_ratio.csv", index=False)
    print("  [OK] Created: expense_ratio.csv")

    # 9. Risk Metrics
    # Source: 07_scheme_performance.csv
    # Target columns: scheme_code, sharpe_ratio, beta, alpha, max_drawdown
    risk_metrics = pd.DataFrame({
        "scheme_code": df_perf["amfi_code"],
        "sharpe_ratio": df_perf["sharpe_ratio"],
        "beta": df_perf["beta"],
        "alpha": df_perf["alpha"],
        "max_drawdown": df_perf["max_drawdown_pct"]
    })
    risk_metrics.to_csv(raw_dir / "risk_metrics.csv", index=False)
    print("  [OK] Created: risk_metrics.csv")

    # 10. Investor Transactions
    # Source: 08_investor_transactions.csv
    # Target columns: transaction_id, scheme_code, txn_date, txn_type, amount, units
    # Calculate units dynamically based on historical NAV at transaction date
    df_txn = read_dataset("08_investor_transactions.csv")
    
    # Parse dates for sorting and merging
    df_nav_sorted = df_nav.copy()
    df_nav_sorted["date"] = pd.to_datetime(df_nav_sorted["date"])
    df_nav_sorted = df_nav_sorted.sort_values("date")
    
    df_txn_sorted = df_txn.copy()
    df_txn_sorted["transaction_date"] = pd.to_datetime(df_txn_sorted["transaction_date"])
    df_txn_sorted = df_txn_sorted.sort_values("transaction_date")
    
    # Perform backward fill lookup for NAV on transaction date (handles weekends/holidays)
    df_txn_merged = pd.merge_asof(
        df_txn_sorted,
        df_nav_sorted,
        left_on="transaction_date",
        right_on="date",
        by="amfi_code",
        direction="backward"
    )
    
    # Fallback to default NAV of 10.0 if not found
    df_txn_merged["nav"] = df_txn_merged["nav"].fillna(10.0)
    df_txn_merged["units"] = (df_txn_merged["amount_inr"] / df_txn_merged["nav"]).round(4)
    
    # Restore sorting and formatting
    df_txn_merged = df_txn_merged.sort_values("transaction_date")
    
    investor_transactions = pd.DataFrame({
        "transaction_id": [f"TXN{i:05d}" for i in range(len(df_txn_merged))],
        "scheme_code": df_txn_merged["amfi_code"],
        "txn_date": df_txn_merged["transaction_date"].dt.strftime('%Y-%m-%d'),
        "txn_type": df_txn_merged["transaction_type"],
        "amount": df_txn_merged["amount_inr"],
        "units": df_txn_merged["units"]
    })
    
    investor_transactions.to_csv(raw_dir / "investor_transactions.csv", index=False)
    print("  [OK] Created: investor_transactions.csv")

    print("\nAll 10 raw datasets successfully copied and mapped from dataset/ to data/raw/")


if __name__ == "__main__":
    generate_sample_data()