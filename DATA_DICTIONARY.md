# Inventory ML Data Dictionary

The project uses a SQLite database containing purchase, pricing, vendor-invoice and inventory tables. Training scripts derive model-ready features from these tables.

## Main modeling fields

| Field | Use |
|---|---|
| Dollars | Invoice / purchase amount |
| Quantity | Purchased quantity |
| VendorNumber | Vendor identifier |
| Freight | Regression target for freight-cost prediction |
| PODate | Purchase-order date |
| InvoiceDate | Invoice date |
| days_po_to_invoice | Engineered PO-to-invoice delay |
| po_month | Engineered PO month |
| po_day_of_week | Engineered PO weekday |

`data.db` is intentionally excluded from GitHub because it is a large local dataset. Place it at the project root before running the training scripts.
