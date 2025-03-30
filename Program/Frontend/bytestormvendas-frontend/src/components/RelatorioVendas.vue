<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from 'vue';
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';

// Registrar componentes necessários do Chart.js
Chart.register(...registerables, zoomPlugin);

const props = defineProps({
  regioes: {
    type: Array,
    required: true,
    default: () => []
  },
  mostrar: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['fechar']);

const carregando = ref(true);
const erro = ref(null);
const dadosVendas = ref(null);
const regioesSelecionadas = ref([]);

// Título formatado para as regiões selecionadas
const tituloRegioes = computed(() => {
  if (regioesSelecionadas.value.length === 1) {
    return `Região ${regioesSelecionadas.value[0]}`;
  } else if (regioesSelecionadas.value.length === 5) {
    return 'Todas as Regiões';
  } else {
    return `${regioesSelecionadas.value.length} Regiões Selecionadas`;
  }
});

// Referências para os canvas dos gráficos
const vendasProdutoChart = ref(null);
const vendasEstadoChart = ref(null);
const qtdProdutoMesChart = ref(null);
const vendasEstadoMesChart = ref(null);
const lucroReceitaChart = ref(null);

// Instâncias dos gráficos
let chartVendasProduto = null;
let chartVendasEstado = null;
let chartQtdProdutoMes = null;
let chartVendasEstadoMes = null;
let chartLucroReceita = null;

// Variável para controlar tentativas de renderização
let tentativasRenderizacao = 0;
const MAX_TENTATIVAS = 5;

// Função para inicializar os gráficos com um atraso maior
const inicializarGraficos = () => {
  console.log('Iniciando inicialização dos gráficos...');
  tentativasRenderizacao = 0;
  tentarRenderizarGraficos();
};

// Função para tentar renderizar os gráficos várias vezes
const tentarRenderizarGraficos = () => {
  tentativasRenderizacao++;
  console.log(`Tentativa ${tentativasRenderizacao} de renderizar gráficos`);
  
  // Verificar se os elementos canvas estão disponíveis
  const canvasDisponiveis = 
    vendasProdutoChart.value && 
    vendasEstadoChart.value && 
    qtdProdutoMesChart.value && 
    vendasEstadoMesChart.value &&
    lucroReceitaChart.value;
  
  console.log('Canvas disponíveis:', canvasDisponiveis);
  
  if (canvasDisponiveis) {
    console.log('Todos os canvas estão disponíveis, renderizando gráficos');
    renderizarGraficos();
  } else if (tentativasRenderizacao < MAX_TENTATIVAS) {
    console.log(`Alguns canvas não estão disponíveis, tentando novamente em ${tentativasRenderizacao * 200}ms`);
    setTimeout(tentarRenderizarGraficos, tentativasRenderizacao * 200);
  } else {
    console.error('Número máximo de tentativas excedido. Falha ao renderizar gráficos.');
    erro.value = 'Não foi possível carregar os gráficos. Por favor, tente novamente.';
  }
};

// Função para carregar os dados de vendas das regiões selecionadas
const carregarDados = async () => {
  carregando.value = true;
  erro.value = null;
  regioesSelecionadas.value = [...props.regioes];
  
  if (regioesSelecionadas.value.length === 0) {
    erro.value = 'Nenhuma região selecionada. Por favor, selecione pelo menos uma região.';
    carregando.value = false;
    return;
  }
  
  try {
    console.log(`Carregando dados para as regiões: ${regioesSelecionadas.value.join(', ')}`);
    
    // Usando Promise.all para carregar dados de múltiplas regiões em paralelo
    const requests = regioesSelecionadas.value.map(regiao => 
      axios.get(`http://localhost:8000/api/vendas/dados/${regiao}`)
    );
    
    const responses = await Promise.all(requests);
    console.log('Todas as respostas recebidas:', responses);
    
    // Combinar dados de todas as regiões
    const dadosCombinados = combinarDadosRegioes(responses.map(response => response.data));
    dadosVendas.value = dadosCombinados;
    
    // Renderizar os gráficos após os dados serem carregados
    await nextTick();
    inicializarGraficos();
  } catch (error) {
    console.error('Erro ao carregar dados:', error);
    if (error.response) {
      // O servidor respondeu com um status de erro
      console.error('Resposta do servidor:', error.response.data);
      erro.value = error.response.data.detail || `Erro ${error.response.status}: ${error.response.statusText}`;
    } else if (error.request) {
      // A requisição foi feita mas não houve resposta
      console.error('Sem resposta do servidor');
      erro.value = 'Não foi possível conectar ao servidor. Verifique se o backend está em execução.';
    } else {
      // Algo aconteceu ao configurar a requisição que acionou um erro
      console.error('Erro de configuração:', error.message);
      erro.value = `Erro ao configurar requisição: ${error.message}`;
    }
  } finally {
    carregando.value = false;
  }
};

// Função para combinar dados de múltiplas regiões
const combinarDadosRegioes = (dadosRegioes) => {
  if (!dadosRegioes || dadosRegioes.length === 0) {
    return { dados_tabela: [] };
  }
  
  // Combinar todos os dados_tabela em uma única array
  const dadosTabelaCombinados = [];
  
  dadosRegioes.forEach((dadosRegiao, index) => {
    if (dadosRegiao && dadosRegiao.dados_tabela) {
      // Adicionar informação da região se não existir
      const regiao = regioesSelecionadas.value[index];
      const dadosComRegiao = dadosRegiao.dados_tabela.map(item => ({
        ...item,
        Regiao: item.Regiao || regiao
      }));
      
      dadosTabelaCombinados.push(...dadosComRegiao);
    }
  });
  
  return { dados_tabela: dadosTabelaCombinados };
};

// Função para renderizar os gráficos usando Chart.js
const renderizarGraficos = () => {
  console.log('Tentando renderizar gráficos com dados:', dadosVendas.value);
  if (!dadosVendas.value || !dadosVendas.value.dados_tabela) {
    console.error('Dados inválidos para renderização de gráficos:', dadosVendas.value);
    return;
  }
  
  // Processar dados para os gráficos
  const dados = processarDadosGraficos();
  console.log('Dados processados para gráficos:', dados);

  // Renderizar gráfico de vendas por produto
  if (vendasProdutoChart.value) {
    console.log('Elemento canvas para vendas por produto disponível');
    renderizarGraficoVendasProduto(dados.vendasProduto);
  } else {
    console.error('Elemento canvas para vendas por produto não encontrado');
  }
  
  // Renderizar gráfico de vendas por estado
  if (vendasEstadoChart.value) {
    console.log('Elemento canvas para vendas por estado disponível');
    renderizarGraficoVendasEstado(dados.vendasEstado);
  } else {
    console.error('Elemento canvas para vendas por estado não encontrado');
  }
  
  // Renderizar gráfico de quantidade por produto e mês
  if (qtdProdutoMesChart.value) {
    console.log('Elemento canvas para quantidade por produto e mês disponível');
    const qtdProdutoMesDatasets = dados.qtdProdutoMesDatasets;
    const meses = dados.mesesNomes;
    renderizarGraficoQtdProdutoMes(qtdProdutoMesDatasets, meses);
  } else {
    console.error('Elemento canvas para quantidade por produto e mês não encontrado');
  }
  
  // Renderizar gráfico de vendas por estado e mês
  if (vendasEstadoMesChart.value) {
    console.log('Elemento canvas para vendas por estado e mês disponível');
    const vendasEstadoMesDatasets = dados.vendasEstadoMesDatasets;
    const meses = dados.mesesNomes;
    renderizarGraficoVendasEstadoMes(vendasEstadoMesDatasets, meses);
  } else {
    console.error('Elemento canvas para vendas por estado e mês não encontrado');
  }
  
  // Renderizar gráfico de lucro e receita por produto
  if (lucroReceitaChart.value) {
    console.log('Elemento canvas para lucro e receita disponível');
    renderizarGraficoLucroReceita(dados.lucroProduto, dados.vendasProduto);
  } else {
    console.error('Elemento canvas para lucro e receita não encontrado');
  }
};

// Função para processar dados para os gráficos
const processarDadosGraficos = () => {
  const dados = dadosVendas.value.dados_tabela;
  
  // Converter datas para objetos Date
  dados.forEach(item => {
    item.DataObj = new Date(item.Data);
    // Criar formatos de mês para ordenação e exibição
    item.MesOrdenacao = `${item.DataObj.getFullYear()}-${String(item.DataObj.getMonth() + 1).padStart(2, '0')}`;
    item.MesNome = item.DataObj.toLocaleString('pt-BR', { month: 'short', year: 'numeric' });
    
    // Garantir que valor está disponível
    if (!item.hasOwnProperty('Valor') && item.hasOwnProperty('Valor_Unitario') && item.hasOwnProperty('Quantidade')) {
      item.Valor = item.Valor_Unitario * item.Quantidade;
    }
  });

  // Coletar todos os meses únicos e ordenar cronologicamente
  const mesesSet = new Set();
  dados.forEach(item => mesesSet.add(item.MesOrdenacao));
  const mesesOrdenados = Array.from(mesesSet).sort();
  
  // Mapeamento de mês ordenação para nome do mês
  const mesParaNome = {};
  dados.forEach(item => {
    mesParaNome[item.MesOrdenacao] = item.MesNome;
  });
  
  // Lista de nomes de meses, em ordem cronológica
  const mesesNomes = mesesOrdenados.map(mes => mesParaNome[mes] || mes);

  // Vendas por produto
  const vendasProdutoTemp = {};
  dados.forEach(item => {
    if (vendasProdutoTemp[item.Produto]) {
      vendasProdutoTemp[item.Produto] += item.Valor;
    } else {
      vendasProdutoTemp[item.Produto] = item.Valor;
    }
  });
  
  // Remover a limitação de 10 produtos mais vendidos
  const produtosOrdenados = Object.entries(vendasProdutoTemp)
    .sort((a, b) => b[1] - a[1]);
  
  const vendasProduto = Object.fromEntries(produtosOrdenados);

  // Vendas por estado/região
  const vendasEstadoTemp = {};
  dados.forEach(item => {
    // Usar região se estado não estiver disponível, ou combinados quando temos múltiplas regiões
    let chave = item.Estado ? getEstadoNome(item.Estado) : item.Regiao;
    
    // Se temos múltiplas regiões, adicione a região ao nome do estado para distinguir
    if (regioesSelecionadas.value.length > 1 && item.Estado) {
      chave = `${getEstadoNome(item.Estado)} (${item.Regiao})`;
    }
    
    if (vendasEstadoTemp[chave]) {
      vendasEstadoTemp[chave] += item.Valor;
    } else {
      vendasEstadoTemp[chave] = item.Valor;
    }
  });
  
  // Limitar a 15 estados/regiões com mais vendas quando temos múltiplas regiões
  const limite = regioesSelecionadas.value.length > 1 ? 15 : 10;
  const estadosOrdenados = Object.entries(vendasEstadoTemp)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limite);
  
  const vendasEstado = Object.fromEntries(estadosOrdenados);

  // Quantidade por produto e mês
  const qtdProdutoMesTemp = {};
  
  // Usar MesOrdenacao para agrupar dados
  dados.forEach(item => {
    if (!qtdProdutoMesTemp[item.Produto]) {
      qtdProdutoMesTemp[item.Produto] = {};
    }
    if (qtdProdutoMesTemp[item.Produto][item.MesOrdenacao]) {
      qtdProdutoMesTemp[item.Produto][item.MesOrdenacao] += item.Quantidade;
    } else {
      qtdProdutoMesTemp[item.Produto][item.MesOrdenacao] = item.Quantidade;
    }
  });
  
  // Calcular total de unidades vendidas por produto
  const produtosTotais = {};
  Object.entries(qtdProdutoMesTemp).forEach(([produto, mesesData]) => {
    produtosTotais[produto] = Object.values(mesesData).reduce((acc, val) => acc + val, 0);
  });
  
  // Remover a limitação de 5 produtos mais vendidos em quantidade
  const produtosTopQuantidade = Object.entries(produtosTotais)
    .sort((a, b) => b[1] - a[1])
    .map(item => item[0]);
  
  // Preparar dados para gráfico: produtos por mês
  const qtdProdutoMesDatasets = produtosTopQuantidade.map((produto, index) => {
    const cores = [
      'rgba(255, 99, 132, 0.7)',
      'rgba(54, 162, 235, 0.7)',
      'rgba(255, 206, 86, 0.7)',
      'rgba(75, 192, 192, 0.7)',
      'rgba(153, 102, 255, 0.7)',
      'rgba(255, 159, 64, 0.7)',
      'rgba(201, 203, 207, 0.7)',
      'rgba(0, 162, 232, 0.7)',
      'rgba(139, 195, 74, 0.7)',
      'rgba(103, 58, 183, 0.7)',
      'rgba(255, 99, 71, 0.7)',
      'rgba(0, 191, 255, 0.7)',
      'rgba(255, 215, 0, 0.7)',
      'rgba(147, 112, 219, 0.7)',
      'rgba(50, 205, 50, 0.7)'
    ];
    
    return {
      label: produto,
      data: mesesOrdenados.map(mes => qtdProdutoMesTemp[produto]?.[mes] || 0),
      backgroundColor: cores[index % cores.length],
      borderColor: cores[index % cores.length].replace('0.7', '1'),
      borderWidth: 1
    };
  });

  // Vendas por estado/região e mês
  const vendasEstadoMesTemp = {};
  dados.forEach(item => {
    // Usar região se estado não estiver disponível, ou combinados quando temos múltiplas regiões
    let chave = item.Estado ? getEstadoNome(item.Estado) : item.Regiao;
    
    // Se temos múltiplas regiões, adicione a região ao nome do estado para distinguir
    if (regioesSelecionadas.value.length > 1 && item.Estado) {
      chave = `${getEstadoNome(item.Estado)} (${item.Regiao})`;
    }
    
    if (!vendasEstadoMesTemp[chave]) {
      vendasEstadoMesTemp[chave] = {};
    }
    if (vendasEstadoMesTemp[chave][item.MesOrdenacao]) {
      vendasEstadoMesTemp[chave][item.MesOrdenacao] += item.Valor;
    } else {
      vendasEstadoMesTemp[chave][item.MesOrdenacao] = item.Valor;
    }
  });
  
  // Calcular total de vendas por estado
  const estadosTotais = {};
  Object.entries(vendasEstadoMesTemp).forEach(([estado, mesesData]) => {
    estadosTotais[estado] = Object.values(mesesData).reduce((acc, val) => acc + val, 0);
  });
  
  // Pegar os 5 estados com mais vendas para o gráfico por mês (ou mais quando múltiplas regiões)
  const limite2 = regioesSelecionadas.value.length > 1 ? 8 : 5;
  const estadosTopVendas = Object.entries(estadosTotais)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limite2)
    .map(item => item[0]);
  
  // Preparar dados para gráfico: estados por mês
  const vendasEstadoMesDatasets = estadosTopVendas.map((estado, index) => {
    const cores = [
      'rgba(255, 99, 132, 0.7)',
      'rgba(54, 162, 235, 0.7)',
      'rgba(255, 206, 86, 0.7)',
      'rgba(75, 192, 192, 0.7)',
      'rgba(153, 102, 255, 0.7)',
      'rgba(255, 159, 64, 0.7)',
      'rgba(201, 203, 207, 0.7)',
      'rgba(0, 162, 232, 0.7)',
      'rgba(139, 195, 74, 0.7)',
      'rgba(103, 58, 183, 0.7)',
    ];
    
    return {
      label: estado,
      data: mesesOrdenados.map(mes => vendasEstadoMesTemp[estado]?.[mes] || 0),
      backgroundColor: cores[index % cores.length],
      borderColor: cores[index % cores.length].replace('0.7', '1'),
      borderWidth: 1
    };
  });

  // Lucro por produto
  const lucroProdutoTemp = {};
  dados.forEach(item => {
    if (lucroProdutoTemp[item.Produto]) {
      lucroProdutoTemp[item.Produto] += item.Lucro || 0;
    } else {
      lucroProdutoTemp[item.Produto] = item.Lucro || 0;
    }
  });
  
  // Usar os mesmos produtos do gráfico de vendas para manter consistência
  const lucroProduto = {};
  Object.keys(vendasProduto).forEach(produto => {
    lucroProduto[produto] = lucroProdutoTemp[produto] || 0;
  });

  return { 
    vendasProduto, 
    vendasEstado, 
    mesesNomes,
    qtdProdutoMesDatasets,
    vendasEstadoMesDatasets,
    lucroProduto
  };
};

