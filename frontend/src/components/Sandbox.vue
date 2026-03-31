<script setup>
import { ref } from 'vue'
import Dropdown from './Dropdown.vue'

const showSandbox = ref(false)
</script>

<template>
  <div class="wrapper">
    <div class="sandbox">

      <template v-if="!showSandbox">
        <h2 @click="showSandbox = true"><\></h2>
        <p>WAKE THE F*CK UP, DEV. WE HAVE A CODE TO BURN.</p>
      </template>
      
    <Dropdown 
    v-if="showSandbox"
    v-model="currentType"
    defaultValue="Тип сделки"
    :options="['Обычная аренда', 'Аренда с выкупом']"
    />

    </div>
  </div>
</template>

<style scoped>
.wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.wrapper h2{
    cursor: pointer;
    padding: 15px;
    font-size: 150px;
    text-shadow: 0 0 15px var(--cyan);
}

.sandbox {
    position: absolute;
    bottom: calc(50% - 50px);
    text-align: center;
}
</style>