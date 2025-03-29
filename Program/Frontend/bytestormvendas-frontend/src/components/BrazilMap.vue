<script setup>
import { ref, onMounted } from 'vue';
import RelatorioVendas from './RelatorioVendas.vue';

const selectedRegion = ref(null);
const mapLoaded = ref(false);
const showRelatorio = ref(false);

// Definição das regiões e seus estados
const regions = {
  Norte: ['Acre', 'Amapá', 'Amazonas', 'Pará', 'Rondônia', 'Roraima', 'Tocantins'],
  Nordeste: ['Alagoas', 'Bahia', 'Ceará', 'Maranhão', 'Paraíba', 'Pernambuco', 'Piauí', 'Rio Grande do Norte', 'Sergipe'],
  CentroOeste: ['Distrito Federal', 'Goiás', 'Mato Grosso', 'Mato Grosso do Sul'],
  Sudeste: ['Espírito Santo', 'Minas Gerais', 'Rio de Janeiro', 'São Paulo'],
  Sul: ['Paraná', 'Rio Grande do Sul', 'Santa Catarina']
};

// Mapeamento de estados para regiões
const stateToRegion = {
  'BR-AC': 'Norte', 'BR-AP': 'Norte', 'BR-AM': 'Norte', 'BR-PA': 'Norte', 
  'BR-RO': 'Norte', 'BR-RR': 'Norte', 'BR-TO': 'Norte',
  'BR-AL': 'Nordeste', 'BR-BA': 'Nordeste', 'BR-CE': 'Nordeste', 
  'BR-MA': 'Nordeste', 'BR-PB': 'Nordeste', 'BR-PE': 'Nordeste', 
  'BR-PI': 'Nordeste', 'BR-RN': 'Nordeste', 'BR-SE': 'Nordeste',
  'BR-DF': 'CentroOeste', 'BR-GO': 'CentroOeste', 
  'BR-MT': 'CentroOeste', 'BR-MS': 'CentroOeste',
  'BR-ES': 'Sudeste', 'BR-MG': 'Sudeste', 'BR-RJ': 'Sudeste', 'BR-SP': 'Sudeste',
  'BR-PR': 'Sul', 'BR-RS': 'Sul', 'BR-SC': 'Sul'
};

// Função para selecionar uma região
const selectRegion = (region) => {
  selectedRegion.value = region;
  updateMapColors();
};

// Função para abrir o relatório
const abrirRelatorio = () => {
  if (selectedRegion.value) {
    showRelatorio.value = true;
  }
};

// Função para fechar o relatório
const fecharRelatorio = () => {
  showRelatorio.value = false;
};

// Função para atualizar as cores do mapa
const updateMapColors = () => {
  const mapContainer = document.getElementById('map-container');
  if (!mapContainer) return;
  
  // Primeiro, resetamos todas as cores para branco
  const paths = mapContainer.querySelectorAll('path');
  paths.forEach(path => {
    path.setAttribute('fill', '#FFFFFF');
  });
  
  // Se uma região está selecionada, colorimos seus estados
  if (selectedRegion.value) {
    paths.forEach(path => {
      const stateId = path.id;
      if (stateToRegion[stateId] === selectedRegion.value) {
        path.setAttribute('fill', '#3498db');
      }
    });
  }
};

// Carrega o SVG e adiciona interatividade
const loadMap = async () => {
  try {
    const response = await fetch('/src/assets/brazil.svg');
    const svgText = await response.text();
    
    const mapContainer = document.getElementById('map-container');
    if (mapContainer) {
      mapContainer.innerHTML = svgText;
      
      // Adiciona estilos e eventos aos paths
      const paths = mapContainer.querySelectorAll('path');
      paths.forEach(path => {
        // Adiciona evento de clique
        path.addEventListener('click', (event) => {
          const stateId = event.currentTarget.id;
          const region = stateToRegion[stateId];
          
          if (region) {
            selectRegion(region);
          }
        });
        
        // Adiciona estilos de hover
        path.style.transition = 'fill 0.3s ease';
        path.style.stroke = '#333';
        path.style.strokeWidth = '0.5';
        path.style.cursor = 'pointer';
      });
      
      mapLoaded.value = true;
      updateMapColors();
    }
  } catch (error) {
    console.error('Erro ao carregar o mapa:', error);
  }
};

onMounted(() => {
  loadMap();
});
</script>

<template>
  <div class="map-container">
    <h2>Mapa do Brasil</h2>
    <div class="map-wrapper">
      <div id="map-container" class="brazil-map"></div>
      <div v-if="!mapLoaded" class="loading">Carregando mapa...</div>
    </div>
    <div class="region-info" v-if="selectedRegion">
      <h3>Região {{ selectedRegion }}</h3>
      <div class="states-list">
        <p><strong>Estados:</strong></p>
        <ul>
          <li v-for="state in regions[selectedRegion]" :key="state">{{ state }}</li>
        </ul>
      </div>
      <div class="acoes">
        <button class="btn-relatorio" @click="abrirRelatorio">
          <i class="bi bi-graph-up"></i> Gerar Relatório de Vendas
        </button>
      </div>
    </div>
    <div class="region-info" v-else>
      <p>Selecione uma região no mapa para visualizar detalhes e gerar relatórios de vendas.</p>
    </div>
    
    <!-- Componente de Relatório -->
    <RelatorioVendas 
      :regiao="selectedRegion" 
      :mostrar="showRelatorio" 
      @fechar="fecharRelatorio" 
    />
  </div>
</template>

<style scoped>
.map-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.map-wrapper {
  width: 100%;
  max-width: 800px;
  margin: 20px 0;
  position: relative;
}

.brazil-map {
  width: 100%;
  height: auto;
}

.loading {
  text-align: center;
  margin: 20px 0;
  font-style: italic;
  color: #666;
}

:deep(path) {
  transition: fill 0.3s ease;
  stroke: #333;
  stroke-width: 0.5;
  cursor: pointer;
}

:deep(path:hover) {
  fill: #e0e0e0 !important;
}

.region-info {
  margin-top: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  width: 100%;
  max-width: 600px;
  background-color: #f9f9f9;
}

.states-list ul {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 5px;
  padding-left: 20px;
}

.acoes {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.btn-relatorio {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-relatorio:hover {
  background-color: #2980b9;
}
</style> 