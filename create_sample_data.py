import pandas as pd
import numpy as np
from datetime import date, timedelta
import os
import pathlib

# Get the folder where this script is located
BASE = pathlib.Path(__file__).parent.resolve()


print("Creating sample CSV files...")

# 1. Fund Master
fund_master = pd.DataFrame({
    "scheme_code": [119551, 120503, 118632, 119092, 120841, 125497, 101305, 102816, 103504, 118989],
    "scheme_name": ["SBI Bluechip", "ICICI Bluechip", "Nippon Large Cap",
                    "Axis Bluechip", "Kotak Bluechip", "HDFC Top 100",
                    "DSP Top 100", "Franklin Bluechip", "Mirae Large Cap", "Parag Parikh Flexi"],
    "fund_house":  ["SBI MF", "ICICI Prudential", "Nippon India", "Axis MF",
                    "Kotak MF", "HDFC MF", "DSP MF", "Franklin", "Mirae", "Parag Parikh"],
    "category":    ["Equity"] * 10,
    "sub_category":["Large Cap"]*6 + ["Mid Cap", "Small Cap", "Flexi Cap", "ELSS"],
    "risk_grade":  ["Moderately High"]*8 + ["High", "Very High"],
    "plan_type":   ["Direct"] * 10,
})
fund_master.to_csv(BASE / "data" / "raw" / "fund_master.csv", index=False)
print("✅ fund_master.csv created")

# 2. NAV History
schemes = [119551, 120503, 118632, 119092, 120841, 125497, 101305, 102816, 103504, 118989]
dates = pd.date_range(end=date.today(), periods=365, freq="B")
rows = []
for sc in schemes:
    nav = 50.0
    for d in dates:
        nav = nav * (1 + np.random.normal(0.0003, 0.008))
        rows.append({"scheme_code": sc, "nav_date": d.date(), "nav_value": round(nav, 4)})
pd.DataFrame(rows).to_csv(BASE / "data" / "raw" / "nav_history.csv", index=False)
print("✅ nav_history.csv created")

# 3. Scheme Returns
pd.DataFrame({
    "scheme_code": schemes,
    "1m_return":  [round(np.random.uniform(-3, 6), 2) for _ in schemes],
    "3m_return":  [round(np.random.uniform(-5, 12), 2) for _ in schemes],
    "6m_return":  [round(np.random.uniform(-8, 18), 2) for _ in schemes],
    "1y_return":  [round(np.random.uniform(-10, 35), 2) for _ in schemes],
    "3y_return":  [round(np.random.uniform(5, 60), 2) for _ in schemes],
    "5y_return":  [round(np.random.uniform(15, 120), 2) for _ in schemes],
}).to_csv(BASE / "data" / "raw" / "scheme_returns.csv", index=False)
print("✅ scheme_returns.csv created")

# 4. Benchmark Index
b_rows = []
bidx = 18000.0
for d in dates:
    bidx = bidx * (1 + np.random.normal(0.0003, 0.007))
    b_rows.append({"date": d.date(), "index_name": "Nifty 100", "close": round(bidx, 2)})
pd.DataFrame(b_rows).to_csv(BASE / "data" / "raw" / "benchmark_index.csv", index=False)
print("✅ benchmark_index.csv created")

# 5. Fund Manager
pd.DataFrame({
    "scheme_code":    schemes,
    "manager_name":   ["Prashant Jain", "S. Naren", "Sailesh Raj Bhan", "Jinesh Gopani",
                       "Harish Krishnan", "Chirag Setalvad", "Apoorva Shah", "Ankit Jain",
                       "Neelesh Surana", "Rajeev Thakkar"],
    "experience_yrs": list(range(10, 20)),
}).to_csv(BASE / "data" / "raw" / "fund_manager.csv", index=False)
print("✅ fund_manager.csv created")

# 6. Portfolio Holdings
stocks = ["Reliance", "HDFC Bank", "Infosys", "ICICI Bank", "TCS", "ITC", "Kotak Bank"]
hold_rows = []
for sc in schemes:
    for stk in stocks:
        hold_rows.append({
            "scheme_code": sc,
            "stock_name":  stk,
            "weight_pct":  round(np.random.uniform(3, 12), 2),
        })
pd.DataFrame(hold_rows).to_csv(BASE / "data" / "raw" / "portfolio_holdings.csv", index=False)
print("✅ portfolio_holdings.csv created")

# 7. AUM History
aum_rows = []
for i, sc in enumerate(schemes):
    aum = (1000 + i * 200)
    for d in pd.date_range(end=date.today(), periods=12, freq="ME"):
        aum = aum * (1 + np.random.normal(0.02, 0.04))
        aum_rows.append({"scheme_code": sc, "date": d.date(), "aum_crore": round(aum, 2)})
pd.DataFrame(aum_rows).to_csv(BASE / "data" / "raw" / "aum_history.csv", index=False)
print("✅ aum_history.csv created")

# 8. Expense Ratio
pd.DataFrame({
    "scheme_code":           schemes,
    "direct_expense_ratio":  [round(np.random.uniform(0.3, 1.2), 2) for _ in schemes],
    "regular_expense_ratio": [round(np.random.uniform(1.2, 2.5), 2) for _ in schemes],
}).to_csv(BASE / "data" / "raw" / "expense_ratio.csv", index=False)
print("✅ expense_ratio.csv created")

# 9. Risk Metrics
pd.DataFrame({
    "scheme_code":  schemes,
    "sharpe_ratio": [round(np.random.uniform(0.4, 1.8), 2) for _ in schemes],
    "beta":         [round(np.random.uniform(0.7, 1.3), 2) for _ in schemes],
    "alpha":        [round(np.random.uniform(-2, 5), 2) for _ in schemes],
    "max_drawdown": [round(np.random.uniform(-35, -8), 2) for _ in schemes],
}).to_csv(BASE / "data" / "raw" / "risk_metrics.csv", index=False)
print("✅ risk_metrics.csv created")

# 10. Investor Transactions
txn_rows = []
for i in range(100):
    txn_rows.append({
        "transaction_id": f"TXN{i:04d}",
        "scheme_code":    np.random.choice(schemes),
        "txn_date":       (date.today() - timedelta(days=np.random.randint(0, 365))).isoformat(),
        "txn_type":       np.random.choice(["BUY", "SELL", "SWP"]),
        "amount":         round(np.random.uniform(1000, 500000), 2),
        "units":          round(np.random.uniform(10, 5000), 3),
    })
pd.DataFrame(txn_rows).to_csv(BASE / "data" / "raw" / "investor_transactions.csv", index=False)
print("✅ investor_transactions.csv created")

print("\n🎉 All 10 CSV files created inside data/raw/ folder!")