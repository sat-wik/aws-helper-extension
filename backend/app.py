from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import re

# Configuration
OLLAMA_HOST = "127.0.0.1:11434"
MODEL_NAME = "deepseek-r1"  # Faster quantized model
ollama_client = ollama.Client(host=f"http://{OLLAMA_HOST}", timeout=300)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    input: str

def clean_response(text: str) -> str:
    """Remove thinking patterns and internal monologue"""
    # Remove XML-like tags
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Remove markdown formatting
    text = re.sub(r'```\w*', '', text)
    # Remove step numbers if not needed
    text = re.sub(r'\n\d+\.\s*', '\n• ', text)
    # Trim whitespace and special tokens
    return text.strip().replace('**', '').replace('*', '')

@app.post("/api/query")
async def query(request: QueryRequest):
    try:
        # Optimized prompt to prevent thinking output
        prompt = f"""<task>
        You are an AWS expert. Provide only the final answer in clear steps.
        Do not show reasoning. Use concise bullet points.
        
        Question: {request.input}
        Answer:</task>
        """

        # Faster generation parameters
        response = ollama_client.generate(
            model=MODEL_NAME,
            prompt=prompt,
            options={
                "temperature": 0.3,  # Less randomness
                "max_tokens": 1024,   # Faster than 4096
                "num_ctx": 2048,      # Reduced context window
                "num_gpu": 20,        # Use more GPU layers if available
                "seed": 123           # Consistent outputs
            }
        )
        
        # Clean and return response
        cleaned = clean_response(response['response'])
        return {"response": cleaned}
    
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
