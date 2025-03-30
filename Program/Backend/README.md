# 🛠 Backend - TrendsightAI

## 📋 Descrição
Backend do sistema TrendsightAI, desenvolvido em Python com FastAPI, integrando PostgreSQL e Ollama para análise de dados e processamento de linguagem natural.

## 🚀 Tecnologias Principais
- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pandas
- NumPy
- Ollama (DeepSeek-R1)

## 📁 Estrutura do Projeto
```
Backend/
├── app.py              # Aplicação principal FastAPI
├── main.py            # Ponto de entrada da aplicação
├── config.py          # Configurações do sistema
├── models.py          # Modelos de dados
├── routes.py          # Rotas da API
├── services.py        # Serviços principais
├── data_store.py      # Gerenciamento de dados
├── postgreImplementation.py  # Implementação PostgreSQL
├── llamaAPI.py        # Integração com Ollama
├── criar_tabelas.py   # Script de criação de tabelas
├── importar_csv.py    # Script de importação de dados
└── requirements.txt   # Dependências do projeto
```

## 🔌 Endpoints da API

### Produtos
- `GET /produtos` - Lista todos os produtos
- `GET /produtos/{id}` - Obtém detalhes de um produto específico
- `GET /produtos/busca/{termo}` - Busca produtos por termo
- `GET /produtos/analise` - Análise estatística dos produtos

### Vendas
- `GET /vendas` - Lista todas as vendas
- `GET /vendas/{id}` - Obtém detalhes de uma venda específica
- `GET /vendas/periodo/{inicio}/{fim}` - Vendas por período
- `GET /vendas/analise` - Análise estatística das vendas

### Clientes
- `GET /clientes` - Lista todos os clientes
- `GET /clientes/{id}` - Obtém detalhes de um cliente específico
- `GET /clientes/analise` - Análise estatística dos clientes

### IA e Análise
- `POST /ia/analise` - Análise de dados com IA
- `POST /ia/previsao` - Previsão de vendas
- `POST /ia/recomendacoes` - Recomendações baseadas em IA

## 🗄 Banco de Dados

### Tabelas Principais
- `produtos` - Informações dos produtos
- `vendas` - Registro de vendas
- `clientes` - Dados dos clientes
- `analises` - Resultados de análises
- `chats` - Histórico de interações com IA

### Scripts SQL
- `criar_tabelas.sql` - Criação das tabelas principais
- `criar_tabelas_chat.sql` - Criação das tabelas de chat
- `atualizar_mensagens.sql` - Atualização de mensagens

## 🔧 Configuração

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure o banco de dados:
```bash
python criar_tabelas.py
```

3. Importe os dados iniciais:
```bash
python importar_csv.py
```

4. Configure as variáveis de ambiente:
```env
DATABASE_URL=postgresql://usuario:senha@localhost:5432/codesellers
OLLAMA_API_URL=http://localhost:11434
```

## 🚀 Executando o Servidor

```bash
uvicorn app:app --reload
```

## 📊 Análise de Dados

O sistema utiliza:
- Pandas para manipulação de dados
- NumPy para cálculos estatísticos
- SQLAlchemy para ORM
- Ollama para processamento de linguagem natural

## 🤖 Integração com IA

O sistema utiliza o Ollama com o modelo DeepSeek-R1 para:
- Análise de tendências
- Previsão de vendas
- Geração de insights
- Recomendações personalizadas

## 🔍 Testes

Para executar os testes:
```bash
```

## 📝 Documentação da API

A documentação completa da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`