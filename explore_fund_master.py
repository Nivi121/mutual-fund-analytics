import pandas as pd
import pathlib

BASE = pathlib.Path(__file__).parent.resolve()
RAW  = BASE / "data" / "raw"

# Load fund master
df = pd.read_csv(RAW / "fund_master.csv")

print("=" * 50)
print("  FUND MASTER EXPLORATION")
print("=" * 50)

# 1. Unique Fund Houses
print("\n🏦 FUND HOUSES:")
for fh in sorted(df["fund_house"].unique()):
    count = (df["fund_house"] == fh).sum()
    print(f"  • {fh:<25} {count} schemes")

# 2. Unique Categories
print("\n📁 CATEGORIES:")
for cat in sorted(df["category"].unique()):
    count = (df["category"] == cat).sum()
    print(f"  • {cat:<25} {count} schemes")

# 3. Unique Sub-Categories
print("\n📂 SUB-CATEGORIES:")
for sub in sorted(df["sub_category"].unique()):
    count = (df["sub_category"] == sub).sum()
    print(f"  • {sub:<25} {count} schemes")

# 4. Risk Grades
print("\n⚠️  RISK GRADES:")
for risk in sorted(df["risk_grade"].unique()):
    count = (df["risk_grade"] == risk).sum()
    print(f"  • {risk:<25} {count} schemes")

# 5. AMFI Scheme Code Structure
print("\n🔢 AMFI SCHEME CODE STRUCTURE:")
print(f"  Total schemes    : {len(df)}")
print(f"  Lowest code      : {df['scheme_code'].min()}")
print(f"  Highest code     : {df['scheme_code'].max()}")
print(f"  Code digit length: {len(str(df['scheme_code'].iloc[0]))} digits")
print("\n  Sample codes:")
for _, row in df.head(5).iterrows():
    print(f"  • {row['scheme_code']}  →  {row['scheme_name']}")

print("\n" + "=" * 50)
print("  EXPLORATION COMPLETE!")
print("=" * 50)