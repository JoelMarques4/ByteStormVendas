<script setup>
import { ref } from 'vue';
import BrazilMap from './components/BrazilMap.vue';
import ChatView from './components/ChatView.vue';
import AppSidebar from './components/AppSidebar.vue';

// Estado da aplicação
const activeView = ref('chat');
const isSidebarOpen = ref(false);

// Manipuladores de eventos
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

const changeView = (view) => {
  activeView.value = view;
};
</script>

<template>
  <div class="app-container">
    <!-- Barra Lateral -->
    <AppSidebar 
      :isSidebarOpen="isSidebarOpen" 
      :activeView="activeView"
      @toggle-sidebar="toggleSidebar"
      @change-view="changeView"
    />

    <!-- Conteúdo Principal -->
    <div class="main-content" :class="{ 'content-shifted': isSidebarOpen }">
      <!-- Chat View -->
      <ChatView v-if="activeView === 'chat'" />

      <!-- Mapa View -->
      <BrazilMap v-if="activeView === 'map'" />
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
</style>