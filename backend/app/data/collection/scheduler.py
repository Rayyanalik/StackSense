import schedule
import time
import logging
from datetime import datetime
import os
from typing import Optional
from run_collection import main as run_collection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataCollectionScheduler:
    """Scheduler for automated data collection."""
    
    def __init__(self, interval_hours: int = 24):
        """
        Initialize the scheduler.
        
        Args:
            interval_hours: Number of hours between data collection runs
        """
        self.interval_hours = interval_hours
        self.last_run: Optional[datetime] = None
        self.is_running = False
    
    def run_collection_job(self):
        """Run the data collection job."""
        try:
            logger.info("Starting scheduled data collection...")
            self.is_running = True
            self.last_run = datetime.now()
            
            # Run the data collection
            run_collection()
            
            logger.info("Scheduled data collection completed successfully")
        except Exception as e:
            logger.error(f"Error during scheduled data collection: {str(e)}")
        finally:
            self.is_running = False
    
    def start(self):
        """Start the scheduler."""
        logger.info(f"Starting data collection scheduler (interval: {self.interval_hours} hours)")
        
        # Schedule the job
        schedule.every(self.interval_hours).hours.do(self.run_collection_job)
        
        # Run immediately on startup
        self.run_collection_job()
        
        # Keep the scheduler running
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def stop(self):
        """Stop the scheduler."""
        schedule.clear()
        self.is_running = False
        logger.info("Scheduler stopped")

def main():
    """Run the data collection scheduler."""
    # Get interval from environment variable or use default
    interval_hours = int(os.getenv('DATA_COLLECTION_INTERVAL_HOURS', '24'))
    
    # Create and start scheduler
    scheduler = DataCollectionScheduler(interval_hours=interval_hours)
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in scheduler: {str(e)}")
        raise

if __name__ == "__main__":
    main() 