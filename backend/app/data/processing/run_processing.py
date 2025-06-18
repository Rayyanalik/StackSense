import os
import json
import logging
from datetime import datetime
from data_processor import DataProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_latest_data_file(data_dir: str = "data") -> str:
    """Get the path of the latest data file."""
    files = [f for f in os.listdir(data_dir) if f.startswith("merged_tech_stacks_")]
    if not files:
        raise FileNotFoundError("No merged data files found")
    
    # Sort by timestamp in filename
    latest_file = sorted(files)[-1]
    return os.path.join(data_dir, latest_file)

def main():
    """Run the data processing pipeline."""
    try:
        # Get latest data file
        input_file = get_latest_data_file()
        logger.info(f"Processing data from {input_file}")
        
        # Load data
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Initialize processor
        processor = DataProcessor()
        
        # Process data
        processed_df = processor.process_data(data)
        
        # Get and log statistics
        stats = processor.get_processing_stats(processed_df)
        logger.info("\nProcessing Statistics:")
        for key, value in stats.items():
            logger.info(f"{key}: {value}")
        
        logger.info("Data processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error during data processing: {str(e)}")
        raise

if __name__ == "__main__":
    main() 