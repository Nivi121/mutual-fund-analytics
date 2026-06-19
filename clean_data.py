"""
clean_data.py
=============
Processes raw datasets into cleaned versions ready for database ingestion.
Main cleaning duties include handling missing dates (forward-fill), standardizing
transaction category codes, checking bounds, and removing data duplicates.
"""

import sys
import pathlib
import pandas as pd

# Force stdout encoding to UTF-8 if supported
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Default base path is the directory containing this script
BASE_PATH = pathlib.Path(__file__).parent.resolve()


def clean_nav_history(raw_dir: pathlib.Path, processed_dir: pathlib.Path) -> bool:
    """
    Cleans raw NAV history data: parses dates, removes duplicates,
    forward-fills missing calendar days, and flags negative NAV values.

    Args:
        raw_dir (pathlib.Path): Location of raw CSVs.
        processed_dir (pathlib.Path): Location to write clean CSVs.

    Returns:
        bool: True if cleaning completed successfully.
    """
    print("\nDataset: nav_history.csv")
    file_path = raw_dir / "nav_history.csv"

    if not file_path.exists():
        print(f"  [ERROR] Raw nav_history.csv not found at {file_path}")
        return False

    try:
        nav = pd.read_csv(file_path)
        print(f"  * Rows before cleaning: {len(nav)}")

        # Step 1: Parse dates to datetime
        nav["nav_date"] = pd.to_datetime(nav["nav_date"])
        print("  * Date formatting applied.")

        # Step 2: Sort by scheme_code and date
        nav = nav.sort_values(["scheme_code", "nav_date"])
        print("  * Sorted records by scheme and date.")

        # Step 3: Remove duplicates
        nav = nav.drop_duplicates(subset=["scheme_code", "nav_date"])
        print("  * Removed duplicate rows.")

        # Step 4: Forward fill missing NAV (holidays/weekends)
        filled_frames = []
        for code, group in nav.groupby("scheme_code"):
            group = group.set_index("nav_date")
            all_dates = pd.date_range(group.index.min(), group.index.max(), freq="D")
            group = group.reindex(all_dates).ffill()
            group["scheme_code"] = code
            group = group.reset_index()
            group.columns = ["nav_date", "scheme_code", "nav_value"]
            filled_frames.append(group)

        nav = pd.concat(filled_frames, ignore_index=True)
        print("  * Missing holiday/weekend dates forward-filled.")

        # Step 5: Validate NAV > 0
        invalid = nav[nav["nav_value"] <= 0]
        if len(invalid) > 0:
            print(f"  * [WARNING] Removed {len(invalid)} records with invalid non-positive NAV values.")
            nav = nav[nav["nav_value"] > 0]
        else:
            print("  * Verified all NAV values are positive.")

        print(f"  * Rows after cleaning : {len(nav)}")

        # Save output
        nav.to_csv(processed_dir / "nav_history_clean.csv", index=False)
        print("  Saved clean file to: data/processed/nav_history_clean.csv")
        return True

    except Exception as e:
        print(f"  [ERROR] Error cleaning NAV history: {e}")
        return False


def clean_investor_transactions(raw_dir: pathlib.Path, processed_dir: pathlib.Path) -> bool:
    """
    Cleans raw investor transaction data: parses dates, standardizes
    transaction codes into user-friendly names, and checks bounds.

    Args:
        raw_dir (pathlib.Path): Location of raw CSVs.
        processed_dir (pathlib.Path): Location to write clean CSVs.

    Returns:
        bool: True if cleaning completed successfully.
    """
    print("\nDataset: investor_transactions.csv")
    file_path = raw_dir / "investor_transactions.csv"

    if not file_path.exists():
        print(f"  [ERROR] Raw investor_transactions.csv not found at {file_path}")
        return False

    try:
        txn = pd.read_csv(file_path)
        print(f"  * Rows before cleaning: {len(txn)}")

        # Step 1: Parse dates
        txn["txn_date"] = pd.to_datetime(txn["txn_date"])
        print("  * Date formatting applied.")

        # Step 2: Standardise transaction type labels
        type_map = {
            "BUY":  "Lumpsum",
            "SELL": "Redemption",
            "SWP":  "SIP",
            "STP":  "SIP",
        }
        txn["txn_type"] = txn["txn_type"].map(type_map).fillna(txn["txn_type"])
        print(f"  * Normalized transaction types: {txn['txn_type'].unique().tolist()}")

        # Step 3: Remove negative/zero amounts
        invalid_amt = txn[txn["amount"] <= 0]
        if len(invalid_amt) > 0:
            print(f"  * [WARNING] Removed {len(invalid_amt)} records with invalid amount <= 0.")
            txn = txn[txn["amount"] > 0]
        else:
            print("  * Verified all transaction amounts are positive.")

        # Step 4: Drop duplicates
        txn = txn.drop_duplicates()
        print("  * Removed duplicate records.")
        print(f"  * Rows after cleaning : {len(txn)}")

        # Save output
        txn.to_csv(processed_dir / "investor_transactions_clean.csv", index=False)
        print("  Saved clean file to: data/processed/investor_transactions_clean.csv")
        return True

    except Exception as e:
        print(f"  [ERROR] Error cleaning transactions: {e}")
        return False


