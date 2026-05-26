-- ==============================================================================
-- Banking Fraud Detection System - Phase 1 Schema
-- Target RDBMS: PostgreSQL
-- Design: 3NF, Production-Grade
-- ==============================================================================

-- Enable UUID extension (requires superuser, often enabled by default in modern pg)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================================================
-- 1. CUSTOMERS
-- Stores core customer identity and PII.
-- ==============================================================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uq_customers_email UNIQUE (email),
    CONSTRAINT uq_customers_phone UNIQUE (phone),
    CONSTRAINT chk_customers_status CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'LOCKED'))
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);

-- ==============================================================================
-- 2. ACCOUNTS
-- A customer can have multiple accounts (checking, savings, credit).
-- ==============================================================================
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL,
    account_number VARCHAR(34) NOT NULL, -- Up to 34 chars for IBAN
    account_type VARCHAR(20) NOT NULL,
    currency CHAR(3) NOT NULL, -- ISO 4217 Currency Code (e.g., USD, EUR)
    balance NUMERIC(19, 4) NOT NULL DEFAULT 0.0000, -- Financial grade precision
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_accounts_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT,
    CONSTRAINT uq_accounts_account_number UNIQUE (account_number),
    CONSTRAINT chk_accounts_type CHECK (account_type IN ('CHECKING', 'SAVINGS', 'CREDIT', 'LOAN')),
    CONSTRAINT chk_accounts_status CHECK (status IN ('ACTIVE', 'FROZEN', 'CLOSED', 'RESTRICTED'))
);

CREATE INDEX idx_accounts_customer_id ON accounts(customer_id);
CREATE INDEX idx_accounts_account_number ON accounts(account_number);

-- ==============================================================================
-- 3. DEVICES
-- Tracks known devices used by customers to detect anomalies (new device logins).
-- ==============================================================================
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL,
    device_fingerprint VARCHAR(255) NOT NULL, -- Hash of device characteristics
    device_type VARCHAR(20) NOT NULL,
    os_version VARCHAR(50),
    is_trusted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_devices_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    CONSTRAINT uq_devices_fingerprint_customer UNIQUE (device_fingerprint, customer_id),
    CONSTRAINT chk_devices_type CHECK (device_type IN ('MOBILE', 'DESKTOP', 'TABLET', 'UNKNOWN'))
);

CREATE INDEX idx_devices_customer_id ON devices(customer_id);
CREATE INDEX idx_devices_fingerprint ON devices(device_fingerprint);

-- ==============================================================================
-- 4. MERCHANTS
-- Stores merchant data for transaction classification and risk profiling.
-- ==============================================================================
CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_name VARCHAR(255) NOT NULL,
    category_code CHAR(4) NOT NULL, -- Merchant Category Code (MCC)
    country_code CHAR(2) NOT NULL, -- ISO 3166-1 alpha-2
    risk_tier VARCHAR(10) NOT NULL DEFAULT 'LOW', -- Calculated risk tier
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_merchants_risk CHECK (risk_tier IN ('LOW', 'MEDIUM', 'HIGH', 'BLACKLISTED'))
);

CREATE INDEX idx_merchants_mcc ON merchants(category_code);
CREATE INDEX idx_merchants_country ON merchants(country_code);

-- ==============================================================================
-- 5. TRANSACTIONS
-- Immutable ledger of financial movements with fraud/risk metadata.
-- ==============================================================================
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL,
    merchant_id UUID, -- Nullable for P2P or internal transfers
    device_id UUID,   -- Nullable if transaction originated externally (e.g., ACH in)
    
    amount NUMERIC(19, 4) NOT NULL,
    currency CHAR(3) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    
    -- Geographic & Network Data
    ip_address INET,
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),
    
    -- Fraud Tracking
    risk_score NUMERIC(5, 2) DEFAULT 0.00, -- Range: 0.00 to 100.00
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_transactions_account FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE RESTRICT,
    CONSTRAINT fk_transactions_merchant FOREIGN KEY (merchant_id) REFERENCES merchants(id) ON DELETE RESTRICT,
    CONSTRAINT fk_transactions_device FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL,
    
    CONSTRAINT chk_transactions_amount CHECK (amount > 0),
    CONSTRAINT chk_transactions_type CHECK (transaction_type IN ('DEPOSIT', 'WITHDRAWAL', 'TRANSFER', 'PURCHASE', 'REFUND')),
    CONSTRAINT chk_transactions_status CHECK (status IN ('PENDING', 'COMPLETED', 'FAILED', 'REJECTED', 'REVERSED')),
    CONSTRAINT chk_transactions_risk_score CHECK (risk_score >= 0 AND risk_score <= 100)
);

-- Crucial indexes for querying transaction history and running fraud models
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_merchant_id ON transactions(merchant_id);
CREATE INDEX idx_transactions_device_id ON transactions(device_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_risk_score ON transactions(risk_score) WHERE risk_score > 70.00; -- Partial index for high risk

-- ==============================================================================
-- 6. FRAUD_ALERTS
-- Workflow table for fraud investigation team based on high risk scores.
-- ==============================================================================
CREATE TABLE fraud_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'NEW',
    investigator_notes TEXT,
    resolved_by VARCHAR(100), -- Username/ID of the investigator
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_fraud_alerts_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    CONSTRAINT uq_fraud_alerts_transaction UNIQUE (transaction_id), -- One alert per transaction typically
    CONSTRAINT chk_fraud_alerts_type CHECK (alert_type IN ('HIGH_RISK_SCORE', 'UNUSUAL_LOCATION', 'VELOCITY_LIMIT', 'KNOWN_FRAUD_MERCHANT', 'DEVICE_ANOMALY')),
    CONSTRAINT chk_fraud_alerts_status CHECK (status IN ('NEW', 'UNDER_REVIEW', 'CONFIRMED_FRAUD', 'FALSE_POSITIVE'))
);

CREATE INDEX idx_fraud_alerts_status ON fraud_alerts(status);
CREATE INDEX idx_fraud_alerts_created_at ON fraud_alerts(created_at);

-- ==============================================================================
-- 7. AUDIT_LOGS
-- Immutable table capturing PII and critical state changes for compliance.
-- ==============================================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(50) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(10) NOT NULL,
    old_data JSONB, -- Stores previous state
    new_data JSONB, -- Stores new state
    changed_by VARCHAR(100) NOT NULL, -- User, Service, or System making the change
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_audit_logs_action CHECK (action IN ('INSERT', 'UPDATE', 'DELETE'))
);

-- Index for searching history of a specific record
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- ==============================================================================
-- 8. TRIGGER FUNCTIONS
-- Automatically manage updated_at timestamps
-- ==============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_customers_modtime BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_accounts_modtime BEFORE UPDATE ON accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_merchants_modtime BEFORE UPDATE ON merchants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_transactions_modtime BEFORE UPDATE ON transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_fraud_alerts_modtime BEFORE UPDATE ON fraud_alerts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
