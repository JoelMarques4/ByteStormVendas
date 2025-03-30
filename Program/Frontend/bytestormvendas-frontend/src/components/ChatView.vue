<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';
const loading = ref(false);
const message = ref('');
const chatHistory = ref([]);
const userInput = ref('');
const chats = ref([]);
const currentChatId = ref(null);

// Carregar chats ao montar o componente
onMounted(async () => {
  await loadChats();
});

// Carregar lista de chats
const loadChats = async () => {
  try {
    const response = await axios.get(`${API_URL}/chats`);
    chats.value = response.data;
  } catch (error) {
    message.value = 'Erro ao carregar chats: ' + error.message;
  }
};

// Criar novo chat
const createNewChat = async () => {
  try {
    const response = await axios.post(`${API_URL}/chats`);
    currentChatId.value = response.data.chat_id;
    chatHistory.value = [];
    await loadChats();
  } catch (error) {
    message.value = 'Erro ao criar novo chat: ' + error.message;
  }
};

// Carregar mensagens de um chat específico
const loadChatMessages = async (chatId) => {
  try {
    const response = await axios.get(`${API_URL}/chats/${chatId}/messages`);
    chatHistory.value = response.data.map(msg => ({
      ...msg,
      type: msg.sender // Usar o sender como type para manter compatibilidade com o CSS
    }));
    currentChatId.value = chatId;
  } catch (error) {
    message.value = 'Erro ao carregar mensagens: ' + error.message;
  }
};

