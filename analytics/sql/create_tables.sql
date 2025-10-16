-- ============================================
-- Smart Sales Analytics - ClickHouse Schema
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS sales_analytics;

USE sales_analytics;

-- ============================================
-- DIMENSION TABLES
-- ============================================

-- Dimension: Products
CREATE TABLE IF NOT EXISTS dim_products (
    product_id UInt32,
    sku String,
    product_name String,
    category String,
    subcategory String,
    unit_price Decimal(10, 2),
    cost Decimal(10, 2)
) ENGINE = MergeTree()
ORDER BY product_id;

-- Dimension: Customers
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id UInt32,
    customer_name String,
    email String,
    phone String,
    location_id UInt16,
    created_at DateTime
) ENGINE = MergeTree()
ORDER BY customer_id;

-- Dimension: Dates
CREATE TABLE IF NOT EXISTS dim_dates (
    date_id UInt32,
    date Date,
    year UInt16,
    month UInt8,
    day UInt8,
    quarter UInt8,
    day_of_week UInt8,
    month_name String,
    is_weekend UInt8,
    is_holiday UInt8
) ENGINE = MergeTree()
ORDER BY date_id;

-- Dimension: Payments
CREATE TABLE IF NOT EXISTS dim_payments (
    payment_id UInt16,
    payment_method String,
    payment_gateway String,
    is_online UInt8
) ENGINE = MergeTree()
ORDER BY payment_id;

-- Dimension: Promotions
CREATE TABLE IF NOT EXISTS dim_promotions (
    promotion_id UInt16,
    promo_code String,
    promo_name String,
    discount_type String,
    discount_value Decimal(10, 2),
    start_date Date,
    end_date Date
) ENGINE = MergeTree()
ORDER BY promotion_id;

-- Dimension: Locations
CREATE TABLE IF NOT EXISTS dim_locations (
    location_id UInt16,
    province String,
    city String,
    district String,
    postal_code String,
    region String
) ENGINE = MergeTree()
ORDER BY location_id;

-- ============================================
-- FACT TABLE
-- ============================================

-- Fact: Orders
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id UInt64,
    order_number String,
    date_id UInt32,
    product_id UInt32,
    customer_id UInt32,
    payment_id UInt16,
    promotion_id Nullable(UInt16),
    location_id UInt16,
    quantity UInt32,
    unit_price Decimal(10, 2),
    discount_amount Decimal(10, 2),
    tax_amount Decimal(10, 2),
    shipping_cost Decimal(10, 2),
    total_amount Decimal(10, 2),
    created_at DateTime
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (date_id, product_id, customer_id);

-- ============================================
-- HELPER FUNCTIONS & VIEWS
-- ============================================

-- View: Sales Summary by Date
CREATE VIEW IF NOT EXISTS v_daily_sales AS
SELECT
    d.date,
    d.year,
    d.month,
    d.month_name,
    COUNT(DISTINCT f.order_number) as order_count,
    SUM(f.quantity) as total_quantity,
    SUM(f.total_amount) as total_revenue,
    AVG(f.total_amount) as avg_order_value
FROM fact_orders f
JOIN dim_dates d ON f.date_id = d.date_id
GROUP BY d.date, d.year, d.month, d.month_name;

-- View: Product Performance
CREATE VIEW IF NOT EXISTS v_product_performance AS
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    COUNT(DISTINCT f.order_number) as order_count,
    SUM(f.quantity) as total_quantity,
    SUM(f.total_amount) as total_revenue,
    SUM(f.total_amount - (f.unit_price * f.quantity - f.discount_amount)) as gross_profit
FROM fact_orders f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.subcategory;

-- View: Location Analysis
CREATE VIEW IF NOT EXISTS v_location_sales AS
SELECT
    l.location_id,
    l.province,
    l.city,
    l.region,
    COUNT(DISTINCT f.order_number) as order_count,
    SUM(f.total_amount) as total_revenue,
    AVG(f.total_amount) as avg_order_value
FROM fact_orders f
JOIN dim_locations l ON f.location_id = l.location_id
GROUP BY l.location_id, l.province, l.city, l.region;

-- ============================================
-- INDEXES FOR OPTIMIZATION
-- ============================================

-- Create indexes for common query patterns
-- (ClickHouse automatically creates indexes based on ORDER BY)

-- ============================================
-- SAMPLE DATA INSERTION (for testing)
-- ============================================

-- Insert default "No Promotion" record
INSERT INTO dim_promotions (promotion_id, promo_code, promo_name, discount_type, discount_value, start_date, end_date)
VALUES (0, 'NONE', 'No Promotion', 'none', 0.00, '2020-01-01', '2099-12-31');

-- Insert default payment methods
INSERT INTO dim_payments (payment_id, payment_method, payment_gateway, is_online)
VALUES
    (1, 'Credit Card', 'Stripe', 1),
    (2, 'Debit Card', 'Stripe', 1),
    (3, 'PayPal', 'PayPal', 1),
    (4, 'Bank Transfer', 'SCB', 1),
    (5, 'Cash on Delivery', 'N/A', 0),
    (6, 'PromptPay', 'ThaiQR', 1),
    (7, 'TrueMoney Wallet', 'TrueMoney', 1);

-- Insert Thai regions and provinces
INSERT INTO dim_locations (location_id, province, city, district, postal_code, region)
VALUES
    (1, 'Bangkok', 'Bangkok', 'Pathum Wan', '10330', 'Central'),
    (2, 'Bangkok', 'Bangkok', 'Bang Rak', '10500', 'Central'),
    (3, 'Chiang Mai', 'Chiang Mai', 'Mueang', '50000', 'North'),
    (4, 'Phuket', 'Phuket', 'Mueang', '83000', 'South'),
    (5, 'Khon Kaen', 'Khon Kaen', 'Mueang', '40000', 'Northeast'),
    (6, 'Chonburi', 'Pattaya', 'Bang Lamung', '20150', 'Central'),
    (7, 'Nonthaburi', 'Nonthaburi', 'Mueang', '11000', 'Central');

-- ============================================
-- UTILITY QUERIES
-- ============================================

-- Query to check table sizes
-- SELECT table, sum(rows) as rows, formatReadableSize(sum(bytes)) as size
-- FROM system.parts
-- WHERE database = 'sales_analytics' AND active
-- GROUP BY table;

-- Query to check database info
-- SELECT * FROM system.databases WHERE name = 'sales_analytics';
