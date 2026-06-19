"""
run_pipeline.py
===============
Bluestock Mutual Fund Analytics — Master Execution Script
Orchestrates and runs the complete data pipeline from dataset generation,
ingestion, cleaning, database storage, SQL querying, metadata exploration,
and database dictionary generation.

Usage:
    python run_pipeline.py [options]

Options:
    -h, --help       Show this help message and exit.
    --skip-live      Skip fetching live NAV data from mfapi.in API (Step 3).
"""

import subprocess
import sys
import time
from pathlib import Path

# Force stdout encoding to UTF-8 if supported
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Base directory path
BASE = Path(__file__).resolve().parent

# Pipeline steps in execution order
STEPS = [
    ("create_sample_data.py",      "Step 1: Prepare and map raw client datasets"),
    ("data_ingestion.py",          "Step 2: Profile structural dataset inputs"),
    ("live_nav_fetch.py",          "Step 3: Fetch real-time AMFI NAV logs"),
    ("clean_data.py",              "Step 4: Execute data cleaning transformations"),
    ("create_database.py",         "Step 5: Setup SQLite schema and load values"),
    ("write_queries.py",           "Step 6: Run 10 analytical SQL queries"),
    ("explore_fund_master.py",     "Step 7: Profile raw Fund Master categorizations"),
    ("validate_data.py",           "Step 8: Execute Data Quality validations"),
    ("create_data_dictionary.py",  "Step 9: Compile database documentation dictionary"),
]


def display_help() -> None:
    """
    Prints utility usage guidelines and flags.
    """
    print(__doc__)


def run_script(script_name: str, description: str) -> bool:
    """
    Spawns a subprocess to execute a pipeline python script,
    captures its stdout and stderr, and logs statuses cleanly.

    Args:
        script_name (str): File name of the python script to run.
        description (str): Explanatory text of the pipeline step.

    Returns:
        bool: True if execution code is 0, False if an error occurred.
    """
    print(f"\n{'-'*65}")
    print(f"  >  {description}")
    print(f"{'-'*65}")

    script_path = BASE / script_name

    if not script_path.exists():
        print(f"  [ERROR] Script file not found: {script_name}")
        return False

    start = time.time()

    # Launch subprocess running the target script
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    elapsed = round(time.time() - start, 1)

    if result.returncode == 0:
        print(f"  [OK] Completed in {elapsed}s")
        return True
    else:
        print(f"  [FAIL] Failed after {elapsed}s with exit code {result.returncode}")
        print("\n--- ERROR DETAIL FROM SUBPROCESS ---")
        if result.stderr.strip():
            print(result.stderr.strip())
        elif result.stdout.strip():
            print(result.stdout.strip())
        else:
            print("No output reported by the process.")
        print("------------------------------------\n")
        return False


def main() -> None:
    """
    Parses arguments, runs steps sequentially, and prints a final pipeline summary report.
    """
    args = sys.argv[1:]

    if "-h" in args or "--help" in args:
        display_help()
        sys.exit(0)

    skip_live = "--skip-live" in args

    print("=" * 65)
    print("  BLUESTOCK MF ANALYTICS - ETL PIPELINE EXECUTION ENGINE")
    print("=" * 65)

    results = []
    overall_success = True

    for script, description in STEPS:
        if script == "live_nav_fetch.py" and skip_live:
            print(f"\n{'-'*65}")
            print(f"  >  {description}")
            print(f"{'-'*65}")
            print("  [SKIP] Skipping live NAV API download (offline flag active).")
            results.append((description, True, "SKIPPED"))
            continue

        success = run_script(script, description)
        results.append((description, success, "COMPLETED" if success else "FAILED"))

        if not success:
            overall_success = False
            print(f"\n  [WARNING] Pipeline halted due to error in {script}.")
            break

    # Final summary report
    print(f"\n{'='*65}")
    print("  PIPELINE EXECUTION SUMMARY")
    print(f"{'='*65}")

    for desc, success, status in results:
        if status == "SKIPPED":
            icon = "[SKIP]"
            label = "Skipped"
        else:
            icon = "[OK]" if success else "[FAIL]"
            label = "Passed" if success else "Failed"
        print(f"  {icon:<8} {desc:<45} [{label}]")

    print(f"\n  Final Pipeline Status: {'SUCCESS' if overall_success else 'FAILED'}")
    print(f"{'='*65}\n")

    if overall_success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()