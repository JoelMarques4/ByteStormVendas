from typing import Dict, List, Any

class DataStore:
    """Classe para gerenciar os dados de regiões e vendas."""

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

    # Dados fictícios de vendas para cada região
    @property
    def dados_vendas_mockados(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "Norte": [
                {"ID": 1, "Data": "2023-05-15", "Produto": "Laptop", "Quantidade": 3, "Valor": 6500.00, "Estado": "BR-AM", "Cliente": "Cliente 5"},
                {"ID": 2, "Data": "2023-06-10", "Produto": "Smartphone", "Quantidade": 5, "Valor": 4500.00, "Estado": "BR-PA", "Cliente": "Cliente 2"},
                {"ID": 3, "Data": "2023-07-22", "Produto": "Tablet", "Quantidade": 2, "Valor": 2200.00, "Estado": "BR-AC", "Cliente": "Cliente 8"},
                {"ID": 4, "Data": "2023-08-03", "Produto": "Monitor", "Quantidade": 4, "Valor": 3800.00, "Estado": "BR-RO", "Cliente": "Cliente 3"},
                {"ID": 5, "Data": "2023-09-18", "Produto": "Teclado", "Quantidade": 8, "Valor": 960.00, "Estado": "BR-TO", "Cliente": "Cliente 12"}
            ],
            "Nordeste": [
                {"ID": 6, "Data": "2023-04-12", "Produto": "Laptop", "Quantidade": 7, "Valor": 15400.00, "Estado": "BR-BA", "Cliente": "Cliente 9"},
                {"ID": 7, "Data": "2023-06-23", "Produto": "Smartphone", "Quantidade": 12, "Valor": 10800.00, "Estado": "BR-CE", "Cliente": "Cliente 4"},
                {"ID": 8, "Data": "2023-08-05", "Produto": "Tablet", "Quantidade": 6, "Valor": 6600.00, "Estado": "BR-PE", "Cliente": "Cliente 7"},
                {"ID": 9, "Data": "2023-09-14", "Produto": "Monitor", "Quantidade": 5, "Valor": 4750.00, "Estado": "BR-MA", "Cliente": "Cliente 11"},
                {"ID": 10, "Data": "2023-10-27", "Produto": "Teclado", "Quantidade": 15, "Valor": 1800.00, "Estado": "BR-PB", "Cliente": "Cliente 6"}
            ],
            "CentroOeste": [
                {"ID": 11, "Data": "2023-05-08", "Produto": "Laptop", "Quantidade": 4, "Valor": 8800.00, "Estado": "BR-DF", "Cliente": "Cliente 14"},
                {"ID": 12, "Data": "2023-07-19", "Produto": "Smartphone", "Quantidade": 8, "Valor": 7200.00, "Estado": "BR-GO", "Cliente": "Cliente 10"},
                {"ID": 13, "Data": "2023-08-30", "Produto": "Tablet", "Quantidade": 3, "Valor": 3300.00, "Estado": "BR-MT", "Cliente": "Cliente 15"},
                {"ID": 14, "Data": "2023-10-11", "Produto": "Monitor", "Quantidade": 6, "Valor": 5700.00, "Estado": "BR-MS", "Cliente": "Cliente 1"},
                {"ID": 15, "Data": "2023-11-22", "Produto": "Teclado", "Quantidade": 10, "Valor": 1200.00, "Estado": "BR-DF", "Cliente": "Cliente 18"}
            ],
            "Sudeste": [
                {"ID": 16, "Data": "2023-03-14", "Produto": "Laptop", "Quantidade": 12, "Valor": 26400.00, "Estado": "BR-SP", "Cliente": "Cliente 20"},
                {"ID": 17, "Data": "2023-05-25", "Produto": "Smartphone", "Quantidade": 20, "Valor": 18000.00, "Estado": "BR-RJ", "Cliente": "Cliente 13"},
                {"ID": 18, "Data": "2023-07-06", "Produto": "Tablet", "Quantidade": 10, "Valor": 11000.00, "Estado": "BR-MG", "Cliente": "Cliente 17"},
                {"ID": 19, "Data": "2023-09-17", "Produto": "Monitor", "Quantidade": 15, "Valor": 14250.00, "Estado": "BR-ES", "Cliente": "Cliente 19"},
                {"ID": 20, "Data": "2023-11-28", "Produto": "Teclado", "Quantidade": 25, "Valor": 3000.00, "Estado": "BR-SP", "Cliente": "Cliente 16"}
            ],
            "Sul": [
                {"ID": 21, "Data": "2023-04-05", "Produto": "Laptop", "Quantidade": 5, "Valor": 11000.00, "Estado": "BR-RS", "Cliente": "Cliente 22"},
                {"ID": 22, "Data": "2023-06-16", "Produto": "Smartphone", "Quantidade": 10, "Valor": 9000.00, "Estado": "BR-PR", "Cliente": "Cliente 21"},
                {"ID": 23, "Data": "2023-08-27", "Produto": "Tablet", "Quantidade": 4, "Valor": 4400.00, "Estado": "BR-SC", "Cliente": "Cliente 25"},
                {"ID": 24, "Data": "2023-10-08", "Produto": "Monitor", "Quantidade": 8, "Valor": 7600.00, "Estado": "BR-PR", "Cliente": "Cliente 23"},
                {"ID": 25, "Data": "2023-12-19", "Produto": "Teclado", "Quantidade": 12, "Valor": 1440.00, "Estado": "BR-RS", "Cliente": "Cliente 24"}
            ]
        }

    # Gráficos mockados como dados base64
    @property
    def graficos_mockados(self) -> Dict[str, str]:
        return {
            "vendas_por_produto": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
            "quantidade_por_produto": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
            "vendas_por_estado": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        }

    def get_regioes(self) -> List[str]:
        """Retorna a lista de regiões disponíveis."""
        return list(self.estados_por_regiao.keys())

    def get_dados_regiao(self, regiao: str) -> List[Dict[str, Any]]:
        """Retorna os dados de vendas para uma região específica."""
        return self.dados_vendas_mockados.get(regiao, [])

# Instância singleton para acesso aos dados
data_store = DataStore() 