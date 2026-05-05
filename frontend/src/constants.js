/**
 * ✅ КОНСТАНТЫ ПРИЛОЖЕНИЯ
 * 
 * Содержит:
 * - Русские названия всех полей
 * - Список чувствительных полей (не показываются в таблице)
 */

/**
 * ✅ РУССКИЕ НАЗВАНИЯ ПОЛЕЙ
 * 
 * Используется для отображения названий колонок в таблице и форме
 * Чтобы добавить новое поле:
 * 1. Добавьте строку вида: fieldName: "Русское название"
 * 2. Поле будет автоматически отображаться в таблице, если оно в видимых колонках
 */
export const COLUMN_LABELS_RU = {
  // 👤 ЛИЧНЫЕ ДАННЫЕ
  fullName: "ФИО",
  pin: "PIN",
  documentNumber: "Номер документа",
  declaredAddress: "Декларированный адрес",
  residentialAddress: "Фактический адрес",

  // 🏦 БАНКОВСКИЕ РЕКВИЗИТЫ
  bank: "Банк",
  swift: "SWIFT",
  iban: "IBAN",

  // 📞 КОНТАКТЫ
  phoneNumber: "Телефон",
  email: "E-mail",

  // 🚗 СВЯЗЬ С МАШИНОЙ
  carId: "Машина",

  // 📄 ДОГОВОР
  status: "Статус",
  agreementNumber: "Номер договора",
  signingDate: "Дата заключения",
  expirationDate: "Дата окончания",
  agreementDuration: "Срок (мес.)",
  paymentDate: "Дата платежа",
  lastPaymentDate: "Последний платёж",

  // 💰 ФИНАНСЫ
  leaseRate: "Ставка (%)",
  downPayment: "Первый взнос (%)",
  downPaymentAmount: "Взнос (EUR)",
  monthlyPayment: "Платёж (EUR)",
  preparationFee: "Сбор (EUR)",
  totalAmount: "Общая сумма (EUR)",
  paidAmount: "Оплачено (EUR)",
  debtRemaining: "Остаток (EUR)",

  // 🚗 ХАРАКТЕРИСТИКИ МАШИНЫ
  makeModel: "Марка и модель",
  yearOfManufacture: "Год выпуска",
  vin: "VIN",
  plate: "Гос. номер",
  mileage: "Пробег",
  cost: "Цена (EUR)",
};

/**
 * ✅ ЧУВСТВИТЕЛЬНЫЕ ПОЛЯ
 * 
 * Эти поля НЕ показываются в таблице при выборе видимых колонок
 * Это защита приватных данных (VIN, PIN, IBAN, SWIFT)
 */
export const SENSITIVE_FIELDS = ["vin", "pin", "iban", "swift"];