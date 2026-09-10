import streamlit as st
import pandas as pd
import sys
from pathlib import Path


# ============================================================
# PROJECT SETUP
# ============================================================

sys.path.append(
    str(Path(__file__).parent / "src")
)

from analytics import RetailAnalytics
from inventory_alerts import InventoryAlerts
from sales_alerts import SalesAlerts
from copilot import RetailCopilot


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RetailIQ Copilot",
    page_icon="🛍️",
    layout="wide"
)


# ============================================================
# DATA PATH
# ============================================================

data_path = Path(__file__).parent / "data"


# ============================================================
# LOAD DATA
# ============================================================

stores_data = pd.read_csv(
    data_path / "stores.csv"
)

sales_data = pd.read_csv(
    data_path / "sales.csv"
)

sales_data["date"] = pd.to_datetime(
    sales_data["date"]
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🛍️ RetailIQ")

st.sidebar.write(
    "Retail Sales & Inventory Copilot"
)

store_options = ["All Stores"] + list(
    stores_data["store_id"].unique()
)

selected_store = st.sidebar.selectbox(
    "🏪 Select Store",
    store_options
)

st.sidebar.divider()

st.sidebar.info(
    "Use the dashboard to monitor sales, "
    "inventory and business priorities."
)


# ============================================================
# FILTER SALES
# ============================================================

if selected_store == "All Stores":

    filtered_sales = sales_data

else:

    filtered_sales = sales_data[
        sales_data["store_id"] == selected_store
    ]


# ============================================================
# INITIALIZE ANALYTICS
# ============================================================

analytics = RetailAnalytics()

inventory = InventoryAlerts()

sales_alerts = SalesAlerts()


# ============================================================
# ANALYTICS
# ============================================================

sales = analytics.total_sales()

top_products = analytics.top_products(5)

store_sales = analytics.sales_by_store()

stockout_risk = inventory.stockout_risk()

overstock = inventory.overstock()

sales_spikes = sales_alerts.sales_spikes()

sales_drops = sales_alerts.sales_drops()


# ============================================================
# HEADER
# ============================================================

st.title("🛍️ RetailIQ Copilot")

st.subheader(
    "AI-Powered Sales & Inventory Intelligence"
)

st.write(
    f"📍 **Currently viewing:** {selected_store}"
)


# ============================================================
# BUSINESS OVERVIEW
# ============================================================

st.divider()

st.header("📊 Business Overview")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "💰 Total Revenue",
        f"₹{sales['total_revenue']:,}"
    )


with col2:

    st.metric(
        "📦 Units Sold",
        f"{sales['total_units']:,}"
    )


with col3:

    st.metric(
        "🧾 Sales Records",
        f"{sales['sales_records']:,}"
    )


with col4:

    total_issues = (
        len(stockout_risk)
        + len(sales_spikes)
        + len(sales_drops)
    )

    st.metric(
        "🚨 Issues",
        total_issues
    )


# ============================================================
# SALES INTELLIGENCE
# ============================================================

st.divider()

st.header("📈 Sales Intelligence")

col1, col2 = st.columns(2)


# -----------------------------
# Top Products
# -----------------------------

with col1:

    st.subheader("🏆 Top Products")

    st.dataframe(
        top_products,
        use_container_width=True,
        hide_index=True
    )


# -----------------------------
# Store Performance
# -----------------------------

with col2:

    st.subheader("🏪 Store Performance")

    st.dataframe(
        store_sales,
        use_container_width=True,
        hide_index=True
    )


# -----------------------------
# Daily Sales Trend
# -----------------------------

st.subheader("📈 Daily Sales Trend")

daily_sales = (
    filtered_sales
    .groupby("date")["revenue"]
    .sum()
)

st.line_chart(
    daily_sales
)


# ============================================================
# INVENTORY INTELLIGENCE
# ============================================================

st.divider()

st.header("📦 Inventory Intelligence")


# -----------------------------
# Current Inventory
# -----------------------------

inventory_data = analytics.current_inventory()


col1, col2, col3 = st.columns(3)


with col1:

    current_stock = inventory_data[
        "stock_quantity"
    ].sum()

    st.metric(
        "📦 Current Stock",
        f"{current_stock:,}"
    )


with col2:

    st.metric(
        "🔴 Stock-Out Risks",
        len(stockout_risk)
    )


with col3:

    st.metric(
        "📦 Overstock Items",
        len(overstock)
    )


# -----------------------------
# Inventory Tables
# -----------------------------

col1, col2 = st.columns(2)


# Stock-out risks
with col1:

    st.subheader("🔴 Stock-Out Risks")

    if not stockout_risk.empty:

        st.dataframe(
            stockout_risk,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "✅ No major stock-out risks detected."
        )


