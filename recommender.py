"""
recommender.py
==============
Interactive command-line tool to recommend top 3 mutual funds based on user risk appetite.
Integrates historical Sharpe ratio performance index with AMFI registry risk classifications.
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

RISK_MAP = {
    "Low":      ["Low", "Moderately Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High":     ["High", "Very High"],
}


def recommend_funds(risk_appetite: str, base_path: pathlib.Path = BASE_PATH) -> bool:
    """
    Filters funds by the user's risk appetite category and displays the top 3
    recommended schemes ranked by their Sharpe ratio performance.

    Args:
        risk_appetite (str): One of "Low", "Moderate", "High".
        base_path (pathlib.Path): Root path of the project.

    Returns:
        bool: True if recommendation execution succeeded, False on file loading errors.
    """
    sharpe_path = base_path / "sharpe_ratio.csv"
    master_path = base_path / "data" / "raw" / "fund_master.csv"

    if not sharpe_path.exists() or not master_path.exists():
        print("  [ERROR] Recommendation engine files missing (requires sharpe_ratio.csv & fund_master.csv)")
        return False

    try:
        # Load and prepare Sharpe and Fund master details
        sharpe_df = pd.read_csv(sharpe_path).drop(columns=["scheme_name"], errors="ignore")
        funds = pd.read_csv(master_path)

        sharpe_merged = sharpe_df.merge(
            funds[["scheme_code", "scheme_name", "risk_grade", "sub_category"]],
            on="scheme_code",
            how="left"
        )

        matched_grades = RISK_MAP.get(risk_appetite, [])
        filtered = sharpe_merged[sharpe_merged["risk_grade"].isin(matched_grades)]

        # If no specific matches exist for that class, default back to full list
        if filtered.empty:
            filtered = sharpe_merged.copy()

        top3 = filtered.nlargest(3, "sharpe_ratio")[
            ["scheme_name", "risk_grade", "annual_return_%", "sharpe_ratio"]
        ].reset_index(drop=True)
        top3.index += 1

        print(f"\n{'='*60}")
        print(f"  BLUESTOCK MUTUAL FUND RECOMMENDER")
        print(f"  Risk Profile Filter: {risk_appetite}")
        print(f"{'='*60}")
        print("\nTop 3 Recommended Funds:")
        print(top3.to_string())
        print(f"{'='*60}")
        return True

    except Exception as e:
        print(f"  [ERROR] Error running recommendation queries: {e}")
        return False


def main() -> None:
    """
    Runs the main interactive terminal CLI command loop.
    """
    print("\n================================================")
    print("      Welcome to Bluestock Fund Recommender!")
    print("================================================")

    while True:
        print("\nAvailable Risk Levels: Low / Moderate / High")
        print("Type 'Exit' to exit the recommender program.")

        user_input = input("\nEnter your risk appetite: ").strip().capitalize()

        if user_input == "Exit":
            print("\nThank you for using Bluestock Fund Recommender. Goodbye!\n")
            break

        if user_input not in RISK_MAP:
            print(f"  [WARNING] '{user_input}' is not a valid risk level. Please try again.")
            continue

        recommend_funds(user_input)


if __name__ == "__main__":
    main()