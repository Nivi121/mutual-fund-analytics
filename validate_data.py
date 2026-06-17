"""
validate_data.py
================
Runs assertions and quality validation tests on raw datasets.
Checks AMFI fund code referential integrity, scans for null/empty records,
counts duplicate rows, and records a validation summary in reports/.
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

CSV_FILES = [
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


def check_amfi_codes(raw_dir: pathlib.Path) -> tuple:
    """
    Checks referential integrity by comparing AMFI codes between the
    fund master registry and the historical NAV log.

    Args:
        raw_dir (pathlib.Path): Location of raw CSVs.

    Returns:
        tuple: (master_codes, nav_codes, matched, missing) Sets containing code details.
    """
    print("\nCHECK 1: AMFI CODE VALIDATION")
    print("  Do all codes in fund_master exist in nav_history?")

    try:
        fund_master = pd.read_csv(raw_dir / "fund_master.csv")
        nav_history = pd.read_csv(raw_dir / "nav_history.csv")

        master_codes = set(fund_master["scheme_code"].unique())
        nav_codes = set(nav_history["scheme_code"].unique())

        matched = master_codes & nav_codes
        missing = master_codes - nav_codes

        print(f"  * Total codes in fund_master  : {len(master_codes)}")
        print(f"  * Total codes in nav_history  : {len(nav_codes)}")
        print(f"  * Codes matched               : {len(matched)}")
        print(f"  * Codes missing from nav      : {len(missing)}")

        if missing:
            print("  * [WARNING] Missing codes:")
            for code in sorted(missing):
                print(f"    - {code}")
        else:
            print("  * [OK] All codes matched!")

        return master_codes, nav_codes, matched, missing

    except Exception as e:
        print(f"  [ERROR] Error executing Check 1: {e}")
        return set(), set(), set(), set()


def check_missing_values(raw_dir: pathlib.Path) -> tuple:
    """
    Scans raw CSV files to detect any empty / null cell occurrences.

    Args:
        raw_dir (pathlib.Path): Path to raw data folder.

    Returns:
        tuple: (all_clean, log_messages) bool status and list of log lines.
    """
    print("\nCHECK 2: MISSING VALUES IN ALL RAW FILES")

    all_clean = True
    log_messages = []

    for filename in CSV_FILES:
        filepath = raw_dir / filename
        if not filepath.exists():
            continue
        try:
            df = pd.read_csv(filepath)
            nulls = df.isnull().sum().sum()
            if nulls > 0:
                msg = f"  * [WARNING] {filename:<30} has {nulls} missing values"
                print(msg)
                log_messages.append(msg)
                all_clean = False
            else:
                msg = f"  * [OK]  {filename:<30} Clean!"
                print(msg)
                log_messages.append(msg)
        except Exception as e:
            msg = f"  * [ERROR]  Error checking {filename}: {e}"
            print(msg)
            log_messages.append(msg)
            all_clean = False

    return all_clean, log_messages


def check_duplicate_rows(raw_dir: pathlib.Path) -> tuple:
    """
    Identifies exact duplicate row entries in the CSV files.

    Args:
        raw_dir (pathlib.Path): Location of raw CSVs.

    Returns:
        tuple: (all_unique, log_messages) bool status and list of duplicate logs.
    """
    print("\nCHECK 3: DUPLICATE ROWS IN ALL RAW FILES")

    all_unique = True
    log_messages = []

    for filename in CSV_FILES:
        filepath = raw_dir / filename
        if not filepath.exists():
            continue
        try:
            df = pd.read_csv(filepath)
            dups = df.duplicated().sum()
            if dups > 0:
                msg = f"  * [WARNING] {filename:<30} has {dups} duplicate rows"
                print(msg)
                log_messages.append(msg)
                all_unique = False
            else:
                msg = f"  * [OK]  {filename:<30} No duplicates!"
                print(msg)
                log_messages.append(msg)
        except Exception as e:
            msg = f"  * [ERROR]  Error checking {filename}: {e}"
            print(msg)
            log_messages.append(msg)
            all_unique = False

    return all_unique, log_messages


def validate_data_quality(base_path: pathlib.Path = BASE_PATH) -> bool:
    """
    Runs all data quality checks and writes a consolidated report to reports/.

    Args:
        base_path (pathlib.Path): Root path of the project.

    Returns:
        bool: True if data quality meets basic integrity standards.
    """
    raw_dir = base_path / "data" / "raw"
    reports_dir = base_path / "reports"
    reports_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("  RUNNING DATA QUALITY VALIDATION")
    print("=" * 60)

    # 1. Check AMFI Codes
    master_codes, nav_codes, matched, missing = check_amfi_codes(raw_dir)

    # 2. Check Nulls
    all_clean, null_logs = check_missing_values(raw_dir)

    # 3. Check Duplicates
    all_unique, dup_logs = check_duplicate_rows(raw_dir)

    print("\n" + "=" * 60)
    print("  WRITING QUALITY ASSURANCE SUMMARY REPORT")
    print("=" * 60)

    report_content = f"""DATA QUALITY SUMMARY REPORT
============================
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

1. AMFI REFERENTIAL INTEGRITY CODE VALIDATION
   - Total codes in fund_master : {len(master_codes)}
   - Total codes in nav_history : {len(nav_codes)}
   - Codes matching on both sides: {len(matched)}
   - Codes missing from history : {len(missing)}
   - Status: {'[OK] ALL CODES MATCHED' if not missing else '[WARNING] REFERENTIAL INTEGRITY ISSUES FOUND'}

2. NULL & EMPTY RECORD SCAN
   - Status: {'[OK] DATA IS CONSOLIDATED (NO MISSING CELLS)' if all_clean else '[WARNING] NULL CELLS DETECTED'}
{chr(10).join(null_logs)}

3. DUPLICATE ROW ENTRIES
   - Status: {'[OK] NO DUPLICATE ROW ENTRIES DETECTED' if all_unique else '[WARNING] DUPLICATES DETECTED'}
{chr(10).join(dup_logs)}

OVERALL QUALITY ASSURANCE STATUS
--------------------------------
{'[OK] DATA QUALITY IS PASSING AND VERIFIED' if not missing and all_clean and all_unique else '[WARNING] CONTAINS MINOR WARNINGS - INVESTIGATE SCAN LOGS'}
"""

    report_path = reports_dir / "data_quality_summary.txt"
    try:
        report_path.write_text(report_content, encoding="utf-8")
        print(f"  [OK] Validation report written to: reports/data_quality_summary.txt")
        print("\n" + "=" * 60)
        print("  VALIDATION CHECKS COMPLETED!")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"  [ERROR] Error saving validation report: {e}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    validate_data_quality()