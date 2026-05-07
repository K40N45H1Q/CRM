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
.settings-modal {
  padding: 22px;
  max-height: 85vh;
  overflow-y: auto;
  color: #e2e8f0;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.tabs button {
  padding: 10px 18px;
  border-radius: 14px;
  border: 1px solid rgba(56, 189, 248, 0.18);
  background: rgba(15, 23, 42, 0.9);
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tabs button:hover {
  background: rgba(56, 189, 248, 0.14);
}

.tabs button.active {
  color: #ffffff;
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(34, 197, 94, 0.18));
  border-color: rgba(56, 189, 248, 0.32);
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.f label {
  display: block;
  font-size: 0.9rem;
  color: #94a3b8;
  margin-bottom: 6px;
  font-weight: 600;
}

.f input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(100, 116, 139, 0.2);
  background: rgba(15, 23, 42, 0.92);
  color: #e2e8f0;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.f input:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.12);
}

.col-section {
  margin-bottom: 20px;
  padding: 18px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.92);
  border: 1px solid rgba(56, 189, 248, 0.14);
}

.col-section h3 {
  margin: 0 0 12px;
  font-size: 1rem;
  font-weight: 700;
  color: #ffffff;
}

.cols-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  max-height: 240px;
  overflow-y: auto;
  padding-right: 4px;
}

.chk {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 10px 12px;
  border-radius: 14px;
  transition: background 0.2s;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.12);
}

.chk:hover {
  background: rgba(56, 189, 248, 0.12);
}

.chk input[type="checkbox"] {
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.hint {
  margin-top: 12px;
  color: #94a3b8;
  font-size: 0.95rem;
  line-height: 1.6;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 22px;
}

.save,
.cancel {
  padding: 12px 18px;
  border-radius: 14px;
  border: 1px solid transparent;
  font-weight: 700;
  transition: all 0.2s ease;
}

.save {
  background: linear-gradient(135deg, #38bdf8, #22c55e);
  color: #020617;
}

.save:hover {
  filter: brightness(1.05);
}

.cancel {
  background: rgba(148, 163, 184, 0.12);
  color: #cbd5e1;
  border-color: rgba(148, 163, 184, 0.2);
}

.cancel:hover {
  background: rgba(148, 163, 184, 0.2);
}

.user-form {
  display: flex !important;
  flex-direction: column !important;
}

@media (max-width: 720px) {
  .grid,
  .cols-list {
    grid-template-columns: 1fr;
  }
}
</style>