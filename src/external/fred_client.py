import requests
from requests.exceptions import RequestException
import os
import pandas as pd
from dotenv import load_dotenv

# Data for FRED API
load_dotenv()
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
FRED_API_KEY = os.getenv('FRED_API_KEY')
if not FRED_API_KEY:
    FRED_API_KEY = input("Please enter your FRED API key: ")

# Series IDs
INFLATION_RATE_ID = "CPIAUCSL"
INTEREST_RATE_ID = "FEDFUNDS"
FED_INFRA_SPEND_ID = "FGEXPND"
HOUSING_STARTS_SERIES_ID = "HOUSTNSA"


class FredClient:
    """ Client for the FRED API.

    The same base endpoint handles different series via parameters.
    Base url = https://api.stlouisfed.org/fred/series/observations

    `Documentation for fred/series/observations endpoint
    <https://fred.stlouisfed.org/docs/api/fred/series_observations.html>`__
    """

    def __init__(self, base_year: int, api_key: str = FRED_API_KEY, base_url: str = FRED_BASE_URL):
        self.session = requests.Session()
        self.base_year = base_year
        self.api_key = api_key
        self.base_url = base_url

    def _fetch_series_data(self, series_id: str, units: str = 'lin', frequency: str = 'm', method: str = 'avg'):
        """Fetch series data from FRED API.

        `Documentation for FRED Series API parameters 
        <https://fred.stlouisfed.org/docs/api/fred/series_observations.html>`__

        Parameters
        ----------
        series_id: str
            The id for a series. `series_id` in the documentation.
        units: str, optional
            A key for data value transformation. `units` in the documentation. Set to `lin` by default.
        frequency: str, optional
            A parameter that indicates a lower frequency to aggregate values to. `frequency` in the documentation. Set to `m` by default.
        method: str, optional
            A key that indicates the aggregation method used for `frequency`. `aggregation_method` in the documentation. Set to `avg` by default.

        Returns
        -------
        data: json
            FRED API Response in JSON format.

        Raises
        ------
        e: RequestException
            If API request returns any issues.
        """
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': f'{self.base_year}-01-01',
            'sort_order': 'asc',
            'units' : units,
            'frequency' : frequency,
            'aggregation_method' : method
        }
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            print("FRED API Request Successful")
        
        except RequestException as e:
            print(f"{response.status_code}: {e}")
        
        else:
            data = response.json()
            return data
        
    def _to_df(self, data, name: str = 'value'):
        """Transform data to a pandas Dataframe.
        """
        df = pd.DataFrame(data['observations'])
        
        # Transform date to datetime format and values to float, dropping N/A
        df['date'] = pd.to_datetime(df['date'])

        df['date'] = df['date'] + pd.offsets.MonthEnd(0)

        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['value'] = df['value'].ffill()
        
        df.rename(columns={'value' : name}, inplace=True)

        return df[['date', name]]
        
    def fetch_inflation_rate_data(self):
        """Fetch monthly Consumer Price Index (CPI) data from the FRED API as % change (inflation rate).
        """
        raw = self._fetch_series_data(series_id = INFLATION_RATE_ID, units = 'pch')
        df = self._to_df(data = raw, name = "inflation")
        df = df.ffill() # Solves possible missing values from government shutdowns.
        return df

    def fetch_interest_rate_data(self):
        """Fetch monthly Federal Funds Effective Rate (%) data from the FRED API.
        """
        raw = self._fetch_series_data(series_id = INTEREST_RATE_ID)
        df = self._to_df(data = raw, name = "interest_rate")
        return df

    def fetch_federal_infrastructure_spending(self):
        """Fetch quarterly Federal Government: Current Expenditures (Billions) data from the FRED API.
        """
        raw = self._fetch_series_data(series_id = FED_INFRA_SPEND_ID, frequency = 'q') # Quarterly is the most frequent!
        df = self._to_df(data = raw, name = "fed_infra_spend")
        return df

    def fetch_housing_starts(self):
        """Fetch monthly New Housing Starts (thousands) from the FRED API.
        """
        raw = self._fetch_series_data(series_id = HOUSING_STARTS_SERIES_ID)
        df = self._to_df(data = raw, name = "housing_starts")
        return df
        

    def close(self):
        """Closes session.
        """
        self.session.close()
