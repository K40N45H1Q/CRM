import { ref } from 'vue'

export const apiBase = 'http://localhost:8000/api'

export const baseFields = {
  CAR: [
    'Brand', 'Model', 'YEAR',
    'VIN', 'PLATE', 'MILEAGE',
    'CONDITION', 'INITIAL DEPOSIT', 'STATUS'],
  PERSON: [
    'NAME', 'SURNAME', 'PHONE', 'EMAIL', 
    'PASSPORT NUMBER', 'PASSPORT EXPIRY',
    'RESIDENCE STATUS', 'RESIDENCE EXPIRY',
    'LICENSE NUMBER', 'LICENSE EXPIRY',
    'AMOUNT', 'TERM', 'APR', 'CAR', 'TYPE OF DEAL'
  ]
};

export const userGroup = ref(null)
export const currentType = ref("CAR")
export const isAuthenticated = ref(false)
export const isInitializing = ref(true)