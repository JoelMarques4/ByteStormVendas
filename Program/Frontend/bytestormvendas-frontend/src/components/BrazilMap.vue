<script setup>
import { ref, onMounted } from 'vue';
import RelatorioVendas from './RelatorioVendas.vue';

const selectedRegions = ref([]);
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

// Cores para cada região
const regionColors = {
  Norte: '#3498db',
  Nordeste: '#e74c3c',
  CentroOeste: '#2ecc71',
  Sudeste: '#f39c12',
  Sul: '#9b59b6'
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

// Função para alternar a seleção de uma região
const toggleRegion = (region) => {
  const index = selectedRegions.value.indexOf(region);
  if (index === -1) {
    // Se a região não está selecionada, adicione-a
    selectedRegions.value.push(region);
  } else {
    // Se a região já está selecionada, remova-a
    selectedRegions.value.splice(index, 1);
  }
  updateMapColors();
};

// Função para verificar se uma região está selecionada
const isRegionSelected = (region) => {
  return selectedRegions.value.includes(region);
};

// Função para selecionar todas as regiões
const selectAllRegions = () => {
  selectedRegions.value = Object.keys(regions);
  updateMapColors();
};

// Função para limpar todas as seleções
const clearAllRegions = () => {
  selectedRegions.value = [];
  updateMapColors();
};

// Função para abrir o relatório
const abrirRelatorio = () => {
  if (selectedRegions.value.length > 0) {
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
  
  // Colorimos os estados das regiões selecionadas
  selectedRegions.value.forEach(region => {
    paths.forEach(path => {
      const stateId = path.id;
      if (stateToRegion[stateId] === region) {
        path.setAttribute('fill', regionColors[region]);
      }
    });
  });
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
            toggleRegion(region);
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
    
    <!-- Seletor de regiões -->
    <div class="region-selector">
      <div class="selector-header">
        <h3>Selecione as regiões para o relatório</h3>
        <div class="selector-actions">
          <button class="btn-selector" @click="selectAllRegions">Selecionar Todas</button>
          <button class="btn-selector" @click="clearAllRegions">Limpar Seleção</button>
        </div>
      </div>
      <div class="region-checkboxes">
        <div v-for="(states, region) in regions" :key="region" class="region-checkbox">
          <label :style="{ borderColor: regionColors[region] }">
            <input 
              type="checkbox" 
              :checked="isRegionSelected(region)" 
              @change="toggleRegion(region)"
            />
            <span :style="{ backgroundColor: isRegionSelected(region) ? regionColors[region] : 'transparent' }">{{ region }}</span>
          </label>
        </div>
      </div>
    </div>
    
    <div class="map-wrapper">
      <div id="map-container" class="brazil-map"></div>
      <div v-if="!mapLoaded" class="loading">Carregando mapa...</div>
    </div>
    
    <div class="region-info" v-if="selectedRegions.length > 0">
      <h3>Regiões Selecionadas: {{ selectedRegions.length }}</h3>
      <div class="selected-regions">
        <div v-for="region in selectedRegions" :key="region" class="selected-region">
          <div class="region-tag" :style="{ backgroundColor: regionColors[region] }">
            {{ region }}
          </div>
          <div class="states-list">
            <ul>
              <li v-for="state in regions[region]" :key="state">{{ state }}</li>
            </ul>
          </div>
        </div>
      </div>
      <div class="acoes">
        <button class="btn-relatorio" @click="abrirRelatorio" :disabled="selectedRegions.length === 0">
          <i class="bi bi-graph-up"></i> Gerar Relatório de Vendas
        </button>
      </div>
    </div>
    <div class="region-info" v-else>
      <p>Selecione pelo menos uma região no mapa para gerar relatórios de vendas.</p>
    </div>
    
    <!-- Componente de Relatório -->
    <RelatorioVendas 
      :regioes="selectedRegions" 
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

.region-selector {
  width: 100%;
  max-width: 800px;
  margin-bottom: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.selector-header h3 {
  margin: 0;
  font-size: 18px;
}

.selector-actions {
  display: flex;
  gap: 10px;
}

.btn-selector {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.btn-selector:hover {
  background-color: #e0e0e0;
}

.region-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.region-checkbox label {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border: 2px solid;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.region-checkbox label:hover {
  background-color: rgba(0,0,0,0.05);
}

.region-checkbox input {
  display: none;
}

.region-checkbox span {
  color: #333;
  font-weight: 600;
  border-radius: 16px;
  padding: 2px 10px;
  transition: all 0.2s;
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
  max-width: 800px;
  background-color: #f9f9f9;
}

.selected-regions {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 15px;
}

.selected-region {
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.region-tag {
  padding: 5px 10px;
  border-radius: 4px;
  color: white;
  font-weight: bold;
  min-width: 100px;
  text-align: center;
}

.states-list {
  flex: 1;
}

.states-list ul {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 5px;
  padding-left: 20px;
  margin: 0;
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

.btn-relatorio:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .selector-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .selected-region {
    flex-direction: column;
  }
  
  .region-tag {
    width: 100%;
  }
}
</style> 