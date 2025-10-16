# 🚀 Quick Start - 3 Steps to Running

## Your Server is Already Running! ✅

**Current Status:**
- ✅ Django server running at http://localhost:8000
- ✅ Sample data file ready: `sample_orders.csv`
- ⚠️ ClickHouse database needs setup
- ⚠️ OpenAI API key needs configuration

---

## Step 1: Configure OpenAI API Key (1 minute)

1. Get your API key from https://platform.openai.com/api-keys
2. Open `.env` file in project root
3. Find the line: `OPENAI_API_KEY=`
4. Add your key: `OPENAI_API_KEY=sk-your-actual-key-here`
5. Save the file

**No restart needed** - the app will use the key immediately.

---

## Step 2: Setup ClickHouse Database (2 minutes)

### Option A: Install ClickHouse (Recommended)

**On Windows (WSL2):**
```bash
wsl
curl https://clickhouse.com/ | sh
sudo ./clickhouse install
sudo clickhouse start
```

**On Windows (Native):**
Download from: https://clickhouse.com/docs/en/install

### Option B: Skip for Demo (Limited Functionality)
You can test the UI without ClickHouse, but queries and uploads won't work.

### Initialize Database

Once ClickHouse is running:

```bash
# In project directory
venv\Scripts\activate
python manage.py setup_clickhouse
```

This creates all tables and loads reference data.

---

## Step 3: Create Admin User (30 seconds)

```bash
python manage.py createsuperuser
```

Enter:
- Username: admin
- Email: admin@example.com
- Password: (your choice)

---

## 🎉 You're Ready!

### Access the Application:

1. **Main Chat**: http://localhost:8000
   - Ask: "What are the top 5 products?"

2. **Upload Data**: http://localhost:8000/upload/
   - Upload: `sample_orders.csv`

3. **Admin Panel**: http://localhost:8000/admin/
   - Login with your superuser credentials

---

## 📊 Test with Sample Data

1. Go to http://localhost:8000/upload/
2. Drag and drop `sample_orders.csv`
3. Wait for "Success" message
4. Go to http://localhost:8000
5. Ask: "What are the top 5 best-selling products?"

---

## 🛠️ Useful Commands

### Start Server (if stopped)
```bash
venv\Scripts\activate
python manage.py runserver
```

Or just run: `run.bat`

### Check Server Status
Visit: http://localhost:8000/api/health/

### View Logs
The console shows all requests and errors in real-time.

### Stop Server
Press `Ctrl+C` in the terminal

---

## 📱 Mobile Access

To access from other devices on your network:

1. Find your computer's IP address:
   ```bash
   ipconfig
   ```

2. Look for "IPv4 Address" (e.g., 192.168.1.100)

3. Access from mobile/tablet:
   ```
   http://192.168.1.100:8000
   ```

---

## ❓ Troubleshooting

### "OpenAI API key not configured"
→ Edit `.env` and add your key (see Step 1)

### "Database connection failed"
→ Install and start ClickHouse (see Step 2)

### "Module not found" error
→ Run: `venv\Scripts\activate` then `pip install -r requirements.txt`

### Port 8000 already in use
→ Use different port: `python manage.py runserver 8080`

---

## 🎯 Next Actions

**Priority 1 - To Use AI Chat:**
- [ ] Add OpenAI API key to `.env`

**Priority 2 - To Store Data:**
- [ ] Install ClickHouse
- [ ] Run `python manage.py setup_clickhouse`

**Priority 3 - Full Access:**
- [ ] Create superuser
- [ ] Upload `sample_orders.csv`
- [ ] Try example questions

---

## 📚 Learn More

- **Full Usage Guide**: Read `USAGE.md`
- **Deployment Guide**: Read `DEPLOYMENT.md`
- **API Documentation**: Visit `/api/` endpoints
- **Schema Design**: Read `docs/SCHEMA_DESIGN.md`

---

## 💡 Example Questions to Ask

Once data is uploaded, try these:

```
"What are the top 5 best-selling products?"
"Show me sales by province"
"Which payment method is most popular?"
"Total revenue in January 2024"
"Products in Electronics category"
"Customer count by city"
```

---

**Need help?** The server is running and ready! Just complete the 3 steps above. 🚀
