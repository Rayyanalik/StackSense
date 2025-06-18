import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import schedule
import time
from .github_collector import GitHubCollector
from .stackoverflow_collector import StackOverflowCollector
from .stackshare_collector import StackShareCollector
from data_validator import TechStackValidator
from quality_report import QualityReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def merge_data(github_data: List[Dict[str, Any]], 
               stackoverflow_data: List[Dict[str, Any]],
               stackshare_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge data from different sources.
    
    Args:
        github_data: Data from GitHub
        stackoverflow_data: Data from Stack Overflow
        stackshare_data: Data from StackShare
        
    Returns:
        Merged data
    """
    # Add source identifier
    for entry in github_data:
        entry['metadata']['source'] = 'github'
    
    for entry in stackoverflow_data:
        entry['metadata']['source'] = 'stackoverflow'
    
    for entry in stackshare_data:
        entry['metadata']['source'] = 'stackshare'
    
    # Merge all data
    merged_data = github_data + stackoverflow_data + stackshare_data
    
    return merged_data

def save_merged_data(data: List[Dict[str, Any]], output_dir: str = "data"):
    """
    Save merged data to file.
    
    Args:
        data: Data to save
        output_dir: Output directory
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"merged_tech_stacks_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Save to file
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Saved {len(data)} entries to {filepath}")

def collect_data():
    """Collect data from all sources."""
    try:
        logger.info("Starting data collection...")
        
        # Initialize collectors
        github_collector = GitHubCollector()
        stackoverflow_collector = StackOverflowCollector()
        stackshare_collector = StackShareCollector()
        
        # Collect data
        github_data = github_collector.collect(min_stars=1000)
        stackoverflow_data = stackoverflow_collector.collect()
        stackshare_data = stackshare_collector.collect(limit=100)
        
        # Merge data
        merged_data = merge_data(github_data, stackoverflow_data, stackshare_data)
        
        # Save merged data
        save_merged_data(merged_data)
        
        logger.info("Data collection completed successfully")
        
    except Exception as e:
        logger.error(f"Error during data collection: {str(e)}")

def schedule_collection(interval_hours: int = 24):
    """
    Schedule periodic data collection.
    
    Args:
        interval_hours: Hours between collections
    """
    schedule.every(interval_hours).hours.do(collect_data)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    """Run data collection."""
    # Run initial collection
    collect_data()
    
    # Schedule periodic collection
    schedule_collection()

if __name__ == "__main__":
    main() 