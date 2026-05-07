import { fileURLToPath, URL } from 'node:url'
import fs from 'fs'
import path from 'path'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const sslPath = path.resolve(process.cwd(), '..', 'ssl')

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },

  server: {
    host: true,

    https: {
      key: fs.readFileSync(path.join(sslPath, 'localhost-key.pem')),
      cert: fs.readFileSync(path.join(sslPath, 'localhost.pem')),
    }
  }
})