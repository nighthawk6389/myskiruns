import { createHash } from 'node:crypto'
import { readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'
import { defineConfig, type Connect, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { handleConditions, memoryStores } from './api/_lib/conditions'

// `vite` / `vite preview` serve /api/conditions from memory so the shared
// conditions votes work locally; on Vercel, api/conditions.ts serves it.
function localConditionsApi(): Connect.NextHandleFunction {
  const stores = memoryStores()
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
      const response = await handleConditions(request, stores)
      res.statusCode = response.status
      res.setHeader('content-type', 'application/json')
      res.end(await response.text())
    })
  }
}

// Fills in the BUILD line of the built public/sw.js: the scripts and styles to
// precache (every resort's data included, so any resort opens offline once the
// worker is installed) and a version that changes whenever any built file does
// (a new version replaces the old cache, keeping the maps a device has).
function serviceWorkerBuild(): Plugin {
  let outDir = 'dist'
  const files = (dir: string): string[] =>
    readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? files(join(dir, e.name)) : [join(dir, e.name)]))
  return {
    name: 'service-worker-build',
    apply: 'build',
    configResolved: (config) => void (outDir = resolve(config.root, config.build.outDir)),
    writeBundle(_, bundle) {
      const assets = Object.keys(bundle).filter((f) => /\.(js|css)$/.test(f)).sort().map((f) => `/${f}`)
      const sw = join(outDir, 'sw.js')
      const hash = createHash('sha256')
      for (const f of files(outDir).filter((f) => f !== sw).sort()) hash.update(relative(outDir, f)).update(readFileSync(f))
      const src = readFileSync(sw, 'utf8')
      const line = /^const BUILD = .*;$/m
      if (!line.test(src)) throw new Error('public/sw.js has no "const BUILD = ...;" line to fill in')
      const build = { version: hash.digest('hex').slice(0, 12), assets }
      writeFileSync(sw, src.replace(line, `const BUILD = ${JSON.stringify(build)};`))
    },
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
    serviceWorkerBuild(),
  ],
  build: {
    rollupOptions: {
      output: {
        // one chunk per resort (its trail list and overlays), loaded when the
        // resort is opened (src/resorts.ts)
        manualChunks: (id) => id.match(/\/src\/data\/resorts\/([^/]+)\//)?.[1],
      },
    },
  },
})
