# Smart Sales Analytics - Usage Guide

This guide explains how to use the Smart Sales Analytics system effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Uploading Data](#uploading-data)
3. [Querying Data](#querying-data)
4. [Understanding Results](#understanding-results)
5. [Advanced Features](#advanced-features)

## Getting Started

### First Time Setup

1. **Access the Application**
   - Open your browser and navigate to `http://localhost:8000` (development) or your production URL
   - You'll see the main chat interface

2. **Configure API Key**
   - Ensure OpenAI API key is set in `.env` file
   - Without it, AI queries won't work

3. **Upload Your First Dataset**
   - Click "Upload Data" in the navigation
   - Follow the CSV format requirements

## Uploading Data

### CSV File Format

Your CSV file must include these **required columns**:

- `order_number`: Unique order identifier
- `order_date`: Date in YYYY-MM-DD format
- `product_name`: Name of the product
- `quantity`: Number of items (integer)
- `unit_price`: Price per unit (decimal)
- `total_amount`: Total order amount (decimal)

**Optional columns** for enriched analysis:

- `sku`: Stock Keeping Unit code
- `category`: Product category
- `subcategory`: Product subcategory
- `customer_name`: Customer's name
- `customer_email`: Customer's email
- `customer_phone`: Phone number
- `province`: Province/state
- `city`: City
- `district`: District/area
- `postal_code`: Postal code
- `region`: Geographic region
- `payment_method`: How customer paid
- `promotion_code`: Promo code used
- `discount_amount`: Discount applied
- `tax_amount`: Tax charged
- `shipping_cost`: Shipping fee

### Example CSV

```csv
order_number,order_date,product_name,sku,category,quantity,unit_price,total_amount,customer_name,customer_email,province,payment_method
ORD001,2024-01-15,Laptop Computer,LAP001,Electronics,1,25000.00,24610.00,John Doe,john@example.com,Bangkok,Credit Card
ORD002,2024-01-15,Wireless Mouse,MOU001,Electronics,2,450.00,963.00,Jane Smith,jane@example.com,Bangkok,PromptPay
```

### Upload Process

1. **Navigate to Upload Page**
   - Click "Upload Data" in navigation

2. **Select File**
   - Drag and drop your CSV file, or
   - Click "Choose File" to browse

3. **Verify File Preview**
   - Check filename and size
   - Ensure it's a CSV file

4. **Upload**
   - Click "Upload File"
   - Wait for processing (progress bar shows status)
   - System validates, transforms, and loads data

5. **Check Results**
   - Success: See confirmation with statistics
   - Error: Review validation errors and fix CSV

### Upload Limits

- Maximum file size: 10MB (configurable)
- Recommended: < 100,000 rows per upload
- For larger datasets, split into multiple files

## Querying Data

### How to Ask Questions

The AI understands natural language questions. Be clear and specific.

### Good Question Examples

**Sales Analysis:**
- "What are the top 5 best-selling products?"
- "Show me total sales by month in 2024"
- "Which products generated the most revenue?"
- "What's the average order value?"

**Geographic Analysis:**
- "Total sales in Bangkok?"
- "Which province has the highest number of orders?"
- "Sales breakdown by region"

**Customer Analysis:**
- "How many unique customers do we have?"
- "Who are our top 10 customers by spend?"
- "Customer acquisition trend by month"

**Product Performance:**
- "Which category is performing best?"
- "Products with declining sales"
- "SKU-level revenue analysis"

**Payment & Promotions:**
- "Which payment method is most popular?"
- "How many times was promo code SAVE100 used?"
- "Discount impact on sales"

**Time-Based Analysis:**
- "Daily sales for last week"
- "Weekend vs weekday sales comparison"
- "Sales trend for Q1 2024"

### Question Best Practices

✅ **DO:**
- Be specific: "Top 5 products in Bangkok" vs "Products"
- Include timeframes: "Sales in January 2024"
- Use proper names: "Bangkok" not "bkk"
- Ask one thing at a time

❌ **DON'T:**
- Be too vague: "Show me stuff"
- Ask multiple unrelated questions
- Use unclear abbreviations
- Request data modifications (DELETE, UPDATE)

### Query Results

After asking a question, you'll receive:

1. **AI Summary**
   - Plain English explanation of findings
   - Key insights and numbers

2. **Execution Details**
   - Number of rows returned
   - Query execution time

3. **View Full Results**
   - Click to see:
     - Complete data table
     - Generated SQL query
     - SQL explanation

## Understanding Results

### Result Components

**Summary Section:**
- AI-generated insights in business language
- Highlights important findings
- Actionable information

**SQL Query:**
- The actual query executed against database
- Useful for learning or custom queries
- Can be copied for direct ClickHouse access

**Data Table:**
- Tabular display of results
- First 100 rows shown (for large result sets)
- Sortable columns
- Copy/export functionality

### Interpreting Results

**Sales Metrics:**
- `total_amount`: Revenue in currency
- `quantity`: Number of units
- `order_count`: Number of transactions

**Aggregations:**
- `SUM()`: Total values
- `AVG()`: Average values
- `COUNT()`: Number of records
- `MAX()`/`MIN()`: Highest/lowest values

**Groupings:**
- `BY product`: Per-product breakdown
- `BY month`: Monthly aggregation
- `BY location`: Geographic grouping

## Advanced Features

### Query History

- All queries are saved automatically
- Access via API: `/api/history/`
- Review past questions and results
- Learn from successful query patterns

### Admin Panel

Access at `/admin/`:

1. **Uploaded Files**
   - View all uploaded files
   - Check processing status
   - Review error messages
   - See file statistics

2. **Query History**
   - Browse all queries
   - Filter by success/failure
   - View execution times
   - Analyze usage patterns

### API Access

For programmatic access:

**Query API:**
```bash
POST /api/query/
{
  "question": "What are the top 5 products?",
  "language": "en"
}
```

**Upload API:**
```bash
POST /api/upload/
Content-Type: multipart/form-data

file: [CSV file]
```

**History API:**
```bash
GET /api/history/?limit=20&offset=0
```

### Health Check

Monitor system health:
```bash
GET /api/health/
```

Returns:
- Database connection status
- OpenAI configuration status
- Overall system health

## Tips & Tricks

### Performance

- Upload data in batches for large datasets
- Be specific in questions to get faster results
- Use date ranges to limit data scanned

### Accuracy

- Ensure data quality before upload
- Use consistent naming (e.g., "Bangkok" not "bangkok")
- Include all relevant columns for rich analysis

### Troubleshooting

**"OpenAI Not Configured"**
- Set `OPENAI_API_KEY` in `.env` file
- Restart Django server

**"No Results Found"**
- Check if data was uploaded successfully
- Verify question references actual data
- Try broader questions

**Upload Fails**
- Check CSV format matches requirements
- Ensure file size is under limit
- Review error messages for specific issues

## Example Workflow

1. **Upload Monthly Sales Data**
   ```
   Upload: sales_january_2024.csv (5,000 rows)
   Result: ✓ Successfully processed
   ```

2. **Ask Analysis Questions**
   ```
   Q: "What are our top 5 products this month?"
   A: Shows products with sales figures and trends
   ```

3. **Dig Deeper**
   ```
   Q: "Show me sales of Product X by city"
   A: Geographic breakdown of specific product
   ```

4. **Review Insights**
   - Read AI summary
   - Check data table
   - View SQL for learning

5. **Export or Act**
   - Use insights for business decisions
   - Share results with team
   - Plan inventory/marketing based on data

## Support & Help

- **Documentation**: Check README.md and DEPLOYMENT.md
- **Sample Data**: Download template at `/media/sample_orders.csv`
- **Logs**: Review application logs for errors
- **Admin**: Use `/admin/` for detailed system info

## Best Practices

1. **Data Quality**: Clean data = better insights
2. **Regular Uploads**: Keep data current
3. **Specific Questions**: Get more precise answers
4. **Review SQL**: Learn from generated queries
5. **Monitor Usage**: Check query history for patterns

## Limitations

- Maximum 10MB file uploads (configurable)
- AI queries require OpenAI API access
- Complex multi-step analysis may need multiple queries
- Historical data should be uploaded in chronological order

## Next Steps

- Explore example questions
- Upload your actual sales data
- Experiment with different question types
- Review generated SQL to learn
- Share insights with your team
