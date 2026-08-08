CREATE TABLE IF NOT EXISTS financial_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    currency VARCHAR(10) NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    merchant VARCHAR(150),
    country VARCHAR(100),
    status VARCHAR(30),

    transaction_year INTEGER,
    transaction_month INTEGER,
    transaction_day INTEGER,
    transaction_hour INTEGER,

    amount_category VARCHAR(20),

    validation_status VARCHAR(20),
    validation_reason VARCHAR(255),

    processed_at TIMESTAMP NOT NULL
);