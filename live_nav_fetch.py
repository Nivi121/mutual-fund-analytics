import requests
import pandas as pd
import pathlib

# Get project folder path
BASE = pathlib.Path(__file__).parent.resolve()
RAW  = BASE / "data" / "raw"

# The 6 mutual funds we want to fetch
SCHEMES = {
    125497: "HDFC_Top100_Direct",
    119551: "SBI_Bluechip_Direct",
    120503: "ICICI_Bluechip_Direct",
    118632: "Nippon_LargeCap_Direct",
    119092: "Axis_Bluechip_Direct",
    120841: "Kotak_Bluechip_Direct",
}

print("=" * 50)
print("  FETCHING LIVE NAV DATA")
print("=" * 50)

# Store latest NAV of all schemes here
snapshot = []

for code, name in SCHEMES.items():

    print(f"\n📡 Fetching {name} (code: {code}) ...")

    # Call the API (like opening a webpage but for data)
    url      = f"https://api.mfapi.in/mf/{code}"
    response = requests.get(url, timeout=10)

    # Check if it worked
    if response.status_code != 200:
        print(f"  ❌ Failed! Status code: {response.status_code}")
        continue

    # Convert response to Python dictionary
    data = response.json()

    # Get fund details
    meta    = data["meta"]
    records = data["data"]

    print(f"  ✅ Got {len(records)} NAV records")
    print(f"  Fund House : {meta['fund_house']}")
    print(f"  Category   : {meta['scheme_category']}")

    # Convert to DataFrame
    df = pd.DataFrame(records)
    df.columns = ["nav_date", "nav_value"]
    df["scheme_code"] = code
    df["scheme_name"] = meta["scheme_name"]
    df["fund_house"]  = meta["fund_house"]

    # Show latest NAV
    latest = df.iloc[0]
    print(f"  Latest NAV : ₹ {latest['nav_value']} on {latest['nav_date']}")

    # Save individual scheme CSV
    filename = f"nav_{code}_{name}.csv"
    df.to_csv(RAW / filename, index=False)
    print(f"  💾 Saved as {filename}")

    # Add to snapshot
    snapshot.append({
        "scheme_code": code,
        "scheme_name": meta["scheme_name"],
        "fund_house":  meta["fund_house"],
        "category":    meta["scheme_category"],
        "latest_nav":  latest["nav_value"],
        "nav_date":    latest["nav_date"],
    })

# Save snapshot of all latest NAVs
print("\n" + "=" * 50)
snap_df = pd.DataFrame(snapshot)
snap_df.to_csv(RAW / "live_nav_snapshot.csv", index=False)

print("\n📊 LIVE NAV SNAPSHOT:")
print(snap_df.to_string(index=False))
print("\n💾 Saved as live_nav_snapshot.csv")
print("\n✅ ALL DONE!")