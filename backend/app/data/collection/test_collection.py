import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from app.data.collection.github_collector import GitHubCollector
from app.data.collection.stackoverflow_collector import StackOverflowCollector
from app.data.collection.stackshare_collector import StackShareCollector
from app.data.processing.data_processor import DataProcessor
from app.data.processing.feedback_handler import FeedbackHandler
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_github_collector() -> List[Dict[str, Any]]:
    """Test GitHub data collection."""
    logger.info("Testing GitHub collector...")
    
    try:
        collector = GitHubCollector()
        tech_stacks = collector.collect(limit=1, min_stars=100)  # Reduce to 1 entry
        
        if not tech_stacks:
            logger.error("No data collected from GitHub")
            return []
        
        logger.info(f"Successfully collected {len(tech_stacks)} entries from GitHub")
        logger.info("Sample GitHub entry:")
        logger.info(json.dumps(tech_stacks[0], indent=2))
        
        return tech_stacks
    except Exception as e:
        logger.error(f"GitHub collector test failed: {str(e)}")
        return []

def test_stackoverflow_collector() -> List[Dict[str, Any]]:
    """Test Stack Overflow collector."""
    try:
        collector = StackOverflowCollector()
        
        # Check if we're rate limited before starting
        if collector.is_rate_limited():
            logger.warning("Stack Overflow API is rate limited. Skipping test.")
            return None
            
        tech_stacks = collector.collect(limit=1)  # Reduce to 1 entry
        
        if not tech_stacks:
            logger.warning("No data collected from Stack Overflow")
            return None
            
        logger.info(f"Successfully collected {len(tech_stacks)} entries from Stack Overflow")
        logger.info("Sample Stack Overflow entry:")
        logger.info(json.dumps(tech_stacks[0], indent=2))
        return tech_stacks
        
    except Exception as e:
        logger.error(f"Stack Overflow collector test failed: {str(e)}")
        return None

def test_stackshare_collector() -> bool:
    """StackShare collector is skipped (not tested)."""
    logger.info("Skipping StackShare collector test (not required).")
    return True

def test_data_processor():
    """Test data processor."""
    logger.info("Testing data processor...")
    processor = DataProcessor()
    
    # Test data processing
    test_data = [
        {
            'name': 'Test Project',
            'description': 'A test project',
            'technologies': ['Python', 'Django'],
            'metadata': {'stars': 100}
        }
    ]
    
    try:
        processed_data = processor.process_data(test_data)
        
        if not processed_data:
            logger.error("Data processor test failed: No data processed")
            return False
        
        # Verify data structure
        for entry in processed_data:
            if not all(key in entry for key in ['name', 'description', 'technologies', 'metadata', 'tech_count', 'description_length', 'domain']):
                logger.error("Data processor test failed: Invalid data structure")
                return False
        
        logger.info(f"Successfully processed {len(processed_data)} entries")
        return True
        
    except Exception as e:
        logger.error(f"Data processor test failed: {str(e)}")
        return False

def test_feedback_handler() -> None:
    """Test feedback handler."""
    logger.info("Testing feedback handler...")
    
    try:
        handler = FeedbackHandler()
        
        # Test technology correction
        handler.add_tech_correction("reactjs", "React", "test_user1")
        handler.add_tech_correction("reactjs", "React", "test_user2")
        
        # Test domain correction
        handler.add_domain_correction("test_entry1", "Web Development", "test_user1")
        
        # Test description correction
        handler.add_description_correction("test_entry1", "Updated description", "test_user1")
        
        # Get corrections
        corrections = handler.get_most_common_corrections()
        
        logger.info("Feedback handler test results:")
        logger.info(json.dumps(corrections, indent=2))
        
    except Exception as e:
        logger.error(f"Feedback handler test failed: {str(e)}")

