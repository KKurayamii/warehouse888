# Smart Sales Analytics System 🚀

An AI-powered sales analytics platform with **ChatGPT integration** that allows e-commerce entrepreneurs to have natural conversations about their sales data.

## ✨ Features

- **ChatGPT-Powered Chat**: Real conversational AI for sales insights
- **Natural Language Queries**: Ask questions in plain language
- **Conversation History**: Maintains context across multiple questions
- **Fast Data Processing**: ClickHouse data warehouse for high-performance queries
- **Easy Data Upload**: Simple web interface for CSV file uploads
- **Automated ETL**: Automatic data processing and transformation
- **Beautiful UI**: Apple-inspired design with smooth animations

## Tech Stack

- **Backend**: Django 5.0 + Django REST Framework
- **Frontend**: Django Templates + Tailwind CSS + JavaScript
- **Database**: ClickHouse (Data Warehouse)
- **AI**: OpenAI API + LangChain
- **Data Processing**: Pandas

## Installation

### Prerequisites

- Python 3.10+
- ClickHouse Server
- Node.js (for Tailwind CSS)
- OpenAI API Key

### Setup

1. Clone or navigate to the project directory:
```bash
cd smart-sales-analytics
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment variables:
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

5. Edit `.env` file with your credentials:
- Add your OpenAI API key
- Configure ClickHouse connection details
- Set Django secret key

6. Install ClickHouse:
- Download from: https://clickhouse.com/docs/en/install
- Start ClickHouse server

7. Run Django migrations:
```bash
python manage.py migrate
```

8. Create superuser:
```bash
python manage.py createsuperuser
```

9. Run development server:
```bash
python manage.py runserver
```

## Project Structure

```
smart-sales-analytics/
├── analytics/          # Main Django app
│   ├── etl/           # ETL pipeline modules
│   ├── ai/            # AI query engine
│   ├── models.py      # Data models
│   ├── views.py       # API views
│   └── templates/     # HTML templates
├── config/            # Django project settings
├── static/            # Static files (CSS, JS)
├── media/             # Uploaded files
├── venv/              # Virtual environment
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
└── manage.py          # Django management script
```

## 🚀 Quick Start

**Your server is already running!** Just open your browser and go to:

```
http://localhost:8000
```

### First Time Setup (If Not Running)

1. **Open Terminal/Command Prompt**
2. **Navigate to project directory**:
   ```bash
   cd C:\Users\HP\smart-sales-analytics
   ```

3. **Activate virtual environment**:
   ```bash
   venv\Scripts\activate
   ```

4. **Run the server**:
   ```bash
   python manage.py runserver
   ```

5. **Open browser** to `http://localhost:8000`

That's it! 🎉

## 💬 Using the ChatGPT Interface

### Chat with Your Data

1. Go to the **home page** (`http://localhost:8000`)
2. Type your question in the chat box
3. ChatGPT will analyze your data and respond naturally
4. Continue the conversation - it remembers context!

### Upload New Data

1. Click **"Upload New File"** button
2. Select your CSV file
3. Wait for processing to complete
4. Files appear below the chat interface

### Example Questions

**Simple Queries:**
- "What are the top 5 best-selling products?"
- "Total sales in Bangkok?"
- "Which payment method is most used?"

**Conversational:**
- "Show me sales trends this month"
- "How do they compare to last month?"
- "Which region performs best?"

**Complex Analysis:**
- "What are the seasonal patterns in our sales?"
- "Which products have the best profit margins?"
- "Show me customer behavior by location"

## Development

### Running Tests

```bash
pytest
```

### Database Schema

The system uses a Star Schema design:
- **Fact Table**: fact_orders
- **Dimension Tables**: dim_products, dim_customers, dim_dates, dim_payments, dim_promotions, dim_locations

## License

MIT License

## Support

For issues and questions, please create an issue in the repository.
