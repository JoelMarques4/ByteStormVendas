from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class QueryInput(BaseModel):
    """Modelo para input de consulta no assistente de chat."""
    message: str
    api_token: Optional[str] = None

class LangflowResponse(BaseModel):
    """Modelo para resposta do Langflow."""
    response: str

class VendasRegiao(BaseModel):
    """Modelo para dados de vendas de uma região."""
    resumo: Dict[str, Any]
    graficos: Dict[str, str]
    dados_tabela: List[Dict[str, Any]] 