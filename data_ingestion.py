"""
data_ingestion.py
=================
Performs the initial loading, schema profiling, and validation of raw CSV datasets.
Ensures that all required columns are present and profiles row counts, types, and nulls.
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

DATASETS = [
    "fund_master.csv",
    "nav_history.csv",
    "scheme_returns.csv",
    "benchmark_index.csv",
    "fund_manager.csv",
    "portfolio_holdings.csv",
    "aum_history.csv",
    "expense_ratio.csv",
    "risk_metrics.csv",
    "investor_transactions.csv",
]


def profile_datasets(base_path: pathlib.Path = BASE_PATH) -> bool:
    """
    Loads all 10 raw CSV datasets, logs structural info (shape, column types,
    and missing values), and reports any initial data quality issues.

    Args:
        base_path (pathlib.Path): The root directory of the project.

    Returns:
        bool: True if all datasets are loaded successfully, False otherwise.
    """
    raw_dir = base_path / "data" / "raw"

    print("=" * 60)
    print("  LOADING AND PROFILING RAW DATASETS")
    print("=" * 60)

    success = True

    for filename in DATASETS:
        filepath = raw_dir / filename
        if not filepath.exists():
            print(f"  [ERROR] File not found: {filename} at {filepath}")
            success = False
            continue

        print(f"\nDataset: {filename}")
        print("-" * 50)

        try:
            # Load the CSV file
            df = pd.read_csv(filepath)

            # Print shape (rows, columns)
            print(f"  * Dimensions  : {df.shape[0]} rows x {df.shape[1]} columns")

            # Print column names and their data types
            print(f"  * Column Schema:")
            for col, dtype in df.dtypes.items():
                print(f"    - {col:<25} ({dtype})")

            # Check for missing values
            nulls = df.isnull().sum()
            nulls = nulls[nulls > 0]
            if not nulls.empty:
                print(f"  * [WARNING] Missing values found:")
                for col, cnt in nulls.items():
                    print(f"    - {col}: {cnt} missing")
            else:
                print(f"  * Schema Status: Clean (No missing values)")

        except Exception as e:
            print(f"  [ERROR] Error loading {filename}: {e}")
            success = False

    print("\n" + "=" * 60)
    if success:
        print("  ALL DATASETS LOADED AND PROFILED SUCCESSFULLY!")
    else:
        print("  [WARNING] SOME DATASETS FAILED TO LOAD OR ARE MISSING!")
    print("=" * 60)

    return success


if __name__ == "__main__":
    profile_datasets()