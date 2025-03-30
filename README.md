# 🚀 ByteStorm Vendas - Sistema de Análise de Vendas com IA

<div align="center">

![ByteStorm Logo](Frontend/src/assets/logo.png)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0-blue.svg)](https://www.postgresql.org/)
[![Ollama](https://img.shields.io/badge/Ollama-0.1.0-green.svg)](https://ollama.ai/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.5.13-green.svg)](https://vuejs.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.3-blue.svg)](https://getbootstrap.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.0.0-blue.svg)](https://www.chartjs.org/)

</div>

## 📑 Sumário
- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Executar](#-como-executar)
- [Documentação](#-documentação)
- [Contribuição](#-contribuição)

## 🎯 Sobre o Projeto

ByteStorm Vendas é um sistema avançado de análise de vendas que utiliza Inteligência Artificial para fornecer insights valiosos sobre dados de vendas. O sistema integra tecnologias modernas como PostgreSQL para armazenamento de dados e Ollama com o modelo DeepSeek-R1 para análise inteligente.

### 📚 Documentação Detalhada
- [Documentação do Backend](Backend/README.md)
- [Documentação do Frontend](Frontend/README.md)

## ✨ Funcionalidades

### 📊 Análise de Dados
- Análise detalhada de vendas
- Visualização de dados interativa
- Gráficos e dashboards personalizados
- Análise temporal e comparativa

### 🤖 Inteligência Artificial
- Previsão de vendas
- Análise de tendências
- Recomendações personalizadas
- Detecção de anomalias

### 📱 Interface
- Design moderno e responsivo
- Visualizações interativas
- Filtros dinâmicos
- Exportação de dados

## 🛠 Tecnologias Utilizadas

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- Pandas
- NumPy
- PostgreSQL
- Ollama (DeepSeek-R1)

### Frontend
- Vue.js 3
- Bootstrap 5.3.3
- Chart.js
- D3.js
- Vuex
- Axios

## 📋 Pré-requisitos

- Python 3.11 ou superior
- Node.js 18 ou superior
- PostgreSQL 15.0
- Ollama instalado localmente
- Git

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/ByteStormVendas.git
cd ByteStormVendas
```

2. Configure o ambiente virtual Python:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. Instale as dependências do Backend:
```bash
cd Backend
pip install -r requirements.txt
```

4. Instale as dependências do Frontend:
```bash
cd ../Frontend
npm install
```

5. Configure o banco de dados PostgreSQL:
```bash
# Crie um banco de dados chamado 'bytestorm'
createdb bytestorm
```

6. Configure as variáveis de ambiente:
```bash
# Backend (.env)
DATABASE_URL=postgresql://usuario:senha@localhost:5432/bytestorm
OLLAMA_API_URL=http://localhost:11434

# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_OLLAMA_URL=http://localhost:11434
```

## 📁 Estrutura do Projeto

```
ByteStormVendas/
├── Backend/           # API e lógica de negócio
│   ├── app/          # Aplicação principal
│   ├── services/     # Serviços e lógica
│   └── tests/        # Testes
├── Frontend/         # Interface do usuário
│   ├── src/          # Código fonte
│   └── public/       # Arquivos estáticos
└── docs/            # Documentação
```

## 🎮 Como Executar

1. Inicie o servidor Backend:
```bash
cd Backend
uvicorn app:app --reload
```

2. Em outro terminal, inicie o Frontend:
```bash
cd Frontend
npm run dev
```

3. Acesse a aplicação:
```
http://localhost:5173
```

## 📝 Documentação

### API
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Componentes
- [Documentação do Backend](Backend/README.md)
- [Documentação do Frontend](Frontend/README.md)

## 🤝 Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📈 Roadmap

- [ ] Implementação de autenticação
- [ ] Mais tipos de visualizações
- [ ] Exportação avançada de dados
- [ ] Integração com mais fontes de dados
- [ ] Sistema de notificações
- [ ] App mobile

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">
Feito com ❤️ pela equipe ByteStorm
</div> 