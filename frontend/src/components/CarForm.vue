<template>
  <div class="car-form">
    <!-- ✅ Заголовок формы -->
    <h2>{{ isEditMode ? "🔄 Редактировать машину" : "➕ Добавить машину" }}</h2>

    <!-- ✅ Форма для ввода данных машины -->
    <div class="form-grid">
      <!-- Марка и модель -->
      <div class="field">
        <label>Марка и модель *</label>
        <input v-model="localModel.makeModel" required />
      </div>

      <!-- Год выпуска -->
      <div class="field">
        <label>Год выпуска</label>
        <input type="number" v-model.number="localModel.yearOfManufacture" />
      </div>

      <!-- VIN код -->
      <div class="field">
        <label>VIN</label>
        <input v-model="localModel.vin" />
      </div>

      <!-- Гос. номер -->
      <div class="field">
        <label>Гос. номер</label>
        <input v-model="localModel.plate" />
      </div>

      <!-- Пробег -->
      <div class="field">
        <label>Пробег (км)</label>
        <input type="number" v-model.number="localModel.mileage" />
      </div>

      <!-- Цена -->
      <div class="field">
        <label>Цена (EUR) *</label>
        <input type="number" v-model.number="localModel.cost" required />
      </div>

      <!-- Статус -->
      <div class="field">
        <label>Статус</label>
        <select v-model="localModel.status">
          <option value="available">✅ Свободна</option>
          <option value="busy">🔒 Занята</option>
        </select>
      </div>
    </div>

    <!-- ✅ Кнопки действия -->
    <div class="actions">
      <button class="save" @click="saveModel">💾 Сохранить</button>
      <button class="cancel" @click="$emit('cancel')">❌ Отмена</button>
    </div>
  </div>
</template>

<script>
/**
 * ✅ ФОРМА ДЛЯ ДОБАВЛЕНИЯ И РЕДАКТИРОВАНИЯ МАШИН
 */

import { ref, computed } from "vue";
import { api } from "../api";

export default {
  name: "CarForm",

  props: {
    model: { type: Object, default: () => ({}) },
  },

  emits: ["saved", "cancel"],

  setup(props, { emit }) {
    // ✅ Локальная копия данных машины
    const localModel = ref({ ...props.model });

    // ✅ Флаг для проверки, редактируем ли мы существующую машину
    const isEditMode = computed(() => !!localModel.value._id);

    /**
     * ✅ Сохранить машину в базу данных
     * 
     * Логика:
     * 1. Если редактируем - отправляем PUT запрос
     * 2. Если создаем новую - отправляем POST запрос
     * 3. Уведомляем родителя об успешном сохранении
     */
    async function saveModel() {
      try {
        if (isEditMode.value) {
          // ✅ Обновление существующей машины
          await api.updateCar(localModel.value._id, localModel.value);
        } else {
          // ✅ Создание новой машины
          await api.createCar(localModel.value);
        }
        // ✅ Уведомляем родителя об успешном сохранении
        emit("saved");
      } catch (e) {
        alert("❌ Ошибка при сохранении машины: " + e.message);
        console.error("Save error:", e);
      }
    }

    return { localModel, saveModel, isEditMode };
  },
};
</script>

<style scoped>
.car-form {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
  color: #1f2937;
}

.car-form h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
  padding-bottom: 16px;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
}

.field input,
.field select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.field input:focus,
.field select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
}

.save,
.cancel {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.save {
  background: #3b82f6;
  color: white;
}
.save:hover { background: #2563eb; }

.cancel {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}
.cancel:hover { background: #e5e7eb; }

@media (max-width: 768px) {
  .car-form { padding: 12px; }
  .save, .cancel { width: 100%; justify-content: center; }
}
</style>
