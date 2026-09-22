"""
database.py — SQLite Database Layer for Personal Finance Dashboard

This file handles ALL database operations:
- Creating tables (transactions + jars)
- Adding, updating, deleting transactions
- Querying data for charts and summaries
- Managing budget jars

The database file (finance.db) is auto-created in the same folder.
"""

import sqlite3
import os
import pandas as pd
from datetime import datetime

# Database file lives next to this script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance.db")

# ─── Expense categories available in the app ────────────────────────────────
EXPENSE_CATEGORIES = [
    "Food",
    "Shopping",
    "Travel",
    "Bills",
    "Education",
    "Entertainment",
    "Health",
    "Groceries",
    "Rent",
    "Gifts",
    "Investments",
    "Other",
]

INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Business",
    "Interest",
    "Gifts Received",
    "Refund",
    "Other",
]

# ─── Default Jar Configuration (6 Jars System) ─────────────────────────────
DEFAULT_JARS = [
    ("Necessities", 55, "#FF6B6B", "Rent, bills, groceries, essentials"),
    ("Education", 10, "#4ECDC4", "Books, courses, self-improvement"),
    ("Savings", 10, "#45B7D1", "Emergency fund, long-term savings"),
    ("Entertainment", 10, "#96CEB4", "Fun, movies, dining out, hobbies"),
    ("Giving", 5, "#FFEAA7", "Gifts, charity, donations"),
    ("Financial Freedom", 10, "#DDA0DD", "Investments, side business"),
]

# ─── Mapping: which expense categories belong to which jar ──────────────────
# This connects your spending categories to the jar system
JAR_CATEGORY_MAP = {
    "Necessities": ["Bills", "Rent", "Groceries", "Health"],
    "Education": ["Education"],
    "Savings": [],  # Savings jar doesn't have direct expense categories
    "Entertainment": ["Entertainment", "Food", "Travel", "Shopping"],
    "Giving": ["Gifts"],
    "Financial Freedom": ["Investments"],
}


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def init_db():
    """
    Create database tables if they don't exist.

    Called once when the app starts. Safe to call multiple times —
    'IF NOT EXISTS' prevents errors if tables already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Transactions table — stores every income/expense entry
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            type        TEXT    NOT NULL CHECK(type IN ('Income', 'Expense')),
            category    TEXT    NOT NULL,
            amount      REAL    NOT NULL CHECK(amount > 0),
            description TEXT    DEFAULT '',
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Jars table — stores budget jar definitions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jars (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            percentage  REAL    NOT NULL CHECK(percentage >= 0 AND percentage <= 100),
            color       TEXT    NOT NULL,
            description TEXT    DEFAULT ''
        )
    """)

    # Insert default jars if the table is empty
    cursor.execute("SELECT COUNT(*) FROM jars")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO jars (name, percentage, color, description) VALUES (?, ?, ?, ?)",
            DEFAULT_JARS,
        )

    conn.commit()
    conn.close()


# ─── Transaction CRUD Operations ────────────────────────────────────────────


def add_transaction(date, txn_type, category, amount, description=""):
    """
    Add a new transaction to the database.

    Parameters:
        date (str):        Date in 'YYYY-MM-DD' format
        txn_type (str):    'Income' or 'Expense'
        category (str):    Category name (e.g., 'Food', 'Salary')
        amount (float):    Amount (must be positive)
        description (str): Optional note about the transaction
    """
    conn = get_connection()
    conn.execute(
        "INSERT INTO transactions (date, type, category, amount, description) VALUES (?, ?, ?, ?, ?)",
        (str(date), txn_type, category, round(amount, 2), description),
    )
    conn.commit()
    conn.close()


def update_transaction(txn_id, date, txn_type, category, amount, description=""):
    """Update an existing transaction by its ID."""
    conn = get_connection()
    conn.execute(
        """UPDATE transactions
           SET date=?, type=?, category=?, amount=?, description=?
           WHERE id=?""",
        (str(date), txn_type, category, round(amount, 2), description, txn_id),
    )
    conn.commit()
    conn.close()


def delete_transaction(txn_id):
    """Delete a transaction by its ID."""
    conn = get_connection()
    conn.execute("DELETE FROM transactions WHERE id=?", (txn_id,))
    conn.commit()
    conn.close()


