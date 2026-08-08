import streamlit as st
import requests
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://api:8000"

st.set_page_config(
    page_title="Financial ETL Platform",
    page_icon="💰",
    layout="wide"
)


# ============================================================
# API HELPER
# ============================================================

def get_api_data(endpoint):

    try:

        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as error:

        st.error(f"API error: {error}")

        return None


# ============================================================
# HEADER
# ============================================================

st.title("💰 Financial ETL Platform")

st.caption(
    "Financial transaction analytics and ETL monitoring"
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:

    st.header("🔎 Transaction Filters")

    country = st.selectbox(
        "Country",
        [
            "ALL",
            "GERMANY",
            "INDIA",
            "UK",
            "USA"
        ]
    )

    status = st.selectbox(
        "Status",
        [
            "ALL",
            "FAILED",
            "PENDING",
            "SUCCESS"
        ]
    )

    transaction_type = st.selectbox(
        "Transaction Type",
        [
            "ALL",
            "CREDIT",
            "DEBIT",
            "TRANSFER"
        ]
    )

    amount_category = st.selectbox(
        "Amount Category",
        [
            "ALL",
            "HIGH",
            "LOW",
            "MEDIUM",
            "VERY_HIGH"
        ]
    )

    validation_status = st.selectbox(
        "Validation Status",
        [
            "ALL",
            "FLAGGED",
            "VALID"
        ]
    )

    st.divider()

    limit = st.slider(
        "Transactions per page",
        min_value=10,
        max_value=100,
        value=20,
        step=10
    )

    if st.button("🔄 Refresh"):

        st.rerun()


# ============================================================
# BUILD FILTER PARAMETERS
# ============================================================

filter_params = []


if country != "ALL":

    filter_params.append(
        f"country={country}"
    )


if status != "ALL":

    filter_params.append(
        f"status={status}"
    )


if transaction_type != "ALL":

    filter_params.append(
        f"transaction_type={transaction_type}"
    )


if amount_category != "ALL":

    filter_params.append(
        f"amount_category={amount_category}"
    )


if validation_status != "ALL":

    filter_params.append(
        f"validation_status={validation_status}"
    )


# ============================================================
# TRANSACTION API QUERY
# ============================================================

transaction_params = [
    f"limit={limit}",
    "offset=0"
]

transaction_params.extend(
    filter_params
)


transaction_endpoint = (
    "/transactions?"
    + "&".join(transaction_params)
)


# ============================================================
# ANALYTICS FILTER QUERY
# ============================================================

if filter_params:

    filtered_analytics_endpoint = (
        "/analytics/filtered?"
        + "&".join(filter_params)
    )

else:

    filtered_analytics_endpoint = (
        "/analytics/summary"
    )


# ============================================================
# HEALTH CHECK
# ============================================================

health = get_api_data(
    "/health"
)


if health and health.get("status") == "healthy":

    st.success(
        "🟢 API and PostgreSQL connected"
    )

else:

    st.error(
        "🔴 Backend unavailable"
    )


# ============================================================
# FILTER STATUS
# ============================================================

if filter_params:

    st.info(
        "🔎 Dashboard is showing filtered analytics."
    )

else:

    st.info(
        "📊 Dashboard is showing all transactions."
    )


# ============================================================
# FILTERED SUMMARY / KPI
# ============================================================

summary = get_api_data(
    filtered_analytics_endpoint
)


if summary:

    total_transactions = int(
        summary.get(
            "total_transactions",
            0
        )
    )

    total_customers = int(
        summary.get(
            "total_customers",
            0
        )
    )

    total_amount = float(
        summary.get(
            "total_amount",
            0
        )
    )

    successful = int(
        summary.get(
            "successful_transactions",
            0
        )
    )

    failed = int(
        summary.get(
            "failed_transactions",
            0
        )
    )

    pending = int(
        summary.get(
            "pending_transactions",
            0
        )
    )

    flagged = int(
        summary.get(
            "flagged_transactions",
            0
        )
    )

    success_rate = float(
        summary.get(
            "success_rate",
            (
                successful / total_transactions * 100
                if total_transactions
                else 0
            )
        )
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    st.subheader(
        "📊 Key Performance Indicators"
    )

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "💳 Transactions",
            f"{total_transactions:,}"
        )


    with col2:

        st.metric(
            "👥 Customers",
            f"{total_customers:,}"
        )


    with col3:

        st.metric(
            "💰 Transaction Value",
            f"${total_amount:,.2f}"
        )


    with col4:

        st.metric(
            "🚩 Flagged",
            f"{flagged:,}"
        )


    # ========================================================
    # TRANSACTION HEALTH
    # ========================================================

    st.subheader(
        "Transaction Health"
    )

    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "✅ Successful",
            f"{successful:,}"
        )


    with c2:

        st.metric(
            "❌ Failed",
            f"{failed:,}"
        )


    with c3:

        st.metric(
            "⏳ Pending",
            f"{pending:,}"
        )


    with c4:

        st.metric(
            "📈 Success Rate",
            f"{success_rate:.2f}%"
        )


