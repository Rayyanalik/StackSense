import pandas as pd
import numpy as np
import spacy
import logging
from typing import List, Dict, Any, Optional, Union
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import json
import os
from datetime import datetime
from .feedback_handler import FeedbackHandler
import re
from html import escape

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles data cleaning, validation, and enrichment."""
    
    def __init__(self, output_dir: str = "processed_data"):
        """
        Initialize the data processor.
        
        Args:
            output_dir: Directory to save processed data
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.info("Downloading spaCy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Load technology mapping
        self.tech_mapping = self._load_tech_mapping()
        
        # Initialize feedback handler
        self.feedback_handler = FeedbackHandler()
        
        # Initialize LDA model
        self.lda = LatentDirichletAllocation(
            n_components=5,
            random_state=42
        )
        self.vectorizer = CountVectorizer(
            max_df=0.95,
            min_df=2,
            stop_words='english'
        )
        
        self.technology_pattern = re.compile(r'^[a-zA-Z0-9\s\-\.\+]+$')
    
    def _load_tech_mapping(self) -> Dict[str, str]:
        """Load technology name normalization mapping."""
        mapping_file = os.path.join(os.path.dirname(__file__), 'tech_mapping.json')
        try:
            with open(mapping_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Tech mapping file not found: {mapping_file}")
            return {}
    
    def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a list of project data dictionaries.
        
        Args:
            data: List of dictionaries containing project data
            
        Returns:
            List of processed project data dictionaries
            
        Raises:
            TypeError: If data is not a list or contains invalid items
        """
        if not isinstance(data, list):
            raise TypeError("Data must be a list")
        
        processed_data = []
        for item in data:
            if not isinstance(item, dict):
                raise TypeError("Each item must be a dictionary")
            
            processed_item = self._process_item(item)
            processed_data.append(processed_item)
        
        return processed_data
    
    def _process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single project data dictionary.
        
        Args:
            item: Dictionary containing project data
            
        Returns:
            Processed project data dictionary
        """
        processed = {
            'name': str(item.get('name', '')),
            'description': self._process_description(item.get('description', '')),
            'technologies': self._process_technologies(item.get('technologies', [])),
            'metadata': self._process_metadata(item.get('metadata', {}))
        }
        
        return processed
    
    def _process_description(self, description: str) -> str:
        """
        Process project description.
        
        Args:
            description: Project description string
            
        Returns:
            Processed description string
        """
        if not isinstance(description, str):
            return ''
        
        # Escape HTML to prevent XSS
        description = escape(description)
        
        # Remove any remaining script tags
        description = re.sub(r'<script.*?>.*?</script>', '', description, flags=re.IGNORECASE)
        
        return description
    
    def _process_technologies(self, technologies: Union[List[str], str]) -> List[str]:
        """
        Process technologies list.
        
        Args:
            technologies: List of technology strings or comma-separated string
            
        Returns:
            List of processed technology strings
        """
        if isinstance(technologies, str):
            # Split comma-separated string into list
            technologies = [t.strip() for t in technologies.split(',')]
        elif not isinstance(technologies, list):
            return []
        
        # Process each technology
        processed_techs = set()
        for tech in technologies:
            if not isinstance(tech, str):
                continue
            
            tech = tech.strip()
            if not tech:
                continue
            
            # Validate technology name
            if not self.technology_pattern.match(tech):
                continue
            
            # Normalize case (capitalize first letter)
            tech = tech[0].upper() + tech[1:].lower()
            processed_techs.add(tech)
        
        return sorted(list(processed_techs))
    
    def _process_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process metadata dictionary.
        
        Args:
            metadata: Dictionary containing metadata
            
        Returns:
            Processed metadata dictionary
        """
        if not isinstance(metadata, dict):
            return {}
        
        processed = {}
        for key, value in metadata.items():
            if not isinstance(key, str):
                continue
            
            # Convert numeric values to appropriate type
            if isinstance(value, (int, float)):
                processed[key] = value
            elif isinstance(value, str):
                try:
                    # Try to convert string to number
                    processed[key] = float(value) if '.' in value else int(value)
                except ValueError:
                    processed[key] = value
            else:
                processed[key] = str(value)
        
        return processed
    
    def _clean_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Clean the input data."""
        logger.info("Cleaning data...")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['title', 'description', 'technologies'])
        
        # Clean text fields
        df['title'] = df['title'].str.strip()
        df['description'] = df['description'].str.strip()
        
        # Clean technology lists
        df['technologies'] = df['technologies'].apply(
            lambda x: [tech.strip() for tech in x if tech.strip()]
        )
        
        # Remove empty entries
        df = df.dropna(subset=['title', 'description', 'technologies'])
        
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate the data structure and content."""
        logger.info("Validating data...")
        
        # Check required fields
        required_fields = ['title', 'description', 'technologies', 'domain', 'source']
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Validate data types
        df['technologies'] = df['technologies'].apply(
            lambda x: x if isinstance(x, list) else []
        )
        
        # Validate technology names
        df['technologies'] = df['technologies'].apply(
            lambda x: [tech for tech in x if isinstance(tech, str) and tech.strip()]
        )
        
        return df
    
    def _enrich_technologies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich technology information."""
        logger.info("Enriching technology information...")
        
        # Normalize technology names
        df['technologies'] = df['technologies'].apply(
            lambda x: [self.tech_mapping.get(tech.lower(), tech) for tech in x]
        )
        
        # Remove duplicates in technology lists
        df['technologies'] = df['technologies'].apply(lambda x: list(set(x)))
        
        # Add technology count
        df['tech_count'] = df['technologies'].apply(len)
        
        return df
    
    def _enrich_descriptions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich description information using NLP."""
        logger.info("Enriching descriptions...")
        
        # Process descriptions with spaCy
        df['processed_description'] = df['description'].apply(
            lambda x: self._process_text(x)
        )
        
        # Extract key phrases
        df['key_phrases'] = df['processed_description'].apply(
            lambda x: self._extract_key_phrases(x)
        )
        
        # Add description length
        df['description_length'] = df['description'].str.len()
        
        return df
    
    def _enrich_domains(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enrich domain information using topic modeling."""
        logger.info("Enriching domain information...")
        
        # Process descriptions
        processed_texts = df['processed_description'].tolist()
        
        # Fit LDA
        X = self.vectorizer.fit_transform(processed_texts)
        self.lda.fit(X)
        
        # Get topic distributions
        topic_dist = self.lda.transform(X)
        
        # Add topic distributions to DataFrame
        for i in range(topic_dist.shape[1]):
            df[f'topic_{i}_weight'] = topic_dist[:, i]
        
        return df
    
    def _process_text(self, text: str) -> str:
        """Process text using spaCy."""
        doc = self.nlp(text)
        
        # Lemmatize and remove stop words
        processed = [
            token.lemma_.lower()
            for token in doc
            if not token.is_stop and not token.is_punct
        ]
        
        return ' '.join(processed)
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text."""
        doc = self.nlp(text)
        
        # Extract noun phrases
        key_phrases = [
            chunk.text
            for chunk in doc.noun_chunks
            if len(chunk.text.split()) <= 3
        ]
        
        return key_phrases

    def clean_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and standardize the collected data."""
        cleaned_data = []
        
        for entry in data:
            try:
                # Create a copy of the entry to avoid modifying the original
                cleaned_entry = entry.copy()
                
                # Handle missing fields
                if 'name' not in cleaned_entry and 'title' in cleaned_entry:
                    cleaned_entry['name'] = cleaned_entry['title']
                elif 'name' not in cleaned_entry:
                    cleaned_entry['name'] = f"Untitled_{len(cleaned_data)}"
                
                # Ensure required fields exist
                required_fields = ['name', 'description', 'technologies', 'metadata']
                for field in required_fields:
                    if field not in cleaned_entry:
                        if field == 'technologies':
                            cleaned_entry[field] = []
                        elif field == 'metadata':
                            cleaned_entry[field] = {}
                        else:
                            cleaned_entry[field] = ""
                
                # Clean and standardize technologies
                if isinstance(cleaned_entry['technologies'], list):
                    cleaned_entry['technologies'] = [
                        self.standardize_technology(tech)
                        for tech in cleaned_entry['technologies']
                        if tech and isinstance(tech, str)
                    ]
                else:
                    cleaned_entry['technologies'] = []
                
                # Add derived fields
                cleaned_entry['tech_count'] = len(cleaned_entry['technologies'])
                cleaned_entry['description_length'] = len(cleaned_entry.get('description', ''))
                
                # Add domain if not present
                if 'domain' not in cleaned_entry:
                    cleaned_entry['domain'] = self.infer_domain(cleaned_entry)
                
                cleaned_data.append(cleaned_entry)
                
            except Exception as e:
                logger.error(f"Error cleaning entry: {str(e)}")
                continue
        
        return cleaned_data

    def standardize_technology(self, tech: str) -> str:
        """Standardize technology names."""
        if not tech or not isinstance(tech, str):
            return ""
            
        # Convert to title case and remove extra whitespace
        tech = tech.strip().title()
        
        # Apply common corrections
        corrections = {
            'Javascript': 'JavaScript',
            'Typescript': 'TypeScript',
            'Reactjs': 'React',
            'React.js': 'React',
            'Nodejs': 'Node.js',
            'Node.js': 'Node.js',
            'Python3': 'Python',
            'Django3': 'Django',
            'Flask2': 'Flask',
            'Springboot': 'Spring Boot',
            'Spring Boot': 'Spring Boot',
            'Angularjs': 'Angular',
            'Vuejs': 'Vue.js',
            'Vue.js': 'Vue.js'
        }
        
        return corrections.get(tech, tech)

    def infer_domain(self, entry: dict) -> str:
        """Infer the domain of a tech stack entry. Returns 'General' by default for minimal or malformed data."""
        # You can expand this logic as needed for more advanced domain inference
        return 'General'

def main():
    """Run the data processor."""
    try:
        # Initialize processor
        processor = DataProcessor()
        
        # Load input data
        input_file = "data/merged_tech_stacks_latest.json"
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        # Process data
        result = processor.process_data(data)
        
        # Get and print statistics
        logger.info("Processing Statistics:")
        for key, value in result['statistics'].items():
            logger.info(f"{key}: {value}")
        
    except Exception as e:
        logger.error(f"Error during data processing: {str(e)}")
        raise

if __name__ == "__main__":
    main() 