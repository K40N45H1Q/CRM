import { ref } from 'vue'

export const baseFields = {
  CAR: ['BRAND', 'MODEL', 'YEAR', 'VIN', 'PLATE', 'MILEAGE', 'CONDITION', 'STATUS'],
  PERSON: [
    'FULL NAME', 'PHONE', 'EMAIL', 
    'PASSPORT NUMBER', 'PASSPORT EXPIRY',
    'RESIDENCE STATUS', 'RESIDENCE EXPIRY',
    'LICENSE NUMBER', 'LICENSE EXPIRY',
    'AMOUNT', 'TERM', 'APR', 'CAR'
  ]
};

export const userGroup = ref(null)
export const currentType = ref("CAR")
export const isAuthenticated = ref(false)
export const isInitializing = ref(true)