import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "transactions_large.csv"

NUM_RECORDS = 100_000


def generate_transactions():

    print("Generating financial transactions...")

    random.seed(42)

    currencies = ["INR", "USD", "EUR", "GBP"]

    transaction_types = [
        "DEBIT",
        "CREDIT",
        "TRANSFER"
    ]

    merchants = [
        "Amazon",
        "Flipkart",
        "Swiggy",
        "Zomato",
        "HDFC Bank",
        "ICICI Bank",
        "Uber",
        "Netflix"
    ]

    countries = [
        "India",
        "USA",
        "UK",
        "Germany"
    ]

    statuses = [
        "SUCCESS",
        "SUCCESS",
        "SUCCESS",
        "FAILED",
        "PENDING"
    ]

    start_date = datetime(2025, 1, 1)

    transactions = []

    for i in range(1, NUM_RECORDS + 1):

        transaction_id = f"TXN{i:06d}"

        # 5,000 possible customers means customers will
        # naturally have multiple transactions.
        customer_id = f"CUST{random.randint(1, 5000):05d}"

        transaction_date = start_date + timedelta(
            minutes=random.randint(0, 525600)
        )

        amount = round(
            random.uniform(50, 250000),
            2
        )

        transaction = {
            "transaction_id": transaction_id,
            "customer_id": customer_id,
            "transaction_date": transaction_date,
            "amount": amount,
            "currency": random.choice(currencies),
            "transaction_type": random.choice(transaction_types),
            "merchant": random.choice(merchants),
            "country": random.choice(countries),
            "status": random.choice(statuses)
        }

        transactions.append(transaction)

    df = pd.DataFrame(transactions)

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("Generation completed.")
    print(f"Records generated: {len(df):,}")
    print(f"Customers: {df['customer_id'].nunique():,}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_transactions()