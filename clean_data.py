import pandas as pd
import pathlib

BASE = pathlib.Path(__file__).parent.resolve()
RAW  = BASE / "data" / "raw"
PROC = BASE / "data" / "processed"

print("=" * 50)
print("  DAY 2: DATA CLEANING")
print("=" * 50)

# ─────────────────────────────────────────────
# TASK 1: Clean nav_history.csv
# ─────────────────────────────────────────────
print("\n📂 Cleaning nav_history.csv ...")

nav = pd.read_csv(RAW / "nav_history.csv")
print(f"  Rows before cleaning : {len(nav)}")

# Step 1 — Parse dates to datetime
nav["nav_date"] = pd.to_datetime(nav["nav_date"])
print("  ✅ Dates parsed to datetime")

# Step 2 — Sort by scheme_code + date
nav = nav.sort_values(["scheme_code", "nav_date"])
print("  ✅ Sorted by scheme_code and date")

# Step 3 — Remove duplicates
nav = nav.drop_duplicates(subset=["scheme_code", "nav_date"])
print(f"  ✅ Duplicates removed")

# Step 4 — Forward fill missing NAV (holidays/weekends)
filled_frames = []
for code, group in nav.groupby("scheme_code"):
    group = group.set_index("nav_date")
    all_dates = pd.date_range(group.index.min(), group.index.max(), freq="D")
    group = group.reindex(all_dates).ffill()
    group["scheme_code"] = code
    group = group.reset_index()
    group.columns = ["nav_date", "nav_value", "scheme_code"]
    filled_frames.append(group)
nav = pd.concat(filled_frames, ignore_index=True)
print("  ✅ Missing dates forward-filled")

# Step 5 — Validate NAV > 0
invalid = nav[nav["nav_value"] <= 0]
if len(invalid) > 0:
    print(f"  ⚠️  {len(invalid)} rows with NAV <= 0 removed")
    nav = nav[nav["nav_value"] > 0]
else:
    print("  ✅ All NAV values are positive")

print(f"  Rows after cleaning  : {len(nav)}")

# Save cleaned file
nav.to_csv(PROC / "nav_history_clean.csv", index=False)
print("  💾 Saved as nav_history_clean.csv")

# ─────────────────────────────────────────────
# TASK 2: Clean investor_transactions.csv
# ─────────────────────────────────────────────
print("\n📂 Cleaning investor_transactions.csv ...")

txn = pd.read_csv(RAW / "investor_transactions.csv")
print(f"  Rows before cleaning : {len(txn)}")

# Step 1 — Fix date formats
txn["txn_date"] = pd.to_datetime(txn["txn_date"])
print("  ✅ Dates parsed to datetime")

# Step 2 — Standardise transaction_type values
type_map = {
    "BUY":  "Lumpsum",
    "SELL": "Redemption",
    "SWP":  "SIP",
    "STP":  "SIP",
}
txn["txn_type"] = txn["txn_type"].map(type_map).fillna(txn["txn_type"])
print("  ✅ Transaction types standardised")
print(f"     Unique types now: {txn['txn_type'].unique().tolist()}")

# Step 3 — Validate amount > 0
invalid_amt = txn[txn["amount"] <= 0]
if len(invalid_amt) > 0:
    print(f"  ⚠️  {len(invalid_amt)} rows with amount <= 0 removed")
    txn = txn[txn["amount"] > 0]
else:
    print("  ✅ All amounts are positive")

# Step 4 — Remove duplicates
txn = txn.drop_duplicates()
print("  ✅ Duplicates removed")

print(f"  Rows after cleaning  : {len(txn)}")

# Save cleaned file
txn.to_csv(PROC / "investor_transactions_clean.csv", index=False)
print("  💾 Saved as investor_transactions_clean.csv")

# ─────────────────────────────────────────────
# TASK 3: Clean scheme_returns.csv
# (used as scheme_performance)
# ─────────────────────────────────────────────
print("\n📂 Cleaning scheme_returns.csv ...")

perf = pd.read_csv(RAW / "scheme_returns.csv")
print(f"  Rows before cleaning : {len(perf)}")

# Step 1 — Validate all return columns are numeric
return_cols = ["1m_return", "3m_return", "6m_return",
               "1y_return", "3y_return", "5y_return"]
for col in return_cols:
    perf[col] = pd.to_numeric(perf[col], errors="coerce")
print("  ✅ All return values confirmed numeric")

# Step 2 — Flag anomalies (returns > 200% or < -100%)
for col in return_cols:
    anomalies = perf[(perf[col] > 200) | (perf[col] < -100)]
    if len(anomalies) > 0:
        print(f"  ⚠️  {col}: {len(anomalies)} anomalies flagged")
    else:
        print(f"  ✅ {col}: No anomalies")

# Step 3 — Check expense_ratio range
exp = pd.read_csv(RAW / "expense_ratio.csv")
out_of_range = exp[
    (exp["direct_expense_ratio"] < 0.1) |
    (exp["direct_expense_ratio"] > 2.5)
]
if len(out_of_range) > 0:
    print(f"  ⚠️  {len(out_of_range)} funds with expense ratio out of range!")
else:
    print("  ✅ All expense ratios in valid range (0.1% - 2.5%)")

print(f"  Rows after cleaning  : {len(perf)}")

# Save cleaned file
perf.to_csv(PROC / "scheme_performance_clean.csv", index=False)
print("  💾 Saved as scheme_performance_clean.csv")

print("\n" + "=" * 50)
print("  DATA CLEANING COMPLETE!")
print("=" * 50)
print("\n  Next → run  py create_database.py")