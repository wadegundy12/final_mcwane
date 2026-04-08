# Sources Configurations

SALES_DATA_SOURCE = "sql"
SALES_OUTPUT_FILE_NAME = "processed_sales_data.csv"
SALES_COLUMNS = [
    "PostDate",
    "ShipTons",
    "CompanyID"
]
SALES_DATE_COLUMN = "PostDate"
SALES_NUMERICAL_COLUMN = "ShipTons"
SALES_COMPANY_ID_COLUMN = "CompanyID"
SALES_COMPANY_ID = "MDUT"

# TODO: Check if CompanyID is in SQL DB. If so, update sql_sales_dao.py with SALES_COLUMNS
SALES_COLUMNS_SQL = [
    "PostDate",
    "ShipTons"
]


OPPORTUNITIES_DATA_SOURCE = "excel"
OPPORTUNITIES_OUTPUT_FILE_NAME = "processed_opportunities_data.csv"
OPPORTUNITIES_COLUMNS = [
    "CloseDate",
    "Total_Tons__c"
]

OPPORTUNITIES_DATE_COLUMN = "CloseDate"
OPPORTUNITIES_NUMERICAL_COLUMN = "Total_Tons__c"

#FRED API Configuration
BASE_YEAR = 2007

# Sales Excel Configurations
SALES_EXL_FILE_NAME = "Sales and Opportunities.xlsx"
SALES_SHEET_NAME = "Sales"
SALES_HEADER_ROW = 0

# Opportunities Excel Configurations
OPPORTUNITIES_EXL_FILE_NAME = "Sales and Opportunities.xlsx"
OPPORTUNITIES_SHEET_NAME = "Opportunities"
OPPORTUNITIES_HEADER_ROW = 1