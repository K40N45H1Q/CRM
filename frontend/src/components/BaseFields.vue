<script setup>
import { ref, watch } from 'vue'
import { apiBase, baseFields, currentType } from '@/state'

const form = ref({})
const extendedKeys = ref([])

const loadFields = async () => {
  const response = await fetch(
    `${apiBase}/get_config/${currentType.value}`,
    { credentials: 'include' }
  )

  extendedKeys.value = response.ok ? await response.json() : []

  form.value = Object.fromEntries([
    ...(baseFields[currentType.value] || []).map(k => [k, '']),
    ...extendedKeys.value.map(k => [k, ''])
  ])
}

const addExtendedField = () => {
  const newKey = 'NEW_FIELD_' + (extendedKeys.value.length + 1)
  extendedKeys.value.push(newKey)
  form.value[newKey] = ''
}

const removeExtendedField = (index) => {
  const key = extendedKeys.value[index]
  delete form.value[key]
  extendedKeys.value.splice(index, 1)
}

watch(currentType, loadFields, { immediate: true })
</script>

<template>
  <div class="wrapper">

    <!-- BASE FIELDS -->
    <div class="block">
      <h3>Base fields</h3>

      <div class="grid-2">
        <div
          class="field"
          v-for="key in baseFields[currentType]"
          :key="'base-' + key"
        >
          <label :for="'input-' + key">{{ key }}</label>
          <input
            :id="'input-' + key"
            v-model="form[key]"
            type="text"
          >
        </div>
      </div>
    </div>

    <!-- EXTENDED FIELDS -->
    <div class="block" v-if="extendedKeys.length > 0">
      <h3>Extended fields</h3>

      <div
        class="row"
        v-for="(key, i) in extendedKeys"
        :key="'ext-' + key"
      >
        <div class="column">
          <label>Key</label>
          <input v-model="extendedKeys[i]" type="text">
        </div>

        <div class="column">
          <label>Value</label>
          <input v-model="form[key]" type="text">
        </div>

        <button class="remove-btn" @click="removeExtendedField(i)">✕</button>
      </div>
    </div>

    <button class="add-btn" @click="addExtendedField()">Add field</button>

  </div>
</template>

<style scoped>
/* Контейнеры одинаковой ширины и высоты */
.wrapper {
  padding: 20px;
  display: flex;
  gap: 40px;
  align-items: stretch;
}

.block {
  flex: 1;
  min-width: 350px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;

  display: flex;
  flex-direction: column;
  height: 400px;
}

/* Базовые поля — 2 инпута в строку */
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
}

/* Расширенные поля */
.row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 6px;
  align-items: center;
}

.column {
  display: flex;
  flex-direction: column;
  flex: 1;
}

/* Кнопка удаления */
.remove-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #d33;
  background: #f8d7da;
  color: #a00;
  font-weight: bold;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: #f5c2c7;
}

/* Кнопка добавления */
.add-btn {
  height: 40px;
  padding: 0 20px;
  margin-top: auto;
  border-radius: 6px;
  border: 1px solid #888;
  cursor: pointer;
}
</style>
