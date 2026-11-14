# Regional Market Transaction Data Collection

## 1. Project Overview

This project uses simulated regional market transaction data to understand market behaviour, product pricing and sales performance. The dataset is used for data preparation, cleaning and business analytics.

## 2. Dataset Description

The dataset covers 20 regional markets and 12 products during January 2024 to December 2024.

It contains daily observations of market and product transactions.

## 3. Dataset Files

The project contains three main data files:

- regional_market_transactions.csv
- market_metadata.csv
- product_metadata.csv

## 4. Important Data Fields

The transaction dataset contains the following fields:

- Date
- Market ID
- Product ID
- Price
- Competitor Price
- Promotion
- Units Sold
- Revenue
- Treated Market
- Treatment Date
- Treatment
- Region
- Unit Cost
- Gross Profit

## 5. Simulated Pricing Intervention

The dataset includes a simulated price intervention. Four markets receive an 8% price increase starting from 1 July 2024.

Promotions, seasonality, market size and some missing values are also included to support data analysis and quality checks.

## 6. Data Storage

The original datasets are stored in the `data/raw` folder.

The cleaned datasets are stored separately in the `data/processed` folder.

This structure helps maintain the original data and makes it easier to manage the processed data.

## 7. Data Limitations

The dataset contains simulated development data. It does not represent actual company transactions or verified real-world market results.

All analysis and findings based on this dataset must be presented as simulated results.

## 8. Purpose of Data Collection

The dataset provides a foundation for data cleaning, data validation, exploratory data analysis, product pricing analysis and further causal modelling.