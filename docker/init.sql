CREATE TABLE IF NOT EXISTS financial_transactions_large (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    amount NUMERIC(15,2) NOT NULL,
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

CREATE INDEX IF NOT EXISTS financial_transactions_large_customer_id_idx
ON financial_transactions_large(customer_id);


CREATE TABLE IF NOT EXISTS etl_audit (
    run_id SERIAL PRIMARY KEY,
    pipeline_name VARCHAR(100) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    records_extracted INTEGER,
    records_transformed INTEGER,
    records_rejected INTEGER,
    records_loaded INTEGER,
    status VARCHAR(20),
    error_message TEXT,
    duration_seconds NUMERIC(10,2)
);