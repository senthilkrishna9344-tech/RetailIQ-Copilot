import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# -----------------------------
# 1. STORES
# -----------------------------
stores = [
    ["S001", "Chennai Central", "Chennai"],
    ["S002", "Coimbatore Mall", "Coimbatore"],
    ["S003", "Bangalore City", "Bangalore"],
]

with open(DATA_DIR / "stores.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["store_id", "store_name", "city"])
    writer.writerows(stores)


# -----------------------------
# 2. PRODUCTS
# -----------------------------
products = [
    ["P001", "iPhone 15", "Smartphones", 69999, 58000, "Supplier A"],
    ["P002", "Samsung Galaxy S24", "Smartphones", 74999, 61000, "Supplier B"],
    ["P003", "OnePlus 12", "Smartphones", 59999, 49000, "Supplier C"],
    ["P004", "Redmi Note 13", "Smartphones", 18999, 14500, "Supplier D"],
    ["P005", "MacBook Air M3", "Laptops", 114999, 97000, "Supplier A"],
    ["P006", "Dell Inspiron", "Laptops", 65999, 54000, "Supplier B"],
    ["P007", "HP Pavilion", "Laptops", 62999, 51000, "Supplier C"],
    ["P008", "Lenovo IdeaPad", "Laptops", 55999, 45000, "Supplier D"],
    ["P009", "Samsung 55 TV", "Television", 64999, 52000, "Supplier A"],
    ["P010", "LG 43 TV", "Television", 44999, 36000, "Supplier B"],
    ["P011", "Sony Bluetooth Speaker", "Audio", 8999, 6500, "Supplier C"],
    ["P012", "JBL Headphones", "Audio", 5999, 4200, "Supplier D"],
    ["P013", "Apple AirPods", "Audio", 14999, 11000, "Supplier A"],
    ["P014", "Nike Air Max", "Footwear", 12999, 8500, "Supplier B"],
    ["P015", "Adidas Running Shoes", "Footwear", 9999, 6500, "Supplier C"],
    ["P016", "Puma Sneakers", "Footwear", 7999, 5200, "Supplier D"],
    ["P017", "Levi's Jeans", "Clothing", 4999, 3000, "Supplier A"],
    ["P018", "Allen Solly Shirt", "Clothing", 2999, 1800, "Supplier B"],
    ["P019", "Wildcraft Backpack", "Accessories", 3499, 2200, "Supplier C"],
    ["P020", "Casio Watch", "Accessories", 4999, 3200, "Supplier D"],
]

with open(DATA_DIR / "products.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "product_id",
        "product_name",
        "category",
        "price",
        "cost",
        "supplier"
    ])
    writer.writerows(products)


# -----------------------------
# 3. SALES
# -----------------------------
start_date = date.today() - timedelta(days=89)

sales_rows = []

for day_number in range(90):
    current_date = start_date + timedelta(days=day_number)

    for store_id, _, _ in stores:
        for product in products:
            product_id = product[0]
            price = product[3]

            # Different products have different demand
            base_demand = random.randint(1, 8)

            # Create some realistic sales trends
            if product_id in ["P001", "P005", "P013"]:
                base_demand += 4

            if product_id in ["P018", "P020"]:
                base_demand = max(0, base_demand - 2)

            # Weekend boost
            if current_date.weekday() >= 5:
                base_demand = int(base_demand * 1.25)

            quantity = max(0, int(random.gauss(base_demand, 1.5)))

            if quantity > 0:
                revenue = quantity * price

                sales_rows.append([
                    current_date.isoformat(),
                    store_id,
                    product_id,
                    quantity,
                    price,
                    revenue
                ])

with open(DATA_DIR / "sales.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "date",
        "store_id",
        "product_id",
        "quantity",
        "unit_price",
        "revenue"
    ])
    writer.writerows(sales_rows)


# -----------------------------
# 4. INVENTORY
# -----------------------------
inventory_rows = []

# Initial stock for every store/product
stock = {}

for store_id, _, _ in stores:
    for product in products:
        product_id = product[0]

        # Some products intentionally start with low stock
        if product_id in ["P001", "P014", "P009"]:
            initial_stock = random.randint(10, 25)
        elif product_id in ["P018", "P020"]:
            initial_stock = random.randint(80, 140)
        else:
            initial_stock = random.randint(30, 100)

        stock[(store_id, product_id)] = initial_stock


for day_number in range(90):
    current_date = start_date + timedelta(days=day_number)

    for store_id, _, _ in stores:
        for product in products:
            product_id = product[0]

            # Approximate daily sales
            daily_sales = random.randint(0, 7)

            # High-demand products sell faster
            if product_id in ["P001", "P005", "P013"]:
                daily_sales += random.randint(2, 5)

            stock[(store_id, product_id)] -= daily_sales

            # Replenishment
            if stock[(store_id, product_id)] < 10:
                if product_id in ["P001", "P014", "P009"]:
                    # Keep these relatively low to create stock-out alerts
                    stock[(store_id, product_id)] += random.randint(5, 15)
                else:
                    stock[(store_id, product_id)] += random.randint(25, 60)

            stock[(store_id, product_id)] = max(
                0, stock[(store_id, product_id)]
            )

            inventory_rows.append([
                current_date.isoformat(),
                store_id,
                product_id,
                stock[(store_id, product_id)]
            ])


with open(DATA_DIR / "inventory.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "date",
        "store_id",
        "product_id",
        "stock_quantity"
    ])
    writer.writerows(inventory_rows)


print("====================================")
print("RetailIQ dataset created successfully!")
print("====================================")
print(f"Products : {len(products)}")
print(f"Stores   : {len(stores)}")
print(f"Sales rows      : {len(sales_rows)}")
print(f"Inventory rows  : {len(inventory_rows)}")
print()
print("Files created inside:")
print(DATA_DIR)