import requests
from typing import Dict, List, Any
from fastapi import HTTPException
import pandas as pd
from datetime import datetime

from data_store import data_store
from config import DEFAULT_API_TOKEN, LANGFLOW_API_URL

class LangflowService:
    """Serviço para interagir com a API do Langflow."""
    
    def extract_message(self, response_data):
        """Extrai a mensagem da resposta do Langflow."""
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
    
    async def query(self, message: str, api_token: str = None):
        """Envia uma consulta para o Langflow e retorna a resposta."""
        # Use o token API fornecido ou o padrão
        token = api_token or DEFAULT_API_TOKEN
        
        # Parâmetros da consulta
        params = {
            "stream": "false"
        }
        
        # Cabeçalhos
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # Payload da requisição
        payload = {
            "input_value": message,
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
            # Faz a requisição para a API
            response = requests.post(LANGFLOW_API_URL, params=params, headers=headers, json=payload)
            
            # Verifica se a requisição foi bem-sucedida
            response.raise_for_status()
            
            # Extrai a mensagem da resposta
            message = self.extract_message(response.json())
            
            # Retorna apenas a mensagem
            return message
        
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Erro ao chamar a API do Langflow: {str(e)}")


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
langflow_service = LangflowService()
vendas_service = VendasService() 