# Smart Sales Analytics System 🚀

ชื่อโครงการ
- ระบบวิเคราะห์ข้อมูลการขายอัจฉริยะสำหรับธุรกิจอีคอมเมิร์ซด้วย Data Warehouse และ Generative AI

สมาชิก 
มีจำนวนทัังหมด 4 คน ได้แก่
- 64114540436 นายธนานนท์ โสภิตชา 
- 65114540709 นางสาวอันนา สาครวงศ์วัฒนา
- 65114540310 นางสาวนัตติกานต์ คำสวาสดิ์
- 64114540102 นายฐานันดร มิยะพันธ์

วัตถุประสงค์
- เพื่อช่วยให้ผู้ประกอบการวิเคราะห์ข้อมูลการขายได้ด้วยตนเอง โดยไม่ต้องพึ่งพาผู้เชี่ยวชาญ
- เพื่อลดเวลาในการสร้างรายงาน จากหลายชั่วโมงเหลือเพียงไม่กี่นาที
- เพื่อให้ได้ข้อมูลเชิงลึก (Insights) ที่นำไปใช้ตัดสินใจทางธุรกิจได้ทันที
- เพื่อรองรับข้อมูลจากแพลตฟอร์มอีคอมเมิร์ซชั้นนำในประเทศไทย

เครื่องมือ
Backend Framework:
- Django: ใช้จัดการ Logic ทั้งหมด, สร้าง API, และเชื่อมต่อกับส่วนต่างๆ ของระบบ
- Django REST Framework: (แนะนำ) สำหรับสร้าง API ที่เป็นระเบียบและง่ายต่อการจัดการ

Frontend:
- Django Templates: ใช้สร้างหน้าเว็บ HTML พื้นฐาน
- CSS Framework (เช่น Bootstrap, Tailwind CSS): เพื่อความสวยงามและ Responsive
- JavaScript (Fetch API หรือ Axios): เพื่อให้หน้าเว็บสามารถรับ-ส่งข้อมูลกับ Django Backend ได้โดยไม่ต้องโหลดใหม่ทั้งหน้า (Asynchronous)

ฐานข้อมูล (Data Warehouse):
-ClickHouse:ฐานข้อมูลหลักสำหรับเก็บข้อมูลวิเคราะห์
-clickhouse-driver: Library ของ Python สำหรับให้ Django เชื่อมต่อกับ ClickHouse

AI & Data Processing:
-Python: ภาษาหลักในการพัฒนา
-OpenAI API: ใช้บริการโมเดลภาษาขนาดใหญ่ (Gemini)
-openai (Python Library): สำหรับเรียกใช้ OpenAI API
-LangChain: Framework ที่ช่วยจัดการการสร้าง Prompt และการเชื่อมต่อกับ OpenAI ให้ง่ายขึ้น
-Pandas: สำหรับจัดการข้อมูลจากไฟล์ CSV/Excel ในขั้นตอน ETL

Deployment (การนำขึ้นใช้งานจริง):
- Web Server (เช่น Gunicorn, Nginx): สำหรับ Run Django Application
- Server/Cloud (เช่น AWS, Google Cloud, DigitalOcean): สำหรับติดตั้งและให้บริการโปรแกรม


ลิงค์ สไลด์นำเสนอ : https://www.canva.com/design/DAG2BdtwMOI/P2Q5v82eNB7IxaKiC77q0A/edit?utm_content=DAG2BdtwMOI&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton
ลิงค์Folder video : https://drive.google.com/drive/folders/1xTTDLr5TBQR2ddWARosgHNXVPs_Vea46?usp=sharing
----------------------------------------

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