// Função para obter o nome do estado a partir do código
const getEstadoNome = (codigoEstado) => {
  const estadosNomes = {
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
  };
  return estadosNomes[codigoEstado] || codigoEstado;
};

// Renderizar gráfico de vendas por produto
const renderizarGraficoVendasProduto = (vendasProduto) => {
  if (!vendasProdutoChart.value) return;
  
  const produtos = Object.keys(vendasProduto);
  const valores = produtos.map(produto => vendasProduto[produto]);

  if (chartVendasProduto) {
    chartVendasProduto.destroy();
  }

  const ctx = vendasProdutoChart.value.getContext('2d');
  if (!ctx) return;
  
  chartVendasProduto = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: produtos,
      datasets: [{
        label: 'Valor Total Vendido (R$)',
        data: valores,
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => `Valor: ${formatarMoeda(context.raw)}`
          }
        },
        title: {
          display: true,
          text: 'Vendas por Produto'
        },
        legend: {
          display: true,
          position: 'top'
        },
        zoom: {
          pan: {
            enabled: true,
            mode: 'x'
          },
          zoom: {
            wheel: {
              enabled: true,
              speed: 0.05
            },
            pinch: {
              enabled: true
            },
            mode: 'x',
            drag: {
              enabled: true,
              backgroundColor: 'rgba(54, 162, 235, 0.3)',
              borderColor: 'rgba(54, 162, 235, 0.5)'
            }
          },
          limits: {
            x: {min: 'original', max: 'original'}
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: value => formatarMoeda(value)
          }
        }
      }
    }
  });
};

