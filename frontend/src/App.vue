<script setup>

import { onMounted } from 'vue'
import { isAuthenticated, isInitializing, userGroup } from './state.js' 
import Header from "./components/Header.vue";
import CRM from "./components/CRM.vue";
import Login from "./components/Login.vue";
import Elite from './components/Elite.vue';

const getSession = async () => {
  while (true) {
    try {
      const response = await fetch('http://localhost:8000/api/get_session', { 
        credentials: 'include' 
      });
      const data = await response.json();
      isAuthenticated.value = data.isAuthenticated;
      userGroup.value = data.group

      break; 
    } catch (e) {
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
}

onMounted(async () => {
  const timer = new Promise(resolve => setTimeout(resolve, 5000));
  await Promise.all([getSession(), timer]);
  isInitializing.value = false;
});

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
        <Header @logout="isAuthenticated = false" />

        <template v-if="userGroup === 'admin'">
            <CRM />
          </template>
          
          <template v-else-if="userGroup === 'developer'">
            <Elite/>
          </template>
      </template>
      
      <Login v-else @login-success="getSession" />
    </template>

  </div>
</template>

<style scoped>

.init-screen {
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
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