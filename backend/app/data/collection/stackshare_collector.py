import logging
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from pathlib import Path
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

class StackShareCollector:
    """Collects tech stack data from StackShare API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the StackShare collector.
        
        Args:
            api_key: StackShare API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('STACKSHARE_API_KEY')
        if not self.api_key:
            logger.warning("No StackShare API key provided. Set STACKSHARE_API_KEY environment variable.")
        
        self.base_url = "https://api.stackshare.io/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }
        
        # Create data directory if it doesn't exist
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
    
    def collect_data(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Collect tech stack data from StackShare.
        
        Args:
            limit: Maximum number of tech stacks to collect
            
        Returns:
            List of tech stack entries
        """
        if not self.api_key:
            logger.error("Cannot collect data: No StackShare API key provided")
            return []
            
        logger.info(f"Collecting tech stacks from StackShare (limit: {limit})")
        
        try:
            # GraphQL query to get tech stacks
            query = """
            query {
                techStacks(first: %d) {
                    edges {
                        node {
                            name
                            description
                            technologies {
                                edges {
                                    node {
                                        name
                                        category
                                    }
                                }
                            }
                            company {
                                name
                                website
                            }
                        }
                    }
                }
            }
            """ % limit
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query},
                verify=False  # Disable SSL verification
            )
            
            if response.status_code != 200:
                logger.error(f"Error fetching StackShare data: {response.text}")
                return []
                
            data = response.json()
            
            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return []
            
            tech_stacks = []
            for edge in data.get("data", {}).get("techStacks", {}).get("edges", []):
                node = edge["node"]
                company = node.get("company", {})
                
                # Extract technologies
                technologies = [
                    tech["node"]["name"]
                    for tech in node.get("technologies", {}).get("edges", [])
                ]
                
                # Create tech stack entry
                entry = {
                    "name": node.get("name", ""),
                    "description": node.get("description", ""),
                    "technologies": technologies,
                    "metadata": {
                        "company": company.get("name", ""),
                        "website": company.get("website", ""),
                        "source": "StackShare",
                        "collected_at": datetime.now().isoformat()
                    }
                }
                
                tech_stacks.append(entry)
            
            # Save to file
            if tech_stacks:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = self.data_dir / f"tech_stacks_stackshare_{timestamp}.json"
                with open(filename, "w") as f:
                    json.dump(tech_stacks, f, indent=2)
                logger.info(f"Saved {len(tech_stacks)} entries to {filename}")
            
            return tech_stacks
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL Error: {str(e)}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request Error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error collecting StackShare data: {str(e)}")
            return []

def main():
    """Test the StackShare collector."""
    collector = StackShareCollector()
    stacks = collector.collect_data(limit=10)
    
    # Print sample data
    if stacks:
        print("\nSample StackShare Data:")
        print(f"Total stacks collected: {len(stacks)}")
        print("\nFirst stack:")
        print(f"Title: {stacks[0]['name']}")
        print(f"Description: {stacks[0]['description']}")
        print(f"Technologies: {', '.join(stacks[0]['technologies'])}")

if __name__ == "__main__":
    main() 