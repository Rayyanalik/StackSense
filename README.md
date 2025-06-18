# StackSense - AI-Powered Tech Stack Recommender

An intelligent system that recommends optimal technology stacks for new projects based on project requirements and similar successful implementations.

## Features

- AI-powered tech stack recommendations
- Similar project analysis
- Detailed explanations for recommendations
- Modern, responsive UI
- Real-time processing

## Tech Stack

### Backend
- FastAPI
- Sentence Transformers
- FAISS
- OpenAI GPT-3.5
- Python 3.9+

### Frontend
- React with TypeScript
- Material-UI
- Axios
- React Query

## Project Structure

```
tech-stack-recommender/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   └── services/       # Business logic
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
│
└── frontend/               # React frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── pages/         # Page components
    │   ├── services/      # API services
    │   └── utils/         # Utility functions
    ├── public/            # Static files
    └── package.json       # Node dependencies
```

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the backend directory with:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the development server:
```bash
uvicorn app.main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm start
```

## Development Guidelines

1. Use Git for version control
2. Write clear documentation
3. Implement proper error handling
4. Add logging for debugging
5. Follow PEP 8 style guide for Python
6. Follow ESLint rules for TypeScript/JavaScript
7. Write unit tests for critical functionality
8. Use type hints and TypeScript for better code maintainability
9. Implement API key security best practices
10. Add proper error handling for API rate limits

## License

MIT License 