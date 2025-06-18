import logging
import time
import psutil
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Represents a performance metric."""
    name: str
    value: float
    timestamp: datetime
    category: str  # 'collection', 'processing', 'system'

class PerformanceMonitor:
    """Monitors and tracks system performance metrics."""
    
    def __init__(self, output_dir: str = "performance_logs"):
        """
        Initialize the performance monitor.
        
        Args:
            output_dir: Directory to store performance logs
        """
        self.output_dir = output_dir
        self.metrics: List[PerformanceMetric] = []
        self.start_times: Dict[str, float] = {}
        
    def start_operation(self, operation_name: str):
        """Start timing an operation."""
        self.start_times[operation_name] = time.time()
    
    def end_operation(self, operation_name: str, category: str = "processing"):
        """End timing an operation and record the duration."""
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            self.record_metric(
                f"{operation_name}_duration",
                duration,
                category
            )
            del self.start_times[operation_name]
    
    def record_metric(self, name: str, value: float, category: str = "system"):
        """Record a performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            category=category
        )
        self.metrics.append(metric)
        logger.info(f"Recorded metric: {name}={value} ({category})")
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system resource usage metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / (1024**3)
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {str(e)}")
            return {}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report."""
        # Calculate averages for each metric
        metric_averages = defaultdict(list)
        for metric in self.metrics:
            metric_averages[metric.name].append(metric.value)
        
        averages = {
            name: sum(values) / len(values)
            for name, values in metric_averages.items()
        }
        
        # Get current system metrics
        system_metrics = self.get_system_metrics()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'metric_averages': averages,
            'current_system_metrics': system_metrics,
            'total_metrics_recorded': len(self.metrics)
        }
    
    def save_performance_log(self, output_file: Optional[str] = None):
        """Save performance metrics to a file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.output_dir}/performance_log_{timestamp}.json"
        
        try:
            # Convert metrics to dictionary format
            metrics_data = [
                {
                    'name': m.name,
                    'value': m.value,
                    'timestamp': m.timestamp.isoformat(),
                    'category': m.category
                }
                for m in self.metrics
            ]
            
            with open(output_file, 'w') as f:
                json.dump({
                    'metrics': metrics_data,
                    'report': self.get_performance_report()
                }, f, indent=2)
            
            logger.info(f"Performance log saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving performance log: {str(e)}")
    
    def clear_metrics(self):
        """Clear all recorded metrics."""
        self.metrics = []
        self.start_times = {}
        logger.info("Cleared all performance metrics")

def main():
    """Test the performance monitor."""
    monitor = PerformanceMonitor()
    
    # Test operation timing
    monitor.start_operation("test_operation")
    time.sleep(1)  # Simulate work
    monitor.end_operation("test_operation")
    
    # Record some metrics
    monitor.record_metric("collection_speed", 100.5, "collection")
    monitor.record_metric("processing_speed", 50.2, "processing")
    
    # Get and print system metrics
    system_metrics = monitor.get_system_metrics()
    print("System Metrics:")
    print(json.dumps(system_metrics, indent=2))
    
    # Get and print performance report
    report = monitor.get_performance_report()
    print("\nPerformance Report:")
    print(json.dumps(report, indent=2))
    
    # Save performance log
    monitor.save_performance_log()

if __name__ == "__main__":
    main() 