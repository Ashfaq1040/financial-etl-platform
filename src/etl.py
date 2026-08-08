import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import time

from pathlib import Path
from dotenv import load_dotenv
from logger import logger


# Get project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


# Location of raw transaction data

# Small dataset used for initial testing
SMALL_DATA_FILE = BASE_DIR / "data" / "transactions.csv"

# Large dataset used for performance testing
LARGE_DATA_FILE = BASE_DIR / "data" / "transactions_large.csv"

# Select which dataset ETL should process
DATA_FILE = LARGE_DATA_FILE


def extract_data():
    """Extract transaction data from CSV."""

    logger.info("Starting data extraction...")

    df = pd.read_csv(DATA_FILE)

    logger.info("Data extraction completed.")
    logger.info(f"Total records extracted: {len(df)}")

    return df


def profile_data(df):
    """Profile the transaction dataset."""

    print("\n========== DATA PROFILE ==========")

    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Transactions:")
    print(df.duplicated().sum())

    print("\nTransaction Status:")
    print(df["status"].value_counts())

    print("\nTransaction Types:")
    print(df["transaction_type"].value_counts())

    print("==================================")


def validate_data(df):
    """Validate financial transaction records."""

    print("\n========== DATA VALIDATION ==========")

    df = df.copy()

    # Default classification
    df["validation_status"] = "VALID"
    df["validation_reason"] = ""

    # Missing customer ID
    missing_customer = df["customer_id"].isnull()

    df.loc[missing_customer, "validation_status"] = "REJECTED"
    df.loc[missing_customer, "validation_reason"] = "Missing customer ID"

    # Missing amount
    missing_amount = df["amount"].isnull()

    df.loc[missing_amount, "validation_status"] = "REJECTED"
    df.loc[missing_amount, "validation_reason"] = "Missing transaction amount"

    # Negative or zero amount
    invalid_amount = df["amount"].notna() & (df["amount"] <= 0)

    df.loc[invalid_amount, "validation_status"] = "REJECTED"
    df.loc[invalid_amount, "validation_reason"] = "Invalid transaction amount"

    # Convert transaction date to datetime
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    invalid_date = df["transaction_date"].isnull()

    df.loc[invalid_date, "validation_status"] = "REJECTED"
    df.loc[invalid_date, "validation_reason"] = "Invalid transaction date"

    # Identify duplicate transaction IDs
    duplicate_ids = df.duplicated(
        subset=["transaction_id"],
        keep="first"
    )

    df.loc[duplicate_ids, "validation_status"] = "REJECTED"
    df.loc[duplicate_ids, "validation_reason"] = "Duplicate transaction"

    # Flag unusually large transactions
    high_value = (
        (df["amount"] > 100000)
        & (df["validation_status"] == "VALID")
    )

    df.loc[high_value, "validation_status"] = "FLAGGED"
    df.loc[high_value, "validation_reason"] = "High-value transaction"

    print(df["validation_status"].value_counts())

    print("\nRejected/Flagged Records:")

    print(
        df.loc[
            df["validation_status"] != "VALID",
            [
                "transaction_id",
                "customer_id",
                "amount",
                "validation_status",
                "validation_reason",
            ],
        ].to_string(index=False)
    )

    print("=====================================")

    return df


def transform_data(df):
    """Transform validated transactions for downstream analytics."""

    print("\n========== DATA TRANSFORMATION ==========")

    # Keep valid and flagged transactions
    clean_df = df[
        df["validation_status"].isin(["VALID", "FLAGGED"])
    ].copy()

    # Standardize text columns
    text_columns = [
        "currency",
        "transaction_type",
        "country",
        "status"
    ]

    for column in text_columns:
        clean_df[column] = (
            clean_df[column]
            .str.strip()
            .str.upper()
        )

    # Standardize merchant names
    clean_df["merchant"] = clean_df["merchant"].str.strip()

    # Create useful date dimensions
    clean_df["transaction_year"] = clean_df["transaction_date"].dt.year
    clean_df["transaction_month"] = clean_df["transaction_date"].dt.month
    clean_df["transaction_day"] = clean_df["transaction_date"].dt.day
    clean_df["transaction_hour"] = clean_df["transaction_date"].dt.hour

    # Categorize transaction amount
    clean_df["amount_category"] = pd.cut(
        clean_df["amount"],
        bins=[0, 1000, 10000, 100000, float("inf")],
        labels=["LOW", "MEDIUM", "HIGH", "VERY_HIGH"]
    )

    # Timestamp showing when our ETL pipeline processed the record
    clean_df["processed_at"] = pd.Timestamp.now()

    print(f"Records received: {len(df)}")
    print(f"Records transformed: {len(clean_df)}")

    print("\nAmount Categories:")
    print(clean_df["amount_category"].value_counts())

    print("\nTransformed Data Preview:")

    print(
        clean_df[
            [
                "transaction_id",
                "customer_id",
                "transaction_date",
                "amount",
                "currency",
                "transaction_type",
                "amount_category",
                "validation_status"
            ]
        ].head(10).to_string(index=False)
    )

    print("=========================================")

    return clean_df


def save_output(validated_df, transformed_df):
    """Save processed and rejected transaction datasets."""

    print("\n========== SAVING OUTPUT ==========")

    processed_file = (
        BASE_DIR
        / "data"
        / "processed"
        / "transactions_processed.csv"
    )

    rejected_file = (
        BASE_DIR
        / "data"
        / "rejected"
        / "transactions_rejected.csv"
    )

    # Save valid + flagged transformed transactions
    transformed_df.to_csv(
        processed_file,
        index=False
    )

    # Separate rejected records
    rejected_df = validated_df[
        validated_df["validation_status"] == "REJECTED"
    ].copy()

    rejected_df.to_csv(
        rejected_file,
        index=False
    )

    print(f"Processed records saved: {len(transformed_df)}")
    print(f"Rejected records saved: {len(rejected_df)}")

    print(f"\nProcessed file: {processed_file}")
    print(f"Rejected file: {rejected_file}")

    print("===================================")


