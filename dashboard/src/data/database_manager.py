"""
Database Connection Manager

Implements direct SQLite database access with SQLAlchemy connection pooling
and health monitoring as designed in the creative phase architecture.
"""

import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Dict, Any, Optional, List
import pandas as pd
from src.utils.config import Config
from src.utils.logging_setup import get_data_logger

logger = get_data_logger()


class DatabaseConnectionManager:
    """
    Manages SQLite database connections with pooling and health monitoring
    
    Implements the database layer from the Hybrid Cached Pipeline Architecture
    with direct SQLite access for optimal performance.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection manager
        
        Args:
            db_path: Path to SQLite database file (defaults to config)
        """
        self.db_path = db_path or Config.get_database_path()
        self.engine = None
        self._connection_count = 0
        self._initialize_engine()
        
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with optimized settings"""
        try:
            # Verify database file exists
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
            
            # Create engine with optimized SQLite settings
            self.engine = create_engine(
                f'sqlite:///{self.db_path}',
                poolclass=StaticPool,
                pool_pre_ping=True,
                pool_recycle=3600,  # Recycle connections every hour
                echo=False,  # Set to True for SQL debugging
                connect_args={
                    'check_same_thread': False,  # Allow multi-threading
                    'timeout': 30  # Connection timeout
                }
            )
            
            logger.info(f"Database engine initialized: {self.db_path}")
            
            # Perform initial health check
            self.health_check()
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection with automatic cleanup
        
        Yields:
            SQLAlchemy connection object
        """
        connection = None
        try:
            connection = self.engine.connect()
            self._connection_count += 1
            logger.debug(f"Database connection acquired (active: {self._connection_count})")
            yield connection
        except SQLAlchemyError as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
                self._connection_count -= 1
                logger.debug(f"Database connection released (active: {self._connection_count})")
    
    def health_check(self) -> bool:
        """
        Perform database health check
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            with self.get_connection() as conn:
                result = conn.execute(text("SELECT 1")).fetchone()
                if result and result[0] == 1:
                    logger.debug("Database health check passed")
                    return True
                else:
                    logger.warning("Database health check failed - unexpected result")
                    return False
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_table_info(self) -> Dict[str, List[str]]:
        """
        Get information about available tables and columns
        
        Returns:
            Dictionary mapping table names to column lists
        """
        try:
            with self.get_connection() as conn:
                inspector = inspect(conn)
                tables = {}
                
                for table_name in inspector.get_table_names():
                    columns = [col['name'] for col in inspector.get_columns(table_name)]
                    tables[table_name] = columns
                    
                logger.info(f"Database schema info retrieved: {list(tables.keys())}")
                return tables
                
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return {}
    
    def execute_query(
        self,
        query: str,
        params: Optional[List] = None,
        return_dataframe: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Execute a SQL query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            return_dataframe: Whether to return pandas DataFrame
            
        Returns:
            Query results as DataFrame or None
        """
        try:
            with self.get_connection() as conn:
                if return_dataframe:
                    # Convert list params to dict for pandas compatibility
                    if params:
                        # For pandas, we need to use named parameters or pass as tuple
                        df = pd.read_sql(query, conn, params=tuple(params))
                    else:
                        df = pd.read_sql(query, conn)
                    logger.debug(f"Query executed successfully, returned {len(df)} rows")
                    return df
                else:
                    if params:
                        result = conn.execute(text(query), params)
                    else:
                        result = conn.execute(text(query))
                        
                    logger.debug("Query executed successfully")
                    return result.fetchall()
                    
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.debug(f"Failed query: {query}")
            logger.debug(f"Query params: {params}")
            return None
    
    def get_temperature_humidity_data(
        self,
        start_time: str,
        end_time: str,
        locations: Optional[List[str]] = None
    ) -> Optional[pd.DataFrame]:
        """
        Get temperature and humidity data for specified time range and locations
        
        Args:
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
            locations: List of location names (optional)
            
        Returns:
            DataFrame with temperature/humidity data or None
        """
        query = """
        SELECT timestamp, temperature, humidity, location
        FROM temp_humidity
        WHERE timestamp BETWEEN ? AND ?
        """
        params = [start_time, end_time]
        
        if locations:
            placeholders = ','.join(['?' for _ in locations])
            query += f" AND location IN ({placeholders})"
            params.extend(locations)
        
        query += " ORDER BY timestamp"
        
        logger.debug(f"Fetching temp/humidity data: {start_time} to {end_time}")
        return self.execute_query(query, params)
    
    def get_battery_data(
        self,
        start_time: str,
        end_time: str,
        locations: Optional[List[str]] = None
    ) -> Optional[pd.DataFrame]:
        """
        Get battery data for specified time range and locations
        
        Args:
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
            locations: List of location names (optional)
            
        Returns:
            DataFrame with battery data or None
        """
        query = """
        SELECT timestamp, voltage, percentage, dischargerate, location
        FROM nano_cell_battery
        WHERE timestamp BETWEEN ? AND ?
        """
        params = [start_time, end_time]
        
        if locations:
            placeholders = ','.join(['?' for _ in locations])
            query += f" AND location IN ({placeholders})"
            params.extend(locations)
        
        query += " ORDER BY timestamp"
        
        logger.debug(f"Fetching battery data: {start_time} to {end_time}")
        return self.execute_query(query, params)
    
    def get_available_locations(self) -> List[str]:
        """
        Get list of available locations from both tables
        
        Returns:
            List of unique location names
        """
        try:
            temp_locations = self.execute_query(
                "SELECT DISTINCT location FROM temp_humidity ORDER BY location"
            )
            battery_locations = self.execute_query(
                "SELECT DISTINCT location FROM nano_cell_battery ORDER BY location"
            )
            
            locations = set()
            if temp_locations is not None and not temp_locations.empty:
                locations.update(temp_locations['location'].tolist())
            if battery_locations is not None and not battery_locations.empty:
                locations.update(battery_locations['location'].tolist())
            
            result = sorted(list(locations))
            logger.info(f"Available locations: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get available locations: {e}")
            return []
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics about the data in the database
        
        Returns:
            Dictionary with data statistics
        """
        try:
            stats = {}
            
            # Temperature/humidity statistics
            temp_stats = self.execute_query("""
                SELECT 
                    COUNT(*) as record_count,
                    MIN(timestamp) as earliest_record,
                    MAX(timestamp) as latest_record,
                    COUNT(DISTINCT location) as location_count
                FROM temp_humidity
            """)
            
            if temp_stats is not None and not temp_stats.empty:
                stats['temperature_humidity'] = temp_stats.iloc[0].to_dict()
            
            # Battery statistics
            battery_stats = self.execute_query("""
                SELECT 
                    COUNT(*) as record_count,
                    MIN(timestamp) as earliest_record,
                    MAX(timestamp) as latest_record,
                    COUNT(DISTINCT location) as location_count
                FROM nano_cell_battery
            """)
            
            if battery_stats is not None and not battery_stats.empty:
                stats['battery'] = battery_stats.iloc[0].to_dict()
            
            logger.info("Database statistics retrieved successfully")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get data statistics: {e}")
            return {}
    
    def close(self):
        """Close database engine and cleanup resources"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine disposed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close() 