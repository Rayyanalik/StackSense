from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from typing import List, Dict, Optional
from app.schemas.tech_stack import TechStackRecommendationRequest, TechStackRecommendationResponse
from app.services.recommendation_engine import RecommendationEngine
from app.core.logging import logger

router = APIRouter()
recommendation_engine = RecommendationEngine()

@router.get("/recommend", response_class=HTMLResponse)
async def get_recommendation_form():
    """Return a simple HTML form for tech stack recommendations."""
    return """
    <html>
        <head>
            <title>Tech Stack Recommender</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                form { display: flex; flex-direction: column; gap: 15px; }
                textarea, input { padding: 8px; margin: 5px 0; }
                button { padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; }
                button:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <h1>Tech Stack Recommender</h1>
            <form id="recommendForm">
                <div>
                    <label for="description">Project Description:</label>
                    <textarea id="description" name="description" rows="4" required></textarea>
                </div>
                <div>
                    <label for="requirements">Requirements (one per line):</label>
                    <textarea id="requirements" name="requirements" rows="4" required></textarea>
                </div>
                <div>
                    <label for="constraints">Constraints (JSON format):</label>
                    <input type="text" id="constraints" name="constraints" value='{"frontend": [], "backend": []}'>
                </div>
                <button type="submit">Get Recommendation</button>
            </form>
            <div id="result"></div>

            <script>
                document.getElementById('recommendForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const form = e.target;
                    const data = {
                        description: form.description.value,
                        requirements: form.requirements.value.split('\\n').filter(r => r.trim()),
                        constraints: JSON.parse(form.constraints.value)
                    };
                    
                    try {
                        const response = await fetch('/api/v1/tech-stack/recommend', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        });
                        const result = await response.json();
                        document.getElementById('result').innerHTML = 
                            `<pre>${JSON.stringify(result, null, 2)}</pre>`;
                    } catch (error) {
                        document.getElementById('result').innerHTML = 
                            `<p style="color: red">Error: ${error.message}</p>`;
                    }
                });
            </script>
        </body>
    </html>
    """

@router.post("/recommend", response_model=TechStackRecommendationResponse)
async def recommend_tech_stack(request: TechStackRecommendationRequest):
    """Generate a tech stack recommendation based on project requirements."""
    try:
        recommendation = recommendation_engine.generate_recommendation(
            request.description,
            request.requirements,
            request.constraints
        )
        return recommendation
    except Exception as e:
        logger.error(f"Error generating recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 