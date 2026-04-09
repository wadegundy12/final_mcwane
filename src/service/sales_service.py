
from datetime import datetime
from dao.sales_dao import SalesDAO
from config.settings import SALES_DATE_COLUMN, SALES_NUMERICAL_COLUMN
import pandas as pd

class SalesService:

    def __init__(self):
        self.sales_dao = SalesDAO()
        self.sales =self.sales_dao.get_all_sales()

    def get_sales_data(self):
        self._clean_data()
        self._aggregate_data()
        return self.sales

    def _aggregate_data(self):
        # 4. Create month period (first day of each month)
        self.sales['month'] = self.sales[SALES_DATE_COLUMN].dt.to_period('M').dt.to_timestamp()

        print(f"  - Original data: {len(self.sales)} rows")

        # 5. Aggregate by month - sum the numerical values
        print(f"  - Aggregating '{SALES_NUMERICAL_COLUMN}' by month...")
        self.sales = self.sales.groupby('month', as_index=False).agg({
            SALES_NUMERICAL_COLUMN: 'sum'
        })
        
        # Rename columns for clarity
        self.sales = self.sales.rename(columns={
            'month': 'date'
        })
        
        
        print(f"  - After monthly aggregation: {len(self.sales)} months")

        self.sales['date'] = pd.to_datetime(self.sales['date'])

        # Get current month
        current_month = pd.Timestamp(datetime.now()).to_period('M') 

        # Get last month in your data
        last_month = self.sales.iloc[-1]['date'].to_period('M')

        # If last month IS the current month → drop it
        if last_month == current_month:
            self.sales = self.sales.iloc[:-1]

        

    def _clean_data(self):
        print("Cleaning sales data...")
    
        # 1. Remove completely empty rows and columns then reset index
        self.sales = self.sales.dropna(how='all').dropna(axis=1, how='all')
        self.sales = self.sales.reset_index(drop=True)

        # 2. Convert date column to datetime
        print(f"  - Converting '{SALES_DATE_COLUMN}' to datetime...")
        self.sales[SALES_DATE_COLUMN] = pd.to_datetime(self.sales[SALES_DATE_COLUMN], errors='coerce')
        
        # Remove rows where date conversion failed
        before_date = len(self.sales)
        self.sales = self.sales.dropna(subset=[SALES_DATE_COLUMN])
        removed_dates = before_date - len(self.sales)
        if removed_dates > 0:
            print(f"  - Removed {removed_dates} rows with invalid dates")

        # 3. Ensure numerical column is numeric
        print(f"  - Converting '{SALES_NUMERICAL_COLUMN}' to numeric...")
        self.sales[SALES_NUMERICAL_COLUMN] = pd.to_numeric(self.sales[SALES_NUMERICAL_COLUMN], errors='coerce')

        # Remove rows where numerical conversion failed
        before_numeric = len(self.sales)
        self.sales = self.sales.dropna(subset=[SALES_NUMERICAL_COLUMN])
        removed_numeric = before_numeric - len(self.sales)
        if removed_numeric > 0:
            print(f"  - Removed {removed_numeric} rows with invalid numerical values")

        
       
        
