import pandas as pd
from pathlib import Path


class RetailAnalytics:

    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "data"

        self.products = pd.read_csv(data_dir / "products.csv")
        self.stores = pd.read_csv(data_dir / "stores.csv")
        self.sales = pd.read_csv(data_dir / "sales.csv")
        self.inventory = pd.read_csv(data_dir / "inventory.csv")

        self.sales["date"] = pd.to_datetime(self.sales["date"])
        self.inventory["date"] = pd.to_datetime(self.inventory["date"])

    # -----------------------------
    # TOTAL SALES
    # -----------------------------
    def total_sales(self):
        return {
            "total_revenue": round(self.sales["revenue"].sum(), 2),
            "total_units": int(self.sales["quantity"].sum()),
            "sales_records": len(self.sales)
        }

    # -----------------------------
    # TOP PRODUCTS
    # -----------------------------
    def top_products(self, limit=5):

        result = (
            self.sales
            .groupby("product_id")
            .agg(
                units_sold=("quantity", "sum"),
                revenue=("revenue", "sum")
            )
            .reset_index()
        )

        result = result.merge(
            self.products[["product_id", "product_name", "category"]],
            on="product_id"
        )

        result = result.sort_values(
            "revenue",
            ascending=False
        ).head(limit)

        return result

    # -----------------------------
    # SALES BY STORE
    # -----------------------------
    def sales_by_store(self):

        result = (
            self.sales
            .groupby("store_id")
            .agg(
                units_sold=("quantity", "sum"),
                revenue=("revenue", "sum")
            )
            .reset_index()
        )

        result = result.merge(
            self.stores,
            on="store_id"
        )

        return result.sort_values(
            "revenue",
            ascending=False
        )

    # -----------------------------
    # CURRENT INVENTORY
    # -----------------------------
    def current_inventory(self):

        latest_date = self.inventory["date"].max()

        current = self.inventory[
            self.inventory["date"] == latest_date
        ].copy()

        current = current.merge(
            self.products[
                ["product_id", "product_name", "category"]
            ],
            on="product_id"
        )

        current = current.merge(
            self.stores[
                ["store_id", "store_name", "city"]
            ],
            on="store_id"
        )

        return current

    # -----------------------------
    # LOW STOCK PRODUCTS
    # -----------------------------
    def low_stock(self, threshold=15):

        current = self.current_inventory()

        return current[
            current["stock_quantity"] <= threshold
        ].sort_values("stock_quantity")

    # -----------------------------
    # PRODUCT PERFORMANCE
    # -----------------------------
    def product_performance(self, product_name):

        product = self.products[
            self.products["product_name"].str.lower()
            == product_name.lower()
        ]

        if product.empty:
            return None

        product_id = product.iloc[0]["product_id"]

        sales = self.sales[
            self.sales["product_id"] == product_id
        ]

        return {
            "product": product_name,
            "units_sold": int(sales["quantity"].sum()),
            "revenue": round(sales["revenue"].sum(), 2),
            "average_daily_units":
                round(
                    sales.groupby("date")["quantity"]
                    .sum()
                    .mean(),
                    2
                )
        }


# --------------------------------
# TEST THE ANALYTICS ENGINE
# --------------------------------

if __name__ == "__main__":

    analytics = RetailAnalytics()

    print("\n========== RETAIL ANALYTICS ==========\n")

    print("TOTAL SALES")
    print(analytics.total_sales())

    print("\nTOP PRODUCTS")
    print(analytics.top_products().to_string(index=False))

    print("\nSALES BY STORE")
    print(analytics.sales_by_store().to_string(index=False))

    print("\nLOW STOCK")
    print(analytics.low_stock().to_string(index=False))

    print("\nPRODUCT PERFORMANCE")
    print(analytics.product_performance("iPhone 15"))