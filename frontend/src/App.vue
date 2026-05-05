<template>
  <div class="app-container">
    <header class="top-bar">
      <h1>CRM</h1>
      <div class="controls">
        <input v-model="searchQuery" placeholder="Поиск по таблице..." class="search-input"/>
        <select v-model="currentTable" @change="loadTableData">
          <option value="users">Пользователи</option>
          <option value="cars">Машины</option>
        </select>
        <button @click="openAddForm">Добавить запись</button>
        <button @click="isSettingsModalVisible = true">Настройки</button>
      </div>
    </header>

    <TabulatorTable
      :data="tableData"
      :visibleColumns="visibleColumnsEffective"
      :columnLabels="columnLabelsEffective"
      :cars="cars"
      :globalSearch="searchQuery"
      :tableType="currentTable"
      @edit="onEditRow" @delete="onDeleteRow" @files="onOpenFiles"
    />

    <div v-if="isSettingsModalVisible" class="modal-overlay" @click.self="isSettingsModalVisible = false">
      <div class="modal">
        <SettingsModal
          :dbFields="dbFields"
          :visibleColumnsUsers="visibleColumnsUsers"
          :visibleColumnsCars="visibleColumnsCars"
          :labels="columnLabelsEffective"
          :settings="settings"
          @saved="onSettingsSaved" @close="isSettingsModalVisible = false"
        />
      </div>
    </div>

    <div v-if="isFormVisible" class="modal-overlay" @click.self="closeForm">
      <div class="modal">
        <component
          :is="currentFormComponent"
          :model="editingModel"
          :freeCars="freeCars"
          :defaults="settings"
          @saved="onFormSaved"
          @cancel="closeForm"
        />
      </div>
    </div>

    <div v-if="isFilesModalVisible" class="modal-overlay" @click.self="closeFilesModal">
      <div class="modal"><FilesModal :ownerType="filesOwnerType" :ownerId="filesOwnerId" @close="closeFilesModal" /></div>
    </div>
  </div>
</template>

<script>
/**
 * ✅ ГЛАВНЫЙ КОМПОНЕНТ ПРИЛОЖЕНИЯ
 * 
 * Отвечает за:
 * 1. Управление состоянием приложения (пользователи, машины, настройки)
 * 2. Загрузку данных с сервера при запуске
 * 3. Управление модальными окнами (форма добавления, редактирования, настройки, файлы)
 * 4. Синхронизацию данных между компонентами
 */

import { ref, computed, onMounted, shallowRef, markRaw } from "vue";
import { api } from "./api";
import { COLUMN_LABELS_RU, SENSITIVE_FIELDS } from "./constants";
import TabulatorTable from "./components/TabulatorTable.vue";
import SettingsModal from "./components/SettingsModal.vue";
import UserForm from "./components/UserForm.vue";
import CarForm from "./components/CarForm.vue";
import FilesModal from "./components/FilesModal.vue";

