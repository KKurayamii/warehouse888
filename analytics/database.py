"""
ClickHouse Database Connection Manager

This module provides a connection manager for ClickHouse database operations,
including connection pooling, query execution, and error handling.
"""

from clickhouse_driver import Client
from django.conf import settings
import logging
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ClickHouseManager:
    """
    Singleton manager for ClickHouse database connections and operations.
    """

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ClickHouseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the ClickHouse client with settings from Django configuration."""
        if self._client is None:
            try:
                self._client = Client(
                    host=settings.CLICKHOUSE_HOST,
                    port=settings.CLICKHOUSE_PORT,
                    user=settings.CLICKHOUSE_USER,
                    password=settings.CLICKHOUSE_PASSWORD,
                    database=settings.CLICKHOUSE_DATABASE,
                    send_receive_timeout=300,  # 5 minutes timeout
                )
                logger.info(f"Connected to ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}")
            except Exception as e:
                logger.error(f"Failed to connect to ClickHouse: {str(e)}")
                raise

    @property
    def client(self) -> Client:
        """Get the ClickHouse client instance."""
        if self._client is None:
            self.__init__()
        return self._client

    def test_connection(self) -> bool:
        """
        Test if the database connection is alive.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            result = self.client.execute('SELECT 1')
            return result[0][0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    def execute(self, query: str, params: Optional[Dict] = None) -> List[tuple]:
        """
        Execute a query and return all results.

        Args:
            query: SQL query string
            params: Optional parameters for parameterized queries

        Returns:
            List of result tuples

        Raises:
            Exception: If query execution fails
        """
        try:
            logger.debug(f"Executing query: {query}")
            result = self.client.execute(query, params or {})
            logger.debug(f"Query returned {len(result)} rows")
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            logger.error(f"Query: {query}")
            raise

    def execute_with_column_names(self, query: str, params: Optional[Dict] = None) -> tuple:
        """
        Execute a query and return results with column names.

        Args:
            query: SQL query string
            params: Optional parameters for parameterized queries

        Returns:
            Tuple of (data, columns) where columns is a list of column names

        Raises:
            Exception: If query execution fails
        """
        try:
            logger.debug(f"Executing query with columns: {query}")
            result = self.client.execute(query, params or {}, with_column_types=True)

            # Extract column names from column types
            columns = [col[0] for col in result[1]]
            data = result[0]

            logger.debug(f"Query returned {len(data)} rows with {len(columns)} columns")
            return data, columns
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            logger.error(f"Query: {query}")
            raise

    def execute_dict(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results as list of dictionaries.

        Args:
            query: SQL query string
            params: Optional parameters for parameterized queries

        Returns:
            List of dictionaries where keys are column names

        Raises:
            Exception: If query execution fails
        """
        data, columns = self.execute_with_column_names(query, params)

        # Convert to list of dicts
        results = []
        for row in data:
            results.append(dict(zip(columns, row)))

        return results

    def insert(self, table: str, data: List[Dict[str, Any]]) -> int:
        """
        Insert data into a table.

        Args:
            table: Table name
            data: List of dictionaries containing row data

        Returns:
            Number of rows inserted

        Raises:
            Exception: If insert fails
        """
        if not data:
            return 0

        try:
            # Get column names from first dict
            columns = list(data[0].keys())
            column_str = ', '.join(columns)

            # Prepare values
            values = [[row.get(col) for col in columns] for row in data]

            query = f"INSERT INTO {table} ({column_str}) VALUES"

            logger.debug(f"Inserting {len(data)} rows into {table}")
            self.client.execute(query, values)

            logger.info(f"Successfully inserted {len(data)} rows into {table}")
            return len(data)
        except Exception as e:
            logger.error(f"Insert failed: {str(e)}")
            logger.error(f"Table: {table}")
            raise

    def bulk_insert(self, table: str, columns: List[str], data: List[tuple]) -> int:
        """
        Bulk insert data into a table using raw tuples for better performance.

        Args:
            table: Table name
            columns: List of column names
            data: List of tuples containing row data

        Returns:
            Number of rows inserted

        Raises:
            Exception: If insert fails
        """
        if not data:
            return 0

        try:
            column_str = ', '.join(columns)
            query = f"INSERT INTO {table} ({column_str}) VALUES"

            logger.debug(f"Bulk inserting {len(data)} rows into {table}")
            self.client.execute(query, data)

            logger.info(f"Successfully bulk inserted {len(data)} rows into {table}")
            return len(data)
        except Exception as e:
            logger.error(f"Bulk insert failed: {str(e)}")
            logger.error(f"Table: {table}")
            raise

    def get_table_count(self, table: str) -> int:
        """
        Get the number of rows in a table.

        Args:
            table: Table name

        Returns:
            Row count

        Raises:
            Exception: If query fails
        """
        query = f"SELECT count() FROM {table}"
        result = self.execute(query)
        return result[0][0] if result else 0

    def table_exists(self, table: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table: Table name

        Returns:
            True if table exists, False otherwise
        """
        query = f"""
            SELECT count()
            FROM system.tables
            WHERE database = '{settings.CLICKHOUSE_DATABASE}'
            AND name = '{table}'
        """
        result = self.execute(query)
        return result[0][0] > 0 if result else False

    def get_schema(self, table: str) -> List[Dict[str, str]]:
        """
        Get the schema (column definitions) of a table.

        Args:
            table: Table name

        Returns:
            List of dicts with column information (name, type, default_kind, etc.)

        Raises:
            Exception: If query fails
        """
        query = f"""
            SELECT
                name,
                type,
                default_kind,
                default_expression,
                comment
            FROM system.columns
            WHERE database = '{settings.CLICKHOUSE_DATABASE}'
            AND table = '{table}'
            ORDER BY position
        """
        return self.execute_dict(query)

    def get_all_tables(self) -> List[str]:
        """
        Get list of all tables in the current database.

        Returns:
            List of table names
        """
        query = f"""
            SELECT name
            FROM system.tables
            WHERE database = '{settings.CLICKHOUSE_DATABASE}'
            ORDER BY name
        """
        result = self.execute(query)
        return [row[0] for row in result]

    def drop_table(self, table: str, if_exists: bool = True) -> None:
        """
        Drop a table from the database.

        Args:
            table: Table name
            if_exists: If True, use IF EXISTS clause

        Raises:
            Exception: If drop fails
        """
        exists_clause = "IF EXISTS" if if_exists else ""
        query = f"DROP TABLE {exists_clause} {table}"

        logger.warning(f"Dropping table: {table}")
        self.client.execute(query)
        logger.info(f"Successfully dropped table: {table}")

    def truncate_table(self, table: str) -> None:
        """
        Truncate (delete all data from) a table.

        Args:
            table: Table name

        Raises:
            Exception: If truncate fails
        """
        query = f"TRUNCATE TABLE {table}"

        logger.warning(f"Truncating table: {table}")
        self.client.execute(query)
        logger.info(f"Successfully truncated table: {table}")

    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        Note: ClickHouse doesn't support traditional ACID transactions,
        but this provides a context for error handling.
        """
        try:
            yield self
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise

    def close(self):
        """Close the database connection."""
        if self._client:
            self._client.disconnect()
            self._client = None
            logger.info("ClickHouse connection closed")


# Singleton instance
ch_manager = ClickHouseManager()
