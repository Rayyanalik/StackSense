from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from typing import Dict, List
import threading

class RateLimiter:
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, List[float]] = {}
        self.lock = threading.Lock()

    def is_allowed(self, ip: str) -> bool:
        with self.lock:
            current_time = time.time()
            
            # Clean up expired requests
            self.cleanup()
            
            # Initialize or get request timestamps for this IP
            if ip not in self.requests:
                self.requests[ip] = []
            
            # Remove timestamps older than the time window
            self.requests[ip] = [
                timestamp for timestamp in self.requests[ip]
                if current_time - timestamp < self.time_window
            ]
            
            # Check if under the limit
            if len(self.requests[ip]) < self.max_requests:
                self.requests[ip].append(current_time)
                return True
            
            return False

    def cleanup(self):
        current_time = time.time()
        expired_ips = []
        
        for ip, timestamps in self.requests.items():
            # Remove expired timestamps
            self.requests[ip] = [
                timestamp for timestamp in timestamps
                if current_time - timestamp < self.time_window
            ]
            
            # Remove IP if no timestamps left
            if not self.requests[ip]:
                expired_ips.append(ip)
        
        for ip in expired_ips:
            del self.requests[ip]

async def rate_limit_middleware(request: Request, call_next):
    # Get client IP
    client_ip = request.client.host
    
    # Initialize rate limiter if not exists
    if not hasattr(request.app.state, 'rate_limiter'):
        request.app.state.rate_limiter = RateLimiter()
    
    # Check if request is allowed
    if not request.app.state.rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after": request.app.state.rate_limiter.time_window
            }
        )
    
    # Process the request
    response = await call_next(request)
    return response 