// Renderizar gráfico de vendas por estado
const renderizarGraficoVendasEstado = (vendasEstado) => {
  if (!vendasEstadoChart.value) return;
  
  const estados = Object.keys(vendasEstado);
  const valores = estados.map(estado => vendasEstado[estado]);

  if (chartVendasEstado) {
    chartVendasEstado.destroy();
  }

  const ctx = vendasEstadoChart.value.getContext('2d');
  if (!ctx) return;
  
  chartVendasEstado = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: estados,
      datasets: [{
        label: 'Valor Total Vendido (R$)',
        data: valores,
        backgroundColor: 'rgba(75, 192, 192, 0.7)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => `Valor: ${formatarMoeda(context.raw)}`
          }
        },
        title: {
          display: true,
          text: regioesSelecionadas.value.length > 1 ? 'Vendas por Estado/Região' : 'Vendas por Estado'
        },
        legend: {
          display: true,
          position: 'top'
        },
        zoom: {
          pan: {
            enabled: true,
            mode: 'x'
          },
          zoom: {
            wheel: {
              enabled: true,
              speed: 0.05
            },
            pinch: {
              enabled: true
            },
            mode: 'x',
            drag: {
              enabled: true,
              backgroundColor: 'rgba(75, 192, 192, 0.3)',
              borderColor: 'rgba(75, 192, 192, 0.5)'
            }
          },
          limits: {
            x: {min: 'original', max: 'original'}
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: value => formatarMoeda(value)
          }
        }
      }
    }
  });
};

