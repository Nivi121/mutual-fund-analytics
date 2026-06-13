"""
recommender.py
==============
Simple Fund Recommender based on risk appetite
Usage: py recommender.py
"""
import pandas as pd
import pathlib

BASE = pathlib.Path(__file__).resolve().parent

# Load data
sharpe_df = pd.read_csv(BASE / "sharpe_ratio.csv")
funds     = pd.read_csv(BASE / "data" / "raw" / "fund_master.csv")

# Drop duplicate scheme_name
sharpe_df = sharpe_df.drop(columns=["scheme_name"])
sharpe_merged = sharpe_df.merge(
    funds[["scheme_code", "scheme_name", "risk_grade", "sub_category"]],
    on="scheme_code", how="left"
)

# Risk mapping
risk_map = {
    "Low":      ["Low", "Moderately Low"],
    "Moderate": ["Moderate", "Moderately High"],
    "High":     ["High", "Very High"],
}

def recommend_funds(risk_appetite: str) -> None:
    print(f"\n{'='*55}")
    print(f"  FUND RECOMMENDER")
    print(f"  Risk Appetite : {risk_appetite}")
    print(f"{'='*55}")

    matched_grades = risk_map.get(risk_appetite, [])
    filtered = sharpe_merged[sharpe_merged["risk_grade"].isin(matched_grades)]

    if filtered.empty:
        filtered = sharpe_merged.copy()

    top3 = filtered.nlargest(3, "sharpe_ratio")[
        ["scheme_name", "risk_grade",
         "annual_return_%", "sharpe_ratio"]
    ].reset_index(drop=True)
    top3.index += 1

    print(f"\n  Top 3 Recommended Funds:\n")
    print(top3.to_string())
    print(f"\n{'='*55}")

if __name__ == "__main__":
    print("\nWelcome to Bluestock Fund Recommender!")
    print("Risk options: Low / Moderate / High")
    risk = input("\nEnter your risk appetite: ").strip().capitalize()
    recommend_funds(risk)