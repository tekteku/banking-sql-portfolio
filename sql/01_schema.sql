-- ============================================================
-- Banking SQL Portfolio — Schema
-- 6 tables, production-quality constraints and indexes
-- ============================================================

CREATE TABLE IF NOT EXISTS clients (
                                       id              INTEGER PRIMARY KEY AUTOINCREMENT,
                                       first_name      TEXT    NOT NULL,
                                       last_name       TEXT    NOT NULL,
                                       email           TEXT    NOT NULL UNIQUE,
                                       age             INTEGER NOT NULL CHECK (age >= 18),
    monthly_income  REAL    NOT NULL CHECK (monthly_income >= 0),
    city            TEXT    NOT NULL,
    country         TEXT    NOT NULL DEFAULT 'France',
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
    );

CREATE TABLE IF NOT EXISTS accounts (
                                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                                        client_id       INTEGER NOT NULL REFERENCES clients(id),
    account_no      TEXT    NOT NULL UNIQUE,
    account_type    TEXT    NOT NULL
    CHECK (account_type IN ('CHECKING','SAVINGS','INVESTMENT')),
    balance         REAL    NOT NULL DEFAULT 0 CHECK (balance >= 0),
    currency        TEXT    NOT NULL DEFAULT 'EUR',
    opened_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    is_active       INTEGER NOT NULL DEFAULT 1
    );

CREATE TABLE IF NOT EXISTS transactions (
                                            id              INTEGER PRIMARY KEY AUTOINCREMENT,
                                            from_account_id INTEGER REFERENCES accounts(id),
    to_account_id   INTEGER REFERENCES accounts(id),
    amount          REAL    NOT NULL CHECK (amount > 0),
    tx_type         TEXT    NOT NULL
    CHECK (tx_type IN ('DEPOSIT','WITHDRAWAL','TRANSFER','FEE')),
    status          TEXT    NOT NULL DEFAULT 'COMPLETED'
    CHECK (status IN ('PENDING','COMPLETED','FAILED')),
    tx_date         TEXT    NOT NULL DEFAULT (datetime('now')),
    description     TEXT,
    CHECK (from_account_id IS NOT NULL OR to_account_id IS NOT NULL)
    );

CREATE TABLE IF NOT EXISTS policies (
                                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                                        client_id       INTEGER NOT NULL REFERENCES clients(id),
    policy_type     TEXT    NOT NULL
    CHECK (policy_type IN ('AUTO','HOME','HEALTH','LIFE')),
    coverage_amount REAL    NOT NULL CHECK (coverage_amount >= 1000),
    annual_premium  REAL    NOT NULL CHECK (annual_premium > 0),
    deductible      REAL    NOT NULL DEFAULT 0,
    start_date      TEXT    NOT NULL,
    end_date        TEXT    NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
    );

CREATE TABLE IF NOT EXISTS claims (
                                      id              INTEGER PRIMARY KEY AUTOINCREMENT,
                                      policy_id       INTEGER NOT NULL REFERENCES policies(id),
    claimed_amount  REAL    NOT NULL CHECK (claimed_amount > 0),
    approved_amount REAL    CHECK (approved_amount >= 0),
    incident_date   TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'SUBMITTED'
    CHECK (status IN
('SUBMITTED','UNDER_REVIEW','APPROVED','REJECTED','PAID')),
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
    );

CREATE TABLE IF NOT EXISTS risk_scores (
                                           id          INTEGER PRIMARY KEY AUTOINCREMENT,
                                           client_id   INTEGER NOT NULL UNIQUE REFERENCES clients(id),
    score       INTEGER NOT NULL CHECK (score BETWEEN 0 AND 100),
    risk_level  TEXT    NOT NULL
    CHECK (risk_level IN ('LOW','MEDIUM','HIGH','VERY_HIGH')),
    computed_at TEXT    NOT NULL DEFAULT (datetime('now'))
    );

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_accounts_client   ON accounts(client_id);
CREATE INDEX IF NOT EXISTS idx_tx_from           ON transactions(from_account_id);
CREATE INDEX IF NOT EXISTS idx_tx_to             ON transactions(to_account_id);
CREATE INDEX IF NOT EXISTS idx_tx_date           ON transactions(tx_date);
CREATE INDEX IF NOT EXISTS idx_policies_client   ON policies(client_id);
CREATE INDEX IF NOT EXISTS idx_claims_policy     ON claims(policy_id);
CREATE INDEX IF NOT EXISTS idx_claims_status     ON claims(status);