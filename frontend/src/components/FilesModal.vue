<template>
  <div class="files-modal">
    <h2>📎 Прикрепленные файлы</h2>
    <div class="drop-area" @dragover.prevent="onDragOver" @dragleave="onDragLeave" @drop.prevent="onDrop" :class="{ over: dragOver }">
      <p>Перетащите файл или</p>
      <input type="file" ref="fileInput" @change="onFileSelect" style="display:none" />
      <button @click="triggerFileInput" class="btn-primary">Выбрать файл</button>
    </div>

    <table v-if="files.length" class="files-table">
      <thead><tr><th>Имя</th><th>Размер</th><th>Действия</th></tr></thead>
      <tbody>
        <tr v-for="file in files" :key="file._id">
          <td :title="file.originalName">{{ file.originalName }}</td>
          <td>{{ (file.size / 1024).toFixed(1) }} KB</td>
          <td>
            <button class="btn-open" @click="openFile(file)">👁 Открыть</button>
            <button class="btn-delete" @click="removeFile(file._id)">Удалить 🗑</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-else class="empty-state">Нет файлов</div>

    <div class="actions">
      <button class="cancel" @click="$emit('close')">Закрыть</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { api } from "../api";

export default {
  props: { ownerType: { type: String, required: true }, ownerId: { type: String, required: true } },
  emits: ["close"],
  setup(props) {
    const files = ref([]);
    const dragOver = ref(false);
    const fileInput = ref(null);
    const API_BASE = "http://localhost:8000";

    const loadFiles = async () => { files.value = await api.listFiles(props.ownerType, props.ownerId); };
    const onDragOver = () => dragOver.value = true;
    const onDragLeave = () => dragOver.value = false;
    const onDrop = async (e) => { dragOver.value = false; if (e.dataTransfer.files[0]) await uploadFile(e.dataTransfer.files[0]); };
    const triggerFileInput = () => fileInput.value?.click();
    const onFileSelect = async (e) => { if (e.target.files[0]) await uploadFile(e.target.files[0]); e.target.value = ""; };
    const uploadFile = async (file) => {
      const formData = new FormData();
      formData.append("ownerId", props.ownerId);
      formData.append("ownerType", props.ownerType);
      formData.append("file", file);
      await api.uploadFile(formData);
      await loadFiles();
    };
    const openFile = (file) => {
      const url = file.url.startsWith("http") ? file.url : `${API_BASE}${file.url}`;
      window.open(`${url}?t=${Date.now()}`, "_blank");
    };
    const removeFile = async (id) => { if (confirm("Удалить?")) { await api.deleteFile(id); await loadFiles(); } };

    onMounted(loadFiles);
    return { files, dragOver, fileInput, onDragOver, onDragLeave, onDrop, triggerFileInput, onFileSelect, uploadFile, openFile, removeFile };
  }
};
</script>

<style scoped>
.files-modal { padding: 10px; font-family: sans-serif; }
.drop-area { border: 2px dashed #ccc; padding: 15px; text-align: center; margin-bottom: 15px; border-radius: 8px; }
.drop-area.over { border-color: #4CAF50; background: #f0fff0; }
.files-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
.files-table th, .files-table td { padding: 8px; border-bottom: 1px solid #eee; text-align: left; }
.btn-primary, .btn-open, .btn-delete, .cancel { padding: 6px 10px; margin: 0 4px; cursor: pointer; border: 1px solid #ccc; border-radius: 4px; background: #fff; }
.btn-primary { background: #007BFF; color: white; border: none; }
.btn-open { background: #28a745; color: white; border: none; }
.btn-delete { background: #dc3545; color: white; border: none; }
.empty-state { text-align: center; color: #888; padding: 20px; }
</style>