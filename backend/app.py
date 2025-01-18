from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cohere

# Initialize Cohere client
COHERE_API_KEY = "6oBYLB9PXKJfyLK4mTVGW5ReMxhYamXLwQWwl5bR"  # Replace with your API key
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
