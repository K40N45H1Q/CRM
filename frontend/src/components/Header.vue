<script setup>
import { currentType, isAuthenticated, userGroup } from "../state.js"
import Dropdown from "./Dropdown.vue"
const emit = defineEmits(['logout'])
const logout = async () => {
  try {
    await fetch('http://localhost:8000/api/logout', { 
      method: 'POST', 
      credentials: 'include'
    })
  } catch (e) {
    console.error('Logout request failed')
  } finally {
    isAuthenticated.value = false
    emit('logout')
  }
}
</script>

<template>
  <header>
    <h2>CRM SYSTEM</h2>
    
    <div class="actions">

      <Dropdown 
      v-model="currentType"
      defaultValue=currentType
      :options="['CAR', 'PERSON']"
      />

      <button class="logout button" @click="logout">LOGOUT</button>
    </div>
  </header>
</template>

<style scoped>
header {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

h2 {
  padding-left: 15px;
  border-left: 4px solid var(--cyan);
}

:deep(.dropdown) {
  width: 100px !important;
}

:deep(.dropdown-button) {
  height: 100%;
}

.actions {
  gap: 15px;
  display: flex;
}

.logout {
  color: var(--red);
  border-color: var(--red);
  box-shadow: 0 0 20px rgba(255, 0, 0, 0.2);
}

.logout:hover {
  color: black;
  background-color: var(--red);
}

.type:hover {
  color: black;
  background-color: var(--cyan);
}
</style>