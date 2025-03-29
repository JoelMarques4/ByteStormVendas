"""
Arquivo principal para iniciar a aplicação.
Este arquivo agora serve como um ponto de entrada para a aplicação.
A lógica real foi movida para módulos separados para facilitar a manutenção.
"""
import uvicorn
from app import app

if __name__ == "__main__":
    # Para usar a aplicação modularizada, execute:
    # python main.py
    #
    # Para instalar as dependências:
    # pip install -r requirements.txt
    uvicorn.run(app, host="0.0.0.0", port=8000)