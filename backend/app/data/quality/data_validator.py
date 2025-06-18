import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ValidationRule:
    """Represents a validation rule for tech stack data."""
    field: str
    rule_type: str  # 'required', 'type', 'format', 'range', 'enum'
    parameters: Dict[str, Any]
    description: str
    severity: str  # 'error', 'warning'

class DataValidator:
    """Handles data validation and quality metrics for tech stack data."""
    
    def __init__(self, rules_file: str = "validation_rules.json"):
        """
        Initialize the data validator.
        
        Args:
            rules_file: Path to the validation rules file
        """
        self.rules_file = rules_file
        self.rules = self._load_rules()
        self.quality_metrics = defaultdict(float)
        self.validation_results = []
        
    def _load_rules(self) -> List[ValidationRule]:
        """Load validation rules from file."""
        default_rules = [
            ValidationRule(
                field="name",
                rule_type="required",
                parameters={},
                description="Name is required",
                severity="error"
            ),
            ValidationRule(
                field="technologies",
                rule_type="type",
                parameters={"type": "list"},
                description="Technologies must be a list",
                severity="error"
            ),
            ValidationRule(
                field="metadata",
                rule_type="type",
                parameters={"type": "dict"},
                description="Metadata must be a dictionary",
                severity="error"
            ),
            ValidationRule(
                field="description",
                rule_type="format",
                parameters={"min_length": 10},
                description="Description must be at least 10 characters",
                severity="warning"
            )
        ]
        
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r') as f:
                    rules_data = json.load(f)
                    return [ValidationRule(**rule) for rule in rules_data]
            return default_rules
        except Exception as e:
            logger.error(f"Error loading validation rules: {str(e)}")
            return default_rules
    
    def validate_entry(self, entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate a single tech stack entry.
        
        Args:
            entry: Tech stack entry to validate
            
        Returns:
            List of validation results
        """
        results = []
        
        for rule in self.rules:
            result = {
                'field': rule.field,
                'rule_type': rule.rule_type,
                'description': rule.description,
                'severity': rule.severity,
                'passed': True,
                'message': ''
            }
            
            try:
                if rule.rule_type == 'required':
                    if rule.field not in entry or not entry[rule.field]:
                        result['passed'] = False
                        result['message'] = f"Required field '{rule.field}' is missing or empty"
                
                elif rule.rule_type == 'type':
                    expected_type = rule.parameters['type']
                    if not isinstance(entry.get(rule.field), eval(expected_type)):
                        result['passed'] = False
                        result['message'] = f"Field '{rule.field}' must be of type {expected_type}"
                
                elif rule.rule_type == 'format':
                    if 'min_length' in rule.parameters:
                        if len(str(entry.get(rule.field, ''))) < rule.parameters['min_length']:
                            result['passed'] = False
                            result['message'] = f"Field '{rule.field}' is too short"
                
                elif rule.rule_type == 'range':
                    value = entry.get(rule.field)
                    if value is not None:
                        if 'min' in rule.parameters and value < rule.parameters['min']:
                            result['passed'] = False
                            result['message'] = f"Field '{rule.field}' is below minimum value"
                        if 'max' in rule.parameters and value > rule.parameters['max']:
                            result['passed'] = False
                            result['message'] = f"Field '{rule.field}' exceeds maximum value"
                
                elif rule.rule_type == 'enum':
                    if entry.get(rule.field) not in rule.parameters['values']:
                        result['passed'] = False
                        result['message'] = f"Field '{rule.field}' has invalid value"
            
            except Exception as e:
                result['passed'] = False
                result['message'] = f"Validation error: {str(e)}"
            
            results.append(result)
        
        return results
    
    def validate_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a list of tech stack entries.
        
        Args:
            data: List of tech stack entries to validate
            
        Returns:
            Dictionary containing validation results and quality metrics
        """
        validation_results = []
        error_count = 0
        warning_count = 0
        
        for entry in data:
            entry_results = self.validate_entry(entry)
            validation_results.extend(entry_results)
            
            for result in entry_results:
                if not result['passed']:
                    if result['severity'] == 'error':
                        error_count += 1
                    else:
                        warning_count += 1
        
        # Calculate quality metrics
        total_entries = len(data)
        total_validations = len(validation_results)
        
        self.quality_metrics.update({
            'total_entries': total_entries,
            'error_rate': error_count / total_validations if total_validations > 0 else 0,
            'warning_rate': warning_count / total_validations if total_validations > 0 else 0,
            'completeness': sum(1 for r in validation_results if r['passed']) / total_validations if total_validations > 0 else 0
        })
        
        return {
            'validation_results': validation_results,
            'quality_metrics': dict(self.quality_metrics),
            'summary': {
                'total_entries': total_entries,
                'error_count': error_count,
                'warning_count': warning_count,
                'validation_timestamp': datetime.now().isoformat()
            }
        }
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Generate a quality report for the validated data."""
        return {
            'metrics': dict(self.quality_metrics),
            'timestamp': datetime.now().isoformat(),
            'validation_rules': len(self.rules)
        }
    
    def save_validation_results(self, results: Dict[str, Any], output_file: str):
        """Save validation results to a file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Validation results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving validation results: {str(e)}")

def main():
    """Test the data validator."""
    validator = DataValidator()
    
    # Test data
    test_data = [
        {
            'name': 'Test Project',
            'description': 'A test project',
            'technologies': ['Python', 'Flask'],
            'metadata': {'stars': 100}
        },
        {
            'name': '',
            'description': 'Too short',
            'technologies': 'not a list',
            'metadata': None
        }
    ]
    
    # Validate data
    results = validator.validate_data(test_data)
    
    # Print results
    print("Validation Results:")
    print(json.dumps(results, indent=2))
    
    # Print quality report
    print("\nQuality Report:")
    print(json.dumps(validator.get_quality_report(), indent=2))

if __name__ == "__main__":
    main() 