export default {
  name: "App",
  components: { TabulatorTable, SettingsModal, UserForm, CarForm, FilesModal },
  setup() {
    // ✅ СОСТОЯНИЕ ТАБЛИЦЫ
    const currentTable = ref("users"); // текущая активная таблица (users/cars)
    const tableData = ref([]); // данные для отображения в таблице
    const cars = ref([]); // полный список машин (для связей)
    const freeCars = ref([]); // только свободные машины (для формы добавления)
    const searchQuery = ref(""); // поисковой запрос

    // ✅ СОСТОЯНИЕ МОДАЛЕЙ
    const isSettingsModalVisible = ref(false); // видимость модали настроек
    const isFormVisible = ref(false); // видимость модали формы
    const isFilesModalVisible = ref(false); // видимость модали файлов
    const editingModel = ref({}); // модель, которая редактируется в форме
    const filesOwnerType = ref(null); // тип владельца файлов (user/car)
    const filesOwnerId = ref(null); // ID владельца файлов
    const currentFormComponent = shallowRef(null); // компонент формы (UserForm/CarForm)

    // ✅ СОСТОЯНИЕ НАСТРОЕК
    const dbFields = ref({ users: [], cars: [] }); // доступные поля в БД
    const settings = ref({}); // настройки компании и системы
    const visibleColumnsUsers = ref([]); // видимые колонки для таблицы пользователей
    const visibleColumnsCars = ref([]); // видимые колонки для таблицы машин
    const columnLabelsFromServer = ref({}); // названия колонок с сервера

    // ✅ ВЫЧИСЛЯЕМОЕ СВОЙСТВО: эффективные названия колонок
    // Комбинирует дефолтные названия с названиями с сервера
    const columnLabelsEffective = computed(() => ({
      ...COLUMN_LABELS_RU,
      ...(settings.value?.columnLabels || {}),
      ...columnLabelsFromServer.value
    }));

    // ✅ ВЫЧИСЛЯЕМОЕ СВОЙСТВО: видимые колонки (фильтруем чувствительные поля)
    const visibleColumnsEffective = computed(() => {
      const cols = currentTable.value === "users" ? visibleColumnsUsers.value : visibleColumnsCars.value;
      return (cols || []).filter(f => f && !SENSITIVE_FIELDS.includes(f));
    });

    /**
     * ✅ Загрузить настройки компании из сервера
     */
    async function loadSettings() {
      try {
        const r = await api.getSettings();
        if (r) {
          settings.value = r;
          visibleColumnsUsers.value = r.visibleColumnsUsers || [];
          visibleColumnsCars.value = r.visibleColumnsCars || [];
          columnLabelsFromServer.value = r.columnLabels || {};
        } else {
          console.warn("⚠️ Настройки не загружены, используется пусто объект");
          settings.value = {};
        }
      } catch (e) {
        console.error("❌ Ошибка загрузки настроек:", e);
        settings.value = {};
      }
    }

    /**
     * ✅ Загрузить доступные поля БД
     */
    async function loadDbFields() {
      try {
        dbFields.value = await api.getDbFields();
      } catch (e) {
        console.error("❌ Ошибка загрузки полей БД:", e);
      }
    }

    /**
     * ✅ Загрузить машины и отфильтровать свободные
     */
    async function loadCars() {
      try {
        const r = await api.getCars();
        cars.value = r || [];
        freeCars.value = r ? r.filter(c => c.status === "available") : [];
      } catch (e) {
        console.error("❌ Ошибка загрузки машин:", e);
      }
    }

    /**
     * ✅ Загрузить данные для активной таблицы (пользователи или машины)
     */
    async function loadTableData() {
      try {
        tableData.value = currentTable.value === "users" 
          ? await api.getUsers() 
          : await api.getCars();
      } catch (e) {
        console.error("❌ Ошибка загрузки данных таблицы:", e);
        tableData.value = [];
      }
    }

    /**
     * ✅ Загрузить ВСЕ данные при запуске приложения
     */
    async function loadAll() {
      await loadSettings();
      await loadDbFields();
      await loadCars();
      await loadTableData();
    }

    /**
     * ✅ Открыть модаль добавления новой записи
     */
    function openAddForm() {
      editingModel.value = {}; // пустая модель для новой записи
      currentFormComponent.value = markRaw(
        currentTable.value === "users" ? UserForm : CarForm
      );
      isFormVisible.value = true;
    }

    /**
     * ✅ Закрыть модаль формы
     */
    function closeForm() {
      isFormVisible.value = false;
      editingModel.value = {};
    }

    /**
     * ✅ Открыть модаль редактирования существующей записи
     */
    function onEditRow(row) {
      editingModel.value = { ...row }; // копируем данные строки
      currentFormComponent.value = markRaw(
        currentTable.value === "users" ? UserForm : CarForm
      );
      isFormVisible.value = true;
    }

    /**
     * ✅ Удалить запись с подтверждением
     */
    async function onDeleteRow(row) {
      if (!confirm("Вы уверены, что хотите удалить эту запись?")) return;
      try {
        currentTable.value === "users"
          ? await api.deleteUser(row._id)
          : await api.deleteCar(row._id);
        await loadCars();
        await loadTableData();
      } catch (e) {
        alert("❌ Ошибка удаления: " + e.message);
      }
    }

    /**
     * ✅ Открыть модаль управления файлами
     */
    function onOpenFiles(row) {
      filesOwnerType.value = currentTable.value === "users" ? "user" : "car";
      filesOwnerId.value = row._id;
      isFilesModalVisible.value = true;
    }

    /**
     * ✅ Закрыть модаль файлов
     */
    function closeFilesModal() {
      isFilesModalVisible.value = false;
      filesOwnerId.value = null;
      filesOwnerType.value = null;
    }

    /**
     * ✅ Обработчик события "сохранение формы"
     * Перезагружает машины и таблицу, закрывает форму
     */
    async function onFormSaved() {
      await loadCars();
      await loadTableData();
      closeForm();
    }

    /**
     * ✅ Обработчик события "сохранение настроек"
     * Обновляет локальные настройки и перезагружает таблицу
     */
    async function onSettingsSaved(updated) {
      if (updated) {
        settings.value = updated;
        visibleColumnsUsers.value = updated.visibleColumnsUsers || [];
        visibleColumnsCars.value = updated.visibleColumnsCars || [];
        columnLabelsFromServer.value = updated.columnLabels || {};
        await loadTableData();
      }
      isSettingsModalVisible.value = false;
    }

    // ✅ При монтировании компонента загружаем все данные
    onMounted(loadAll);

    return {
      currentTable, tableData, cars, freeCars, dbFields, settings,
      visibleColumnsUsers, visibleColumnsCars, columnLabelsEffective, visibleColumnsEffective,
      searchQuery, isSettingsModalVisible, isFormVisible, editingModel, currentFormComponent,
      isFilesModalVisible, filesOwnerType, filesOwnerId, loadTableData, openAddForm, closeForm,
      onEditRow, onDeleteRow, onOpenFiles, closeFilesModal, onFormSaved, onSettingsSaved
    };
  }
};
</script>