// Renderizar gráfico de quantidade por produto e mês
const renderizarGraficoQtdProdutoMes = (datasets, meses) => {
  if (!qtdProdutoMesChart.value) return;

  if (chartQtdProdutoMes) {
    chartQtdProdutoMes.destroy();
  }

  const ctx = qtdProdutoMesChart.value.getContext('2d');
  if (!ctx) return;
  
  chartQtdProdutoMes = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: meses,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => `Quantidade: ${context.raw}`
          }
        },
        title: {
          display: true,
          text: 'Quantidade por Produto e Mês'
        },
        legend: {
          display: true,
          position: 'top'
        },
        zoom: {
          pan: {
            enabled: true,
            mode: 'x'
          },
          zoom: {
            wheel: {
              enabled: true,
              speed: 0.05
            },
            pinch: {
              enabled: true
            },
            mode: 'x',
            drag: {
              enabled: true,
              backgroundColor: 'rgba(255, 99, 132, 0.3)',
              borderColor: 'rgba(255, 99, 132, 0.5)'
            }
          },
          limits: {
            x: {min: 'original', max: 'original'}
          }
        }
      },
      scales: {
        x: {
          stacked: false,
        },
        y: {
          stacked: false,
          beginAtZero: true
        }
      }
    }
  });
};

