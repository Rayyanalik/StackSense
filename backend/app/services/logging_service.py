import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import traceback
import sys

class LoggingService:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        self.logger = logging.getLogger("stacksense")
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        self._setup_handlers()
        
        # Set format
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add handlers to logger
        for handler in self.handlers:
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)
    
    def _setup_handlers(self):
        """Setup logging handlers for different log levels"""
        self.handlers = []
        
        # Console handler for all levels
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        self.handlers.append(console_handler)
        
        # File handlers for different levels
        levels = {
            'error': logging.ERROR,
            'warning': logging.WARNING,
            'info': logging.INFO,
            'debug': logging.DEBUG
        }
        
        for level_name, level in levels.items():
            file_handler = logging.FileHandler(
                self.log_dir / f"{level_name}.log"
            )
            file_handler.setLevel(level)
            self.handlers.append(file_handler)
    
    def _format_log_data(self, 
                        message: str, 
                        extra_data: Optional[Dict[str, Any]] = None) -> str:
        """Format log data as JSON string"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'message': message
        }
        
        if extra_data:
            log_data.update(extra_data)
            
        return json.dumps(log_data)
    
    def error(self, 
             message: str, 
             error: Optional[Exception] = None,
             extra_data: Optional[Dict[str, Any]] = None):
        """Log error with optional exception and extra data"""
        log_data = extra_data or {}
        
        if error:
            log_data.update({
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc()
            })
        
        self.logger.error(
            self._format_log_data(message, log_data)
        )
    
    def warning(self, 
                message: str,
                extra_data: Optional[Dict[str, Any]] = None):
        """Log warning with optional extra data"""
        self.logger.warning(
            self._format_log_data(message, extra_data)
        )
    
    def info(self, 
             message: str,
             extra_data: Optional[Dict[str, Any]] = None):
        """Log info with optional extra data"""
        self.logger.info(
            self._format_log_data(message, extra_data)
        )
    
    def debug(self, 
              message: str,
              extra_data: Optional[Dict[str, Any]] = None):
        """Log debug with optional extra data"""
        self.logger.debug(
            self._format_log_data(message, extra_data)
        )
    
    def log_api_request(self,
                       method: str,
                       endpoint: str,
                       status_code: int,
                       duration_ms: float,
                       request_data: Optional[Dict[str, Any]] = None,
                       response_data: Optional[Dict[str, Any]] = None):
        """Log API request details"""
        extra_data = {
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration_ms': duration_ms,
            'request_data': request_data,
            'response_data': response_data
        }
        
        if 200 <= status_code < 400:
            self.info(f"API Request: {method} {endpoint}", extra_data)
        else:
            self.error(f"API Error: {method} {endpoint}", extra_data=extra_data)
    
    def log_recommendation(self,
                          project_description: str,
                          requirements: list,
                          constraints: list,
                          recommendation: Dict[str, Any],
                          processing_time_ms: float):
        """Log recommendation generation details"""
        extra_data = {
            'project_description': project_description,
            'requirements': requirements,
            'constraints': constraints,
            'recommendation': recommendation,
            'processing_time_ms': processing_time_ms
        }
        
        self.info("Generated recommendation", extra_data)
    
    def log_data_processing(self,
                           source: str,
                           data_count: int,
                           processing_time_ms: float,
                           errors: Optional[list] = None):
        """Log data processing details"""
        extra_data = {
            'source': source,
            'data_count': data_count,
            'processing_time_ms': processing_time_ms,
            'errors': errors
        }
        
        if errors:
            self.warning(f"Data processing completed with {len(errors)} errors", extra_data)
        else:
            self.info("Data processing completed successfully", extra_data) 