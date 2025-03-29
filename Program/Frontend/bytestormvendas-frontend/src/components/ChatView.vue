<script setup>
import { ref } from 'vue';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/query';
const loading = ref(false);
const message = ref('');
const chatHistory = ref([]);
const userInput = ref('');

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
</script>

<template>
  <div class="container">
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
</template>

<style scoped>
.chat-container {
  height: 500px;
  overflow-y: auto;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 0.5rem;
}

.chat-message {
  margin-bottom: 15px;
  padding: 10px 15px;
  border-radius: 10px;
  max-width: 80%;
  position: relative;
}

.user {
  background-color: #d1e7ff;
  margin-left: auto;
  text-align: right;
  border-top-right-radius: 0;
}

.assistant {
  background-color: #f0f0f0;
  margin-right: auto;
  text-align: left;
  border-top-left-radius: 0;
}

.message-content {
  word-break: break-word;
}

.message-timestamp {
  display: block;
  font-size: 12px;
  color: #888;
  margin-top: 5px;
}

textarea {
  resize: none;
}
</style> 