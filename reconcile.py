import logging
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime
import pandas as pd
from google.cloud import bigquery
from pymongo import MongoClient
from tqdm import tqdm
import json
from config import (
    BIGQUERY_CONFIG,
    MONGODB_CONFIG,
    RECONCILIATION_CONFIG,
    COMPARISON_RULES,
    ERROR_HANDLING
)

# Setup logging
logging.basicConfig(
    level=getattr(logging, RECONCILIATION_CONFIG['log_level']),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ReconciliationTool:
    def __init__(self):
        self.bq_client = bigquery.Client()
        self.mongo_client = MongoClient(MONGODB_CONFIG['uri'])
        self.mongo_db = self.mongo_client[MONGODB_CONFIG['database']]
        self.mongo_collection = self.mongo_db[MONGODB_CONFIG['collection']]
        
        # Create output directory if it doesn't exist
        os.makedirs(RECONCILIATION_CONFIG['output_dir'], exist_ok=True)
        
        self.results = {
            'total_records': 0,
            'matching_records': 0,
            'discrepancies': [],
            'errors': []
        }

    def get_bigquery_data(self, offset: int, limit: int) -> List[Dict]:
        """Fetch data from BigQuery in batches."""
        query = f"""
        SELECT *
        FROM `{BIGQUERY_CONFIG['project_id']}.{BIGQUERY_CONFIG['dataset_id']}.{BIGQUERY_CONFIG['table_id']}`
        LIMIT {limit}
        OFFSET {offset}
        """
        
        try:
            query_job = self.bq_client.query(query)
            return [dict(row) for row in query_job]
        except Exception as e:
            logger.error(f"Error fetching data from BigQuery: {str(e)}")
            self.results['errors'].append({
                'source': 'bigquery',
                'error': str(e),
                'offset': offset,
                'limit': limit
            })
            return []

    def get_mongodb_data(self, query: Dict) -> List[Dict]:
        """Fetch data from MongoDB in batches."""
        try:
            return list(self.mongo_collection.find(query).limit(MONGODB_CONFIG['batch_size']))
        except Exception as e:
            logger.error(f"Error fetching data from MongoDB: {str(e)}")
            self.results['errors'].append({
                'source': 'mongodb',
                'error': str(e),
                'query': query
            })
            return []

    def compare_records(self, bq_record: Dict, mongo_record: Dict) -> Tuple[bool, List[Dict]]:
        """Compare records between BigQuery and MongoDB."""
        discrepancies = []
        
        for field in RECONCILIATION_CONFIG['compare_fields']:
            bq_value = bq_record.get(field)
            mongo_value = mongo_record.get(field)
            
            if field in COMPARISON_RULES:
                if not COMPARISON_RULES[field](bq_value, mongo_value):
                    discrepancies.append({
                        'field': field,
                        'bigquery_value': bq_value,
                        'mongodb_value': mongo_value
                    })
            elif bq_value != mongo_value:
                discrepancies.append({
                    'field': field,
                    'bigquery_value': bq_value,
                    'mongodb_value': mongo_value
                })
        
        return len(discrepancies) == 0, discrepancies

    def process_batch(self, bq_records: List[Dict]):
        """Process a batch of records."""
        for bq_record in bq_records:
            self.results['total_records'] += 1
            
            # Construct MongoDB query based on key fields
            mongo_query = {
                field: bq_record[field]
                for field in RECONCILIATION_CONFIG['key_fields']
            }
            
            mongo_records = self.get_mongodb_data(mongo_query)
            
            if not mongo_records:
                self.results['discrepancies'].append({
                    'type': 'missing_in_mongodb',
                    'record': bq_record
                })
                continue
            
            mongo_record = mongo_records[0]
            is_match, discrepancies = self.compare_records(bq_record, mongo_record)
            
            if is_match:
                self.results['matching_records'] += 1
            else:
                self.results['discrepancies'].append({
                    'type': 'data_mismatch',
                    'bigquery_record': bq_record,
                    'mongodb_record': mongo_record,
                    'discrepancies': discrepancies
                })

    def run_reconciliation(self):
        """Run the full reconciliation process."""
        logger.info("Starting reconciliation process...")
        
        offset = 0
        while True:
            bq_records = self.get_bigquery_data(offset, BIGQUERY_CONFIG['batch_size'])
            if not bq_records:
                break
                
            self.process_batch(bq_records)
            offset += BIGQUERY_CONFIG['batch_size']
            
            logger.info(f"Processed {offset} records...")
        
        self.generate_report()
        logger.info("Reconciliation process completed.")

    def generate_report(self):
        """Generate reconciliation report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_records': self.results['total_records'],
                'matching_records': self.results['matching_records'],
                'discrepancy_count': len(self.results['discrepancies']),
                'error_count': len(self.results['errors'])
            },
            'discrepancies': self.results['discrepancies'],
            'errors': self.results['errors']
        }
        
        report_path = os.path.join(
            RECONCILIATION_CONFIG['output_dir'],
            f"reconciliation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report generated at: {report_path}")

if __name__ == "__main__":
    tool = ReconciliationTool()
    tool.run_reconciliation() 