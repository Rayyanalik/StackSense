from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Union, Dict, Any
import time
from app.services.logging_service import LoggingService

class ErrorHandler:
    def __init__(self, logger: LoggingService):
        self.logger = logger
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000
            
            # Log successful request
            self.logger.log_api_request(
                method=request.method,
                endpoint=str(request.url.path),
                status_code=response.status_code,
                duration_ms=duration,
                request_data=await self._get_request_data(request)
            )
            
            return response
            
        except Exception as exc:
            duration = (time.time() - start_time) * 1000
            
            # Log error
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                error=exc,
                extra_data={
                    'method': request.method,
                    'endpoint': str(request.url.path),
                    'duration_ms': duration,
                    'request_data': await self._get_request_data(request)
                }
            )
            
            # Return error response
            return self._handle_exception(exc)
    
    async def _get_request_data(self, request: Request) -> Dict[str, Any]:
        """Extract request data for logging"""
        try:
            body = await request.body()
            if body:
                return {
                    'headers': dict(request.headers),
                    'query_params': dict(request.query_params),
                    'body': body.decode()
                }
            return {
                'headers': dict(request.headers),
                'query_params': dict(request.query_params)
            }
        except Exception:
            return {
                'headers': dict(request.headers),
                'query_params': dict(request.query_params)
            }
    
    def _handle_exception(self, exc: Exception) -> JSONResponse:
        """Handle different types of exceptions and return appropriate responses"""
        if isinstance(exc, RequestValidationError):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    'error': 'Validation Error',
                    'detail': exc.errors()
                }
            )
        
        # Handle custom exceptions
        error_mapping = {
            'ValueError': (status.HTTP_400_BAD_REQUEST, 'Bad Request'),
            'KeyError': (status.HTTP_400_BAD_REQUEST, 'Bad Request'),
            'TypeError': (status.HTTP_400_BAD_REQUEST, 'Bad Request'),
            'AttributeError': (status.HTTP_400_BAD_REQUEST, 'Bad Request'),
            'FileNotFoundError': (status.HTTP_404_NOT_FOUND, 'Not Found'),
            'PermissionError': (status.HTTP_403_FORBIDDEN, 'Forbidden'),
            'TimeoutError': (status.HTTP_504_GATEWAY_TIMEOUT, 'Gateway Timeout'),
            'ConnectionError': (status.HTTP_503_SERVICE_UNAVAILABLE, 'Service Unavailable'),
            'MemoryError': (status.HTTP_507_INSUFFICIENT_STORAGE, 'Insufficient Storage'),
            'NotImplementedError': (status.HTTP_501_NOT_IMPLEMENTED, 'Not Implemented')
        }
        
        error_type = type(exc).__name__
        if error_type in error_mapping:
            status_code, error_message = error_mapping[error_type]
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            error_message = 'Internal Server Error'
        
        return JSONResponse(
            status_code=status_code,
            content={
                'error': error_message,
                'detail': str(exc)
            }
        )

class CustomException(Exception):
    """Base class for custom exceptions"""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationException(CustomException):
    """Exception for validation errors"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)

class NotFoundException(CustomException):
    """Exception for not found errors"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class AuthenticationException(CustomException):
    """Exception for authentication errors"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class AuthorizationException(CustomException):
    """Exception for authorization errors"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

class RateLimitException(CustomException):
    """Exception for rate limit errors"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS) 