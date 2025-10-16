# เอกสารประกอบระบบ Smart Sales Analytics (ภาษาไทย)

---

## 📋 สารบัญ

1. [ภาพรวมระบบ](#1-ภาพรวมระบบ)
2. [วัตถุประสงค์และความสามารถของระบบ](#2-วัตถุประสงค์และความสามารถของระบบ)
3. [Function Requirements](#3-function-requirements)
4. [โครงสร้างของโปรแกรม](#4-โครงสร้างของโปรแกรม)
5. [Workflow ของระบบ](#5-workflow-ของระบบ)
6. [เทคโนโลยีและเครื่องมือที่ใช้](#6-เทคโนโลยีและเครื่องมือที่ใช้)
7. [Database Schema Design](#7-database-schema-design)
8. [การติดตั้งและใช้งาน](#8-การติดตั้งและใช้งาน)

---

## 1. ภาพรวมระบบ

### 1.1 ระบบนี้คืออะไร?

**Smart Sales Analytics System** เป็นระบบวิเคราะห์ข้อมูลการขายแบบอัจฉริยะ ที่ใช้เทคโนโลยี AI (Artificial Intelligence) เพื่อช่วยให้ผู้ประกอบการอีคอมเมิร์ซสามารถวิเคราะห์ข้อมูลการขายได้อย่างรวดเร็วและง่ายดาย โดยไม่ต้องมีความรู้ทางด้าน SQL หรือการเขียนโปรแกรม

### 1.2 ใช้งานอย่างไร?

ผู้ใช้สามารถ:
1. **อัพโหลดไฟล์ยอดขาย** (รองรับไฟล์ CSV และ Excel) จากแพลตฟอร์มอีคอมเมิร์ซ เช่น Shopee, Lazada
2. **ถามคำถามเป็นภาษาไทยหรือภาษาอังกฤษ** เช่น "สินค้าขายดี 5 อันดับแรกคืออะไร?" หรือ "ยอดขายรวมในกรุงเทพเดือนนี้เท่าไหร่?"
3. **รับคำตอบและรายงานทันที** พร้อมกราฟและตารางข้อมูลที่เข้าใจง่าย

### 1.3 ประโยชน์หลัก

- ✅ **ประหยัดเวลา**: ไม่ต้องวิเคราะห์ข้อมูลด้วยตัวเอง
- ✅ **ใช้งานง่าย**: ถามคำถามเป็นภาษาธรรมดา ไม่ต้องเขียน SQL
- ✅ **รวดเร็ว**: ใช้ ClickHouse Database ประมวลผลข้อมูลล้านแถวภายในไม่กี่วินาที
- ✅ **รองรับภาษาไทย**: เข้าใจคำถามและข้อมูลภาษาไทยจากแพลตฟอร์มไทย
- ✅ **รองรับข้อมูล Shopee**: แปลงคอลัมน์ภาษาไทยจาก Shopee อัตโนมัติ

---

## 2. วัตถุประสงค์และความสามารถของระบบ

### 2.1 วัตถุประสงค์

1. **เพื่อช่วยให้ผู้ประกอบการวิเคราะห์ข้อมูลการขายได้เองโดยไม่ต้องพึ่งผู้เชี่ยวชาญ**
2. **เพื่อลดเวลาในการสร้างรายงานจากหลายชั่วโมงเหลือเพียงไม่กี่นาที**
3. **เพื่อให้ได้ข้อมูลเชิงลึก (Insights) ที่ช่วยในการตัดสินใจทางธุรกิจ**
4. **เพื่อรองรับข้อมูลจากหลายแพลตฟอร์มอีคอมเมิร์ซในประเทศไทย**

### 2.2 ความสามารถของระบบ (Features)

#### 2.2.1 การอัพโหลดข้อมูล
- ✅ รองรับไฟล์ **CSV** (.csv)
- ✅ รองรับไฟล์ **Excel** (.xlsx, .xls)
- ✅ ตรวจสอบความถูกต้องของข้อมูล (Data Validation)
- ✅ แปลงคอลัมน์ภาษาไทยจาก Shopee เป็นภาษาอังกฤษอัตโนมัติ
- ✅ รองรับไฟล์ขนาดใหญ่ (กำหนดค่าได้)
- ✅ แสดงประวัติการอัพโหลด พร้อมสถานะและสถิติ

#### 2.2.2 การวิเคราะห์ด้วย AI (Natural Language Query)
- ✅ ถามคำถามเป็น**ภาษาไทย**หรือ**ภาษาอังกฤษ**
- ✅ ระบบแปลงคำถามเป็น SQL Query โดยอัตโนมัติ
- ✅ แสดงคำอธิบายว่า SQL ทำงานอย่างไร
- ✅ แสดงผลลัพธ์เป็นตารางพร้อมสรุปข้อมูล
- ✅ บันทึกประวัติคำถามและคำตอบ

#### 2.2.3 การประมวลผลข้อมูล (ETL Pipeline)
- ✅ **Extract**: อ่านข้อมูลจากไฟล์ CSV/Excel
- ✅ **Transform**:
  - ทำความสะอาดข้อมูล
  - แปลงรูปแบบวันที่
  - สร้าง Dimension Keys
  - จัดการค่า NULL
  - ลบข้อมูลซ้ำ
- ✅ **Load**: โหลดข้อมูลเข้า ClickHouse Database

#### 2.2.4 การรายงานและวิเคราะห์
- ✅ **วิเคราะห์สินค้า**: สินค้าขายดี, สินค้าขายไม่ดี, หมวดหมู่ยอดนิยม
- ✅ **วิเคราะห์เวลา**: ยอดขายรายวัน/รายเดือน/รายไตรมาส/รายปี
- ✅ **วิเคราะห์พื้นที่**: ยอดขายตามจังหวัด/ภูมิภาค
- ✅ **วิเคราะห์ลูกค้า**: ลูกค้าซื้อบ่อย, มูลค่าลูกค้า
- ✅ **วิเคราะห์การชำระเงิน**: ช่องทางการชำระเงินที่นิยม
- ✅ **วิเคราะห์โปรโมชั่น**: ประสิทธิภาพของโค้ดส่วนลด

---

## 3. Function Requirements

### 3.1 Functional Requirements

#### FR-1: การจัดการไฟล์อัพโหลด
- **FR-1.1**: ระบบต้องรองรับการอัพโหลดไฟล์ CSV และ Excel (xlsx, xls)
- **FR-1.2**: ระบบต้องตรวจสอบ file extension และ file size
- **FR-1.3**: ระบบต้องแสดง drag-and-drop interface
- **FR-1.4**: ระบบต้องแสดง progress bar ขณะอัพโหลด
- **FR-1.5**: ระบบต้องบันทึกประวัติการอัพโหลดพร้อม timestamp
- **FR-1.6**: ระบบต้องแสดงสถานะ (pending, processing, completed, failed)

#### FR-2: การตรวจสอบข้อมูล (Data Validation)
- **FR-2.1**: ระบบต้องตรวจสอบว่ามีคอลัมน์ที่จำเป็นครบถ้วน:
  - order_number (เลขที่คำสั่งซื้อ)
  - order_date (วันที่สั่งซื้อ)
  - product_name (ชื่อสินค้า)
  - quantity (จำนวน - optional, default = 1)
  - unit_price (ราคาต่อหน่วย)
  - total_amount (ยอดรวม)
- **FR-2.2**: ระบบต้องตรวจสอบรูปแบบวันที่
- **FR-2.3**: ระบบต้องตรวจสอบค่าติดลบในคอลัมน์ตัวเลข
- **FR-2.4**: ระบบต้องตรวจสอบ data type ของแต่ละคอลัมน์
- **FR-2.5**: ระบบต้องตรวจสอบ duplicate order numbers
- **FR-2.6**: ระบบต้องแสดงข้อผิดพลาดที่เฉพาะเจาะจง

#### FR-3: การแปลงคอลัมน์ภาษาไทย
- **FR-3.1**: ระบบต้องรองรับคอลัมน์จาก Shopee Export:
  - หมายเลขคำสั่งซื้อ → order_number
  - วันที่ทำการสั่งซื้อ → order_date
  - ชื่อสินค้า → product_name
  - ราคาสินค้าที่ชำระโดยผู้ซื้อ (THB) → unit_price
  - จำนวนเงินทั้งหมด → total_amount
  - ชื่อผู้รับ → customer_name
  - จังหวัด → province
  - เขต/อำเภอ → city
  - ช่องทางการชำระเงิน → payment_method
  - และอื่นๆ
- **FR-3.2**: ระบบต้องแปลงคอลัมน์อัตโนมัติก่อนการ validate
- **FR-3.3**: ระบบต้อง log การแปลงคอลัมน์

#### FR-4: ETL Pipeline
- **FR-4.1**: **Extract**
  - อ่านไฟล์ CSV ด้วย encoding หลายแบบ (utf-8, utf-8-sig, latin-1, cp1252)
  - อ่านไฟล์ Excel ด้วย openpyxl
  - จัดการ BOM (Byte Order Mark)
- **FR-4.2**: **Transform**
  - ทำความสะอาด order_number
  - แปลง order_date เป็น datetime
  - สร้าง date_id ในรูปแบบ YYYYMMDD
  - แปลง sku เป็น string
  - จัดการค่า NULL ในคอลัมน์ optional
  - ลบ duplicate orders
  - สร้าง surrogate keys สำหรับ dimensions
- **FR-4.3**: **Load**
  - โหลดข้อมูลเข้า dim_products
  - โหลดข้อมูลเข้า dim_customers
  - โหลดข้อมูลเข้า dim_locations
  - โหลดข้อมูลเข้า dim_payments
  - โหลดข้อมูลเข้า dim_promotions
  - โหลดข้อมูลเข้า fact_orders
  - ใช้ bulk insert เพื่อประสิทธิภาพ

#### FR-5: Natural Language Query
- **FR-5.1**: ระบบต้องรับคำถามเป็นภาษาไทยและภาษาอังกฤษ
- **FR-5.2**: ระบบต้องใช้ OpenAI GPT-4 แปลงคำถามเป็น SQL
- **FR-5.3**: ระบบต้องตรวจสอบความปลอดภัยของ SQL (ไม่อนุญาต DELETE, UPDATE, DROP)
- **FR-5.4**: ระบบต้องแสดง SQL query ที่สร้างขึ้น
- **FR-5.5**: ระบบต้องแสดงคำอธิบาย SQL
- **FR-5.6**: ระบบต้อง execute query บน ClickHouse
- **FR-5.7**: ระบบต้องแสดงผลลัพธ์เป็นตาราง
- **FR-5.8**: ระบบต้องสรุปผลลัพธ์เป็นภาษาธรรมดา
- **FR-5.9**: ระบบต้องบันทึกประวัติคำถาม พร้อม execution time

#### FR-6: User Interface
- **FR-6.1**: หน้าแรก (Chat Interface) สำหรับถามคำถาม
- **FR-6.2**: หน้าอัพโหลด (Upload Page) สำหรับอัพโหลดไฟล์
- **FR-6.3**: แสดงคำถามตัวอย่าง (Sample Questions)
- **FR-6.4**: แสดงประวัติคำถาม (Query History)
- **FR-6.5**: แสดงประวัติการอัพโหลด (Upload History)
- **FR-6.6**: ออกแบบ UI แบบ Apple-inspired (สะอาด, ทันสมัย)

#### FR-7: API Endpoints
- **FR-7.1**: `POST /api/query/` - ส่งคำถามและรับคำตอบ
- **FR-7.2**: `POST /api/upload/` - อัพโหลดไฟล์
- **FR-7.3**: `GET /api/history/` - ดึงประวัติคำถาม
- **FR-7.4**: `GET /api/uploads/` - ดึงประวัติการอัพโหลด
- **FR-7.5**: `GET /api/health/` - ตรวจสอบสถานะระบบ

### 3.2 Non-Functional Requirements

#### NFR-1: Performance
- **NFR-1.1**: ระบบต้องประมวลผล query ภายใน 3 วินาที (สำหรับข้อมูล < 1 ล้านแถว)
- **NFR-1.2**: ระบบต้องรองรับการอัพโหลดไฟล์ขนาด 50 MB
- **NFR-1.3**: ระบบต้องรองรับข้อมูลขนาด > 10 ล้านแถว

#### NFR-2: Security
- **NFR-2.1**: ป้องกัน SQL Injection
- **NFR-2.2**: ไม่อนุญาตให้ execute คำสั่ง DELETE, UPDATE, DROP
- **NFR-2.3**: ใช้ CSRF token สำหรับ form submissions
- **NFR-2.4**: เก็บ OpenAI API key ใน environment variables

#### NFR-3: Usability
- **NFR-3.1**: UI ต้องใช้งานง่าย ไม่ต้องอ่าน manual
- **NFR-3.2**: แสดงข้อความ error ที่เข้าใจง่าย
- **NFR-3.3**: รองรับ responsive design (mobile-friendly)

#### NFR-4: Reliability
- **NFR-4.1**: ระบบต้องจัดการ error ได้อย่างเหมาะสม
- **NFR-4.2**: บันทึก logs สำหรับ debugging
- **NFR-4.3**: แสดงสถานะการประมวลผลที่ชัดเจน

---

## 4. โครงสร้างของโปรแกรม

### 4.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER (Web Browser)                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTP/HTTPS
                 │
┌────────────────▼────────────────────────────────────────────┐
│                   DJANGO WEB APPLICATION                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Frontend (Templates)                  │ │
│  │  - HTML/CSS (Tailwind CSS)                            │ │
│  │  - JavaScript (Vanilla JS)                            │ │
│  │  - Chat Interface & Upload Page                       │ │
│  └─────────────┬──────────────────────────────────────────┘ │
│                │                                             │
│  ┌─────────────▼──────────────────────────────────────────┐ │
│  │              Backend (Django + DRF)                    │ │
│  │                                                        │ │
│  │  ┌─────────────────┐    ┌─────────────────┐          │ │
│  │  │   Views/APIs    │    │   Models        │          │ │
│  │  │ - query_api     │    │ - UploadedFile  │          │ │
│  │  │ - upload_api    │    │ - QueryHistory  │          │ │
│  │  │ - history_api   │    │                 │          │ │
│  │  └────────┬────────┘    └─────────────────┘          │ │
│  │           │                                            │ │
│  │  ┌────────▼──────────────────────────────────────────┐ │ │
│  │  │           Business Logic Layer                   │ │ │
│  │  │                                                  │ │ │
│  │  │  ┌──────────────┐      ┌──────────────┐        │ │ │
│  │  │  │ ETL Pipeline │      │ AI Engine    │        │ │ │
│  │  │  │              │      │              │        │ │ │
│  │  │  │ ┌──────────┐ │      │ ┌──────────┐ │        │ │ │
│  │  │  │ │Validator │ │      │ │Query Gen │ │        │ │ │
│  │  │  │ └──────────┘ │      │ └──────────┘ │        │ │ │
│  │  │  │ ┌──────────┐ │      │ ┌──────────┐ │        │ │ │
│  │  │  │ │Processor │ │      │ │Summarizer│ │        │ │ │
│  │  │  │ └──────────┘ │      │ └──────────┘ │        │ │ │
│  │  │  └──────────────┘      └──────────────┘        │ │ │
│  │  └────────┬─────────────────────┬──────────────────┘ │ │
│  └───────────┼─────────────────────┼────────────────────┘ │
└──────────────┼─────────────────────┼──────────────────────┘
               │                     │
               │                     │
     ┌─────────▼──────────┐  ┌──────▼──────────┐
     │  ClickHouse DB     │  │  OpenAI API     │
     │  (Data Warehouse)  │  │  (GPT-4)        │
     │                    │  │                 │
     │ - fact_orders      │  │ - SQL Gen       │
     │ - dim_products     │  │ - Summarization │
     │ - dim_customers    │  │                 │
     │ - dim_dates        │  └─────────────────┘
     │ - dim_locations    │
     │ - dim_payments     │
     │ - dim_promotions   │
     └────────────────────┘
```

### 4.2 Project Directory Structure

```
smart-sales-analytics/
│
├── analytics/                  # Main Django Application
│   ├── __init__.py
│   ├── models.py              # Django Models (UploadedFile, QueryHistory)
│   ├── views.py               # API Views & Frontend Views
│   ├── urls.py                # URL Routing
│   ├── admin.py               # Django Admin Configuration
│   │
│   ├── etl/                   # ETL Pipeline Module
│   │   ├── __init__.py
│   │   ├── validator.py       # Data Validation
│   │   │   └── DataValidator class
│   │   │       ├── validate_file()
│   │   │       ├── normalize_columns()
│   │   │       ├── check_required_columns()
│   │   │       └── check_data_types()
│   │   │
│   │   └── processor.py       # ETL Processing
│   │       └── ETLProcessor class
│   │           ├── extract()      # Read CSV/Excel
│   │           ├── transform()    # Clean & Transform
│   │           ├── load()         # Load to ClickHouse
│   │           └── process_csv()  # Main Pipeline
│   │
│   ├── ai/                    # AI Query Engine Module
│   │   ├── __init__.py
│   │   └── query_engine.py    # Natural Language to SQL
│   │       └── QueryEngine class
│   │           ├── generate_sql()      # Convert NL to SQL
│   │           ├── execute_query()     # Run SQL
│   │           ├── summarize_results() # Summarize Output
│   │           └── process_question()  # Complete Pipeline
│   │
│   ├── templates/             # HTML Templates
│   │   └── analytics/
│   │       ├── base.html      # Base Template
│   │       ├── chat.html      # Chat Interface
│   │       └── upload.html    # Upload Page
│   │
│   └── database.py            # ClickHouse Connection Manager
│
├── config/                    # Django Project Settings
│   ├── __init__.py
│   ├── settings.py           # Main Settings
│   ├── urls.py               # Root URL Configuration
│   └── wsgi.py               # WSGI Configuration
│
├── static/                    # Static Files
│   ├── css/
│   │   └── output.css        # Tailwind CSS Output
│   └── js/
│       ├── chat.js           # Chat Interface JS
│       └── upload.js         # Upload Page JS
│
├── media/                     # Uploaded Files
│   ├── uploads/              # User Uploaded CSV/Excel Files
│   └── sample_orders.csv     # Sample File
│
├── docs/                      # Documentation
│   ├── SCHEMA_DESIGN.md      # Database Schema Documentation
│   └── SYSTEM_DOCUMENTATION_TH.md  # This File
│
├── venv/                      # Python Virtual Environment
│
├── manage.py                  # Django Management Script
├── requirements.txt           # Python Dependencies
├── package.json               # Node.js Dependencies
├── tailwind.config.js         # Tailwind CSS Configuration
├── .env                       # Environment Variables (Secret)
├── .env.example               # Environment Variables Template
└── README.md                  # Project README
```

### 4.3 Module Details

#### 4.3.1 Django Models (`analytics/models.py`)

**UploadedFile Model**
- ใช้เก็บข้อมูลไฟล์ที่ผู้ใช้อัพโหลด
- Fields: filename, file, uploaded_at, file_size, row_count, status, error_message, processing_stats

**QueryHistory Model**
- ใช้เก็บประวัติคำถามและคำตอบ
- Fields: question, language, generated_sql, result_summary, row_count, execution_time, success

#### 4.3.2 ETL Module (`analytics/etl/`)

**validator.py - DataValidator Class**
```python
# ฟังก์ชันหลัก
- validate_file(file_path)          # ตรวจสอบไฟล์ทั้งหมด
- normalize_columns(df)             # แปลงคอลัมน์ไทยเป็นอังกฤษ
- check_required_columns(df)        # เช็คคอลัมน์จำเป็น
- check_data_types(df)              # เช็ค data type
- check_duplicates(df)              # เช็คข้อมูลซ้ำ
- check_negative_values(df)         # เช็คค่าติดลบ
- check_date_format(df)             # เช็ครูปแบบวันที่
```

**processor.py - ETLProcessor Class**
```python
# ETL Pipeline
- extract(file_path)                # อ่านไฟล์ CSV/Excel
- transform(df)                     # แปลงข้อมูล
  ├── clean_data()                  # ทำความสะอาด
  ├── prepare_dimensions()          # เตรียม dimension data
  └── prepare_fact_data()           # เตรียม fact data
- load(transformed_data)            # โหลดเข้า database
  ├── load_dimensions()             # โหลด dimension tables
  └── load_fact()                   # โหลด fact table
- process_csv(file_path)            # รัน pipeline ทั้งหมด
```

#### 4.3.3 AI Module (`analytics/ai/`)

**query_engine.py - QueryEngine Class**
```python
# AI Query Processing
- generate_sql(question, language)  # แปลง NL → SQL
- validate_sql(sql)                 # ตรวจสอบความปลอดภัย
- execute_query(sql)                # รัน SQL บน ClickHouse
- summarize_results(results)        # สรุปผลลัพธ์
- process_question(question)        # Pipeline ทั้งหมด
```

#### 4.3.4 Views (`analytics/views.py`)

**Frontend Views**
```python
- home(request)                     # หน้าแรก (Chat)
- upload_page(request)              # หน้าอัพโหลด
```

**API Endpoints**
```python
- query_api(request)                # POST /api/query/
- upload_api(request)               # POST /api/upload/
- query_history_api(request)        # GET /api/history/
- upload_history_api(request)       # GET /api/uploads/
- health_check(request)             # GET /api/health/
```

---

## 5. Workflow ของระบบ

### 5.1 Upload Workflow (การอัพโหลดไฟล์)

```
┌─────────────────────┐
│  1. User Uploads    │
│     CSV/Excel File  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. File Validation │
│  - Check extension  │
│  - Check file size  │
│  - Save to media/   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. Data Validation │
│  (DataValidator)    │
│  - Read file        │
│  - Normalize cols   │
│  - Check required   │
│  - Check types      │
│  - Check dates      │
└──────────┬──────────┘
           │
       ┌───┴───┐
       │ Valid?│
       └───┬───┘
           │
    ┌──────┴──────┐
    │             │
   No            Yes
    │             │
    ▼             ▼
┌────────┐   ┌──────────────────┐
│ Return │   │  4. ETL Pipeline │
│ Error  │   │  (ETLProcessor)  │
└────────┘   └──────────┬───────┘
                        │
                        ▼
             ┌────────────────────┐
             │  4.1 Extract       │
             │  - Read CSV/Excel  │
             │  - Handle encoding │
             └──────────┬─────────┘
                        │
                        ▼
             ┌────────────────────┐
             │  4.2 Transform     │
             │  - Clean data      │
             │  - Create date_id  │
             │  - Remove dupes    │
             │  - Prepare dims    │
             └──────────┬─────────┘
                        │
                        ▼
             ┌────────────────────┐
             │  4.3 Load          │
             │  → dim_products    │
             │  → dim_customers   │
             │  → dim_locations   │
             │  → dim_payments    │
             │  → dim_promotions  │
             │  → fact_orders     │
             └──────────┬─────────┘
                        │
                        ▼
             ┌────────────────────┐
             │  5. Update Status  │
             │  status='completed'│
             │  + statistics      │
             └──────────┬─────────┘
                        │
                        ▼
             ┌────────────────────┐
             │  6. Return Success │
             │  + row counts      │
             └────────────────────┘
```

**ตัวอย่างการทำงาน:**
1. ผู้ใช้เลือกไฟล์ `Order.completed.20240301_20240331.xlsx` (Shopee Export)
2. Frontend ส่ง POST request พร้อมไฟล์ไปที่ `/api/upload/`
3. Backend ตรวจสอบว่าเป็นไฟล์ .xlsx และขนาดไม่เกิน 50MB
4. บันทึกไฟล์ลง `media/uploads/` และสร้าง UploadedFile record (status='processing')
5. DataValidator อ่านไฟล์และตรวจสอบ:
   - พบคอลัมน์ "หมายเลขคำสั่งซื้อ" → แปลงเป็น "order_number"
   - พบคอลัมน์ "ชื่อสินค้า" → แปลงเป็น "product_name"
   - เช็คว่ามีคอลัมน์ครบถ้วน ✅
6. ETLProcessor ประมวลผล:
   - Extract: อ่าน Excel ได้ 1,500 rows
   - Transform: ลบ duplicate 18 rows, เหลือ 1,482 rows
   - Load: โหลดเข้า ClickHouse
7. อัพเดท status='completed', row_count=1482
8. ส่ง response กลับ: `{"success": true, "stats": {"rows_processed": 1500, "rows_inserted": 1482}}`

### 5.2 Query Workflow (การถามคำถาม)

```
┌─────────────────────┐
│  1. User Types      │
│     Question        │
│  "สินค้าขายดี 5     │
│   อันดับแรกคืออะไร?"│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. Send to API     │
│  POST /api/query/   │
│  {question: "...",  │
│   language: "th"}   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────┐
│  3. AI Query Engine         │
│  (QueryEngine)              │
│                             │
│  ┌───────────────────────┐  │
│  │ 3.1 Generate SQL      │  │
│  │ - Send to OpenAI GPT-4│  │
│  │ - Include DB schema   │  │
│  │ - Get SQL query       │  │
│  └──────────┬────────────┘  │
│             │               │
│             ▼               │
│  ┌───────────────────────┐  │
│  │ 3.2 Validate SQL      │  │
│  │ - Check for DELETE    │  │
│  │ - Check for DROP      │  │
│  │ - Must be SELECT      │  │
│  └──────────┬────────────┘  │
│             │               │
│     ┌───────┴────────┐      │
│     │ Valid & Safe?  │      │
│     └───────┬────────┘      │
│             │               │
│      ┌──────┴──────┐        │
│      │             │        │
│     No            Yes       │
│      │             │        │
│      ▼             ▼        │
│  ┌────────┐  ┌───────────┐ │
│  │ Return │  │ 3.3 Exec  │ │
│  │ Error  │  │ on ClickH │ │
│  └────────┘  └─────┬─────┘ │
│                    │        │
│                    ▼        │
│             ┌──────────────┐│
│             │ 3.4 Get      ││
│             │ Results      ││
│             └──────┬───────┘│
│                    │        │
│                    ▼        │
│             ┌──────────────┐│
│             │ 3.5 Summarize││
│             │ with GPT-4   ││
│             └──────┬───────┘│
└────────────────────┼────────┘
                     │
                     ▼
          ┌──────────────────┐
          │ 4. Save to       │
          │    QueryHistory  │
          └──────────┬───────┘
                     │
                     ▼
          ┌──────────────────┐
          │ 5. Return to UI  │
          │ - SQL            │
          │ - Explanation    │
          │ - Results (table)│
          │ - Summary        │
          └──────────────────┘
```

**ตัวอย่างการทำงาน:**

**Input:**
```json
{
  "question": "สินค้าขายดี 5 อันดับแรกคืออะไร?",
  "language": "th"
}
```

**Step 1: Generate SQL**
- ส่งคำถามพร้อม database schema ไปที่ OpenAI GPT-4
- GPT-4 วิเคราะห์และสร้าง SQL:
```sql
SELECT
    p.product_name,
    SUM(f.quantity) as total_quantity,
    SUM(f.total_amount) as total_revenue
FROM fact_orders f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_quantity DESC
LIMIT 5
```

**Step 2: Validate SQL**
- ✅ เป็น SELECT query
- ✅ ไม่มี DELETE, DROP, UPDATE
- ✅ ไม่ใช้ system tables

**Step 3: Execute**
- รัน SQL บน ClickHouse
- ได้ผลลัพธ์ 5 แถว:
```json
[
  {"product_name": "iPhone 15 Pro", "total_quantity": 150, "total_revenue": 5850000},
  {"product_name": "Samsung Galaxy S24", "total_quantity": 120, "total_revenue": 3960000},
  ...
]
```

**Step 4: Summarize**
- ส่งผลลัพธ์ไปให้ GPT-4 สรุป:
```
"สินค้าขายดี 5 อันดับแรก ได้แก่ iPhone 15 Pro (ขายได้ 150 ชิ้น มูลค่า 5.85 ล้านบาท),
Samsung Galaxy S24 (120 ชิ้น), MacBook Air M3 (95 ชิ้น), AirPods Pro (88 ชิ้น),
และ iPad Pro (75 ชิ้น)"
```

**Output:**
```json
{
  "success": true,
  "question": "สินค้าขายดี 5 อันดับแรกคืออะไร?",
  "sql": "SELECT p.product_name, ...",
  "explanation": "คำสั่ง SQL นี้ดึงข้อมูลสินค้าจากตารางคำสั่งซื้อ...",
  "results": [...],
  "row_count": 5,
  "summary": "สินค้าขายดี 5 อันดับแรก ได้แก่...",
  "execution_time": 0.25
}
```

---

## 6. เทคโนโลยีและเครื่องมือที่ใช้

### 6.1 Backend Technologies

#### 6.1.1 Python 3.10+
- **ภาษาหลักของโปรเจค**
- รองรับ async/await, type hints
- เวอร์ชั่น: 3.10 หรือสูงกว่า

#### 6.1.2 Django 5.0.1
- **Web Framework หลัก**
- ใช้สำหรับ: URL routing, Views, Templates, Models, Admin panel
- ติดตั้ง: `pip install Django==5.0.1`

#### 6.1.3 Django REST Framework 3.14.0
- **สำหรับสร้าง RESTful APIs**
- ใช้สำหรับ: API endpoints, Serializers, Authentication
- ติดตั้ง: `pip install djangorestframework==3.14.0`

#### 6.1.4 ClickHouse Database
- **OLAP Database สำหรับวิเคราะห์ข้อมูล**
- รองรับข้อมูลขนาดใหญ่ (billions of rows)
- Query เร็วมาก (milliseconds)
- Driver: `clickhouse-driver==0.2.7`
- ติดตั้ง ClickHouse: https://clickhouse.com/docs/en/install

#### 6.1.5 Pandas 2.2.0
- **Data Processing และ ETL**
- ใช้สำหรับ: อ่าน CSV/Excel, ทำความสะอาดข้อมูล, Transform
- ติดตั้ง: `pip install pandas==2.2.0`

#### 6.1.6 OpenAI 1.12.0
- **OpenAI API Client**
- ใช้ GPT-4 model สำหรับ:
  - แปลง Natural Language → SQL
  - สรุปผลลัพธ์
  - อธิบาย SQL
- ติดตั้ง: `pip install openai==1.12.0`
- ต้องมี: OpenAI API Key

#### 6.1.7 LangChain 0.1.6
- **LLM Application Framework**
- ใช้สำหรับ: จัดการ prompts, chains, agents
- ติดตั้ง: `pip install langchain==0.1.6 langchain-openai==0.0.5`

#### 6.1.8 อื่นๆ
- **python-dotenv**: จัดการ environment variables
- **openpyxl**: อ่านไฟล์ Excel
- **django-cors-headers**: CORS support
- **pytest**: Testing framework

### 6.2 Frontend Technologies

#### 6.2.1 HTML5 & CSS3
- **โครงสร้างและสไตล์ของหน้าเว็บ**
- ใช้ semantic HTML
- CSS Grid & Flexbox

#### 6.2.2 Tailwind CSS 3.4.13
- **Utility-First CSS Framework**
- ใช้สำหรับ: styling ทุกอย่างในโปรเจค
- Apple-inspired design (สะอาด, ทันสมัย)
- ติดตั้ง: `npm install tailwindcss@3.4.13 postcss autoprefixer`

#### 6.2.3 Vanilla JavaScript
- **Client-side Scripting**
- ไม่ใช้ framework (ไม่มี React, Vue)
- ใช้สำหรับ:
  - Fetch API สำหรับเรียก backend APIs
  - DOM manipulation
  - Form handling
  - Drag and drop
  - File upload with progress

#### 6.2.4 Font Awesome
- **Icon Library**
- ใช้ไอคอนต่างๆ ใน UI

### 6.3 Development Tools

#### 6.3.1 Git
- **Version Control**
- บันทึกการเปลี่ยนแปลงของโค้ด

#### 6.3.2 VS Code (แนะนำ)
- **Code Editor**
- Extensions แนะนำ:
  - Python
  - Django
  - Tailwind CSS IntelliSense
  - Prettier

#### 6.3.3 Node.js & npm
- **สำหรับ Tailwind CSS**
- ติดตั้ง: https://nodejs.org/
- เวอร์ชั่น: 16+ แนะนำ

#### 6.3.4 Postman (แนะนำ)
- **ทดสอบ APIs**
- ทดสอบ `/api/query/`, `/api/upload/` endpoints

### 6.4 การติดตั้ง Dependencies ทั้งหมด

#### Python Dependencies (requirements.txt)
```txt
Django==5.0.1
djangorestframework==3.14.0
clickhouse-driver==0.2.7
pandas==2.2.0
numpy==1.26.3
openai==1.12.0
langchain==0.1.6
langchain-openai==0.0.5
python-dotenv==1.0.1
python-dateutil==2.8.2
pytz==2024.1
openpyxl==3.1.2
django-cors-headers==4.3.1
pytest==8.0.0
pytest-django==4.7.0
```

**ติดตั้ง:**
```bash
pip install -r requirements.txt
```

#### Node.js Dependencies (package.json)
```json
{
  "dependencies": {
    "tailwindcss": "^3.4.13",
    "postcss": "^8.4.47",
    "autoprefixer": "^10.4.20"
  }
}
```

**ติดตั้ง:**
```bash
npm install
```

### 6.5 Environment Variables (.env)

สร้างไฟล์ `.env` ในโฟลเดอร์ root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI API
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# ClickHouse Database
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=sales_analytics

# Upload Settings
MAX_UPLOAD_SIZE=52428800  # 50MB in bytes
```

---

## 7. Database Schema Design

### 7.1 Star Schema Overview

ระบบใช้ **Star Schema** ซึ่งเป็น Design Pattern ที่เหมาะสำหรับ Data Warehouse และ OLAP:

```
         dim_dates
              │
              │
dim_products──┼──fact_orders──dim_customers
              │         │
        dim_payments    ├──dim_locations
              │         │
        dim_promotions──┘
```

### 7.2 Fact Table

#### fact_orders (ตารางหลัก - เก็บธุรกรรม)

| Column | Type | Description |
|--------|------|-------------|
| order_id | UInt64 | Primary Key (auto-increment) |
| order_number | String | เลขที่คำสั่งซื้อ |
| date_id | UInt32 | FK → dim_dates |
| product_id | UInt32 | FK → dim_products |
| customer_id | UInt32 | FK → dim_customers |
| payment_id | UInt16 | FK → dim_payments |
| promotion_id | Nullable(UInt16) | FK → dim_promotions |
| location_id | UInt16 | FK → dim_locations |
| quantity | UInt32 | จำนวนสินค้า |
| unit_price | Decimal(10,2) | ราคาต่อหน่วย |
| discount_amount | Decimal(10,2) | ส่วนลด |
| tax_amount | Decimal(10,2) | ภาษี |
| shipping_cost | Decimal(10,2) | ค่าส่ง |
| total_amount | Decimal(10,2) | ยอดรวม |
| created_at | DateTime | เวลาสร้าง order |

**Indexes:** ORDER BY (date_id, product_id, customer_id)
**Partitioning:** PARTITION BY toYYYYMM(created_at)

### 7.3 Dimension Tables

#### dim_products (ข้อมูลสินค้า)
- product_id, sku, product_name, category, subcategory, unit_price, cost

#### dim_customers (ข้อมูลลูกค้า)
- customer_id, customer_name, email, phone, location_id, created_at

#### dim_dates (มิติเวลา)
- date_id, date, year, month, day, quarter, day_of_week, month_name, is_weekend

#### dim_payments (วิธีชำระเงิน)
- payment_id, payment_method, payment_gateway, is_online

#### dim_promotions (โปรโมชั่น)
- promotion_id, promo_code, promo_name, discount_type, discount_value, start_date, end_date

#### dim_locations (สถานที่)
- location_id, province, city, district, postal_code, region

### 7.4 ตัวอย่าง SQL Queries

**ยอดขายรวมตามเดือน:**
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

**สินค้าขายดี Top 5 ในกรุงเทพ:**
```sql
SELECT
    p.product_name,
    SUM(f.quantity) as total_sold,
    SUM(f.total_amount) as revenue
FROM fact_orders f
JOIN dim_products p ON f.product_id = p.product_id
JOIN dim_locations l ON f.location_id = l.location_id
WHERE l.province = 'Bangkok'
GROUP BY p.product_name
ORDER BY total_sold DESC
LIMIT 5
```

---

## 8. การติดตั้งและใช้งาน

### 8.1 ความต้องการของระบบ (System Requirements)

#### ฮาร์ดแวร์ขั้นต่ำ:
- CPU: 4 cores
- RAM: 8 GB (แนะนำ 16 GB)
- Storage: 20 GB (สำหรับ system + data)

#### ซอฟต์แวร์ที่ต้องมี:
- ✅ Windows 10/11, macOS, หรือ Linux
- ✅ Python 3.10 หรือสูงกว่า
- ✅ Node.js 16+ (สำหรับ Tailwind CSS)
- ✅ ClickHouse Server
- ✅ Git (แนะนำ)

### 8.2 ขั้นตอนการติดตั้ง

#### Step 1: Clone/Download โปรเจค
```bash
cd C:\Users\HP
# หากมี Git
git clone <repository-url>
# หรือ download ZIP แล้ว extract
```

#### Step 2: สร้าง Virtual Environment
```bash
cd smart-sales-analytics
python -m venv venv
```

#### Step 3: Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### Step 4: ติดตั้ง Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 5: ติดตั้ง Node.js Dependencies
```bash
npm install
```

#### Step 6: สร้างไฟล์ .env
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

แก้ไขไฟล์ `.env`:
```env
SECRET_KEY=your-django-secret-key-here
OPENAI_API_KEY=sk-proj-your-openai-api-key
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
```

#### Step 7: ติดตั้ง ClickHouse

**Windows:**
1. ดาวน์โหลดจาก: https://clickhouse.com/docs/en/install
2. ติดตั้งและ start service

**macOS (Homebrew):**
```bash
brew install clickhouse
brew services start clickhouse
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y apt-transport-https ca-certificates dirmngr
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8919F6BD2B48D754
echo "deb https://packages.clickhouse.com/deb stable main" | sudo tee /etc/apt/sources.list.d/clickhouse.list
sudo apt-get update
sudo apt-get install -y clickhouse-server clickhouse-client
sudo service clickhouse-server start
```

#### Step 8: สร้าง ClickHouse Database และ Tables
```bash
python manage.py shell
```

```python
from analytics.database import ch_manager
ch_manager.create_database()
ch_manager.create_tables()
```

#### Step 9: Run Django Migrations
```bash
python manage.py migrate
```

#### Step 10: สร้าง Django Superuser (Optional)
```bash
python manage.py createsuperuser
```

#### Step 11: Build Tailwind CSS
```bash
npx tailwindcss -i static/css/input.css -o static/css/output.css --watch
```
(เปิดทิ้งไว้ใน terminal หนึ่ง)

#### Step 12: Start Django Server
เปิด terminal ใหม่:
```bash
cd smart-sales-analytics
venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000
```

### 8.3 เข้าใช้งานระบบ

เปิด browser:
- **หน้าแรก (Chat):** http://localhost:8000/
- **หน้าอัพโหลด:** http://localhost:8000/upload/
- **Django Admin:** http://localhost:8000/admin/

### 8.4 ทดสอบระบบ

#### 8.4.1 ทดสอบการอัพโหลด
1. ไปที่ http://localhost:8000/upload/
2. คลิก "Download Sample" เพื่อดาวน์โหลดไฟล์ตัวอย่าง
3. อัพโหลดไฟล์ตัวอย่าง
4. ระบบจะประมวลผลและแสดงสถิติ

#### 8.4.2 ทดสอบการถามคำถาม
1. ไปที่ http://localhost:8000/
2. พิมพ์คำถาม: "สินค้าขายดี 5 อันดับแรกคืออะไร?"
3. คลิก Send หรือกด Enter
4. ระบบจะแสดง:
   - SQL query ที่สร้างขึ้น
   - คำอธิบาย SQL
   - ตารางผลลัพธ์
   - สรุปคำตอบ

### 8.5 คำถามตัวอย่างที่ใช้งานได้

**ภาษาไทย:**
- "สินค้าขายดี 5 อันดับแรกคืออะไร?"
- "ยอดขายรวมในกรุงเทพเดือนนี้เท่าไหร่?"
- "ช่องทางการชำระเงินไหนที่ใช้บ่อยที่สุด?"
- "โค้ดส่งฟรีถูกใช้กี่ครั้ง?"
- "ลูกค้าซื้อสินค้ามากที่สุด 10 คนคือใคร?"

**English:**
- "What are the top 5 best-selling products?"
- "Total sales in Bangkok this month?"
- "Which payment method is most popular?"
- "How many times was the free shipping code used?"
- "Who are the top 10 customers by purchase value?"

### 8.6 Troubleshooting

#### ปัญหา: ClickHouse connection refused
**วิธีแก้:**
```bash
# ตรวจสอบว่า ClickHouse ทำงานอยู่หรือไม่
# Windows
sc query clickhouse-server

# Linux/macOS
sudo service clickhouse-server status
# หรือ
brew services list
```

#### ปัญหา: OpenAI API Error
**วิธีแก้:**
- เช็คว่า `.env` มี `OPENAI_API_KEY` ที่ถูกต้อง
- เช็ค API quota: https://platform.openai.com/usage

#### ปัญหา: Upload fails with "Missing columns"
**วิธีแก้:**
- ตรวจสอบว่าไฟล์มีคอลัมน์ที่จำเป็น:
  - order_number, order_date, product_name, unit_price, total_amount
- หากเป็นไฟล์จาก Shopee ให้ใช้ไฟล์ที่ export มาโดยตรง (ไม่ต้องแก้ไข)

#### ปัญหา: Tailwind CSS ไม่ทำงาน
**วิธีแก้:**
```bash
# Build CSS ใหม่
npx tailwindcss -i static/css/input.css -o static/css/output.css

# Collect static files
python manage.py collectstatic --noinput
```

---

## 9. สรุป

### 9.1 จุดเด่นของระบบ

1. **ใช้งานง่าย**: ไม่ต้องมีความรู้ SQL หรือโปรแกรมมิ่ง
2. **รวดเร็ว**: Query ข้อมูลล้านแถวภายในไม่กี่วินาที
3. **อัจฉริยะ**: ใช้ AI แปลงภาษาธรรมดาเป็น SQL
4. **รองรับภาษาไทย**: เข้าใจข้อมูลจากแพลตฟอร์มไทยเช่น Shopee
5. **ยืดหยุ่น**: รองรับข้อมูลหลายรูปแบบ (CSV, Excel)
6. **ปลอดภัย**: ป้องกัน SQL Injection และคำสั่งอันตราย

### 9.2 การพัฒนาต่อในอนาคต

- 📊 เพิ่มกราฟและ visualization
- 📱 Mobile app
- 🔄 Real-time data sync
- 📧 Email reports
- 🤖 AI recommendations
- 🌐 Multi-language support (Chinese, English, etc.)

### 9.3 การติดต่อและสนับสนุน

หากมีคำถามหรือพบปัญหา กรุณาติดต่อ:
- GitHub Issues: [repository-url]/issues
- Email: support@example.com

---

**เอกสารนี้อัพเดทล่าสุด:** วันที่ 15 ตุลาคม 2568
**เวอร์ชั่นระบบ:** 1.0.0
**ผู้จัดทำ:** Smart Sales Analytics Team

---