// Renderizar gráfico de vendas por estado e mês
const renderizarGraficoVendasEstadoMes = (datasets, meses) => {
  if (!vendasEstadoMesChart.value) return;

  if (chartVendasEstadoMes) {
    chartVendasEstadoMes.destroy();
  }

  const ctx = vendasEstadoMesChart.value.getContext('2d');
  if (!ctx) return;
  
  // Se temos múltiplas regiões selecionadas, adicione legenda para identificação
  const titulo = regioesSelecionadas.value.length > 1 
    ? 'Vendas por Estado/Região e Mês' 
    : 'Vendas por Estado e Mês';
  
  chartVendasEstadoMes = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: meses,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => {
              const dataset = context.dataset;
              return `${dataset.label}: ${formatarMoeda(context.raw)}`;
            }
          }
        },
        title: {
          display: true,
          text: titulo
        },
        legend: {
          display: true,
          position: 'top'
        },
        zoom: {
          pan: {
            enabled: true,
            mode: 'x'
          },
          zoom: {
            wheel: {
              enabled: true,
              speed: 0.05
            },
            pinch: {
              enabled: true
            },
            mode: 'x',
            drag: {
              enabled: true,
              backgroundColor: 'rgba(153, 102, 255, 0.3)',
              borderColor: 'rgba(153, 102, 255, 0.5)'
            }
          },
          limits: {
            x: {min: 'original', max: 'original'}
          }
        }
      },
      scales: {
        x: {
          stacked: false,
        },
        y: {
          stacked: false,
          beginAtZero: true,
          ticks: {
            callback: value => formatarMoeda(value)
          }
        }
      }
    }
  });
};

// Função para renderizar o gráfico de lucro e receita por produto
const renderizarGraficoLucroReceita = (lucroProduto, vendasProduto) => {
  if (!lucroReceitaChart.value) return;
  
  const produtos = Object.keys(vendasProduto);
  const valoresVenda = produtos.map(produto => vendasProduto[produto]);
  const valoresLucro = produtos.map(produto => lucroProduto[produto]);

  if (chartLucroReceita) {
    chartLucroReceita.destroy();
  }

  const ctx = lucroReceitaChart.value.getContext('2d');
  if (!ctx) return;
  
  chartLucroReceita = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: produtos,
      datasets: [
        {
          label: 'Receita Total (R$)',
          data: valoresVenda,
          backgroundColor: 'rgba(54, 162, 235, 0.7)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        },
        {
          label: 'Lucro (R$)',
          data: valoresLucro,
          backgroundColor: 'rgba(75, 192, 92, 0.7)',
          borderColor: 'rgba(75, 192, 92, 1)',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => `${context.dataset.label}: ${formatarMoeda(context.raw)}`
          }
        },
        title: {
          display: true,
          text: 'Comparação de Receita e Lucro por Produto'
        },
        legend: {
          display: true,
          position: 'top'
        },
        zoom: {
          pan: {
            enabled: true,
            mode: 'x'
          },
          zoom: {
            wheel: {
              enabled: true,
              speed: 0.05
            },
            pinch: {
              enabled: true
            },
            mode: 'x',
            drag: {
              enabled: true,
              backgroundColor: 'rgba(54, 162, 235, 0.3)',
              borderColor: 'rgba(54, 162, 235, 0.5)'
            }
          },
          limits: {
            x: {min: 'original', max: 'original'}
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: value => formatarMoeda(value)
          }
        }
      }
    }
  });
};

// Funções auxiliares para formatação
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', { 
    style: 'currency', 
    currency: 'BRL' 
  }).format(valor);
};

const formatarData = (data) => {
  if (!data) return '';
  
  try {
    const dataObj = new Date(data);
    return dataObj.toLocaleDateString('pt-BR');
  } catch (e) {
    console.error('Erro ao formatar data:', e);
    return data;
  }
};

// Limpar mapa ao fechar o relatório
const fecharRelatorio = () => {
  console.log('Fechando relatório e limpando gráficos');
  limparGraficos();
  emit('fechar');
};

