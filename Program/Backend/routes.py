from fastapi import APIRouter

from models import QueryInput, LangflowResponse, VendasRegiao
from services import llama_service, vendas_service

# Criar os roteadores para cada grupo de endpoints
chat_router = APIRouter(prefix="/api", tags=["chat"])
vendas_router = APIRouter(prefix="/api/vendas", tags=["vendas"])

@chat_router.post("/query", response_model=LangflowResponse)
async def query_llama(query_input: QueryInput):
    """Envia uma consulta para o assistente de chat e retorna a resposta."""
    response = await llama_service.query(query_input.message)
    return LangflowResponse(response=response)

@vendas_router.get("/regioes")
async def listar_regioes():
    """Retorna a lista de regiões disponíveis."""
    regioes = vendas_service.listar_regioes()
    return {"regioes": regioes}

@vendas_router.get("/dados/{regiao}", response_model=VendasRegiao)
async def dados_vendas_por_regiao(regiao: str):
    """Retorna dados de vendas para uma região específica."""
    return vendas_service.obter_dados_vendas_regiao(regiao) 