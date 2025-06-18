# Data Collection System

This module handles the collection, validation, and analysis of tech stack data from various sources.

## Components

1. **Base Collector (`base_collector.py`)**
   - Defines the interface for all data collectors
   - Provides common data validation and enrichment methods
   - Handles data normalization and standardization

2. **GitHub Collector (`github_collector.py`)**
   - Collects data from GitHub repositories using REST API v3
   - Implements rate limiting and pagination
   - Collects repository metadata and tech stack information

3. **Stack Overflow Collector (`stackoverflow_collector.py`)**
   - Collects data from Stack Overflow using Stack Exchange API 2.3
   - Extracts technology mentions from questions and answers
   - Implements quota management and error handling

4. **Data Validator (`data_validator.py`)**
   - Validates and normalizes collected data
   - Ensures data quality and consistency
   - Handles duplicate detection and removal

5. **Quality Report Generator (`quality_report.py`)**
   - Analyzes collected data
   - Generates visualizations and reports
   - Provides data quality metrics

6. **Data Collection Runner (`run_collection.py`)**
   - Orchestrates the data collection process
   - Merges data from multiple sources
   - Handles error recovery and logging

7. **Data Collection Scheduler (`scheduler.py`)**
   - Automates periodic data collection
   - Configurable collection intervals
   - Robust error handling and logging

## Usage

### Manual Data Collection

To run a single data collection:

```bash
python -m backend.app.data.collection.run_collection
```

### Automated Data Collection

To start the automated data collection scheduler:

```bash
python -m backend.app.data.collection.scheduler
```

The scheduler can be configured using environment variables:
- `DATA_COLLECTION_INTERVAL_HOURS`: Hours between collection runs (default: 24)

### Output Files

The system generates several output files:

1. **Raw Collection Files**
   - `tech_stacks_github_*.json`: GitHub data
   - `tech_stacks_stackoverflow_*.json`: Stack Overflow data

2. **Merged Files**
   - `merged_tech_stacks_*.json`: Combined data from all sources

3. **Validated Files**
   - `validated_tech_stacks_*.json`: Cleaned and normalized data

4. **Quality Reports**
   - `reports/summary_report.md`: Human-readable summary
   - `reports/basic_stats.json`: Basic statistics
   - `reports/technology_analysis.json`: Technology usage analysis
   - `reports/domain_analysis.json`: Domain distribution analysis
   - `reports/source_analysis.json`: Source-specific metrics
   - Various visualization files (PNG)

### Data Quality Metrics

The system tracks several quality metrics:

1. **Data Volume**
   - Total number of entries
   - Unique technologies
   - Average technologies per stack

2. **Data Quality**
   - Missing descriptions
   - Description length
   - Technology coverage

3. **Data Freshness**
   - Collection timestamps
   - Source-specific metrics

## Future Improvements

1. **Additional Data Sources**
   - StackShare API integration
   - Product Hunt API integration
   - More GitHub data points

2. **Enhanced Analysis**
   - Technology trend analysis
   - Domain-specific insights
   - Cross-source correlation

3. **Improved Automation**
   - Dynamic scheduling based on data freshness
   - Automated error recovery
   - Performance optimization

## Notes

- The system is designed to be extensible for additional data sources
- All components include comprehensive error handling
- Data validation ensures consistency across sources
- Quality reports help monitor data health
- The scheduler ensures data stays up-to-date automatically 