def get_all_transactions():
    """
    Fetch all transactions as a pandas DataFrame.

    Returns an empty DataFrame with correct columns if no data exists.
    This prevents errors in charts and tables when the database is new.
    """
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM transactions ORDER BY date DESC, id DESC", conn
    )
    conn.close()

    if df.empty:
        # Return empty DataFrame with expected columns
        return pd.DataFrame(
            columns=["id", "date", "type", "category", "amount", "description", "created_at"]
        )

    df["date"] = pd.to_datetime(df["date"])
    return df


def get_transactions_by_date_range(start_date, end_date):
    """Fetch transactions within a date range."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date DESC",
        conn,
        params=(str(start_date), str(end_date)),
    )
    conn.close()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


# ─── Summary & Analytics Queries ────────────────────────────────────────────


def get_summary(df=None):
    """
    Calculate total income, expenses, and savings.

    Returns a dictionary:
        {
            'total_income': 50000.0,
            'total_expenses': 35000.0,
            'savings': 15000.0,
            'savings_rate': 30.0
        }
    """
    if df is None:
        df = get_all_transactions()

    if df.empty:
        return {
            "total_income": 0,
            "total_expenses": 0,
            "savings": 0,
            "savings_rate": 0,
        }

    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expenses = df[df["type"] == "Expense"]["amount"].sum()
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "savings": round(savings, 2),
        "savings_rate": round(savings_rate, 1),
    }


def get_expense_by_category(df=None):
    """Get total spending per expense category."""
    if df is None:
        df = get_all_transactions()

    expenses = df[df["type"] == "Expense"]
    if expenses.empty:
        return pd.DataFrame(columns=["category", "amount"])

    return expenses.groupby("category")["amount"].sum().reset_index().sort_values(
        "amount", ascending=False
    )


def get_monthly_trend(df=None):
    """Get monthly income and expense totals for trend charts."""
    if df is None:
        df = get_all_transactions()

    if df.empty:
        return pd.DataFrame(columns=["month", "type", "amount"])

    df_copy = df.copy()
    df_copy["month"] = df_copy["date"].dt.to_period("M").astype(str)

    return df_copy.groupby(["month", "type"])["amount"].sum().reset_index()


# ─── Jar/Budget Operations ──────────────────────────────────────────────────


def get_jars():
    """Fetch all budget jars as a list of dictionaries."""
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM jars ORDER BY id")
    jars = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jars


def update_jar_percentage(jar_id, percentage):
    """Update a jar's percentage allocation."""
    conn = get_connection()
    conn.execute("UPDATE jars SET percentage=? WHERE id=?", (percentage, jar_id))
    conn.commit()
    conn.close()


def get_jar_summary(df=None):
    """
    Calculate how much money is allocated to each jar and how much is spent.

    For each jar:
        - allocated = total_income × jar_percentage / 100
        - spent = sum of expenses in categories mapped to this jar
        - remaining = allocated - spent

    Returns a list of dicts with jar details + financial data.
    """
    if df is None:
        df = get_all_transactions()

    summary = get_summary(df)
    total_income = summary["total_income"]
    jars = get_jars()

    jar_summary = []
    for jar in jars:
        # Calculate how much money this jar gets
        allocated = total_income * jar["percentage"] / 100

        # Calculate how much has been spent from this jar
        mapped_categories = JAR_CATEGORY_MAP.get(jar["name"], [])
        spent = 0
        if mapped_categories and not df.empty:
            expenses = df[(df["type"] == "Expense") & (df["category"].isin(mapped_categories))]
            spent = expenses["amount"].sum() if not expenses.empty else 0

        remaining = allocated - spent
        usage_pct = (spent / allocated * 100) if allocated > 0 else 0

        jar_summary.append({
            "name": jar["name"],
            "percentage": jar["percentage"],
            "color": jar["color"],
            "description": jar["description"],
            "allocated": round(allocated, 2),
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "usage_percent": round(usage_pct, 1),
            "id": jar["id"],
        })

    return jar_summary


def clear_all_transactions():
    """Delete all transactions — used when resetting sample data."""
    conn = get_connection()
    conn.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()


def get_transaction_count():
    """Return the number of transactions in the database."""
    conn = get_connection()
    cursor = conn.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    conn.close()
    return count
