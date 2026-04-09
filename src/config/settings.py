# Sales Configurations
SALES_DATA_SOURCE = "sql"
SALES_DATE_COLUMN = "PostDate"
SALES_NUMERICAL_COLUMN = "ShipTons"
SALES_COLUMNS_SQL = [
    SALES_DATE_COLUMN,
    SALES_NUMERICAL_COLUMN
]

#FRED API Configuration
BASE_YEAR = 2007

# Export Configurations
REPORT_DIR = "."

# Model Configurations
TARGET_COL = "ShipTons"

SALES_LAGS = [1, 2, 3, 4, 5, 6]
ROLLING_WINDOWS = [3]

INFLATION_LAGS = [1, 2, 3]

FUTURE_MONTHS = 24

HISTORY_MONTHS = 6*12 # Set to None to show all history