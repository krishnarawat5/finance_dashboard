"""
sample_data.py — Load Sample Transactions for Testing

This script adds ~30 realistic transactions (income + expenses) so you can
immediately see the dashboard in action without entering data manually.

Usage:
    - Called from the Streamlit sidebar via a button
    - Can also be run directly: python sample_data.py
"""

from datetime import date, timedelta
import random
from database import add_transaction, clear_all_transactions, init_db

# ─── Sample Transactions ────────────────────────────────────────────────────
# Each tuple: (days_ago, type, category, amount, description)

SAMPLE_TRANSACTIONS = [
    # Income entries
    (30, "Income", "Salary", 50000, "Monthly salary - September"),
    (1, "Income", "Salary", 50000, "Monthly salary - October"),
    (20, "Income", "Freelance", 8000, "Website design project"),
    (10, "Income", "Freelance", 5000, "Logo design work"),
    (15, "Income", "Interest", 1200, "Savings account interest"),
    (5, "Income", "Refund", 2500, "Amazon order refund"),

    # Food & Groceries
    (28, "Expense", "Food", 450, "Dinner at restaurant"),
    (25, "Expense", "Groceries", 3200, "Weekly groceries"),
    (22, "Expense", "Food", 350, "Lunch with friends"),
    (18, "Expense", "Groceries", 2800, "Monthly grocery stock"),
    (12, "Expense", "Food", 600, "Pizza delivery"),
    (7, "Expense", "Food", 250, "Coffee shop"),
    (3, "Expense", "Groceries", 1500, "Fruits and vegetables"),

    # Bills & Rent
    (29, "Expense", "Rent", 15000, "Monthly house rent"),
    (27, "Expense", "Bills", 2500, "Electricity bill"),
    (26, "Expense", "Bills", 800, "Internet bill"),
    (24, "Expense", "Bills", 500, "Mobile recharge"),

    # Shopping
    (21, "Expense", "Shopping", 3500, "New headphones"),
    (14, "Expense", "Shopping", 2000, "Clothes shopping"),
    (6, "Expense", "Shopping", 1200, "Kitchen supplies"),

    # Travel
    (19, "Expense", "Travel", 4500, "Weekend trip to hills"),
    (8, "Expense", "Travel", 800, "Cab rides this week"),

    # Education
    (23, "Expense", "Education", 5000, "Online Python course"),
    (11, "Expense", "Education", 1500, "Programming book"),

    # Entertainment
    (17, "Expense", "Entertainment", 1200, "Movie tickets + popcorn"),
    (9, "Expense", "Entertainment", 500, "Netflix subscription"),
    (4, "Expense", "Entertainment", 800, "Concert tickets"),

    # Health
    (16, "Expense", "Health", 2000, "Doctor visit + medicines"),
    (2, "Expense", "Health", 1500, "Gym membership"),

    # Gifts & Investments
    (13, "Expense", "Gifts", 2000, "Birthday gift for friend"),
    (10, "Expense", "Investments", 10000, "Mutual fund SIP"),
]


def load_sample_data():
    """
    Clear existing data and load fresh sample transactions.

    Dates are calculated relative to today so the data always
    looks recent and relevant.
    """
    clear_all_transactions()

    today = date.today()
    for days_ago, txn_type, category, amount, description in SAMPLE_TRANSACTIONS:
        txn_date = today - timedelta(days=days_ago)
        # Add a small random variation to amounts for realism
        variation = random.uniform(0.95, 1.05)
        adjusted_amount = round(amount * variation, 2)
        add_transaction(txn_date, txn_type, category, adjusted_amount, description)

    print(f"[OK] Loaded {len(SAMPLE_TRANSACTIONS)} sample transactions!")


# Allow running this file directly
if __name__ == "__main__":
    init_db()
    load_sample_data()
