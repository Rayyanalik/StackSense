import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.rate_limiter import RateLimiter
import time

client = TestClient(app)

def test_rate_limiter_initialization():
    limiter = RateLimiter(max_requests=10, time_window=60)
    assert limiter.max_requests == 10
    assert limiter.time_window == 60
    assert isinstance(limiter.requests, dict)

def test_rate_limiter_allows_requests_within_limit():
    limiter = RateLimiter(max_requests=3, time_window=1)
    
    # Make 3 requests
    for _ in range(3):
        assert limiter.is_allowed("test_ip") is True
    
    # Fourth request should be blocked
    assert limiter.is_allowed("test_ip") is False

def test_rate_limiter_resets_after_time_window():
    limiter = RateLimiter(max_requests=2, time_window=1)
    
    # Make 2 requests
    assert limiter.is_allowed("test_ip") is True
    assert limiter.is_allowed("test_ip") is True
    
    # Third request should be blocked
    assert limiter.is_allowed("test_ip") is False
    
    # Wait for time window to expire
    time.sleep(1.1)
    
    # Should be allowed again
    assert limiter.is_allowed("test_ip") is True

def test_rate_limiter_different_ips():
    limiter = RateLimiter(max_requests=2, time_window=1)
    
    # Make requests from different IPs
    assert limiter.is_allowed("ip1") is True
    assert limiter.is_allowed("ip2") is True
    assert limiter.is_allowed("ip1") is True
    assert limiter.is_allowed("ip2") is True
    
    # Both IPs should be blocked now
    assert limiter.is_allowed("ip1") is False
    assert limiter.is_allowed("ip2") is False

def test_rate_limiter_middleware():
    # Test the rate limiter middleware with the FastAPI app
    response = client.post(
        "/api/recommend",
        json={"description": "Test project description"}
    )
    assert response.status_code == 200
    
    # Make multiple requests quickly
    for _ in range(10):
        response = client.post(
            "/api/recommend",
            json={"description": "Test project description"}
        )
    
    # Next request should be rate limited
    response = client.post(
        "/api/recommend",
        json={"description": "Test project description"}
    )
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

def test_rate_limiter_cleanup():
    limiter = RateLimiter(max_requests=2, time_window=1)
    
    # Make some requests
    limiter.is_allowed("ip1")
    limiter.is_allowed("ip2")
    
    # Wait for time window to expire
    time.sleep(1.1)
    
    # Cleanup should remove expired entries
    limiter.cleanup()
    assert "ip1" not in limiter.requests
    assert "ip2" not in limiter.requests

def test_rate_limiter_edge_cases():
    limiter = RateLimiter(max_requests=0, time_window=1)
    assert limiter.is_allowed("test_ip") is False
    
    limiter = RateLimiter(max_requests=1, time_window=0)
    assert limiter.is_allowed("test_ip") is True
    assert limiter.is_allowed("test_ip") is True  # No time window, so always allowed

def test_rate_limiter_concurrent_requests():
    import threading
    
    limiter = RateLimiter(max_requests=5, time_window=1)
    results = []
    
    def make_request():
        results.append(limiter.is_allowed("test_ip"))
    
    # Create multiple threads to simulate concurrent requests
    threads = [threading.Thread(target=make_request) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    # Should have exactly 5 True and 5 False results
    assert results.count(True) == 5
    assert results.count(False) == 5 