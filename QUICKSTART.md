# 🚀 Quick Start Guide - Inventory Optimization System

## What is this project?

This is a **sophisticated AI-powered Inventory Optimization System** that helps businesses:

- 📊 **Predict sales** using machine learning (LSTM models)
- 🎯 **Optimize inventory** with smart recommendations
- 📈 **Generate reports** automatically using AI
- 🔄 **Automate decisions** on restocking, clearance sales, and donations
- 🌍 **Handle multi-location** inventory across different stores

## 🎯 Key Features

### 🤖 AI-Powered Analytics
- **LSTM Neural Networks** for sales forecasting
- **Google Gemini AI** for intelligent report generation
- **Automated decision-making** for inventory actions

### 📊 Smart Dashboard
- **Real-time inventory tracking**
- **Store performance analytics**
- **Geographic and demographic filtering**
- **Interactive store reports**

### 🔄 Automated Workflows
- **Data synchronization** between databases
- **Model retraining** when needed
- **Intelligent restocking** recommendations
- **Expiry management** with action suggestions

## ⚡ Super Quick Demo (5 minutes)

### 1. **Prerequisites Check**
```bash
# Check Python version (need 3.8+)
python --version

# Check if pip is working
pip --version
```

### 2. **Install & Setup** 
```bash
# Navigate to project
cd "c:\Users\shash\Desktop\Inventory_Optimization-main"

# Dependencies are already installed in venv!
# Just activate the environment:
venv\Scripts\activate

# Copy environment template
copy .env.example .env
```

### 3. **Configure (REQUIRED)**
Edit the `.env` file with your settings:
```env
# Minimum required for demo:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_key

# For local demo (optional):
AUTODB_NAME=demo_db
AUTODB_USER=postgres
AUTODB_PASSWORD=your_password
AUTODB_HOST=localhost
```

### 4. **Run the Application**
```bash
# Quick start with batch file:
start.bat

# OR manually:
cd backend
uvicorn auth_api:app --reload --host 0.0.0.0 --port 8000
```

### 5. **Access the System**
Open your browser and go to: **http://localhost:8000**

1. **Sign up** for a new account
2. **Login** with your credentials  
3. **Dashboard** will show store overview
4. **Click any store** to see detailed reports
5. **AI-generated insights** and recommendations

## 🏗️ Full Production Setup

### Database Setup (PostgreSQL)
```sql
-- Create database
CREATE DATABASE inventory_optimization;

-- Run schema
\i autodb_project/schema.sql
```

### Supabase Setup
1. Go to [supabase.io](https://supabase.io)
2. Create new project
3. Create `userdb` table:
```sql
CREATE TABLE userdb (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Google Gemini API
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Create API key
3. Add to `.env` file

## 🎪 Demo Scenarios

### Scenario 1: Store Manager Dashboard
- View all stores with geographic filters
- See real-time inventory status
- Get AI-powered recommendations

### Scenario 2: Inventory Optimization
- System predicts sales for next 14 days
- Recommends actions (restock, clearance, donate)
- Generates automated reports

### Scenario 3: Multi-Store Analytics
- Compare performance across locations
- Identify high/low performing stores
- Optimize inventory distribution

## 🔧 Troubleshooting

### Common Issues:

**"Module not found" errors:**
```bash
# Make sure venv is activated
venv\Scripts\activate
pip install -r requirements.txt
```

**Database connection errors:**
- Check PostgreSQL is running
- Verify credentials in `.env`
- Make sure database exists

**API key errors:**
- Verify Supabase URL and key
- Check Gemini API key validity
- Ensure proper permissions

**Port already in use:**
```bash
# Use different port
uvicorn auth_api:app --reload --port 8001
```

## 📞 Need Help?

1. **Check the logs** in terminal for error messages
2. **Verify .env configuration** - most issues are here
3. **Test database connection** separately
4. **Check API key permissions**

## 🎯 What makes this special?

This isn't just another inventory system. It's a **complete AI-driven solution** that:

- **Learns from your data** to make better predictions
- **Adapts to seasonal patterns** and local preferences  
- **Automates complex decisions** that usually require expert analysis
- **Scales with your business** from single store to enterprise
- **Integrates modern AI** (Google Gemini) with proven ML techniques (LSTM)

Perfect for:
- 🏪 **Retail chains** with multiple locations
- 🍕 **Restaurants** managing perishable inventory  
- 📱 **E-commerce** optimizing warehouse stock
- 🏥 **Healthcare** managing medical supplies
- 🎓 **Educational** learning advanced AI/ML concepts

---

**Ready to optimize your inventory with AI?** 🚀

Start with the 5-minute demo above, then explore the full features!
