<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { current_type } from '../state.js'

// --- Config ---
const API_URL = 'http://localhost:8000/api/records'
const CFG_URL = 'http://localhost:8000/api/config'

const baseFieldsConfig = {
  CAR: ['BRAND', 'MODEL', 'YEAR', 'COLOR'],
  PERSON: ['NAME', 'SURNAME', 'TIN', 'GENDER', 'CAR']
}

// --- State ---
const fields = ref([])
const records = ref([])
const tempFiles = ref([])
const fileInput = ref(null)
const editingId = ref(null)

const showModal = ref(false)
const activeRecord = ref(null)

// --- Computed ---

// Заголовки таблицы всегда следуют за текущими полями в форме
const tableHeaders = computed(() => fields.value.map(f => f.k))

const availableCars = computed(() => {
  const cars = records.value.filter(r => r.__recordType === 'CAR')
  if (cars.length === 0) return []
  return cars.map(r => {
    const brand = r.BRAND || ''
    const model = r.MODEL || ''
    const year = r.YEAR ? ` (${r.YEAR})` : ''
    const label = `${brand} ${model}`.trim()
    return label ? `${label}${year}` : 'UNKNOWN CAR'
  })
})

// --- API Logic (Конфигурация полей) ---

const loadFieldsConfig = async () => {
  try {
    const res = await fetch(`${CFG_URL}/${current_type.value}`)
    const customKeys = res.ok ? await res.json() : []
    
    const base = baseFieldsConfig[current_type.value] || []
    const baseFields = base.map(f => ({ k: f, v: '', isBase: true }))
    const customFields = customKeys.map(f => ({ k: f, v: '', isBase: false }))
    
    fields.value = [...baseFields, ...customFields]
  } catch (err) {
    console.error('Config Load Error:', err)
  }
}

