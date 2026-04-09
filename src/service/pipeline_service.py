# src/service/pipeline_service.py
"""
Orchestrates the complete data pipeline:
- Fetches external data (FRED API)
- Loads internal data (SQL)
- Merges and processes
- Outputs results
"""
import os
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for thread safety
import matplotlib.pyplot as plt
from datetime import datetime
from src.service.model_service import ModelService
from src.external.fred_client import FredClient
from src.service.sales_service import SalesService
from src.config.settings import BASE_YEAR, FUTURE_MONTHS, HISTORY_MONTHS, REPORT_DIR, TARGET_COL


class PipelineService:
    """Coordinates all data sources and transformations"""
    
    def __init__(self):
        self.fred_client = FredClient(BASE_YEAR)
        self.sales_service = SalesService()
        self.model_service = ModelService()
    
    def execute(self, output_dir: Path = None) -> dict:
        """
        Run the complete pipeline.
        
        Returns
        -------
        dict
            {
                'processed_data': Path to processed CSV,
                'metrics': Path to metrics JSON,
                'status': 'success' or 'error'
            }
        """
        output_dir = output_dir or Path(REPORT_DIR)
        
        # Step 1: Fetch external data
        external_data = self._fetch_external_data()
        print(f'  - Retrieved {external_data.shape[0]} months of external data...')
        
        # Step 2: Fetch internal data
        internal_data = self._fetch_internal_data()
        
        # Step 3: Merge and process
        processed = self._process_data(external_data, internal_data)
        print(f'Processed: {processed.shape[0]} rows and {processed.shape[1]} columns.')
        
        lagged = self.model_service.prepare_features(processed)
        self.model_service.train(lagged)
        forecasted = self.model_service.forecast(lagged)


        # Step 4: Save results
        today = datetime.now().strftime('%m-%d-%Y_%H-%M-%S')

        self._save_full_table(forecasted, output_dir, today)
        self._save_predicted_table(forecasted, output_dir, today)

        self._save_plot(forecasted, output_dir, today)
        
        # Step 5: Generate metrics
        metrics = self._generate_metrics(lagged)
        
        
        return {
            'processed_data': output_dir / f'{today}-table.xlsx',
            'metrics': output_dir / f'{today}-metrics.json',
            'status': 'success'
        }
    
    def _fetch_external_data(self):
        """Fetch data from external sources"""
        print("Retrieving external data...")
        return self.fred_client.fetch_inflation_rate_data()
    
    def _fetch_internal_data(self):
        """Fetch internal data from configured source"""
        print("Retrieving sales data...")
        return self.sales_service.get_sales_data()
    
    def _process_data(self, external, internal):
        """Merge and process"""
        internal['date'] = internal['date'] + pd.offsets.MonthEnd(0)
        df = pd.merge(internal, external, on='date', how='left')
        df["inflation"] = df["inflation"].ffill()
        df = df.dropna(how='all').dropna(axis=1, how='all')
        return df
    
    def _save_full_table(self, data, output_dir, today):
        """Save to Excel"""
        # Split data
        train = data.iloc[:-FUTURE_MONTHS]
        forecast = data.iloc[-(FUTURE_MONTHS+1):]

        if HISTORY_MONTHS is not None:
            train = train.iloc[-HISTORY_MONTHS:]
        output_dir.mkdir(parents=True, exist_ok=True)
        data.to_excel(output_dir / f'{today}-report.xlsx')

    def _save_predicted_table(self, data, output_dir, today):
        """Save only predicted values to Excel"""
        # Split data
        forecast = data.iloc[-(FUTURE_MONTHS):][["date", TARGET_COL]]

        output_dir.mkdir(parents=True, exist_ok=True)
        forecast.to_excel(output_dir / f'{today}-forecast.xlsx')
    
    def _generate_metrics(self, data):
        """Calculate and save metrics"""
        metrics = {
            'row_count': len(data),
            'date_range': [data.index.min(), data.index.max()],
            # Add your metrics
        }
        return metrics
    
    def _save_plot(self, df, output_dir, today):

        # Split data
        train = df.iloc[:-FUTURE_MONTHS]
        forecast = df.iloc[-(FUTURE_MONTHS+1):]

        if HISTORY_MONTHS is not None:
            train = train.iloc[-HISTORY_MONTHS:]

        # Plot
        plt.figure()

        plt.plot(train['date'], train['ShipTons'], label='Historical')
        plt.plot(forecast['date'], forecast['ShipTons'], label='Forecast')

        plt.legend()
        plt.xlabel('Date')
        plt.ylabel('ShipTons')
        plt.title('ShipTons Forecast')

        # Save figure
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{today}_shiptons_forecast.png")
        plt.savefig(file_path)

        print(f"Saved forecast plot to {file_path}")
        plt.close()