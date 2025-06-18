import pytest
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient
from app.middleware.error_handler import (
    ErrorHandler,
    CustomException,
    ValidationException,
    NotFoundException,
    AuthenticationException,
    AuthorizationException,
    RateLimitException
)
from app.services.logging_service import LoggingService
import json
import os
from pathlib import Path

@pytest.fixture
def logger():
    # Use a test log directory
    test_log_dir = "test_logs"
    logger = LoggingService(log_dir=test_log_dir)
    yield logger
    # Cleanup test logs after tests
    if os.path.exists(test_log_dir):
        for file in Path(test_log_dir).glob("*"):
            file.unlink()
        os.rmdir(test_log_dir)

@pytest.fixture
def error_handler(logger):
    return ErrorHandler(logger)

@pytest.fixture
def app(error_handler):
    app = FastAPI()
    app.middleware("http")(error_handler)
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_successful_request(app, client, logger):
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
    
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "success"}
    
    # Check if request was logged
    log_file = Path("test_logs/info.log")
    assert log_file.exists()
    with open(log_file) as f:
        log_content = f.read()
        assert "API Request: GET /test" in log_content

def test_validation_error(app, client, logger):
    @app.get("/test/{id}")
    async def test_endpoint(id: int):
        return {"id": id}
    
    response = client.get("/test/invalid")
    assert response.status_code == 422
    assert "error" in response.json()
    assert "detail" in response.json()
    
    # Check if error was logged
    log_file = Path("test_logs/error.log")
    assert log_file.exists()
    with open(log_file) as f:
        log_content = f.read()
        assert "Request failed: GET /test/invalid" in log_content

def test_custom_exceptions(app, client, logger):
    @app.get("/not-found")
    async def not_found():
        raise NotFoundException("Resource not found")
    
    @app.get("/auth")
    async def auth():
        raise AuthenticationException("Authentication required")
    
    @app.get("/forbidden")
    async def forbidden():
        raise AuthorizationException("Access denied")
    
    @app.get("/rate-limit")
    async def rate_limit():
        raise RateLimitException("Too many requests")
    
    # Test NotFoundException
    response = client.get("/not-found")
    assert response.status_code == 404
    assert response.json()["error"] == "Not Found"
    
    # Test AuthenticationException
    response = client.get("/auth")
    assert response.status_code == 401
    assert response.json()["error"] == "Unauthorized"
    
    # Test AuthorizationException
    response = client.get("/forbidden")
    assert response.status_code == 403
    assert response.json()["error"] == "Forbidden"
    
    # Test RateLimitException
    response = client.get("/rate-limit")
    assert response.status_code == 429
    assert response.json()["error"] == "Too Many Requests"

def test_logging_service(logger):
    # Test different log levels
    logger.debug("Debug message", {"data": "debug"})
    logger.info("Info message", {"data": "info"})
    logger.warning("Warning message", {"data": "warning"})
    logger.error("Error message", {"data": "error"})
    
    # Check if all log files were created
    assert Path("test_logs/debug.log").exists()
    assert Path("test_logs/info.log").exists()
    assert Path("test_logs/warning.log").exists()
    assert Path("test_logs/error.log").exists()
    
    # Test API request logging
    logger.log_api_request(
        method="GET",
        endpoint="/api/test",
        status_code=200,
        duration_ms=100,
        request_data={"param": "value"},
        response_data={"result": "success"}
    )
    
    # Test recommendation logging
    logger.log_recommendation(
        project_description="Test project",
        requirements=["req1", "req2"],
        constraints=["const1"],
        recommendation={"stack": ["tech1", "tech2"]},
        processing_time_ms=200
    )
    
    # Test data processing logging
    logger.log_data_processing(
        source="github",
        data_count=100,
        processing_time_ms=300,
        errors=["error1", "error2"]
    )
    
    # Verify log contents
    with open("test_logs/info.log") as f:
        log_content = f.read()
        assert "API Request: GET /api/test" in log_content
        assert "Generated recommendation" in log_content
        assert "Data processing completed with 2 errors" in log_content

def test_error_handler_request_data(app, client, logger):
    @app.post("/test")
    async def test_endpoint(request: Request):
        body = await request.json()
        return {"received": body}
    
    # Test with request body
    response = client.post(
        "/test",
        json={"test": "data"},
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 200
    
    # Test with query parameters
    response = client.get("/test?param=value")
    assert response.status_code == 200
    
    # Verify request data was logged
    with open("test_logs/info.log") as f:
        log_content = f.read()
        assert "test" in log_content
        assert "param" in log_content

def test_error_handler_duration(app, client, logger):
    @app.get("/slow")
    async def slow_endpoint():
        import time
        time.sleep(0.1)  # Simulate slow operation
        return {"message": "slow"}
    
    response = client.get("/slow")
    assert response.status_code == 200
    
    # Verify duration was logged
    with open("test_logs/info.log") as f:
        log_content = f.read()
        assert "duration_ms" in log_content
        # Duration should be at least 100ms
        log_data = json.loads(log_content.split("\n")[-2])
        assert float(log_data["duration_ms"]) >= 100 