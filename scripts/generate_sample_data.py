"""Generate a tiny, deterministic, SYNTHETIC sample shaped like the three source datasets.

The files are written to ``data/sample/`` so the ingestion pipeline can be demonstrated and
tested without downloading M5, DataCo or Olist. Column names mirror the public files; every
value is invented. This is NOT real data and must never be presented as such.

Usage:
    python scripts/generate_sample_data.py [--out data/sample] [--seed 42]
"""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

M5_DAYS = 28
M5_STORES = [("CA_1", "CA"), ("CA_2", "CA"), ("WI_1", "WI")]
M5_ITEMS = [
    ("FOODS_1_001", "FOODS_1", "FOODS"),
    ("FOODS_1_002", "FOODS_1", "FOODS"),
    ("FOODS_2_001", "FOODS_2", "FOODS"),
    ("HOUSEHOLD_1_001", "HOUSEHOLD_1", "HOUSEHOLD"),
    ("HOUSEHOLD_1_002", "HOUSEHOLD_1", "HOUSEHOLD"),
    ("HOBBIES_1_001", "HOBBIES_1", "HOBBIES"),
]
OLIST_CATEGORIES = {
    "beleza_saude": "health_beauty",
    "informatica_acessorios": "computers_accessories",
    "esporte_lazer": "sports_leisure",
    "brinquedos": "toys",
}
DATACO_HEADER = (
    "Type,Days for shipping (real),Days for shipment (scheduled),Benefit per order,Sales per customer,"
    "Delivery Status,Late_delivery_risk,Category Id,Category Name,Customer City,Customer Country,"
    "Customer Email,Customer Fname,Customer Id,Customer Lname,Customer Password,Customer Segment,"
    "Customer State,Customer Street,Customer Zipcode,Department Name,Latitude,Longitude,Market,"
    "Order City,Order Country,order date (DateOrders),Order Id,Order Item Discount,Order Item Id,"
    "Order Item Product Price,Order Item Profit Ratio,Order Item Quantity,Sales,Order Item Total,"
    "Order Region,Order State,Order Status,Product Card Id,Product Category Id,Product Description,"
    "Product Image,Product Name,Product Price,Product Status,shipping date (DateOrders),Shipping Mode"
)


