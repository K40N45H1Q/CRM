<script setup>
import { ref, defineEmits } from 'vue'

const emit = defineEmits(['login-success'])

const username = ref('')
const password = ref('')
const isNotifyVisible = ref(false)
const message = ref('')
const isLoading = ref(false)

const showNotify = (msg) => {
  message.value = msg
  isNotifyVisible.value = true
  setTimeout(() => {
    isNotifyVisible.value = false
  }, 3000)
}

const handleLogin = async () => {
  if (isLoading.value) return
  
  if (!username.value || !password.value) {
    showNotify('EMPTY FIELDS')
    return
  }

  isLoading.value = true
  
  try {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      }),
      credentials: 'include' 
    })

    if (response.ok) {
      showNotify('SUCCESS!')
      setTimeout(() => {
        emit('login-success')
      }, 600)
    } else {
      showNotify('ACCESS DENIED!')
      password.value = ''
    }
  } catch (error) {
    showNotify('SERVER ERROR')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="viewport-fix" :style="{ '--cyan': '#00ffff', '--h': '40px' }">
    <div class="bordered page-container">
      <div class="login-wrapper">
        
        <div class="notify" :class="{ visible: isNotifyVisible }">
          <h1>{{ message }}</h1>
        </div>

        <div class="login-modal">
          <h1>CRM SYSTEM</h1>
          <form @submit.prevent="handleLogin" class="form-group">
            <input 
              v-model="username" 
              type="text" 
              placeholder="USERNAME" 
              :disabled="isLoading"
              autocomplete="username"
            >
            <input 
              v-model="password" 
              type="password" 
              placeholder="PASSWORD" 
              :disabled="isLoading"
              autocomplete="current-password"
            >
            <button type="submit" class="button auth-btn" :disabled="isLoading">
              {{ isLoading ? 'WAIT...' : 'EXECUTE' }}
            </button>
          </form>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.viewport-fix {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: #000;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    padding: 15px;
    overflow: hidden;
}

.page-container {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
}

.login-wrapper {
    width: 300px;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.notify {
    position: absolute;
    top: -85px; 
    width: 100%;
    padding: 10px;
    border: 2px solid var(--cyan);
    color: var(--cyan);
    text-align: center;
    background: rgba(0, 0, 0, 0.95);
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
    box-sizing: border-box;
    visibility: hidden; 
    opacity: 0;
    transform: scaleX(0); 
    transform-origin: left; 
    transition: transform 0.4s cubic-bezier(0.23, 1, 0.32, 1), 
                opacity 0.3s ease, 
                visibility 0.4s;
    z-index: 10;
}

.notify.visible {
    visibility: visible;
    opacity: 1;
    transform: scaleX(1);
}

.notify h1 {
    font-size: 16px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0;
    font-family: monospace;
}

.login-modal {
    padding: 30px;
    width: 300px;
    border: 2px solid var(--cyan);
    background: black;
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
    box-sizing: border-box;
}

.login-modal h1 {
    color: var(--cyan);
    margin: 0 0 25px 0;
    letter-spacing: 4px;
    text-shadow: 0 0 8px var(--cyan);
    text-transform: uppercase; 
    border-left: 4px solid var(--cyan); 
    padding-left: 15px;
    font-size: 20px;
    font-family: monospace;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 15px;
    width: 100%;
}

.login-modal input {
    width: 100%;
    height: var(--h);
    background: rgba(0, 255, 255, 0.05);
    border: 1px solid var(--cyan);
    color: var(--cyan);
    padding: 0 15px;
    font-family: monospace;
    outline: none;
    box-sizing: border-box;
}

.auth-btn {
    width: 100%;
    height: var(--h);
    background: black;
    color: var(--cyan);
    border: 1px solid var(--cyan);
    font-family: monospace;
    font-weight: bold;
    cursor: pointer;
    text-transform: uppercase;
    transition: 0.2s;
}

.auth-btn:hover {
    background: var(--cyan);
    color: black;
}

.auth-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
</style>