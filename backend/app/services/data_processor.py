from typing import List, Dict, Any, Optional
from app.services.logging_service import LoggingService
import re
from collections import Counter
import time

class DataProcessor:
    def __init__(self):
        self.logger = LoggingService()
        self.tech_stack_patterns = {
            'frontend': [
                r'react', r'vue', r'angular', r'svelte',
                r'typescript', r'javascript', r'html', r'css',
                r'tailwind', r'bootstrap', r'material-ui'
            ],
            'backend': [
                r'node\.js', r'express', r'django', r'flask',
                r'fastapi', r'spring', r'laravel', r'ruby on rails',
                r'asp\.net', r'php'
            ],
            'database': [
                r'mongodb', r'postgresql', r'mysql', r'sqlite',
                r'redis', r'cassandra', r'elasticsearch'
            ],
            'devops': [
                r'docker', r'kubernetes', r'aws', r'azure',
                r'gcp', r'jenkins', r'github actions', r'gitlab ci'
            ]
        }
    
    def process_github_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and normalize GitHub repository data.
        """
        try:
            start_time = time.time()
            processed_data = []
            errors = []
            
            for item in data:
                try:
                    processed_item = {
                        'name': item.get('name', ''),
                        'description': self._normalize_text(item.get('description', '')),
                        'technologies': self._extract_technologies(
                            item.get('description', '') + ' ' + 
                            ' '.join(item.get('topics', []))
                        ),
                        'metadata': {
                            'stars': item.get('stargazers_count', 0),
                            'forks': item.get('forks_count', 0),
                            'language': item.get('language', ''),
                            'created_at': item.get('created_at', ''),
                            'updated_at': item.get('updated_at', '')
                        }
                    }
                    processed_data.append(processed_item)
                except Exception as e:
                    errors.append({
                        'item': item.get('name', 'unknown'),
                        'error': str(e)
                    })
            
            duration = (time.time() - start_time) * 1000
            self.logger.log_data_processing(
                source='github',
                data_count=len(processed_data),
                processing_time_ms=duration,
                errors=errors if errors else None
            )
            
            return processed_data
            
        except Exception as e:
            self.logger.error(
                "Error processing GitHub data",
                error=e,
                extra_data={'data_count': len(data)}
            )
            raise
    
    def process_stackoverflow_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and normalize StackOverflow data.
        """
        try:
            start_time = time.time()
            processed_data = []
            errors = []
            
            for item in data:
                try:
                    processed_item = {
                        'name': item.get('title', ''),
                        'description': self._normalize_text(
                            item.get('body', '') + ' ' + 
                            ' '.join(item.get('tags', []))
                        ),
                        'technologies': self._extract_technologies(
                            item.get('body', '') + ' ' + 
                            ' '.join(item.get('tags', []))
                        ),
                        'metadata': {
                            'score': item.get('score', 0),
                            'view_count': item.get('view_count', 0),
                            'answer_count': item.get('answer_count', 0),
                            'created_at': item.get('creation_date', ''),
                            'tags': item.get('tags', [])
                        }
                    }
                    processed_data.append(processed_item)
                except Exception as e:
                    errors.append({
                        'item': item.get('title', 'unknown'),
                        'error': str(e)
                    })
            
            duration = (time.time() - start_time) * 1000
            self.logger.log_data_processing(
                source='stackoverflow',
                data_count=len(processed_data),
                processing_time_ms=duration,
                errors=errors if errors else None
            )
            
            return processed_data
            
        except Exception as e:
            self.logger.error(
                "Error processing StackOverflow data",
                error=e,
                extra_data={'data_count': len(data)}
            )
            raise
    
    def _extract_technologies(self, text: str) -> List[str]:
        """
        Extract technology mentions from text using regex patterns.
        """
        try:
            technologies = set()
            text = text.lower()
            
            for category, patterns in self.tech_stack_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text):
                        technologies.add(pattern.replace(r'\.', '.'))
            
            return list(technologies)
            
        except Exception as e:
            self.logger.error(
                "Error extracting technologies",
                error=e,
                extra_data={'text_length': len(text)}
            )
            return []
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text by removing special characters and extra whitespace.
        """
        try:
            if not text:
                return ""
            
            # Remove special characters and extra whitespace
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
            
        except Exception as e:
            self.logger.error(
                "Error normalizing text",
                error=e,
                extra_data={'text_length': len(text)}
            )
            return text
    
    def calculate_similarity_score(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two text strings.
        """
        try:
            if not text1 or not text2:
                return 0.0
            
            # Normalize texts
            text1 = self._normalize_text(text1)
            text2 = self._normalize_text(text2)
            
            # Convert to sets of words
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception as e:
            self.logger.error(
                "Error calculating similarity score",
                error=e,
                extra_data={
                    'text1_length': len(text1),
                    'text2_length': len(text2)
                }
            )
            return 0.0
    
    def get_technology_frequency(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Calculate frequency of technologies across processed data.
        """
        try:
            all_technologies = []
            for item in data:
                all_technologies.extend(item.get('technologies', []))
            
            return dict(Counter(all_technologies))
            
        except Exception as e:
            self.logger.error(
                "Error calculating technology frequency",
                error=e,
                extra_data={'data_count': len(data)}
            )
            return {}
    
    def filter_by_technologies(self, 
                             data: List[Dict[str, Any]], 
                             technologies: List[str]) -> List[Dict[str, Any]]:
        """
        Filter data by specified technologies.
        """
        try:
            if not technologies:
                return data
            
            technologies = set(tech.lower() for tech in technologies)
            return [
                item for item in data
                if any(tech.lower() in technologies 
                      for tech in item.get('technologies', []))
            ]
            
        except Exception as e:
            self.logger.error(
                "Error filtering by technologies",
                error=e,
                extra_data={
                    'data_count': len(data),
                    'technologies': technologies
                }
            )
            return [] 