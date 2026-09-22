"""
app.py — Personal Finance Dashboard (Streamlit)

Main entry point for the application. Run with:
    streamlit run app.py

This file contains all 4 pages of the dashboard:
    1. 📊 Dashboard  — Overview with KPIs and charts
    2. 💰 Transactions — Add, edit, delete transactions
    3. 🏺 Jar System  — Budget jars with progress tracking
    4. 📈 Analytics   — Detailed spending analysis
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta

# Import our custom modules
from database import (
    init_db,
    add_transaction,
    update_transaction,
    delete_transaction,
    get_all_transactions,
    get_summary,
    get_expense_by_category,
    get_monthly_trend,
    get_jar_summary,
    get_jars,
    update_jar_percentage,
    get_transaction_count,
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
)
from sample_data import load_sample_data

# ─── Page Configuration ─────────────────────────────────────────────────────

st.set_page_config(
    page_title="💰 Personal Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS for Modern Look ─────────────────────────────────────────────

st.markdown("""
<style>
    /* ── KPI Metric Cards ── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea11, #764ba211);
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #666 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* ── Sidebar Styling ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e, #16213e);
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }

    /* ── Card Container ── */
    .jar-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-left: 4px solid;
    }

    /* ── Smooth transitions ── */
    .stProgress > div > div {
        transition: width 0.5s ease;
    }

    /* ── Section dividers ── */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #eee;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─── Initialize Database ────────────────────────────────────────────────────

init_db()

# ─── Sidebar Navigation ─────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 💰 Finance Dashboard")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "💰 Transactions", "🏺 Jar System", "📈 Analytics"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Quick stats in sidebar
    txn_count = get_transaction_count()
    st.caption(f"📝 {txn_count} transactions recorded")

    st.markdown("---")

    # Sample data loader
    st.markdown("### 🧪 Sample Data")
    if st.button("🔄 Load Sample Data", use_container_width=True):
        load_sample_data()
        st.success("✅ Sample data loaded!")
        st.rerun()

    if txn_count > 0:
        if st.button("🗑️ Clear All Data", use_container_width=True, type="secondary"):
            from database import clear_all_transactions
            clear_all_transactions()
            st.success("🗑️ All data cleared!")
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1: DASHBOARD — Overview with KPIs and charts
# ═════════════════════════════════════════════════════════════════════════════

