from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# BigQuery Configuration
BIGQUERY_CONFIG = {
    'project_id': os.getenv('BIGQUERY_PROJECT_ID'),
    'dataset_id': os.getenv('BIGQUERY_DATASET_ID'),
    'table_id': os.getenv('BIGQUERY_TABLE_ID'),
    'batch_size': 10000,  # Adjust based on your memory constraints
}

# MongoDB Configuration
MONGODB_CONFIG = {
    'uri': os.getenv('MONGODB_URI'),
    'database': os.getenv('MONGODB_DATABASE'),
    'collection': os.getenv('MONGODB_COLLECTION'),
    'batch_size': 10000,  # Should match BigQuery batch size
}

# Reconciliation Settings
RECONCILIATION_CONFIG = {
    'key_fields': ['id', 'timestamp'],  # Fields that uniquely identify a record
    'compare_fields': ['field1', 'field2', 'field3'],  # Fields to compare
    'output_dir': 'reconciliation_results',
    'log_level': 'INFO',  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
}

# Custom Comparison Rules
# Add custom comparison rules for fields that need special handling
COMPARISON_RULES: Dict[str, Any] = {
    # Example: Compare timestamps within 1 second
    'timestamp': lambda x, y: abs(x - y) < 1,
    
    # Example: Compare prices within 0.01
    'price': lambda x, y: abs(x - y) < 0.01,
    
    # Example: Case-insensitive string comparison
    'status': lambda x, y: x.lower() == y.lower(),
    
    # Example: Compare arrays with same elements regardless of order
    'tags': lambda x, y: set(x) == set(y),
    
    # Example: Compare nested objects
    'metadata': lambda x, y: all(x[k] == y[k] for k in x.keys() if k in y),
}

# Error Handling Settings
ERROR_HANDLING = {
    'max_retries': 3,        # Number of retries for failed operations
    'retry_delay': 5,        # Seconds to wait between retries
    'continue_on_error': True  # Whether to continue processing on errors
}

# Optional: Add custom logging configuration
LOGGING_CONFIG = {
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
    'handlers': [
        'file',
        'console'
    ]
}

# Optional: Add custom MongoDB query options
MONGODB_QUERY_OPTIONS = {
    'max_time_ms': 30000,  # Maximum time to wait for query execution
    'read_preference': 'secondary',  # Read from secondary nodes
    'read_concern': 'local',  # Read concern level
    'read_preference_tags': {'nodeType': 'ANALYTICS'},  # Direct queries to analytics nodes
    'use_analytics_nodes': True  # Enable analytics node isolation
}

# Optional: Add custom BigQuery query options
BIGQUERY_QUERY_OPTIONS = {
    'use_legacy_sql': False,
    'maximum_bytes_billed': 1000000000  # 1GB
}

# Optional: Add custom output formatting
OUTPUT_CONFIG = {
    'json_indent': 2,
    'include_timestamp': True,
    'include_summary': True,
    'include_details': True
} 