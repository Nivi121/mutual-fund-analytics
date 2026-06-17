"""
explore_fund_master.py
======================
Explores and prints categorical summaries from the Fund Master raw file.
Outputs unique value distributions for fund houses, categories, sub-categories,
risk grades, and details AMFI scheme code structural attributes.
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


def explore_fund_master_data(base_path: pathlib.Path = BASE_PATH) -> bool:
    """
    Loads raw fund master file and outputs unique categorizations (fund houses,
    categories, sub-categories, risk grades) and AMFI code stats.

    Args:
        base_path (pathlib.Path): Root path of the project.

    Returns:
        bool: True if file loads and profiles successfully, False otherwise.
    """
    file_path = base_path / "data" / "raw" / "fund_master.csv"

    if not file_path.exists():
        print(f"  [ERROR] Raw fund master file not found at {file_path}")
        return False

    print("=" * 60)
    print("  EXPLORING FUND MASTER METADATA")
    print("=" * 60)

    try:
        df = pd.read_csv(file_path)

        # 1. Unique Fund Houses
        print("\nFUND HOUSES:")
        for fh in sorted(df["fund_house"].unique()):
            count = (df["fund_house"] == fh).sum()
            print(f"  • {fh:<25} ({count} scheme(s))")

        # 2. Unique Categories
        print("\nCATEGORIES:")
        for cat in sorted(df["category"].unique()):
            count = (df["category"] == cat).sum()
            print(f"  • {cat:<25} ({count} scheme(s))")

        # 3. Unique Sub-Categories
        print("\nSUB-CATEGORIES:")
        for sub in sorted(df["sub_category"].unique()):
            count = (df["sub_category"] == sub).sum()
            print(f"  • {sub:<25} ({count} scheme(s))")

        # 4. Risk Grades
        print("\nRISK GRADES:")
        for risk in sorted(df["risk_grade"].unique()):
            count = (df["risk_grade"] == risk).sum()
            print(f"  • {risk:<25} ({count} scheme(s))")

        # 5. AMFI Scheme Code Structure
        print("\nAMFI SCHEME CODE STRUCTURE:")
        print(f"  * Total schemes         : {len(df)}")
        print(f"  * Lowest AMFI code      : {df['scheme_code'].min()}")
        print(f"  * Highest AMFI code     : {df['scheme_code'].max()}")
        print(f"  * Code digit length     : {len(str(df['scheme_code'].iloc[0]))} digits")
        print("\n  Sample AMFI Codes:")
        for _, row in df.head(5).iterrows():
            print(f"  • {row['scheme_code']}  →  {row['scheme_name']}")

        print("\n" + "=" * 60)
        print("  FUND MASTER EXPLORATION COMPLETE!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"  [ERROR] Error exploring fund master: {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    explore_fund_master_data()