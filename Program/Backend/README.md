# CodeSellers Vendas - Backend

Este é o backend do sistema CodeSellers Vendas, uma aplicação para visualização e análise de dados de vendas por região no Brasil.

## Estrutura do Projeto

O projeto foi organizado em vários módulos para facilitar a manutenção e a legibilidade do código:

- `app.py`: Configuração e criação da aplicação FastAPI
- `config.py`: Configurações e constantes da aplicação
- `data_store.py`: Gerenciamento dos dados de regiões e vendas
- `models.py`: Modelos de dados usando Pydantic
- `routes.py`: Definição dos endpoints da API
- `services.py`: Lógica de negócio e serviços
- `main.py`: Ponto de entrada da aplicação

## Instalação

1. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando o Servidor

Para iniciar o servidor de desenvolvimento:

```bash
python main.py
```

Por padrão, o servidor rodará em `http://localhost:8000`.

## Endpoints da API

### Chat

- `POST /api/query`: Envia uma consulta para o assistente de chat

### Vendas

- `GET /api/vendas/regioes`: Lista todas as regiões disponíveis
- `GET /api/vendas/dados/{regiao}`: Obtém dados de vendas para uma região específica

## Documentação da API

Com o servidor em execução, você pode acessar a documentação interativa em:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc` 