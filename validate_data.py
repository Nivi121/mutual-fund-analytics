import pandas as pd
import pathlib

BASE = pathlib.Path(__file__).parent.resolve()
RAW  = BASE / "data" / "raw"
REPORTS = BASE / "reports"

# Load the two files we need to cross-check
fund_master = pd.read_csv(RAW / "fund_master.csv")
nav_history = pd.read_csv(RAW / "nav_history.csv")

print("=" * 50)
print("  DATA QUALITY VALIDATION")
print("=" * 50)

# ── Check 1: AMFI Code Validation ──────────────
print("\n🔍 CHECK 1: AMFI CODE VALIDATION")
print("  Do all codes in fund_master exist in nav_history?")

master_codes = set(fund_master["scheme_code"].unique())
nav_codes    = set(nav_history["scheme_code"].unique())

matched  = master_codes & nav_codes   # codes in BOTH
missing  = master_codes - nav_codes   # codes in master but NOT in nav

print(f"\n  Total codes in fund_master  : {len(master_codes)}")
print(f"  Total codes in nav_history  : {len(nav_codes)}")
print(f"  Codes matched               : {len(matched)}")
print(f"  Codes missing from nav      : {len(missing)}")

if missing:
    print(f"\n  ⚠️  Missing codes:")
    for code in sorted(missing):
        print(f"    • {code}")
else:
    print(f"\n  ✅  All codes matched!")

# ── Check 2: Missing Values ─────────────────────
print("\n🔍 CHECK 2: MISSING VALUES IN ALL FILES")

csv_files = [
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

all_clean = True
for filename in csv_files:
    df    = pd.read_csv(RAW / filename)
    nulls = df.isnull().sum().sum()
    if nulls > 0:
        print(f"  ⚠️  {filename:<35} {nulls} missing values")
        all_clean = False
    else:
        print(f"  ✅  {filename:<35} Clean!")

# ── Check 3: Duplicate Rows ─────────────────────
print("\n🔍 CHECK 3: DUPLICATE ROWS")

for filename in csv_files:
    df   = pd.read_csv(RAW / filename)
    dups = df.duplicated().sum()
    if dups > 0:
        print(f"  ⚠️  {filename:<35} {dups} duplicates")
    else:
        print(f"  ✅  {filename:<35} No duplicates!")

# ── Write Summary Report ────────────────────────
print("\n" + "=" * 50)
print("  WRITING QUALITY REPORT...")

report = f"""
DATA QUALITY SUMMARY REPORT
============================

1. AMFI CODE VALIDATION
   Total codes in fund_master  : {len(master_codes)}
   Total codes in nav_history  : {len(nav_codes)}
   Codes matched               : {len(matched)}
   Codes missing               : {len(missing)}
   Result: {'✅ ALL CODES MATCHED' if not missing else '⚠️ SOME CODES MISSING'}

2. MISSING VALUES
   Result: {'✅ ALL FILES CLEAN' if all_clean else '⚠️ SOME FILES HAVE MISSING VALUES'}

3. OVERALL STATUS
   {'✅ DATA QUALITY IS GOOD!' if not missing and all_clean else '⚠️ SOME ISSUES FOUND - CHECK ABOVE'}
"""

report_path = REPORTS / "data_quality_summary.txt"
report_path.write_text(report, encoding="utf-8")

print(f"  ✅ Report saved to reports/data_quality_summary.txt")
print("\n" + "=" * 50)
print("  VALIDATION COMPLETE!")
print("=" * 50)