def _write(path: Path, text: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").encode(encoding))


def make_m5(out: Path, rng: random.Random) -> None:
    start = datetime(2016, 1, 1)
    days = [f"d_{i}" for i in range(1, M5_DAYS + 1)]
    sales = ["id,item_id,dept_id,cat_id,store_id,state_id," + ",".join(days)]
    for item, dept, cat in M5_ITEMS:
        for store, state in M5_STORES:
            units = ",".join(str(max(0, int(rng.gauss(3, 2)))) for _ in days)
            sales.append(f"{item}_{store}_validation,{item},{dept},{cat},{store},{state},{units}")
    _write(out / "m5" / "sales_train_validation.csv", "\n".join(sales) + "\n")

    cal = [
        "date,wm_yr_wk,weekday,wday,month,year,d,event_name_1,event_type_1,event_name_2,"
        "event_type_2,snap_CA,snap_TX,snap_WI"
    ]
    for i in range(M5_DAYS):
        day = start + timedelta(days=i)
        wk = 11600 + i // 7
        snap = 1 if day.day <= 10 else 0
        cal.append(
            f"{day:%Y-%m-%d},{wk},{day:%A},{(day.weekday() + 2) % 7 + 1},{day.month},"
            f"{day.year},d_{i + 1},,,,,{snap},0,{snap}"
        )
    _write(out / "m5" / "calendar.csv", "\n".join(cal) + "\n")

    prices = ["store_id,item_id,wm_yr_wk,sell_price"]
    for item, _, _ in M5_ITEMS:
        base = round(rng.uniform(1.0, 9.0), 2)
        for store, _ in M5_STORES:
            for wk in range(11600, 11600 + M5_DAYS // 7):
                prices.append(f"{store},{item},{wk},{base:.2f}")
    _write(out / "m5" / "sell_prices.csv", "\n".join(prices) + "\n")


def make_olist(out: Path, rng: random.Random) -> None:
    base = out / "olist"
    cats = list(OLIST_CATEGORIES)
    products = [
        "product_id,product_category_name,product_name_lenght,product_description_lenght,"
        "product_photos_qty,product_weight_g,product_length_cm,product_height_cm,product_width_cm"
    ]
    for i in range(1, 9):
        products.append(
            f"p{i},{cats[i % len(cats)]},{rng.randint(20, 60)},{rng.randint(100, 900)},"
            f"{rng.randint(1, 5)},{rng.randint(100, 3000)},{rng.randint(10, 40)},"
            f"{rng.randint(5, 25)},{rng.randint(5, 30)}"
        )
    _write(base / "olist_products_dataset.csv", "\n".join(products) + "\n")

    customers = ["customer_id,customer_unique_id,customer_zip_code_prefix,customer_city,customer_state"]
    for i in range(1, 16):
        customers.append(f"c{i},u{i},{1000 * i:05d},sao paulo,SP")
    _write(base / "olist_customers_dataset.csv", "\n".join(customers) + "\n")

    sellers = ["seller_id,seller_zip_code_prefix,seller_city,seller_state"]
    for i in range(1, 4):
        sellers.append(f"s{i},{4000 + i:05d},curitiba,PR")
    _write(base / "olist_sellers_dataset.csv", "\n".join(sellers) + "\n")

    translation = ["product_category_name,product_category_name_english"]
    translation += [f"{pt},{en}" for pt, en in OLIST_CATEGORIES.items()]
    _write(base / "product_category_name_translation.csv", "\n".join(translation) + "\n")

    orders = [
        "order_id,customer_id,order_status,order_purchase_timestamp,order_approved_at,"
        "order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date"
    ]
    items = ["order_id,order_item_id,product_id,seller_id,shipping_limit_date,price,freight_value"]
    t0 = datetime(2018, 1, 1, 9, 0, 0)
    for i in range(1, 21):
        purchase = t0 + timedelta(hours=7 * i)
        approved = purchase + timedelta(minutes=10)
        carrier = purchase + timedelta(days=1)
        estimated = purchase + timedelta(days=9)
        delivered = purchase + timedelta(days=rng.randint(4, 13))
        status = "delivered" if i % 10 else "shipped"
        delivered_s = f"{delivered:%Y-%m-%d %H:%M:%S}" if status == "delivered" else ""
        orders.append(
            f"o{i},c{(i % 15) + 1},{status},{purchase:%Y-%m-%d %H:%M:%S},{approved:%Y-%m-%d %H:%M:%S},"
            f"{carrier:%Y-%m-%d %H:%M:%S},{delivered_s},{estimated:%Y-%m-%d %H:%M:%S}"
        )
        for line in range(1, rng.randint(1, 2) + 1):
            items.append(
                f"o{i},{line},p{rng.randint(1, 8)},s{rng.randint(1, 3)},"
                f"{carrier:%Y-%m-%d %H:%M:%S},{rng.uniform(10, 150):.2f},{rng.uniform(5, 25):.2f}"
            )
    _write(base / "olist_orders_dataset.csv", "\n".join(orders) + "\n")
    _write(base / "olist_order_items_dataset.csv", "\n".join(items) + "\n")


def make_dataco(out: Path, rng: random.Random) -> None:
    rows = [DATACO_HEADER]
    products = [
        (365, "Synthetic Fitness Item", "Sporting Goods", 59.99),
        (403, "Caf\u00e9 Synthetic Footwear", "Cleats", 129.99),
        (502, "Synthetic Running Shoe", "Men's Footwear", 50.00),
    ]
    statuses = ["Shipping on time", "Late delivery", "Advance shipping"]
    for n in range(1, 21):
        pid, pname, cat, price = products[n % len(products)]
        sched = rng.randint(2, 4)
        real = rng.randint(1, 6)
        status = statuses[0] if real == sched else statuses[1] if real > sched else statuses[2]
        risk = 1 if real > sched else 0
        qty = rng.randint(1, 3)
        sales = round(price * qty, 2)
        order = datetime(2018, 1, 1) + timedelta(days=n)
        ship = order + timedelta(days=real)
        rows.append(
            f"DEBIT,{real},{sched},10.5,{sales},{status},{risk},1,{cat},Caguas,Puerto Rico,"
            f"XXXXXXXXX,Synthetic,{n},Person,XXXXXXXXX,Consumer,PR,Main St 1,725,Fitness,18.2,-66.0,"
            f"LATAM,Bekasi,Indonesia,{order:%m/%d/%Y %H:%M},{1000 + n},5.0,{n},{price},0.1,{qty},"
            f"{sales},{sales},Southeast Asia,Java,COMPLETE,{pid},9,,,{pname},{price},0,"
            f"{ship:%m/%d/%Y %H:%M},Standard Class"
        )
    _write(out / "dataco" / "DataCoSupplyChainDataset.csv", "\n".join(rows) + "\n", "latin-1")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic sample CSVs")
    parser.add_argument("--out", default="data/sample", type=Path)
    parser.add_argument("--seed", default=42, type=int)
    args = parser.parse_args(argv)
    rng = random.Random(args.seed)
    make_m5(args.out, rng)
    make_olist(args.out, rng)
    make_dataco(args.out, rng)
    print(f"Synthetic sample data written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
