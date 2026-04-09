import os
import pandas as pd
import pyodbc
from dotenv import load_dotenv
from src.config.settings import SALES_COLUMNS_SQL, SALES_DATE_COLUMN

class SalesDAO:
    """
    Loads sales from SQL Server using connection settings from .env.
    Mirrors the previous contract: returns a pandas DataFrame with SALES_COLUMNS.
    """

    def __init__(self, conn_str: str | None = None):
        # Load environment variables once when DAO is constructed
        load_dotenv(override=False)

        # Allow explicit injection for testing/overrides
        self._conn_str = conn_str or os.getenv("SQLSERVER_CONN_STR") or self._compose_conn_str_from_parts()

        if not self._conn_str:
            raise ValueError(
                "SQL Server connection string not provided. "
                "Set SQLSERVER_CONN_STR in .env or individual SQLSERVER_* variables."
            )

        # Optional: validate columns are not empty
        if not SALES_COLUMNS_SQL or not isinstance(SALES_COLUMNS_SQL, (list, tuple)):
            raise ValueError("SALES_COLUMNS must be a non-empty list/tuple of column names.")

    def _compose_conn_str_from_parts(self) -> str | None:
        """
        Compose a connection string from individual env vars if the unified one is not provided.
        """
        driver = os.getenv("SQLSERVER_DRIVER")
        server = os.getenv("SQLSERVER_SERVER")
        database = os.getenv("SQLSERVER_DATABASE")
        username = os.getenv("SQLSERVER_USERNAME")
        password = os.getenv("SQLSERVER_PASSWORD")
        encrypt = os.getenv("SQLSERVER_ENCRYPT", "yes")
        trust_cert = os.getenv("SQLSERVER_TRUST_CERT", "no")
        timeout = os.getenv("SQLSERVER_TIMEOUT", "30")

        # Require minimum viable fields
        if not all([driver, server, database, username, password]):
            return None

        # Escape braces in driver if present
        driver_braced = driver if driver.startswith("{") else f"{{{driver}}}"

        return (
            f"Driver={driver_braced};"
            f"Server={server};"
            f"Database={database};"
            f"Uid={username};"
            f"Pwd={password};"
            f"Encrypt={encrypt};"
            f"TrustServerCertificate={trust_cert};"
            f"Connection Timeout={timeout};"
        )

    def _get_connection(self):
        """
        Returns a live pyodbc connection. Caller is responsible for closing.
        """
        try:
            return pyodbc.connect(self._conn_str)
        except pyodbc.Error as e:
            # Surface meaningful errors to calling layer with context
            raise ConnectionError(f"Failed to connect to SQL Server: {e}")

    def get_all_sales(self) -> pd.DataFrame:
        """
        Reads sales rows from SQL Server and returns a DataFrame with the expected columns.
        """
        # Build a column-safe SELECT list
        table = os.getenv("SQLSERVER_TABLE")
        select_list = ", ".join(f"{table}.[{c}]" for c in SALES_COLUMNS_SQL)

        query = f"""
            SELECT {select_list}
            FROM {table}
            ORDER BY {SALES_DATE_COLUMN}
        """

        # If you need filtering or ordering, adjust here (parameterized if filters are dynamic)
        # e.g., WHERE clause with parameters: pd.read_sql(query, conn, params=[...])

        conn = None
        try:
            conn = self._get_connection()
            chunks = pd.read_sql(query, conn, chunksize=10000)

            df = pd.concat(chunks)
            return df
        except Exception as e:
            raise RuntimeError(f"Error retrieving sales data: {e}")
        finally:
            if conn is not None:
                conn.close()