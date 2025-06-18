from locust import HttpUser, task, between
import random
import json

class TechStackUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Initialize user with some test data."""
        self.test_descriptions = [
            {
                "description": "I want to build a modern web application with real-time features",
                "requirements": ["Scalability", "Real-time updates"],
                "constraints": ["Must use open-source technologies"]
            },
            {
                "description": "A mobile app for food delivery with real-time tracking",
                "requirements": ["GPS integration", "Push notifications"],
                "constraints": ["Must work offline"]
            },
            {
                "description": "An e-commerce platform with inventory management",
                "requirements": ["Payment processing", "Stock tracking"],
                "constraints": ["Must be PCI compliant"]
            }
        ]
    
    @task(3)  # Higher weight for recommendation endpoint
    def get_recommendation(self):
        """Test the recommendation endpoint."""
        description = random.choice(self.test_descriptions)
        headers = {
            "Content-Type": "application/json"
        }
        with self.client.post(
            "/api/recommend",
            json=description,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 429:
                response.success()  # Rate limiting is expected
            elif response.status_code != 200:
                response.failure(f"Failed with status {response.status_code}")
            else:
                try:
                    data = response.json()
                    required_fields = [
                        "primary_tech_stack",
                        "alternatives",
                        "explanation",
                        "confidence_level",
                        "similar_projects"
                    ]
                    if not all(field in data for field in required_fields):
                        response.failure("Missing required fields in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
    
    @task(1)
    def get_available_technologies(self):
        """Test the available technologies endpoint."""
        with self.client.get(
            "/api/technologies",
            catch_response=True
        ) as response:
            if response.status_code == 429:
                response.success()  # Rate limiting is expected
            elif response.status_code != 200:
                response.failure(f"Failed with status {response.status_code}")
            else:
                try:
                    data = response.json()
                    if not isinstance(data, list):
                        response.failure("Response is not a list")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
    
    @task(1)
    def health_check(self):
        """Test the health check endpoint."""
        with self.client.get(
            "/api/health",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed with status {response.status_code}")
            else:
                try:
                    data = response.json()
                    if data.get("status") != "healthy":
                        response.failure("Health check failed")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response") 