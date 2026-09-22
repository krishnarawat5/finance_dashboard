# 💰 Personal Finance Dashboard

A clean, modern **Personal Finance Dashboard** built with Python and Streamlit.
Track your income, expenses, savings, and manage your money using the **6 Jars Budget System**.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

---

## ✨ Features

- **📊 Dashboard** — KPI cards showing total income, expenses, savings, and savings rate with interactive charts
- **💰 Transactions** — Add, edit, and delete income/expense entries with category tagging
- **🏺 Jar System** — Divide your income into budget jars (Necessities, Education, Savings, Entertainment, Giving, Financial Freedom)
- **📈 Analytics** — Category breakdowns, daily trends, income vs expense comparison, top expenses
- **💾 Persistent Storage** — SQLite database saves your data during each session
- **🧪 Sample Data** — One-click sample data loader for immediate testing

---

## 🚀 Deploy to Streamlit Community Cloud

### Step 1: Push to GitHub

This folder must be its **own GitHub repository** (not inside another project).

```bash
cd c:\Users\rawat\Downloads\AI_Chatbot\finance_dashboard

# Initialize git repo
git init
git add .
git commit -m "Initial commit: Personal Finance Dashboard"

# Create a new repo on GitHub (e.g., 'finance-dashboard'), then:
git remote add origin https://github.com/YOUR_USERNAME/finance-dashboard.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your **GitHub** account
3. Click **"New app"**
4. Select your **repository**: `YOUR_USERNAME/finance-dashboard`
5. Set **Branch**: `main`
6. Set **Main file path**: `app.py`
7. Click **"Deploy!"**

Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

### Step 3: Access Your Dashboard

Once deployed, you'll get a public URL like:
```
https://finance-dashboard-yourname.streamlit.app
```

Share this URL with anyone — no installation needed!

---

## 🏃 Run Locally (Development)

```bash
cd c:\Users\rawat\Downloads\AI_Chatbot\finance_dashboard
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Opens at **http://localhost:8501**.

---

## 📁 Project Structure

```
finance_dashboard/
├── .streamlit/
│   └── config.toml         # Streamlit theme & server config
├── .gitignore               # Files excluded from git
├── app.py                   # Main Streamlit application (4 pages)
├── database.py              # SQLite database operations (CRUD + queries)
├── sample_data.py           # Sample transaction loader for testing
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🏺 The 6 Jars System

| Jar | Default % | Purpose |
|-----|-----------|---------|
| 🏠 Necessities | 55% | Rent, bills, groceries, essentials |
| 📚 Education | 10% | Books, courses, self-improvement |
| 💰 Savings | 10% | Emergency fund, long-term savings |
| 🎮 Entertainment | 10% | Fun, movies, dining out, hobbies |
| 🎁 Giving | 5% | Gifts, charity, donations |
| 💸 Financial Freedom | 10% | Investments, side business |

You can customize the percentages in the **Jar System** page.

---

## ⚠️ Important: Cloud Storage Note

Streamlit Community Cloud uses **ephemeral storage** — the SQLite database resets when the app sleeps or redeploys. Your data persists during active sessions but is not permanent.

**For permanent cloud storage**, you can upgrade to:
- **Google Sheets** as a backend (free)
- **Supabase** or **PlanetScale** (free tier available)
- **Streamlit `st.session_state`** with file download/upload for data backup

---

## 🔮 Future Ideas

- CSV import/export for bank statements
- Monthly budget goals with alerts
- Recurring transactions (salary, rent, subscriptions)
- Multi-currency support
- Bill reminders
- AI-powered spending insights
- Cloud database integration for permanent storage

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **Streamlit** — Web UI framework
- **Plotly** — Interactive charts
- **Pandas** — Data manipulation
- **SQLite** — Local database (built into Python)
