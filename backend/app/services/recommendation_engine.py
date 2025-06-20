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
            logger.error(f"Perplexity LLM fallback failed: {e}. Trying Cohere.")

        # If Perplexity fails, attempt Cohere LLM
        if llm_recommendation is None:
            try:
                logger.info("Attempting Cohere LLM for recommendation.")
                cohere_api_key = os.getenv('COHERE_API_KEY')
                if not cohere_api_key:
                    raise Exception('COHERE_API_KEY not set')

                import cohere
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
                logger.error(f"Cohere LLM also failed: {e}. Falling back to local data.")

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
        constraint_list = []
        if constraints:
            for category, value in constraints.items():
                if isinstance(value, list):
                    constraint_list.extend(value)
                else:
                    constraint_list.append(str(value))
        N = 5
        similar_projects = self.find_similar_projects(project_description, top_n=N)
        for project in similar_projects:
            techs = []
            for cat in self.tech_categories:
                techs.extend(project.get(cat, []))
            project['technologies'] = techs
        tech_counter = {cat: Counter() for cat in self.tech_categories}
        for project in similar_projects:
            for cat in self.tech_categories:
                techs = project.get(cat, [])
                for tech in techs:
                    if not any(c.lower() in tech.lower() for c in constraint_list):
                        tech_counter[cat][tech.lower()] += 1
        primary_stack = []
        for cat, counter in tech_counter.items():
            if counter:
                tech, _ = counter.most_common(1)[0]
                primary_stack.append({
                    "name": tech,
                    "category": cat,
                    "version": None,
                    "description": None
                })
        if not primary_stack and similar_projects:
            fallback = similar_projects[0]
            for cat in self.tech_categories:
                techs = fallback.get(cat, [])
                if techs:
                    primary_stack.append({
                        "name": techs[0],
                        "category": cat,
                        "version": None,
                        "description": None
                    })
        alternatives = {}
        for cat, counter in tech_counter.items():
            if counter:
                alt_techs = [
                    {"name": tech, "category": cat, "version": None, "description": None}
                    for tech, _ in counter.most_common()[1:4]
                ]
                if alt_techs:
                    alternatives[cat] = alt_techs
        similar_names = ', '.join([p.get('name', 'Unknown') for p in similar_projects])
        explanation = (
            f"[Local] Based on your project description, I found similar projects: {similar_names}. "
            f"The recommended stack is based on the most common technologies used in these projects."
        )
        duration = (time.time() - start_time) * 1000
        recommendation = {
            'primary_tech_stack': primary_stack,
            'alternatives': alternatives,
            'explanation': explanation,
            'confidence_level': 0.9 if primary_stack else 0.5,
            'similar_projects': similar_projects
        }
        logger.info(
            "Generated local recommendation",
            extra={
                'project_description': project_description,
                'requirements': requirements,
                'constraints': constraints,
                'recommendation': recommendation,
                'processing_time_ms': duration
            }
        )
        return recommendation

    def _find_similar_projects(
        self,
        description: str,
        requirements: List[str],
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find projects similar to the given description and requirements.
        """
        try:
            similar_projects = []
            
            for project in data:
                # Calculate similarity scores
                desc_similarity = self.data_processor.calculate_similarity_score(
                    description,
                    project['description']
                )
                
                req_similarity = 0.0
                if requirements:
                    req_similarity = sum(
                        self.data_processor.calculate_similarity_score(req, project['description'])
                        for req in requirements
                    ) / len(requirements)
                
                # Combined similarity score (weighted)
                similarity = (desc_similarity * 0.7) + (req_similarity * 0.3)
                
                similar_projects.append({
                    **project,
                    'similarity_score': similarity
                })
            
            # Sort by similarity score
            similar_projects.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return similar_projects
            
        except Exception as e:
            logger.error(
                "Error finding similar projects",
                extra={
                    'description_length': len(description),
                    'requirements_count': len(requirements),
                    'data_count': len(data)
                }
            )
            return []

    def _generate_primary_stack(
        self,
        tech_frequency: Dict[str, int],
        constraints: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate primary tech stack based on technology frequency and constraints.
        """
        try:
            primary_stack = []
            constraints = [c.lower() for c in constraints]
            
            for category, techs in self.tech_categories.items():
                # Filter out constrained technologies
                available_techs = [
                    tech for tech in techs
                    if not any(c in tech.lower() for c in constraints)
                ]
                
                if available_techs:
                    # Find most frequent technology in category
                    category_techs = {
                        tech: tech_frequency.get(tech, 0)
                        for tech in available_techs
                    }
                    
                    if category_techs:
                        most_frequent = max(category_techs.items(), key=lambda x: x[1])[0]
                        primary_stack.append({
                            "name": most_frequent,
                            "category": category,
                            "version": None,
                            "description": None
                        })
            
            return primary_stack
            
        except Exception as e:
            logger.error(
                "Error generating primary stack",
                extra={
                    'tech_count': len(tech_frequency),
                    'constraints_count': len(constraints)
                }
            )
            return []

    def _generate_alternatives(
        self,
        tech_frequency: Dict[str, int],
        primary_stack: List[Dict[str, Any]],
        constraints: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate alternative technology options.
        """
        try:
            alternatives = {}
            constraints = [c.lower() for c in constraints]
            
            for category, techs in self.tech_categories.items():
                # Filter out primary stack and constrained technologies
                available_techs = [
                    tech for tech in techs
                    if tech not in [t["name"] for t in primary_stack]
                    and not any(c in tech.lower() for c in constraints)
                ]
                
                if available_techs:
                    # Sort by frequency
                    category_techs = {
                        tech: tech_frequency.get(tech, 0)
                        for tech in available_techs
                    }
                    
                    sorted_techs = sorted(
                        category_techs.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    
                    alternatives[category] = [
                        {
                            "name": tech,
                            "category": category,
                            "version": None,
                            "description": None
                        }
                        for tech, _ in sorted_techs[:3]  # Top 3 alternatives
                    ]
            
            return alternatives
            
        except Exception as e:
            logger.error(
                "Error generating alternatives",
                extra={
                    'tech_count': len(tech_frequency),
                    'primary_stack_count': len(primary_stack),
                    'constraints_count': len(constraints)
                }
            )
            return {}

    def _calculate_confidence(
        self,
        similar_projects: List[Dict[str, Any]],
        tech_frequency: Dict[str, int]
    ) -> float:
        """
        Calculate confidence level for the recommendation.
        """
        try:
            if not similar_projects or not tech_frequency:
                return 0.0
            
            # Factors affecting confidence:
            # 1. Number of similar projects
            # 2. Similarity scores
            # 3. Technology frequency distribution
            
            # Similar projects factor (0-0.4)
            project_factor = min(len(similar_projects) / 10, 1.0) * 0.4
            
            # Similarity scores factor (0-0.3)
            similarity_factor = (
                sum(p['similarity_score'] for p in similar_projects[:5]) / 5
            ) * 0.3
            
            # Technology frequency factor (0-0.3)
            total_freq = sum(tech_frequency.values())
            if total_freq > 0:
                max_freq = max(tech_frequency.values())
                freq_factor = (max_freq / total_freq) * 0.3
            else:
                freq_factor = 0.0
            
            return min(project_factor + similarity_factor + freq_factor, 1.0)
            
        except Exception as e:
            logger.error(
                "Error calculating confidence",
                extra={
                    'similar_projects_count': len(similar_projects),
                    'tech_count': len(tech_frequency)
                }
            )
            return 0.0

    def _generate_explanation(
        self,
        primary_stack: List[Dict[str, Any]],
        alternatives: Dict[str, List[Dict[str, Any]]],
        similar_projects: List[Dict[str, Any]],
        confidence: float
    ) -> str:
        """
        Generate explanation for the recommendations.
        """
        try:
            explanation_parts = []
            
            # Primary stack explanation
            if primary_stack:
                explanation_parts.append(
                    f"Based on your project requirements, we recommend using "
                    f"{', '.join([t['name'] for t in primary_stack])} as your primary technology stack."
                )
            
            # Alternatives explanation
            if alternatives:
                explanation_parts.append(
                    f"Alternative technologies to consider include "
                    f"{', '.join([', '.join([t['name'] for t in techs]) for techs in alternatives.values()])}."
                )
            
            # Similar projects explanation
            if similar_projects:
                project_names = [p['name'] for p in similar_projects[:3]]
                explanation_parts.append(
                    f"These recommendations are based on similar projects: "
                    f"{', '.join(project_names)}."
                )
            
            # Confidence explanation
            confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
            explanation_parts.append(
                f"We have {confidence_level} confidence in these recommendations "
                f"(confidence score: {confidence:.2f})."
            )
            
            return " ".join(explanation_parts)
            
        except Exception as e:
            logger.error(
                "Error generating explanation",
                extra={
                    'primary_stack': primary_stack,
                    'alternatives': alternatives,
                    'similar_projects_count': len(similar_projects),
                    'confidence': confidence
                }
            )
            return "Unable to generate detailed explanation." 