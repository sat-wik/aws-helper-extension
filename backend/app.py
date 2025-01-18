from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cohere
import os

# Initialize Cohere client
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
co = cohere.Client(COHERE_API_KEY)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for your specific needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema
class QueryRequest(BaseModel):
    input: str

@app.get("/")
def read_root():
    """Root endpoint to handle default requests."""
    return {"message": "Welcome to the AWS Helper API! Use /api/query for queries."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Serve an empty response for favicon requests."""
    return {"message": "No favicon available"}


# Endpoint for querying
@app.post("/api/query")
async def query(request: QueryRequest):
    user_input = request.input.strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # Generate response using Cohere
        response = co.generate(
            model="command-xlarge-nightly",
            prompt=f"Answer the query concisely: {user_input}",
            max_tokens=100,
            temperature=0.7,
        )
        generated_text = response.generations[0].text.strip()
        return {"response": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
