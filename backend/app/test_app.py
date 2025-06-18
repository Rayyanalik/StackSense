from fastapi import FastAPI

app = FastAPI(
    title="Test API",
    description="A test API to verify FastAPI documentation",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Hello World"} 