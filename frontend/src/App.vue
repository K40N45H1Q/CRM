<script setup>
import { ref, onMounted } from 'vue'
import Header from "./compontents/Header.vue";
import CRM from "./compontents/CRM.vue";
import Login from "./compontents/Login.vue";

const isAuthenticated = ref(false)

onMounted(async () => {
  try {
    const res = await fetch('http://localhost:8000/api/records', { credentials: 'include' })
    if (res.ok) {
      isAuthenticated.value = true
    }
  } catch (e) {
    console.error('Auth check failed')
  }
})

const onLoginSuccess = () => {
  isAuthenticated.value = true
}
</script>

<template>
  <div class="bordered frame">
    <template v-if="isAuthenticated">
      <Header @logout="isAuthenticated = false" />
      <CRM />
    </template>
    <Login v-else @login-success="onLoginSuccess" />
  </div>
</template>

<style scoped></style>