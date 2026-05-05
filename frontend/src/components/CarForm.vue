<template>
  <div>
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