def test_database_connection():
    """Test connection to the PostgreSQL database."""

    print("\n========== DATABASE CONNECTION ==========")

    connection = None

    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        print("PostgreSQL connection successful.")

    except Exception as error:
        print(f"Database connection failed: {error}")

    finally:
        if connection is not None:
            connection.close()
            print("Database connection closed.")

    print("=========================================")


def load_data_batch(df):
    """Load transformed transactions using batch inserts."""

    print("\n========== BATCH LOADING TO POSTGRESQL ==========")

    connection = None
    cursor = None

    start_time = time.perf_counter()

    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cursor = connection.cursor()

        insert_query = """
            INSERT INTO financial_transactions_large (
                transaction_id,
                customer_id,
                transaction_date,
                amount,
                currency,
                transaction_type,
                merchant,
                country,
                status,
                transaction_year,
                transaction_month,
                transaction_day,
                transaction_hour,
                amount_category,
                validation_status,
                validation_reason,
                processed_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (transaction_id)
            DO NOTHING;
        """

        records = []

        for _, row in df.iterrows():
            records.append(
                (
                    row["transaction_id"],
                    row["customer_id"],
                    row["transaction_date"],
                    float(row["amount"]),
                    row["currency"],
                    row["transaction_type"],
                    row["merchant"],
                    row["country"],
                    row["status"],
                    int(row["transaction_year"]),
                    int(row["transaction_month"]),
                    int(row["transaction_day"]),
                    int(row["transaction_hour"]),
                    str(row["amount_category"]),
                    row["validation_status"],
                    row["validation_reason"],
                    row["processed_at"]
                )
            )

        execute_batch(
            cursor,
            insert_query,
            records,
            page_size=1000
        )

        connection.commit()

        end_time = time.perf_counter()

        print(f"Records processed: {len(records):,}")
        print(f"Batch load time: {end_time - start_time:.2f} seconds")

    except Exception as error:
        if connection is not None:
            connection.rollback()

        print(f"Batch load failed: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()

    print("=================================================")


def create_audit_record(
    start_time,
    end_time,
    records_extracted,
    records_transformed,
    records_rejected,
    records_loaded,
    status,
    error_message=None,
    duration_seconds=None
):
    """Store ETL pipeline execution details in PostgreSQL."""

    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cursor = connection.cursor()

        insert_query = """
            INSERT INTO etl_audit (
                pipeline_name,
                start_time,
                end_time,
                records_extracted,
                records_transformed,
                records_rejected,
                records_loaded,
                status,
                error_message,
                duration_seconds
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            );
        """

        cursor.execute(
            insert_query,
            (
                "financial_etl",
                start_time,
                end_time,
                records_extracted,
                records_transformed,
                records_rejected,
                records_loaded,
                status,
                error_message,
                duration_seconds
            )
        )

        connection.commit()

        logger.info("ETL audit record created successfully.")

    except Exception as error:
        logger.error(
            f"Failed to create ETL audit record: {error}"
        )

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


if __name__ == "__main__":

    pipeline_start = pd.Timestamp.now()

    try:

        logger.info(
            "========== ETL PIPELINE STARTED =========="
        )

        # EXTRACT
        transactions = extract_data()

        records_extracted = int(len(transactions))

        print("\nFirst 5 transactions:")
        print(transactions.head())

        # PROFILE
        profile_data(transactions)

        # VALIDATE
        validated_transactions = validate_data(
            transactions
        )

        records_rejected = int(
            validated_transactions[
                "validation_status"
            ]
            .eq("REJECTED")
            .sum()
        )

        # TRANSFORM
        transformed_transactions = transform_data(
            validated_transactions
        )

        records_transformed = int(
            len(transformed_transactions)
        )

        # SAVE CSV OUTPUT
        save_output(
            validated_transactions,
            transformed_transactions
        )

        # LOAD TO POSTGRESQL
        load_data_batch(
            transformed_transactions
        )

        records_loaded = int(
            records_transformed
        )

        # Pipeline completion time
        pipeline_end = pd.Timestamp.now()

        # Calculate pipeline duration
        duration_seconds = (
            pipeline_end - pipeline_start
        ).total_seconds()

        # AUDIT
        create_audit_record(
            start_time=pipeline_start,
            end_time=pipeline_end,
            records_extracted=records_extracted,
            records_transformed=records_transformed,
            records_rejected=records_rejected,
            records_loaded=records_loaded,
            status="SUCCESS",
            duration_seconds=duration_seconds
        )

        logger.info(
            "========== ETL PIPELINE COMPLETED =========="
        )

    except Exception as error:

        pipeline_end = pd.Timestamp.now()

        duration_seconds = (
            pipeline_end - pipeline_start
        ).total_seconds()

        logger.error(
            f"ETL pipeline failed: {error}"
        )

        create_audit_record(
            start_time=pipeline_start,
            end_time=pipeline_end,
            records_extracted=int(
                locals().get(
                    "records_extracted",
                    0
                )
            ),
            records_transformed=int(
                locals().get(
                    "records_transformed",
                    0
                )
            ),
            records_rejected=int(
                locals().get(
                    "records_rejected",
                    0
                )
            ),
            records_loaded=int(
                locals().get(
                    "records_loaded",
                    0
                )
            ),
            status="FAILED",
            error_message=str(error),
            duration_seconds=duration_seconds
        )