from analytics import RetailAnalytics
from inventory_alerts import InventoryAlerts
from sales_alerts import SalesAlerts
import pandas as pd


class RetailCopilot:

    def __init__(self):
        self.analytics = RetailAnalytics()
        self.inventory = InventoryAlerts()
        self.sales = SalesAlerts()

    # =========================================================
    # FIND PRODUCT
    # =========================================================
    def _find_product(self, question):

        try:
            stockout_data = self.inventory.stockout_risk()

            if stockout_data.empty:
                return None

            if "product_name" not in stockout_data.columns:
                return None

            products = (
                stockout_data["product_name"]
                .dropna()
                .astype(str)
                .unique()
            )

            # Longest product names first
            products = sorted(
                products,
                key=len,
                reverse=True
            )

            for product in products:

                if product.lower() in question.lower():
                    return product

        except Exception:
            pass

        return None

    # =========================================================
    # FIND ONE STORE
    # =========================================================
    def _find_store(self, question):

        try:
            store_data = self.analytics.sales_by_store()

            if store_data.empty:
                return None

            if "store_id" not in store_data.columns:
                return None

            # Check store ID
            for store_id in store_data["store_id"].dropna().unique():

                if str(store_id).lower() in question.lower():
                    return store_id

            # Check store name
            if "store_name" in store_data.columns:

                for store_name in (
                    store_data["store_name"]
                    .dropna()
                    .astype(str)
                    .unique()
                ):

                    if store_name.lower() in question.lower():

                        row = store_data[
                            store_data["store_name"].astype(str).str.lower()
                            == store_name.lower()
                        ]

                        if not row.empty:
                            return row.iloc[0]["store_id"]

        except Exception:
            pass

        return None

    # =========================================================
    # FIND MULTIPLE STORES
    # =========================================================
    def _find_stores(self, question):

        stores_found = []

        try:
            store_data = self.analytics.sales_by_store()

            if store_data.empty:
                return stores_found

            if "store_id" not in store_data.columns:
                return stores_found

            store_ids = (
                store_data["store_id"]
                .dropna()
                .astype(str)
                .unique()
            )

            for store_id in store_ids:

                if store_id.lower() in question.lower():
                    stores_found.append(store_id)

        except Exception:
            pass

        return stores_found

    # =========================================================
    # MAIN COPILOT
    # =========================================================
    def ask(self, question):

        if question is None:
            return "Please enter a question."

        question = str(question).strip()

        if not question:
            return "Please enter a question."

        q = question.lower()

        # =====================================================
        # 0. PRODUCT-SPECIFIC QUESTIONS
        # =====================================================

        product = self._find_product(q)

        if product:

            # -------------------------------------------------
            # 0A. WHY ARE SALES DROPPING FOR PRODUCT?
            # -------------------------------------------------

            if (
                "sales dropping" in q
                or "sales drop" in q
                or "sales declining" in q
                or "sales decline" in q
                or "sales decreased" in q
                or "sales decreasing" in q
                or "why are sales" in q
                or "why is sales" in q
            ):

                try:

                    drops = self.sales.sales_drops()

                    if drops.empty:

                        return (
                            f"### 📉 Sales Analysis: {product}\n\n"
                            f"No significant sales drop was detected for "
                            f"**{product}**."
                        )

                    product_drop = drops[
                        drops["product_name"]
                        .astype(str)
                        .str.lower()
                        == str(product).lower()
                    ]

                    if product_drop.empty:

                        return (
                            f"### 📊 {product}\n\n"
                            f"No significant sales drop was detected for "
                            f"**{product}** in the current sales-drop data."
                        )

                    row = product_drop.iloc[0]

                    current_units = float(
                        row.get("current_units", 0)
                    )

                    previous_units = float(
                        row.get("previous_units", 0)
                    )

                    current_revenue = float(
                        row.get("current_revenue", 0)
                    )

                    previous_revenue = float(
                        row.get("previous_revenue", 0)
                    )

                    change_percent = float(
                        row.get("sales_change_percent", 0)
                    )

                    answer = (
                        f"### 📉 Sales Drop: {product}\n\n"
                        f"- Previous units: **{previous_units:,.0f}**\n"
                        f"- Current units: **{current_units:,.0f}**\n"
                        f"- Change: **{change_percent:.2f}%**\n"
                        f"- Previous revenue: "
                        f"**₹{previous_revenue:,.2f}**\n"
                        f"- Current revenue: "
                        f"**₹{current_revenue:,.2f}**\n\n"
                    )

                    # Check inventory risk
                    try:

                        stockout = self.inventory.stockout_risk()

                        product_stock = stockout[
                            stockout["product_name"]
                            .astype(str)
                            .str.lower()
                            == str(product).lower()
                        ]

                        high_risk = product_stock[
                            product_stock["risk_level"]
                            .astype(str)
                            .str.upper()
                            == "HIGH"
                        ]

                        if not high_risk.empty:

                            answer += (
                                "⚠️ **Inventory factor to investigate:** "
                                f"{product} also has a HIGH stock-out "
                                "risk record.\n\n"
                                "This could affect sales, but the available "
                                "data does not prove that the stock-out "
                                "caused the sales decline.\n\n"
                            )

                    except Exception:
                        pass

                    answer += (
                        "### 🔎 Why?\n\n"
                        "The available dataset confirms that sales "
                        "declined, but it does not contain enough "
                        "information about promotions, competitors, "
                        "customer behavior, or pricing changes to "
                        "identify the exact cause.\n\n"
                        "### 🎯 Recommended Action\n\n"
                        "Check inventory availability, pricing, "
                        "promotions, and store-level performance "
                        f"for **{product}**."
                    )

                    return answer

                except Exception as e:

                    return (
                        f"Unable to analyze the sales drop for "
                        f"{product}: {e}"
                    )

            # -------------------------------------------------
            # 0B. PRODUCT STOCK-OUT RISK
            # -------------------------------------------------

            if (
                "at risk" in q
                or "stockout" in q
                or "stock-out" in q
                or "stock out" in q
                or "running out" in q
                or "run out" in q
            ):

                try:

                    stockout = self.inventory.stockout_risk()

                    product_data = stockout[
                        stockout["product_name"]
                        .astype(str)
                        .str.lower()
                        == str(product).lower()
                    ]

                    if product_data.empty:

                        return (
                            f"No stock-out risk information was found "
                            f"for **{product}**."
                        )

                    row = product_data.sort_values(
                        "days_of_inventory"
                    ).iloc[0]

                    return (
                        f"### ⚠️ Stock Risk: {product}\n\n"
                        f"- Store: **{row['store_id']}**\n"
                        f"- Current stock: "
                        f"**{row['stock_quantity']:,.0f} units**\n"
                        f"- Average daily sales: "
                        f"**{row['avg_daily_sales']:.2f} units/day**\n"
                        f"- Days of inventory: "
                        f"**{row['days_of_inventory']:.2f} days**\n"
                        f"- Risk level: **{row['risk_level']}**\n"
                        f"- Recommended action: "
                        f"**{row['recommended_action']}**"
                    )

                except Exception as e:

                    return (
                        f"Unable to analyze stock risk for "
                        f"{product}: {e}"
                    )

            # -------------------------------------------------
            # 0C. WHY SHOULD I REORDER?
            # -------------------------------------------------

            if (
                "why should i reorder" in q
                or "why reorder" in q
                or "should reorder" in q
                or "need to reorder" in q
            ):

                try:

                    stockout = self.inventory.stockout_risk()

                    product_data = stockout[
                        stockout["product_name"]
                        .astype(str)
                        .str.lower()
                        == str(product).lower()
                    ]

                    if product_data.empty:

                        return (
                            f"No reorder information was found "
                            f"for **{product}**."
                        )

                    row = product_data.sort_values(
                        "days_of_inventory"
                    ).iloc[0]

                    return (
                        f"### 🔄 Why Reorder {product}?\n\n"
                        f"Current stock is **"
                        f"{row['stock_quantity']:,.0f} units**.\n\n"
                        f"Average daily sales are **"
                        f"{row['avg_daily_sales']:.2f} units/day**.\n\n"
                        f"That gives approximately **"
                        f"{row['days_of_inventory']:.2f} days "
                        f"of inventory**.\n\n"
                        f"Risk level: **{row['risk_level']}**\n\n"
                        f"👉 Recommended action: "
                        f"**{row['recommended_action']}**"
                    )

                except Exception as e:

                    return (
                        f"Unable to analyze reorder requirement: {e}"
                    )

            # -------------------------------------------------
            # 0D. WHAT SHOULD I DO ABOUT PRODUCT?
            # -------------------------------------------------

            if (
                "what should i do about" in q
                or "what should i do with" in q
                or "action for" in q
                or "what action" in q
            ):

                try:

                    stockout = self.inventory.stockout_risk()

                    product_data = stockout[
                        stockout["product_name"]
                        .astype(str)
                        .str.lower()
                        == str(product).lower()
                    ]

                    if not product_data.empty:

                        row = product_data.sort_values(
                            "days_of_inventory"
                        ).iloc[0]

                        return (
                            f"### 🎯 Recommended Action: {product}\n\n"
                            f"- Store: **{row['store_id']}**\n"
                            f"- Current stock: "
                            f"**{row['stock_quantity']:,.0f} units**\n"
                            f"- Days of inventory: "
                            f"**{row['days_of_inventory']:.2f} days**\n"
                            f"- Risk: **{row['risk_level']}**\n"
                            f"- Action: "
                            f"**{row['recommended_action']}**"
                        )

                except Exception:
                    pass

        # =====================================================
        # 1. COMPARE TWO STORES
        # =====================================================

        if (
            "compare" in q
            or "comparison" in q
            or "compare stores" in q
            or "compare store" in q
        ):

            stores_found = self._find_stores(q)

            if len(stores_found) >= 2:

                try:

                    store_data = self.analytics.sales_by_store()

                    store_a = stores_found[0]
                    store_b = stores_found[1]

                    data_a = store_data[
                        store_data["store_id"]
                        .astype(str)
                        .str.lower()
                        == str(store_a).lower()
                    ]

                    data_b = store_data[
                        store_data["store_id"]
                        .astype(str)
                        .str.lower()
                        == str(store_b).lower()
                    ]

                    if data_a.empty or data_b.empty:

                        return (
                            f"Complete sales data was not found for "
                            f"{store_a} and {store_b}."
                        )

                    row_a = data_a.iloc[0]
                    row_b = data_b.iloc[0]

                    revenue_a = float(
                        row_a.get("revenue", 0)
                    )

                    revenue_b = float(
                        row_b.get("revenue", 0)
                    )

                    units_a = float(
                        row_a.get("units_sold", 0)
                    )

                    units_b = float(
                        row_b.get("units_sold", 0)
                    )

                    revenue_difference = abs(
                        revenue_a - revenue_b
                    )

                    units_difference = abs(
                        units_a - units_b
                    )

                    if revenue_a > revenue_b:
                        revenue_winner = store_a
                    elif revenue_b > revenue_a:
                        revenue_winner = store_b
                    else:
                        revenue_winner = "Tie"

                    if units_a > units_b:
                        units_winner = store_a
                    elif units_b > units_a:
                        units_winner = store_b
                    else:
                        units_winner = "Tie"

                    return (
                        f"### 🏬 Store Comparison\n\n"
                        f"**{store_a}**\n"
                        f"- Revenue: "
                        f"**₹{revenue_a:,.2f}**\n"
                        f"- Units sold: "
                        f"**{units_a:,.0f}**\n\n"
                        f"**{store_b}**\n"
                        f"- Revenue: "
                        f"**₹{revenue_b:,.2f}**\n"
                        f"- Units sold: "
                        f"**{units_b:,.0f}**\n\n"
                        f"### 📊 Result\n\n"
                        f"- Revenue leader: **{revenue_winner}**\n"
                        f"- Units sold leader: **{units_winner}**\n"
                        f"- Revenue difference: "
                        f"**₹{revenue_difference:,.2f}**\n"
                        f"- Units difference: "
                        f"**{units_difference:,.0f}**"
                    )

                except Exception as e:

                    return (
                        f"Unable to compare the stores: {e}"
                    )

            return (
                "Please specify two stores to compare.\n\n"
                "Example:\n"
                "**Compare S001 and S002**"
            )

        # =====================================================
        # 2. WHICH STORE HAS MOST STOCK-OUT RISK?
        # =====================================================

        if (
            "which store has the most stock" in q
            or "which store has most stock" in q
            or "store with the most stock" in q
            or "store with most stock" in q
            or "highest stockout risk store" in q
            or "highest stock-out risk store" in q
            or "most stockout risk" in q
            or "most stock-out risk" in q
        ):

            try:

                stockout = self.inventory.stockout_risk()

                if stockout.empty:

                    return (
                        "### ✅ Stock-Out Risk\n\n"
                        "No stock-out risk records were detected."
                    )

                high_risk = stockout[
                    stockout["risk_level"]
                    .astype(str)
                    .str.upper()
                    == "HIGH"
                ].copy()

                if high_risk.empty:

                    return (
                        "No HIGH-risk stock-out records were found."
                    )

                store_counts = (
                    high_risk
                    .groupby("store_id")
                    .size()
                    .reset_index(
                        name="high_risk_count"
                    )
                    .sort_values(
                        "high_risk_count",
                        ascending=False
                    )
                )

                top_store = store_counts.iloc[0]

                store_id = top_store["store_id"]

                risk_count = int(
                    top_store["high_risk_count"]
                )

                store_products = high_risk[
                    high_risk["store_id"] == store_id
                ].sort_values(
                    "days_of_inventory"
                )

                urgent_product = store_products.iloc[0]

                return (
                    f"### 🚨 Highest Stock-Out Risk Store\n\n"
                    f"**Store {store_id}** has the most HIGH-risk "
                    f"stock-out records.\n\n"
                    f"- HIGH-risk products: "
                    f"**{risk_count}**\n"
                    f"- Most urgent product: "
                    f"**{urgent_product['product_name']}**\n"
                    f"- Current stock: "
                    f"**{urgent_product['stock_quantity']:,.0f} units**\n"
                    f"- Days of inventory: "
                    f"**{urgent_product['days_of_inventory']:.2f} days**\n\n"
                    f"### 🎯 Recommended Action\n\n"
                    f"Prioritize inventory replenishment at "
                    f"**Store {store_id}**."
                )

            except Exception as e:

                return (
                    f"Unable to analyze store stock-out risk: {e}"
                )

        # =====================================================
        # 3. WHICH PRODUCT GENERATES MOST REVENUE?
        # =====================================================

        if (
            "which product generates the most revenue" in q
            or "which product generates most revenue" in q
            or "product generates the most revenue" in q
            or "highest revenue product" in q
            or "product with the highest revenue" in q
            or "most revenue product" in q
            or "product makes the most revenue" in q
            or "product with most revenue" in q
        ):

            try:

                products = self.analytics.top_products(1000)

                if products.empty:

                    return (
                        "No product revenue data is available."
                    )

                if "revenue" not in products.columns:

                    return (
                        "The available product data does not contain "
                        "revenue information."
                    )

                products = products.sort_values(
                    "revenue",
                    ascending=False
                )

                row = products.iloc[0]

                return (
                    f"### 💰 Highest Revenue Product\n\n"
                    f"**{row['product_name']}** generates the "
                    f"most revenue.\n\n"
                    f"- Revenue: "
                    f"**₹{row['revenue']:,.2f}**\n"
                    f"- Units sold: "
                    f"**{row['units_sold']:,.0f}**\n\n"
                    f"👉 This is the highest-revenue product "
                    f"in the available sales data."
                )

            except Exception as e:

                return (
                    f"Unable to identify the highest-revenue "
                    f"product: {e}"
                )

        # =====================================================
        # 4. BIGGEST BUSINESS RISK
        # =====================================================

        if (
            "biggest business risk" in q
            or "biggest risk" in q
            or "main business risk" in q
            or "largest business risk" in q
            or "most important business risk" in q
            or "biggest problem" in q
            or "main risk" in q
            or "greatest risk" in q
            or "biggest threat" in q
            or "main threat" in q
        ):

            try:

                stockout = self.inventory.stockout_risk()
                overstock = self.inventory.overstock()
                spikes = self.sales.sales_spikes()
                drops = self.sales.sales_drops()

                # HIGH stock-out risks
                if stockout.empty:

                    high_risk = pd.DataFrame()

                else:

                    high_risk = stockout[
                        stockout["risk_level"]
                        .astype(str)
                        .str.upper()
                        == "HIGH"
                    ]

                high_risk_count = len(high_risk)

                overstock_count = (
                    len(overstock)
                    if not overstock.empty
                    else 0
                )

                spike_count = (
                    len(spikes)
                    if not spikes.empty
                    else 0
                )

                drop_count = (
                    len(drops)
                    if not drops.empty
                    else 0
                )

                # ---------------------------------------------
                # STOCK-OUT IS HIGHEST PRIORITY
                # ---------------------------------------------

                if high_risk_count > 0:

                    urgent = high_risk.sort_values(
                        "days_of_inventory",
                        ascending=True
                    ).head(5)

                    answer = (
                        "### 🚨 Biggest Business Risk: Stock-Outs\n\n"
                        f"The current inventory data contains "
                        f"**{high_risk_count} HIGH-risk stock-out "
                        f"records**.\n\n"
                        "**Most urgent products:**\n\n"
                    )

                    for _, row in urgent.iterrows():

                        answer += (
                            f"- **{row['product_name']}** — "
                            f"Store **{row['store_id']}**, "
                            f"**{row['days_of_inventory']:.2f} days** "
                            f"of inventory remaining\n"
                        )

                    answer += (
                        "\n### 🎯 Recommended Action\n\n"
                        "Prioritize replenishment for the products "
                        "with the lowest days of inventory."
                    )

                    return answer

                # ---------------------------------------------
                # SALES DROP
                # ---------------------------------------------

                if drop_count > 0:

                    return (
                        "### 📉 Biggest Business Risk: Sales Decline\n\n"
                        f"The current data contains "
                        f"**{drop_count} sales-drop records**.\n\n"
                        "Recommended action: investigate affected "
                        "products using inventory, pricing, "
                        "promotion and store-level data."
                    )

                # ---------------------------------------------
                # OVERSTOCK
                # ---------------------------------------------

                if overstock_count > 0:

                    return (
                        "### 📦 Biggest Business Risk: Overstock\n\n"
                        f"There are **{overstock_count} overstock / "
                        f"slow-moving inventory records**.\n\n"
                        "Recommended action: review slow-moving "
                        "products and reduce unnecessary inventory."
                    )

                # ---------------------------------------------
                # SALES SPIKE
                # ---------------------------------------------

                if spike_count > 0:

                    return (
                        "### 📈 Biggest Business Risk: "
                        "Demand Volatility\n\n"
                        f"The data contains **{spike_count} sales "
                        f"spike(s)**.\n\n"
                        "Review inventory levels to ensure the "
                        "business can support increased demand."
                    )

                return (
                    "### ✅ Biggest Business Risk\n\n"
                    "No major risk was detected from the available "
                    "stock-out, overstock, sales-drop and "
                    "sales-spike indicators."
                )

            except Exception as e:

                return (
                    f"Unable to determine the biggest business "
                    f"risk: {e}"
                )

        # =====================================================
        # 5. TODAY'S PRIORITIES
        # =====================================================

        if (
            (
                "today" in q
                and (
                    "priority" in q
                    or "priorities" in q
                    or "focus" in q
                    or "action" in q
                )
            )
            or "what should i focus on" in q
            or "what should i do today" in q
            or "today focus" in q
        ):

            try:

                stockout = self.inventory.stockout_risk()
                spikes = self.sales.sales_spikes()
                drops = self.sales.sales_drops()

                if stockout.empty:

                    high_risk_count = 0

                else:

                    high_risk_count = len(
                        stockout[
                            stockout["risk_level"]
                            .astype(str)
                            .str.upper()
                            == "HIGH"
                        ]
                    )

                spike_count = (
                    len(spikes)
                    if not spikes.empty
                    else 0
                )

                drop_count = (
                    len(drops)
                    if not drops.empty
                    else 0
                )

                answer = "### 🎯 Today's Priorities\n\n"

                # Priority 1
                if high_risk_count > 0:

                    answer += (
                        f"**1. 🚨 Inventory**\n\n"
                        f"Review **{high_risk_count} HIGH-risk "
                        f"stock-out records** and prioritize "
                        f"replenishment.\n\n"
                    )

                else:

                    answer += (
                        "**1. ✅ Inventory**\n\n"
                        "No HIGH-risk stock-out records are "
                        "currently detected.\n\n"
                    )

                # Priority 2
                answer += (
                    f"**2. 📈 Sales Spikes**\n\n"
                    f"**{spike_count}** sales spike(s) "
                    f"were detected.\n\n"
                )

                # Priority 3
                answer += (
                    f"**3. 📉 Sales Drops**\n\n"
                    f"**{drop_count}** sales drop(s) "
                    f"were detected.\n\n"
                )

                # Priority 4
                answer += (
                    "**4. 🎯 Focus**\n\n"
                    "Prioritize products with the lowest "
                    "days of inventory before reviewing "
                    "lower-priority issues."
                )

                return answer

            except Exception as e:

                return (
                    f"Unable to generate today's priorities: {e}"
                )

        # =====================================================
        # 6. TOTAL SALES / REVENUE
        # =====================================================

        if (
            "total sales" in q
            or "total revenue" in q
            or "how much sales" in q
            or "how much revenue" in q
            or "overall sales" in q
            or "overall revenue" in q
        ):

            try:

                summary = self.analytics.summary()

                revenue = float(
                    summary.get("total_revenue", 0)
                )

                units = float(
                    summary.get("total_units", 0)
                )

                records = float(
                    summary.get("sales_records", 0)
                )

                return (
                    "### 💰 Overall Sales\n\n"
                    f"- Total revenue: **₹{revenue:,.2f}**\n"
                    f"- Total units sold: **{units:,.0f}**\n"
                    f"- Sales records: **{records:,.0f}**"
                )

            except Exception as e:

                return (
                    f"Unable to calculate total sales: {e}"
                )

        # =====================================================
        # 7. TOP / BEST SELLING PRODUCTS
        # =====================================================

        if (
            "top products" in q
            or "best selling" in q
            or "best-selling" in q
            or "top selling" in q
            or "top-selling" in q
        ):

            try:

                top = self.analytics.top_products(5)

                if top.empty:

                    return "No product sales data available."

                answer = "### 🏆 Top-Selling Products\n\n"

                for i, (_, row) in enumerate(
                    top.iterrows(),
                    start=1
                ):

                    answer += (
                        f"{i}. **{row['product_name']}** — "
                        f"{row['units_sold']:,.0f} units, "
                        f"₹{row['revenue']:,.2f}\n"
                    )

                return answer

            except Exception as e:

                return (
                    f"Unable to identify top products: {e}"
                )

        # =====================================================
        # 8. STORE PERFORMANCE
        # =====================================================

        if (
            "store performance" in q
            or "store sales" in q
            or "stores performing" in q
            or "store performance" in q
        ):

            try:

                stores = self.analytics.sales_by_store()

                if stores.empty:

                    return "No store sales data available."

                answer = "### 🏬 Store Performance\n\n"

                for _, row in stores.iterrows():

                    answer += (
                        f"**{row['store_id']}** — "
                        f"₹{row.get('revenue', 0):,.2f}, "
                        f"{row.get('units_sold', 0):,.0f} units\n"
                    )

                return answer

            except Exception as e:

                return (
                    f"Unable to analyze store performance: {e}"
                )

        # =====================================================
        # 9. STOCK-OUT RISK
        # =====================================================

        if (
            "stockout risk" in q
            or "stock-out risk" in q
            or "stock out risk" in q
            or "stockout" in q
            or "stock-out" in q
            or "running out" in q
        ):

            try:

                stockout = self.inventory.stockout_risk()

                if stockout.empty:

                    return "✅ No stock-out risks detected."

                high_risk = stockout[
                    stockout["risk_level"]
                    .astype(str)
                    .str.upper()
                    == "HIGH"
                ].copy()

                answer = (
                    "### ⚠️ Stock-Out Risk\n\n"
                    f"Total risk records: **{len(stockout)}**\n"
                    f"HIGH-risk records: **{len(high_risk)}**\n\n"
                )

                if not high_risk.empty:

                    urgent = high_risk.sort_values(
                        "days_of_inventory"
                    ).head(5)

                    answer += "**Most urgent items:**\n\n"

                    for _, row in urgent.iterrows():

                        answer += (
                            f"- **{row['product_name']}** "
                            f"(Store {row['store_id']}) — "
                            f"**{row['days_of_inventory']:.2f} days** "
                            f"of inventory\n"
                        )

                return answer

            except Exception as e:

                return (
                    f"Unable to analyze stock-out risk: {e}"
                )

        # =====================================================
        # 10. OVERSTOCK / SLOW MOVING
        # =====================================================

        if (
            "overstock" in q
            or "slow moving" in q
            or "slow-moving" in q
            or "dead stock" in q
        ):

            try:

                overstock = self.inventory.overstock()

                if overstock.empty:

                    return (
                        "### 📦 Overstock\n\n"
                        "No overstock or slow-moving "
                        "inventory was detected."
                    )

                answer = (
                    "### 📦 Overstock / Slow-Moving Inventory\n\n"
                    f"Records found: **{len(overstock)}**\n\n"
                )

                for _, row in overstock.head(10).iterrows():

                    answer += (
                        f"- **{row.get('product_name', 'Unknown')}** — "
                        f"Stock: "
                        f"{row.get('stock_quantity', 0):,.0f}\n"
                    )

                return answer

            except Exception as e:

                return (
                    f"Unable to analyze overstock: {e}"
                )

        # =====================================================
        # 11. SALES SPIKES
        # =====================================================

        if (
            "sales spike" in q
            or "sales spikes" in q
            or "spike in sales" in q
            or "sales increased" in q
            or "sales increase" in q
        ):

            try:

                spikes = self.sales.sales_spikes()

                if spikes.empty:

                    return "No significant sales spikes detected."

                answer = (
                    "### 📈 Sales Spikes\n\n"
                    f"Detected spikes: **{len(spikes)}**\n\n"
                )

                for _, row in spikes.head(10).iterrows():

                    answer += (
                        f"- **{row['product_name']}** — "
                        f"{row['sales_change_percent']:.2f}% increase "
                        f"({row['previous_units']:,.0f} → "
                        f"{row['current_units']:,.0f} units)\n"
                    )

                return answer

            except Exception as e:

                return (
                    f"Unable to analyze sales spikes: {e}"
                )

        # =====================================================
        # 12. SALES DROPS
        # =====================================================

        if (
            "sales drop" in q
            or "sales drops" in q
            or "sales decline" in q
            or "sales declines" in q
            or "sales decreased" in q
            or "sales decrease" in q
        ):

            try:

                drops = self.sales.sales_drops()

                if drops.empty:

                    return "✅ No significant sales drops detected."

                answer = (
                    "### 📉 Sales Drops\n\n"
                    f"Detected drops: **{len(drops)}**\n\n"
                )

                for _, row in drops.head(10).iterrows():

                    answer += (
                        f"- **{row['product_name']}** — "
                        f"{row['sales_change_percent']:.2f}% change "
                        f"({row['previous_units']:,.0f} → "
                        f"{row['current_units']:,.0f} units)\n"
                    )

                return answer

            except Exception as e:

                return (
                    f"Unable to analyze sales drops: {e}"
                )

        # =====================================================
        # 13. URGENT REORDER
        # =====================================================

        if (
            "urgent reorder" in q
            or "urgent reorders" in q
            or "products need reorder" in q
            or "products to reorder" in q
            or "what should i reorder" in q
            or "what products should i reorder" in q
            or "which products need reorder" in q
        ):

            try:

                stockout = self.inventory.stockout_risk()

                high_risk = stockout[
                    stockout["risk_level"]
                    .astype(str)
                    .str.upper()
                    == "HIGH"
                ].copy()

                if high_risk.empty:

                    return (
                        "### ✅ Urgent Reorder\n\n"
                        "No HIGH-risk products currently "
                        "require urgent reorder."
                    )

                high_risk = high_risk.sort_values(
                    "days_of_inventory"
                ).head(10)

                answer = (
                    "### 🚨 Products Needing Urgent Reorder\n\n"
                )

                for _, row in high_risk.iterrows():

                    answer += (
                        f"**{row['product_name']}** — "
                        f"Store {row['store_id']}\n"
                        f"- Stock: "
                        f"{row['stock_quantity']:,.0f} units\n"
                        f"- Daily sales: "
                        f"{row['avg_daily_sales']:.2f}\n"
                        f"- Days left: "
                        f"{row['days_of_inventory']:.2f}\n"
                        f"- Action: "
                        f"{row['recommended_action']}\n\n"
                    )

                return answer

            except Exception as e:

                return (
                    f"Unable to identify urgent reorders: {e}"
                )

        # =====================================================
        # 14. UNKNOWN QUESTION
        # =====================================================

        return (
            "I couldn't answer that from the available retail data.\n\n"
            "Try one of these questions:\n\n"
            "• What are my total sales?\n"
            "• Which products need urgent reorder?\n"
            "• Which store has the most stock-out risk?\n"
            "• Which product generates the most revenue?\n"
            "• Compare S001 and S002\n"
            "• What is my biggest business risk?\n"
            "• Why are sales dropping for iPhone 15?\n"
            "• What are today's priorities?\n"
            "• Show me the top-selling products\n"
            "• Show me sales spikes\n"
            "• Show me sales drops\n"
            "• Show me overstock"
        )