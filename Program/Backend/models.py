from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field
from datetime import datetime

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
    dados_tabela: List[Dict[str, Any]]

class MessageInput(BaseModel):
    """Modelo para input de mensagem no chat."""
    content: str
    sender: str

class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chat.id")
    content: str
    sender: str
    timestamp: datetime = Field(default_factory=datetime.now) 