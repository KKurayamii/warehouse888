# Star Schema Design for E-Commerce Sales Analytics

## Overview

This document describes the Star Schema design for the Smart Sales Analysis System. The schema is optimized for analytical queries in ClickHouse.

## Schema Diagram

```
                    ┌─────────────────┐
                    │  dim_dates      │
                    ├─────────────────┤
                    │ date_id (PK)    │
                    │ date            │
                    │ year            │
                    │ month           │
                    │ day             │
                    │ quarter         │
                    │ day_of_week     │
                    │ month_name      │
                    └─────────────────┘
                            │
                            │
┌─────────────────┐         │         ┌─────────────────┐
│  dim_products   │         │         │  dim_customers  │
├─────────────────┤         │         ├─────────────────┤
│ product_id (PK) │         │         │ customer_id(PK) │
│ sku             │         │         │ customer_name   │
│ product_name    │         │         │ email           │
│ category        │         │         │ phone           │
│ subcategory     │         │         │ location_id(FK) │
│ unit_price      │         │         └─────────────────┘
│ cost            │         │                   │
└─────────────────┘         │                   │
        │                   │                   │
        │                   │                   │
        │         ┌──────────────────────┐      │
        └─────────│   fact_orders        │──────┘
                  ├──────────────────────┤
                  │ order_id (PK)        │
                  │ order_number         │
                  │ date_id (FK)         │
                  │ product_id (FK)      │
                  │ customer_id (FK)     │
                  │ payment_id (FK)      │
                  │ promotion_id (FK)    │
                  │ location_id (FK)     │
                  │ quantity             │
                  │ unit_price           │
                  │ discount_amount      │
                  │ tax_amount           │
                  │ shipping_cost        │
                  │ total_amount         │
                  │ created_at           │
                  └──────────────────────┘
                  │         │         │
        ┌─────────┘         │         └─────────┐
        │                   │                   │
┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐
│  dim_payments   │  │ dim_promotions  │  │ dim_locations│
├─────────────────┤  ├─────────────────┤  ├──────────────┤
│ payment_id (PK) │  │ promotion_id(PK)│  │location_id(PK│
│ payment_method  │  │ promo_code      │  │ province     │
│ payment_gateway │  │ promo_name      │  │ city         │
│ is_online       │  │ discount_type   │  │ district     │
└─────────────────┘  │ discount_value  │  │ postal_code  │
                     │ start_date      │  │ region       │
                     │ end_date        │  └──────────────┘
                     └─────────────────┘
```

## Table Specifications

### Fact Table

#### fact_orders
The central fact table containing order transactions.

| Column | Type | Description |
|--------|------|-------------|
| order_id | UInt64 | Primary key, auto-increment |
| order_number | String | Original order reference number |
| date_id | UInt32 | Foreign key to dim_dates |
| product_id | UInt32 | Foreign key to dim_products |
| customer_id | UInt32 | Foreign key to dim_customers |
| payment_id | UInt16 | Foreign key to dim_payments |
| promotion_id | Nullable(UInt16) | Foreign key to dim_promotions |
| location_id | UInt16 | Foreign key to dim_locations |
| quantity | UInt32 | Number of items ordered |
| unit_price | Decimal(10,2) | Price per unit |
| discount_amount | Decimal(10,2) | Total discount applied |
| tax_amount | Decimal(10,2) | Tax amount |
| shipping_cost | Decimal(10,2) | Shipping/delivery cost |
| total_amount | Decimal(10,2) | Final total amount |
| created_at | DateTime | Order creation timestamp |

**Indexes:** ORDER BY (date_id, product_id, customer_id)

### Dimension Tables

#### dim_products
Product catalog dimension.

| Column | Type | Description |
|--------|------|-------------|
| product_id | UInt32 | Primary key |
| sku | String | Stock Keeping Unit |
| product_name | String | Product name |
| category | String | Main category |
| subcategory | String | Subcategory |
| unit_price | Decimal(10,2) | Standard unit price |
| cost | Decimal(10,2) | Product cost |

#### dim_customers
Customer information dimension.

