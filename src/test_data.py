import pandas as pd
from pathlib import Path

# -----------------------------
# Project Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# -----------------------------
# Load Data
# -----------------------------
products = pd.read_csv(DATA_DIR / "products.csv")
stores = pd.read_csv(DATA_DIR / "stores.csv")
sales = pd.read_csv(DATA_DIR / "sales.csv")
inventory = pd.read_csv(DATA_DIR / "inventory.csv")


print("\n========== DATASET TEST ==========\n")


# -----------------------------
# PRODUCTS
# -----------------------------
print("PRODUCTS")
print(products.head())

print("\nNumber of products:", len(products))


# -----------------------------
# STORES
# -----------------------------
print("\nSTORES")
print(stores.head())

print("\nNumber of stores:", len(stores))


# -----------------------------
# SALES
# -----------------------------
print("\nSALES")
print(sales.head())

print("\nNumber of sales records:", len(sales))


# -----------------------------
# INVENTORY
# -----------------------------
print("\nINVENTORY")
print(inventory.head())

print("\nNumber of inventory records:", len(inventory))


# -----------------------------
# COLUMNS
# -----------------------------
print("\n========== COLUMNS ==========\n")

print("Products:", list(products.columns))
print("Stores:", list(stores.columns))
print("Sales:", list(sales.columns))
print("Inventory:", list(inventory.columns))


# -----------------------------
# BASIC CHECKS
# -----------------------------
print("\n========== BASIC CHECKS ==========\n")

# Total revenue
total_revenue = sales["revenue"].sum()

# Total units sold
total_units = sales["quantity"].sum()

# Average revenue per unit
average_revenue_per_unit = (
    total_revenue / total_units
)

# Latest inventory date
latest_date = inventory["date"].max()

# Current stock based on latest date
current_total_stock = inventory[
    inventory["date"] == latest_date
]["stock_quantity"].sum()


# -----------------------------
# Display Results
# -----------------------------
print(f"Total Revenue: ₹{total_revenue:,.2f}")

print(f"Total Units Sold: {total_units:,}")

print(
    f"Average Revenue Per Unit: "
    f"₹{average_revenue_per_unit:,.2f}"
)

print(f"Latest Inventory Date: {latest_date}")

print(
    f"Current Total Stock: "
    f"{current_total_stock:,}"
)


# -----------------------------
# Final Message
# -----------------------------
print("\nDataset test completed successfully!")