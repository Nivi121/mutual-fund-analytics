"""
live_nav_fetch.py
=================
Fetches real-time Net Asset Value (NAV) data from the public Mutual Fund API (mfapi.in).
Downloads historical NAV structures for target AMFI schemes, logs the latest NAV,
and stores individual csv logs and a snapshot summary in data/raw/.
"""

import sys
import pathlib
import pandas as pd
import requests

# Force stdout encoding to UTF-8 if supported
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Default base path is the directory containing this script
BASE_PATH = pathlib.Path(__file__).parent.resolve()

SCHEMES = {
    125497: "HDFC_Top100_Direct",
    119551: "SBI_Bluechip_Direct",
    120503: "ICICI_Bluechip_Direct",
    118632: "Nippon_LargeCap_Direct",
    119092: "Axis_Bluechip_Direct",
    120841: "Kotak_Bluechip_Direct",
}


def fetch_live_navs(base_path: pathlib.Path = BASE_PATH) -> bool:
    """
    Queries the mfapi.in API for each pre-defined mutual fund scheme,
    extracts the metadata and NAV history, writes individual CSVs,
    and updates the latest NAV snapshot.

    Args:
        base_path (pathlib.Path): The root directory of the project.

    Returns:
        bool: True if the operation was successful for at least one fund,
              False if there was a complete system failure or network error.
    """
    raw_dir = base_path / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  FETCHING LIVE NAV DATA FROM MFAPI.IN")
    print("=" * 60)

    snapshot = []
    successful_fetches = 0

    for code, name in SCHEMES.items():
        print(f"\nQuerying API for {name} (AMFI: {code}) ...")
        url = f"https://api.mfapi.in/mf/{code}"

        try:
            # Fetch with a 10-second timeout
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                print(f"  [ERROR] API returned status code: {response.status_code}")
                continue

            # Convert response to dictionary
            data = response.json()
            meta = data.get("meta", {})
            records = data.get("data", [])

            if not records:
                print("  [ERROR] Received empty dataset from API.")
                continue

            print(f"  [OK] Retrieved {len(records)} NAV history records.")
            print(f"    - Fund House: {meta.get('fund_house', 'N/A')}")
            print(f"    - Category  : {meta.get('scheme_category', 'N/A')}")

            # Convert records to DataFrame
            df = pd.DataFrame(records)
            df.columns = ["nav_date", "nav_value"]
            df["scheme_code"] = code
            df["scheme_name"] = meta.get("scheme_name", name)
            df["fund_house"] = meta.get("fund_house", "N/A")

            # Get the latest entry
            latest = df.iloc[0]
            print(f"    - Latest NAV: Rs. {latest['nav_value']} on {latest['nav_date']}")

            # Save individual CSV
            filename = f"nav_{code}_{name}.csv"
            df.to_csv(raw_dir / filename, index=False)
            print(f"    - Saved individual CSV to data/raw/{filename}")

            # Append to snapshot summary
            snapshot.append({
                "scheme_code": code,
                "scheme_name": meta.get("scheme_name", name),
                "fund_house": meta.get("fund_house", "N/A"),
                "category": meta.get("scheme_category", "N/A"),
                "latest_nav": latest["nav_value"],
                "nav_date": latest["nav_date"],
            })
            successful_fetches += 1

        except requests.exceptions.Timeout:
            print("  [ERROR] Connection timed out (10s limit exceeded). Skipping.")
        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Network/Connection error occurred: {e}. Skipping.")
        except Exception as e:
            print(f"  [ERROR] Unexpected error parsing response: {e}. Skipping.")

    print("\n" + "=" * 60)
    if successful_fetches > 0:
        snap_df = pd.DataFrame(snapshot)
        snap_df.to_csv(raw_dir / "live_nav_snapshot.csv", index=False)
        print("LIVE NAV SNAPSHOT SUMMARY:")
        print(snap_df.to_string(index=False))
        print(f"\nSaved live snapshot to: data/raw/live_nav_snapshot.csv")
        print(f"  Successfully fetched {successful_fetches}/{len(SCHEMES)} schemes.")
        print("=" * 60)
        return True
    else:
        print("  [ERROR] FAILED TO FETCH ANY LIVE NAV DATA (API is offline or network is disconnected).")
        print("=" * 60)
        return False


if __name__ == "__main__":
    fetch_live_navs()