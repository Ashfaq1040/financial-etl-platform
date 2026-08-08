import os
import psycopg2

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

app = FastAPI(
    title="Financial ETL API",
    description="REST API for the Financial ETL Pipeline",
    version="1.0.0"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv(
            "DB_NAME",
            "financial_etl"
        ),
        user=os.getenv(
            "DB_USER",
            "postgres"
        ),
        password=os.getenv(
            "DB_PASSWORD"
        )
    )


# ============================================================
# HELPER - BUILD FILTERS
# ============================================================

def build_filters(
    country=None,
    status=None,
    transaction_type=None,
    amount_category=None,
    validation_status=None,
    start_date=None,
    end_date=None
):

    conditions = []
    parameters = []

    # Country
    if country:
        conditions.append(
            "country = %s"
        )
        parameters.append(
            country.upper()
        )

    # Status
    if status:
        conditions.append(
            "status = %s"
        )
        parameters.append(
            status.upper()
        )

    # Transaction type
    if transaction_type:
        conditions.append(
            "transaction_type = %s"
        )
        parameters.append(
            transaction_type.upper()
        )

    # Amount category
    if amount_category:
        conditions.append(
            "amount_category = %s"
        )
        parameters.append(
            amount_category.upper()
        )

    # Validation status
    if validation_status:
        conditions.append(
            "validation_status = %s"
        )
        parameters.append(
            validation_status.upper()
        )

    # Start date
    if start_date:
        conditions.append(
            "transaction_date >= %s"
        )
        parameters.append(
            start_date
        )

    # End date
    if end_date:
        conditions.append(
            "transaction_date < (%s::date + INTERVAL '1 day')"
        )
        parameters.append(
            end_date
        )

    if conditions:

        where_clause = (
            "WHERE "
            + " AND ".join(conditions)
        )

    else:

        where_clause = ""

    return where_clause, parameters


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "application": "Financial ETL API",
        "status": "running",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    connection = None

    try:

        connection = get_connection()

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Database connection failed: "
                f"{error}"
            )
        )

    finally:

        if connection is not None:
            connection.close()


# ============================================================
# TRANSACTIONS
# ============================================================

