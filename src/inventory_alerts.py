import pandas as pd
from pathlib import Path


class InventoryAlerts:

    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "data"

        self.products = pd.read_csv(data_dir / "products.csv")
        self.sales = pd.read_csv(data_dir / "sales.csv")
        self.inventory = pd.read_csv(data_dir / "inventory.csv")

        self.sales["date"] = pd.to_datetime(self.sales["date"])
        self.inventory["date"] = pd.to_datetime(self.inventory["date"])

    def calculate_inventory_metrics(self):

        # Latest inventory date
        latest_date = self.inventory["date"].max()

        current_stock = self.inventory[
            self.inventory["date"] == latest_date
        ].copy()

        # Average daily sales for each store/product
        daily_sales = (
            self.sales
            .groupby(["store_id", "product_id", "date"])
            ["quantity"]
            .sum()
            .reset_index()
        )

        avg_sales = (
            daily_sales
            .groupby(["store_id", "product_id"])
            ["quantity"]
            .mean()
            .reset_index()
        )

        avg_sales.rename(
            columns={"quantity": "avg_daily_sales"},
            inplace=True
        )

        result = current_stock.merge(
            avg_sales,
            on=["store_id", "product_id"],
            how="left"
        )

        result = result.merge(
            self.products[
                [
                    "product_id",
                    "product_name",
                    "category",
                    "price"
                ]
            ],
            on="product_id",
            how="left"
        )

        result["avg_daily_sales"] = result[
            "avg_daily_sales"
        ].fillna(0)

        # Avoid division by zero
        result["days_of_inventory"] = result.apply(
            lambda row:
                row["stock_quantity"] / row["avg_daily_sales"]
                if row["avg_daily_sales"] > 0
                else 999,
            axis=1
        )

        return result

    # ---------------------------------
    # STOCK-OUT RISK
    # ---------------------------------

    def stockout_risk(self):

        data = self.calculate_inventory_metrics()

        risk = data[
            (data["avg_daily_sales"] > 0) &
            (data["days_of_inventory"] <= 7)
        ].copy()

        risk["risk_level"] = risk[
            "days_of_inventory"
        ].apply(
            lambda x:
                "HIGH" if x <= 3
                else "MEDIUM"
        )

        risk["recommended_action"] = (
            "Reorder stock"
        )

        return risk.sort_values(
            "days_of_inventory"
        )

    # ---------------------------------
    # OVERSTOCK
    # ---------------------------------

    def overstock(self):

        data = self.calculate_inventory_metrics()

        result = data[
            (data["days_of_inventory"] >= 30) &
            (data["stock_quantity"] > 20)
        ].copy()

        result["risk_level"] = "OVERSTOCK"

        result["recommended_action"] = (
            "Consider promotion or reduce future orders"
        )

        return result.sort_values(
            "days_of_inventory",
            ascending=False
        )

    # ---------------------------------
    # DAILY PRIORITIES
    # ---------------------------------

    def daily_priorities(self):

        stockout = self.stockout_risk()
        overstock = self.overstock()

        print("\n========== TODAY'S PRIORITIES ==========\n")

        if stockout.empty:
            print("No immediate stock-out risks.")
        else:
            print(" STOCK-OUT RISKS")

            for _, row in stockout.head(5).iterrows():

                print(
                    f"{row['product_name']} | "
                    f"Store: {row['store_id']} | "
                    f"Stock: {int(row['stock_quantity'])} | "
                    f"Daily sales: "
                    f"{row['avg_daily_sales']:.2f} | "
                    f"Days left: "
                    f"{row['days_of_inventory']:.1f}"
                )

        print("\n OVERSTOCK")

        if overstock.empty:
            print("No major overstock detected.")
        else:
            for _, row in overstock.head(5).iterrows():

                print(
                    f"{row['product_name']} | "
                    f"Store: {row['store_id']} | "
                    f"Stock: {int(row['stock_quantity'])} | "
                    f"Days of inventory: "
                    f"{row['days_of_inventory']:.1f}"
                )


# ---------------------------------
# TEST
# ---------------------------------

if __name__ == "__main__":

    alerts = InventoryAlerts()

    print("\n========== STOCK-OUT RISK ==========\n")

    print(
        alerts.stockout_risk()
        [
            [
                "store_id",
                "product_name",
                "stock_quantity",
                "avg_daily_sales",
                "days_of_inventory",
                "risk_level"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\n========== OVERSTOCK ==========\n")

    print(
        alerts.overstock()
        [
            [
                "store_id",
                "product_name",
                "stock_quantity",
                "avg_daily_sales",
                "days_of_inventory",
                "risk_level"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    alerts.daily_priorities()