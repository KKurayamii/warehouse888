# Getting Started with Smart Sales Analytics

Welcome! This guide will help you set up and run the Smart Sales Analytics system in just a few minutes.

## Quick Start (5 minutes)

### Step 1: Prerequisites Check

Make sure you have:
- ✅ Python 3.10 or higher installed
- ✅ ClickHouse installed and running
- ✅ OpenAI API key (get one at https://platform.openai.com/)

### Step 2: Install ClickHouse (if not installed)

**Windows:**
```powershell
# Download from https://clickhouse.com/docs/en/install
# Or use WSL2 and follow Linux instructions
```

**Linux/Mac:**
```bash
curl https://clickhouse.com/ | sh
sudo ./clickhouse install
sudo clickhouse start
```

### Step 3: Setup Application

```bash
# Navigate to project directory
cd smart-sales-analytics

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies (if not done)
pip install -r requirements.txt

# Build Tailwind CSS
npm install
npm run build:css
```

### Step 4: Configure Environment

```bash
# Copy environment template
copy .env.example .env    # Windows
# cp .env.example .env    # Linux/Mac

# Edit .env and add your OpenAI API key
notepad .env              # Windows
# nano .env               # Linux/Mac
```

Set these values in `.env`:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
OPENAI_API_KEY=sk-your-openai-key-here

CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_DATABASE=sales_analytics
```

### Step 5: Initialize Database

```bash
# Run Django migrations
python manage.py migrate

# Setup ClickHouse database
python manage.py setup_clickhouse

# Create admin user
python manage.py createsuperuser
```

### Step 6: Start the Server

```bash
# Run development server
python manage.py runserver
```

🎉 **Success!** Open http://localhost:8000 in your browser

## What to Do Next

### 1. Upload Sample Data

The project includes a sample CSV file:

1. Go to http://localhost:8000/upload/
2. Upload `sample_orders.csv`
3. Wait for processing (should take a few seconds)
4. See confirmation message

### 2. Try Example Questions

Go to http://localhost:8000 and ask:

- "What are the top 5 best-selling products?"
- "Total sales in Bangkok?"
- "Sales by month in 2024?"
- "Which payment method is most used?"

### 3. Upload Your Own Data

1. Prepare your CSV file (see format below)
2. Go to Upload page
3. Drag and drop or select file
4. Wait for processing
5. Start querying!

## CSV File Format

Your CSV needs these columns:

**Required:**
- `order_number` - Unique order ID
- `order_date` - Date (YYYY-MM-DD format)
- `product_name` - Product name
- `quantity` - Number of items
- `unit_price` - Price per unit
- `total_amount` - Total order value

**Optional (for richer analysis):**
- `customer_name`, `customer_email`
- `province`, `city`, `district`
- `category`, `subcategory`, `sku`
- `payment_method`
- `promotion_code`
- And more...

**Example CSV:**
```csv
order_number,order_date,product_name,quantity,unit_price,total_amount,customer_email,province,payment_method
ORD001,2024-01-15,Laptop,1,25000,25000,john@example.com,Bangkok,Credit Card
ORD002,2024-01-16,Mouse,2,450,900,jane@example.com,Chiang Mai,PromptPay
```

## System Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────┐
│  Django Frontend                │
│  - Chat Interface (/)           │
│  - Upload Page (/upload)        │
│  - Admin Panel (/admin)         │
└───────┬─────────────────────────┘
        │
        ↓
┌─────────────────────────────────┐
│  Django Backend                 │
│  - REST API                     │
│  - AI Query Engine (OpenAI)     │
│  - ETL Pipeline (Pandas)        │
└───────┬─────────────────────────┘
        │
        ↓
┌─────────────────────────────────┐
│  ClickHouse Data Warehouse      │
│  - Star Schema                  │
│  - Fast Analytics               │
└─────────────────────────────────┘
```

## Key Features

### 1. Natural Language Queries
Ask questions in plain English or Thai:
- "Show me sales trends"
- "Top products by revenue"
- "Customer analysis by region"

### 2. Automatic SQL Generation
- AI converts your question to SQL
- Validates for safety
- Optimizes for performance

### 3. Smart Data Processing
- Automatic ETL pipeline
- Data validation
- Star schema transformation

### 4. Beautiful Visualizations
- Data tables
- AI-generated summaries
- SQL explanations

## Available Endpoints

### Frontend Pages
- `/` - Chat interface for queries
- `/upload/` - Upload CSV files
- `/admin/` - Django admin panel

### API Endpoints
- `POST /api/query/` - Submit natural language query
- `POST /api/upload/` - Upload CSV file
- `GET /api/history/` - Query history
- `GET /api/uploads/` - Upload history
- `GET /api/health/` - System health check

## Troubleshooting

### ClickHouse Not Running

```bash
# Check status
clickhouse-client

# Start if not running
sudo clickhouse start    # Linux
# Or start from Windows services
```

### OpenAI Error

- Verify API key is set in `.env`
- Check key has credits at https://platform.openai.com/
- Restart Django server after changing `.env`

### Import Error

```bash
# Make sure virtual environment is activated
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### CSS Not Loading

```bash
# Rebuild Tailwind CSS
npm run build:css

# Collect static files
python manage.py collectstatic --no-input
```

## Project Structure

```
smart-sales-analytics/
├── analytics/              # Main Django app
│   ├── ai/                # AI query engine
│   │   └── query_engine.py
│   ├── etl/               # ETL pipeline
│   │   ├── processor.py
│   │   └── validator.py
│   ├── sql/               # Database scripts
│   ├── templates/         # HTML templates
│   ├── management/        # Django commands
│   ├── models.py          # Data models
│   ├── views.py           # API & views
│   ├── admin.py           # Admin config
│   └── database.py        # ClickHouse manager
├── config/                # Django settings
├── static/                # CSS, JavaScript
├── media/                 # Uploaded files
├── docs/                  # Documentation
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
├── package.json           # Node dependencies
└── manage.py              # Django CLI
```

## Development Commands

```bash
# Run development server
python manage.py runserver

# Run with custom port
python manage.py runserver 0.0.0.0:8080

# Create superuser
python manage.py createsuperuser

# Run database setup
python manage.py setup_clickhouse

# Rebuild CSS
npm run watch:css          # Watch mode
npm run build:css          # One-time build

# Django shell
python manage.py shell

# Check for issues
python manage.py check
```

## Next Steps

1. ✅ **Read USAGE.md** - Learn how to use the system effectively
2. ✅ **Upload real data** - Import your actual sales data
3. ✅ **Explore queries** - Try different types of questions
4. ✅ **Review DEPLOYMENT.md** - When ready for production
5. ✅ **Customize** - Adapt to your specific needs

## Support & Resources

- **Documentation**: See README.md, USAGE.md, DEPLOYMENT.md
- **Sample Data**: `sample_orders.csv` in project root
- **API Docs**: Visit `/api/` endpoints
- **Admin Panel**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/api/health/

## Tips for Success

1. **Start Small**: Upload sample data first
2. **Ask Simple Questions**: Begin with basic queries
3. **Review SQL**: Learn from generated queries
4. **Check Logs**: Monitor for errors
5. **Read Docs**: USAGE.md has detailed examples

---

**Ready to analyze your sales data?** Start asking questions! 🚀
