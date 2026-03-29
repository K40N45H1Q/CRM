<template>

  <header>

    <h2>CRM SYSTEM</h2>
    
    <div class="actions">
      <div class="dropdown">
        <button class="type button">{{ current_type }}</button>
        <ul class="bordered">
          <li @click="current_type = 'CAR'">CAR</li>
          <li @click="current_type = 'PERSON'">PERSON</li>
        </ul>
      </div>
      <button class="logout button">LOGOUT</button>
    </div>

  </header>

</template>

<style scoped>

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

h2 {
  padding-left: 15px;
  border-left: 4px solid var(--cyan);
}

.actions {
  gap: 15px;
  display: flex;
}

.dropdown {
  position: relative;
}

ul {
  left: 0;
  top: 100%;
  width: 100%;
  padding: 0;
  opacity: 0;
  margin-top: 15px;
  list-style: none;
  transition: 0.3s;
  visibility: hidden;
  position: absolute;
  background: black;
  transform: translateY(-10px);
}

.dropdown:hover ul {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

li {
  font-weight: bold;
  padding: 10px;
  cursor: pointer;
}

li:hover {
  color: black;
  background-color: var(--cyan)
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

<script setup>
import { current_type } from "../state.js"
</script>