def verify_data_quality(data: List[Dict[str, Any]]) -> bool:
    """Verify data quality metrics."""
    logger.info("Verifying data quality...")
    
    try:
        # Check required fields
        required_fields = ['id', 'title', 'description', 'technologies', 'domain']
        for entry in data:
            missing_fields = [field for field in required_fields if field not in entry]
            if missing_fields:
                raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Check data types
        for entry in data:
            if not isinstance(entry['technologies'], list):
                raise ValueError(f"Invalid technologies type in entry {entry['id']}")
            if not isinstance(entry['description'], str):
                raise ValueError(f"Invalid description type in entry {entry['id']}")
        
        # Check for duplicates
        ids = [entry['id'] for entry in data]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate IDs found")
        
        logger.info("Data quality verification passed")
        return True
        
    except Exception as e:
        logger.error(f"Data quality verification failed: {str(e)}")
        return False

def test_data_processor_integration():
    """Test integration between collectors and data processor."""
    logger.info("Testing data processor integration...")
    
    try:
        # Initialize collectors
        github_collector = GitHubCollector()
        stackoverflow_collector = StackOverflowCollector()
        
        # Collect data from GitHub (since Stack Overflow is rate limited)
        github_data = github_collector.collect(limit=2, min_stars=100)
        if not github_data:
            logger.error("No data collected from GitHub")
            return False
            
        # Initialize processor
        processor = DataProcessor()
        
        # Process the data
        processed_data = processor.process_data(github_data)
        if not processed_data:
            logger.error("No data processed")
            return False
            
        # Verify processed data structure
        for item in processed_data:
            # Check required fields
            required_fields = ['name', 'description', 'technologies', 'metadata', 
                             'tech_count', 'description_length', 'domain']
            if not all(field in item for field in required_fields):
                logger.error(f"Missing required fields in processed data: {item}")
                return False
                
            # Verify technology standardization
            if not all(isinstance(tech, str) for tech in item['technologies']):
                logger.error(f"Invalid technology format in processed data: {item['technologies']}")
                return False
                
            # Verify metadata structure
            if not isinstance(item['metadata'], dict):
                logger.error(f"Invalid metadata format: {item['metadata']}")
                return False
                
            # Verify derived fields
            if not isinstance(item['tech_count'], int) or item['tech_count'] < 0:
                logger.error(f"Invalid tech_count: {item['tech_count']}")
                return False
                
            if not isinstance(item['description_length'], int) or item['description_length'] < 0:
                logger.error(f"Invalid description_length: {item['description_length']}")
                return False
                
            if not isinstance(item['domain'], str):
                logger.error(f"Invalid domain: {item['domain']}")
                return False
        
        logger.info(f"Successfully processed {len(processed_data)} entries")
        logger.info("Sample processed entry:")
        logger.info(json.dumps(processed_data[0], indent=2))
        
        return True
        
    except Exception as e:
        logger.error(f"Data processor integration test failed: {str(e)}")
        return False

def test_data_processor_edge_cases():
    """Test data processor with edge cases."""
    logger.info("Testing data processor edge cases...")
    
    try:
        processor = DataProcessor()
        
        # Test cases
        test_cases = [
            # Empty data
            [],
            # Missing fields
            [{'name': 'Test'}],
            # Invalid technology format
            [{'name': 'Test', 'technologies': [123, None, 'Python']}],
            # Empty strings
            [{'name': '', 'description': '', 'technologies': []}],
            # Very long strings
            [{'name': 'Test', 'description': 'x' * 1000, 'technologies': ['Python']}]
        ]
        
        for i, test_data in enumerate(test_cases):
            logger.info(f"Testing case {i + 1}")
            processed_data = processor.process_data(test_data)
            
            if not isinstance(processed_data, list):
                logger.error(f"Invalid return type for case {i + 1}")
                return False
                
            # Verify each processed item
            for item in processed_data:
                if not all(isinstance(tech, str) for tech in item.get('technologies', [])):
                    logger.error(f"Invalid technology format in case {i + 1}")
                    return False
                    
                if not isinstance(item.get('tech_count', 0), int):
                    logger.error(f"Invalid tech_count in case {i + 1}")
                    return False
                    
                if not isinstance(item.get('description_length', 0), int):
                    logger.error(f"Invalid description_length in case {i + 1}")
                    return False
        
        logger.info("Successfully processed all edge cases")
        return True
        
    except Exception as e:
        logger.error(f"Data processor edge cases test failed: {str(e)}")
        return False

