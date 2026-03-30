<script setup>

import { onMounted } from 'vue'
import { isAuthenticated, isInitializing } from './state.js' 
import Header from "./components/Header.vue";
import CRM from "./components/CRM.vue";
import Login from "./components/Login.vue";

onMounted(async () => {
  const timer = new Promise(resolve => setTimeout(resolve, 5000))
  
  const authCheck = fetch('http://localhost:8000/api/get_session', { 
    credentials: 'include' 
  }).catch(err => err)

  const [res] = await Promise.all([authCheck, timer])
  
  if (res && res.status === 200) {
    isAuthenticated.value = true
  }

  isInitializing.value = false
})

const onLoginSuccess = () => {
  isAuthenticated.value = true
}

const onLogout = () => {
  isAuthenticated.value = false
}

</script>

<template>
  <div class="bordered frame">
    
    <div v-if="isInitializing" class="init-screen">
       <div class="init-loader">
          <div class="scanner"></div>
          <h1>INITIALIZING SYSTEM...</h1>
          <p>PLEASE WAIT</p>
       </div>
    </div>

    <template v-else>
      <template v-if="isAuthenticated">
        <Header @logout="onLogout" />
        <CRM />
      </template>
      
      <Login v-else @login-success="onLoginSuccess" />
    </template>

  </div>
</template>

<style scoped>


.init-screen {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background: #000;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
    text-align: center;
    color: var(--cyan);
    font-family: monospace;
}

.init-loader h1 {
    font-size: 18px;
    letter-spacing: 4px;
    margin-bottom: 10px;
    text-shadow: 0 0 10px var(--cyan);
}

.init-loader p {
    font-size: 12px;
    opacity: 0.6;
    letter-spacing: 2px;
}

.scanner {
    width: 200px;
    height: 2px;
    background: var(--cyan);
    margin: 20px auto;
    box-shadow: 0 0 15px var(--cyan);
    animation: scan 1.5s infinite ease-in-out;
}

@keyframes scan {
    0%, 100% { transform: scaleX(0.1); opacity: 0.2; }
    50% { transform: scaleX(1); opacity: 1; }
}
</style>