from typing import Dict, List, Any
import csv
import os
from datetime import datetime

class DataStore:
    """Classe para gerenciar os dados de regiões e vendas."""

    def __init__(self):
        self.dados_por_regiao = self._carregar_dados_csv()

    # Mapeamento de estados para regiões usando códigos do SVG
    @property
    def estado_para_regiao(self) -> Dict[str, str]:
        return {
            # Norte
            'BR-AC': 'Norte', 'BR-AP': 'Norte', 'BR-AM': 'Norte', 'BR-PA': 'Norte', 
            'BR-RO': 'Norte', 'BR-RR': 'Norte', 'BR-TO': 'Norte',
            # Nordeste
            'BR-AL': 'Nordeste', 'BR-BA': 'Nordeste', 'BR-CE': 'Nordeste', 
            'BR-MA': 'Nordeste', 'BR-PB': 'Nordeste', 'BR-PE': 'Nordeste', 
            'BR-PI': 'Nordeste', 'BR-RN': 'Nordeste', 'BR-SE': 'Nordeste',
            # Centro-Oeste
            'BR-DF': 'CentroOeste', 'BR-GO': 'CentroOeste', 
            'BR-MT': 'CentroOeste', 'BR-MS': 'CentroOeste',
            # Sudeste
            'BR-ES': 'Sudeste', 'BR-MG': 'Sudeste', 'BR-RJ': 'Sudeste', 'BR-SP': 'Sudeste',
            # Sul
            'BR-PR': 'Sul', 'BR-RS': 'Sul', 'BR-SC': 'Sul'
        }
    
    # Mapeamento inverso da região para o nome no CSV
    @property
    def regiao_para_nome_csv(self) -> Dict[str, str]:
        return {
            'Norte': 'Norte',
            'Nordeste': 'Nordeste',
            'CentroOeste': 'Centro-Oeste',
            'Sudeste': 'Sudeste',
            'Sul': 'Sul'
        }

    # Mapeamento de nome CSV para região
    @property
    def nome_csv_para_regiao(self) -> Dict[str, str]:
        return {
            'Norte': 'Norte',
            'Nordeste': 'Nordeste',
            'Centro-Oeste': 'CentroOeste',
            'Sudeste': 'Sudeste',
            'Sul': 'Sul'
        }

    # Mapeamento inverso para listar todos os estados por região
    @property
    def estados_por_regiao(self) -> Dict[str, List[str]]:
        return {
            'Norte': ['BR-AC', 'BR-AP', 'BR-AM', 'BR-PA', 'BR-RO', 'BR-RR', 'BR-TO'],
            'Nordeste': ['BR-AL', 'BR-BA', 'BR-CE', 'BR-MA', 'BR-PB', 'BR-PE', 'BR-PI', 'BR-RN', 'BR-SE'],
            'CentroOeste': ['BR-DF', 'BR-GO', 'BR-MT', 'BR-MS'],
            'Sudeste': ['BR-ES', 'BR-MG', 'BR-RJ', 'BR-SP'],
            'Sul': ['BR-PR', 'BR-RS', 'BR-SC']
        }

    # Nomes completos dos estados
    @property
    def nome_estado(self) -> Dict[str, str]:
        return {
            'BR-AC': 'Acre', 'BR-AP': 'Amapá', 'BR-AM': 'Amazonas', 'BR-PA': 'Pará', 
            'BR-RO': 'Rondônia', 'BR-RR': 'Roraima', 'BR-TO': 'Tocantins',
            'BR-AL': 'Alagoas', 'BR-BA': 'Bahia', 'BR-CE': 'Ceará', 
            'BR-MA': 'Maranhão', 'BR-PB': 'Paraíba', 'BR-PE': 'Pernambuco', 
            'BR-PI': 'Piauí', 'BR-RN': 'Rio Grande do Norte', 'BR-SE': 'Sergipe',
            'BR-DF': 'Distrito Federal', 'BR-GO': 'Goiás', 
            'BR-MT': 'Mato Grosso', 'BR-MS': 'Mato Grosso do Sul',
            'BR-ES': 'Espírito Santo', 'BR-MG': 'Minas Gerais', 
            'BR-RJ': 'Rio de Janeiro', 'BR-SP': 'São Paulo',
            'BR-PR': 'Paraná', 'BR-RS': 'Rio Grande do Sul', 'BR-SC': 'Santa Catarina'
        }
    
    def _carregar_dados_csv(self) -> Dict[str, List[Dict[str, Any]]]:
        """Carrega os dados do arquivo CSV e organiza-os por região."""
        resultado = {
            "Norte": [],
            "Nordeste": [],
            "CentroOeste": [],
            "Sudeste": [],
            "Sul": []
        }
        
        csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dadosdosprodutos.csv')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=';')
                headers = next(reader)  # Pular o cabeçalho
                
                # Mapear os índices das colunas que nos interessam
                latitude_idx = headers.index('Latitude')
                longitude_idx = headers.index('Longitude')
                data_idx = headers.index('Data')
                cpf_idx = headers.index('CPF')
                cnpj_idx = headers.index('CNPJ')
                nome_cliente_idx = headers.index('nome_cliente')
                regiao_idx = headers.index('regiao')
                estado_idx = headers.index('estado')
                produto_idx = headers.index('produto')
                quantidade_idx = headers.index('quantidade')
                valor_unitario_idx = headers.index('valor_unitario')
                lucro_total_idx = headers.index('lucro_total')
                
                id_counter = 1
                
                for row in reader:
                    if len(row) >= 12:  # Verificar se a linha tem dados suficientes
                        try:
                            # Converter data para o formato ISO
                            data_parts = row[data_idx].split('/')
                            data_iso = f"{data_parts[2]}-{data_parts[1]}-{data_parts[0]}"
                            
                            # Limpar e converter valores numéricos
                            quantidade = int(row[quantidade_idx])
                            valor_unitario = float(row[valor_unitario_idx].replace(',', '.'))
                            lucro_total = float(row[lucro_total_idx].replace(',', '.'))
                            valor_total = quantidade * valor_unitario
                            
                            # Pegar CPF ou CNPJ
                            cpf = row[cpf_idx].strip()
                            cnpj = row[cnpj_idx].strip()
                            doc_fiscal = cnpj if cnpj else cpf
                            
                            regiao_csv = row[regiao_idx]
                            estado = row[estado_idx]
                            regiao_key = self.nome_csv_para_regiao.get(regiao_csv, regiao_csv)
                            
                            # Corrigir o código do estado para o formato SVG (BR-XX)
                            codigo_estado = None
                            for codigo, nome in self.nome_estado.items():
                                if nome.lower() == estado.lower() or nome.replace(' ', '').lower() == estado.lower():
                                    codigo_estado = codigo
                                    break
                            
                            # Se não encontrou diretamente, tente encontrar pela região
                            if not codigo_estado and regiao_key in self.estados_por_regiao:
                                # Use o primeiro estado da região como fallback
                                estados_da_regiao = self.estados_por_regiao[regiao_key]
                                if estados_da_regiao:
                                    codigo_estado = estados_da_regiao[0]
                            
                            # Criar entrada de dados
                            entrada = {
                                "ID": id_counter,
                                "Data": data_iso,
                                "Latitude": row[latitude_idx].replace(',', '.'),
                                "Longitude": row[longitude_idx].replace(',', '.'),
                                "CPF_CNPJ": doc_fiscal,
                                "Cliente": row[nome_cliente_idx],
                                "Regiao": regiao_csv,
                                "Estado": codigo_estado,
                                "Estado_Nome": estado,
                                "Produto": row[produto_idx],
                                "Quantidade": quantidade,
                                "Valor_Unitario": valor_unitario,
                                "Valor": valor_total,  # Calcular valor total
                                "Lucro": lucro_total
                            }
                            
                            # Adicionar à região correspondente
                            if regiao_key in resultado:
                                resultado[regiao_key].append(entrada)
                                id_counter += 1
                        except (ValueError, IndexError) as e:
                            print(f"Erro ao processar linha: {row}, Erro: {e}")
        except Exception as e:
            print(f"Erro ao abrir ou processar o arquivo CSV: {e}")
            # Se houver erro, retornamos dados vazios
        
        return resultado

    def get_regioes(self) -> List[str]:
        """Retorna a lista de regiões disponíveis."""
        return list(self.estados_por_regiao.keys())

    def get_dados_regiao(self, regiao: str) -> List[Dict[str, Any]]:
        """Retorna os dados de vendas para uma região específica."""
        return self.dados_por_regiao.get(regiao, [])

# Instância singleton para acesso aos dados
data_store = DataStore() 