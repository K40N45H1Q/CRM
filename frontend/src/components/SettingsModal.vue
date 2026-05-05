<template>
  <div class="settings-modal">
    <!-- ✅ Заголовок модали -->
    <h2>⚙️ Настройки системы</h2>

    <!-- ✅ Табы навигации -->
    <div class="tabs">
      <button :class="{active: tab==='general'}" @click="tab='general'">🏢 Компания</button>
      <button :class="{active: tab==='columns'}" @click="tab='columns'">📋 Колонки</button>
      <button :class="{active: tab==='contract'}" @click="tab='contract'">📊 Условия</button>
    </div>

    <!-- ✅ ТАБ 1: НАСТРОЙКИ КОМПАНИИ -->
    <div v-if="tab==='general'" class="tab-content">
      <!-- Данные компании: название, рег.номер, адрес, представитель, банковские реквизиты -->
      <div class="grid">
        <div class="f" v-for="key in ['companyName','registrationNo','legalAddress','representedBy','bank','swift','iban','phoneNumber','email']" :key="key">
          <label>{{ labels[key] || key }}</label>
          <input v-model="local[key]" />
        </div>
      </div>
    </div>

    <!-- ✅ ТАБ 2: ВЫБОР ВИДИМЫХ КОЛОНОК -->
    <div v-if="tab==='columns'" class="tab-content">
      <!-- Выбор колонок для таблицы пользователей -->
      <div class="col-section">
        <h3>👤 Пользователи</h3>
        <div class="cols-list">
          <label v-for="field in dbFields.users" :key="field" class="chk">
            <input type="checkbox" :value="field" v-model="local.visibleColumnsUsers">
            {{ labels[field] || field }}
          </label>
        </div>
      </div>

      <!-- Выбор колонок для таблицы машин -->
      <div class="col-section">
        <h3>🚗 Машины</h3>
        <div class="cols-list">
          <label v-for="field in dbFields.cars" :key="field" class="chk">
            <input type="checkbox" :value="field" v-model="local.visibleColumnsCars">
            {{ labels[field] || field }}
          </label>
        </div>
      </div>
    </div>

    <!-- ✅ ТАБ 3: УСЛОВИЯ ЛИЗИНГА ПО УМОЛЧАНИЮ -->
    <div v-if="tab==='contract'" class="tab-content">
      <div class="grid">
        <!-- Ставка лизинга по умолчанию -->
        <div class="f">
          <label>Ставка лизинга по умолчанию (%)</label>
          <input type="number" v-model.number="local.defaultLeaseRate" step="0.1" />
        </div>

        <!-- Первый взнос по умолчанию -->
        <div class="f">
          <label>Первый взнос по умолчанию (%)</label>
          <input type="number" v-model.number="local.defaultDownPaymentPercent" step="1" />
        </div>

        <!-- Комиссия за подготовку -->
        <div class="f">
          <label>Комиссия за подготовку (EUR)</label>
          <input type="number" v-model.number="local.defaultPreparationFee" step="1" />
        </div>
      </div>
      <p class="hint">
        💡 Эти параметры применяются автоматически при создании нового договора,
        если они не указаны явно в форме.
      </p>
    </div>

    <!-- ✅ Кнопки действия -->
    <div class="actions">
      <button class="save" @click="save">💾 Сохранить</button>
      <button class="cancel" @click="$emit('close')">✕ Закрыть</button>
    </div>
  </div>
</template>

<script>
/**
 * ✅ МОДАЛЬ НАСТРОЕК СИСТЕМЫ
 * 
 * Позволяет пользователю:
 * 1. Редактировать информацию о компании (название, реквизиты)
 * 2. Выбирать какие колонки видимы в таблицах
 * 3. Устанавливать условия лизинга по умолчанию
 */

import { ref, onMounted } from "vue";
import { api } from "../api";

export default {
  props: {
    dbFields: { type: Object, default: () => ({ users: [], cars: [] }) },
    visibleColumnsUsers: { type: Array, default: () => [] },
    visibleColumnsCars: { type: Array, default: () => [] },
    labels: { type: Object, default: () => ({}) },
    settings: { type: Object, default: () => ({}) },
  },
  emits: ["saved", "close"],
  setup(props, { emit }) {
    // ✅ Активный таб (general/columns/contract)
    const tab = ref("general")

    // ✅ Локальная копия настроек (защита от изменения родительских данных)
    const local = ref({
      ...props.settings,
      visibleColumnsUsers: Array.isArray(props.settings.visibleColumnsUsers)
        ? [...props.settings.visibleColumnsUsers]
        : [],
      visibleColumnsCars: Array.isArray(props.settings.visibleColumnsCars)
        ? [...props.settings.visibleColumnsCars]
        : [],
    })

    /**
     * ✅ Сохранить настройки на сервер
     */
    async function save() {
      try {
        // ✅ Отправляем обновленные настройки
        const updated = await api.updateSettings(local.value)
        // ✅ Уведомляем родителя об успешном сохранении
        emit("saved", updated)
      } catch (e) {
        alert("❌ Ошибка сохранения настроек: " + e.message)
        console.error("Save error:", e)
      }
    }

    return { tab, local, save }
  }
};
</script>

<style scoped>
/* ✅ Основной контейнер модали */
.settings-modal {
  padding: 15px;
  font-family: sans-serif;
  max-height: 85vh;
  overflow-y: auto;
}

/* ✅ Стили для табов навигации */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.tabs button {
  padding: 8px 16px;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.2s;
  font-size: 14px;
}

.tabs button:hover {
  opacity: 0.8;
}

.tabs button.active {
  opacity: 1;
  border-bottom: 2px solid #00FFFF;
  font-weight: bold;
  color: #007BFF;
}

/* ✅ Сетка для расположения элементов */
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

/* ✅ Стили для полей ввода */
.f label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
  font-weight: 500;
}

.f input {
  width: 100%;
  padding: 6px;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  transition: border 0.2s;
}

.f input:focus {
  outline: none;
  border-color: #007BFF;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

/* ✅ Секция с колонками */
.col-section {
  margin-bottom: 20px;
}

.col-section h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

/* ✅ Список для выбора колонок */
.cols-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  max-height: 250px;
  overflow-y: auto;
  padding-right: 5px;
}

/* ✅ Чекбокс с подписью */
.chk {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
  user-select: none;
}

.chk:hover {
  background: #f5f5f5;
}

.chk input[type="checkbox"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
}

/* ✅ Подсказка */
.hint {
  margin-top: 10px;
  color: #666;
  font-size: 13px;
  line-height: 1.4;
}

/* ✅ Кнопки действия */
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 15px;
}

.save,
.cancel {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.save {
  background: #007BFF;
  color: white;
}

.save:hover {
  background: #0056b3;
}

.cancel {
  background: #6c757d;
  color: white;
}

.cancel:hover {
  background: #5a6268;
}

/* ✅ Скроллбар для списка колонок */
.cols-list::-webkit-scrollbar {
  width: 6px;
}

.cols-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.cols-list::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.cols-list::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>