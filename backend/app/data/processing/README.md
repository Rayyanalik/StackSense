# Data Processing Module

This module handles the cleaning, validation, and enrichment of tech stack data.

## Components

1. **Data Processor (`data_processor.py`)**
   - Main class for processing and enriching data
   - Handles data cleaning, validation, and enrichment
   - Uses spaCy for NLP tasks and LDA for topic modeling

2. **Technology Mapping (`tech_mapping.json`)**
   - Maps technology names to their standardized forms
   - Handles common variations and aliases
   - Used for normalizing technology names

3. **Feedback Handler (`feedback_handler.py`)**
   - Manages user feedback for data corrections
   - Handles technology name corrections
   - Handles domain and description corrections
   - Implements voting system for corrections

4. **Processing Script (`run_processing.py`)**
   - Script to run the data processing pipeline
   - Handles file I/O and logging

## Features

### Data Cleaning
- Removes duplicates
- Standardizes text formats
- Handles missing values
- Normalizes technology names

### Data Validation
- Checks required fields
- Validates data types
- Ensures data consistency
- Validates technology names

### Data Enrichment
- Uses spaCy for NLP tasks
- Implements LDA for topic modeling
- Adds metadata and statistics
- Enriches domain information

### User Feedback System
- Collects user corrections
- Implements voting mechanism
- Applies approved corrections
- Maintains correction history

## Usage

1. **Manual Processing**
   ```bash
   python -m backend.app.data.processing.run_processing
   ```

2. **Using the Processor**
   ```python
   from backend.app.data.processing.data_processor import DataProcessor
   
   processor = DataProcessor()
   result = processor.process_data(data)
   ```

3. **Using the Feedback Handler**
   ```python
   from backend.app.data.processing.feedback_handler import FeedbackHandler
   
   handler = FeedbackHandler()
   handler.add_tech_correction("reactjs", "React", "user1")
   ```

## Dependencies

- pandas: Data manipulation
- numpy: Numerical operations
- spacy: NLP tasks
- scikit-learn: Topic modeling
- json: File I/O
- logging: Logging

## Output Files

1. **Processed Data**
   - `processed_tech_stacks_YYYYMMDD_HHMMSS.json`
   - Contains cleaned and enriched data
   - Includes processing statistics

2. **Feedback Data**
   - `tech_corrections.json`: Technology name corrections
   - `domain_corrections.json`: Domain corrections
   - `description_corrections.json`: Description corrections

## Notes

- The processor uses spaCy for NLP tasks
- Topic modeling helps in domain categorization
- The feedback system requires multiple votes for corrections
- All corrections are timestamped and user-tracked 