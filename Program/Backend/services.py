import requests
from typing import Dict, List, Any
from fastapi import HTTPException
import pandas as pd
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy.engine import create_engine
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from data_store import data_store
from config import DEFAULT_API_TOKEN, LANGFLOW_API_URL
from importar_csv import Pessoa

# Configuração do banco de dados
DATABASE_URL = "postgresql://postgres:12345678Oito*@localhost:5432/postgres?client_encoding=LATIN1"
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Para ver as consultas SQL no console
    connect_args={
        "client_encoding": "LATIN1",
        "options": "-c TimeZone=America/Sao_Paulo"
    }
)

class LlamaService:
    """Serviço para interagir com o Llama local e banco de dados."""
    
    def __init__(self):
        self.llama_url = "http://localhost:11434/api/generate"
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        
    def formatar_dados_banco(self, dados: List[Pessoa]) -> str:
        """Formata os dados do banco para incluir no contexto da IA."""
        texto_formatado = "Dados disponíveis no banco de dados:\n\n"
        
        # Agrupar por região
        dados_por_regiao = {}
        for item in dados:
            regiao = item.regiao or "Não especificada"
            if regiao not in dados_por_regiao:
                dados_por_regiao[regiao] = []
            dados_por_regiao[regiao].append(item)
        
        # Formatar dados por região
        for regiao, items in dados_por_regiao.items():
            texto_formatado += f"\nRegião: {regiao}\n"
            for item in items:
                texto_formatado += f"- Cliente: {item.nome_cliente}\n"
                texto_formatado += f"  Produto: {item.produto}\n"
                texto_formatado += f"  Quantidade: {item.quantidade}\n"
                texto_formatado += f"  Valor: R$ {item.valor_unitario:.2f}\n"
                texto_formatado += f"  Lucro: R$ {item.lucro_total:.2f}\n"
                texto_formatado += f"  Data: {item.data}\n"
        
        return texto_formatado
    
    def buscar_dados_relevantes(self, query: str, dados: List[Pessoa], top_k: int = 5) -> List[Pessoa]:
        """Busca os dados mais relevantes para a consulta usando TF-IDF."""
        # Criar textos para cada registro
        textos = []
        for item in dados:
            texto = f"Região: {item.regiao}, Cliente: {item.nome_cliente}, Produto: {item.produto}, "
            texto += f"Quantidade: {item.quantidade}, Valor: {item.valor_unitario}, Lucro: {item.lucro_total}"
            textos.append(texto)
        
        # Adicionar a query à lista de textos
        textos.append(query)
        
        # Calcular TF-IDF
        try:
            tfidf_matrix = self.vectorizer.fit_transform(textos)
            
            # Calcular similaridade entre a query e todos os documentos
            query_vector = tfidf_matrix[-1:]  # Último vetor é a query
            doc_vectors = tfidf_matrix[:-1]  # Todos os outros são documentos
            
            similaridades = cosine_similarity(query_vector, doc_vectors)[0]
            
            # Obter índices dos top_k mais relevantes
            indices_relevantes = np.argsort(similaridades)[-top_k:][::-1]
            
            # Retornar os dados mais relevantes
            return [dados[i] for i in indices_relevantes]
        except Exception as e:
            print(f"Erro ao calcular similaridade: {str(e)}")
            # Em caso de erro, retorna os primeiros top_k registros
            return dados[:top_k]
    
    async def query(self, message: str):
        """Envia uma consulta para o Llama local com contexto do banco de dados."""
        try:
            # Buscar dados do banco
            with Session(engine) as session:
                statement = select(Pessoa)
                dados_banco = session.exec(statement).all()
            
            print(f"Dados do banco recuperados com sucesso. Total de registros: {len(dados_banco)}")
            
            # Buscar dados mais relevantes para a consulta
            dados_relevantes = self.buscar_dados_relevantes(message, dados_banco)
            
            # Formatar dados relevantes
            contexto_banco = self.formatar_dados_banco(dados_relevantes)
            
            # Preparar prompt para o Llama
            prompt = f"""Você é um assistente especializado em análise de dados de vendas. Use os dados do banco de dados para responder à pergunta do usuário.

Dados do banco de dados:
{contexto_banco}

Pergunta do usuário: {message}

Por favor, responda de forma clara e concisa, usando os dados disponíveis. Se não houver dados suficientes para responder completamente, indique isso na sua resposta."""

            # Enviar para o Llama
            payload = {
                "model": "deepseek-r1",
                "prompt": prompt,
                "stream": False
            }
            
            print("Enviando requisição para o Llama local...")
            response = requests.post(self.llama_url, json=payload)
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao chamar o Llama: {response.status_code}, {response.text}"
                )
        
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

class VendasService:
    """Serviço para gerenciar dados de vendas."""
    
    def listar_regioes(self) -> List[str]:
        """Retorna a lista de regiões disponíveis."""
        return data_store.get_regioes()
    
    def calcular_resumo_vendas(self, dados_regiao: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula o resumo de vendas para uma região."""
        if not dados_regiao:
            return {
                "total_vendas": 0,
                "total_produtos": 0,
                "media_valor": 0,
                "num_clientes": 0,
                "total_lucro": 0,
                "margem_lucro": 0
            }
        
        total_vendas = sum(item["Valor"] for item in dados_regiao)
        total_produtos = sum(item["Quantidade"] for item in dados_regiao)
        total_lucro = sum(item.get("Lucro", 0) for item in dados_regiao)
        media_valor = total_vendas / len(dados_regiao) if len(dados_regiao) > 0 else 0
        clientes = set(item["Cliente"] for item in dados_regiao)
        margem_lucro = (total_lucro / total_vendas * 100) if total_vendas > 0 else 0
        
        return {
            "total_vendas": float(total_vendas),
            "total_produtos": int(total_produtos),
            "media_valor": float(media_valor),
            "num_clientes": len(clientes),
            "total_lucro": float(total_lucro),
            "margem_lucro": float(margem_lucro)
        }
    
    def obter_dados_vendas_regiao(self, regiao: str) -> Dict[str, Any]:
        """Obtém todos os dados de vendas para uma região específica."""
        # Verificar se a região é válida
        if regiao not in data_store.estados_por_regiao:
            raise HTTPException(status_code=404, detail=f"Região '{regiao}' não encontrada")
        
        # Obter dados da região
        dados_regiao = data_store.get_dados_regiao(regiao)
        
        if not dados_regiao:
            raise HTTPException(status_code=404, detail=f"Nenhum dado encontrado para a região '{regiao}'")
        
        # Calcular o resumo dos dados
        resumo = self.calcular_resumo_vendas(dados_regiao)
        
        # Certificar-se de que cada item tem o campo Estado
        for item in dados_regiao:
            if 'Estado' not in item or not item['Estado']:
                # Usar o primeiro estado da região como padrão se não estiver definido
                estados_regiao = data_store.estados_por_regiao.get(regiao, [])
                item['Estado'] = estados_regiao[0] if estados_regiao else regiao
        
        # Estrutura para o frontend
        return {
            "resumo": resumo,
            "dados_tabela": dados_regiao
        }

# Instâncias singleton dos serviços
llama_service = LlamaService()
vendas_service = VendasService() 