// Função para limpar os gráficos
const limparGraficos = () => {
  console.log('Limpando instâncias de gráficos');
  if (chartVendasProduto) {
    chartVendasProduto.destroy();
    chartVendasProduto = null;
  }
  if (chartVendasEstado) {
    chartVendasEstado.destroy();
    chartVendasEstado = null;
  }
  if (chartQtdProdutoMes) {
    chartQtdProdutoMes.destroy();
    chartQtdProdutoMes = null;
  }
  if (chartVendasEstadoMes) {
    chartVendasEstadoMes.destroy();
    chartVendasEstadoMes = null;
  }
  if (chartLucroReceita) {
    chartLucroReceita.destroy();
    chartLucroReceita = null;
  }
};

// Função para resetar zoom de um gráfico específico
const resetarZoom = (tipoGrafico) => {
  if (tipoGrafico === 'vendasProduto' && chartVendasProduto) {
    chartVendasProduto.resetZoom();
  } else if (tipoGrafico === 'vendasEstado' && chartVendasEstado) {
    chartVendasEstado.resetZoom();
  } else if (tipoGrafico === 'qtdProdutoMes' && chartQtdProdutoMes) {
    chartQtdProdutoMes.resetZoom();
  } else if (tipoGrafico === 'vendasEstadoMes' && chartVendasEstadoMes) {
    chartVendasEstadoMes.resetZoom();
  } else if (tipoGrafico === 'lucroReceita' && chartLucroReceita) {
    chartLucroReceita.resetZoom();
  }
};

// Observar mudanças nas regiões selecionadas
watch(() => props.regioes, (novasRegioes) => {
  if (novasRegioes && novasRegioes.length > 0 && props.mostrar) {
    carregarDados();
  }
}, { deep: true });

// Observar mudanças na visibilidade
watch(() => props.mostrar, (mostrar) => {
  if (mostrar && props.regioes && props.regioes.length > 0) {
    carregarDados();
  }
});

// Ao montar o componente
onMounted(() => {
  if (props.mostrar && props.regioes && props.regioes.length > 0) {
    carregarDados();
  }
});

// Limpar os gráficos antes do componente ser desmontado
onBeforeUnmount(() => {
  console.log('Componente sendo desmontado, limpando gráficos');
  limparGraficos();
});

// Função para exportar dados para CSV (que pode ser aberto no Excel)
const exportarParaCSV = () => {
  if (!dadosVendas.value || !dadosVendas.value.dados_tabela) {
    console.error('Sem dados para exportar');
    return;
  }
  
  try {
    // Cabeçalhos da tabela
    const cabecalhos = [
      'Data', 'Cliente', 'Estado', 'Região', 'Produto', 
      'Quantidade', 'Valor Unitário', 'Valor Total', 'Lucro'
    ];
    
    // Dados formatados
    const linhas = dadosVendas.value.dados_tabela.map(item => [
      formatarData(item.Data),
      item.Cliente,
      item.Estado || getEstadoNome(item),
      item.Regiao,
      item.Produto,
      item.Quantidade || 1,
      formatarMoedaSemSimbolo(item.Valor_Unitario || (item.Valor / (item.Quantidade || 1))),
      formatarMoedaSemSimbolo(item.Valor),
      formatarMoedaSemSimbolo(item.Lucro || 0)
    ]);
    
    // Funções auxiliares para formatação
    function formatarMoedaSemSimbolo(valor) {
      return valor.toFixed(2).replace('.', ',');
    }
    
    // Criar conteúdo CSV
    let csvContent = cabecalhos.join(';') + '\n';
    linhas.forEach(linha => {
      csvContent += linha.join(';') + '\n';
    });
    
    // Adicionar BOM para garantir que caracteres especiais sejam exibidos corretamente
    const BOM = '\uFEFF';
    csvContent = BOM + csvContent;
    
    // Criar blob e link para download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    // Configurar link
    link.setAttribute('href', url);
    link.setAttribute('download', `relatorio_vendas_${regioesSelecionadas.value.join('_')}_${new Date().toISOString().slice(0, 10)}.csv`);
    link.style.display = 'none';
    
    // Adicionar ao DOM, clicar e remover
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    console.log('Arquivo CSV gerado com sucesso');
  } catch (error) {
    console.error('Erro ao exportar para CSV:', error);
  }
};

// Função para formatar moeda sem o símbolo - para uso na exportação
const formatarMoedaSemSimbolo = (valor) => {
  if (valor === undefined || valor === null) return '0,00';
  return valor.toFixed(2).replace('.', ',');
};
</script>