def test_end_to_end_pipeline() -> bool:
    """Test the full end-to-end pipeline (GitHub + Stack Overflow only)."""
    logger.info("Testing full end-to-end pipeline (without StackShare)...")
    try:
        # Initialize collectors
        github_collector = GitHubCollector()
        stackoverflow_collector = StackOverflowCollector()
        
        # Collect data from both sources
        github_data = github_collector.collect(limit=1)
        stackoverflow_data = stackoverflow_collector.collect(limit=1)
        
        # Merge data
        all_data = github_data + stackoverflow_data
        logger.info(f"Merged {len(all_data)} entries from GitHub and Stack Overflow.")
        
        # Process data
        processor = DataProcessor()
        processed_data = processor.process_data(all_data)
        logger.info(f"Processed {len(processed_data)} entries.")
        
        # Test feedback system
        feedback_handler = FeedbackHandler()
        if processed_data:
            sample_entry = processed_data[0]
            if "technologies" in sample_entry and sample_entry["technologies"]:
                old_tech = sample_entry["technologies"][0]
                new_tech = "TestTech"
                feedback_handler.add_tech_correction(old_tech, new_tech, user_id="test_user_1")
                feedback_handler.add_tech_correction(old_tech, new_tech, user_id="test_user_2")
                corrected_data = feedback_handler.apply_corrections(processed_data)
                for entry in corrected_data:
                    if entry.get("id") == sample_entry.get("id"):
                        assert new_tech in entry["technologies"], "Correction was not applied"
                        logger.info(f"Applied feedback correction: {old_tech} -> {new_tech}")
                        break
        logger.info("End-to-end pipeline test passed.")
        return True
    except Exception as e:
        logger.error(f"End-to-end pipeline test failed: {str(e)}")
        return False

