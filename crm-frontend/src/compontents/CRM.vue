<script setup>
import { ref, watch } from 'vue'
import { current_type } from '../state.js'

// --- Config ---
const baseFieldsConfig = {
  CAR: ['BRAND', 'MODEL', 'YEAR', 'COLOR'],
  PERSON: ['NAME', 'SURNAME', 'AGE', 'GENDER']
}

// --- State ---
const fields = ref([])
const records = ref([])
const tempFiles = ref([])
const fileInput = ref(null)
const editingId = ref(null)

const showModal = ref(false)
const activeRecord = ref(null)

// --- Logic ---
const initFields = () => {
  const base = baseFieldsConfig[current_type.value] || []
  fields.value = base.map(f => ({ k: f, v: '', isBase: true }))
  tempFiles.value = []
  editingId.value = null
}

watch(current_type, initFields, { immediate: true })

const triggerFiles = () => fileInput.value.click()

const processFiles = (event) => {
  const selectedFiles = Array.from(event.target.files)
  selectedFiles.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      tempFiles.value.push({
        name: file.name,
        type: file.type,
        data: e.target.result
      })
    }
    reader.readAsDataURL(file)
  })
  event.target.value = ''
}

const openFile = (file) => {
  const base64Data = file.data.split(',')[1]
  const byteCharacters = atob(base64Data)
  const byteNumbers = new Array(byteCharacters.length)
  
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i)
  }
  
  const byteArray = new Uint8Array(byteNumbers)
  const blob = new Blob([byteArray], { type: file.type })
  const fileURL = URL.createObjectURL(blob)
  
  window.open(fileURL, '_blank')
}

const saveRecord = () => {
  const data = {
    id: editingId.value || Date.now(),
    files: [...tempFiles.value]
  }
  fields.value.forEach(f => { data[f.k] = f.v })

  if (editingId.value) {
    const idx = records.value.findIndex(r => r.id === editingId.value)
    records.value[idx] = data
  } else {
    records.value.push(data)
  }
  
  fields.value.forEach(f => f.v = '')
  tempFiles.value = []
  editingId.value = null
}

const editRecord = (record) => {
  editingId.value = record.id
  tempFiles.value = [...record.files]
  fields.value.forEach(f => { f.v = record[f.k] || '' })
}

const deleteRecord = (id) => {
  records.value = records.value.filter(r => r.id !== id)
}
</script>

