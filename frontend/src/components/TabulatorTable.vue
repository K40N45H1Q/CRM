<template>
  <div ref="tableElement" style="width:100%"></div>
</template>

<script>
import { onMounted, ref, watch, onBeforeUnmount, computed } from 'vue'
import { TabulatorFull as Tabulator } from 'tabulator-tables'
// ✅ Импорт официальной тёмной темы midnight
import 'tabulator-tables/dist/css/tabulator_midnight.min.css'

export default {
  name: 'TabulatorTable',
  props: {
    data: { type: Array, default: () => [] },
    visibleColumns: { type: Array, default: () => [] },
    columnLabels: { type: Object, default: () => ({}) },
    cars: { type: Array, default: () => [] },
    globalSearch: { type: String, default: '' },
    tableType: { type: String, default: 'users' }
  },
  emits: ['edit', 'delete', 'files'],
  setup(props, { emit }) {
    const tableElement = ref(null)
    let tableInstance = null

    /**
     * ✅ ФИЛЬТРАЦИЯ ДАННЫХ ДО TABULATOR — БЕЗОПАСНО И НАДЁЖНО
     * Никаких clearFilter/setFilter — фильтрация в Vue, Tabulator получает чистые данные
     */
    const filteredData = computed(() => {
      const q = (props.globalSearch || '').trim().toLowerCase()
      if (!q) return props.data

      return props.data.filter(row => {
        const fields = props.visibleColumns?.length
          ? props.visibleColumns
          : Object.keys(row).filter(k => k !== '_id')

        return fields.some(f => {
          let val = row[f]
          if (f === 'carId') {
            const c = props.cars.find(x => x._id === val)
            val = c ? `${c.makeModel} (${c.plate})` : val || ''
          }
          return val !== null && val !== undefined && String(val).toLowerCase().includes(q)
        })
      })
    })

    /**
     * ✅ Построение колонок
     */
    const buildColumns = () => {
      const cols = []
      const fields = props.tableType === 'cars'
        ? ['makeModel', 'yearOfManufacture', 'vin', 'plate', 'mileage', 'cost', 'status']
        : props.visibleColumns

      fields.forEach(f => {
        if (!f) return
        if (f === 'paymentDate') {
          cols.push({
            title: props.columnLabels[f] || 'Дата платежа',
            field: f,
            formatter: (cell) => {
              const v = cell.getValue()
              if (!v) return '-'
              try { return new Date(v).toLocaleDateString('ru-RU') }
              catch (e) { return v }
            }
          })
        } else if (f === 'status' && props.tableType === 'cars') {
          cols.push({
            title: props.columnLabels[f] || 'Статус',
            field: f,
            formatter: (cell) => {
              const v = cell.getValue()
              if (v === 'available') return '✅ Свободна'
              if (v === 'busy') return '🔒 Занята'
              return v || '-'
            }
          })
        } else {
          cols.push({
            title: props.columnLabels[f] || f,
            field: f
          })
        }
      })

      // Колонка "Действия"
      cols.push({
        title: 'Действия',
        field: '_actions',
        formatter: () => '<button class="t-edit">✏️</button> <button class="t-del">🗑️</button> <button class="t-files">📎</button>',
        hozAlign: 'center',
        width: 150,
        headerSort: false,
        cellClick: (e, cell) => {
          const row = cell.getRow().getData()
          if (e.target.closest('.t-edit')) emit('edit', row)
          if (e.target.closest('.t-del')) emit('delete', row)
          if (e.target.closest('.t-files')) emit('files', row)
        }
      })

      return cols
    }

    /**
     * ✅ Создание таблицы
     */
    const buildTable = () => {
      if (tableInstance) {
        tableInstance.destroy()
        tableInstance = null
      }
      if (!tableElement.value) return

      tableInstance = new Tabulator(tableElement.value, {
        data: filteredData.value,
        layout: 'fitColumns',
        columns: buildColumns(),
        height: '520px',
        placeholder: 'Нет данных',
        // ✅ Дополнительные опции для тёмной темы
        rowHeight: 36,
        resizableColumns: true,
      })
    }

    onMounted(buildTable)

    // 🔥 Пересоздаём таблицу при изменении данных / колонок / поиска
    watch(() => [props.data, props.visibleColumns, props.globalSearch], buildTable, { deep: true })

    onBeforeUnmount(() => {
      if (tableInstance) tableInstance.destroy()
    })

    return { tableElement }
  }
}
</script>

<style>
/* ✅ CYBER-AQUA АКЦЕНТЫ ПОВЕРХ ТЕМЫ MIDNIGHT */

/* Границы и текст — циановые */
.tabulator,
.tabulator-header,
.tabulator-col,
.tabulator-cell {
  border-color: #00FFFF !important;
  color: #00FFFF !important;
}

/* Заголовки колонок */
.tabulator-col {
  background: #0a0a0a !important;
  font-weight: bold;
  text-align: center !important;
}

/* Чередование строк */
.tabulator-row:nth-child(even) {
  background: #0a0a0a !important;
}
.tabulator-row:nth-child(odd) {
  background: #000 !important;
}

/* Поля ввода внутри ячеек (редактирование) */
.tabulator-cell input,
.tabulator-cell select,
.tabulator-editor input,
.tabulator-editor select {
  background: #000 !important;
  color: #00FFFF !important;
  border: 1px solid #00FFFF !important;
}

/* Чекбоксы */
input[type="checkbox"] {
  accent-color: #00FFFF;
  cursor: pointer;
}

/* Выпадающий список редактора */
.tabulator-edit-list {
  background: #000 !important;
  border: 1px solid #00FFFF !important;
}
.tabulator-edit-list-item {
  color: #00FFFF !important;
}
.tabulator-edit-list-item:hover {
  background: #00FFFF !important;
  color: #000 !important;
}

/* Меню колонок */
.tabulator-menu {
  background: #000 !important;
  border: 1px solid #00FFFF !important;
}
.tabulator-menu-item {
  color: #00FFFF !important;
}
.tabulator-menu-item:hover {
  background: #00FFFF !important;
  color: #000 !important;
}

/* Плейсхолдер "Нет данных" */
.tabulator-placeholder span {
  color: rgba(0, 255, 255, 0.5) !important;
  font-size: 14px !important;
}

/* ✅ КНОПКИ ДЕЙСТВИЙ */
.t-edit,
.t-del,
.t-files {
  cursor: pointer;
  border: 1px solid #00FFFF;
  background: transparent;
  color: #00FFFF !important;
  font-size: 14px;
  padding: 2px 8px;
  margin: 0 2px;
  border-radius: 4px;
  transition: all 0.15s;
}

.t-edit:hover,
.t-del:hover,
.t-files:hover {
  background: #00FFFF !important;
  color: #000 !important;
  transform: scale(1.05);
}

/* ✅ СКРОЛЛБАР */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #000;
}
::-webkit-scrollbar-thumb {
  background: #00FFFF;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #00cccc;
}
</style>