if page == "📊 Dashboard":
    st.title("📊 Financial Overview")
    st.caption("Your financial health at a glance")

    # Fetch all data
    df = get_all_transactions()
    summary = get_summary(df)

    # ── KPI Cards Row ──
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Income",
            value=f"₹{summary['total_income']:,.0f}",
            delta="All time",
        )
    with col2:
        st.metric(
            label="Total Expenses",
            value=f"₹{summary['total_expenses']:,.0f}",
            delta=f"-₹{summary['total_expenses']:,.0f}",
            delta_color="inverse",
        )
    with col3:
        st.metric(
            label="Net Savings",
            value=f"₹{summary['savings']:,.0f}",
            delta=f"{summary['savings_rate']}% saved",
            delta_color="normal",
        )
    with col4:
        st.metric(
            label="Savings Rate",
            value=f"{summary['savings_rate']}%",
            delta="of income",
        )

    st.markdown("---")

    if df.empty:
        st.info("📭 No transactions yet! Click **'Load Sample Data'** in the sidebar to get started, or go to **Transactions** to add your first entry.")
    else:
        # ── Charts Row ──
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.subheader("💳 Expense Breakdown")
            expense_data = get_expense_by_category(df)
            if not expense_data.empty:
                fig_pie = px.pie(
                    expense_data,
                    values="amount",
                    names="category",
                    hole=0.45,  # Donut chart looks more modern
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig_pie.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
                )
                fig_pie.update_layout(
                    showlegend=False,
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=350,
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No expense data to show.")

        with chart_col2:
            st.subheader("📅 Monthly Trend")
            monthly = get_monthly_trend(df)
            if not monthly.empty:
                fig_trend = px.bar(
                    monthly,
                    x="month",
                    y="amount",
                    color="type",
                    barmode="group",
                    color_discrete_map={"Income": "#2ecc71", "Expense": "#e74c3c"},
                    labels={"amount": "Amount (₹)", "month": "Month", "type": "Type"},
                )
                fig_trend.update_layout(
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=350,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No monthly data to show.")

        # ── Recent Transactions Table ──
        st.subheader("🕐 Recent Transactions")
        recent = df.head(10).copy()
        recent["date"] = recent["date"].dt.strftime("%d %b %Y")
        recent["amount"] = recent["amount"].apply(lambda x: f"₹{x:,.2f}")

        # Color-code the type column
        st.dataframe(
            recent[["date", "type", "category", "amount", "description"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "date": st.column_config.TextColumn("📅 Date", width="medium"),
                "type": st.column_config.TextColumn("📌 Type", width="small"),
                "category": st.column_config.TextColumn("🏷️ Category", width="medium"),
                "amount": st.column_config.TextColumn("💵 Amount", width="medium"),
                "description": st.column_config.TextColumn("📝 Note", width="large"),
            },
        )


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2: TRANSACTIONS — Add, Edit, Delete
# ═════════════════════════════════════════════════════════════════════════════

elif page == "💰 Transactions":
    st.title("💰 Manage Transactions")
    st.caption("Add, edit, and delete your income and expenses")

    # ── Add New Transaction Form ──
    with st.expander("➕ Add New Transaction", expanded=True):
        with st.form("add_transaction_form", clear_on_submit=True):
            form_col1, form_col2 = st.columns(2)

            with form_col1:
                txn_date = st.date_input("📅 Date", value=date.today(), max_value=date.today())
                txn_type = st.selectbox("📌 Type", ["Expense", "Income"])

            with form_col2:
                # Show different categories based on type
                categories = EXPENSE_CATEGORIES if txn_type == "Expense" else INCOME_CATEGORIES
                txn_category = st.selectbox("🏷️ Category", categories)
                txn_amount = st.number_input("💵 Amount (₹)", min_value=0.01, step=100.0, format="%.2f")

            txn_description = st.text_input("📝 Description (optional)", placeholder="e.g., Dinner at restaurant")

            submitted = st.form_submit_button("✅ Add Transaction", use_container_width=True, type="primary")
            if submitted:
                add_transaction(txn_date, txn_type, txn_category, txn_amount, txn_description)
                st.success(f"✅ Added {txn_type}: ₹{txn_amount:,.2f} in {txn_category}")
                st.rerun()

    st.markdown("---")

    # ── All Transactions Table ──
    st.subheader("📋 All Transactions")

    df = get_all_transactions()

    if df.empty:
        st.info("📭 No transactions yet. Use the form above to add one!")
    else:
        # Filters
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            type_filter = st.selectbox("Filter by Type", ["All", "Income", "Expense"])
        with filter_col2:
            all_categories = sorted(df["category"].unique().tolist())
            cat_filter = st.selectbox("Filter by Category", ["All"] + all_categories)
        with filter_col3:
            sort_order = st.selectbox("Sort by Date", ["Newest First", "Oldest First"])

        # Apply filters
        filtered_df = df.copy()
        if type_filter != "All":
            filtered_df = filtered_df[filtered_df["type"] == type_filter]
        if cat_filter != "All":
            filtered_df = filtered_df[filtered_df["category"] == cat_filter]
        if sort_order == "Oldest First":
            filtered_df = filtered_df.sort_values("date", ascending=True)

        st.caption(f"Showing {len(filtered_df)} of {len(df)} transactions")

        # Display transactions with edit/delete buttons
        for idx, row in filtered_df.iterrows():
            with st.container():
                cols = st.columns([2, 1.5, 1.5, 2, 3, 1, 1])

                date_str = row["date"].strftime("%d %b %Y")
                type_emoji = "🟢" if row["type"] == "Income" else "🔴"
                amount_str = f"₹{row['amount']:,.2f}"

                cols[0].markdown(f"**{date_str}**")
                cols[1].markdown(f"{type_emoji} {row['type']}")
                cols[2].markdown(f"🏷️ {row['category']}")
                cols[3].markdown(f"**{amount_str}**")
                cols[4].markdown(f"_{row['description']}_" if row["description"] else "_—_")

                # Edit button
                if cols[5].button("✏️", key=f"edit_{row['id']}", help="Edit"):
                    st.session_state[f"editing_{row['id']}"] = True

                # Delete button
                if cols[6].button("🗑️", key=f"del_{row['id']}", help="Delete"):
                    delete_transaction(row["id"])
                    st.success(f"🗑️ Deleted transaction #{row['id']}")
                    st.rerun()

                # Edit form (shown when edit button is clicked)
                if st.session_state.get(f"editing_{row['id']}", False):
                    with st.form(f"edit_form_{row['id']}"):
                        st.markdown(f"**Editing Transaction #{row['id']}**")
                        ec1, ec2 = st.columns(2)

                        with ec1:
                            edit_date = st.date_input("Date", value=row["date"].date(), key=f"edate_{row['id']}")
                            edit_type = st.selectbox(
                                "Type", ["Expense", "Income"],
                                index=0 if row["type"] == "Expense" else 1,
                                key=f"etype_{row['id']}",
                            )
                        with ec2:
                            edit_cats = EXPENSE_CATEGORIES if edit_type == "Expense" else INCOME_CATEGORIES
                            default_idx = edit_cats.index(row["category"]) if row["category"] in edit_cats else 0
                            edit_cat = st.selectbox("Category", edit_cats, index=default_idx, key=f"ecat_{row['id']}")
                            edit_amount = st.number_input(
                                "Amount", value=float(row["amount"]), min_value=0.01, key=f"eamt_{row['id']}"
                            )

                        edit_desc = st.text_input("Description", value=row["description"] or "", key=f"edesc_{row['id']}")

                        save_col, cancel_col = st.columns(2)
                        with save_col:
                            if st.form_submit_button("💾 Save", use_container_width=True, type="primary"):
                                update_transaction(row["id"], edit_date, edit_type, edit_cat, edit_amount, edit_desc)
                                st.session_state[f"editing_{row['id']}"] = False
                                st.success("✅ Updated!")
                                st.rerun()
                        with cancel_col:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state[f"editing_{row['id']}"] = False
                                st.rerun()

                st.markdown("<hr style='margin: 4px 0; border-top: 1px solid #f0f0f0;'>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 3: JAR SYSTEM — Budget allocation and tracking
# ═════════════════════════════════════════════════════════════════════════════

elif page == "🏺 Jar System":
    st.title("🏺 Jar / Budget System")
    st.caption("Divide your income into jars and track where your money goes")

    df = get_all_transactions()
    summary = get_summary(df)
    jar_data = get_jar_summary(df)

    # ── Total Income Reference ──
    st.info(f"💵 **Total Income: ₹{summary['total_income']:,.0f}** — This is divided across your jars based on percentages below.")

    st.markdown("---")

    if summary["total_income"] == 0:
        st.warning("⚠️ No income recorded yet. Add income transactions to see your jar allocations.")
    else:
        # ── Jar Cards ──
        # Display jars in a 2-column grid
        for i in range(0, len(jar_data), 2):
            cols = st.columns(2)

            for j, col in enumerate(cols):
                if i + j < len(jar_data):
                    jar = jar_data[i + j]

                    with col:
                        # Determine status color
                        if jar["usage_percent"] > 100:
                            status = "🔴 Over Budget!"
                            status_color = "#e74c3c"
                        elif jar["usage_percent"] > 80:
                            status = "🟡 Almost Full"
                            status_color = "#f39c12"
                        else:
                            status = "🟢 On Track"
                            status_color = "#2ecc71"

                        st.markdown(f"""
                        <div class="jar-card" style="border-left-color: {jar['color']};">
                            <h3 style="margin:0; color: {jar['color']};">🏺 {jar['name']}</h3>
                            <p style="margin:4px 0; color:#888; font-size:0.85rem;">{jar['description']}</p>
                            <p style="margin:2px 0;"><b>Allocation:</b> {jar['percentage']}% of income = <b>₹{jar['allocated']:,.0f}</b></p>
                            <p style="margin:2px 0;"><b>Spent:</b> ₹{jar['spent']:,.0f}</p>
                            <p style="margin:2px 0;"><b>Remaining:</b> <span style="color:{status_color}; font-weight:bold;">₹{jar['remaining']:,.0f}</span></p>
                            <p style="margin:2px 0;">{status}</p>
                        </div>
                        """, unsafe_allow_html=True)

                        # Progress bar showing usage
                        progress_val = min(jar["usage_percent"] / 100, 1.0)
                        st.progress(progress_val, text=f"{jar['usage_percent']}% used")

        st.markdown("---")

        # ── Jar Allocation Chart ──
        st.subheader("📊 Jar Allocation vs Spending")

        jar_chart_data = pd.DataFrame(jar_data)

        fig_jars = go.Figure()
        fig_jars.add_trace(go.Bar(
            name="Allocated",
            x=jar_chart_data["name"],
            y=jar_chart_data["allocated"],
            marker_color=[j["color"] for j in jar_data],
            opacity=0.6,
            text=jar_chart_data["allocated"].apply(lambda x: f"₹{x:,.0f}"),
            textposition="outside",
        ))
        fig_jars.add_trace(go.Bar(
            name="Spent",
            x=jar_chart_data["name"],
            y=jar_chart_data["spent"],
            marker_color=[j["color"] for j in jar_data],
            opacity=1.0,
            text=jar_chart_data["spent"].apply(lambda x: f"₹{x:,.0f}"),
            textposition="outside",
        ))

        fig_jars.update_layout(
            barmode="group",
            height=400,
            margin=dict(t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis_title="Amount (₹)",
        )
        st.plotly_chart(fig_jars, use_container_width=True)

    # ── Edit Jar Percentages ──
    st.markdown("---")
    st.subheader("⚙️ Customize Jar Percentages")
    st.caption("Adjust how your income is divided. Total should add up to 100%.")

    jars = get_jars()
    total_pct = 0

    with st.form("jar_percentages_form"):
        jar_cols = st.columns(3)

        new_percentages = {}
        for idx, jar in enumerate(jars):
            with jar_cols[idx % 3]:
                new_pct = st.number_input(
                    f"🏺 {jar['name']} (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(jar["percentage"]),
                    step=1.0,
                    key=f"jar_pct_{jar['id']}",
                )
                new_percentages[jar["id"]] = new_pct
                total_pct += new_pct

        # Show total
        if abs(total_pct - 100) > 0.1:
            st.warning(f"⚠️ Total: {total_pct}% — Should be 100%")
        else:
            st.success(f"✅ Total: {total_pct}%")

        if st.form_submit_button("💾 Save Jar Settings", use_container_width=True, type="primary"):
            if abs(total_pct - 100) > 0.1:
                st.error("❌ Percentages must add up to 100%!")
            else:
                for jar_id, pct in new_percentages.items():
                    update_jar_percentage(jar_id, pct)
                st.success("✅ Jar percentages updated!")
                st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 4: ANALYTICS — Detailed spending analysis
# ═════════════════════════════════════════════════════════════════════════════

elif page == "📈 Analytics":
    st.title("📈 Spending Analytics")
    st.caption("Understand your spending habits with detailed charts")

    df = get_all_transactions()

    if df.empty:
        st.info("📭 No data to analyze. Add some transactions first!")
    else:
        # ── Date Range Filter ──
        st.subheader("📅 Filter by Date Range")
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            start_date = st.date_input(
                "From",
                value=df["date"].min().date(),
                min_value=df["date"].min().date(),
                max_value=df["date"].max().date(),
            )
        with date_col2:
            end_date = st.date_input(
                "To",
                value=df["date"].max().date(),
                min_value=df["date"].min().date(),
                max_value=df["date"].max().date(),
            )

        # Filter data
        mask = (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
        filtered_df = df[mask]

        if filtered_df.empty:
            st.warning("No transactions in this date range.")
        else:
            summary = get_summary(filtered_df)
            st.info(
                f"📊 **Period Summary** — "
                f"Income: ₹{summary['total_income']:,.0f} | "
                f"Expenses: ₹{summary['total_expenses']:,.0f} | "
                f"Savings: ₹{summary['savings']:,.0f}"
            )

            st.markdown("---")

            # ── Row 1: Category Breakdown + Income vs Expense ──
            an_col1, an_col2 = st.columns(2)

            with an_col1:
                st.subheader("🏷️ Spending by Category")
                expenses = filtered_df[filtered_df["type"] == "Expense"]
                if not expenses.empty:
                    cat_data = expenses.groupby("category")["amount"].sum().reset_index()
                    cat_data = cat_data.sort_values("amount", ascending=True)

                    fig_cat = px.bar(
                        cat_data,
                        x="amount",
                        y="category",
                        orientation="h",
                        color="category",
                        color_discrete_sequence=px.colors.qualitative.Set3,
                        labels={"amount": "Amount (₹)", "category": "Category"},
                    )
                    fig_cat.update_layout(
                        showlegend=False,
                        height=400,
                        margin=dict(t=20, b=20),
                    )
                    fig_cat.update_traces(
                        text=cat_data["amount"].apply(lambda x: f"₹{x:,.0f}"),
                        textposition="outside",
                        hovertemplate="<b>%{y}</b><br>₹%{x:,.0f}<extra></extra>",
                    )
                    st.plotly_chart(fig_cat, use_container_width=True)
                else:
                    st.info("No expenses in this period.")

            with an_col2:
                st.subheader("⚖️ Income vs Expenses")
                type_data = filtered_df.groupby("type")["amount"].sum().reset_index()

                fig_compare = px.bar(
                    type_data,
                    x="type",
                    y="amount",
                    color="type",
                    color_discrete_map={"Income": "#2ecc71", "Expense": "#e74c3c"},
                    labels={"amount": "Amount (₹)", "type": ""},
                    text_auto=True,
                )
                fig_compare.update_layout(
                    showlegend=False,
                    height=400,
                    margin=dict(t=20, b=20),
                )
                fig_compare.update_traces(
                    texttemplate="₹%{y:,.0f}",
                    textposition="outside",
                )
                st.plotly_chart(fig_compare, use_container_width=True)

            st.markdown("---")

            # ── Row 2: Daily Trend + Top Expenses ──
            an_col3, an_col4 = st.columns(2)

            with an_col3:
                st.subheader("📉 Daily Spending Trend")
                daily_expenses = filtered_df[filtered_df["type"] == "Expense"].copy()
                if not daily_expenses.empty:
                    daily = daily_expenses.groupby(daily_expenses["date"].dt.date)["amount"].sum().reset_index()
                    daily.columns = ["date", "amount"]

                    fig_daily = px.area(
                        daily,
                        x="date",
                        y="amount",
                        labels={"amount": "Amount (₹)", "date": "Date"},
                        color_discrete_sequence=["#e74c3c"],
                    )
                    fig_daily.update_layout(
                        height=350,
                        margin=dict(t=20, b=20),
                    )
                    fig_daily.update_traces(
                        fill="tozeroy",
                        fillcolor="rgba(231,76,60,0.15)",
                        hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
                    )
                    st.plotly_chart(fig_daily, use_container_width=True)
                else:
                    st.info("No expense data.")

            with an_col4:
                st.subheader("🔝 Top 5 Expenses")
                top_expenses = filtered_df[filtered_df["type"] == "Expense"].nlargest(5, "amount")
                if not top_expenses.empty:
                    for _, row in top_expenses.iterrows():
                        date_str = row["date"].strftime("%d %b")
                        st.markdown(
                            f"**₹{row['amount']:,.0f}** — {row['category']} "
                            f"({'_' + row['description'] + '_' if row['description'] else ''})"
                            f"  `{date_str}`"
                        )
                        st.progress(
                            min(row["amount"] / top_expenses["amount"].max(), 1.0),
                        )
                else:
                    st.info("No expenses found.")

            st.markdown("---")

            # ── Row 3: Category Distribution Over Time ──
            st.subheader("📊 Category Spending Over Time")
            expenses_time = filtered_df[filtered_df["type"] == "Expense"].copy()
            if not expenses_time.empty:
                expenses_time["week"] = expenses_time["date"].dt.isocalendar().week.astype(str)
                weekly_cat = expenses_time.groupby(["week", "category"])["amount"].sum().reset_index()

                fig_stacked = px.bar(
                    weekly_cat,
                    x="week",
                    y="amount",
                    color="category",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    labels={"amount": "Amount (₹)", "week": "Week Number", "category": "Category"},
                )
                fig_stacked.update_layout(
                    height=400,
                    margin=dict(t=20, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig_stacked, use_container_width=True)