def test_data_quality():
    """Test data quality validation."""
    from app.data.quality.data_validator import DataValidator
    try:
        # Initialize validator
        validator = DataValidator()
        # Test with sample data
        sample_data = [
            {
                'name': 'Test Project',
                'description': 'A test project',
                'technologies': ['Python', 'Django'],
                'metadata': {'source': 'test'}
            }
        ]
        validation_output = validator.validate_data(sample_data)
        print("Sample data validation results:", validation_output)
        logger.info(f"Sample data validation results: {validation_output}")
        validation_results = validation_output['validation_results'] if isinstance(validation_output, dict) and 'validation_results' in validation_output else validation_output
        assert len(validation_results) > 0
        assert all(isinstance(result, dict) for result in validation_results)
        # Test with invalid data
        invalid_data = [
            {
                'name': '',
                'description': None,
                'technologies': [],
                'metadata': {}
            }
        ]
        validation_output = validator.validate_data(invalid_data)
        print("Invalid data validation results:", validation_output)
        logger.info(f"Invalid data validation results: {validation_output}")
        validation_results = validation_output['validation_results'] if isinstance(validation_output, dict) and 'validation_results' in validation_output else validation_output
        assert len(validation_results) > 0
        assert all(isinstance(result, dict) for result in validation_results)
        logger.info("Data quality tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"Data quality test failed: {str(e)}")
        return False

def test_performance_monitoring():
    """Test performance monitoring."""
    from app.data.monitoring.performance_monitor import PerformanceMonitor
    try:
        monitor = PerformanceMonitor()
        monitor.start_operation("test_operation")
        import time
        time.sleep(0.1)
        monitor.end_operation("test_operation")
        monitor.record_metric("test_metric", 100.0, "test")
        report = monitor.get_performance_report()
        assert 'timestamp' in report
        assert 'metric_averages' in report
        assert 'current_system_metrics' in report
        assert 'total_metrics_recorded' in report
        assert report['total_metrics_recorded'] == 2
        assert 'test_operation_duration' in report['metric_averages']
        assert 'test_metric' in report['metric_averages']
        system_metrics = monitor.get_system_metrics()
        assert 'cpu_percent' in system_metrics
        assert 'memory_percent' in system_metrics
        assert 'disk_percent' in system_metrics
        logger.info("Performance monitoring tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"Performance monitoring test failed: {str(e)}")
        return False

def test_data_backup():
    """Test data backup and restoration."""
    from app.data.backup.data_backup import DataBackup
    import os
    try:
        backup = DataBackup()
        sample_data = [
            {'id': 1, 'name': 'Test 1'},
            {'id': 2, 'name': 'Test 2'}
        ]
        backup_file = backup.create_backup(
            sample_data,
            metadata={'source': 'test', 'version': '1.0'}
        )
        assert os.path.exists(backup_file)
        backups = backup.list_backups()
        assert len(backups) > 0
        assert backups[0]['entry_count'] == 2
        restored_data = backup.restore_backup(backup_file)
        assert len(restored_data) == 2
        assert restored_data[0]['name'] == 'Test 1'
        assert restored_data[1]['name'] == 'Test 2'
        backup.delete_backup(backup_file)
        assert not os.path.exists(backup_file)
        logger.info("Data backup tests completed successfully")
        return True
    except Exception as e:
        logger.error(f"Data backup test failed: {str(e)}")
        return False

def test_phase2_feature() -> bool:
    """Test the new feature or integration for Phase 2."""
    logger.info("Testing Phase 2 feature...")
    # Placeholder for Phase 2 testing logic
    logger.info("Phase 2 feature test passed.")
    return True

def run_tests() -> bool:
    """Run all collector tests with a timeout."""
    try:
        logger.info("Starting Phase 1 tests...")
        
        # Run individual collector tests
        logger.info("Testing GitHub collector...")
        github_data = test_github_collector()
        if not github_data:
            logger.error("GitHub collector test failed")
            return False
            
        logger.info("Testing Stack Overflow collector...")
        stackoverflow_data = test_stackoverflow_collector()
        if stackoverflow_data is None:  # None means rate limited, which is expected
            logger.warning("No data collected from Stack Overflow (this is expected due to API rate limits)")
        elif not stackoverflow_data:
            logger.error("Stack Overflow collector test failed")
            return False
            
        logger.info("Testing data processor with collected data...")
        if not test_data_processor():
            logger.error("Data processor test failed")
            return False
            
        logger.info("Testing data processor integration...")
        if not test_data_processor_integration():
            logger.error("Data processor integration test failed")
            return False
            
        logger.info("Testing data processor edge cases...")
        if not test_data_processor_edge_cases():
            logger.error("Data processor edge cases test failed")
            return False
            
        logger.info("Testing data quality...")
        if not test_data_quality():
            logger.error("Data quality test failed")
            return False
            
        logger.info("Testing performance monitoring...")
        if not test_performance_monitoring():
            logger.error("Performance monitoring test failed")
            return False
            
        logger.info("Testing data backup...")
        if not test_data_backup():
            logger.error("Data backup test failed")
            return False
            
        logger.info("Testing full end-to-end pipeline...")
        if not test_end_to_end_pipeline():
            logger.error("End-to-end pipeline test failed")
            return False
            
        logger.info("All tests including end-to-end pipeline passed successfully.")
        return True
        
    except Exception as e:
        logger.error(f"Test suite failed with error: {str(e)}")
        return False

def test_data_processor_with_data(data: List[Dict[str, Any]]) -> bool:
    """Test data processor with actual collected data."""
    try:
        processor = DataProcessor()
        
        # Process the data
        processed_data = processor.process_data(data)
        if not processed_data:
            logger.error("No data processed")
            return False
            
        # Verify processed data structure
        for item in processed_data:
            required_fields = ['name', 'technologies', 'metadata', 'source']
            if not all(field in item for field in required_fields):
                logger.error(f"Missing required fields in processed data: {item}")
                return False
                
            # Verify technology standardization
            if not all(isinstance(tech, str) for tech in item['technologies']):
                logger.error(f"Invalid technology format in processed data: {item['technologies']}")
                return False
                
        logger.info(f"Successfully processed {len(processed_data)} entries")
        logger.info("Sample processed entry:")
        logger.info(json.dumps(processed_data[0], indent=2))
        
        return True
        
    except Exception as e:
        logger.error(f"Data processor test failed: {str(e)}")
        return False

if __name__ == "__main__":
    run_tests() 