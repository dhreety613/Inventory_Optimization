# Inventory Optimization System - Setup Guide

This is an **Inventory Optimization System** built with FastAPI, TensorFlow (LSTM), and various databases. It provides AI-powered inventory management with predictive analytics.

## 🏗️ Architecture Overview

- **Frontend**: HTML templates with modern CSS styling
- **Backend**: FastAPI web framework
- **Database**: PostgreSQL (Supabase) + local PostgreSQL
- **ML/AI**: TensorFlow with LSTM models for sales prediction
- **AI Integration**: Google Gemini for generating reports
- **Data Processing**: Pandas, NumPy for data manipulation

## 📋 Prerequisites

1. **Python 3.8+** (Python 3.12 recommended)
2. **PostgreSQL** database
3. **Supabase** account (for cloud database)
4. **Google Gemini API** key
5. **Firebase** project (optional, for initial data generation)

## 🚀 Quick Start

### Step 1: Install Dependencies

Dependencies are already installed in the virtual environment. If you need to reinstall:

```bash
# Activate virtual environment (if not already active)
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration

1. Copy the `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` file with your actual configuration:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Database Configuration
AUTODB_NAME=inventory_db
AUTODB_USER=your_db_user
AUTODB_PASSWORD=your_db_password
AUTODB_HOST=localhost
AUTODB_PORT=5432

# AI Configuration
GEMINI_API_KEY=your_gemini_api_key
```

### Step 3: Database Setup

1. **Create PostgreSQL Database:**
```sql
CREATE DATABASE inventory_db;
```

2. **Run Schema Creation:**
```bash
psql -U your_user -d inventory_db -f autodb_project/schema.sql
```

3. **Set up Supabase:**
   - Create a Supabase project
   - Create a `userdb` table for authentication:
   ```sql
   CREATE TABLE userdb (
       id SERIAL PRIMARY KEY,
       username VARCHAR(255) UNIQUE NOT NULL,
       password VARCHAR(255) NOT NULL,
       email VARCHAR(255) UNIQUE NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

### Step 4: Run the Application

```bash
# Navigate to backend directory
cd backend

# Start the FastAPI server
uvicorn auth_api:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at: `http://localhost:8000`

## 📁 Project Structure

```
Inventory_Optimization/
├── backend/
│   ├── auth_api.py              # Main FastAPI application
│   ├── templates/               # HTML templates
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── dashboard.html
│   │   ├── loading.html
│   │   └── store_report.html
│   ├── lstm_project/            # Machine Learning components
│   │   ├── lstm_utils.py        # ML utilities
│   │   ├── train_base_lstm.py   # Model training
│   │   ├── retrain_lstm_if_needed.py
│   │   └── auto_update_autodb.py
│   └── abc_engine/              # Business logic
│       ├── expiry_and_action.py
│       └── create_store_reports.py
├── autodb_project/              # Database management
│   ├── schema.sql               # Database schema
│   └── auto_update_autodb.py
├── mywhackdb_from_fireadmin/    # Firebase data generation
└── requirements.txt             # Python dependencies
```

## 🔧 Configuration Details

### Database Configuration

The system uses multiple database connections:

1. **Supabase (Cloud)**: User authentication and main data storage
2. **Local PostgreSQL**: Machine learning training data
3. **Auto DB**: Processed data for analytics

### API Keys Required

1. **Supabase**: Get from your Supabase project settings
2. **Google Gemini**: Get from Google AI Studio
3. **Firebase** (optional): For initial data generation

## 🎯 Key Features

### 1. User Authentication
- Sign up and login functionality
- Session management with Supabase

### 2. Inventory Dashboard
- Store overview with filtering by geography and religion
- Real-time inventory status

### 3. AI-Powered Analytics
- LSTM models for sales prediction
- Automated inventory recommendations
- Smart restocking suggestions

### 4. Report Generation
- Automated store reports using Google Gemini
- Action recommendations (restock, clearance, donate, etc.)
- Export capabilities

### 5. Data Processing Pipeline
- Automated data updates
- Model retraining when needed
- Real-time analytics

## 🔄 Workflow

1. **Data Collection**: Sales data from multiple stores
2. **Data Processing**: Clean and prepare data for ML
3. **Model Training**: LSTM models for sales prediction
4. **Analytics**: Generate insights and recommendations
5. **Report Generation**: Create actionable reports
6. **Decision Making**: Implement recommended actions

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify connection credentials in `.env`

2. **Module Import Error**
   - Ensure virtual environment is activated
   - Install missing dependencies: `pip install -r requirements.txt`

3. **API Key Error**
   - Verify API keys in `.env` file
   - Check key permissions and quotas

4. **Model Training Issues**
   - Ensure sufficient data is available
   - Check TensorFlow installation: `python -c "import tensorflow; print(tensorflow.__version__)"`

### Performance Optimization

1. **Database**: Use indexes for frequently queried columns
2. **ML Models**: Consider using GPU for training large models
3. **Caching**: Implement Redis for frequently accessed data

## 📚 API Endpoints

- `GET /` - Home page (redirects to signup)
- `POST /signup` - User registration
- `GET /login` - Login page
- `POST /login` - User authentication
- `GET /loading` - Processing page
- `POST /start-processing` - Trigger data processing
- `GET /dashboard` - Main dashboard
- `GET /store_report/{store_id}` - Individual store report

## 🔧 Development

### Running in Development Mode

```bash
# Start with auto-reload
uvicorn auth_api:app --reload --host 0.0.0.0 --port 8000

# Run background processes
python lstm_project/auto_update_autodb.py
python lstm_project/retrain_lstm_if_needed.py
python abc_engine/expiry_and_action.py
```

### Testing

```bash
# Run tests (if available)
pytest

# Check code quality
flake8 backend/
```

## 📄 License

This project is for educational and commercial use. Please check the license file for more details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

For support or questions, please create an issue in the repository.
