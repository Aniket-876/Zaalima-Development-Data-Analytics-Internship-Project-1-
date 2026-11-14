# Market and Product Dataset Structure

## 1. Introduction

The project dataset is organized into three CSV files to support regional market analysis and product pricing analysis. Each file has a specific purpose and contributes to the overall analysis.

## 2. Dataset Organization

| File Name | Purpose |
|---|---|
| regional_market_transactions.csv | Contains daily market and product transaction observations |
| market_metadata.csv | Contains information about the regional markets |
| product_metadata.csv | Contains information about products and their baseline pricing and demand |

## 3. Transaction Dataset Structure

The regional market transaction dataset includes the following fields:

| Field | Description |
|---|---|
| date | Date of the transaction observation |
| market_id | Unique identifier for a market |
| product_id | Unique identifier for a product |
| price | Product selling price |
| competitor_price | Competitor's product price |
| promotion | Promotion information |
| units_sold | Number of units sold |
| revenue | Revenue generated |
| treated_market | Indicates whether a market receives the simulated intervention |
| treatment_date | Date of the simulated intervention |
| treatment | Treatment indicator |
| region | Regional classification |
| unit_cost | Cost per product unit |
| gross_profit | Gross profit generated |

## 4. Market Metadata

The market metadata file provides supporting information about the regional markets. It helps organize transaction observations according to their respective markets.

## 5. Product Metadata

The product metadata file provides supporting product information, including baseline price and demand details. It helps in understanding product-level pricing and sales patterns.

## 6. Dataset Relationship

The transaction dataset connects market and product information through the market_id and product_id fields.

This structure allows the transaction data to be analyzed alongside the corresponding market and product metadata.

## 7. Data Storage Structure

- Raw datasets are maintained in the data/raw folder.
- Cleaned datasets are maintained in the data/processed folder.
- Supporting documentation is maintained in the docs folder.

## 8. Conclusion

The organized dataset structure provides a foundation for data cleaning, validation, pricing analysis and further exploratory analysis. Keeping transaction, market and product information organized separately improves project clarity and data management.