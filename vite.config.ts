import { defineConfig, type Connect } from 'vite'
import react from '@vitejs/plugin-react'
import { handleConditions, memoryStore } from './api/_lib/conditions'

// `vite` / `vite preview` serve /api/conditions from memory so the shared
// conditions votes work locally; on Vercel, api/conditions.ts serves it.
function localConditionsApi(): Connect.NextHandleFunction {
  const store = memoryStore()
  return (req, res, next) => {
    if (!req.url?.startsWith('/api/conditions')) return next()
    const chunks: Buffer[] = []
    req.on('data', (c: Buffer) => chunks.push(c))
    req.on('end', async () => {
      const request = new Request(`http://localhost${req.url}`, {
        method: req.method,
        headers: { 'content-type': 'application/json' },
        body: req.method === 'POST' ? Buffer.concat(chunks).toString() : undefined,
      })
      const response = await handleConditions(request, store)
      res.statusCode = response.status
      res.setHeader('content-type', 'application/json')
      res.end(await response.text())
    })
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'local-conditions-api',
      configureServer: (server) => void server.middlewares.use(localConditionsApi()),
      configurePreviewServer: (server) => void server.middlewares.use(localConditionsApi()),
    },
  ],
})
