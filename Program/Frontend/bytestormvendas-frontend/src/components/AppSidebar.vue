<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  isSidebarOpen: {
    type: Boolean,
    required: true
  },
  activeView: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['toggle-sidebar', 'change-view']);

const toggleSidebar = () => {
  emit('toggle-sidebar');
};

const changeView = (view) => {
  emit('change-view', view);
  
  if (window.innerWidth < 768) {
    toggleSidebar();
  }
};
</script>

<template>
  <div class="sidebar-wrapper">
    <!-- Botão do Menu Hamburguer -->
    <button class="menu-toggle" @click="toggleSidebar">
      <i class="bi bi-list"></i>
    </button>

    <!-- Barra Lateral -->
    <div class="sidebar" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="sidebar-header">
        <h3>ByteStorm Vendas</h3>
        <button class="close-sidebar" @click="toggleSidebar">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      <div class="sidebar-menu">
        <button 
          class="menu-item" 
          :class="{ active: activeView === 'chat' }"
          @click="changeView('chat')">
          <i class="bi bi-chat-dots"></i> Chat
        </button>
        <button 
          class="menu-item" 
          :class="{ active: activeView === 'map' }"
          @click="changeView('map')">
          <i class="bi bi-geo-alt"></i> Mapa do Brasil
        </button>
      </div>
    </div>

    <!-- Overlay para fechar o menu em telas pequenas -->
    <div v-if="isSidebarOpen" class="sidebar-overlay" @click="toggleSidebar"></div>
  </div>
</template>

<style scoped>
.menu-toggle {
  position: fixed;
  top: 20px;
  left: 20px;
  z-index: 1000;
  background: none;
  border: none;
  font-size: 24px;
  color: #2c3e50;
  cursor: pointer;
  padding: 10px;
  border-radius: 5px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sidebar {
  width: 250px;
  height: 100vh;
  background-color: #2c3e50;
  color: white;
  padding: 20px;
  position: fixed;
  left: -250px;
  top: 0;
  transition: left 0.3s ease;
  z-index: 1001;
}

.sidebar-open {
  left: 0;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.close-sidebar {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 5px;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.menu-item {
  background: none;
  border: none;
  color: white;
  padding: 10px;
  text-align: left;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  gap: 10px;
}

.menu-item:hover {
  background-color: #34495e;
}

.menu-item.active {
  background-color: #3498db;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}
</style> 