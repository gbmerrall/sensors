"""
Configuration Management System

Centralized configuration for the sensors dashboard application.
"""

import os
from typing import Dict, Any


class Config:
    """
    Application configuration management
    
    Handles database paths, caching settings, timezone configuration,
    and performance parameters.
    """
    
    # Database Configuration
    DATABASE_PATH = os.path.join("external", "sensors.db")
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    
    # Cache Configuration
    CACHE_SETTINGS = {
        'query_cache': {
            'max_size': 50,
            'ttl': 60  # 1 minute
        },
        'processed_cache': {
            'max_size': 100,
            'ttl': 300  # 5 minutes
        },
        'result_cache': {
            'max_size': 200,
            'ttl': 120  # 2 minutes
        },
        'statistics_cache': {
            'max_size': 50,
            'ttl': 120  # 2 minutes
        }
    }
    
    # Timezone Configuration
    DEFAULT_TIMEZONE = "Pacific/Auckland"
    UTC_TIMEZONE = "UTC"
    
    # Performance Configuration
    PERFORMANCE_TARGETS = {
        'page_load_time': 3.0,  # seconds
        'chart_render_time': 1.0,  # seconds
        'query_response_time': 2.0  # seconds
    }
    
    # UI Configuration
    CHART_CONFIG = {
        'default_height': 400,
        'responsive': True,
        'display_mode_bar': True
    }
    
    # Data Processing Configuration
    AGGREGATION_METHODS = {
        'interpolation': '15min',
        'hourly': '1h',  # Updated from '1H' to avoid deprecation warning
        'daily': '1D',
        'weekly': '1W'
    }
    
    # Application Settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5050))
    
    @classmethod
    def get_database_path(cls) -> str:
        """Get the absolute path to the database file"""
        return os.path.abspath(cls.DATABASE_PATH)
    
    @classmethod
    def validate_database_exists(cls) -> bool:
        """Check if the database file exists"""
        return os.path.exists(cls.get_database_path())
    
    @classmethod
    def get_cache_config(cls, cache_type: str) -> Dict[str, Any]:
        """Get cache configuration for specific cache type"""
        return cls.CACHE_SETTINGS.get(cache_type, {})
    
    @classmethod
    def get_all_settings(cls) -> Dict[str, Any]:
        """Get all configuration settings as a dictionary"""
        return {
            'database': {
                'path': cls.DATABASE_PATH,
                'url': cls.DATABASE_URL,
                'exists': cls.validate_database_exists()
            },
            'cache': cls.CACHE_SETTINGS,
            'timezone': {
                'default': cls.DEFAULT_TIMEZONE,
                'utc': cls.UTC_TIMEZONE
            },
            'performance': cls.PERFORMANCE_TARGETS,
            'chart': cls.CHART_CONFIG,
            'aggregation': cls.AGGREGATION_METHODS,
            'app': {
                'debug': cls.DEBUG,
                'host': cls.HOST,
                'port': cls.PORT
            }
        } 