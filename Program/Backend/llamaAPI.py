from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, SQLModel, Field, create_engine
import requests
from typing import Optional, List, Dict, Any
import pandas as pd
import io

# Configuração do banco de dados
DATABASE_URL = "postgresql://postgres:12345678Oito*@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)

# Definição do modelo
class Pessoa(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    idade: int
    email: str

# Modelos Pydantic para as requisições e respostas
class PessoaResponse(SQLModel):
    id: int
    nome: str
    idade: int
    email: str

class ModeloRequest(SQLModel):
    tipo: str = "todos"
    id: Optional[int] = None
    prompt: str = ""

class ModeloResponse(SQLModel):
    dados: List[PessoaResponse]
    resposta_modelo: str

# Criar tabelas
SQLModel.metadata.create_all(engine)

# Dependência para obter a sessão do banco de dados
def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="API de Integração PostgreSQL e Ollama DeepSeek-R1")

@app.post("/importar-csv", response_model=Dict[str, str])
async def importar_csv(arquivo: UploadFile = File(...), session: Session = Depends(get_session)):
    """
    Importa dados de um arquivo CSV para o banco de dados PostgreSQL.
    """
    if not arquivo.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    
    try:
        # Ler conteúdo do arquivo
        contents = await arquivo.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Inserir no banco
        objetos = []
        for _, row in df.iterrows():
            dados = row.to_dict()
            objeto = Pessoa(**dados)
            objetos.append(objeto)
        
        session.add_all(objetos)
        session.commit()
        
        return {"mensagem": f"Importados {len(objetos)} registros com sucesso!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao importar CSV: {str(e)}")

@app.get("/pessoas", response_model=List[PessoaResponse])
def listar_pessoas(session: Session = Depends(get_session)):
    """
    Lista todas as pessoas armazenadas no banco de dados.
    """
    pessoas = session.exec(select(Pessoa)).all()
    return pessoas

@app.post("/consultar-modelo", response_model=ModeloResponse)
def consultar_modelo(
    dados: ModeloRequest = Body(...),
    session: Session = Depends(get_session)
):
    """
    Consulta o modelo DeepSeek-R1 com dados do banco de dados.
    
    - tipo: "todos" para consultar todos os registros ou "id" para consultar por ID
    - id: ID do registro (necessário apenas quando tipo="id")
    - prompt: Texto adicional para enviar ao modelo junto com os dados
    """
    # Buscar dados do banco
    if dados.tipo == "todos":
        pessoas = session.exec(select(Pessoa)).all()
    elif dados.tipo == "id" and dados.id is not None:
        pessoas = session.exec(select(Pessoa).where(Pessoa.id == dados.id)).all()
        if not pessoas:
            raise HTTPException(status_code=404, detail=f"Pessoa com ID {dados.id} não encontrada")
    else:
        raise HTTPException(status_code=400, detail="Tipo de consulta inválido ou ID ausente")
    
    # Formatar dados
    texto_formatado = ""
    for p in pessoas:
        texto_formatado += f"Pessoa: {p.nome}, Idade: {p.idade}, Email: {p.email}\n"
    
    # Adicionar prompt personalizado
    texto_final = f"{dados.prompt}\n\nDados:\n{texto_formatado}"
    
    # Consultar o modelo
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "deepseek-r1",
        "prompt": texto_final,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return ModeloResponse(
                dados=[PessoaResponse(id=p.id, nome=p.nome, idade=p.idade, email=p.email) for p in pessoas],
                resposta_modelo=response.json()["response"]
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao chamar o modelo: {response.status_code}, {response.text}"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta: {str(e)}")

# Adicionar rota para interação básica com o modelo sem dados do banco
@app.post("/perguntar", response_model=Dict[str, str])
async def perguntar_modelo(pergunta: Dict[str, str] = Body(...)):
    """
    Envia uma pergunta diretamente ao modelo DeepSeek-R1 sem usar dados do banco.
    
    Exemplo de corpo da requisição:
    ```json
    {"pergunta": "Qual é a capital da França?"}
    ```
    """
    if "pergunta" not in pergunta:
        raise HTTPException(status_code=400, detail="Corpo da requisição deve conter o campo 'pergunta'")
    
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "deepseek-r1",
        "prompt": pergunta["pergunta"],
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return {"resposta": response.json()["response"]}
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao chamar o modelo: {response.status_code}, {response.text}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta: {str(e)}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)