<template>
  <div class="login-container">
    <div class="login-card">
      <div class="logo-area">
        <i-wallet :size="48" color="#3b82f6" />
        <h1>wallet_Currency</h1>
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Usuario</label>
          <input v-model="form.username" type="text" placeholder="Tu usuario" required />
        </div>
        
        <div class="form-group">
          <label>Contraseña</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required />
        </div>
        
        <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
        
        <button type="submit" :disabled="loading">
          {{ loading ? 'Iniciando...' : 'Entrar' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api';
import { Wallet as IWallet } from 'lucide-vue-next';

const form = ref({ username: '', password: '' });
const loading = ref(false);
const errorMsg = ref('');

const handleLogin = async () => {
  loading.value = true;
  errorMsg.value = '';
  
  try {
    console.log("APP VERSION 2.0")
    const response = await api.post('/login', form.value);
    console.log("APP VERSION 2.0");
    
    if (response.data.status === 'success') {
      alert(`¡Bienvenido ${response.data.user.username}!`);
      // Aquí guardaremos el token o ID en el futuro
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || 'Error al conectar con el servidor';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Estilo rápido para probar */
.login-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f3f4f6; }
.login-card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); width: 350px; }
.logo-area { text-align: center; margin-bottom: 1.5rem; }
.form-group { margin-bottom: 1rem; }
input { width: 100%; padding: 0.5rem; border: 1px solid #d1d5db; border-radius: 6px; }
button { width: 100%; padding: 0.75rem; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; }
.error-text { color: #ef4444; font-size: 0.875rem; margin-bottom: 1rem; }
</style>