# BigQuery to MongoDB Reconciliation Tool

> **Disclaimer**: This is not an official MongoDB tool. This is an open-source project created to help with data reconciliation between BigQuery and MongoDB. No official support is provided by MongoDB Inc. or Google Cloud. Use at your own risk.

This tool helps reconcile data between BigQuery and MongoDB Atlas, specifically designed for large datasets (6TB+).

## Prerequisites

- Python 3.8+
- Google Cloud credentials with BigQuery access
- MongoDB Atlas connection string
- MongoDB Atlas Analytical node configured
- Google Private Service Connect configured between GCP and MongoDB Atlas
- Ensure GCP and MongoDB Atlas are in the same region for optimal performance

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials:
```
# Google Cloud credentials
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
BIGQUERY_PROJECT_ID=your-project-id
BIGQUERY_DATASET_ID=your-dataset-id
BIGQUERY_TABLE_ID=your-table-id

# MongoDB Atlas credentials
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=your_database_name
MONGODB_COLLECTION=your_collection_name
```

## Configuration

The tool is configured through `config.py`. A template configuration file `config.example.py` is provided with examples of all available options. To get started:

1. Copy `config.example.py` to `config.py`:
```bash
cp config.example.py config.py
```

2. Modify `config.py` to match your requirements. The example file includes:
   - Basic configuration for BigQuery and MongoDB
   - Example comparison rules for different data types
   - Error handling settings
   - Optional configurations for logging, query options, and output formatting

### 1. BigQuery Configuration
```python
BIGQUERY_CONFIG = {
    'project_id': os.getenv('BIGQUERY_PROJECT_ID'),
    'dataset_id': os.getenv('BIGQUERY_DATASET_ID'),
    'table_id': os.getenv('BIGQUERY_TABLE_ID'),
    'batch_size': 10000,  # Adjust based on your memory constraints
}
```

### 2. MongoDB Configuration
```python
MONGODB_CONFIG = {
    'uri': os.getenv('MONGODB_URI'),
    'database': os.getenv('MONGODB_DATABASE'),
    'collection': os.getenv('MONGODB_COLLECTION'),
    'batch_size': 10000,  # Should match BigQuery batch size
}
```

### 3. Reconciliation Settings
```python
RECONCILIATION_CONFIG = {
    'key_fields': ['id', 'timestamp'],  # Fields that uniquely identify a record
    'compare_fields': ['field1', 'field2', 'field3'],  # Fields to compare
    'output_dir': 'reconciliation_results',
    'log_level': 'INFO',  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
}
```

### 4. Custom Comparison Rules
For fields that need special comparison logic:
```python
COMPARISON_RULES = {
    'timestamp': lambda x, y: abs(x - y) < 1,  # Compare timestamps within 1 second
    'price': lambda x, y: abs(x - y) < 0.01,   # Compare prices within 0.01
    'status': lambda x, y: x.lower() == y.lower()  # Case-insensitive string comparison
}
```

### 5. Error Handling
```python
ERROR_HANDLING = {
    'max_retries': 3,        # Number of retries for failed operations
    'retry_delay': 5,        # Seconds to wait between retries
    'continue_on_error': True  # Whether to continue processing on errors
}
```

## Usage

1. Configure the reconciliation parameters in `config.py` as described above
2. Run the reconciliation:
```bash
python reconcile.py
```

## Output

The tool generates:
- Summary report of reconciliation results
- Detailed discrepancy reports
- Log files for debugging

### Report Format
The reconciliation report (`reconciliation_results/reconciliation_report_YYYYMMDD_HHMMSS.json`) contains:
```json
{
    "timestamp": "2024-03-21T10:30:00",
    "summary": {
        "total_records": 1000000,
        "matching_records": 999000,
        "discrepancy_count": 1000,
        "error_count": 0
    },
    "discrepancies": [
        {
            "type": "data_mismatch",
            "bigquery_record": {...},
            "mongodb_record": {...},
            "discrepancies": [
                {
                    "field": "price",
                    "bigquery_value": 10.5,
                    "mongodb_value": 10.51
                }
            ]
        }
    ],
    "errors": []
}
```

## Performance Considerations

1. **Network Configuration**:
   - Use Google Private Service Connect to establish a secure, private connection between GCP and MongoDB Atlas
   - Ensure both GCP and MongoDB Atlas are deployed in the same region to minimize latency
   - Configure appropriate firewall rules and security groups

2. **Batch Size**: Adjust `batch_size` in both BigQuery and MongoDB configs based on:
   - Available memory
   - Network bandwidth
   - Processing speed requirements

3. **MongoDB Atlas**: 
   - Use an Analytical node for better performance
   - Ensure proper indexing on key fields
   - Consider using read-only user credentials

4. **BigQuery**:
   - Use appropriate project quotas
   - Consider using a dedicated service account
   - Monitor query costs

## Troubleshooting

1. **Connection Issues**:
   - Verify credentials in `.env` file
   - Check network connectivity
   - Ensure proper permissions

2. **Performance Issues**:
   - Reduce batch size
   - Check MongoDB Atlas node size
   - Monitor BigQuery quota usage

3. **Data Mismatches**:
   - Review comparison rules
   - Check data types
   - Verify key field uniqueness

## Support

For issues or questions:
1. Check the log files in the output directory
2. Review the discrepancy reports
3. Contact your system administrator 