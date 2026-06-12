import pathlib

BASE = pathlib.Path(__file__).parent.resolve()

content = """# Data Dictionary — Mutual Fund Analytics Project

> Auto-generated documentation for all tables and columns.

---

## Table: dim_fund
Dimension table containing master information about each mutual fund scheme.

| Column | Data Type | Description |
|---|---|---|
| scheme_code | INTEGER | Unique AMFI code assigned to each mutual fund scheme. Primary Key. |
| scheme_name | TEXT | Full official name of the mutual fund scheme |
| fund_house | TEXT | Name of the Asset Management Company (AMC) |
| category | TEXT | Broad category e.g. Equity, Debt, Hybrid |
| sub_category | TEXT | Specific type e.g. Large Cap, Mid Cap, ELSS |
| risk_grade | TEXT | Risk level: Low / Moderate / Moderately High / High / Very High |
| plan_type | TEXT | Direct or Regular plan |

---

## Table: dim_date
Dimension table with calendar details for every date in the dataset.

| Column | Data Type | Description |
|---|---|---|
| date_id | TEXT | Unique date identifier in YYYY-MM-DD format. Primary Key. |
| full_date | TEXT | Full date in YYYY-MM-DD format |
| day | INTEGER | Day of the month (1-31) |
| month | INTEGER | Month number (1-12) |
| month_name | TEXT | Full month name e.g. January, February |
| quarter | INTEGER | Quarter of the year (1-4) |
| year | INTEGER | Four digit year e.g. 2024 |
| is_weekend | INTEGER | 1 if Saturday or Sunday, 0 otherwise |

---

## Table: fact_nav
Fact table storing daily Net Asset Value (NAV) for each fund scheme.

| Column | Data Type | Description |
|---|---|---|
| nav_id | INTEGER | Auto-incremented unique ID. Primary Key. |
| scheme_code | INTEGER | AMFI code linking to dim_fund. Foreign Key. |
| nav_date | TEXT | Date of the NAV value in YYYY-MM-DD format |
| nav_value | REAL | NAV price in Indian Rupees (₹) on that date |

**Notes:**
- NAV is the per-unit price of the mutual fund
- Weekend and holiday NAVs are forward-filled from last available value
- All NAV values validated to be greater than 0

---

## Table: fact_transactions
Fact table storing all investor buy/sell/SIP transactions.

| Column | Data Type | Description |
|---|---|---|
| transaction_id | TEXT | Unique transaction identifier e.g. TXN0001. Primary Key. |
| scheme_code | INTEGER | AMFI code linking to dim_fund. Foreign Key. |
| txn_date | TEXT | Date of the transaction in YYYY-MM-DD format |
| txn_type | TEXT | Type: SIP / Lumpsum / Redemption |
| amount | REAL | Transaction amount in Indian Rupees (₹) |
| units | REAL | Number of fund units bought or sold |

**Transaction Types:**
- **SIP** — Systematic Investment Plan (regular monthly investment)
- **Lumpsum** — One-time bulk investment
- **Redemption** — Withdrawal/selling of units

---

## Table: fact_performance
Fact table storing return percentages for each fund over different time periods.

| Column | Data Type | Description |
|---|---|---|
| perf_id | INTEGER | Auto-incremented unique ID. Primary Key. |
| scheme_code | INTEGER | AMFI code linking to dim_fund. Foreign Key. |
| 1m_return | REAL | Returns over last 1 month (%) |
| 3m_return | REAL | Returns over last 3 months (%) |
| 6m_return | REAL | Returns over last 6 months (%) |
| 1y_return | REAL | Returns over last 1 year (%) |
| 3y_return | REAL | Returns over last 3 years (%) |
| 5y_return | REAL | Returns over last 5 years (%) |

**Notes:**
- All return values are percentages
- Negative values indicate losses
- Anomalies flagged if return > 200% or < -100%

---

## Table: fact_aum
Fact table storing monthly Assets Under Management for each fund.

| Column | Data Type | Description |
|---|---|---|
| aum_id | INTEGER | Auto-incremented unique ID. Primary Key. |
| scheme_code | INTEGER | AMFI code linking to dim_fund. Foreign Key. |
| date | TEXT | Month-end date in YYYY-MM-DD format |
| aum_crore | REAL | Total assets managed in Indian Crores (₹) |

**Notes:**
- AUM = total market value of all investments managed by the fund
- Higher AUM generally indicates more investor trust
- 1 Crore = 10 Million Indian Rupees

---

## Source Files

| File | Source | Rows | Description |
|---|---|---|---|
| fund_master.csv | AMFI / Sample | 10 | Master list of all fund schemes |
| nav_history.csv | AMFI / Sample | 3,650 | Raw daily NAV history |
| nav_history_clean.csv | Processed | 5,110 | Cleaned NAV with forward-fill |
| investor_transactions.csv | Sample | 100 | Raw investor transactions |
| investor_transactions_clean.csv | Processed | 100 | Cleaned transactions |
| scheme_returns.csv | Sample | 10 | Fund return percentages |
| scheme_performance_clean.csv | Processed | 10 | Validated performance data |
| aum_history.csv | Sample | 120 | Monthly AUM data |
| expense_ratio.csv | Sample | 10 | Fund expense ratios |
| risk_metrics.csv | Sample | 10 | Risk metrics per fund |

---

## Key Business Terms

| Term | Definition |
|---|---|
| NAV | Net Asset Value — price of one unit of a mutual fund |
| AUM | Assets Under Management — total money managed by fund |
| AMFI | Association of Mutual Funds in India — regulatory body |
| SIP | Systematic Investment Plan — fixed monthly investment |
| Expense Ratio | Annual fee charged by fund (% of AUM) |
| Direct Plan | Fund bought directly without broker (lower fees) |
| Regular Plan | Fund bought through broker (higher fees) |
| Large Cap | Funds investing in top 100 companies by market cap |
| Mid Cap | Funds investing in 101-250 ranked companies |
| ELSS | Equity Linked Savings Scheme — tax saving fund |
"""

output = BASE / "data_dictionary.md"
output.write_text(content, encoding="utf-8")
print("✅ data_dictionary.md created successfully!")
print(f"   Saved to: {output}")