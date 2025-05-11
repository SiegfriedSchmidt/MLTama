import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react-swc'
import tsconfigPaths from "vite-tsconfig-paths"
import * as fs from "fs";

// https://vitejs.dev/config/

const production = process.env.NODE_ENV === 'production';

export default defineConfig({
  server: {
    port: 8000,
    host: '0.0.0.0',
    https: production ? {} : {
      cert: fs.readFileSync('../certs/server-cert.pem'),
      key: fs.readFileSync('../certs/server-key.pem')
    },
  },
  esbuild: {
    supported: {
      'top-level-await': true
    },
  },
  base: production ? '/static/' : '/',
  plugins: [react(), tsconfigPaths()],
})