<template>
  <div class="relatorio-container" v-if="mostrar">
    <div class="relatorio-content">
      <div class="relatorio-header">
        <h2>Relatório de Vendas: {{ tituloRegioes }}</h2>
        <button class="fechar-btn" @click="fecharRelatorio">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      
      <div v-if="carregando" class="loading-container">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Carregando...</span>
        </div>
        <p>Carregando dados...</p>
      </div>
      
      <div v-else-if="erro" class="error-container">
        <i class="bi bi-exclamation-triangle-fill text-danger" style="font-size: 48px;"></i>
        <p class="text-danger">{{ erro }}</p>
      </div>
      
      <div v-else-if="dadosVendas && dadosVendas.dados_tabela && dadosVendas.dados_tabela.length > 0">
        <!-- Regiões selecionadas -->
        <div class="regioes-selecionadas" v-if="regioesSelecionadas.length > 1">
          <h4>Regiões incluídas neste relatório:</h4>
          <div class="regioes-tags">
            <span v-for="regiao in regioesSelecionadas" :key="regiao" class="regiao-tag">
              {{ regiao }}
            </span>
          </div>
          </div>
          
        <!-- Visualizações gráficas -->
        <div class="charts-container">
          <!-- Gráfico de Vendas por Produto -->
          <div class="chart-container">
            <h4>Vendas por Produto</h4>
            <div class="chart-wrapper">
              <canvas ref="vendasProdutoChart"></canvas>
              <button class="reset-zoom-btn" @click="resetarZoom('vendasProduto')">
                <i class="bi bi-arrows-angle-expand"></i> Resetar Zoom
              </button>
            </div>
            <div class="chart-info">Use a roda do mouse para zoom ou arraste para selecionar uma área</div>
          </div>
          
          <!-- Gráfico de Vendas por Estado -->
          <div class="chart-container">
            <h4>{{ regioesSelecionadas.length > 1 ? 'Vendas por Estado/Região' : 'Vendas por Estado' }}</h4>
            <div class="chart-wrapper">
              <canvas ref="vendasEstadoChart"></canvas>
              <button class="reset-zoom-btn" @click="resetarZoom('vendasEstado')">
                <i class="bi bi-arrows-angle-expand"></i> Resetar Zoom
              </button>
            </div>
            <div class="chart-info">Use a roda do mouse para zoom ou arraste para selecionar uma área</div>
          </div>
          
          <!-- Gráfico de Quantidade por Produto e Mês -->
          <div class="chart-container">
            <h4>Quantidade por Produto e Mês</h4>
            <div class="chart-wrapper">
              <canvas ref="qtdProdutoMesChart"></canvas>
              <button class="reset-zoom-btn" @click="resetarZoom('qtdProdutoMes')">
                <i class="bi bi-arrows-angle-expand"></i> Resetar Zoom
              </button>
          </div>
            <div class="chart-info">Use a roda do mouse para zoom ou arraste para selecionar uma área</div>
        </div>
        
          <!-- Gráfico de Vendas por Estado e Mês -->
          <div class="chart-container">
            <h4>{{ regioesSelecionadas.length > 1 ? 'Vendas por Estado/Região e Mês' : 'Vendas por Estado e Mês' }}</h4>
            <div class="chart-wrapper">
              <canvas ref="vendasEstadoMesChart"></canvas>
              <button class="reset-zoom-btn" @click="resetarZoom('vendasEstadoMes')">
                <i class="bi bi-arrows-angle-expand"></i> Resetar Zoom
              </button>
            </div>
            <div class="chart-info">Use a roda do mouse para zoom ou arraste para selecionar uma área</div>
          </div>
          
          <!-- Gráfico de Lucro e Receita por Produto -->
          <div class="chart-container">
            <h4>Lucro e Receita por Produto</h4>
            <div class="chart-wrapper">
              <canvas ref="lucroReceitaChart"></canvas>
              <button class="reset-zoom-btn" @click="resetarZoom('lucroReceita')">
                <i class="bi bi-arrows-angle-expand"></i> Resetar Zoom
              </button>
            </div>
            <div class="chart-info">Use a roda do mouse para zoom ou arraste para selecionar uma área</div>
          </div>
        </div>
        
        <!-- Barra de Ações -->
        <div class="acoes-bar">
          <div class="acoes-left">
            <button class="btn-exportar" @click="exportarParaCSV">
              <i class="fas fa-file-export"></i> Exportar para Excel
            </button>
          </div>
        </div>
        
        <!-- Resumo em Cards -->
        <div class="resumo-cards" v-if="dadosVendas && dadosVendas.resumo">
          <div class="card-resumo">
            <div class="card-icon">
              <i class="bi bi-cash-coin"></i>
            </div>
            <div class="card-content">
              <h5>Receita Total</h5>
              <p class="valor">{{ formatarMoeda(dadosVendas.resumo.total_vendas) }}</p>
            </div>
          </div>
          
          <div class="card-resumo">
            <div class="card-icon card-icon-lucro">
              <i class="bi bi-graph-up-arrow"></i>
            </div>
            <div class="card-content">
              <h5>Lucro Total</h5>
              <p class="valor">{{ formatarMoeda(dadosVendas.resumo.total_lucro) }}</p>
            </div>
          </div>
          
          <div class="card-resumo">
            <div class="card-icon card-icon-margem">
              <i class="bi bi-percent"></i>
            </div>
            <div class="card-content">
              <h5>Margem de Lucro</h5>
              <p class="valor">{{ dadosVendas.resumo.margem_lucro.toFixed(2) }}%</p>
            </div>
          </div>
          
          <div class="card-resumo">
            <div class="card-icon card-icon-produtos">
              <i class="bi bi-box-seam"></i>
            </div>
            <div class="card-content">
              <h5>Produtos Vendidos</h5>
              <p class="valor">{{ dadosVendas.resumo.total_produtos }}</p>
            </div>
          </div>
          
          <div class="card-resumo">
            <div class="card-icon card-icon-clientes">
              <i class="bi bi-people"></i>
            </div>
            <div class="card-content">
              <h5>Clientes Atendidos</h5>
              <p class="valor">{{ dadosVendas.resumo.num_clientes }}</p>
            </div>
          </div>
        </div>
        
        <!-- Tabela de dados -->
        <h4 class="mt-4">Dados Detalhados</h4>
        <div class="table-responsive">
          <table class="data-table">
              <thead>
                <tr>
                <th>Data</th>
                <th>Região</th>
                <th>Estado</th>
                <th>Produto</th>
                <th>Quantidade</th>
                <th>Valor Unit.</th>
                <th>Valor Total</th>
                <th>Lucro</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in dadosVendas.dados_tabela" :key="index">
                <td>{{ formatarData(item.Data) }}</td>
                <td>{{ item.Regiao }}</td>
                <td>{{ item.Estado_Nome || getEstadoNome(item.Estado) }}</td>
                <td>{{ item.Produto }}</td>
                <td>{{ item.Quantidade }}</td>
                <td>{{ formatarMoeda(item.Valor_Unitario) }}</td>
                <td>{{ formatarMoeda(item.Valor) }}</td>
                <td>{{ formatarMoeda(item.Lucro) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
      <div v-else-if="dadosVendas" class="no-data-container">
        <i class="bi bi-exclamation-circle text-warning" style="font-size: 48px;"></i>
        <p>Não foram encontrados dados para as regiões selecionadas.</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.relatorio-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: white;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.relatorio-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: white;
}

.relatorio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 10;
}