# Overstock
with col2:

    st.subheader("📦 Overstock")

    if not overstock.empty:

        st.dataframe(
            overstock,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "✅ No major overstock detected."
        )


# ============================================================
# ATTENTION REQUIRED
# ============================================================

st.divider()

st.header("🚨 Attention Required")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "🔴 Stock-Out Risks",
        len(stockout_risk)
    )


with col2:

    st.metric(
        "📈 Sales Spikes",
        len(sales_spikes)
    )


with col3:

    st.metric(
        "📉 Sales Drops",
        len(sales_drops)
    )


# ============================================================
# SALES ALERTS
# ============================================================

col1, col2 = st.columns(2)


# -----------------------------
# Sales Spikes
# -----------------------------

with col1:

    st.subheader("📈 Sales Spikes")

    if not sales_spikes.empty:

        st.dataframe(
            sales_spikes,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No significant sales spikes detected."
        )


# -----------------------------
# Sales Drops
# -----------------------------

with col2:

    st.subheader("📉 Sales Drops")

    if not sales_drops.empty:

        st.dataframe(
            sales_drops,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "✅ No significant sales drops detected."
        )


# ============================================================
# TODAY'S PRIORITIES
# ============================================================

st.divider()

st.header("🎯 Today's Priorities")

priorities = []


# ============================================================
# HIGH PRIORITY - STOCK-OUT
# ============================================================

for _, row in stockout_risk.iterrows():

    product = row.get(
        "product_name",
        "Unknown Product"
    )

    store = row.get(
        "store_id",
        "Unknown Store"
    )

    stock = row.get(
        "stock_quantity",
        0
    )

    days = row.get(
        "days_of_inventory",
        0
    )

    priorities.append({

        "Priority": "🔴 HIGH",

        "Issue": "Stock-out risk",

        "Product": product,

        "Store": store,

        "Evidence": (
            f"Stock: {stock} | "
            f"~{days:.1f} days remaining"
        ),

        "Recommended Action":
            "Reorder stock immediately"
    })


# ============================================================
# MEDIUM PRIORITY - SALES SPIKES
# ============================================================

for _, row in sales_spikes.iterrows():

    product = row.get(
        "product_name",
        "Unknown Product"
    )

    change = row.get(
        "change",
        0
    )

    priorities.append({

        "Priority": "🟡 MEDIUM",

        "Issue": "Sales spike",

        "Product": product,

        "Store": "All stores",

        "Evidence": (
            f"Sales increased by "
            f"{float(change):.1f}%"
        ),

        "Recommended Action":
            "Review demand and increase stock if needed"
    })


# ============================================================
# MEDIUM PRIORITY - SALES DROPS
# ============================================================

for _, row in sales_drops.iterrows():

    product = row.get(
        "product_name",
        "Unknown Product"
    )

    change = row.get(
        "change",
        0
    )

    priorities.append({

        "Priority": "🟡 MEDIUM",

        "Issue": "Sales decline",

        "Product": product,

        "Store": "All stores",

        "Evidence": (
            f"Sales decreased by "
            f"{abs(float(change)):.1f}%"
        ),

        "Recommended Action":
            "Investigate demand and consider promotion"
    })


# ============================================================
# DISPLAY PRIORITIES
# ============================================================

if len(priorities) > 0:

    priority_df = pd.DataFrame(
        priorities
    )

    priority_order = {
        "🔴 HIGH": 1,
        "🟡 MEDIUM": 2,
        "🟢 LOW": 3
    }

    priority_df["Sort"] = (
        priority_df["Priority"]
        .map(priority_order)
    )

    priority_df = (
        priority_df
        .sort_values("Sort")
        .drop(columns=["Sort"])
    )

    st.dataframe(
        priority_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "✅ No urgent priorities detected today."
    )


# ============================================================
# AI MANAGER
# ============================================================

st.divider()

st.header("🤖 Ask RetailIQ")

st.write(
    "Ask RetailIQ about sales, inventory, "
    "products, stores or today's priorities."
)


question = st.text_input(
    "Manager Question",
    placeholder=(
        "Example: Which products need immediate attention?"
    )
)


if st.button(
    "🤖 Ask RetailIQ",
    use_container_width=True
):

    if question:

        with st.spinner(
            "RetailIQ is analyzing your business data..."
        ):

            try:

                copilot = RetailCopilot()

                answer = copilot.ask(
                    question
                )

                st.subheader(
                    "💡 RetailIQ Answer"
                )

                st.write(
                    answer
                )

            except Exception as e:

                st.error(
                    f"Unable to get AI response: {e}"
                )

    else:

        st.warning(
            "Please enter a question first."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "RetailIQ Copilot • AI-powered retail decision support"
)