const syncConfigWithDB = async () => {
  const customKeys = fields.value.filter(f => !f.isBase).map(f => f.k)
  try {
    await fetch(`${CFG_URL}/${current_type.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(customKeys)
    })
  } catch (err) {
    console.error('Config Save Error:', err)
  }
}

// Вызываем при каждом изменении названия поля
const onKeyChange = () => {
  syncConfigWithDB()
}

// --- API Logic (Записи) ---

const loadRecords = async () => {
  try {
    const res = await fetch(API_URL)
    if (res.ok) records.value = await res.json()
  } catch (err) {
    console.error('DB Error:', err)
  }
}

const deleteRecord = async (id) => {
  try {
    await fetch(`${API_URL}/${id}`, { method: 'DELETE' })
    await loadRecords()
  } catch (err) {
    console.error('Delete Error:', err)
  }
}

const saveRecord = async () => {
  const payload = {
    __recordType: current_type.value,
    files: [...tempFiles.value]
  }
  fields.value.forEach(f => { payload[f.k] = f.v })

  const method = editingId.value ? 'PUT' : 'POST'
  const url = editingId.value ? `${API_URL}/${editingId.value}` : API_URL

  try {
    const res = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      editingId.value = null
      tempFiles.value = []
      await loadFieldsConfig() 
      await loadRecords()
    }
  } catch (err) {
    console.error('Save Error:', err)
  }
}

// --- UI Logic ---

const addCustomField = async () => {
  fields.value.push({ k: 'NEW_FIELD', v: '', isBase: false })
  await syncConfigWithDB()
}

const removeField = async (index) => {
  if (!fields.value[index].isBase) {
    fields.value.splice(index, 1)
    await syncConfigWithDB()
  }
}

const editRecord = (record) => {
  editingId.value = record.id
  tempFiles.value = [...record.files]
  fields.value.forEach(f => {
    f.v = record[f.k] || ''
  })
}

// --- Files ---

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

onMounted(loadRecords)

watch(current_type, async () => {
  await loadFieldsConfig()
}, { immediate: true })

</script>

<template>
  <div class="content-stack">
    
    <div class="grid-form">
      <div v-for="(field, i) in fields" :key="i" class="dynamic-row">
        <div class="form-group">
          <label>KEY {{ field.isBase ? '(FIXED)' : '' }}</label>
          <input v-model="field.k" :disabled="field.isBase" @input="onKeyChange">
        </div>
        
        <div class="form-group">
          <label>VALUE</label>
          
          <template v-if="current_type === 'PERSON' && field.k === 'CAR'">
            <div class="dropdown">
              <button class="type-btn" type="button">
                {{ field.v || (availableCars.length ? 'CHOOSE CAR...' : 'NO CARS') }}
              </button>
              <ul v-if="availableCars.length > 0" class="bordered scrollable-list">
                <li v-for="car in availableCars" :key="car" @click="field.v = car">
                  {{ car }}
                </li>
              </ul>
            </div>
          </template>
          
          <template v-else>
            <input v-model="field.v" placeholder="...">
          </template>
        </div>

        <button 
          class="btn-remove-col" 
          :style="field.isBase ? 'opacity:0.3; cursor:not-allowed' : ''" 
          @click="removeField(i)"
        >✕</button>
      </div>
    </div>

    <div class="controls-section">
      <input type="file" ref="fileInput" multiple hidden @change="processFiles">
      <div class="sub-controls">
        <button class="btn-ui" @click="addCustomField">ADD FIELD</button>
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
            <th v-for="header in tableHeaders" :key="header">{{ header }}</th>
            <th class="col-shrink">FILES</th> 
            <th class="col-shrink">ACTIONS</th> 
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in records" :key="r.id">
            <template v-if="r.__recordType === current_type">
              <td v-for="header in tableHeaders" :key="header">{{ r[header] || '—' }}</td>
              <td class="col-shrink text-center"> 
                <span class="docs-link" @click="activeRecord = r; showModal = true">
                  {{ r.files.length }} Files
                </span>
              </td>
              <td class="col-shrink"> 
                <div class="actions-cell">
                  <button class="btn-action btn-edit" @click="editRecord(r)">EDIT</button>
                  <button class="btn-action btn-del" @click="deleteRecord(r.id)">DEL</button>
                </div>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>

  </div>

  <div v-if="showModal" id="modal" @click.self="showModal = false">
    <div class="modal-box shadow-cyan">
      <header class="modal-header">
        <h3 class="modal-title">RESOURCES</h3>
        <button class="btn-close-modal" @click="showModal = false">✕</button>
      </header>
      
      <div class="files-grid-container">
        <div v-for="(f, i) in activeRecord.files" :key="i" class="file-card">
          <button class="btn-del-file" @click.stop="activeRecord.files.splice(i, 1)">✕</button>
          <div class="file-preview-box" @click="openFile(f)">
            <img v-if="f.type.startsWith('image')" :src="f.data" class="file-img">
            <div v-else class="file-icon-big">📄</div>
          </div>
          <div class="file-name-label" :title="f.name">{{ f.name }}</div>
        </div>
        <div v-if="activeRecord.files.length === 0" class="no-files-msg">NO ATTACHED FILES</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Твои стили без изменений */
.content-stack { width: 100%; display: flex; flex-direction: column; }
.grid-form { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 20px 25px; margin-top: 20px; }
.dynamic-row { display: grid; grid-template-columns: 1fr 1fr 44px; gap: 10px; align-items: flex-end; }
.form-group { display: flex; flex-direction: column; }
label { color: var(--cyan); font-size: 11px; margin-bottom: 6px; text-transform: uppercase; }
input { background: rgba(0, 255, 255, 0.05); border: 2px solid var(--cyan); color: white; padding: 0 10px; height: 44px; outline: none; width: 100%; box-sizing: border-box; box-shadow: 0 0 20px rgba(0, 255, 255, 0.2); }
.dropdown { position: relative; width: 100%; }
.type-btn { background: rgba(0, 255, 255, 0.05); border: 2px solid var(--cyan); color: white; padding: 0 15px; height: 44px; width: 100%; text-align: left; cursor: pointer; font-weight: bold; text-transform: uppercase; font-size: 11px; box-shadow: 0 0 20px rgba(0, 255, 255, 0.2); transition: 0.3s; }
.type-btn:hover { background-color: var(--cyan); color: black; }
ul { left: 0; top: 100%; width: 100%; padding: 0; opacity: 0; margin-top: 10px; list-style: none; transition: 0.3s; visibility: hidden; position: absolute; background: black; transform: translateY(-10px); z-index: 100; border: 2px solid var(--cyan); }
.dropdown:hover ul { opacity: 1; visibility: visible; transform: translateY(0); }
li { font-weight: bold; padding: 12px 15px; cursor: pointer; color: white; border-bottom: 1px solid rgba(0,255,255,0.1); }
li:hover { color: black; background-color: var(--cyan); }
.scrollable-list { max-height: 200px; overflow-y: auto; }
.controls-section { display: flex; flex-direction: column; gap: 15px; margin-top: 25px; }
.sub-controls { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.btn-ui { cursor: pointer; font-weight: bold; text-transform: uppercase; border: 2px solid var(--cyan); height: 44px; background: transparent; color: var(--cyan); font-size: 11px; transition: 0.2s; }
.btn-ui:hover { background: var(--cyan); color: black; }
.btn-main { background: var(--cyan); color: black; border: none; }
.btn-attach { border-style: dashed; }
.btn-remove-col { border: 2px solid var(--red) !important; background: black; color: var(--red); height: 44px; width: 44px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(255, 0, 0, 0.2) !important; }
.table-wrapper { width: 100%; overflow-x: auto; margin-top: 15px; border: 1px solid rgba(0, 255, 255, 0.1); }
.debtor-table { width: 100%; border-collapse: collapse; min-width: 650px; }
.debtor-table th, .debtor-table td { border: 1px solid rgba(0, 255, 255, 0.2); padding: 12px; text-align: left; font-size: 12px; }
.debtor-table th { color: var(--cyan); background: rgba(0, 255, 255, 0.1); text-transform: uppercase; }
.col-shrink { width: 1%; white-space: nowrap; }
.actions-cell { display: flex; gap: 8px; }
.docs-link { color: var(--cyan); cursor: pointer; text-decoration: underline; font-weight: bold; }
.btn-action { background: none; border: 1px solid; padding: 6px 12px; cursor: pointer; font-size: 10px; text-transform: uppercase; }
.btn-edit { border-color: var(--cyan); color: var(--cyan); }
.btn-del { border-color: var(--red); color: var(--red); }
#modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.95); z-index: 999; display: flex; align-items: center; justify-content: center; }
.modal-box { background: #000; border: 2px solid var(--cyan); width: 90%; max-width: 900px; max-height: 85vh; display: flex; flex-direction: column; }
.shadow-cyan { box-shadow: 0 0 40px rgba(0, 255, 255, 0.3); }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px; border-bottom: 2px solid var(--cyan); }
.modal-title { color: var(--cyan); margin: 0; letter-spacing: 2px; }
.btn-close-modal { background: none; border: 1px solid var(--red); color: var(--red); width: 34px; height: 34px; cursor: pointer; font-size: 18px; }
.files-grid-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 20px; padding: 25px; overflow-y: auto; }
.file-card { position: relative; background: rgba(0, 255, 255, 0.03); border: 1px solid rgba(0, 255, 255, 0.2); padding: 10px; transition: 0.3s; }
.file-card:hover { border-color: var(--cyan); transform: scale(1.02); }
.file-preview-box { width: 100%; height: 110px; background: #111; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; cursor: pointer; overflow: hidden; }
.file-img { width: 100%; height: 100%; object-fit: cover; }
.file-icon-big { font-size: 40px; }
.file-name-label { font-size: 11px; text-align: center; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.btn-del-file { position: absolute; top: 0; right: 0; z-index: 2; background: var(--red); border: none; color: white; width: 24px; height: 24px; cursor: pointer; font-size: 14px; }
.no-files-msg { grid-column: 1 / -1; text-align: center; color: var(--cyan); opacity: 0.5; padding: 40px; }
@media (max-width: 600px) { .grid-form { grid-template-columns: 1fr; } .sub-controls { grid-template-columns: 1fr; } }
</style>