// Excluir chat
const deleteChat = async (chatId) => {
  if (!confirm('Tem certeza que deseja excluir este chat?')) return;
  
  try {
    await axios.delete(`${API_URL}/chats/${chatId}`);
    if (currentChatId.value === chatId) {
      currentChatId.value = null;
      chatHistory.value = [];
    }
    await loadChats();
  } catch (error) {
    message.value = 'Erro ao excluir chat: ' + error.message;
  }
};

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
        if (response.response.text) return response.response.text.replace(/<think>.*?<\/think>/g, '');
        if (response.response.content) return response.response.content.replace(/<think>.*?<\/think>/g, '');
        if (response.response.result) return response.response.result.replace(/<think>.*?<\/think>/g, '');
        if (response.response.output) return response.response.output.replace(/<think>.*?<\/think>/g, '');
        if (response.response.answer) return response.response.answer.replace(/<think>.*?<\/think>/g, '');
        
        // Se não encontrar, retorna o objeto formatado
        return JSON.stringify(response.response, null, 2);
      }
      return response.response.replace(/<think>.*?<\/think>/g, '');
    }
    
    // Se a resposta tiver uma propriedade 'result', usa ela
    if (response.result) {
      return response.result.replace(/<think>.*?<\/think>/g, '');
    }
    
    // Se a resposta tiver uma propriedade 'message', usa ela
    if (response.message) {
      return response.message.replace(/<think>.*?<\/think>/g, '');
    }
    
    // Se a resposta tiver uma propriedade 'text', usa ela
    if (response.text) {
      return response.text.replace(/<think>.*?<\/think>/g, '');
    }
    
    // Se a resposta tiver uma propriedade 'content', usa ela
    if (response.content) {
      return response.content.replace(/<think>.*?<\/think>/g, '');
    }
    
    // Se a resposta tiver uma propriedade 'output', usa ela
    if (response.output) {
      return response.output.replace(/<think>.*?<\/think>/g, '');
    }
    
    // Se a resposta tiver uma propriedade 'answer', usa ela
    if (response.answer) {
      return response.answer.replace(/<think>.*?<\/think>/g, '');
    }
    
    // Se a resposta for um objeto, tenta encontrar o primeiro valor de string
    for (const key in response) {
      if (typeof response[key] === 'string') {
        return response[key].replace(/<think>.*?<\/think>/g, '');
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
  
  // Se não houver chat atual, criar um novo
  if (!currentChatId.value) {
    await createNewChat();
  }
  
  loading.value = true;
  try {
    // Enviar mensagem para o Langflow
    const response = await axios.post(`${API_URL}/query`, {
      message: userInput.value
    });
    
    // Salvar mensagem do usuário
    await axios.post(`${API_URL}/chats/${currentChatId.value}/messages`, {
      content: userInput.value,
      sender: 'user'
    });
    
    // Salvar resposta do assistente
    await axios.post(`${API_URL}/chats/${currentChatId.value}/messages`, {
      content: processResponse(response.data),
      sender: 'assistant'
    });
    
    // Atualizar histórico local
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
    
    // Atualizar lista de chats
    await loadChats();
    
    // Rolar para a última mensagem
    setTimeout(() => {
      const chatContainer = document.querySelector('.chat-messages');
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

// Enviar mensagem com Enter
const handleKeyPress = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
};
</script>

<template>
  <div class="chat-app">
    <!-- Sidebar com lista de chats -->
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <h2>CodeSellers Vendas</h2>
        <button class="btn-new-chat" @click="createNewChat">
          <i class="bi bi-plus-lg"></i>
          Novo Chat
        </button>
      </div>
      
      <div class="chat-list">
        <div v-for="chat in chats" 
             :key="chat.id"
             class="chat-item"
             :class="{ active: currentChatId === chat.id }"
             @click="loadChatMessages(chat.id)">
          <div class="chat-item-content">
            <i class="bi bi-chat-dots"></i>
            <div class="chat-item-info">
              <div class="chat-item-title">
                Chat #{{ chat.id }}
              </div>
              <div class="chat-item-meta">
                {{ chat.message_count }} mensagens
              </div>
            </div>
          </div>
          <button class="btn-delete" @click.stop="deleteChat(chat.id)">
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Área principal do chat -->
    <div class="chat-main">
      <div class="chat-header">
        <div class="chat-title">
          <i class="bi bi-chat-dots-fill"></i>
          <span v-if="currentChatId">Chat #{{ currentChatId }}</span>
          <span v-else>Selecione um chat ou crie um novo</span>
        </div>
      </div>

      <div class="chat-messages" ref="messagesContainer">
        <div v-if="loading" class="loading-container">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Carregando...</span>
          </div>
        </div>
        <div v-else-if="chatHistory.length === 0" class="empty-state">
          <i class="bi bi-chat-dots"></i>
          <p v-if="currentChatId">Inicie uma conversa enviando uma mensagem.</p>
          <p v-else>Selecione um chat existente ou crie um novo para começar.</p>
        </div>
        <div v-else class="messages-list">
          <div v-for="(message, index) in chatHistory" 
               :key="index" 
               :class="['message-wrapper', message.type]">
            <div class="message">
              <div class="message-content">
                {{ message.content }}
              </div>
              <div class="message-timestamp">
                {{ new Date(message.timestamp).toLocaleString() }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <div class="input-container">
          <textarea 
            class="message-input"
            v-model="userInput"
            @keypress="handleKeyPress"
            placeholder="Digite sua mensagem..."
            rows="1"
            :disabled="!currentChatId"
          ></textarea>
          <button 
            class="send-button"
            @click="sendMessage"
            :disabled="loading || !userInput.trim() || !currentChatId"
          >
            <i class="bi bi-send"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-app {
  display: flex;
  height: 100vh;
  background-color: #ffffff;
}

.chat-sidebar {
  width: 260px;
  background-color: #f7f7f8;
  border-right: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e5e5e5;
}

.sidebar-header h2 {
  font-size: 1.2rem;
  margin-bottom: 16px;
  color: #333;
}

.btn-new-chat {
  width: 100%;
  padding: 8px 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.btn-new-chat:hover {
  background-color: #0056b3;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.chat-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 4px;
}

.chat-item:hover {
  background-color: #e9ecef;
}

.chat-item.active {
  background-color: #e3f2fd;
}

.chat-item-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.chat-item i {
  font-size: 1.2rem;
  color: #666;
}

.chat-item-info {
  flex: 1;
  min-width: 0;
}

.chat-item-title {
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-item-meta {
  font-size: 0.8rem;
  color: #666;
}

.btn-delete {
  padding: 4px 8px;
  background: none;
  border: none;
  color: #dc3545;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.chat-item:hover .btn-delete {
  opacity: 1;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
}

.chat-header {
  padding: 16px;
  border-bottom: 1px solid #e5e5e5;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  color: #333;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  gap: 16px;
}

.empty-state i {
  font-size: 3rem;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 80%;
}

.message-wrapper.user {
  align-self: flex-end;
}

.message-wrapper.assistant {
  align-self: flex-start;
}

.message {
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.message-wrapper.user .message {
  background-color: #2b5278;
  color: white;
  border-top-right-radius: 4px;
  margin-left: auto;
}

.message-wrapper.assistant .message {
  background-color: #f0f2f5;
  color: #1a1a1a;
  border-top-left-radius: 4px;
  margin-right: auto;
}

.message-content {
  line-height: 1.5;
  white-space: pre-wrap;
  font-size: 0.95rem;
}

.message-timestamp {
  font-size: 0.75rem;
  margin-top: 4px;
  opacity: 0.7;
}

.message-wrapper.user .message-timestamp {
  color: rgba(255, 255, 255, 0.8);
}

.message-wrapper.assistant .message-timestamp {
  color: #666;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #e5e5e5;
  background-color: #ffffff;
}

.input-container {
  display: flex;
  gap: 12px;
  max-width: 800px;
  margin: 0 auto;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  resize: none;
  font-size: 1rem;
  line-height: 1.5;
  transition: border-color 0.2s;
}

.message-input:focus {
  outline: none;
  border-color: #007bff;
}

.message-input:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.send-button {
  padding: 0 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: #0056b3;
}

.send-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* Estilização da barra de rolagem */
.chat-list::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-list::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-list::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.chat-list::-webkit-scrollbar-thumb:hover,
.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style> 