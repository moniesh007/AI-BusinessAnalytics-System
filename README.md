# AI-Based Business Analytics System

A CSBS mini-project that combines software development, database management, business metrics, and data visualization. It is a Flask web application for recording sales and reviewing revenue, estimated profit, product performance, and region/category summaries.

> **Note:** The "AI insights" in this starter project are transparent, rule-based business insights generated from recorded data. They are not a trained machine-learning model and should not be treated as guaranteed predictions.

## Features
- Business dashboard with revenue, estimated gross profit, units sold, order-record count, and margin.
- Charts for monthly revenue, category revenue, and regional revenue.
- Rule-based business insights from current data.
- Add, search, and delete sales records.
- Import sales from CSV and export records to CSV.
- SQLite database created automatically.
- Seeded sample records for demonstration.
- Responsive layout.

## Tech stack
- Python 3
- Flask
- Flask-SQLAlchemy / SQLite
- Pandas (CSV import)
- HTML, CSS, JavaScript
- Chart.js (charts loaded from CDN)

## Run locally

### 1. Install Python
Use Python 3.10 or newer.

### 2. Create and activate a virtual environment
Windows:
```powershell
py -m venv .venv
.venv\Scripts\activate
```
macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the app
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your browser.

The database is created at `instance/business_analytics.db` the first time the app runs. Demo data is inserted only when the database is empty.

## CSV format
CSV import requires these exact column names:
```csv
sale_date,product,category,quantity,unit_price,unit_cost,customer,region
2026-10-01,Wireless Mouse,Electronics,4,699,380,Online Store,Chennai
```
Dates should be parseable by Pandas (recommended format `YYYY-MM-DD`). Quantity must be a positive whole number. Prices and costs cannot be negative.

A sample file is included at `data/sample_sales.csv`.

## Main pages
- `/` — Dashboard
- `/sales` — Search and manage sales
- `/sales/add` — Add a sales record
- `/import` — Import CSV
- `/export` — Download CSV
- `/about` — Project details

## Business calculations
- Revenue = quantity × unit price
- Estimated cost = quantity × unit cost
- Estimated gross profit = revenue − estimated cost
- Gross profit margin (%) = estimated gross profit ÷ revenue × 100

These calculations exclude taxes, shipping, discounts, overheads, and returns unless you add them to the data model.

## Project structure
```text
ai_business_analytics_system/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── sample_sales.csv
├── instance/                 # created locally; ignored by Git
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── sales.html
│   ├── sale_form.html
│   ├── import.html
│   └── about.html
└── static/
    ├── css/style.css
    └── js/dashboard.js
```

## Upload to GitHub
1. Create a new repository on GitHub, e.g. `ai-business-analytics-system`.
2. Open a terminal in this project folder.
3. Run:
```bash
git init
git add .
git commit -m "Initial commit: AI Business Analytics System"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ai-business-analytics-system.git
git push -u origin main
```
Replace `YOUR-USERNAME` with your GitHub username. Do not commit passwords, secret keys, virtual environments, or the local database.

## Academic project summary
**Problem statement:** Small businesses may store sales data without a clear way to review revenue, profit, and product performance. This application organizes sales records and presents useful business summaries in one dashboard.

**Objectives:**
1. Store and manage sales records.
2. Calculate revenue and estimated gross profit.
3. Visualize monthly, category, and regional performance.
4. Generate understandable, data-based business observations.
5. Support CSV import and export for basic reporting.

**Future enhancements:** Role-based login, trained forecasting model, customer segmentation, automated PDF reports, and deployment to a hosting provider.