<style>
/* ✅ Сброс и базовые стили для центрирования */
* {
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}

/* ✅ Центрируем app-container через flexbox на #app */
#app {
  display: flex;
  align-items: center;      /* вертикаль */
  justify-content: center;  /* горизонталь */
  background: #f9fafb;
}

/* ✅ Сам контейнер */
.app-container {
  width: 100%;
  height: 100%;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #000;
  color: #00FFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* ✅ Остальные стили */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding-bottom: 12px;
  width: 100%;
}

.top-bar h1 {
  color: #00FFFF;
  border-left: 4px solid #00FFFF;
  font-size: 24px;
  margin: 0;
  padding-left: 12px;
}

.controls {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.controls input,
.controls select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  font-size: 14px;
}

.controls button {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s;
}

.controls button:hover {
  background: #2563eb;
}

/* ✅ Модальные окна */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  color: #00FFFF;
  background: #000;
  padding: 20px;
  border-radius: 12px;
  min-width: 400px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal.large {
  min-width: 700px;
}

.search-input {
  width: 300px;
}

.modal {
  width: 50%;
  border: 1px solid #00FFFF !important;
}

.modal h3, label, button, p {
  color: #00FFFF !important;
}

.modal button, input, select {
  outline: none !important;
  background-color: #000 !important;
  color: #00FFFF !important;
  border: 1px solid #00FFFF !important;
  border-radius: 4px !important;
}

.modal .col-section label:hover, button:hover {
  color: #000 !important;
  background-color: #00FFFF !important;
}

button {
  background-color: #000 !important;
  color: #00FFFF !important;
  border: 1px solid #00FFFF !important;
  border-radius: 4px !important;
}

button:hover {
  background-color: #00FFFF !important;
  color: #000 !important;
}

</style>