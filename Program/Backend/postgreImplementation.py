from sqlmodel import Session, select
from sqlalchemy.engine import create_engine
import requests
import json

# Importar o modelo Vendas da etapa anterior
from importar_csv import Vendas, engine

def buscar_dados_do_banco():
    """Busca dados do PostgreSQL"""
    with Session(engine) as session:
        statement = select(Vendas)
        results = session.exec(statement).all()
        return results

def formatar_dados_para_modelo(dados):
    """Formata os dados para um formato adequado para o modelo"""
    # Exemplo de formatação - ajuste conforme sua necessidade
    texto_formatado = ""
    
    for item in dados:
        texto_formatado += f"Venda: {item.nome}, Idade: {item.idade}, Email: {item.email}, Estoque: {item.estoque_atual}\n"
    
    return texto_formatado

def enviar_para_modelo(texto):
    """Envia o texto para o modelo DeepSeek-R1 no Ollama"""
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "deepseek-r1",
        "prompt": texto,
        "stream": False
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        print(f"Erro ao chamar o modelo: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # Buscar dados do banco
    dados = buscar_dados_do_banco()
    
    # Formatar dados para o modelo
    texto_formatado = formatar_dados_para_modelo(dados)
    
    # Enviar para o modelo
    resultado = enviar_para_modelo(texto_formatado)
    
    print("Resposta do modelo:")
    print(resultado)