# ============================================================
# ANALYTICS CHARTS
# ============================================================

st.divider()

st.subheader(
    "📈 Transaction Analytics"
)


left, right = st.columns(2)


# ============================================================
# STATUS CHART
# ============================================================

with left:

    st.subheader(
        "📊 Transaction Status"
    )

    status_endpoint = (
        "/analytics/status"
    )

    if filter_params:

        status_endpoint = (
            "/analytics/status?"
            + "&".join(filter_params)
        )


    status_data = get_api_data(
        status_endpoint
    )


    if status_data:

        status_df = pd.DataFrame(
            status_data
        )


        if not status_df.empty:

            st.bar_chart(
                status_df.set_index(
                    "status"
                )["transaction_count"]
            )

        else:

            st.info(
                "No status data for selected filters."
            )


# ============================================================
# COUNTRY CHART
# ============================================================

with right:

    st.subheader(
        "🌍 Transactions by Country"
    )

    country_endpoint = (
        "/analytics/countries"
    )


    if filter_params:

        country_endpoint = (
            "/analytics/countries?"
            + "&".join(filter_params)
        )


    country_data = get_api_data(
        country_endpoint
    )


    if country_data:

        country_df = pd.DataFrame(
            country_data
        )


        if not country_df.empty:

            st.bar_chart(
                country_df.set_index(
                    "country"
                )["transaction_count"]
            )

        else:

            st.info(
                "No country data for selected filters."
            )


# ============================================================
# MERCHANT ANALYTICS
# ============================================================

st.divider()

st.subheader(
    "🏪 Top Merchants"
)


merchant_endpoint = (
    "/analytics/merchants"
)


if filter_params:

    merchant_endpoint = (
        "/analytics/merchants?"
        + "&".join(filter_params)
    )


merchant_data = get_api_data(
    merchant_endpoint
)


if merchant_data:

    merchant_df = pd.DataFrame(
        merchant_data
    )


    if not merchant_df.empty:

        st.bar_chart(
            merchant_df.set_index(
                "merchant"
            )["transaction_count"]
        )

    else:

        st.info(
            "No merchant data for selected filters."
        )


# ============================================================
# FILTERED TRANSACTIONS
# ============================================================

st.divider()

st.subheader(
    "💳 Filtered Transactions"
)


transaction_data = get_api_data(
    transaction_endpoint
)


if transaction_data:

    transactions = transaction_data.get(
        "transactions",
        []
    )


    transaction_df = pd.DataFrame(
        transactions
    )


    st.caption(
        f"Showing {len(transaction_df)} transactions"
    )


    if not transaction_df.empty:

        st.dataframe(
            transaction_df,
            use_container_width="stretch",
            hide_index=True
        )

    else:

        st.warning(
            "No transactions match the selected filters."
        )


# ============================================================
# TRANSACTION SEARCH
# ============================================================

st.divider()

st.subheader(
    "🔎 Search Transaction"
)


transaction_id = st.text_input(
    "Transaction ID",
    placeholder="Example: TXN061878"
)


if transaction_id:

    transaction = get_api_data(
        f"/transactions/{transaction_id}"
    )


    if transaction:

        st.success(
            f"Transaction {transaction_id} found"
        )


        transaction_df = pd.DataFrame(
            [transaction]
        )


        st.dataframe(
            transaction_df,
            use_container_width="stretch",
            hide_index=True
        )


# ============================================================
# ETL MONITORING
# ============================================================

st.divider()

st.subheader(
    "⚙️ ETL Pipeline Monitoring"
)


audit_data = get_api_data(
    "/audit"
)


if audit_data:

    audit_df = pd.DataFrame(
        audit_data
    )


    if not audit_df.empty:

        latest = audit_df.iloc[0]


        a1, a2, a3, a4 = st.columns(4)


        with a1:

            st.metric(
                "Pipeline",
                latest["status"]
            )


        with a2:

            st.metric(
                "Loaded",
                f"{int(latest['records_loaded']):,}"
            )


        with a3:

            st.metric(
                "Rejected",
                f"{int(latest['records_rejected']):,}"
            )


        with a4:

            duration = latest[
                "duration_seconds"
            ]


            st.metric(
                "Duration",
                f"{float(duration):.2f}s"
                if duration is not None
                else "N/A"
            )


        st.subheader(
            "Pipeline History"
        )


        columns = [
            "run_id",
            "pipeline_name",
            "records_extracted",
            "records_transformed",
            "records_rejected",
            "records_loaded",
            "duration_seconds",
            "status"
        ]


        available_columns = [
            column
            for column in columns
            if column in audit_df.columns
        ]


        st.dataframe(
            audit_df[
                available_columns
            ],
            use_container_width="stretch",
            hide_index=True
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Financial ETL Platform • "
    "Python • PostgreSQL • FastAPI • Streamlit • Docker"
)