import os
import json
import requests
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from app.data.collection.base_collector import BaseCollector
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubCollector(BaseCollector):
    """Collector for GitHub repository data."""
    
    def __init__(self, output_dir: str = "data"):
        super().__init__(output_dir)
        self.api_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GitHub token not found in environment variables")
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_popular_repos(self, min_stars: int = 1000, language: str = 'python') -> List[Dict[str, Any]]:
        """Get popular repositories from GitHub."""
        try:
            # Construct query with proper format
            query = f"stars:>={min_stars} language:{language}"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 100
            }
            
            # Add authentication header
            headers = {
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Make request with timeout and retry logic
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = requests.get(
                        'https://api.github.com/search/repositories',
                        params=params,
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 403:
                        if 'X-RateLimit-Remaining' in response.headers:
                            remaining = int(response.headers['X-RateLimit-Remaining'])
                            if remaining == 0:
                                reset_time = int(response.headers['X-RateLimit-Reset'])
                                wait_time = max(reset_time - time.time(), 0) + 1
                                logger.warning(f"Rate limit exceeded. Waiting {wait_time:.0f} seconds...")
                                time.sleep(wait_time)
                                continue
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'items' not in data:
                        logger.error(f"Unexpected API response: {data}")
                        return []
                    
                    return data['items']
                    
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        logger.warning(f"Request timed out. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        logger.error("Max retries exceeded for timeout")
                        return []
                        
                except requests.exceptions.RequestException as e:
                    logger.error(f"Request failed: {str(e)}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching repositories: {str(e)}")
            return []
    
    def get_repo_tech_stack(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tech stack information from a repository."""
        # Get repository languages
        languages_url = repo["languages_url"]
        languages_response = requests.get(languages_url, headers=self.headers)
        languages = languages_response.json() if languages_response.status_code == 200 else {}
        
        # Get repository topics
        topics_url = f"{self.api_url}/repos/{repo['full_name']}/topics"
        topics_response = requests.get(
            topics_url,
            headers={**self.headers, "Accept": "application/vnd.github.mercy-preview+json"}
        )
        topics = topics_response.json().get("names", []) if topics_response.status_code == 200 else []
        
        # Combine languages and topics
        technologies = list(set(list(languages.keys()) + topics))
        
        # Create tech stack entry
        tech_stack = {
            "name": repo["name"],
            "description": repo["description"] or "",
            "technologies": [self.normalize_tech_name(tech) for tech in technologies],
            "metadata": {
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "language": repo["language"],
                "topics": topics,
                "url": repo["html_url"]
            }
        }
        
        # Enrich with additional metadata
        tech_stack = self.enrich_metadata(tech_stack)
        
        # Infer domain
        tech_stack["domain"] = self.infer_domain(tech_stack)
        
        return tech_stack
    
    def collect(self, min_stars: int = 1000, limit: int = 100) -> List[Dict[str, Any]]:
        """Collect tech stack data from GitHub."""
        self.logger.info("Starting GitHub data collection")
        
        # Collect from popular languages
        languages = ["python", "javascript", "java", "go", "rust"]
        all_tech_stacks = []
        
        for language in languages:
            self.logger.info(f"Collecting {language} repositories")
            repos = self.get_popular_repos(min_stars=min_stars, language=language)
            
            for repo in repos:
                try:
                    tech_stack = self.get_repo_tech_stack(repo)
                    if self.validate_entry(tech_stack):
                        all_tech_stacks.append(tech_stack)
                        if len(all_tech_stacks) >= limit:
                            break
                except Exception as e:
                    self.logger.error(f"Error processing repository {repo['name']}: {str(e)}")
            
            if len(all_tech_stacks) >= limit:
                break
        
        # Save collected data
        if all_tech_stacks:
            self.save_data(all_tech_stacks, "tech_stacks_github")
        
        self.logger.info(f"Collected {len(all_tech_stacks)} tech stacks from GitHub")
        return all_tech_stacks[:limit]

    def search_projects(self, query: str, limit: int = 5) -> list:
        """Search GitHub for repositories relevant to the query and return their tech stacks."""
        # Simple keyword extraction: remove stopwords, punctuation, and use top 5 words
        stopwords = set(['the', 'and', 'for', 'with', 'to', 'of', 'a', 'in', 'on', 'is', 'it', 'as', 'by', 'at', 'an', 'be', 'or', 'from', 'that', 'this', 'are', 'was', 'but', 'if', 'then', 'so', 'should', 'can', 'will', 'has', 'have', 'had', 'do', 'does', 'did', 'which', 'who', 'what', 'when', 'where', 'why', 'how', 'all', 'any', 'each', 'other', 'their', 'more', 'most', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'than', 'too', 'very', 's', 't', 'just', 'now'])
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stopwords]
        keywords = keywords[:5]  # Take top 5
        github_query = '+'.join(keywords)
        params = {
            'q': github_query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': limit
        }
        try:
            response = requests.get(
                f'{self.api_url}/search/repositories',
                params=params,
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 403:
                if 'X-RateLimit-Remaining' in response.headers and int(response.headers['X-RateLimit-Remaining']) == 0:
                    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                    wait_time = max(reset_time - time.time(), 0) + 1
                    logger.warning(f"GitHub rate limit exceeded. Waiting {wait_time:.0f} seconds...")
                    raise Exception('GitHub rate limit exceeded')
            response.raise_for_status()
            data = response.json()
            if 'items' not in data:
                logger.error(f"Unexpected API response: {data}")
                return []
            repos = data['items']
            tech_stacks = []
            for repo in repos:
                try:
                    tech_stack = self.get_repo_tech_stack(repo)
                    if self.validate_entry(tech_stack):
                        tech_stacks.append(tech_stack)
                except Exception as e:
                    logger.error(f"Error processing repository {repo['name']}: {str(e)}")
            return tech_stacks
        except Exception as e:
            logger.error(f"Error searching GitHub: {str(e)}")
            return []

def main():
    # Initialize collector
    collector = GitHubCollector()
    
    # Collect data for popular languages
    languages = ['python', 'javascript', 'java', 'go', 'rust']
    output_file = collector.collect_and_save(min_stars=1000, languages=languages)
    
    logger.info(f"Data collection completed. Output saved to: {output_file}")

if __name__ == "__main__":
    main() 