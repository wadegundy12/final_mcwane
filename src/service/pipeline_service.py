# src/service/pipeline_service.py
"""
Orchestrates the complete data pipeline:
- Fetches external data (FRED API)
- Loads internal data (SQL)
- Merges and processes
- Outputs results
"""
from pathlib import Path
import pandas as pd
from datetime import datetime
from service.model_service import ModelService
from external.fred_client import FredClient
from service.sales_service import SalesService
from config.settings import BASE_YEAR, REPORT_DIR


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

        # Step 4: Save results
        self._save_results(lagged, output_dir)
        
        # Step 5: Generate metrics
        metrics = self._generate_metrics(lagged)
        
        today = datetime.now().strftime('%m-%d-%Y')
        return {
            'processed_data': output_dir / f'{today}-report.xlsx',
            'metrics': output_dir / 'metrics.json',
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
        df = df.dropna(how='all').dropna(axis=1, how='all')
        return df
    
    def _save_results(self, data, output_dir):
        """Save to Excel"""
        today = datetime.now().strftime('%m-%d-%Y')
        output_dir.mkdir(parents=True, exist_ok=True)
        data.to_excel(output_dir / f'{today}-report.xlsx')
    
    def _generate_metrics(self, data):
        """Calculate and save metrics"""
        metrics = {
            'row_count': len(data),
            'date_range': [data.index.min(), data.index.max()],
            # Add your metrics
        }
        return metrics