<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';

const props = defineProps({
  regiao: {
    type: String,
    required: true
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

// Função para carregar os dados de vendas da região selecionada
const carregarDados = async () => {
  carregando.value = true;
  erro.value = null;
  
  try {
    console.log(`Carregando dados para a região: ${props.regiao}`);
    // Usar a URL do backend corretamente
    const response = await axios.get(`http://localhost:8000/api/vendas/dados/${props.regiao}`);
    console.log('Dados recebidos:', response.data);
    dadosVendas.value = response.data;
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

// Formatar valor monetário
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', { 
    style: 'currency', 
    currency: 'BRL' 
  }).format(valor);
};

// Observar mudanças na região selecionada
watch(() => props.regiao, (novaRegiao) => {
  if (novaRegiao && props.mostrar) {
    carregarDados();
  }
});

// Observar mudanças na visibilidade
watch(() => props.mostrar, (mostrar) => {
  if (mostrar && props.regiao) {
    carregarDados();
  }
});

// Ao montar o componente
onMounted(() => {
  if (props.mostrar && props.regiao) {
    carregarDados();
  }
});
</script>

<template>
  <div v-if="mostrar" class="relatorio-overlay" @click.self="emit('fechar')">
    <div class="relatorio-container">
      <div class="relatorio-header">
        <h2>Relatório de Vendas: {{ regiao }}</h2>
        <button class="btn-fechar" @click="emit('fechar')">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      
      <div v-if="carregando" class="carregando">
        <div class="spinner"></div>
        <p>Carregando dados...</p>
      </div>
      
      <div v-else-if="erro" class="erro">
        <i class="bi bi-exclamation-triangle"></i>
        <p>{{ erro }}</p>
      </div>
      
      <div v-else-if="dadosVendas" class="relatorio-conteudo">
        <!-- Resumo dos dados -->
        <div class="cards-container">
          <div class="card-info">
            <h3>Total de Vendas</h3>
            <p class="valor">{{ formatarMoeda(dadosVendas.resumo.total_vendas) }}</p>
          </div>
          
          <div class="card-info">
            <h3>Média por Venda</h3>
            <p class="valor">{{ formatarMoeda(dadosVendas.resumo.media_valor) }}</p>
          </div>
          
          <div class="card-info">
            <h3>Produtos Vendidos</h3>
            <p class="valor">{{ dadosVendas.resumo.total_produtos }}</p>
          </div>
          
          <div class="card-info">
            <h3>Clientes Atendidos</h3>
            <p class="valor">{{ dadosVendas.resumo.num_clientes }}</p>
          </div>
        </div>
        
        <!-- Gráficos -->
        <div class="graficos-container">
          <div v-if="dadosVendas.graficos.vendas_por_produto" class="grafico">
            <h3>Vendas por Produto</h3>
            <img :src="dadosVendas.graficos.vendas_por_produto" alt="Gráfico de vendas por produto" />
          </div>
          
          <div v-if="dadosVendas.graficos.quantidade_por_produto" class="grafico">
            <h3>Quantidade por Produto</h3>
            <img :src="dadosVendas.graficos.quantidade_por_produto" alt="Gráfico de quantidade por produto" />
          </div>
          
          <div v-if="dadosVendas.graficos.vendas_por_estado" class="grafico">
            <h3>Vendas por Estado</h3>
            <img :src="dadosVendas.graficos.vendas_por_estado" alt="Gráfico de vendas por estado" />
          </div>
        </div>
        
        <!-- Tabela de dados -->
        <div class="tabela-container">
          <h3>Detalhamento de Vendas</h3>
          <div class="tabela-scroll">
            <table>
              <thead>
                <tr>
                  <th v-for="(value, key) in dadosVendas.dados_tabela[0]" :key="key">
                    {{ key }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in dadosVendas.dados_tabela" :key="index">
                  <td v-for="(value, key) in item" :key="key">
                    {{ key.toLowerCase().includes('valor') ? formatarMoeda(value) : value }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Botões de ação -->
        <div class="acoes">
          <button class="btn-imprimir" @click="window.print()">
            <i class="bi bi-printer"></i> Imprimir Relatório
          </button>
          <button class="btn-fechar" @click="emit('fechar')">
            <i class="bi bi-x"></i> Fechar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.relatorio-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.relatorio-container {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 1200px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.relatorio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ddd;
  padding-bottom: 15px;
  margin-bottom: 20px;
}

.relatorio-header h2 {
  margin: 0;
  color: #2c3e50;
}

.btn-fechar {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.btn-fechar:hover {
  color: #f44336;
}

.carregando, .erro {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #666;
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

.erro {
  color: #f44336;
}

.erro i {
  font-size: 40px;
  margin-bottom: 15px;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.card-info {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-info h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #666;
}

.card-info .valor {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}

.graficos-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.grafico {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.grafico h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  color: #2c3e50;
  text-align: center;
}

.grafico img {
  width: 100%;
  height: auto;
  max-height: 300px;
  object-fit: contain;
}

.tabela-container {
  margin-bottom: 30px;
}

.tabela-container h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 18px;
  color: #2c3e50;
}

.tabela-scroll {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

tr:hover {
  background-color: #f5f5f5;
}

.acoes {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn-imprimir {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-imprimir:hover {
  background-color: #45a049;
}

@media print {
  .relatorio-overlay {
    position: static;
    background-color: white;
  }
  
  .relatorio-container {
    width: 100%;
    max-height: none;
    box-shadow: none;
    padding: 0;
  }
  
  .btn-fechar, .acoes {
    display: none;
  }
}

@media (max-width: 768px) {
  .cards-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .graficos-container {
    grid-template-columns: 1fr;
  }
}
</style> 