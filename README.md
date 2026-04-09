# Sales Forecasting Data Pipeline

A comprehensive data pipeline for sales forecasting that integrates SQL Server sales data with FRED API inflation data, processes features, trains machine learning models, and generates forecasts and reports.

## Prerequisites

- Python 3.11
- SQL Server with ODBC driver installed
- FRED API key (free from Federal Reserve Economic Data)


## First-Time Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install ODBC Driver (if not already installed)
Download and install the Microsoft ODBC Driver for SQL Server:
- [Windows](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- [Linux](https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)
- [macOS](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos)

### 3. Create Environment Variables File
Create a `.env` file in the root directory with the following variables:

```env
# SQL Server Configuration
SQLSERVER_DRIVER=ODBC Driver 18 for SQL Server (or installed driver)
SQLSERVER_SERVER=your-server-name
SQLSERVER_DATABASE=your-database-name
SQLSERVER_USERNAME=your-username
SQLSERVER_PASSWORD=your-password
SQLSERVER_ENCRYPT=yes
SQLSERVER_TRUST_CERT=yes
SQLSERVER_TIMEOUT=30
SQLSERVER_TABLE=your-sales-table-name

# FRED API Configuration
FRED_API_KEY=your-fred-api-key-here
```

**Note:** You can also set `SQLSERVER_CONN_STR` directly if you prefer a full connection string instead of individual components.

## How to Run

### Graphical User Interface (GUI)
Launch the GUI application:

```bash
python -m src.app
```

The GUI allows you to:
- Select output directory
- View real-time pipeline logs
- Run the pipeline with a button click


### Command Line Interface (CLI)
Run the pipeline from the command line:

```bash
python -m src.main
```

Optional: Specify custom output directory:
```bash
python -m src.main --output /path/to/output
```

## Configuration

All configuration variables are defined in `src/config/settings.py`. Here's what each variable controls:

### Sales Data Configuration
- `SALES_DATA_SOURCE`: Data source type ("sql" for SQL Server)
- `SALES_DATE_COLUMN`: Column name containing date information in sales data (default: "PostDate")
- `SALES_NUMERICAL_COLUMN`: Column name containing numerical sales values (default: "ShipTons")
- `SALES_COLUMNS_SQL`: List of columns to select from SQL database

### FRED API Configuration
- `BASE_YEAR`: Base year for inflation calculations (default: 2007)

### Export Configuration
- `REPORT_DIR`: Directory where reports and outputs are saved (default: ".")

### Model Configuration
- `TARGET_COL`: Target column for forecasting (default: "ShipTons")
- `SALES_LAGS`: List of lag periods to create for sales data (default: [1, 2, 3, 4, 5, 6])
- `ROLLING_WINDOWS`: Rolling window sizes for feature engineering (default: [3])
- `INFLATION_LAGS`: Lag periods for inflation data (default: [1, 2, 3])
- `FUTURE_MONTHS`: Number of months to forecast ahead (default: 24)
- `HISTORY_MONTHS`: Number of historical months to include in analysis (default: 72, which is 6 years)

## Troubleshooting

### ODBC Connection Issues
- Verify ODBC driver is installed: Check Windows ODBC Data Source Administrator
- Test connection string: Ensure server name, database, and credentials are correct
- Make sure device is connected to McWane network (onsite or VPN)

### FRED API Issues
- API Key: Verify `FRED_API_KEY` is set correctly in `.env`
- Rate Limits: FRED API has rate limits; wait between requests if needed
- Network: Ensure internet connection allows API calls

### Missing Data
- Check SQL table exists and has required columns
- Verify date ranges in data match expectations
- Ensure inflation data is available for the base year

### Python Environment
- Install all requirements: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.11)

## Project Structure

```
mcwane-final/
├── README.md
├── requirements.txt
├── .env (create this file)
├── data/
│   └── processed/          # Output directory for processed data and reports
└── src/
    ├── main.py             # CLI entry point and pipeline orchestration
    ├── app.py              # GUI application
    ├── config/
    │   └── settings.py     # Configuration variables
    ├── dao/
    │   └── sales_dao.py    # Data access layer for SQL Server
    ├── external/
    │   └── fred_client.py  # FRED API client for inflation data
    └── service/
        ├── pipeline_service.py    # Main pipeline logic
        ├── model_service.py       # Machine learning model training
        └── sales_service.py       # Sales data processing
```