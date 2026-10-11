import { createHash } from 'node:crypto'
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'
import { defineConfig, loadEnv, transformWithEsbuild, type Connect, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { accountEnv, handleAccount } from './api/_lib/account'
import { handleConditions, memoryStores } from './api/_lib/conditions'

// `vite` / `vite preview` serve /api/conditions from memory so the shared
// conditions votes work locally, and /api/account against the Supabase project
// in .env.local or the shell (api/_lib/account.ts); on Vercel, api/*.ts serve
// them.
function localApi(env: Record<string, string | undefined>): Connect.NextHandleFunction {
  const stores = memoryStores()
  return (req, res, next) => {
    const route = req.url?.startsWith('/api/conditions') ? 'conditions' : req.url?.startsWith('/api/account') ? 'account' : null
    if (!route) return next()
    const chunks: Buffer[] = []
    req.on('data', (c: Buffer) => chunks.push(c))
    req.on('end', async () => {
      const request = new Request(`http://localhost${req.url}`, {
        method: req.method,
        headers: { 'content-type': 'application/json', authorization: req.headers.authorization ?? '' },
        body: req.method === 'POST' ? Buffer.concat(chunks).toString() : undefined,
      })
      const response =
        route === 'conditions' ? await handleConditions(request, stores) : await handleAccount(request, accountEnv(env))
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
// `skip`: built files that are never loaded, so not worth downloading.
function serviceWorkerBuild(skip: RegExp | null): Plugin {
  let outDir = 'dist'
  const files = (dir: string): string[] =>
    readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? files(join(dir, e.name)) : [join(dir, e.name)]))
  return {
    name: 'service-worker-build',
    apply: 'build',
    configResolved: (config) => void (outDir = resolve(config.root, config.build.outDir)),
    writeBundle(_, bundle) {
      const assets = Object.keys(bundle)
        .filter((f) => /\.(js|css)$/.test(f) && !skip?.test(f))
        .sort()
        .map((f) => `/${f}`)
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

// Writes dist/preview/<id>.json for each resort in src/resorts.ts: its name,
// its trails' ids and ratings, and each map panel's image and overlays. The
// link-preview functions (api/preview.ts, api/og.ts) read it to title a shared
// link and draw its picture, without loading the app's own bundles.
function previewData(): Plugin {
  let root = '.'
  let outDir = 'dist'
  return {
    name: 'preview-data',
    apply: 'build',
    configResolved: (config) => {
      root = config.root
      outDir = resolve(config.root, config.build.outDir)
    },
    async writeBundle() {
      const src = readFileSync(join(root, 'src/resorts.ts'), 'utf8')
      const q = `(?:'((?:[^'\\\\]|\\\\.)*)'|"([^"]*)")`
      const head = new RegExp(`\\n  (oneMap|panels)\\('([a-z0-9-]+)', ${q}, ${q}`, 'g')
      const unq = (a?: string, b?: string) => (a ?? b ?? '').replace(/\\'/g, "'")
      const out = join(outDir, 'preview')
      mkdirSync(out, { recursive: true })
      const entries = [...src.matchAll(head)]
      for (const [i, m] of entries.entries()) {
        const [, kind, id] = m
        const block = src.slice(m.index, entries[i + 1]?.index ?? src.length)
        const dir = join(root, 'src/data/resorts', id)
        const code = (await transformWithEsbuild(readFileSync(join(dir, 'trails.ts'), 'utf8'), 'trails.ts', { loader: 'ts', format: 'esm' })).code
        const { trails } = (await import(`data:text/javascript;base64,${Buffer.from(code).toString('base64')}`)) as {
          trails: { id: string; difficulty: string }[]
        }
        const panels =
          kind === 'panels'
            ? [...block.matchAll(/\{ id: '([^']+)', name: (?:'([^']*)'|"([^"]*)")/g)].map((p) => ({
                id: p[1],
                name: p[2] ?? p[3],
                map: `/maps/${id}-${p[1]}.jpg`,
                file: join(dir, 'panels', p[1], 'trailPaths.json'),
              }))
            : [{ id: 'map', name: 'Trail map', map: `/maps/${id}.jpg`, file: join(dir, 'trailPaths.json') }]
        const data = {
          id,
          name: unq(m[3], m[4]),
          region: unq(m[5], m[6]),
          trails: Object.fromEntries(trails.map((t) => [t.id, t.difficulty])),
          panels: panels.map(({ file, ...p }) => ({ ...p, paths: JSON.parse(readFileSync(file, 'utf8')).trails })),
        }
        writeFileSync(join(out, `${id}.json`), JSON.stringify(data))
      }
      if (entries.length < 2) throw new Error('preview-data: no resorts found in src/resorts.ts')
    },
  }
}

// the Supabase project for accounts: VITE_SUPABASE_* or, as Vercel's Supabase
// integration names them, NEXT_PUBLIC_SUPABASE_* (src/account/account.ts)
const ENV_PREFIX = ['VITE_', 'NEXT_PUBLIC_']

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // every variable, for the local API; the app itself only sees ENV_PREFIX ones
  const env = { ...loadEnv(mode, process.cwd(), ''), ...process.env }
  const accounts = Boolean(env.VITE_SUPABASE_URL || env.NEXT_PUBLIC_SUPABASE_URL)
  return {
    plugins: [
      react(),
      {
        name: 'local-api',
        configureServer: (server) => void server.middlewares.use(localApi(env)),
        configurePreviewServer: (server) => void server.middlewares.use(localApi(env)),
      },
      previewData(),
      // without accounts the Supabase client is never loaded
      serviceWorkerBuild(accounts ? null : /^assets\/supabase-/),
    ],
    envPrefix: ENV_PREFIX,
    // usage counts (src/analytics.ts) only from builds made on Vercel
    define: { __ANALYTICS__: JSON.stringify(Boolean(process.env.VERCEL)) },
    build: {
      rollupOptions: {
        output: {
          // one chunk per resort (its trail list and overlays), loaded when the
          // resort is opened (src/resorts.ts); the Supabase client, loaded only
          // when accounts are set up (src/account/account.ts)
          manualChunks: (id) =>
            id.match(/\/src\/data\/resorts\/([^/]+)\//)?.[1] ??
            (id.includes('/node_modules/@supabase/') ? 'supabase' : undefined),
        },
      },
    },
  }
})
