import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeedbackHandler:
    """Handles user feedback for data correction and enrichment."""
    
    def __init__(self, feedback_dir: str = "feedback"):
        """
        Initialize the feedback handler.
        
        Args:
            feedback_dir: Directory to store feedback data
        """
        self.feedback_dir = feedback_dir
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Initialize feedback storage
        self.tech_corrections = defaultdict(list)
        self.domain_corrections = defaultdict(list)
        self.description_corrections = defaultdict(list)
        
        # Load existing feedback
        self._load_feedback()
    
    def _load_feedback(self):
        """Load existing feedback from files."""
        try:
            # Load technology corrections
            tech_file = os.path.join(self.feedback_dir, "tech_corrections.json")
            if os.path.exists(tech_file):
                with open(tech_file, 'r') as f:
                    self.tech_corrections = defaultdict(list, json.load(f))
            
            # Load domain corrections
            domain_file = os.path.join(self.feedback_dir, "domain_corrections.json")
            if os.path.exists(domain_file):
                with open(domain_file, 'r') as f:
                    self.domain_corrections = defaultdict(list, json.load(f))
            
            # Load description corrections
            desc_file = os.path.join(self.feedback_dir, "description_corrections.json")
            if os.path.exists(desc_file):
                with open(desc_file, 'r') as f:
                    self.description_corrections = defaultdict(list, json.load(f))
                    
        except Exception as e:
            logger.error(f"Error loading feedback: {str(e)}")
    
    def _save_feedback(self):
        """Save feedback to files."""
        try:
            # Save technology corrections
            tech_file = os.path.join(self.feedback_dir, "tech_corrections.json")
            with open(tech_file, 'w') as f:
                json.dump(dict(self.tech_corrections), f, indent=2)
            
            # Save domain corrections
            domain_file = os.path.join(self.feedback_dir, "domain_corrections.json")
            with open(domain_file, 'w') as f:
                json.dump(dict(self.domain_corrections), f, indent=2)
            
            # Save description corrections
            desc_file = os.path.join(self.feedback_dir, "description_corrections.json")
            with open(desc_file, 'w') as f:
                json.dump(dict(self.description_corrections), f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
    
    def add_tech_correction(self, original: str, correction: str, user_id: str):
        """
        Add a technology name correction.
        
        Args:
            original: Original technology name
            correction: Corrected technology name
            user_id: ID of the user providing feedback
        """
        feedback = {
            'correction': correction,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        self.tech_corrections[original].append(feedback)
        self._save_feedback()
        logger.info(f"Added technology correction: {original} -> {correction}")
    
    def add_domain_correction(self, entry_id: str, correction: str, user_id: str):
        """
        Add a domain correction.
        
        Args:
            entry_id: ID of the tech stack entry
            correction: Corrected domain
            user_id: ID of the user providing feedback
        """
        feedback = {
            'correction': correction,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        self.domain_corrections[entry_id].append(feedback)
        self._save_feedback()
        logger.info(f"Added domain correction for entry {entry_id}")
    
    def add_description_correction(self, entry_id: str, correction: str, user_id: str):
        """
        Add a description correction.
        
        Args:
            entry_id: ID of the tech stack entry
            correction: Corrected description
            user_id: ID of the user providing feedback
        """
        feedback = {
            'correction': correction,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        self.description_corrections[entry_id].append(feedback)
        self._save_feedback()
        logger.info(f"Added description correction for entry {entry_id}")
    
    def get_tech_corrections(self, original: str) -> List[Dict[str, Any]]:
        """Get corrections for a technology name."""
        return self.tech_corrections.get(original, [])
    
    def get_domain_corrections(self, entry_id: str) -> List[Dict[str, Any]]:
        """Get corrections for a domain."""
        return self.domain_corrections.get(entry_id, [])
    
    def get_description_corrections(self, entry_id: str) -> List[Dict[str, Any]]:
        """Get corrections for a description."""
        return self.description_corrections.get(entry_id, [])
    
    def get_most_common_corrections(self, min_votes: int = 2) -> Dict[str, Dict[str, Any]]:
        """
        Get the most common corrections that have received multiple votes.
        
        Args:
            min_votes: Minimum number of votes required for a correction
            
        Returns:
            Dictionary of corrections with their vote counts
        """
        corrections = {
            'technologies': {},
            'domains': {},
            'descriptions': {}
        }
        
        # Process technology corrections
        for original, feedbacks in self.tech_corrections.items():
            if len(feedbacks) >= min_votes:
                corrections['technologies'][original] = {
                    'correction': max(
                        set(f['correction'] for f in feedbacks),
                        key=lambda x: sum(1 for f in feedbacks if f['correction'] == x)
                    ),
                    'votes': len(feedbacks)
                }
        
        # Process domain corrections
        for entry_id, feedbacks in self.domain_corrections.items():
            if len(feedbacks) >= min_votes:
                corrections['domains'][entry_id] = {
                    'correction': max(
                        set(f['correction'] for f in feedbacks),
                        key=lambda x: sum(1 for f in feedbacks if f['correction'] == x)
                    ),
                    'votes': len(feedbacks)
                }
        
        # Process description corrections
        for entry_id, feedbacks in self.description_corrections.items():
            if len(feedbacks) >= min_votes:
                corrections['descriptions'][entry_id] = {
                    'correction': max(
                        set(f['correction'] for f in feedbacks),
                        key=lambda x: sum(1 for f in feedbacks if f['correction'] == x)
                    ),
                    'votes': len(feedbacks)
                }
        
        return corrections
    
    def apply_corrections(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply approved corrections to the data.
        
        Args:
            data: List of tech stack entries
            
        Returns:
            Updated data with corrections applied
        """
        corrections = self.get_most_common_corrections()
        
        for entry in data:
            # Apply technology corrections
            if 'technologies' in entry:
                entry['technologies'] = [
                    corrections['technologies'].get(tech, {}).get('correction', tech)
                    for tech in entry['technologies']
                ]
            
            # Apply domain corrections
            entry_id = entry.get('id')
            if entry_id and entry_id in corrections['domains']:
                entry['domain'] = corrections['domains'][entry_id]['correction']
            
            # Apply description corrections
            if entry_id and entry_id in corrections['descriptions']:
                entry['description'] = corrections['descriptions'][entry_id]['correction']
        
        return data

def main():
    """Test the feedback handler."""
    handler = FeedbackHandler()
    
    # Add some test corrections
    handler.add_tech_correction("reactjs", "React", "user1")
    handler.add_tech_correction("reactjs", "React", "user2")
    handler.add_domain_correction("entry1", "Web Development", "user1")
    handler.add_description_correction("entry1", "Updated description", "user1")
    
    # Get and print corrections
    corrections = handler.get_most_common_corrections()
    print("Corrections:", json.dumps(corrections, indent=2))

if __name__ == "__main__":
    main() 