@app.get("/transactions")
def get_transactions(

    limit: int = 10,

    offset: int = 0,

    country: str | None = None,

    status: str | None = None,

    transaction_type: str | None = None,

    amount_category: str | None = None,

    validation_status: str | None = None,

    start_date: str | None = None,

    end_date: str | None = None

):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        where_clause, parameters = build_filters(

            country,

            status,

            transaction_type,

            amount_category,

            validation_status,

            start_date,

            end_date

        )

        query = f"""

            SELECT

                transaction_id,

                customer_id,

                transaction_date,

                amount,

                currency,

                transaction_type,

                merchant,

                country,

                status,

                amount_category,

                validation_status

            FROM financial_transactions_large

            {where_clause}

            ORDER BY transaction_date DESC

            LIMIT %s

            OFFSET %s;

        """

        parameters.extend([
            limit,
            offset
        ])

        cursor.execute(
            query,
            tuple(parameters)
        )

        rows = cursor.fetchall()

        columns = [

            "transaction_id",

            "customer_id",

            "transaction_date",

            "amount",

            "currency",

            "transaction_type",

            "merchant",

            "country",

            "status",

            "amount_category",

            "validation_status"

        ]

        transactions = [

            dict(
                zip(
                    columns,
                    row
                )
            )

            for row in rows

        ]

        return {

            "count":
                len(transactions),

            "limit":
                limit,

            "offset":
                offset,

            "filters": {

                "country":
                    country,

                "status":
                    status,

                "transaction_type":
                    transaction_type,

                "amount_category":
                    amount_category,

                "validation_status":
                    validation_status,

                "start_date":
                    start_date,

                "end_date":
                    end_date

            },

            "transactions":
                transactions

        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# SINGLE TRANSACTION
# ============================================================

@app.get(
    "/transactions/{transaction_id}"
)
def get_transaction(
    transaction_id: str
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        query = """

            SELECT

                transaction_id,

                customer_id,

                transaction_date,

                amount,

                currency,

                transaction_type,

                merchant,

                country,

                status,

                amount_category,

                validation_status,

                validation_reason,

                processed_at

            FROM financial_transactions_large

            WHERE transaction_id = %s;

        """

        cursor.execute(
            query,
            (transaction_id,)
        )

        row = cursor.fetchone()

        if row is None:

            raise HTTPException(
                status_code=404,
                detail="Transaction not found"
            )

        columns = [

            "transaction_id",

            "customer_id",

            "transaction_date",

            "amount",

            "currency",

            "transaction_type",

            "merchant",

            "country",

            "status",

            "amount_category",

            "validation_status",

            "validation_reason",

            "processed_at"

        ]

        return dict(
            zip(
                columns,
                row
            )
        )

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# CUSTOMER TRANSACTIONS
# ============================================================

@app.get(
    "/customers/{customer_id}/transactions"
)
def get_customer_transactions(
    customer_id: str
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        query = """

            SELECT

                transaction_id,

                customer_id,

                transaction_date,

                amount,

                currency,

                transaction_type,

                merchant,

                country,

                status,

                amount_category,

                validation_status

            FROM financial_transactions_large

            WHERE customer_id = %s

            ORDER BY transaction_date DESC;

        """

        cursor.execute(
            query,
            (customer_id,)
        )

        rows = cursor.fetchall()

        columns = [

            "transaction_id",

            "customer_id",

            "transaction_date",

            "amount",

            "currency",

            "transaction_type",

            "merchant",

            "country",

            "status",

            "amount_category",

            "validation_status"

        ]

        transactions = [

            dict(
                zip(
                    columns,
                    row
                )
            )

            for row in rows

        ]

        return {

            "customer_id":
                customer_id,

            "count":
                len(transactions),

            "transactions":
                transactions

        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# FILTERED ANALYTICS
# ============================================================

@app.get("/analytics/filtered")
def get_filtered_analytics(

    country: str | None = None,

    status: str | None = None,

    transaction_type: str | None = None,

    amount_category: str | None = None,

    validation_status: str | None = None,

    start_date: str | None = None,

    end_date: str | None = None

):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        where_clause, parameters = build_filters(

            country,

            status,

            transaction_type,

            amount_category,

            validation_status,

            start_date,

            end_date

        )

        query = f"""

            SELECT

                COUNT(*) AS total_transactions,

                COUNT(
                    DISTINCT customer_id
                ) AS total_customers,

                COALESCE(
                    SUM(amount),
                    0
                ) AS total_amount,

                COUNT(*) FILTER (
                    WHERE status = 'SUCCESS'
                ) AS successful_transactions,

                COUNT(*) FILTER (
                    WHERE status = 'FAILED'
                ) AS failed_transactions,

                COUNT(*) FILTER (
                    WHERE status = 'PENDING'
                ) AS pending_transactions,

                COUNT(*) FILTER (
                    WHERE validation_status = 'FLAGGED'
                ) AS flagged_transactions

            FROM financial_transactions_large

            {where_clause};

        """

        cursor.execute(
            query,
            tuple(parameters)
        )

        row = cursor.fetchone()

        total_transactions = int(row[0])
        successful = int(row[3])

        success_rate = (

            successful
            / total_transactions
            * 100

            if total_transactions

            else 0

        )

        return {

            "total_transactions":
                total_transactions,

            "total_customers":
                int(row[1]),

            "total_amount":
                float(row[2]),

            "successful_transactions":
                successful,

            "failed_transactions":
                int(row[4]),

            "pending_transactions":
                int(row[5]),

            "flagged_transactions":
                int(row[6]),

            "success_rate":
                round(
                    success_rate,
                    2
                ),

            "filters": {

                "country":
                    country,

                "status":
                    status,

                "transaction_type":
                    transaction_type,

                "amount_category":
                    amount_category,

                "validation_status":
                    validation_status,

                "start_date":
                    start_date,

                "end_date":
                    end_date

            }

        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# STATUS DISTRIBUTION
# ============================================================

@app.get("/analytics/status")
def get_status_distribution(

    country: str | None = None,

    status: str | None = None,

    transaction_type: str | None = None,

    amount_category: str | None = None,

    validation_status: str | None = None,

    start_date: str | None = None,

    end_date: str | None = None

):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        where_clause, parameters = build_filters(

            country,

            status,

            transaction_type,

            amount_category,

            validation_status,

            start_date,

            end_date

        )

        query = f"""

            SELECT

                status,

                COUNT(*) AS transaction_count

            FROM financial_transactions_large

            {where_clause}

            GROUP BY status

            ORDER BY transaction_count DESC;

        """

        cursor.execute(
            query,
            tuple(parameters)
        )

        rows = cursor.fetchall()

        return [

            {

                "status":
                    row[0],

                "transaction_count":
                    row[1]

            }

            for row in rows

        ]

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# COUNTRY DISTRIBUTION
# ============================================================

@app.get("/analytics/countries")
def get_country_distribution(

    country: str | None = None,

    status: str | None = None,

    transaction_type: str | None = None,

    amount_category: str | None = None,

    validation_status: str | None = None,

    start_date: str | None = None,

    end_date: str | None = None

):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        where_clause, parameters = build_filters(

            country,

            status,

            transaction_type,

            amount_category,

            validation_status,

            start_date,

            end_date

        )

        query = f"""

            SELECT

                country,

                COUNT(*) AS transaction_count,

                COALESCE(
                    SUM(amount),
                    0
                ) AS total_amount

            FROM financial_transactions_large

            {where_clause}

            GROUP BY country

            ORDER BY transaction_count DESC;

        """

        cursor.execute(
            query,
            tuple(parameters)
        )

        rows = cursor.fetchall()

        return [

            {

                "country":
                    row[0],

                "transaction_count":
                    row[1],

                "total_amount":
                    float(row[2])

            }

            for row in rows

        ]

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# MERCHANT DISTRIBUTION
# ============================================================

@app.get("/analytics/merchants")
def get_merchant_distribution(

    country: str | None = None,

    status: str | None = None,

    transaction_type: str | None = None,

    amount_category: str | None = None,

    validation_status: str | None = None,

    start_date: str | None = None,

    end_date: str | None = None

):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        where_clause, parameters = build_filters(

            country,

            status,

            transaction_type,

            amount_category,

            validation_status,

            start_date,

            end_date

        )

        query = f"""

            SELECT

                merchant,

                COUNT(*) AS transaction_count,

                COALESCE(
                    SUM(amount),
                    0
                ) AS total_amount

            FROM financial_transactions_large

            {where_clause}

            GROUP BY merchant

            ORDER BY transaction_count DESC

            LIMIT 20;

        """

        cursor.execute(
            query,
            tuple(parameters)
        )

        rows = cursor.fetchall()

        return [

            {

                "merchant":
                    row[0],

                "transaction_count":
                    row[1],

                "total_amount":
                    float(row[2])

            }

            for row in rows

        ]

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# GLOBAL SUMMARY
# ============================================================

@app.get("/analytics/summary")
def get_summary():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        query = """

            SELECT

                COUNT(*),

                COUNT(
                    DISTINCT customer_id
                ),

                COALESCE(
                    SUM(amount),
                    0
                ),

                COUNT(*) FILTER (
                    WHERE status = 'SUCCESS'
                ),

                COUNT(*) FILTER (
                    WHERE status = 'FAILED'
                ),

                COUNT(*) FILTER (
                    WHERE status = 'PENDING'
                ),

                COUNT(*) FILTER (
                    WHERE validation_status =
                        'FLAGGED'
                )

            FROM financial_transactions_large;

        """

        cursor.execute(query)

        row = cursor.fetchone()

        total = int(row[0])
        successful = int(row[3])

        success_rate = (

            successful
            / total
            * 100

            if total

            else 0

        )

        return {

            "total_transactions":
                total,

            "total_customers":
                int(row[1]),

            "total_amount":
                float(row[2]),

            "successful_transactions":
                successful,

            "failed_transactions":
                int(row[4]),

            "pending_transactions":
                int(row[5]),

            "flagged_transactions":
                int(row[6]),

            "success_rate":
                round(
                    success_rate,
                    2
                )

        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# ETL AUDIT HISTORY
# ============================================================

@app.get("/audit")
def get_audit_history():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        query = """

            SELECT

                run_id,

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

            FROM etl_audit

            ORDER BY run_id DESC

            LIMIT 20;

        """

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [

            "run_id",

            "pipeline_name",

            "start_time",

            "end_time",

            "records_extracted",

            "records_transformed",

            "records_rejected",

            "records_loaded",

            "status",

            "error_message",

            "duration_seconds"

        ]

        return [

            dict(
                zip(
                    columns,
                    row
                )
            )

            for row in rows

        ]

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()