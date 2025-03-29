from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from typing import Optional
import os

app = FastAPI(title="Langflow API Integration")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request models
class QueryInput(BaseModel):
    message: str
    api_token: Optional[str] = None

# Define response models
class LangflowResponse(BaseModel):
    response: str

# Default API token (for development only)
DEFAULT_API_TOKEN = "AstraCS:MnQbglZIzaTaPbRnxiPZgzQB:819e42f699d4a8544a8389d04ed28961ce76413a0520b9ca7fa58a3dccd0b309"

def extract_message(response_data):
    """Extract the actual message from the Langflow response."""
    try:
        # Tenta encontrar a mensagem no caminho mais comum
        if 'outputs' in response_data and len(response_data['outputs']) > 0:
            first_output = response_data['outputs'][0]
            if 'outputs' in first_output and len(first_output['outputs']) > 0:
                message_data = first_output['outputs'][0]
                if 'outputs' in message_data and 'message' in message_data['outputs']:
                    return message_data['outputs']['message']['message']
                elif 'artifacts' in message_data and 'message' in message_data['artifacts']:
                    return message_data['artifacts']['message']
                elif 'messages' in message_data and len(message_data['messages']) > 0:
                    return message_data['messages'][0]['message']
        
        # Se não encontrar, retorna uma mensagem de erro
        return "Desculpe, não consegui processar a resposta corretamente."
    except Exception as e:
        print(f"Erro ao extrair mensagem: {str(e)}")
        return "Desculpe, ocorreu um erro ao processar a resposta."

@app.post("/api/query", response_model=LangflowResponse)
async def query_langflow(query_input: QueryInput):
    """Send a query to the Langflow API and return the response."""
    # Use provided API token or fall back to default
    api_token = query_input.api_token or DEFAULT_API_TOKEN
    
    # API endpoint
    url = "https://api.langflow.astra.datastax.com/lf/6a45b841-eabe-4f9b-b5a0-8711e83beddf/api/v1/run/795cb236-e7bf-4769-a71c-cc599a4d3165"
    
    # Query parameters
    params = {
        "stream": "false"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    # Request payload
    payload = {
        "input_value": query_input.message,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "Agent-P5ux3": {},
            "ChatInput-UG3MA": {},
            "ChatOutput-bBEAX": {},
            "URL-2vuYK": {},
            "CalculatorComponent-b0roK": {}
        }
    }
    
    try:
        # Make the API request
        response = requests.post(url, params=params, headers=headers, json=payload)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Extract the message from the response
        message = extract_message(response.json())
        
        # Return only the message
        return LangflowResponse(response=message)
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling Langflow API: {str(e)}")

# Only mount static files in production
if os.environ.get("ENVIRONMENT") == "production":
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)