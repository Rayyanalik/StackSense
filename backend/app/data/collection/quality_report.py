import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityReportGenerator:
    """Generates quality reports and visualizations for tech stack data."""
    
    def __init__(self, output_dir: str = "reports"):
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn')
        sns.set_palette("husl")
    
    def generate_basic_stats(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate basic statistics about the dataset."""
        stats = {
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
            'collection_date': datetime.now().isoformat()
        }
        
        # Save stats
        self._save_json(stats, 'basic_stats.json')
        return stats
    
    def analyze_technologies(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze technology usage patterns."""
        # Count technology frequency
        tech_counter = Counter()
        for entry in data:
            tech_counter.update(entry['technologies'])
        
        # Get top technologies
        top_techs = dict(tech_counter.most_common(20))
        
        # Calculate technology co-occurrence
        co_occurrence = {}
        for entry in data:
            techs = entry['technologies']
            for i, tech1 in enumerate(techs):
                for tech2 in techs[i+1:]:
                    pair = tuple(sorted([tech1, tech2]))
                    co_occurrence[pair] = co_occurrence.get(pair, 0) + 1
        
        analysis = {
            'top_technologies': top_techs,
            'technology_count': len(tech_counter),
            'co_occurrence': dict(sorted(
                co_occurrence.items(),
                key=lambda x: x[1],
                reverse=True
            )[:50])
        }
        
        # Save analysis
        self._save_json(analysis, 'technology_analysis.json')
        
        # Generate visualization
        self._plot_technology_distribution(top_techs)
        return analysis
    
    def analyze_domains(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze domain distribution and patterns."""
        # Count domain frequency
        domain_counter = Counter(entry['domain'] for entry in data)
        
        # Analyze technology distribution by domain
        domain_techs = {}
        for entry in data:
            domain = entry['domain']
            if domain not in domain_techs:
                domain_techs[domain] = Counter()
            domain_techs[domain].update(entry['technologies'])
        
        # Get top technologies for each domain
        domain_top_techs = {
            domain: dict(counter.most_common(10))
            for domain, counter in domain_techs.items()
        }
        
        analysis = {
            'domain_distribution': dict(domain_counter),
            'technologies_by_domain': domain_top_techs
        }
        
        # Save analysis
        self._save_json(analysis, 'domain_analysis.json')
        
        # Generate visualization
        self._plot_domain_distribution(domain_counter)
        return analysis
    
    def analyze_sources(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze data source distribution and quality."""
        # Count source frequency
        source_counter = Counter(entry['source'] for entry in data)
        
        # Analyze quality metrics by source
        source_metrics = {}
        for source in source_counter.keys():
            source_data = [entry for entry in data if entry['source'] == source]
            source_metrics[source] = {
                'avg_technologies': sum(
                    len(entry['technologies']) for entry in source_data
                ) / len(source_data),
                'avg_description_length': sum(
                    len(entry['description']) for entry in source_data
                ) / len(source_data),
                'missing_descriptions': sum(
                    1 for entry in source_data if not entry['description'].strip()
                )
            }
        
        analysis = {
            'source_distribution': dict(source_counter),
            'source_metrics': source_metrics
        }
        
        # Save analysis
        self._save_json(analysis, 'source_analysis.json')
        
        # Generate visualization
        self._plot_source_distribution(source_counter)
        return analysis
    
    def generate_summary_report(self, data: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive summary report."""
        # Generate all analyses
        basic_stats = self.generate_basic_stats(data)
        tech_analysis = self.analyze_technologies(data)
        domain_analysis = self.analyze_domains(data)
        source_analysis = self.analyze_sources(data)
        
        # Create report content
        report = [
            "# Tech Stack Data Quality Report",
            f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Basic Statistics",
            f"- Total Entries: {basic_stats['total_entries']}",
            f"- Unique Technologies: {basic_stats['unique_technologies']}",
            f"- Average Technologies per Stack: {basic_stats['avg_technologies_per_stack']:.2f}",
            f"- Missing Descriptions: {basic_stats['missing_descriptions']}",
            f"- Average Description Length: {basic_stats['avg_description_length']:.2f}",
            
            "\n## Top Technologies",
            *[f"- {tech}: {count}" for tech, count in tech_analysis['top_technologies'].items()],
            
            "\n## Domain Distribution",
            *[f"- {domain}: {count}" for domain, count in domain_analysis['domain_distribution'].items()],
            
            "\n## Source Distribution",
            *[f"- {source}: {count}" for source, count in source_analysis['source_distribution'].items()],
            
            "\n## Quality Metrics by Source",
        ]
        
        for source, metrics in source_analysis['source_metrics'].items():
            report.extend([
                f"\n### {source}",
                f"- Average Technologies: {metrics['avg_technologies']:.2f}",
                f"- Average Description Length: {metrics['avg_description_length']:.2f}",
                f"- Missing Descriptions: {metrics['missing_descriptions']}"
            ])
        
        # Save report
        report_path = os.path.join(self.output_dir, 'summary_report.md')
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))
        
        return report_path
    
    def _save_json(self, data: Dict[str, Any], filename: str) -> str:
        """Save data to a JSON file."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return filepath
    
    def _plot_technology_distribution(self, tech_counts: Dict[str, int]):
        """Plot technology distribution."""
        plt.figure(figsize=(12, 6))
        plt.bar(tech_counts.keys(), tech_counts.values())
        plt.xticks(rotation=45, ha='right')
        plt.title('Top Technologies Distribution')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'technology_distribution.png'))
        plt.close()
    
    def _plot_domain_distribution(self, domain_counts: Counter):
        """Plot domain distribution."""
        plt.figure(figsize=(10, 6))
        plt.pie(domain_counts.values(), labels=domain_counts.keys(), autopct='%1.1f%%')
        plt.title('Domain Distribution')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'domain_distribution.png'))
        plt.close()
    
    def _plot_source_distribution(self, source_counts: Counter):
        """Plot source distribution."""
        plt.figure(figsize=(8, 6))
        plt.bar(source_counts.keys(), source_counts.values())
        plt.title('Source Distribution')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'source_distribution.png'))
        plt.close()

def main():
    try:
        # Get the most recent validated file
        data_dir = Path(__file__).parent.parent
        validated_files = list(data_dir.glob('tech_stacks_validated_*.json'))
        
        if not validated_files:
            logger.error("No validated data files found")
            return
        
        latest_file = max(validated_files, key=lambda x: x.stat().st_mtime)
        
        # Generate report
        generator = QualityReportGenerator()
        report_path = generator.generate_summary_report(latest_file)
        
        logger.info(f"Quality report generated in {report_path}")
        
    except Exception as e:
        logger.error(f"Error generating quality report: {str(e)}")
        raise

if __name__ == "__main__":
    main() 