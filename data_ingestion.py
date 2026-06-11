import pandas as pd
import pathlib

# Get project folder path
BASE = pathlib.Path(__file__).parent.resolve()
RAW  = BASE / "data" / "raw"

# List of all 10 CSV files
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

print("=" * 50)
print("  LOADING ALL 10 DATASETS")
print("=" * 50)

for filename in DATASETS:
    filepath = RAW / filename

    print(f"\n📂 {filename}")
    print("-" * 40)

    # Load the CSV file
    df = pd.read_csv(filepath)

    # Print shape (rows, columns)
    print(f"  Shape   : {df.shape[0]} rows × {df.shape[1]} columns")

    # Print column names and their data types
    print(f"\n  Columns & Types:")
    for col, dtype in df.dtypes.items():
        print(f"    • {col:<25} {dtype}")

    # Print first 3 rows
    print(f"\n  First 3 rows:")
    print(df.head(3).to_string())

    # Check for missing values
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if not nulls.empty:
        print(f"\n  ⚠️  Missing values found:")
        for col, cnt in nulls.items():
            print(f"    • {col}: {cnt} missing")
    else:
        print(f"\n  ✅  No missing values")

    print()

print("=" * 50)
print("  ALL DATASETS LOADED SUCCESSFULLY!")
print("=" * 50)