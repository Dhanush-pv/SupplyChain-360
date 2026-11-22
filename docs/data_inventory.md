# Week 1 Data Inventory

Licences and attribution are in [`dataset_licenses.md`](dataset_licenses.md). The synthetic files in `data/sample/` are **not** listed here because they are not source data.

Fill this document after downloading the datasets and running ingestion. Values must come from the actual files and manifest; do not estimate them.

| Source | File | Local size | SHA-256 | Columns | Sample rows inspected | Notes / quality observations |
|---|---|---:|---|---:|---:|---|
| M5 | `sales_train_validation.csv` | Pending | Pending | Pending | Pending | Pending |
| M5 | `calendar.csv` | Pending | Pending | Pending | Pending | Pending |
| M5 | `sell_prices.csv` | Pending | Pending | Pending | Pending | Pending |
| DataCo | `DataCoSupplyChainDataset.csv` | Pending | Pending | Pending | Pending | Pending |
| Olist | `olist_orders_dataset.csv` | Pending | Pending | Pending | Pending | Pending |
| Olist | `olist_order_items_dataset.csv` | Pending | Pending | Pending | Pending | Pending |
| Olist | Remaining Olist CSVs | Pending | Pending | Pending | Pending | Pending |

## Source-level decisions

Record actual dataset version/date, download URL, license/terms checked, attribution, encoding, delimiter, date formats and any known limitations.

## Open questions for Week 2

- Which source fields can serve as stable product, order, seller and customer identifiers?
- Which source identifiers are incompatible and require mapping tables?
- Which datasets overlap in business meaning but not in grain or coverage?
- Which timestamps are local time versus UTC, and what timezone assumptions are documented?
- Which fields have high missingness, invalid values or duplicate keys?