| Column | Type | Description |
|--------|------|-------------|
| customer_id | UInt32 | Primary key |
| customer_name | String | Customer full name |
| email | String | Email address |
| phone | String | Phone number |
| location_id | UInt16 | Foreign key to dim_locations |
| created_at | DateTime | Customer registration date |

#### dim_dates
Date dimension for time-based analysis.

| Column | Type | Description |
|--------|------|-------------|
| date_id | UInt32 | Primary key (YYYYMMDD format) |
| date | Date | Actual date |
| year | UInt16 | Year |
| month | UInt8 | Month (1-12) |
| day | UInt8 | Day of month |
| quarter | UInt8 | Quarter (1-4) |
| day_of_week | UInt8 | Day of week (1=Monday, 7=Sunday) |
| month_name | String | Month name in Thai/English |
| is_weekend | UInt8 | 1 if weekend, 0 otherwise |
| is_holiday | UInt8 | 1 if holiday, 0 otherwise |

#### dim_payments
Payment method dimension.

| Column | Type | Description |
|--------|------|-------------|
| payment_id | UInt16 | Primary key |
| payment_method | String | Payment method name |
| payment_gateway | String | Payment gateway/provider |
| is_online | UInt8 | 1 if online payment, 0 if offline |

#### dim_promotions
Promotion and discount dimension.

| Column | Type | Description |
|--------|------|-------------|
| promotion_id | UInt16 | Primary key |
| promo_code | String | Promotion code |
| promo_name | String | Promotion name |
| discount_type | String | Type (percentage, fixed, free_shipping) |
| discount_value | Decimal(10,2) | Discount value |
| start_date | Date | Promotion start date |
| end_date | Date | Promotion end date |

#### dim_locations
Geographic location dimension.

| Column | Type | Description |
|--------|------|-------------|
| location_id | UInt16 | Primary key |
| province | String | Province/state name |
| city | String | City name |
| district | String | District/sub-district |
| postal_code | String | Postal/ZIP code |
| region | String | Region (e.g., Central, North, Northeast, South) |

## Query Optimization

### Indexes
- **fact_orders**: Sorted by (date_id, product_id, customer_id) for efficient time-series and product analysis
- **Dimension tables**: Sorted by primary key

### Partitioning
- **fact_orders**: Partitioned by date (monthly) using `toYYYYMM(created_at)`

### Example Queries

#### Top 5 Best-Selling Products in Bangkok
```sql
SELECT
    p.product_name,
    SUM(f.quantity) as total_quantity,
    SUM(f.total_amount) as total_revenue
FROM fact_orders f
JOIN dim_products p ON f.product_id = p.product_id
JOIN dim_locations l ON f.location_id = l.location_id
WHERE l.province = 'Bangkok'
GROUP BY p.product_name
ORDER BY total_quantity DESC
LIMIT 5
```

#### Total Sales by Month
```sql
SELECT
    d.year,
    d.month_name,
    SUM(f.total_amount) as monthly_revenue,
    COUNT(DISTINCT f.order_number) as order_count
FROM fact_orders f
JOIN dim_dates d ON f.date_id = d.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month
```

#### Most Used Payment Methods
```sql
SELECT
    pm.payment_method,
    COUNT(*) as usage_count,
    SUM(f.total_amount) as total_value
FROM fact_orders f
JOIN dim_payments pm ON f.payment_id = pm.payment_id
GROUP BY pm.payment_method
ORDER BY usage_count DESC
```

## Data Loading Strategy

1. **Extract**: Read CSV files uploaded by users
2. **Transform**:
   - Clean and validate data
   - Generate surrogate keys for dimensions
   - Handle NULL values and defaults
   - Create date dimension entries
3. **Load**:
   - Insert dimension data first (with conflict handling)
   - Insert fact data referencing dimension keys
   - Use bulk insert for performance

## Notes

- All monetary values use Decimal(10,2) for precision
- Date dimension pre-populated with 10 years of dates
- Supports Thai language for month names and categories
- Designed for OLAP (Online Analytical Processing) queries
