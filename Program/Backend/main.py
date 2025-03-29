from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from typing import Optional, List, Dict, Any
import os
import json
import base64
from pathlib import Path

app = FastAPI(title="ByteStorm Vendas API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Mapeamento de estados para regiões usando códigos do SVG
estado_para_regiao = {
    # Norte
    'BR-AC': 'Norte', 'BR-AP': 'Norte', 'BR-AM': 'Norte', 'BR-PA': 'Norte', 
    'BR-RO': 'Norte', 'BR-RR': 'Norte', 'BR-TO': 'Norte',
    # Nordeste
    'BR-AL': 'Nordeste', 'BR-BA': 'Nordeste', 'BR-CE': 'Nordeste', 
    'BR-MA': 'Nordeste', 'BR-PB': 'Nordeste', 'BR-PE': 'Nordeste', 
    'BR-PI': 'Nordeste', 'BR-RN': 'Nordeste', 'BR-SE': 'Nordeste',
    # Centro-Oeste
    'BR-DF': 'CentroOeste', 'BR-GO': 'CentroOeste', 
    'BR-MT': 'CentroOeste', 'BR-MS': 'CentroOeste',
    # Sudeste
    'BR-ES': 'Sudeste', 'BR-MG': 'Sudeste', 'BR-RJ': 'Sudeste', 'BR-SP': 'Sudeste',
    # Sul
    'BR-PR': 'Sul', 'BR-RS': 'Sul', 'BR-SC': 'Sul'
}

# Mapeamento inverso para listar todos os estados por região
estados_por_regiao = {
    'Norte': ['BR-AC', 'BR-AP', 'BR-AM', 'BR-PA', 'BR-RO', 'BR-RR', 'BR-TO'],
    'Nordeste': ['BR-AL', 'BR-BA', 'BR-CE', 'BR-MA', 'BR-PB', 'BR-PE', 'BR-PI', 'BR-RN', 'BR-SE'],
    'CentroOeste': ['BR-DF', 'BR-GO', 'BR-MT', 'BR-MS'],
    'Sudeste': ['BR-ES', 'BR-MG', 'BR-RJ', 'BR-SP'],
    'Sul': ['BR-PR', 'BR-RS', 'BR-SC']
}

# Nomes completos dos estados
nome_estado = {
    'BR-AC': 'Acre', 'BR-AP': 'Amapá', 'BR-AM': 'Amazonas', 'BR-PA': 'Pará', 
    'BR-RO': 'Rondônia', 'BR-RR': 'Roraima', 'BR-TO': 'Tocantins',
    'BR-AL': 'Alagoas', 'BR-BA': 'Bahia', 'BR-CE': 'Ceará', 
    'BR-MA': 'Maranhão', 'BR-PB': 'Paraíba', 'BR-PE': 'Pernambuco', 
    'BR-PI': 'Piauí', 'BR-RN': 'Rio Grande do Norte', 'BR-SE': 'Sergipe',
    'BR-DF': 'Distrito Federal', 'BR-GO': 'Goiás', 
    'BR-MT': 'Mato Grosso', 'BR-MS': 'Mato Grosso do Sul',
    'BR-ES': 'Espírito Santo', 'BR-MG': 'Minas Gerais', 
    'BR-RJ': 'Rio de Janeiro', 'BR-SP': 'São Paulo',
    'BR-PR': 'Paraná', 'BR-RS': 'Rio Grande do Sul', 'BR-SC': 'Santa Catarina'
}

# Define request models
class QueryInput(BaseModel):
    message: str
    api_token: Optional[str] = None

# Define response models
class LangflowResponse(BaseModel):
    response: str

class VendasRegiao(BaseModel):
    resumo: Dict[str, Any]
    graficos: Dict[str, str]
    dados_tabela: List[Dict[str, Any]]

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

# Dados fictícios de vendas para cada região
dados_vendas_mockados = {
    "Norte": [
        {"ID": 1, "Data": "2023-05-15", "Produto": "Laptop", "Quantidade": 3, "Valor": 6500.00, "Estado": "BR-AM", "Cliente": "Cliente 5"},
        {"ID": 2, "Data": "2023-06-10", "Produto": "Smartphone", "Quantidade": 5, "Valor": 4500.00, "Estado": "BR-PA", "Cliente": "Cliente 2"},
        {"ID": 3, "Data": "2023-07-22", "Produto": "Tablet", "Quantidade": 2, "Valor": 2200.00, "Estado": "BR-AC", "Cliente": "Cliente 8"},
        {"ID": 4, "Data": "2023-08-03", "Produto": "Monitor", "Quantidade": 4, "Valor": 3800.00, "Estado": "BR-RO", "Cliente": "Cliente 3"},
        {"ID": 5, "Data": "2023-09-18", "Produto": "Teclado", "Quantidade": 8, "Valor": 960.00, "Estado": "BR-TO", "Cliente": "Cliente 12"}
    ],
    "Nordeste": [
        {"ID": 6, "Data": "2023-04-12", "Produto": "Laptop", "Quantidade": 7, "Valor": 15400.00, "Estado": "BR-BA", "Cliente": "Cliente 9"},
        {"ID": 7, "Data": "2023-06-23", "Produto": "Smartphone", "Quantidade": 12, "Valor": 10800.00, "Estado": "BR-CE", "Cliente": "Cliente 4"},
        {"ID": 8, "Data": "2023-08-05", "Produto": "Tablet", "Quantidade": 6, "Valor": 6600.00, "Estado": "BR-PE", "Cliente": "Cliente 7"},
        {"ID": 9, "Data": "2023-09-14", "Produto": "Monitor", "Quantidade": 5, "Valor": 4750.00, "Estado": "BR-MA", "Cliente": "Cliente 11"},
        {"ID": 10, "Data": "2023-10-27", "Produto": "Teclado", "Quantidade": 15, "Valor": 1800.00, "Estado": "BR-PB", "Cliente": "Cliente 6"}
    ],
    "CentroOeste": [
        {"ID": 11, "Data": "2023-05-08", "Produto": "Laptop", "Quantidade": 4, "Valor": 8800.00, "Estado": "BR-DF", "Cliente": "Cliente 14"},
        {"ID": 12, "Data": "2023-07-19", "Produto": "Smartphone", "Quantidade": 8, "Valor": 7200.00, "Estado": "BR-GO", "Cliente": "Cliente 10"},
        {"ID": 13, "Data": "2023-08-30", "Produto": "Tablet", "Quantidade": 3, "Valor": 3300.00, "Estado": "BR-MT", "Cliente": "Cliente 15"},
        {"ID": 14, "Data": "2023-10-11", "Produto": "Monitor", "Quantidade": 6, "Valor": 5700.00, "Estado": "BR-MS", "Cliente": "Cliente 1"},
        {"ID": 15, "Data": "2023-11-22", "Produto": "Teclado", "Quantidade": 10, "Valor": 1200.00, "Estado": "BR-DF", "Cliente": "Cliente 18"}
    ],
    "Sudeste": [
        {"ID": 16, "Data": "2023-03-14", "Produto": "Laptop", "Quantidade": 12, "Valor": 26400.00, "Estado": "BR-SP", "Cliente": "Cliente 20"},
        {"ID": 17, "Data": "2023-05-25", "Produto": "Smartphone", "Quantidade": 20, "Valor": 18000.00, "Estado": "BR-RJ", "Cliente": "Cliente 13"},
        {"ID": 18, "Data": "2023-07-06", "Produto": "Tablet", "Quantidade": 10, "Valor": 11000.00, "Estado": "BR-MG", "Cliente": "Cliente 17"},
        {"ID": 19, "Data": "2023-09-17", "Produto": "Monitor", "Quantidade": 15, "Valor": 14250.00, "Estado": "BR-ES", "Cliente": "Cliente 19"},
        {"ID": 20, "Data": "2023-11-28", "Produto": "Teclado", "Quantidade": 25, "Valor": 3000.00, "Estado": "BR-SP", "Cliente": "Cliente 16"}
    ],
    "Sul": [
        {"ID": 21, "Data": "2023-04-05", "Produto": "Laptop", "Quantidade": 5, "Valor": 11000.00, "Estado": "BR-RS", "Cliente": "Cliente 22"},
        {"ID": 22, "Data": "2023-06-16", "Produto": "Smartphone", "Quantidade": 10, "Valor": 9000.00, "Estado": "BR-PR", "Cliente": "Cliente 21"},
        {"ID": 23, "Data": "2023-08-27", "Produto": "Tablet", "Quantidade": 4, "Valor": 4400.00, "Estado": "BR-SC", "Cliente": "Cliente 25"},
        {"ID": 24, "Data": "2023-10-08", "Produto": "Monitor", "Quantidade": 8, "Valor": 7600.00, "Estado": "BR-PR", "Cliente": "Cliente 23"},
        {"ID": 25, "Data": "2023-12-19", "Produto": "Teclado", "Quantidade": 12, "Valor": 1440.00, "Estado": "BR-RS", "Cliente": "Cliente 24"}
    ]
}

# Gráficos mockados como dados base64 (imagens em branco por simplicidade)
graficos_mockados = {
    "vendas_por_produto": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
    "quantidade_por_produto": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
    "vendas_por_estado": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
}

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

@app.get("/api/vendas/regioes")
async def listar_regioes():
    """Retorna a lista de regiões disponíveis."""
    regioes = list(estados_por_regiao.keys())
    return {"regioes": regioes}

@app.get("/api/vendas/dados/{regiao}", response_model=VendasRegiao)
async def dados_vendas_por_regiao(regiao: str):
    """Retorna dados de vendas para uma região específica."""
    # Verificar se a região é válida
    if regiao not in estados_por_regiao:
        raise HTTPException(status_code=404, detail=f"Região '{regiao}' não encontrada")
    
    # Usar dados mockados em vez de tentar carregar de um arquivo
    dados_regiao = dados_vendas_mockados.get(regiao, [])
    
    if not dados_regiao:
        raise HTTPException(status_code=404, detail=f"Nenhum dado encontrado para a região '{regiao}'")
    
    # Calcular o resumo dos dados
    total_vendas = sum(item["Valor"] for item in dados_regiao)
    total_produtos = sum(item["Quantidade"] for item in dados_regiao)
    media_valor = total_vendas / len(dados_regiao)
    clientes = set(item["Cliente"] for item in dados_regiao)
    
    resumo = {
        "total_vendas": float(total_vendas),
        "total_produtos": int(total_produtos),
        "media_valor": float(media_valor),
        "num_clientes": len(clientes)
    }
    
    # Usar dados de tabela mockados
    dados_tabela = dados_regiao
    
    # Usar gráficos mockados
    graficos = graficos_mockados
    
    return {
        "resumo": resumo,
        "graficos": graficos,
        "dados_tabela": dados_tabela
    }

# Only mount static files in production
if os.environ.get("ENVIRONMENT") == "production":
    app.mount("/", StaticFiles(directory="dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)