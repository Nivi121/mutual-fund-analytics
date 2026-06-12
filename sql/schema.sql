

-- Dimension Table: Fund details
CREATE TABLE IF NOT EXISTS dim_fund (
    scheme_code     INTEGER PRIMARY KEY,
    scheme_name     TEXT    NOT NULL,
    fund_house      TEXT    NOT NULL,
    category        TEXT,
    sub_category    TEXT,
    risk_grade      TEXT,
    plan_type       TEXT
);

-- Dimension Table: Date details
CREATE TABLE IF NOT EXISTS dim_date (
    date_id         TEXT    PRIMARY KEY,
    full_date       TEXT    NOT NULL,
    day             INTEGER,
    month           INTEGER,
    month_name      TEXT,
    quarter         INTEGER,
    year            INTEGER,
    is_weekend      INTEGER
);

-- Fact Table: Daily NAV
CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code     INTEGER NOT NULL,
    nav_date        TEXT    NOT NULL,
    nav_value       REAL    NOT NULL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);

-- Fact Table: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id  TEXT    PRIMARY KEY,
    scheme_code     INTEGER NOT NULL,
    txn_date        TEXT    NOT NULL,
    txn_type        TEXT    NOT NULL,
    amount          REAL    NOT NULL,
    units           REAL    NOT NULL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);

-- Fact Table: Scheme Performance / Returns
CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code     INTEGER NOT NULL,
    return_1m       REAL,
    return_3m       REAL,
    return_6m       REAL,
    return_1y       REAL,
    return_3y       REAL,
    return_5y       REAL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);

-- Fact Table: AUM History
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code     INTEGER NOT NULL,
    aum_date        TEXT    NOT NULL,
    aum_crore       REAL    NOT NULL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund(scheme_code)
);
