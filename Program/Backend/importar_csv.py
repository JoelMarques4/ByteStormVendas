from sqlmodel import SQLModel, Field, Session, create_engine
import pandas as pd
from typing import Optional
from sqlalchemy.engine import URL
import sqlalchemy

# Definir modelo corretamente com todas as colunas que você tem
class Vendas(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    data: Optional[str] = Field(default=None)
    cpf: Optional[str] = Field(default=None)
    cnpj: Optional[str] = Field(default=None)
    nome_cliente: str = Field(nullable=False)  # Não pode ser nulo
    regiao: Optional[str] = Field(default=None)
    estado: Optional[str] = Field(default=None)
    produto: Optional[str] = Field(default=None)
    quantidade: Optional[int] = Field(default=None)
    valor_unitario: Optional[float] = Field(default=None)
    lucro_total: Optional[float] = Field(default=None)
    estoque_atual: Optional[int] = Field(default=None)

# Configurar conexão com o banco de dados com parâmetros específicos de codificação
def create_db_engine():
    # Método 1: Usando URL direta com parâmetros de codificação
    DATABASE_URL = "postgresql://postgres:12345678Oito*@localhost:5432/postgres?client_encoding=LATIN1"
    
    # Método 2: Usando objeto URL com parâmetros de conexão
    # connection_url = URL.create(
    #     "postgresql",
    #     username="postgres",
    #     password="sua_senha",
    #     host="localhost",
    #     port=5432,
    #     database="meu_banco"
    # )
    
    # Criar engine com configurações específicas
    engine = create_engine(
        DATABASE_URL,
        echo=True,  # Para ver as consultas SQL no console (útil para depuração)
        connect_args={
            "client_encoding": "LATIN1",  # Tente LATIN1 para caracteres especiais em português
            "options": "-c TimeZone=America/Sao_Paulo"  # Configurar fuso horário
        }
    )
    
    return engine

def criar_tabelas():
    # Obter conexão com configurações corretas
    engine = create_db_engine()
    
    try:
        # Criar todas as tabelas definidas
        SQLModel.metadata.create_all(engine)
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabelas: {str(e)}")
        # Em caso de erro, tente verificar a versão do banco e outras informações
        try:
            with engine.connect() as conn:
                result = conn.execute(sqlalchemy.text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"Versão do PostgreSQL: {version}")
                
                # Verificar configuração de codificação do servidor
                result = conn.execute(sqlalchemy.text("SHOW server_encoding;"))
                server_encoding = result.fetchone()[0]
                print(f"Codificação do servidor: {server_encoding}")
                
                result = conn.execute(sqlalchemy.text("SHOW client_encoding;"))
                client_encoding = result.fetchone()[0]
                print(f"Codificação do cliente: {client_encoding}")
        except Exception as db_error:
            print(f"Erro ao consultar informações do banco: {str(db_error)}")

def importar_csv(arquivo_csv: str):
    engine = create_db_engine()
    
    try:
        # Tente diferentes codificações para ler o arquivo CSV
        try:
            # Primeiro tente com UTF-8
            df = pd.read_csv(arquivo_csv, encoding='utf-8', sep=';', decimal=',')
        except UnicodeDecodeError:
            # Se falhar, tente com LATIN1 (comum para arquivos em português)
            print("UTF-8 falhou, tentando LATIN1...")
            df = pd.read_csv(arquivo_csv, encoding='latin1', sep=';', decimal=',')
            
        print(f"CSV carregado com sucesso. Total de linhas: {len(df)}")
        
        # Converter colunas numéricas
        df['latitude'] = df['Latitude'].str.replace(',', '.').astype(float)
        df['longitude'] = df['Longitude'].str.replace(',', '.').astype(float)
        df['quantidade'] = df['quantidade'].astype(int)
        df['valor_unitario'] = df['valor_unitario'].str.replace(',', '.').astype(float)
        df['lucro_total'] = df['lucro_total'].str.replace(',', '.').astype(float)
        
        # Renomear colunas para corresponder ao modelo
        df.columns = df.columns.str.lower()
        
        # Verificar e preencher valores nulos nas colunas obrigatórias
        if 'nome_cliente' in df.columns and df['nome_cliente'].isnull().any():
            print(f"Atenção: {df['nome_cliente'].isnull().sum()} linhas têm valores nulos na coluna 'nome_cliente'")
            df['nome_cliente'] = df['nome_cliente'].fillna("Nome não informado")
        
        # Se a coluna 'nome_cliente' não existir no CSV
        if 'nome_cliente' not in df.columns:
            print("Erro: A coluna 'nome_cliente' não existe no CSV!")
            print(f"Colunas encontradas: {list(df.columns)}")
            return
        
        # Verificar os tipos de dados
        for col in df.columns:
            print(f"Coluna {col}: tipo {df[col].dtype}")
                
        # Importar em lotes para evitar problemas com grandes conjuntos de dados
        BATCH_SIZE = 100
        total_imported = 0
        
        for i in range(0, len(df), BATCH_SIZE):
            batch = df.iloc[i:i+BATCH_SIZE]
            
            # Criar objetos do modelo
            objetos = []
            for _, row in batch.iterrows():
                try:
                    # Converter linha para dicionário e filtrar apenas as colunas existentes no modelo
                    dados = {k: v for k, v in row.to_dict().items() if k in Vendas.__annotations__}
                    objeto = Vendas(**dados)
                    objetos.append(objeto)
                except Exception as e:
                    print(f"Erro ao processar linha: {row}")
                    print(f"Detalhes: {str(e)}")
            
            # Inserir no banco de dados
            with Session(engine) as session:
                try:
                    session.add_all(objetos)
                    session.commit()
                    total_imported += len(objetos)
                    print(f"Lote {i//BATCH_SIZE + 1} importado com sucesso: {len(objetos)} registros")
                except Exception as e:
                    session.rollback()
                    print(f"Erro ao importar lote {i//BATCH_SIZE + 1}: {str(e)}")
                    
                    # Tentar inserir linha por linha para identificar problemas específicos
                    for obj in objetos:
                        try:
                            with Session(engine) as individual_session:
                                individual_session.add(obj)
                                individual_session.commit()
                                total_imported += 1
                        except Exception as individual_error:
                            print(f"Erro na linha individual: {str(obj)}")
                            print(f"Detalhes: {str(individual_error)}")
        
        print(f"Importação concluída. Total de registros importados: {total_imported}")
        
    except Exception as e:
        print(f"Erro durante a importação: {str(e)}")

def verificar_csv(arquivo_csv: str):
    """Função para analisar o CSV antes de importar"""
    try:
        # Tente diferentes codificações
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                print(f"Tentando ler o CSV com codificação {encoding}...")
                df = pd.read_csv(arquivo_csv, encoding=encoding, nrows=5)
                print(f"Leitura bem-sucedida com codificação {encoding}")
                break
            except UnicodeDecodeError:
                print(f"Falha ao ler com codificação {encoding}")
                continue
        
        if df is None:
            print("Não foi possível ler o arquivo CSV com nenhuma das codificações testadas")
            return
        
        # Mostrar informações sobre o DataFrame
        print("\nInformações do DataFrame:")
        print(df.info())
        
        # Mostrar as primeiras linhas
        print("\nPrimeiras linhas:")
        print(df.head())
        
        # Verificar valores nulos
        print("\nValores nulos por coluna:")
        print(df.isnull().sum())
        
        # Verificar colunas disponíveis
        print("\nColunas disponíveis:")
        print(list(df.columns))
        
    except Exception as e:
        print(f"Erro ao analisar o CSV: {str(e)}")

if __name__ == "__main__":
    # Verificar o CSV primeiro
    print("Analisando o arquivo CSV...")
    verificar_csv("dadosdosprodutos.csv")
    
    # Criar as tabelas
    print("\nCriando tabelas...")
    criar_tabelas()
    
    # Perguntar ao usuário se deseja continuar com a importação
    resposta = input("\nDeseja continuar com a importação? (S/N): ")
    if resposta.upper() == 'S':
        # Importar dados do CSV
        print("\nIniciando importação...")
        importar_csv("dadosdosprodutos.csv")
    else:
        print("Importação cancelada pelo usuário.")