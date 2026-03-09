"""
Application Configuration
Environment-based configuration for the SaaS Customer Portal
"""

import os


class Config:
    """Base configuration class"""
    
    # Application settings
    APP_NAME = os.getenv('APP_NAME', 'saas-customer-portal')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Build information
    BUILD_DATE = os.getenv('BUILD_DATE', 'unknown')
    GIT_COMMIT = os.getenv('GIT_COMMIT', 'unknown')
    
    # Cluster information
    CLUSTER_NAME = os.getenv('CLUSTER_NAME', 'unknown')
    NAMESPACE = os.getenv('NAMESPACE', 'default')
    
    # Database configuration
    DB_ENABLED = os.getenv('DB_ENABLED', 'False').lower() == 'true'
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'saas_portal')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    
    # Redis cache configuration
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'False').lower() == 'true'
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'redis')
    CACHE_REDIS_HOST = os.getenv('CACHE_REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.getenv('CACHE_REDIS_PORT', '6379'))
    CACHE_REDIS_DB = int(os.getenv('CACHE_REDIS_DB', '0'))
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')
    
    # Health check settings
    CHECK_DB_HEALTH = os.getenv('CHECK_DB_HEALTH', 'False').lower() == 'true'
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'False').lower() == 'true'
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per hour')
    
    # Metrics and monitoring
    METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'True').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', '9090'))
    
    # Feature flags
    FEATURE_NEW_UI = os.getenv('FEATURE_NEW_UI', 'False').lower() == 'true'
    FEATURE_ADVANCED_ANALYTICS = os.getenv('FEATURE_ADVANCED_ANALYTICS', 'False').lower() == 'true'
    
    # External services
    EXTERNAL_API_URL = os.getenv('EXTERNAL_API_URL', '')
    EXTERNAL_API_KEY = os.getenv('EXTERNAL_API_KEY', '')
    EXTERNAL_API_TIMEOUT = int(os.getenv('EXTERNAL_API_TIMEOUT', '30'))


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    ENVIRONMENT = 'development'
    LOG_LEVEL = 'DEBUG'


class StagingConfig(Config):
    """Staging environment configuration"""
    DEBUG = False
    ENVIRONMENT = 'staging'
    LOG_LEVEL = 'INFO'
    CHECK_DB_HEALTH = True
    RATE_LIMIT_ENABLED = True


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    ENVIRONMENT = 'production'
    LOG_LEVEL = 'WARNING'
    CHECK_DB_HEALTH = True
    RATE_LIMIT_ENABLED = True
    CACHE_ENABLED = True
    DB_ENABLED = True


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env_name=None):
    """
    Get configuration based on environment name
    
    Args:
        env_name: Environment name (development, staging, production)
        
    Returns:
        Configuration class
    """
    if env_name is None:
        env_name = os.getenv('ENVIRONMENT', 'development')
    
    return config_by_name.get(env_name.lower(), DevelopmentConfig)

# Made with Bob
