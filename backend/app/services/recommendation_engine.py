from typing import List, Dict, Any, Optional, Union
from app.core.logging import logger
import time
from collections import Counter
from .data_processor import DataProcessor
import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from app.data.collection.github_collector import GitHubCollector
from app.data.collection.stackoverflow_collector import StackOverflowCollector
import requests
import cohere

class RecommendationEngine:
    def __init__(self):
        self.tech_categories = {
            'frontend': ['react', 'vue', 'angular', 'svelte', 'next.js', 'gatsby', 'ember', 'preact', 'jquery', 'backbone', 'aurelia', 'knockout', 'mithril'],
            'backend': ['node.js', 'nodejs', 'django', 'flask', 'spring', 'springboot', 'fastapi', 'ruby on rails', 'rails', 'laravel', 'express', 'koa', 'phoenix', 'gin', 'asp.net', 'actix'],
            'database': ['mongodb', 'postgresql', 'postgres', 'mysql', 'redis', 'sqlite', 'mariadb', 'cassandra', 'dynamodb', 'firebase', 'couchbase', 'rethinkdb'],
            'devops': ['docker', 'kubernetes', 'aws', 'jenkins', 'gcp', 'azure', 'travis ci', 'circleci', 'gitlab ci', 'ansible', 'puppet', 'chef', 'terraform', 'vagrant'],
            'mobile': ['react native', 'flutter', 'swift', 'kotlin', 'xamarin', 'ionic', 'cordova'],
            'language': ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c#', 'php', 'ruby', 'scala', 'c++', 'swift', 'kotlin', 'elixir'],
            'testing': ['jest', 'mocha', 'chai', 'selenium', 'cypress', 'junit', 'pytest', 'rspec', 'testing-library'],
            'orm': ['sqlalchemy', 'django orm', 'typeorm', 'sequelize', 'prisma', 'gorm', 'hibernate', 'peewee'],
            'api': ['graphql', 'rest', 'grpc'],
        }
        self.project_data = self._load_project_data()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.project_embeddings = self._precompute_project_embeddings()

    def _load_project_data(self) -> List[Dict[str, Any]]:
        """Load project data from a JSON file."""
        data_path = os.path.join(os.path.dirname(__file__), '../../data/tech_stacks.json')
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
                # Support both {"tech_stacks": [...]} and plain list
                if isinstance(data, dict) and 'tech_stacks' in data:
                    return data['tech_stacks']
                elif isinstance(data, list):
                    return data
                else:
                    logger.warning("Project data format not recognized.")
                    return []
        except Exception as e:
            logger.error(f"Failed to load project data: {e}")
            return []

    def _precompute_project_embeddings(self):
        """Compute and cache embeddings for all project descriptions."""
        descriptions = [p['description'] for p in self.project_data]
        if not descriptions:
            return np.array([])
        return self.model.encode(descriptions, show_progress_bar=False)

    def find_similar_projects(self, user_description: str, top_n: int = 5):
        """Find top-N most similar projects using embeddings and cosine similarity."""
        if not self.project_data or self.project_embeddings.shape[0] == 0:
            return []
        user_emb = self.model.encode([user_description])[0]
        similarities = cosine_similarity([user_emb], self.project_embeddings)[0]
        top_indices = np.argsort(similarities)[::-1][:top_n]
        return [self.project_data[i] for i in top_indices]

    def generate_recommendation(
        self,
        project_description: str,
        requirements: List[str],
        constraints: Optional[Dict[str, Union[str, List[str]]]] = None
    ) -> Dict[str, Any]:
        """
        Generates a tech stack recommendation by combining results from an LLM and similar projects from GitHub.
        """
        # --- Stage 1: Always fetch similar projects from GitHub for context ---
        github_projects = []
        try:
            github_collector = GitHubCollector()
            github_projects = github_collector.search_projects(project_description, limit=5)
            logger.info(f"Found {len(github_projects)} similar projects on GitHub.")
        except Exception as e:
            logger.warning(f"GitHub search for similar projects failed: {e}")

        # --- Stage 2: Always use an LLM to generate the core recommendation ---
        llm_recommendation = None

        # Attempt Perplexity LLM first
        try:
            logger.info("Attempting Perplexity LLM for recommendation.")
            api_key = os.getenv('PERPLEXITY_API_KEY')
            if not api_key:
                raise Exception('PERPLEXITY_API_KEY not set')
            
            url = "https://api.perplexity.ai/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            prompt = self._get_llm_prompt(project_description)
            payload = {
                "model": "llama-3-sonar-large-32k-online",
                "messages": [
                    {"role": "system", "content": "You are an AI assistant that provides tech stack recommendations in a strict JSON format."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1024,
                "response_format": {"type": "json_object"}
            }
            
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if resp.status_code != 200:
                logger.error(f"Perplexity API call failed with status {resp.status_code}: {resp.text}")
                resp.raise_for_status()

            llm_response_text = resp.json()['choices'][0]['message']['content']
            llm_data = json.loads(llm_response_text.strip().removeprefix("```json").removesuffix("```"))
            
            llm_recommendation = {
                'primary_tech_stack': llm_data.get('primary_tech_stack', []),
                'detailed_explanation': llm_data.get('explanation'),
                'confidence_level': 0.8
            }
            logger.info('Successfully received recommendation from Perplexity.')

        except Exception as e:
            logger.error(f"Perplexity LLM processing failed: {e}", exc_info=True)

        # If Perplexity fails, attempt Cohere LLM
        if llm_recommendation is None:
            try:
                logger.info("Attempting Cohere LLM for recommendation.")
                cohere_api_key = os.getenv('COHERE_API_KEY')
                if not cohere_api_key:
                    raise Exception('COHERE_API_KEY not set')

                co = cohere.Client(cohere_api_key)
                prompt = self._get_llm_prompt(project_description)
                
                response = co.chat(model="command-r-plus", message=prompt, temperature=0.3, max_tokens=1024)
                
                llm_response_text = response.text
                llm_data = json.loads(llm_response_text.strip().removeprefix("```json").removesuffix("```"))
                
                llm_recommendation = {
                    'primary_tech_stack': llm_data.get('primary_tech_stack', []),
                    'detailed_explanation': llm_data.get('explanation'),
                    'confidence_level': 0.75
                }
                logger.info('Successfully received recommendation from Cohere.')

            except Exception as e:
                logger.error(f"Cohere LLM processing failed: {e}", exc_info=True)

        # --- Stage 3: Fallback to local data if both LLMs fail ---
        if llm_recommendation is None:
            logger.info('All external APIs failed. Falling back to local dataset.')
            local_rec = self._generate_local_recommendation(project_description, requirements, constraints)
            final_recommendation = {
                'primary_tech_stack': local_rec.get('primary_tech_stack', []),
                'alternatives': local_rec.get('alternatives', {}),
                'explanation': "This recommendation was generated from our local dataset as external services were unavailable.",
                'detailed_explanation': None,
                'confidence_level': 0.5,
                'similar_projects': github_projects or local_rec.get('similar_projects', []) # Use GitHub projects if available
            }
        else:
            # --- Stage 4: Combine GitHub results with LLM recommendation ---
            final_recommendation = {
                'primary_tech_stack': llm_recommendation.get('primary_tech_stack'),
                'alternatives': {}, # LLMs are not currently generating alternatives
                'explanation': "This is the best fit tech stack generated by our StackSense AI based on your project description.",
                'detailed_explanation': llm_recommendation.get('detailed_explanation'),
                'confidence_level': llm_recommendation.get('confidence_level'),
                'similar_projects': github_projects
            }

        logger.info(f'Final recommendation: {final_recommendation}')
        return final_recommendation

    def _get_llm_prompt(self, project_description: str) -> str:
        """Generates a standardized prompt for LLM recommendations."""
        return f"""
        You are an expert software architect. Your task is to suggest a modern tech stack for the project described below and provide a justification.
        Project Description: '{project_description}'

        You MUST provide your response as a single, valid JSON object, without any surrounding text or markdown formatting.
        The JSON object must have two keys: 'primary_tech_stack' and 'explanation'.
        - 'primary_tech_stack' must be a list of objects. Each object must have a 'category' string and a 'name' string.
        - 'explanation' must be a string that provides a detailed justification for why this is a good tech stack for the project.

        Here is an example of the required output format:
        {{
          "primary_tech_stack": [
            {{"category": "frontend", "name": "React"}},
            {{"category": "backend", "name": "Node.js with Express"}},
            {{"category": "database", "name": "PostgreSQL"}}
          ],
          "explanation": "This stack is ideal for a modern SaaS platform because React offers a rich ecosystem for building interactive UIs, Node.js is efficient for I/O-heavy operations, and PostgreSQL is a robust and reliable relational database."
        }}
        """

    def _generate_local_recommendation(self, project_description, requirements, constraints):
        # (existing local logic from previous generate_recommendation)
        start_time = time.time()
        
        if not self.project_data:
            return {
                "primary_tech_stack": [],
                "alternatives": {},
                "explanation": "Could not generate a recommendation due to missing project data.",
                "confidence_level": 0.0,
                "similar_projects": []
            }
            
        similar_projects = self.find_similar_projects(project_description)

        if not similar_projects:
            return {
                "primary_tech_stack": [],
                "alternatives": {},
                "explanation": "Could not find any similar projects in the local dataset to generate a recommendation.",
                "confidence_level": 0.0,
                "similar_projects": []
            }

        all_tech = [tech for proj in similar_projects for tech in proj['tech_stack']]
        tech_frequency = Counter(all_tech)
        
        primary_stack = self._generate_primary_stack(tech_frequency, constraints if constraints else {})
        alternatives = self._generate_alternatives(tech_frequency, primary_stack, constraints if constraints else {})
        confidence = self._calculate_confidence(similar_projects, tech_frequency)
        explanation = self._generate_explanation(primary_stack, alternatives, similar_projects, confidence)

        end_time = time.time()
        logger.info(f"Local recommendation generated in {end_time - start_time:.2f} seconds.")

        return {
            "primary_tech_stack": primary_stack,
            "alternatives": alternatives,
            "explanation": explanation,
            "confidence_level": confidence,
            "similar_projects": similar_projects,
        }

    def _generate_primary_stack(self, tech_frequency, constraints):
        primary_stack = []
        used_tech = set()
        
        # Respect hard constraints first
        for category, tech in constraints.items():
            if category in self.tech_categories and tech not in used_tech:
                primary_stack.append({'category': category, 'name': tech})
                used_tech.add(tech)

        # Fill remaining categories based on frequency
        for category, tech_list in self.tech_categories.items():
            if not any(t['category'] == category for t in primary_stack):
                # Find the most frequent tech for this category that is not already used
                most_frequent_tech = None
                max_freq = -1
                for tech, freq in tech_frequency.items():
                    if tech in tech_list and tech not in used_tech and freq > max_freq:
                        most_frequent_tech = tech
                        max_freq = freq
                
                if most_frequent_tech:
                    primary_stack.append({'category': category, 'name': most_frequent_tech})
                    used_tech.add(most_frequent_tech)
        
        return primary_stack

    def _generate_alternatives(self, tech_frequency, primary_stack, constraints):
        alternatives = {}
        primary_tech_names = {t['name'] for t in primary_stack}

        for tech_in_stack in primary_stack:
            category = tech_in_stack['category']
            
            # Find top 3 alternatives for the category, excluding constrained and primary ones
            category_alternatives = []
            for tech, freq in tech_frequency.most_common():
                if tech in self.tech_categories.get(category, []) and \
                   tech not in primary_tech_names and \
                   tech != constraints.get(category):
                    category_alternatives.append({'name': tech, 'description': f"Used in {freq} similar projects."})
                    if len(category_alternatives) >= 3:
                        break
            
            if category_alternatives:
                alternatives[category] = category_alternatives
                
        return alternatives

    def _calculate_confidence(self, similar_projects, tech_frequency):
        # Simple confidence score based on number of similar projects and frequency of top tech
        if not similar_projects:
            return 0.0
        
        confidence = min(len(similar_projects) / 5.0, 1.0) * 0.6 # 60% weight for number of projects
        
        if tech_frequency:
            top_tech_freq = tech_frequency.most_common(1)[0][1]
            confidence += min(top_tech_freq / 10.0, 1.0) * 0.4 # 40% weight for top tech frequency
            
        return round(confidence, 2)

    def _generate_explanation(self, primary_stack, alternatives, similar_projects, confidence):
        stack_str = ', '.join([f"{t['name']} ({t['category']})" for t in primary_stack])
        return (
            f"Based on an analysis of {len(similar_projects)} similar projects, the recommended stack is {stack_str}. "
            f"This recommendation has a confidence score of {confidence * 100}%. "
            f"Key technologies were chosen based on their frequent appearance in comparable projects."
        )