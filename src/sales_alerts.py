import pandas as pd
from pathlib import Path


class SalesAlerts:

    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        data_dir = base_dir / "data"

        self.products = pd.read_csv(data_dir / "products.csv")
        self.sales = pd.read_csv(data_dir / "sales.csv")

        self.sales["date"] = pd.to_datetime(self.sales["date"])

    # --------------------------------
    # PRODUCT SALES TREND
    # --------------------------------

    def sales_trends(self):

        latest_date = self.sales["date"].max()

        # Last 30 days
        current_start = latest_date - pd.Timedelta(days=29)

        # Previous 30 days
        previous_end = current_start - pd.Timedelta(days=1)
        previous_start = previous_end - pd.Timedelta(days=29)

        current = self.sales[
            (self.sales["date"] >= current_start) &
            (self.sales["date"] <= latest_date)
        ]

        previous = self.sales[
            (self.sales["date"] >= previous_start) &
            (self.sales["date"] <= previous_end)
        ]

        current_sales = (
            current
            .groupby("product_id")
            .agg(
                current_units=("quantity", "sum"),
                current_revenue=("revenue", "sum")
            )
            .reset_index()
        )

        previous_sales = (
            previous
            .groupby("product_id")
            .agg(
                previous_units=("quantity", "sum"),
                previous_revenue=("revenue", "sum")
            )
            .reset_index()
        )

        result = current_sales.merge(
            previous_sales,
            on="product_id",
            how="outer"
        ).fillna(0)

        result = result.merge(
            self.products[
                ["product_id", "product_name", "category"]
            ],
            on="product_id",
            how="left"
        )

        # Percentage change
        result["sales_change_percent"] = result.apply(
            lambda row:
                (
                    (row["current_units"] -
                     row["previous_units"])
                    / row["previous_units"]
                ) * 100
                if row["previous_units"] > 0
                else 100,
            axis=1
        )

        return result.sort_values(
            "sales_change_percent",
            ascending=False
        )

    # --------------------------------
    # SALES SPIKES
    # --------------------------------

    def sales_spikes(self):

        trends = self.sales_trends()

        return trends[
            trends["sales_change_percent"] >= 25
        ].copy()

    # --------------------------------
    # SALES DROPS
    # --------------------------------

    def sales_drops(self):

        trends = self.sales_trends()

        return trends[
            trends["sales_change_percent"] <= -20
        ].copy()

    # --------------------------------
    # SUMMARY
    # --------------------------------

    def attention_summary(self):

        spikes = self.sales_spikes()
        drops = self.sales_drops()

        print("\n========== SALES SPIKES ==========\n")

        if spikes.empty:
            print("No significant sales spikes detected.")
        else:
            for _, row in spikes.head(5).iterrows():

                print(
                    f"{row['product_name']} | "
                    f"Current units: {int(row['current_units'])} | "
                    f"Previous units: {int(row['previous_units'])} | "
                    f"Change: {row['sales_change_percent']:.1f}%"
                )

        print("\n========== SALES DROPS ==========\n")

        if drops.empty:
            print("No significant sales drops detected.")
        else:
            for _, row in drops.head(5).iterrows():

                print(
                    f"{row['product_name']} | "
                    f"Current units: {int(row['current_units'])} | "
                    f"Previous units: {int(row['previous_units'])} | "
                    f"Change: {row['sales_change_percent']:.1f}%"
                )


# --------------------------------
# TEST
# --------------------------------

if __name__ == "__main__":

    alerts = SalesAlerts()

    print("\n========== SALES TREND ==========\n")

    print(
        alerts.sales_trends()
        [
            [
                "product_name",
                "category",
                "current_units",
                "previous_units",
                "sales_change_percent"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    alerts.attention_summary()