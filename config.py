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
    'batch_size': 10000,  # Number of records to process in each batch
}

# MongoDB Configuration
MONGODB_CONFIG = {
    'uri': os.getenv('MONGODB_URI'),
    'database': os.getenv('MONGODB_DATABASE'),
    'collection': os.getenv('MONGODB_COLLECTION'),
    'batch_size': 10000,  # Number of records to process in each batch
}

# Reconciliation Settings
RECONCILIATION_CONFIG = {
    'key_fields': ['id'],  # Fields to use as unique identifiers
    'compare_fields': ['field1', 'field2', 'field3'],  # Fields to compare
    'output_dir': 'reconciliation_results',
    'log_level': 'INFO',
}

# Custom comparison rules (if needed)
COMPARISON_RULES: Dict[str, Any] = {
    # Add custom comparison rules here
    # Example: 'field_name': lambda x, y: abs(x - y) < 0.001
}

# Error handling settings
ERROR_HANDLING = {
    'max_retries': 3,
    'retry_delay': 5,  # seconds
    'continue_on_error': True,
} 