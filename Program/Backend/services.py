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
from importar_csv import Vendas
from models import Chat, Message

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
        
    def formatar_dados_banco(self, dados: List[Vendas]) -> str:
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
                texto_formatado += f"  Quantidade Vendida: {item.quantidade}\n"
                texto_formatado += f"  Preço Unitário: R$ {item.valor_unitario:.2f}\n"
                texto_formatado += f"  Lucro: R$ {item.lucro_total:.2f}\n"
                texto_formatado += f"  Data da Venda: {item.data}\n"
        
        return texto_formatado
    
    def buscar_dados_relevantes(self, query: str, dados: List[Vendas], top_k: int = 5) -> List[Vendas]:
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
                statement = select(Vendas)
                dados_banco = session.exec(statement).all()
            
            print(f"Dados do banco recuperados com sucesso. Total de registros: {len(dados_banco)}")
            
            # Buscar dados mais relevantes para a consulta
            dados_relevantes = self.buscar_dados_relevantes(message, dados_banco)
            
            # Formatar dados relevantes
            contexto_banco = self.formatar_dados_banco(dados_relevantes)
            
            # Preparar prompt para o Llama
            prompt = f"""Você é um assistente especializado em análise de dados de vendas. Use os dados do banco de dados para responder à pergunta do usuário.

IMPORTANTE: Responda SEMPRE em português brasileiro, usando linguagem clara e profissional.

Dados do banco de dados:
{contexto_banco}

Pergunta do usuário: {message}

Por favor, responda de forma clara e concisa, usando os dados disponíveis. Se não houver dados suficientes para responder completamente, indique isso na sua resposta. Lembre-se de usar termos e expressões comuns no português brasileiro."""

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
                "margem_lucro": 0,
                "estoque_total": 0,
                "produtos_baixo_estoque": 0
            }
        
        total_vendas = sum(item["Valor"] for item in dados_regiao)
        total_produtos = sum(item["Quantidade"] for item in dados_regiao)
        total_lucro = sum(item.get("Lucro", 0) for item in dados_regiao)
        media_valor = total_vendas / len(dados_regiao) if len(dados_regiao) > 0 else 0
        clientes = set(item["Cliente"] for item in dados_regiao)
        margem_lucro = (total_lucro / total_vendas * 100) if total_vendas > 0 else 0
        
        # Calcular informações de estoque
        estoque_total = sum(item.get("estoque_atual", 0) for item in dados_regiao)
        produtos_baixo_estoque = sum(1 for item in dados_regiao if item.get("estoque_atual", 0) < 10)
        
        return {
            "total_vendas": float(total_vendas),
            "total_produtos": int(total_produtos),
            "media_valor": float(media_valor),
            "num_clientes": len(clientes),
            "total_lucro": float(total_lucro),
            "margem_lucro": float(margem_lucro),
            "estoque_total": int(estoque_total),
            "produtos_baixo_estoque": int(produtos_baixo_estoque)
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
        
        # Preparar dados para o gráfico de estoque
        dados_estoque = {}
        for item in dados_regiao:
            produto = item.get("Produto", "Sem nome")
            estoque = item.get("estoque_atual", 0)
            if produto not in dados_estoque:
                dados_estoque[produto] = estoque
        
        # Estrutura para o frontend
        return {
            "resumo": resumo,
            "dados_tabela": dados_regiao,
            "dados_estoque": [
                {"produto": produto, "estoque": estoque}
                for produto, estoque in dados_estoque.items()
            ]
        }

class ChatService:
    """Serviço para gerenciar chats e mensagens."""
    
    def __init__(self):
        self.engine = engine
    
    def criar_chat(self) -> int:
        """Cria um novo chat e retorna seu ID."""
        with Session(self.engine) as session:
            chat = Chat()
            session.add(chat)
            session.commit()
            return chat.id
    
    def salvar_mensagem(self, chat_id: int, content: str, sender: str) -> None:
        """Salva uma nova mensagem no chat especificado."""
        with Session(self.engine) as session:
            message = Message(chat_id=chat_id, content=content, sender=sender)
            session.add(message)
            
            # Atualizar o updated_at do chat
            chat = session.get(Chat, chat_id)
            if chat:
                chat.updated_at = datetime.now()
            
            session.commit()
    
    def excluir_chat(self, chat_id: int) -> bool:
        """Exclui um chat e todas as suas mensagens."""
        with Session(self.engine) as session:
            chat = session.get(Chat, chat_id)
            if chat:
                session.delete(chat)
                session.commit()
                return True
            return False
    
    def listar_chats(self) -> List[Dict[str, Any]]:
        """Lista todos os chats com suas informações básicas."""
        with Session(self.engine) as session:
            chats = session.query(Chat).order_by(Chat.updated_at.desc()).all()
            return [
                {
                    "id": chat.id,
                    "created_at": chat.created_at,
                    "updated_at": chat.updated_at,
                    "message_count": session.query(Message).filter(Message.chat_id == chat.id).count()
                }
                for chat in chats
            ]
    
    def obter_mensagens_chat(self, chat_id: int) -> List[Dict[str, Any]]:
        """Obtém todas as mensagens de um chat específico."""
        with Session(self.engine) as session:
            messages = session.query(Message).filter(Message.chat_id == chat_id).order_by(Message.timestamp).all()
            return [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "sender": msg.sender,
                    "timestamp": msg.timestamp
                }
                for msg in messages
            ]

# Instâncias singleton dos serviços
llama_service = LlamaService()
vendas_service = VendasService()
chat_service = ChatService() 