from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from models import QueryInput, LangflowResponse, VendasRegiao, Chat, Message, MessageInput
from services import llama_service, vendas_service, chat_service

# Criar os roteadores para cada grupo de endpoints
chat_router = APIRouter(prefix="/api", tags=["chat"])
vendas_router = APIRouter(prefix="/api/vendas", tags=["vendas"])

@chat_router.post("/query", response_model=LangflowResponse)
async def query_llama(query_input: QueryInput):
    """Envia uma consulta para o assistente de chat e retorna a resposta."""
    response = await llama_service.query(query_input.message)
    return LangflowResponse(response=response)

# Rotas para gerenciamento de chats
@chat_router.post("/chats", response_model=Dict[str, int])
async def criar_chat():
    """Cria um novo chat e retorna seu ID."""
    chat_id = chat_service.criar_chat()
    return {"chat_id": chat_id}

@chat_router.post("/chats/{chat_id}/messages")
async def salvar_mensagem(chat_id: int, message_input: MessageInput):
    """Salva uma nova mensagem no chat especificado."""
    chat_service.salvar_mensagem(chat_id, message_input.content, message_input.sender)
    return {"status": "success"}

@chat_router.delete("/chats/{chat_id}")
async def excluir_chat(chat_id: int):
    """Exclui um chat específico."""
    if not chat_service.excluir_chat(chat_id):
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    return {"status": "success"}

@chat_router.get("/chats", response_model=List[Dict[str, Any]])
async def listar_chats():
    """Lista todos os chats disponíveis."""
    return chat_service.listar_chats()

@chat_router.get("/chats/{chat_id}/messages", response_model=List[Dict[str, Any]])
async def obter_mensagens_chat(chat_id: int):
    """Obtém todas as mensagens de um chat específico."""
    return chat_service.obter_mensagens_chat(chat_id)

@vendas_router.get("/regioes")
async def listar_regioes():
    """Retorna a lista de regiões disponíveis."""
    regioes = vendas_service.listar_regioes()
    return {"regioes": regioes}

@vendas_router.get("/dados/{regiao}", response_model=VendasRegiao)
async def dados_vendas_por_regiao(regiao: str):
    """Retorna dados de vendas para uma região específica."""
    return vendas_service.obter_dados_vendas_regiao(regiao) 