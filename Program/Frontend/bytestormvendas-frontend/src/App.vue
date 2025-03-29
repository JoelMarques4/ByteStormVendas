<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import BrazilMap from './components/BrazilMap.vue';

const API_URL = 'http://localhost:8000/api/query';
const loading = ref(false);
const message = ref('');
const chatHistory = ref([]);
const userInput = ref('');
const activeView = ref('chat');
const selectedRegion = ref(null);
const isSidebarOpen = ref(false);

// Função para processar a resposta do JSON
const processResponse = (response) => {
  try {
    // Se a resposta for uma string, tenta fazer o parse
    if (typeof response === 'string') {
      response = JSON.parse(response);
    }
    
    // Se a resposta tiver uma propriedade 'response', usa ela
    if (response.response) {
      // Se response.response for um objeto, procura pelo texto
      if (typeof response.response === 'object') {
        // Procura por propriedades que podem conter o texto
        if (response.response.text) return response.response.text;
        if (response.response.content) return response.response.content;
        if (response.response.result) return response.response.result;
        if (response.response.output) return response.response.output;
        if (response.response.answer) return response.response.answer;
        
        // Se não encontrar, retorna o objeto formatado
        return JSON.stringify(response.response, null, 2);
      }
      return response.response;
    }
    
    // Se a resposta tiver uma propriedade 'result', usa ela
    if (response.result) {
      return response.result;
    }
    
    // Se a resposta tiver uma propriedade 'message', usa ela
    if (response.message) {
      return response.message;
    }
    
    // Se a resposta tiver uma propriedade 'text', usa ela
    if (response.text) {
      return response.text;
    }
    
    // Se a resposta tiver uma propriedade 'content', usa ela
    if (response.content) {
      return response.content;
    }
    
    // Se a resposta tiver uma propriedade 'output', usa ela
    if (response.output) {
      return response.output;
    }
    
    // Se a resposta tiver uma propriedade 'answer', usa ela
    if (response.answer) {
      return response.answer;
    }
    
    // Se a resposta for um objeto, tenta encontrar o primeiro valor de string
    for (const key in response) {
      if (typeof response[key] === 'string') {
        return response[key];
      }
    }
    
    // Se não encontrar nenhum texto, retorna uma mensagem padrão
    return "Desculpe, não consegui processar a resposta corretamente.";
  } catch (error) {
    console.error('Erro ao processar resposta:', error);
    return "Desculpe, ocorreu um erro ao processar a resposta.";
  }
};

// Enviar mensagem para o Langflow
const sendMessage = async () => {
  if (!userInput.value.trim()) return;
  
  loading.value = true;
  try {
    const response = await axios.post(API_URL, {
      message: userInput.value
    });
    
    // Adicionar mensagem do usuário e resposta ao histórico
    chatHistory.value.push({
      type: 'user',
      content: userInput.value,
      timestamp: new Date()
    });
    
    chatHistory.value.push({
      type: 'assistant',
      content: processResponse(response.data),
      timestamp: new Date()
    });
    
    userInput.value = '';
    message.value = '';
    
    // Rolar para a última mensagem
    setTimeout(() => {
      const chatContainer = document.querySelector('.chat-container');
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }, 100);
  } catch (error) {
    message.value = 'Erro ao enviar mensagem: ' + error.message;
  } finally {
    loading.value = false;
  }
};

// Limpar histórico
const clearHistory = () => {
  chatHistory.value = [];
  message.value = '';
};

// Enviar mensagem com Enter
const handleKeyPress = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
};

// Função para selecionar região
const selectRegion = (region) => {
  selectedRegion.value = region;
};

// Função para alternar o menu
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

// Função para mudar a visualização
const changeView = (view) => {
  activeView.value = view;
  if (window.innerWidth < 768) {
    isSidebarOpen.value = false;
  }
};
</script>

<template>
  <div class="app-container">
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

    <!-- Conteúdo Principal -->
    <div class="main-content" :class="{ 'content-shifted': isSidebarOpen }">
      <!-- Chat View -->
      <div v-if="activeView === 'chat'" class="container">
        <div class="text-center mb-4">
          <h1 class="mb-3">ByteStorm Vendas</h1>
          <p class="lead">Assistente Virtual Inteligente</p>
        </div>

        <!-- Mensagem de alerta -->
        <div v-if="message" class="alert alert-danger" role="alert">
          {{ message }}
          <button type="button" class="btn-close float-end" @click="message = ''"></button>
        </div>

        <!-- Área de chat -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <span>Chat</span>
            <button class="btn btn-sm btn-outline-danger" @click="clearHistory">
              <i class="bi bi-trash"></i> Limpar Histórico
            </button>
          </div>
          <div class="card-body chat-container">
            <div v-if="loading" class="text-center p-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
              </div>
            </div>
            <div v-else-if="chatHistory.length === 0" class="text-center p-3">
              <p>Inicie uma conversa enviando uma mensagem.</p>
            </div>
            <div v-else>
              <div v-for="(message, index) in chatHistory" :key="index" 
                   :class="['chat-message', message.type]">
                <div class="message-content">
                  {{ message.content }}
                </div>
                <small class="message-timestamp">
                  {{ new Date(message.timestamp).toLocaleString() }}
                </small>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <div class="input-group">
              <textarea class="form-control" 
                        v-model="userInput" 
                        @keypress="handleKeyPress"
                        placeholder="Digite sua mensagem..."
                        rows="2"></textarea>
              <button class="btn btn-primary" 
                      @click="sendMessage"
                      :disabled="loading || !userInput.trim()">
                <i class="bi bi-send"></i> Enviar
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Mapa View -->
      <div v-if="activeView === 'map'">
        <BrazilMap />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  position: relative;
  min-height: 100vh;
}

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

.chat-container {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
}

textarea {
  resize: none;
}
</style>