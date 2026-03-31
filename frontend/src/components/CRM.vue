<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import { currentType, baseFields } from '../state.js'

const API_BASE = 'http://localhost:8000/api'

const fields = ref([])
const records = ref([])
const tempFiles = ref([])
const fileInput = ref(null)
const editingId = ref(null)
const showModal = ref(false)
const activeRecord = ref(null)

const tableHeaders = computed(() => {
  const base = fields.value.map(f => f.k)
  return currentType.value === 'PERSON' ? [...base, 'MONTHLY', 'PROFIT'] : base
})

const availableCars = computed(() => records.value
  .filter(r => r.__recordType === 'CAR')
  .map(r => `${r.BRAND || ''} ${r.MODEL || ''} ${r.YEAR ? `(${r.YEAR})` : ''}`.trim() || 'UNKNOWN CAR')
)

const calculateMonthly = (r) => {
  const a = parseFloat(r.AMOUNT) || 0, t = parseFloat(r.TERM) || 0, p = parseFloat(r.APR) || 0
  return (a > 0 && t > 0) ? ((a + (a * p / 100)) / t).toFixed(2) : '0.00'
}

const calculateProfit = (r) => {
  const a = parseFloat(r.AMOUNT) || 0, p = parseFloat(r.APR) || 0
  return (a * p / 100).toFixed(2)
}

const api = (path, opt = {}) => fetch(`${API_BASE}${path}`, { credentials: 'include', ...opt })

const loadFieldsConfig = async () => {
  const res = await api(`/get_config/${currentType.value}`)
  const custom = res.ok ? await res.json() : []
  const base = baseFields[currentType.value] || []
  fields.value = [
    ...base.map(k => ({ k, v: '', isBase: true })),
    ...custom.map(k => ({ k, v: '', isBase: false }))
  ]
}

