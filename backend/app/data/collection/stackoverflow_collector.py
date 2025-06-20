import os
import json
import requests
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from app.data.collection.base_collector import BaseCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StackOverflowCollector(BaseCollector):
    def __init__(self, api_key: str = None):
        """Initialize the Stack Overflow collector."""
        self.api_key = api_key or os.getenv('STACKOVERFLOW_API_KEY')
        if not self.api_key:
            raise ValueError("Stack Overflow API key is required")
            
        self.base_url = "https://api.stackexchange.com/2.3"
        self.tags = ["python"]  # Just one tag for testing
        self.logger = logging.getLogger(__name__)
        
        # Rate limit tracking
        self.quota_remaining = None
        self.quota_max = None
        self.backoff_time = 0
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 5  # Increased base delay to 5 seconds
        self.max_delay = 30  # Maximum delay between requests
        
        # Request configuration
        self.request_timeout = 10  # Timeout for each request
        self.min_quota_threshold = 10  # Minimum quota to proceed with requests
        
        # Conservative request settings
        self.max_questions_per_request = 10  # Limit questions per request
        self.max_answers_per_question = 5    # Limit answers per question

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Handle rate limiting based on API response headers."""
        try:
            # Get quota information from headers
            self.quota_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            self.quota_max = int(response.headers.get('X-RateLimit-Max', 0))
            
            if response.status_code == 429:  # Too Many Requests
                # Get backoff time from response
                backoff = int(response.headers.get('X-RateLimit-Reset', 0))
                if backoff > 0:
                    self.backoff_time = backoff
                    self.logger.warning(f"Rate limit exceeded. Backing off for {backoff} seconds")
                    time.sleep(backoff)
                else:
                    # If no backoff specified, use exponential backoff
                    self.backoff_time = min(self.backoff_time * 2 or self.base_delay, self.max_delay)
                    self.logger.warning(f"Rate limit exceeded. Using exponential backoff: {self.backoff_time} seconds")
                    time.sleep(self.backoff_time)
            else:
                # Reset backoff time on successful request
                self.backoff_time = 0
                
            # Log quota information
            if self.quota_remaining is not None:
                self.logger.info(f"API Quota: {self.quota_remaining}/{self.quota_max} remaining")
                
                # Add delay if quota is running low
                if self.quota_remaining < self.min_quota_threshold:
                    delay = self.base_delay * 2
                    self.logger.warning(f"Low quota remaining. Adding {delay} second delay")
                    time.sleep(delay)
                    
        except Exception as e:
            self.logger.error(f"Error handling rate limit: {str(e)}")

    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited."""
        try:
            # Make a minimal request to check rate limit status
            params = {
                'site': 'stackoverflow',
                'key': self.api_key,
                'pagesize': 1
            }
            
            response = requests.get(
                f"{self.base_url}/questions",
                params=params,
                timeout=5
            )
            
            if response.status_code == 429:
                error_data = response.json()
                if error_data.get('error_name') == 'throttle_violation':
                    wait_time = int(error_data.get('error_message', '').split('available in ')[-1].split()[0])
                    if wait_time > 300:  # If wait time is more than 5 minutes
                        self.logger.warning(f"Stack Overflow API is rate limited for {wait_time} seconds")
                        return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking rate limit status: {str(e)}")
            return True

    def _make_request(self, endpoint: str, params: Dict[str, Any], retry_count: int = 0) -> Optional[Dict[str, Any]]:
        """Make an API request with retry logic."""
        if retry_count >= self.max_retries:
            self.logger.error(f"Max retries ({self.max_retries}) exceeded for endpoint: {endpoint}")
            return None
            
        try:
            # Add delay to respect rate limits
            if self.backoff_time > 0:
                time.sleep(self.backoff_time)
            else:
                time.sleep(self.base_delay)  # Always add base delay between requests
            
            # Make API request
            url = f"{self.base_url}/{endpoint}"
            self.logger.debug(f"Making request to: {url}")
            self.logger.debug(f"With params: {params}")
            
            response = requests.get(
                url,
                params=params,
                timeout=self.request_timeout
            )
            
            # Handle rate limiting
            self._handle_rate_limit(response)
            
            # If we hit rate limit, check if we should retry
            if response.status_code == 429:
                try:
                    error_data = response.json()
                    if error_data.get('error_name') == 'throttle_violation':
                        wait_time = int(error_data.get('error_message', '').split('available in ')[-1].split()[0])
                        if wait_time > 300:  # If wait time is more than 5 minutes
                            self.logger.warning(f"Stack Overflow API is rate limited for {wait_time} seconds")
                            return None
                except:
                    pass
                return self._make_request(endpoint, params, retry_count + 1)
                
            # Check for other errors
            if response.status_code != 200:
                self.logger.error(f"Error in request: {response.status_code}")
                self.logger.error(f"Response content: {response.text}")
                return None
                
            data = response.json()
            if 'error_id' in data:
                self.logger.error(f"API error: {data.get('error_message', 'Unknown error')}")
                return None
                
            return data
            
        except requests.exceptions.Timeout:
            self.logger.error("Request timed out")
            # Exponential backoff for timeouts
            time.sleep(self.base_delay * (2 ** retry_count))
            return self._make_request(endpoint, params, retry_count + 1)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return None

    def get_popular_questions(self, tag: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get popular questions for a tag with answers included."""
        try:
            # Make a single request to get questions with answers
            params = {
                'tagged': tag,
                'site': 'stackoverflow',
                'sort': 'votes',
                'order': 'desc',
                'pagesize': min(limit, self.max_questions_per_request),  # Limit questions per request
                'key': self.api_key,
                'filter': '!9_bDDxJY5',  # Include question body and other necessary fields
                'page': 1  # Start with first page
            }
            
            data = self._make_request('questions', params)
            if not data:
                self.logger.error("Failed to get questions data")
                return []
                
            if 'items' not in data:
                self.logger.error(f"Unexpected API response: {data}")
                return []
                
            questions = data['items']
            if not questions:
                self.logger.warning(f"No questions found for tag: {tag}")
                return []
                
            # Get answers for each question with delay
            for question in questions:
                if question.get('is_answered'):
                    # Add delay between answer requests
                    time.sleep(self.base_delay)
                    answers = self.get_question_answers(question['question_id'])
                    if answers:
                        # Limit number of answers per question
                        question['answers'] = answers[:self.max_answers_per_question]
                    else:
                        question['answers'] = []
                        
            return questions
            
        except Exception as e:
            self.logger.error(f"Error getting popular questions: {str(e)}")
            return []

    def get_question_answers(self, question_id: int) -> List[Dict[str, Any]]:
        """Get answers for a question."""
        try:
            params = {
                'site': 'stackoverflow',
                'order': 'desc',
                'sort': 'votes',
                'filter': '!9_bDDxJY5',  # Include answer body and other necessary fields
                'key': self.api_key,
                'pagesize': self.max_answers_per_question  # Limit answers per request
            }
            
            data = self._make_request(f'questions/{question_id}/answers', params)
            if not data or not data.get('items'):
                self.logger.warning(f"No answers found for question {question_id}")
                return []
                
            return data['items']
            
        except Exception as e:
            self.logger.error(f"Error getting answers: {str(e)}")
            return []

    def extract_technologies(self, text: str) -> List[str]:
        """Extract technology mentions from text."""
        # Common technology patterns
        tech_patterns = [
            r'\b(?:React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|Laravel|Rails)\b',
            r'\b(?:Python|JavaScript|Java|Go|Rust|TypeScript|PHP|Ruby|C#|C\+\+)\b',
            r'\b(?:PostgreSQL|MySQL|MongoDB|Redis|Cassandra|Elasticsearch)\b',
            r'\b(?:Docker|Kubernetes|AWS|Azure|GCP|Heroku|DigitalOcean)\b',
            r'\b(?:TensorFlow|PyTorch|scikit-learn|pandas|numpy|OpenCV)\b'
        ]
        
        import re
        technologies = set()
        
        for pattern in tech_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            technologies.update(match.group() for match in matches)
        
        return list(technologies)
    
    def get_tech_stack(self, question: Dict[str, Any], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract tech stack information from a question and its answers."""
        # Combine question and answer text
        text = f"{question['title']} {question.get('body', '')}"
        for answer in answers:
            text += f" {answer.get('body', '')}"
        
        # Extract technologies
        technologies = self.extract_technologies(text)
        
        # Create tech stack entry
        tech_stack = {
            "name": f"Stack Overflow: {question['title'][:50]}...",
            "description": question.get('body', '')[:500],
            "technologies": [self.normalize_tech_name(tech) for tech in technologies],
            "metadata": {
                "question_id": question["question_id"],
                "score": question["score"],
                "view_count": question["view_count"],
                "answer_count": question["answer_count"],
                "tags": question["tags"],
                "created_at": datetime.fromtimestamp(question["creation_date"]).isoformat(),
                "url": question["link"]
            }
        }
        
        # Enrich with additional metadata
        tech_stack = self.enrich_metadata(tech_stack)
        
        # Infer domain
        tech_stack["domain"] = self.infer_domain(tech_stack)
        
        return tech_stack
    
    def collect(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Collect tech stack data from Stack Overflow."""
        self.logger.info("Starting Stack Overflow data collection")
        tech_stacks = []
        
        for tag in self.tags:
            self.logger.info(f"Collecting questions for tag: {tag}")
            questions = self.get_popular_questions(tag, limit=limit)
            
            if not questions:
                self.logger.warning(f"No questions found for tag: {tag}")
                continue
                
            for question in questions:
                try:
                    # Get answers for the question
                    answers = question.get('answers', [])
                    if not answers:
                        continue
                        
                    # Extract technologies from question and answers
                    technologies = set()
                    
                    # Add technologies from question title and body
                    technologies.update(self.extract_technologies(question['title']))
                    technologies.update(self.extract_technologies(question['body']))
                    
                    # Add technologies from answers
                    for answer in answers:
                        technologies.update(self.extract_technologies(answer['body']))
                    
                    if technologies:
                        tech_stack = {
                            'name': question['title'],
                            'description': question['body'][:200] + '...' if len(question['body']) > 200 else question['body'],
                            'technologies': list(technologies),
                            'metadata': {
                                'score': question['score'],
                                'view_count': question['view_count'],
                                'answer_count': question['answer_count'],
                                'created_at': question['creation_date'],
                                'tags': question['tags'],
                                'url': f"https://stackoverflow.com/questions/{question['question_id']}"
                            },
                            'collected_at': datetime.now().isoformat(),
                            'source': 'StackOverflowCollector',
                            'tech_count': len(technologies),
                            'description_length': len(question['body']),
                            'domain': self.get_domain(tag)
                        }
                        tech_stacks.append(tech_stack)
                        
                        if len(tech_stacks) >= limit:
                            break
                            
                except Exception as e:
                    self.logger.error(f"Error processing question {question.get('question_id', 'unknown')}: {str(e)}")
                    continue
                    
            if len(tech_stacks) >= limit:
                break
        
        # Save collected data
        if tech_stacks:
            self.save_data(tech_stacks)
            self.logger.info(f"Collected {len(tech_stacks)} tech stacks from Stack Overflow")
        else:
            self.logger.warning("No tech stacks collected from Stack Overflow")
            
        return tech_stacks 

    def search_questions(self, query: str, limit: int = 5) -> list:
        """Search Stack Overflow for questions relevant to the query and return their tech stacks."""
        params = {
            'order': 'desc',
            'sort': 'relevance',
            'intitle': query,
            'site': 'stackoverflow',
            'pagesize': limit,
            'key': self.api_key
        }
        try:
            response = requests.get(f"{self.base_url}/search", params=params, timeout=self.request_timeout)
            if response.status_code == 429:
                logger.warning("Stack Overflow API rate limit exceeded.")
                raise Exception('Stack Overflow rate limit exceeded')
            response.raise_for_status()
            data = response.json()
            if 'items' not in data:
                logger.error(f"Unexpected API response: {data}")
                return []
            questions = data['items']
            tech_stacks = []
            for question in questions:
                try:
                    answers = self.get_question_answers(question['question_id'])
                    technologies = set()
                    technologies.update(self.extract_technologies(question['title']))
                    technologies.update(self.extract_technologies(question.get('body', '')))
                    for answer in answers:
                        technologies.update(self.extract_technologies(answer.get('body', '')))
                    if technologies:
                        tech_stack = {
                            'name': question['title'],
                            'description': question.get('body', '')[:200] + '...' if len(question.get('body', '')) > 200 else question.get('body', ''),
                            'technologies': list(technologies),
                            'metadata': {
                                'score': question.get('score'),
                                'view_count': question.get('view_count'),
                                'answer_count': question.get('answer_count'),
                                'created_at': question.get('creation_date'),
                                'tags': question.get('tags'),
                                'url': question.get('link', f"https://stackoverflow.com/questions/{question['question_id']}")
                            },
                            'collected_at': datetime.now().isoformat(),
                            'source': 'StackOverflowCollector',
                            'tech_count': len(technologies),
                            'description_length': len(question.get('body', '')),
                            'domain': self.get_domain(question.get('tags', ['General'])[0]) if question.get('tags') else 'General'
                        }
                        tech_stacks.append(tech_stack)
                except Exception as e:
                    logger.error(f"Error processing question {question.get('question_id', 'unknown')}: {str(e)}")
            return tech_stacks
        except Exception as e:
            logger.error(f"Error searching Stack Overflow: {str(e)}")
            return [] 