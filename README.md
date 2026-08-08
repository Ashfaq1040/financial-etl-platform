# 💰 Financial ETL Platform

> A production-style financial data pipeline that turns raw transaction data into validated, queryable, and interactive analytics.

This project demonstrates an end-to-end data engineering workflow using **Python, PostgreSQL, FastAPI, Streamlit, and Docker**.

Raw financial transactions are extracted, transformed, validated, categorized, loaded into PostgreSQL, exposed through REST APIs, and visualized through an interactive dashboard.

---

## 🎯 What This Project Does

The platform is built around a simple data flow:

**Raw Data → ETL → Validation → PostgreSQL → REST API → Analytics Dashboard**

It supports:

- Transaction ingestion
- Data transformation and validation
- Amount categorization
- Rejected-record handling
- PostgreSQL persistence
- Transaction filtering
- Transaction search
- Customer-level transaction lookup
- Financial analytics
- ETL execution auditing
- REST API access
- Interactive dashboard visualization
- Docker-based local deployment

---

## 🧩 System Architecture

```text
                    RAW TRANSACTION DATA
                           │
                           ▼
                 ┌───────────────────┐
                 │   Python ETL      │
                 │                   │
                 │ Extract           │
                 │ Transform         │
                 │ Validate          │
                 │ Categorize        │
                 │ Load              │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │    PostgreSQL     │
                 │                   │
                 │ Transactions      │
                 │ ETL Audit         │
                 │ Validation Data   │
                 └─────────┬─────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
     ┌─────────────────┐       ┌─────────────────┐
     │    FastAPI      │       │   Streamlit     │
     │    REST API     │       │   Dashboard     │
     └────────┬────────┘       └────────┬────────┘
              │                         │
              └────────────┬────────────┘
                           ▼
                 FINANCIAL ANALYTICS

⚡ Key Capabilities

🔄 ETL Processing

The pipeline processes large transaction datasets through:

Extract
   ↓
Transform
   ↓
Validate
   ↓
Categorize
   ↓
Load

The pipeline also records execution statistics including:

Records extracted
Records transformed
Records rejected
Records loaded
Pipeline status
Processing duration

🔍 Intelligent Transaction Filtering

Transactions can be filtered using multiple dimensions:

Filter	Available Values
Country	Germany, India, UK, USA
Status	Success, Failed, Pending
Transaction Type	Credit, Debit, Transfer
Amount Category	Low, Medium, High, Very High
Validation	Valid, Flagged
Date	Start date / End date

Multiple filters can be combined in a single request.

Example:

INDIA
+
SUCCESS
+
DEBIT
+
VERY_HIGH
+
FLAGGED

📊 Interactive Dashboard

The Streamlit dashboard provides a visual overview of the financial dataset.

It includes:

Transaction KPIs
Customer counts
Transaction value
Success rate
Failed transactions
Pending transactions
Flagged transactions
Country distribution
Transaction-status analysis
Merchant analysis
Filtered transaction tables
Individual transaction search
ETL pipeline monitoring
Dashboard

🔎 Dynamic Filtering

The dashboard allows users to combine multiple transaction filters and immediately see the corresponding analytics and transaction records.

🚀 REST API

The backend is implemented using FastAPI.

Swagger/OpenAPI documentation is automatically available through:

http://localhost:8000/docs
API Documentation

🔌 API Endpoints
Health Check
GET /health

Verifies API and PostgreSQL connectivity.

Transactions
GET /transactions

Supports:

limit
offset
country
status
transaction_type
amount_category
validation_status

Example:

GET /transactions?country=INDIA&status=SUCCESS&transaction_type=DEBIT
Individual Transaction
GET /transactions/{transaction_id}

Example:

GET /transactions/TXN061878
Customer Transactions
GET /customers/{customer_id}/transactions

Example:

GET /customers/CUST00778/transactions
Filtered Analytics
GET /analytics/filtered

Supported filters:

country
status
transaction_type
amount_category
validation_status
start_date
end_date
Analytics
GET /analytics/summary
GET /analytics/status
GET /analytics/countries
GET /analytics/merchants
ETL Audit
GET /audit

Returns recent ETL execution history.

🗄️ Database

PostgreSQL stores the processed financial transactions and ETL audit information.

The primary transaction dataset contains fields such as:

transaction_id
customer_id
transaction_date
amount
currency
transaction_type
merchant
country
status
amount_category
validation_status
validation_reason
processed_at

The project also maintains ETL execution history through the etl_audit table.

🐳 Dockerized Architecture

The complete application can be launched using Docker Compose.

┌──────────────────────────────┐
│       Docker Compose         │
│                              │
│  ┌────────────────────────┐  │
│  │ PostgreSQL             │  │
│  │ :5433 → :5432          │  │
│  └───────────┬────────────┘  │
│              │               │
│  ┌───────────▼────────────┐  │
│  │ FastAPI                │  │
│  │ :8000                  │  │
│  └───────────┬────────────┘  │
│              │               │
│  ┌───────────▼────────────┐  │
│  │ Streamlit              │  │
│  │ :8501                  │  │
│  └────────────────────────┘  │
│                              │
└──────────────────────────────┘
🛠️ Technology Stack
Technology	Role
Python	ETL and application logic
Pandas	Data processing
PostgreSQL	Persistent data storage
psycopg2	PostgreSQL connectivity
FastAPI	REST API
Streamlit	Interactive dashboard
Docker	Containerization
Docker Compose	Service orchestration
Git	Version control
GitHub	Source code hosting

📁 Project Structure
financial-etl-platform/
│
├── api/
│   └── main.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── transactions.csv
│   └── transactions_large.csv
│
├── docker/
│   └── init.sql
│
├── screenshots/
│   ├── dashboard.png
│   ├── filters.png
│   └── api-docs.png
│
├── sql/
│   └── schema.sql
│
├── src/
│   ├── etl.py
│   ├── generate_data.py
│   └── logger.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md

▶️ Run Locally
1. Clone the repository
git clone https://github.com/Ashfaq1040/financial-etl-platform.git
2. Enter the project
cd financial-etl-platform
3. Create .env

Create a .env file in the project root:

DB_HOST=postgres
DB_PORT=5432
DB_NAME=financial_etl
DB_USER=postgres
DB_PASSWORD=postgres

Never commit real credentials or secrets to GitHub.

4. Start the platform
docker compose up --build

🌐 Local Services
Service	URL
Streamlit Dashboard	http://localhost:8501
FastAPI	http://localhost:8000
Swagger UI	http://localhost:8000/docs
PostgreSQL	localhost:5433

🧪 Example Workflow

A typical workflow looks like this:

1. Generate / load transaction data
              ↓
2. Run ETL pipeline
              ↓
3. Validate transactions
              ↓
4. Store processed data in PostgreSQL
              ↓
5. Start FastAPI
              ↓
6. Start Streamlit
              ↓
7. Apply dashboard filters
              ↓
8. Query analytics through API
              ↓
9. Monitor ETL execution history


🔐 Security Considerations

The project uses environment variables for database configuration.

The .gitignore excludes:

.env
venv/
logs/
data/processed/
data/rejected/
__pycache__/

Never commit:

Database passwords
API keys
Cloud credentials
Private tokens
Production secrets


📈 Project Highlights
100,000+ transaction records
Multi-dimensional transaction filtering
PostgreSQL-backed analytics
RESTful API architecture
Interactive Streamlit dashboard
Dockerized services
ETL validation and categorization
ETL audit logging
Swagger API documentation
Pagination and transaction search
Customer-level transaction queries


💡 Why I Built This

This project was designed to demonstrate how a real-world financial data workflow can be structured from ingestion to analytics.

Rather than building only a data-processing script, the platform combines:

Data Engineering
      +
Backend Development
      +
Database Engineering
      +
API Development
      +
Data Visualization
      +
Containerization

into one complete application.

👨‍💻 Author
Ashfaq Ashu

GitHub:
https://github.com/Ashfaq1040