.relatorio-header h2 {
  margin: 0;
  color: #2c3e50;
}

.fechar-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #333;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.fechar-btn:hover {
  color: #e74c3c;
}

.regioes-selecionadas {
  margin-bottom: 20px;
  background-color: #f8f9fa;
  border-radius: 5px;
  padding: 10px 15px;
}

.regioes-selecionadas h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
}

.regioes-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.regiao-tag {
  display: inline-block;
  background-color: #3498db;
  color: white;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: 600;
}

.loading-container, .error-container, .no-data-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  flex-direction: column;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top: 4px solid #3498db;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-top: 20px;
  width: 100%;
}

.chart-container {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  height: 400px;
  position: relative;
  display: flex;
  flex-direction: column;
}

.chart-container h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.chart-wrapper {
  height: 320px;
  width: 100%;
  position: relative;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  font-size: 14px;
}

.data-table th, .data-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.data-table th {
  background-color: #f2f2f2;
  font-weight: bold;
}

.data-table tr:nth-child(even) {
  background-color: #f9f9f9;
}

.reset-zoom-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 5px 10px;
  font-size: 12px;
  cursor: pointer;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 5px;
}

.reset-zoom-btn:hover {
  background-color: #e9ecef;
}

.chart-info {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
  text-align: center;
}

/* Estilo adicional para evitar scroll abaixo do gráfico */
canvas {
  display: block;
  max-width: 100%;
  max-height: 100%;
}

.table-responsive {
  width: 100%;
  overflow-x: auto;
  margin-top: 20px;
}

.resumo-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 25px;
}

.card-resumo {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 3px 10px rgba(0,0,0,0.1);
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-icon {
  width: 50px;
  height: 50px;
  background-color: rgba(54, 162, 235, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: rgba(54, 162, 235, 1);
}

.card-icon-lucro {
  background-color: rgba(75, 192, 92, 0.2);
  color: rgba(75, 192, 92, 1);
}

.card-icon-margem {
  background-color: rgba(255, 159, 64, 0.2);
  color: rgba(255, 159, 64, 1);
}

.card-icon-produtos {
  background-color: rgba(153, 102, 255, 0.2);
  color: rgba(153, 102, 255, 1);
}

.card-icon-clientes {
  background-color: rgba(255, 99, 132, 0.2);
  color: rgba(255, 99, 132, 1);
}

.card-content {
  flex: 1;
}

.card-content h5 {
  margin: 0;
  font-size: 14px;
  color: #666;
  font-weight: 600;
}

.card-content .valor {
  margin: 5px 0 0 0;
  font-size: 18px;
  font-weight: 700;
  color: #333;
}

@media (max-width: 768px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .relatorio-content {
    width: 95%;
    max-height: 95vh;
    padding: 15px;
  }
  
  .chart-container {
    height: 350px;
  }
  
  .chart-wrapper {
    height: 270px;
  }
}

.mapa-container {
  grid-column: 1 / -1;
  margin-top: 20px;
}

.mapa-wrapper {
  width: 100%;
  height: 400px;
  background-color: #f8f9fa;
  border-radius: 5px;
  position: relative;
  overflow: hidden;
}

.mapa-info {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background-color: rgba(255, 255, 255, 0.9);
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.acoes-bar {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin: 20px 0;
  padding: 10px 15px;
  background-color: #f8f9fa;
  border-radius: 5px;
  border: 1px solid #e9ecef;
}

.acoes-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-exportar {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 5px;
  height: 32px;
  background-color: #27ae60;
  color: white;
}

.btn-exportar:hover {
  background-color: #2ecc71;
}
</style> 