const syncConfigWithDB = () => {
  api(`/update_config/${currentType.value}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fields.value.filter(f => !f.isBase).map(f => f.k))
  })
}

const loadRecords = async () => {
  const res = await api('/records')
  if (res.ok) records.value = await res.json()
}

const addCustomField = async () => {
  fields.value.push({ k: 'NEW_FIELD', v: '', isBase: false })
  syncConfigWithDB()
}

const removeField = async (index) => {
  if (!fields.value[index].isBase) {
    fields.value.splice(index, 1)
    syncConfigWithDB()
  }
}

const saveRecord = async () => {
  const payload = { __recordType: currentType.value, files: [...tempFiles.value] }
  fields.value.forEach(f => { payload[f.k] = f.v })

  const res = await api(editingId.value ? `/records/${editingId.value}` : '/records', {
    method: editingId.value ? 'PUT' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  if (res.ok) {
    editingId.value = null
    tempFiles.value = []
    fields.value.forEach(f => f.v = '')
    loadRecords()
  }
}

const deleteRecord = async (id) => {
  await api(`/records/${id}`, { method: 'DELETE' })
  loadRecords()
}

const editRecord = (r) => {
  editingId.value = r.id
  tempFiles.value = [...(r.files || [])]
  fields.value.forEach(f => { f.v = r[f.k] || '' })
}

const triggerFiles = () => fileInput.value.click()

const processFiles = (e) => {
  const files = Array.from(e.target.files)
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (ev) => {
      tempFiles.value.push({
        name: file.name,
        type: file.type,
        data: ev.target.result
      })
    }
    reader.readAsDataURL(file)
  })
  e.target.value = ''
}

const openFile = (f) => {
  const arr = f.data.split(','), mime = arr[0].match(/:(.*?);/)[1], bstr = atob(arr[1])
  let n = bstr.length, u8arr = new Uint8Array(n)
  while(n--) u8arr[n] = bstr.charCodeAt(n)
  window.open(URL.createObjectURL(new Blob([u8arr], {type:mime})), '_blank')
}

watch(currentType, loadFieldsConfig, { immediate: true })
onMounted(loadRecords)
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
          
          <template v-if="currentType === 'PERSON' && field.k === 'CAR'">
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
        {{ editingId ? 'UPDATE' : 'RECORD' }}
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
            <template v-if="r.__recordType === currentType">
              <td v-for="header in tableHeaders" :key="header">
                
                <template v-if="header === 'MONTHLY'">
                  <span style="color: var(--cyan);">{{ calculateMonthly(r) }} EUR</span>
                </template>
                <template v-else-if="header === 'PROFIT'">
                  <span style="color: #00ff00;">{{ calculateProfit(r) }} EUR</span>
                </template>

                <template v-else-if="header === 'TERM' && r[header]">
                  {{ r[header] }} Months
                </template>
                <template v-else-if="header === 'APR' && r[header]">
                  {{ r[header] }}%
                </template>
                <template v-else-if="(header === 'AMOUNT' || header === 'PRICE') && r[header]">
                  {{ r[header] }} EUR
                </template>

                <template v-else>
                  {{ r[header] || '—' }}
                </template>

              </td>
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
.content-stack {
  width: 100%;
  display: flex;
  flex-direction: column;
}
.grid-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 20px 25px;
  margin-top: 20px;
}
.dynamic-row {
  display: grid;
  grid-template-columns: 1fr 1fr 44px;
  gap: 10px;
  align-items: flex-end;
}
.form-group {
  display: flex;
  flex-direction: column;
}
label {
  color: var(--cyan);
  font-size: 11px;
  margin-bottom: 6px;
  text-transform: uppercase;
}
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
.dropdown {
  position: relative;
  width: 100%;
}
.type-btn {
  background: rgba(0, 255, 255, 0.05);
  border: 2px solid var(--cyan);
  color: white;
  padding: 0 15px;
  height: 44px;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 11px;
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
  transition: 0.3s;
}
.type-btn:hover {
  background-color: var(--cyan);
  color: black;
}
ul {
  left: 0;
  top: 100%;
  width: 100%;
  padding: 0;
  opacity: 0;
  margin-top: 10px;
  list-style: none;
  transition: 0.3s;
  visibility: hidden;
  position: absolute;
  background: black;
  transform: translateY(-10px);
  z-index: 100;
  border: 2px solid var(--cyan);
}
.dropdown:hover ul {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}
li {
  font-weight: bold;
  padding: 12px 15px;
  cursor: pointer;
  color: white;
  border-bottom: 1px solid rgba(0, 255, 255, 0.1);
}
li:hover {
  color: black;
  background-color: var(--cyan);
}
.scrollable-list {
  max-height: 200px;
  overflow-y: auto;
}
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
.btn-ui {
  cursor: pointer;
  font-weight: bold;
  text-transform: uppercase;
  border: 2px solid var(--cyan);
  height: 44px;
  background: transparent;
  color: var(--cyan);
  font-size: 11px;
  transition: 0.2s;
}
.btn-ui:hover {
  background: var(--cyan);
  color: black;
}
.btn-main {
  background: var(--cyan);
  color: black;
  border: none;
}
.btn-main:hover {
  box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
}
.btn-attach {
  border-style: dashed;
}
.btn-remove-col {
  border: 2px solid var(--red) !important;
  background: black;
  color: var(--red);
  height: 44px;
  width: 44px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(255, 0, 0, 0.2) !important;
}
.debtor-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 650px;
  font-weight: bold;
}
.table-wrapper {
  width: 100%;
  overflow-x: auto;
  margin-top: 15px;
  border: 1px solid rgba(0, 255, 255, 0.1);
}
.debtor-table th,
.debtor-table td {
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

.col-shrink {
  width: 1%;
  white-space: nowrap;
}
.actions-cell {
  display: flex;
  gap: 8px;
}
.docs-link {
  color: var(--cyan);
  cursor: pointer;
  text-decoration: underline;
  font-weight: bold;
}
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
  font-weight: bold;
  letter-spacing: 1px;
}
.btn-edit:hover {
  color: black;
  background-color: var(--cyan)
}
.btn-del {
  border-color: var(--red);
  color: var(--red);
  font-weight: bold;
  letter-spacing: 1px;
}
.btn-del:hover {
  color: black;
  background-color: var(--red);
}
#modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.95);
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-box {
  background: #000;
  border: 2px solid var(--cyan);
  width: 400px;
  max-width: 400px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
}
.shadow-cyan {
  box-shadow: 0 0 40px rgba(0, 255, 255, 0.3);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 2px solid var(--cyan);
}
.modal-title {
  color: var(--cyan);
  margin: 0;
  letter-spacing: 2px;
}
.btn-close-modal {
  background: none;
  border: 1px solid var(--red);
  color: var(--red);
  width: 34px;
  height: 34px;
  cursor: pointer;
  font-size: 18px;
}
.files-grid-container {
  display: grid;
  grid-template-rows: repeat(auto-fill, minmax(160px, 1fr));
  gap: 20px;
  padding: 25px;
  overflow-y: auto;
}
.file-card {
  position: relative;
  background: rgba(0, 255, 255, 0.03);
  border: 1px solid rgba(0, 255, 255, 0.2);
  padding: 10px;
  transition: 0.3s;
}
.file-card:hover {
  border-color: var(--cyan);
  transform: scale(1.02);
}
.file-preview-box {
  width: 100%;
  height: 110px;
  background: #111;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  cursor: pointer;
  overflow: hidden;
}
.file-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.file-icon-big {
  font-size: 40px;
}
.file-name-label {
  font-size: 11px;
  text-align: center;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.btn-del-file {
  position: absolute;
  top: 0;
  right: 0;
  z-index: 2;
  background: var(--red);
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 14px;
}
.no-files-msg {
  grid-column: 1 / -1;
  text-align: center;
  color: var(--cyan);
  opacity: 0.5;
  padding: 40px;
}
@media (max-width: 600px) {
  .grid-form {
    grid-template-columns: 1fr;
  }
  .sub-controls {
    grid-template-columns: 1fr;
  }
}
</style>