<template>
  <div class="user-form">
    <h2>{{ isEditMode ? "🔄 Редактировать клиента" : "➕ Новый клиент" }}</h2>
    
    <!-- ✅ СЕКЦИЯ 1: Личные данные -->
    <div class="section">
      <h3>👤 Личные данные</h3>
      <div class="field"><label>ФИО *</label><input v-model="local.fullName" required /></div>
      <div class="field"><label>PIN / ID</label><input v-model="local.pin" /></div>
      <div class="field"><label>Номер паспорта/ID</label><input v-model="local.documentNumber" /></div>
      <div class="field"><label>Телефон</label><input v-model="local.phoneNumber" /></div>
      <div class="field"><label>Email</label><input v-model="local.email" /></div>
      <div class="field"><label>Декларированный адрес</label><input v-model="local.declaredAddress" /></div>
      <div class="field"><label>Фактический адрес</label><input v-model="local.residentialAddress" /></div>
    </div>

    <!-- ✅ СЕКЦИЯ 2: Банковские реквизиты -->
    <div class="section">
      <h3>🏦 Банковские реквизиты</h3>
      <div class="field"><label>Банк</label><input v-model="local.bank" /></div>
      <div class="field"><label>SWIFT</label><input v-model="local.swift" /></div>
      <div class="field"><label>IBAN</label><input v-model="local.iban" /></div>
    </div>

    <!-- ✅ СЕКЦИЯ 3: Договор и платежи -->
    <div class="section">
      <h3>🚗 Договор и платежи</h3>
      
      <div class="field">
        <label>Выбрать машину</label>
        <select v-model="local.carId">
          <option value="">-- Не выбрано --</option>
          <option v-for="car in freeCars" :key="car._id" :value="car._id">
            {{ car.makeModel }} ({{ car.plate }}) - {{ car.cost }} EUR
          </option>
        </select>
      </div>
      
      <div class="field"><label>Срок (мес.)</label><input type="number" v-model.number="local.agreementDuration" /></div>
      
      <div class="field">
        <label>Статус платежа</label>
        <select v-model="local.status" @change="onStatusChange">
          <option value="В ожидании">⏳ В ожидании</option>
          <option value="Просрочено">⚠️ Просрочено</option>
          <option value="Оплачено">✅ Оплачено</option>
          <option value="Закрыт">🔒 Закрыт</option>
        </select>
      </div>
      
      <div class="field"><label>Дата следующего платежа</label><input type="date" v-model="local.paymentDate" /></div>
      
      <!-- ❌ ПОЛЯ Ставка/Взнос УБРАНЫ — берутся только из настроек системы -->
      <!-- В local они есть, уходят на сервер, но в UI не рендерятся -->
    </div>

    <div class="actions">
      <button class="save" @click="saveModel">💾 Сохранить</button>
      <button class="cancel" @click="$emit('cancel')">❌ Отмена</button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from "vue";
import { api } from "../api";

export default {
  name: "UserForm",
  props: {
    model: { type: Object, default: () => ({}) },
    freeCars: { type: Array, default: () => [] },
    // ✅ Дефолты из настроек (применяются только к НОВЫМ записям, в фоне)
    defaults: { type: Object, default: () => ({}) }
  },
  emits: ["saved", "cancel"],
  setup(props, { emit }) {
    // ✅ Инициализация: дефолты из настроек — только для новых записей, только в данные
    const local = ref({
      ...( !props.model._id ? {
        leaseRate: props.defaults?.defaultLeaseRate ?? 0,
        downPayment: props.defaults?.defaultDownPaymentPercent ?? 0,
        preparationFee: props.defaults?.defaultPreparationFee ?? 0
      } : {}),
      ...props.model,
      status: props.model.status || "В ожидании"
    });

    const isEditMode = computed(() => !!local.value._id);

    function onStatusChange() {
      if (local.value.status === "Оплачено" && isEditMode.value) {
        const monthly = local.value.monthlyPayment || 0;
        const debt = local.value.debtRemaining || 0;
        const newDebt = Math.round((debt - monthly) * 100) / 100;
        
        local.value.debtRemaining = newDebt;
        local.value.paidAmount = Math.round(((local.value.paidAmount || 0) + monthly) * 100) / 100;
        local.value.lastPaymentDate = new Date().toISOString().split('T')[0];
        
        if (newDebt <= 0) {
          // Полностью погашено
          local.value.status = "Закрыт";
          local.value.debtRemaining = 0;
          local.value.paidAmount = local.value.totalAmount || 0;
        } else {
          // Переместить дату платежа на следующий месяц
          if (local.value.paymentDate) {
            const pDate = new Date(local.value.paymentDate);
            pDate.setMonth(pDate.getMonth() + 1);
            local.value.paymentDate = pDate.toISOString().split('T')[0];
          }
        }
      }
    }

    async function saveModel() {
      if (!local.value.fullName) {
        return alert("ФИО клиента обязательно!");
      }
      try {
        if (isEditMode.value) {
          const updated = await api.updateUser(local.value._id, local.value);
          Object.assign(local.value, updated);
        } else {
          await api.createUser(local.value);
        }
        emit("saved");
      } catch (e) {
        alert("Ошибка при сохранении: " + e.message);
        console.error("Save error:", e);
      }
    }

    return { local, saveModel, isEditMode, onStatusChange };
  }
};
</script>

<style scoped>
.user-form {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
  color: #1f2937;
}

.user-form h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 600;
  padding-bottom: 16px;
}

.section {
  margin-bottom: 24px;
  padding: 20px;
  background: #000;
  border: 1px solid #00FFFF;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.section h3 {
  margin: 0 0 16px 0;
  font-size: 15px;
  font-weight: 600;
  color: #374151;
  padding-bottom: 10px;
}

/* ✅ СТРОГО: 1 ПОЛЕ = 1 СТРОКА */
.field {
  margin-bottom: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field:last-child { margin-bottom: 0; }

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

.field input:disabled {
  background: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
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
  .user-form { padding: 12px; }
  .save, .cancel { width: 100%; justify-content: center; }
  .actions { flex-direction: column; }
}

* {
  color: #00FFFF;
}

</style>