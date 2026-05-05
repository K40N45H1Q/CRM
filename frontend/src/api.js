/**
 * ✅ API КЛИЕНТ
 * 
 * Содержит все функции для взаимодействия с REST API
 * Базовый URL: http://localhost:8000
 */

const API_BASE = "http://localhost:8000";

/**
 * ✅ Универсальная функция для отправки HTTP запросов
 * @param {string} path - путь к API endpoint (начиная с /)
 * @param {object} options - параметры fetch (method, headers, body и т.д.)
 * @returns {Promise} - распарсенный JSON ответ или ошибка
 */
async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  // ✅ ===== ПОЛЬЗОВАТЕЛИ =====
  
  /**
   * Получить список всех пользователей
   * GET /users
   */
  getUsers: () => request("/users"),

  /**
   * Создать нового пользователя
   * POST /users
   * @param {object} p - данные пользователя
   */
  createUser: (p) => request("/users", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p)
  }),

  /**
   * Обновить пользователя
   * PUT /users/{id}
   * @param {string} id - ID пользователя
   * @param {object} p - обновленные данные
   */
  updateUser: (id, p) => request(`/users/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p)
  }),

  /**
   * Удалить пользователя
   * DELETE /users/{id}
   * @param {string} id - ID пользователя
   */
  deleteUser: (id) => request(`/users/${id}`, { method: "DELETE" }),

  // ✅ ===== МАШИНЫ =====

  /**
   * Получить список всех машин
   * GET /cars
   */
  getCars: () => request("/cars"),

  /**
   * Получить список свободных машин
   * GET /cars/available
   */
  getAvailableCars: () => request("/cars/available"),

  /**
   * Создать новую машину
   * POST /cars
   * @param {object} p - данные машины
   */
  createCar: (p) => request("/cars", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p)
  }),

  /**
   * Обновить машину
   * PUT /cars/{id}
   * @param {string} id - ID машины
   * @param {object} p - обновленные данные
   */
  updateCar: (id, p) => request(`/cars/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p)
  }),

  /**
   * Удалить машину
   * DELETE /cars/{id}
   * @param {string} id - ID машины
   */
  deleteCar: (id) => request(`/cars/${id}`, { method: "DELETE" }),

  // ✅ ===== НАСТРОЙКИ =====

  /**
   * Получить настройки компании
   * GET /company-lease-settings
   */
  getSettings: () => request("/company-lease-settings"),

  /**
   * Обновить настройки компании
   * PUT /company-lease-settings
   * @param {object} p - новые настройки
   */
  updateSettings: (p) => request("/company-lease-settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(p)
  }),

  // ✅ ===== ИНФОРМАЦИЯ =====

  /**
   * Получить доступные поля в БД
   * GET /db-fields
   */
  getDbFields: () => request("/db-fields"),

  /**
   * Получить шаблонные переменные для документов
   * GET /template-placeholders
   */
  getTemplatePlaceholders: () => request("/template-placeholders"),

  // ✅ ===== ФАЙЛЫ =====

  /**
   * Загрузить файл
   * POST /upload
   * @param {FormData} formData - данные файла (ownerId, ownerType, file)
   */
  uploadFile: (formData) => fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData
  }).then(async r => r.ok ? r.json() : Promise.reject(new Error(`Upload ${r.status}: ${await r.text()}`))),

  /**
   * Получить список файлов владельца
   * GET /files/{ownerType}/{ownerId}
   * @param {string} ot - тип владельца (user/car)
   * @param {string} oid - ID владельца
   */
  listFiles: (ot, oid) => request(`/files/${ot}/${oid}`),

  /**
   * Удалить файл
   * DELETE /files/{id}
   * @param {string} id - ID файла
   */
  deleteFile: (id) => request(`/files/${id}`, { method: "DELETE" }),
};