def clean_scheme_performance(raw_dir: pathlib.Path, processed_dir: pathlib.Path) -> bool:
    """
    Cleans raw scheme performance returns data: validates column types,
    checks for outlying return anomalies, and cross-checks expense ratios.

    Args:
        raw_dir (pathlib.Path): Location of raw CSVs.
        processed_dir (pathlib.Path): Location to write clean CSVs.

    Returns:
        bool: True if cleaning completed successfully.
    """
    print("\nDataset: scheme_returns.csv")
    returns_path = raw_dir / "scheme_returns.csv"
    expense_path = raw_dir / "expense_ratio.csv"

    if not returns_path.exists():
        print(f"  [ERROR] Raw scheme_returns.csv not found at {returns_path}")
        return False

    try:
        perf = pd.read_csv(returns_path)
        print(f"  * Rows before cleaning: {len(perf)}")

        # Step 1: Force performance fields to numeric
        return_cols = ["1m_return", "3m_return", "6m_return", "1y_return", "3y_return", "5y_return"]
        for col in return_cols:
            perf[col] = pd.to_numeric(perf[col], errors="coerce")
        print("  * Confirmed performance return inputs are numeric.")

        # Step 2: Validate returns are inside realistic boundaries (-100% to 200%)
        for col in return_cols:
            anomalies = perf[(perf[col] > 200) | (perf[col] < -100)]
            if len(anomalies) > 0:
                print(f"  * [WARNING] Return anomalies flagged in {col} (>200% or <-100%): {len(anomalies)} row(s)")

        # Step 3: Check expense ratios if available
        if expense_path.exists():
            exp = pd.read_csv(expense_path)
            out_of_range = exp[(exp["direct_expense_ratio"] < 0.1) | (exp["direct_expense_ratio"] > 2.5)]
            if len(out_of_range) > 0:
                print(f"  * [WARNING] Expense ratios out of standard range (0.1%-2.5%) for {len(out_of_range)} funds!")
            else:
                print("  * Verified expense ratios are within standard boundaries.")

        # Save output
        perf.to_csv(processed_dir / "scheme_performance_clean.csv", index=False)
        print("  Saved clean file to: data/processed/scheme_performance_clean.csv")
        return True

    except Exception as e:
        print(f"  [ERROR] Error cleaning performance/expense metrics: {e}")
        return False


def run_data_cleaning(base_path: pathlib.Path = BASE_PATH) -> bool:
    """
    Driver orchestration function that prepares target folders and invokes
    cleaning scripts on raw datasets.

    Args:
        base_path (pathlib.Path): The root folder of the project.

    Returns:
        bool: True if all cleaning sub-tasks finish successfully, False otherwise.
    """
    raw_dir = base_path / "data" / "raw"
    processed_dir = base_path / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  RUNNING DATA CLEANING PIPELINE")
    print("=" * 60)

    success_nav = clean_nav_history(raw_dir, processed_dir)
    success_txn = clean_investor_transactions(raw_dir, processed_dir)
    success_perf = clean_scheme_performance(raw_dir, processed_dir)

    print("\n" + "=" * 60)
    if success_nav and success_txn and success_perf:
        print("  DATA CLEANING COMPLETE!")
        print("=" * 60)
        return True
    else:
        print("  [ERROR] DATA CLEANING PIPELINE ENCOUNTERED ERRORS!")
        print("=" * 60)
        return False


if __name__ == "__main__":
    run_data_cleaning()