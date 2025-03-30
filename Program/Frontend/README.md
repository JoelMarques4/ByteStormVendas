# 🎨 Frontend - TrendsightAI

## 📋 Descrição
Interface moderna e responsiva do sistema TrendsightAI, desenvolvida com React e TypeScript, oferecendo visualizações interativas e análises detalhadas de dados de vendas.

## 🚀 Tecnologias Principais
- Vue.js 3
- Bootstrap 5.3.3
- Bootstrap Icons
- Chart.js
- D3.js
- Axios
- Vue Router
- Vuex (Gerenciamento de Estado)

## 📁 Estrutura do Projeto
```
Frontend/
├── src/
│   ├── components/     # Componentes reutilizáveis
│   │   ├── charts/    # Componentes de gráficos
│   │   ├── layout/    # Componentes de layout
│   │   └── ui/        # Componentes de interface
│   ├── pages/         # Páginas da aplicação
│   ├── services/      # Serviços e APIs
│   ├── hooks/         # Custom hooks
│   ├── store/         # Gerenciamento de estado
│   ├── types/         # Definições de tipos
│   ├── utils/         # Funções utilitárias
│   └── assets/        # Recursos estáticos
├── public/            # Arquivos públicos
└── package.json       # Dependências e scripts
```

## 🎨 Componentes Principais

### Gráficos e Visualizações
- `LineChart` - Gráfico de linha para tendências
- `BarChart` - Gráfico de barras para comparações
- `PieChart` - Gráfico de pizza para distribuições
- `HeatMap` - Mapa de calor para correlações
- `ScatterPlot` - Gráfico de dispersão

### Layout
- `Sidebar` - Menu lateral
- `Header` - Cabeçalho da aplicação
- `Dashboard` - Painel principal
- `Card` - Componente de card informativo

### UI
- `Button` - Botões personalizados
- `Input` - Campos de entrada
- `Select` - Seletores
- `Modal` - Janelas modais
- `Table` - Tabelas de dados

## 📊 Visualizações de Dados

### Dashboard Principal
- Visão geral de vendas
- Métricas principais
- Gráficos de tendência
- Alertas e notificações

### Análise de Produtos
- Desempenho por produto
- Comparativo de vendas
- Análise de estoque
- Previsões

## 🎯 Funcionalidades

### Interatividade
- Filtros dinâmicos
- Zoom em gráficos
- Exportação de dados
- Personalização de visualizações

### Análise Avançada
- Drill-down em dados
- Comparativos personalizados
- Análise temporal
- Correlações

### IA e Insights
- Recomendações
- Previsões
- Anomalias
- Tendências

## 🔧 Configuração

1. Instale as dependências:
```bash
npm install
```

2. Configure as variáveis de ambiente:
```env
VITE_API_URL=http://localhost:8000
VITE_OLLAMA_URL=http://localhost:11434
```

3. Inicie o servidor de desenvolvimento:
```bash
npm run dev
```

## 🎨 Estilização

### Bootstrap
- Design system responsivo
- Componentes pré-estilizados
- Grid system
- Utilitários CSS
- Temas personalizados
- Animações e transições

### Componentes
- Design consistente
- Acessibilidade
- Performance
- Reutilização

## 📱 Responsividade

- Breakpoints personalizados
- Layout adaptativo