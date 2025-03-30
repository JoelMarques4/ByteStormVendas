from sqlmodel import SQLModel, create_engine
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

def criar_tabelas():
    """Cria as tabelas no banco de dados."""
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    print("Criando tabelas no banco de dados...")
    criar_tabelas()
    print("Tabelas criadas com sucesso!") 