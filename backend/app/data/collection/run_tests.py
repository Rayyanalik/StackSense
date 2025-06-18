import os
import sys
import logging
from dotenv import load_dotenv
from app.data.collection.test_collection import run_tests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment() -> None:
    """Check if required environment variables are set."""
    required_vars = ['GITHUB_TOKEN', 'STACKOVERFLOW_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file")
        # Print actual values for debugging (masked)
        for var in required_vars:
            value = os.getenv(var)
            if value:
                masked = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
                logger.info(f"{var} is set (value: {masked})")
            else:
                logger.info(f"{var} is not set")
        sys.exit(1)
    
    # Print actual values for debugging (masked)
    for var in required_vars:
        value = os.getenv(var)
        masked = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
        logger.info(f"{var} is set (value: {masked})")

def check_dependencies():
    """Check if all required Python packages are installed."""
    required_packages = [
        'requests',
        'pandas',
        'numpy',
        'spacy',
        'sklearn',
        'schedule',
        'dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install these packages using pip")
        return False
    
    return True

def check_spacy_model():
    """Check if the required spaCy model is installed."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        return True
    except OSError:
        logger.error("spaCy model 'en_core_web_sm' not found")
        logger.info("Installing spaCy model...")
        try:
            import spacy.cli
            spacy.cli.download("en_core_web_sm")
            return True
        except Exception as e:
            logger.error(f"Failed to install spaCy model: {str(e)}")
            return False

def main():
    """Run all tests."""
    # Load environment variables first
    load_dotenv()
    
    logger.info("Checking environment...")
    check_environment()
    
    logger.info("Checking dependencies...")
    check_dependencies()
    
    logger.info("Checking spaCy model...")
    check_spacy_model()
    
    logger.info("Running tests...")
    if run_tests():
        logger.info("All checks and tests completed successfully")
    else:
        logger.error("Tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 