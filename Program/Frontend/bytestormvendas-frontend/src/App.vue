<script setup>
import { ref } from 'vue';
import BrazilMap from './components/BrazilMap.vue';
import ChatView from './components/ChatView.vue';
import AppSidebar from './components/AppSidebar.vue';
import RelatorioVendas from './components/RelatorioVendas.vue';

// Estado da aplicação
const activeView = ref('chat');
const isSidebarOpen = ref(false);
const mostrarRelatorio = ref(false);
const regioesSelecionadas = ref([]);
const loading = ref(false);

// Manipuladores de eventos
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

const changeView = (view) => {
  activeView.value = view;
};

const abrirRelatorio = (regioes) => {
  regioesSelecionadas.value = regioes;
  mostrarRelatorio.value = true;
};

const fecharRelatorio = () => {
  mostrarRelatorio.value = false;
  regioesSelecionadas.value = [];
};

// Função para atualizar o estado de loading
const updateLoading = (value) => {
  loading.value = value;
};
</script>

<template>
  <div class="app-container">
   
    
    <!-- Barra Lateral -->
    <AppSidebar 
      :is-sidebar-open="isSidebarOpen"
      :active-view="activeView"
      :loading="loading"
      @toggle-sidebar="toggleSidebar"
      @change-view="changeView"
    />

    <!-- Conteúdo Principal -->
    <div class="main-content" :class="{ 'content-shifted': isSidebarOpen }">
      <!-- Chat View -->
      <ChatView v-if="activeView === 'chat'" v-model="loading" />

      <!-- Mapa View -->
      <BrazilMap v-if="activeView === 'map'" @regiao-selecionada="abrirRelatorio" />

      <RelatorioVendas 
        :mostrar="mostrarRelatorio" 
        :regioes-selecionadas="regioesSelecionadas"
        @fechar="fecharRelatorio" 
      />
    </div>
    
  </div>
</template>

<style scoped>
.app-container {
  position: relative;
  min-height: 100vh;
}

.main-content {
  padding: 20px;
  transition: margin-left 0.3s ease;
}

.content-shifted {
  margin-left: 250px;
}

@media (max-width: 768px) {
  .content-shifted {
    margin-left: 0;
  }
}

.header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.header h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1rem;
  opacity: 0.9;
}

.footer {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  text-align: center;
  margin-top: auto;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  font-size: 0.9rem;
}

@media (max-width: 992px) {
  .header h1 {
    font-size: 1.75rem;
  }
  
  .main-content {
    padding: 1rem;
  }
}

@media (max-width: 576px) {
  .header h1 {
    font-size: 1.5rem;
  }
  
  .main-content {
    padding: 0.75rem;
  }
}

.destaque {
  font-weight: bold;
  color: #3498db;
}
</style>