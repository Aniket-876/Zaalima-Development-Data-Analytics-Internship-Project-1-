# Initial Project Data Dictionary

## 1. Introduction

This data dictionary explains the important fields used in the regional market transaction dataset. It provides a clear understanding of the information available for data preparation and analysis.

## 2. Transaction Dataset Fields

| Field Name | Description | Data Type |
|---|---|---|
| date | Date of the market transaction observation | Date |
| market_id | Unique identification number of the market | Identifier |
| product_id | Unique identification number of the product | Identifier |
| price | Selling price of the product | Numeric |
| competitor_price | Price offered by competitors | Numeric |
| promotion | Indicates promotional activity | Categorical |
| units_sold | Number of product units sold | Numeric |
| revenue | Total revenue generated | Numeric |
| treated_market | Indicates whether the market is assigned to the simulated treatment | Categorical |
| treatment_date | Date of the simulated intervention | Date |
| treatment | Indicates the treatment status | Categorical |
| region | Regional classification of the market | Categorical |
| unit_cost | Cost of one product unit | Numeric |
| gross_profit | Gross profit generated from sales | Numeric |

## 3. Dataset Files

The project uses three main files:

1. regional_market_transactions.csv
2. market_metadata.csv
3. product_metadata.csv

The transaction dataset contains daily market-product observations. The market and product metadata files provide supporting information.

## 4. Important Analytical Fields

The following fields are particularly useful for business analysis:

- Price: Used to study product pricing patterns.
- Competitor Price: Used for competitor price comparisons.
- Units Sold: Used to understand sales volume.
- Revenue: Used to evaluate sales performance.
- Unit Cost: Used to understand product costs.
- Gross Profit: Used to examine profitability.
- Treatment: Used to identify the simulated pricing intervention.

## 5. Data Management

The original files are stored in the data/raw folder, while cleaned files are stored in the data/processed folder.

The data dictionary will help maintain consistency when preparing and analyzing the datasets.

## 6. Note

The dataset contains simulated development data. The descriptions in this dictionary are based on the available project documentation. Additional field details can be updated after examining the complete datasets.