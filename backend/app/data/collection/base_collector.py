from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging
from pathlib import Path
import json
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """Base class for all data collectors."""
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = output_dir
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        """Collect data from the source."""
        pass
    
    def save_data(self, data: List[Dict[str, Any]], prefix: str) -> str:
        """Save collected data to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Saved {len(data)} entries to {filepath}")
        return filepath
    
    def validate_entry(self, entry: Dict[str, Any]) -> bool:
        """Validate a single data entry."""
        required_fields = ['name', 'description', 'technologies']
        
        # Check required fields
        if not all(field in entry for field in required_fields):
            self.logger.warning(f"Missing required fields in entry: {entry.get('name', 'Unknown')}")
            return False
        
        # Validate field types
        if not isinstance(entry['name'], str) or not entry['name'].strip():
            return False
        if not isinstance(entry['description'], str) or not entry['description'].strip():
            return False
        if not isinstance(entry['technologies'], list) or not entry['technologies']:
            return False
        
        return True
    
    def normalize_tech_name(self, tech_name: str) -> str:
        """Normalize technology names to a standard format."""
        # Common technology name mappings
        tech_mappings = {
            'js': 'JavaScript',
            'ts': 'TypeScript',
            'py': 'Python',
            'rb': 'Ruby',
            'php': 'PHP',
            'java': 'Java',
            'go': 'Go',
            'rust': 'Rust',
            'c#': 'C#',
            'c++': 'C++',
            'react': 'React',
            'reactjs': 'React',
            'vue': 'Vue.js',
            'vuejs': 'Vue.js',
            'angular': 'Angular',
            'node': 'Node.js',
            'nodejs': 'Node.js',
            'express': 'Express.js',
            'django': 'Django',
            'flask': 'Flask',
            'spring': 'Spring Boot',
            'springboot': 'Spring Boot',
            'laravel': 'Laravel',
            'rails': 'Ruby on Rails',
            'ror': 'Ruby on Rails',
            'postgres': 'PostgreSQL',
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongo': 'MongoDB',
            'mongodb': 'MongoDB',
            'redis': 'Redis',
            'aws': 'Amazon Web Services',
            'azure': 'Microsoft Azure',
            'gcp': 'Google Cloud Platform',
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes',
        }
        
        # Convert to lowercase for matching
        tech_name = tech_name.lower().strip()
        
        # Return mapped name if exists, otherwise capitalize
        return tech_mappings.get(tech_name, tech_name.title())
    
    def enrich_metadata(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich entry with additional metadata."""
        enriched = entry.copy()
        
        # Add collection timestamp
        enriched['collected_at'] = datetime.now().isoformat()
        
        # Add source information
        enriched['source'] = self.__class__.__name__
        
        # Add technology count
        enriched['tech_count'] = len(entry['technologies'])
        
        # Add description length
        enriched['description_length'] = len(entry['description'])
        
        return enriched
    
    def infer_domain(self, entry: Dict[str, Any]) -> str:
        """Infer the domain/category of the tech stack based on technologies and description."""
        # Domain-specific technology patterns
        domain_patterns = {
            'Web Development': ['react', 'angular', 'vue', 'html', 'css', 'javascript'],
            'Mobile Development': ['react native', 'flutter', 'swift', 'kotlin', 'android'],
            'Data Science': ['python', 'pandas', 'numpy', 'tensorflow', 'pytorch'],
            'DevOps': ['docker', 'kubernetes', 'jenkins', 'terraform', 'ansible'],
            'Backend': ['node', 'python', 'java', 'go', 'ruby'],
            'Database': ['postgresql', 'mysql', 'mongodb', 'redis', 'cassandra'],
            'Cloud': ['aws', 'azure', 'gcp', 'digitalocean', 'heroku'],
            'AI/ML': ['tensorflow', 'pytorch', 'scikit-learn', 'opencv', 'nltk'],
        }
        
        # Count matches for each domain
        domain_scores = {}
        tech_list = [t.lower() for t in entry['technologies']]
        desc_lower = entry['description'].lower()
        
        for domain, patterns in domain_patterns.items():
            score = sum(1 for pattern in patterns if pattern in tech_list or pattern in desc_lower)
            domain_scores[domain] = score
        
        # Return domain with highest score, or 'General' if no clear match
        if domain_scores:
            max_domain = max(domain_scores.items(), key=lambda x: x[1])
            return max_domain[0] if max_domain[1] > 0 else 'General'
        return 'General'

    def save(self, data: List[Dict[str, Any]]) -> Path:
        """Save collected data to a JSON file."""
        try:
            # Create timestamp for filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tech_stacks_{self.__class__.__name__.replace("Collector", "").lower()}_{timestamp}.json'
            output_file = Path(self.output_dir) / filename

            # Save data
            with open(output_file, 'w') as f:
                json.dump({"tech_stacks": data}, f, indent=4)

            logger.info(f"Saved {len(data)} tech stacks to {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
            raise

    def collect_and_save(self) -> Path:
        """Collect data and save it to a file."""
        try:
            data = self.collect()
            return self.save(data)
        except Exception as e:
            logger.error(f"Error in collect_and_save: {str(e)}")
            raise

    def validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Basic validation of collected data."""
        valid_data = []
        for item in data:
            if self.validate_entry(item):
                valid_data.append(item)
        return valid_data

    def enrich_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich collected data with additional information."""
        enriched_data = []
        for item in data:
            enriched_item = self.enrich_metadata(item)
            enriched_data.append(enriched_item)
        return enriched_data 