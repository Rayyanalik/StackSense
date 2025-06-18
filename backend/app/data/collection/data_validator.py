import json
import logging
from typing import Dict, List, Any, Set
from datetime import datetime
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechStackValidator:
    """Validates and normalizes tech stack data."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.required_fields = {
            'name': str,
            'description': str,
            'technologies': list,
            'domain': str,
            'source': str
        }
        
        # Technology name mappings for normalization
        self.tech_mappings = {
            # Programming Languages
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
            
            # Frontend Frameworks
            'react': 'React',
            'reactjs': 'React',
            'vue': 'Vue.js',
            'vuejs': 'Vue.js',
            'angular': 'Angular',
            'angularjs': 'AngularJS',
            'svelte': 'Svelte',
            'next': 'Next.js',
            'nextjs': 'Next.js',
            'nuxt': 'Nuxt.js',
            'nuxtjs': 'Nuxt.js',
            
            # Backend Frameworks
            'node': 'Node.js',
            'nodejs': 'Node.js',
            'express': 'Express.js',
            'expressjs': 'Express.js',
            'django': 'Django',
            'flask': 'Flask',
            'spring': 'Spring Boot',
            'springboot': 'Spring Boot',
            'laravel': 'Laravel',
            'rails': 'Ruby on Rails',
            'ror': 'Ruby on Rails',
            'fastapi': 'FastAPI',
            'nest': 'NestJS',
            'nestjs': 'NestJS',
            
            # Databases
            'postgres': 'PostgreSQL',
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'mongo': 'MongoDB',
            'mongodb': 'MongoDB',
            'redis': 'Redis',
            'cassandra': 'Apache Cassandra',
            'elastic': 'Elasticsearch',
            'elasticsearch': 'Elasticsearch',
            
            # Cloud Platforms
            'aws': 'Amazon Web Services',
            'azure': 'Microsoft Azure',
            'gcp': 'Google Cloud Platform',
            'do': 'DigitalOcean',
            'digitalocean': 'DigitalOcean',
            'heroku': 'Heroku',
            
            # DevOps Tools
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes',
            'jenkins': 'Jenkins',
            'gitlab': 'GitLab',
            'github': 'GitHub',
            'terraform': 'Terraform',
            'ansible': 'Ansible',
            
            # AI/ML Frameworks
            'tensorflow': 'TensorFlow',
            'pytorch': 'PyTorch',
            'sklearn': 'scikit-learn',
            'scikit-learn': 'scikit-learn',
            'opencv': 'OpenCV',
            'nltk': 'NLTK',
            'spacy': 'spaCy',
            
            # Testing Frameworks
            'jest': 'Jest',
            'mocha': 'Mocha',
            'pytest': 'pytest',
            'junit': 'JUnit',
            'cypress': 'Cypress',
            'selenium': 'Selenium'
        }
    
    def validate_entry(self, entry: Dict[str, Any]) -> bool:
        """Validate a single tech stack entry."""
        try:
            # Check required fields
            for field, field_type in self.required_fields.items():
                if field not in entry:
                    self.logger.warning(f"Missing required field '{field}' in entry: {entry.get('name', 'Unknown')}")
                    return False
                
                if not isinstance(entry[field], field_type):
                    self.logger.warning(f"Invalid type for field '{field}' in entry: {entry.get('name', 'Unknown')}")
                    return False
            
            # Validate field values
            if not entry['name'].strip():
                self.logger.warning(f"Empty name in entry")
                return False
            
            if not entry['description'].strip():
                self.logger.warning(f"Empty description in entry: {entry['name']}")
                return False
            
            if not entry['technologies']:
                self.logger.warning(f"No technologies in entry: {entry['name']}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating entry: {str(e)}")
            return False
    
    def normalize_tech_name(self, tech_name: str) -> str:
        """Normalize a technology name to its standard form."""
        # Convert to lowercase for matching
        tech_name = tech_name.lower().strip()
        
        # Return mapped name if exists, otherwise capitalize
        return self.tech_mappings.get(tech_name, tech_name.title())
    
    def normalize_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a tech stack entry."""
        normalized = entry.copy()
        
        # Normalize technology names
        normalized['technologies'] = [
            self.normalize_tech_name(tech)
            for tech in entry['technologies']
        ]
        
        # Remove duplicates from technologies
        normalized['technologies'] = list(set(normalized['technologies']))
        
        # Normalize name and description
        normalized['name'] = entry['name'].strip()
        normalized['description'] = entry['description'].strip()
        
        # Add normalization timestamp
        normalized['normalized_at'] = datetime.now().isoformat()
        
        return normalized
    
    def validate_and_normalize_file(self, input_file: str) -> str:
        """Validate and normalize all entries in a file."""
        try:
            # Read input file
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            # Process entries
            valid_entries = []
            for entry in data:
                if self.validate_entry(entry):
                    normalized_entry = self.normalize_entry(entry)
                    valid_entries.append(normalized_entry)
            
            # Save validated and normalized data
            output_dir = os.path.dirname(input_file)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"tech_stacks_validated_{timestamp}.json")
            
            with open(output_file, 'w') as f:
                json.dump(valid_entries, f, indent=2)
            
            self.logger.info(f"Validated and normalized {len(valid_entries)} entries")
            self.logger.info(f"Output saved to: {output_file}")
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error processing file {input_file}: {str(e)}")
            raise
    
    def calculate_quality_metrics(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate quality metrics for the dataset."""
        metrics = {
            'total_entries': len(data),
            'unique_technologies': len(set(
                tech for entry in data for tech in entry['technologies']
            )),
            'avg_technologies_per_stack': sum(
                len(entry['technologies']) for entry in data
            ) / len(data) if data else 0,
            'missing_descriptions': sum(
                1 for entry in data if not entry['description'].strip()
            ),
            'avg_description_length': sum(
                len(entry['description']) for entry in data
            ) / len(data) if data else 0,
            'source_distribution': {},
            'domain_distribution': {},
            'technology_frequency': {}
        }
        
        # Calculate distributions
        for entry in data:
            # Source distribution
            source = entry.get('source', 'unknown')
            metrics['source_distribution'][source] = metrics['source_distribution'].get(source, 0) + 1
            
            # Domain distribution
            domain = entry.get('domain', 'unknown')
            metrics['domain_distribution'][domain] = metrics['domain_distribution'].get(domain, 0) + 1
            
            # Technology frequency
            for tech in entry['technologies']:
                metrics['technology_frequency'][tech] = metrics['technology_frequency'].get(tech, 0) + 1
        
        return metrics

def main():
    validator = TechStackValidator()
    
    # Get the most recent tech stacks file
    data_dir = Path(__file__).parent.parent
    tech_stack_files = list(data_dir.glob('tech_stacks_github_*.json'))
    
    if not tech_stack_files:
        logger.error("No tech stack files found")
        return
    
    latest_file = max(tech_stack_files, key=lambda x: x.stat().st_mtime)
    
    # Validate and normalize
    validated_file = validator.validate_and_normalize_file(latest_file)
    
    # Analyze data quality
    analysis = validator.calculate_quality_metrics(validator.analyze_data_quality(validated_file))
    
    # Print analysis results
    logger.info("\nData Quality Analysis:")
    for key, value in analysis.items():
        if key != 'technology_frequency':
            logger.info(f"{key}: {value}")
    
    logger.info("\nTop 10 Most Common Technologies:")
    for tech, count in list(analysis['technology_frequency'].items())[:10]:
        logger.info(f"{tech}: {count}")

if __name__ == "__main__":
    main() 