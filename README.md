# 🚀 StackSense - AI-Powered Tech Stack Recommendation Engine

<div align="center">

![StackSense Logo](https://img.shields.io/badge/StackSense-AI%20Powered%20Tech%20Stack%20Recommendation-blue?style=for-the-badge&logo=react)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18+-blue?style=for-the-badge&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=for-the-badge&logo=fastapi)
![Machine Learning](https://img.shields.io/badge/ML-Sentence%20Transformers%20%7C%20LLM-orange?style=for-the-badge&logo=tensorflow)

**Intelligent tech stack recommendations powered by AI and machine learning**

[🌐 Live Demo](https://stacksense-frontend.vercel.app) • [🔗 Backend API](https://stacksense-backend.onrender.com) • [📚 Documentation](#documentation)

[![Deployment Status](https://img.shields.io/badge/Status-Live%20%26%20Running-brightgreen?style=for-the-badge)](https://stacksense-frontend.vercel.app)
[![Last Commit](https://img.shields.io/github/last-commit/Rayyanalik/StackSense?style=for-the-badge)](https://github.com/Rayyanalik/StackSense)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🤖 AI/ML Components](#-aiml-components)
- [🛠️ Tech Stack](#️-tech-stack)
- [📊 Database Schema](#-database-schema)
- [🚀 Getting Started](#-getting-started)
- [📸 Screenshots](#-screenshots)
- [🔧 API Documentation](#-api-documentation)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🎯 Overview

StackSense is an intelligent web application that provides personalized technology stack recommendations for software projects. By leveraging advanced machine learning algorithms and large language models, it analyzes project requirements and suggests optimal tech combinations based on industry best practices and similar successful projects.

### Key Capabilities

- **AI-Powered Recommendations**: Uses Perplexity and Cohere LLMs for intelligent tech stack suggestions
- **Semantic Similarity**: Implements sentence transformers for finding similar projects
- **Real-time GitHub Integration**: Fetches live data from GitHub repositories
- **Multi-Modal Analysis**: Combines LLM insights with statistical analysis
- **Responsive UI**: Modern, intuitive interface built with React and Tailwind CSS

### 🎯 What Makes StackSense Special?

- **Intelligent Analysis**: Combines multiple AI models for comprehensive recommendations
- **Real-time Data**: Live integration with GitHub for current project trends
- **Performance Optimized**: Pre-computed embeddings for lightning-fast responses
- **Production Ready**: Fully deployed and tested in production environment
- **Scalable Architecture**: Built for growth and easy maintenance

---

## ✨ Features

### 🎯 Core Features
- **Smart Tech Stack Recommendations**: AI-generated suggestions based on project descriptions
- **Detailed Justifications**: Comprehensive explanations for each recommendation
- **Similar Project Discovery**: Find relevant open-source projects on GitHub
- **Alternative Options**: Multiple tech stack alternatives for different scenarios
- **Confidence Scoring**: AI confidence levels for each recommendation

### 🔍 Advanced Features
- **Semantic Search**: Find similar projects using embedding-based similarity
- **Real-time API Integration**: Live data from GitHub and external APIs
- **Fallback Mechanisms**: Robust error handling with local dataset fallbacks
- **Performance Optimization**: Pre-computed embeddings for fast startup
- **Scalable Architecture**: Microservices design for easy scaling

### 🚀 Performance Features
- **Fast Startup**: Pre-downloaded ML models and embeddings
- **Caching**: Intelligent caching for repeated queries
- **Error Recovery**: Graceful fallbacks when external APIs fail
- **Responsive Design**: Works seamlessly on all devices

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   APIs          │
│                 │    │                 │    │                 │
│ • User Interface│    │ • ML Engine     │    │ • GitHub API    │
│ • State Mgmt    │    │ • API Gateway   │    │ • Perplexity    │
│ • Responsive UI │    │ • Data Processing│   │ • Cohere        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Data Layer    │
                       │                 │
                       │ • Local Dataset │
                       │ • Embeddings    │
                       │ • Cache         │
                       └─────────────────┘
```

### Component Architecture

#### Frontend (React + TypeScript)
- **Component Structure**: Modular, reusable components
- **State Management**: React hooks and context API
- **Styling**: Tailwind CSS with custom design system
- **API Integration**: Axios for HTTP requests
- **Error Handling**: Comprehensive error boundaries

#### Backend (FastAPI + Python)
- **API Gateway**: RESTful endpoints with automatic documentation
- **ML Engine**: Recommendation engine with multiple AI models
- **Data Processing**: Efficient data transformation and caching
- **Authentication**: JWT-based security (future enhancement)
- **Monitoring**: Comprehensive logging and error tracking

### Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Render        │
│   (Frontend)    │◄──►│   (Backend)     │
│                 │    │                 │
│ • React SPA     │    │ • FastAPI       │
│ • CDN           │    │ • Python 3.10   │
│ • Auto Deploy   │    │ • ML Models     │
└─────────────────┘    └─────────────────┘
```

---

## 🤖 AI/ML Components

### 1. Sentence Transformers
- **Model**: `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **Purpose**: Semantic similarity for project matching
- **Implementation**: Pre-computed embeddings for performance
- **Features**: 
  - 90MB model with 20+ project descriptions
  - Cosine similarity for matching
  - Real-time embedding generation for new queries
  - Pre-downloaded during build for fast startup

### 2. Large Language Models (LLMs)

#### Perplexity AI Integration
- **Model**: `llama-3-sonar-large-32k-online`
- **Capabilities**: 
  - JSON-structured responses
  - Context-aware recommendations
  - Detailed explanations
  - 32k context window for comprehensive analysis
- **Fallback**: Automatic fallback to Cohere on failure

#### Cohere Integration
- **Model**: `command-r-plus`
- **Features**:
  - Structured tech stack generation
  - Confidence scoring
  - Alternative suggestions
  - Robust error handling

### 3. Recommendation Algorithm

```python
# Multi-stage recommendation pipeline
1. GitHub Project Search → Find similar open-source projects
2. LLM Analysis → Generate primary recommendations
3. Local Dataset Fallback → Statistical analysis if APIs fail
4. Similarity Matching → Find relevant projects using embeddings
5. Confidence Scoring → Rate recommendation quality
6. Response Assembly → Combine all insights into final recommendation
```

### 4. Data Processing Pipeline

- **Text Preprocessing**: Normalization and cleaning
- **Feature Extraction**: Tech stack categorization
- **Embedding Generation**: Vector representations
- **Similarity Computation**: Cosine similarity matching
- **Ranking Algorithm**: Multi-factor scoring system
- **Response Formatting**: Structured JSON output

### 5. Performance Optimizations

- **Model Pre-loading**: ML models downloaded during build
- **Embedding Caching**: Pre-computed project embeddings
- **API Timeouts**: Intelligent timeout handling
- **Error Recovery**: Graceful degradation on failures
- **Memory Management**: Efficient resource utilization

---

## 🛠️ Tech Stack

### Frontend Technologies
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2.0 | UI Framework |
| **TypeScript** | 5.0+ | Type Safety |
| **Tailwind CSS** | 3.3+ | Styling |
| **Axios** | 1.4+ | HTTP Client |
| **React Router** | 6.8+ | Navigation |
| **Vite** | 4.3+ | Build Tool |

### Backend Technologies
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.104.1 | Web Framework |
| **Python** | 3.10.12 | Runtime |
| **Uvicorn** | 0.24.0 | ASGI Server |
| **Pydantic** | 2.4.2 | Data Validation |
| **SQLAlchemy** | 2.0.23 | ORM |
| **Redis** | 5.0.1 | Caching |

### Machine Learning Stack
| Technology | Version | Purpose |
|------------|---------|---------|
| **Sentence Transformers** | 2.2.2 | Text Embeddings |
| **Transformers** | 4.40.2 | Hugging Face Models |
| **NumPy** | 1.26.4 | Numerical Computing |
| **Scikit-learn** | 1.4.0 | ML Utilities |
| **Pandas** | 2.2.0 | Data Manipulation |
| **Torch** | 2.7.1 | Deep Learning |

### External APIs
- **GitHub API**: Project search and metadata
- **Perplexity AI**: Primary LLM recommendations
- **Cohere**: Secondary LLM recommendations

### DevOps & Deployment
- **Frontend**: Vercel (React SPA)
- **Backend**: Render (Python FastAPI)
- **Version Control**: Git & GitHub
- **CI/CD**: Automatic deployments
- **Monitoring**: Built-in logging and error tracking

---

## 📊 Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    PROJECTS {
        int id PK
        string name
        string description
        string frontend
        string backend
        string database
        string devops
        string use_cases
        datetime created_at
        datetime updated_at
    }
    
    RECOMMENDATIONS {
        int id PK
        int project_id FK
        string primary_tech_stack
        string alternatives
        string explanation
        float confidence_level
        datetime created_at
    }
    
    SIMILAR_PROJECTS {
        int id PK
        int project_id FK
        string github_url
        string name
        string description
        float similarity_score
        datetime created_at
    }
    
    PROJECTS ||--o{ RECOMMENDATIONS : "generates"
    PROJECTS ||--o{ SIMILAR_PROJECTS : "finds"
```

### Data Models

#### Project Data Structure
```json
{
  "name": "Modern Web App",
  "description": "A real-time chat application for remote teams.",
  "frontend": ["React", "TypeScript", "Tailwind CSS"],
  "backend": ["Node.js", "Express"],
  "database": ["MongoDB"],
  "devops": ["Docker", "AWS"],
  "use_cases": ["Web Applications", "Real-time Applications", "REST APIs"]
}
```

#### Recommendation Response
```json
{
  "primary_tech_stack": [
    {"category": "frontend", "name": "React"},
    {"category": "backend", "name": "Node.js with Express"},
    {"category": "database", "name": "PostgreSQL"}
  ],
  "detailed_explanation": "This stack is ideal for...",
  "confidence_level": 0.85,
  "similar_projects": [...]
}
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- Git

### Frontend Setup
```bash
# Clone the repository
git clone https://github.com/Rayyanalik/StackSense.git
cd StackSense

# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Start the server
uvicorn app.main:app --reload
```

### Environment Variables
```bash
# Required API Keys
PERPLEXITY_API_KEY=your_perplexity_key
COHERE_API_KEY=your_cohere_key
GITHUB_TOKEN=your_github_token

# Optional
DATABASE_URL=your_database_url
REDIS_URL=your_redis_url
```

### Deployment

#### Frontend (Vercel)
1. Connect GitHub repository to Vercel
2. Set build directory to `frontend`
3. Configure environment variables
4. Deploy automatically on push

#### Backend (Render)
1. Connect GitHub repository to Render
2. Set build command: `pip install -r requirements.txt && python download_model.py`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Configure environment variables
5. Deploy automatically on push

### Quick Start with Docker (Future Enhancement)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

---

## 📸 Screenshots

### Main Interface
![Main Interface](screenshots/main-interface.png)
*Clean, modern interface with project description input*

### Recommendation Results
![Recommendation Results](screenshots/recommendation-results.png)
*Three-card layout showing tech stack, justification, and similar projects*

### Responsive Design
![Mobile View](screenshots/mobile-view.png)
*Fully responsive design that works on all devices*

### API Documentation
![API Docs](screenshots/api-docs.png)
*Auto-generated FastAPI documentation*

---

## 🔧 API Documentation

### Base URL
```
Frontend: https://stacksense-frontend.vercel.app
Backend: https://stacksense-backend.onrender.com
```

### Endpoints

#### POST `/api/v1/tech-stack/recommend`
Generate tech stack recommendations

**Request Body:**
```json
{
  "project_description": "A real-time chat application for remote teams",
  "requirements": ["scalability", "real-time"],
  "constraints": {
    "budget": "low",
    "timeline": "3 months"
  }
}
```

**Response:**
```json
{
  "primary_tech_stack": [...],
  "detailed_explanation": "...",
  "confidence_level": 0.85,
  "similar_projects": [...]
}
```

#### GET `/api/v1/tech-stack/similar`
Find similar projects

**Query Parameters:**
- `description`: Project description
- `limit`: Number of results (default: 5)

### Error Handling
- **400**: Invalid request data
- **500**: Internal server error
- **503**: External API unavailable

### API Documentation
Visit the interactive API documentation at: https://stacksense-backend.onrender.com/docs

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- **Frontend**: ESLint + Prettier
- **Backend**: Black + isort
- **TypeScript**: Strict mode enabled
- **Python**: Type hints required

### Testing
```bash
# Frontend tests
cd frontend && npm test

# Backend tests
cd backend && python -m pytest
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Hugging Face** for sentence transformers and the ML ecosystem
- **Perplexity AI** and **Cohere** for powerful LLM capabilities
- **GitHub** for providing rich project data and APIs
- **Vercel** and **Render** for reliable hosting and deployment
- **Open Source Community** for inspiration, tools, and best practices
- **FastAPI** team for the excellent web framework
- **React** team for the amazing frontend library

---

## 📈 Project Statistics

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/Rayyanalik/StackSense?style=for-the-badge&logo=github)
![GitHub forks](https://img.shields.io/github/forks/Rayyanalik/StackSense?style=for-the-badge&logo=github)
![GitHub issues](https://img.shields.io/github/issues/Rayyanalik/StackSense?style=for-the-badge&logo=github)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Rayyanalik/StackSense?style=for-the-badge&logo=github)

</div>

---

<div align="center">

**Made with ❤️ by [Rayyan Ali Khan](https://github.com/Rayyanalik)**

[![GitHub](https://img.shields.io/badge/GitHub-Profile-blue?style=for-the-badge&logo=github)](https://github.com/Rayyanalik)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/rayyanalikhan)
[![Portfolio](https://img.shields.io/badge/Portfolio-View-green?style=for-the-badge&logo=globe)](https://rayyanalikhan.dev)

**⭐ Star this repository if you found it helpful!**

</div>