<template>
  <div class="content-stack">
    
    <div class="grid-form">
      <div v-for="(field, i) in fields" :key="i" class="dynamic-row">
        <div class="form-group">
          <label>KEY {{ field.isBase ? '(FIXED)' : '' }}</label>
          <input v-model="field.k" :disabled="field.isBase">
        </div>
        <div class="form-group">
          <label>VALUE</label>
          <input v-model="field.v" placeholder="...">
        </div>
        <button 
          class="btn-remove-col" 
          :style="field.isBase ? 'opacity:0.3; cursor:not-allowed' : ''" 
          @click="!field.isBase && fields.splice(i, 1)"
        >✕</button>
      </div>
    </div>

    <div class="controls-section">
      <input type="file" ref="fileInput" multiple hidden @change="processFiles">
      <div class="sub-controls">
        <button class="btn-ui" @click="fields.push({ k: 'New Field', v: '', isBase: false })">ADD FIELD</button>
        <button class="btn-ui btn-attach" @click="triggerFiles">ATTACH FILES ({{ tempFiles.length }})</button>
      </div>
      <button class="btn-ui btn-main" @click="saveRecord">
        {{ editingId ? 'UPDATE DATA' : 'RECORD' }}
      </button>
    </div>

    <div class="table-wrapper">
      <table class="debtor-table">
        <thead>
          <tr>
            <th v-for="f in fields" :key="f.k">{{ f.k }}</th>
            <th class="col-shrink">DOCS</th> <th class="col-shrink col-actions">ACTIONS</th> </tr>
        </thead>
        <tbody>
          <tr v-for="r in records" :key="r.id">
            <td v-for="f in fields" :key="f.k">{{ r[f.k] || '—' }}</td>
            <td class="col-shrink text-center"> <span class="docs-link" @click="activeRecord = r; showModal = true">
                {{ r.files.length }} Files
              </span>
            </td>
            <td class="col-shrink"> <div class="actions-cell">
                <button class="btn-action btn-edit" @click="editRecord(r)">EDIT</button>
                <button class="btn-action btn-del" @click="deleteRecord(r.id)">DEL</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>

  <div v-if="showModal" id="modal" @click.self="showModal = false">
    <div class="modal-box">
      <header class="modal-header">
        <h3 class="modal-title">RESOURCES</h3>
        <button class="btn-close-modal" @click="showModal = false">✕</button>
      </header>
      <div class="files-container">
        <div v-for="(f, i) in activeRecord.files" :key="i" class="file-item">
          <div class="file-preview-box" @click="openFile(f)">
            <button class="btn-del-file" @click.stop="activeRecord.files.splice(i, 1)">✕</button>
            <img v-if="f.type.startsWith('image')" :src="f.data" class="file-img">
            <div v-else class="file-icon">📄</div>
          </div>
          <div class="file-name-label">{{ f.name }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Основной контейнер */
.content-stack {
  width: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

/* Сетка полей ввода: теперь элементы .dynamic-row будут врапаться целиком */
.grid-form { 
  display: grid; 
  /* Создаем колонки, которые подстраиваются под размер блока из 3-х элементов */
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); 
  gap: 20px 25px; 
  margin-top: 20px; 
}

/* Строка из 3 элементов: Ключ + Значение + Кнопка */
.dynamic-row { 
  display: grid; 
  /* Фиксируем 3 колонки: две гибких и одна под кнопку */
  grid-template-columns: 1fr 1fr 44px; 
  gap: 10px; 
  align-items: flex-end; 
}

/* Кнопки управления секцией */
.controls-section { 
  display: flex; 
  flex-direction: column; 
  gap: 15px; 
  margin-top: 25px; 
}

.sub-controls { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 15px; 
}

/* ТАБЛИЦА: Скролл + сжатие служебных колонок */
.table-wrapper {
  width: 100%;
  overflow-x: auto;
  margin-top: 15px;
  border: 1px solid rgba(0, 255, 255, 0.1);
}

.debtor-table { 
  width: 100%; 
  border-collapse: collapse; 
  min-width: 650px; 
}

.debtor-table th, .debtor-table td { 
  border: 1px solid rgba(0, 255, 255, 0.2); 
  padding: 12px; 
  text-align: left; 
  font-size: 12px; 
}

.debtor-table th { 
  color: var(--cyan); 
  background: rgba(0, 255, 255, 0.1); 
  text-transform: uppercase; 
}

/* Сжатие колонок DOCS и ACTIONS до max-content */
.col-shrink {
  width: 1%;
  white-space: nowrap;
}

.text-center {
  text-align: center !important;
}

.actions-cell {
  display: flex;
  gap: 10px;
  width: max-content;
}

/* Элементы управления */
.form-group { display: flex; flex-direction: column; }
label { color: var(--cyan); font-size: 11px; margin-bottom: 6px; text-transform: uppercase; }
input { 
  background: rgba(0, 255, 255, 0.05); 
  border: 2px solid var(--cyan); 
  color: white; 
  padding: 0 10px; 
  height: 44px; 
  outline: none; 
  width: 100%;
  box-sizing: border-box;
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
}

.btn-remove-col {
  font-weight: bold;
  border: 2px solid var(--red) !important;
  background: black;
  color: var(--red);
  height: 44px;
  width: 44px;
  cursor: pointer;
  transition: 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(255, 0, 0, 0.2) !important;
}

.btn-remove-col:hover:not([style*="opacity"]) {
  background: var(--red);
  color: black;
}

.btn-ui { 
  cursor: pointer; 
  font-weight: bold; 
  text-transform: uppercase; 
  border: 2px solid var(--cyan); 
  height: 44px; 
  background: transparent; 
  color: var(--cyan); 
  font-size: 11px;
}

.btn-main { background: var(--cyan); color: black; border: none; }
.btn-attach { border-style: dashed; }

.docs-link { color: #0f8; cursor: pointer; text-decoration: underline; white-space: nowrap; }

.btn-action { 
  background: none; 
  border: 1px solid; 
  padding: 6px 12px; 
  cursor: pointer; 
  font-size: 10px; 
  text-transform: uppercase; 
}
.btn-edit {
  border-color: var(--cyan);
  color: var(--cyan);
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
}

.btn-edit:hover {
  color: black;
  background-color: var(--cyan);
}

.btn-del {
  border-color: var(--red);
  color: var(--red);
  box-shadow: 0 0 20px rgba(255, 0, 0, 0.2);
}

.btn-del:hover {
  color: black;
  background: var(--red);
}

/* Modal */
#modal { 
  position: fixed; 
  top: 0; left: 0; 
  width: 100%; height: 100%; 
  background: rgba(0, 0, 0, 0.95); 
  z-index: 999; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  padding: 20px;
}

.modal-box { 
  background: #000; 
  border: 2px solid var(--cyan); 
  padding: 20px; 
  width: 100%; 
  max-width: 800px; 
  max-height: 90vh; 
  overflow-y: auto; 
}

.modal-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  border-bottom: 1px solid rgba(0, 255, 255, 0.3); 
  padding-bottom: 15px; 
  margin-bottom: 20px; 
}

.btn-close-modal {
  font-weight: bold;
  border: 2px solid var(--red) !important;
  box-shadow: 0 0 20px rgba(255, 0, 0, 0.2) !important;
  background: black;
  color: var(--red);
  height: 34px;
  padding: 0 15px;
  cursor: pointer;
}

.files-container { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); 
  gap: 15px; 
}

.file-item { border: 1px solid rgba(0, 255, 255, 0.2); position: relative; }
.file-preview-box { height: 120px; display: flex; align-items: center; justify-content: center; cursor: pointer; overflow: hidden; }
.btn-del-file { 
  position: absolute; 
  top: 5px; right: 5px; 
  background: #f00; color: #fff; 
  border: none; cursor: pointer; 
  z-index: 2; 
}

/* Адаптивность под мобильные */
@media (max-width: 600px) {
  .grid-form {
    /* На маленьких экранах разрешаем занимать всю ширину, но сохраняем 3 элемента в ряд */
    grid-template-columns: 1fr; 
  }
  
  .dynamic-row {
    /* Если экран совсем узкий (например, 320px), можно разрешить перенос внутри строки */
    grid-template-columns: 1fr 1fr 44px;
  }

  .sub-controls { grid-template-columns: 1fr; }
}
</style>