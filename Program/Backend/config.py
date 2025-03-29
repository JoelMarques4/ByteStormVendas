import os

# API Token do serviço Langflow
DEFAULT_API_TOKEN = "AstraCS:MnQbglZIzaTaPbRnxiPZgzQB:819e42f699d4a8544a8389d04ed28961ce76413a0520b9ca7fa58a3dccd0b309"

# URL da API Langflow
LANGFLOW_API_URL = "https://api.langflow.astra.datastax.com/lf/6a45b841-eabe-4f9b-b5a0-8711e83beddf/api/v1/run/795cb236-e7bf-4769-a71c-cc599a4d3165"

# Configurações do servidor
HOST = "0.0.0.0"
PORT = 8000

# Configurações de ambiente
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
STATIC_DIR = "dist" if ENVIRONMENT == "production" else None 