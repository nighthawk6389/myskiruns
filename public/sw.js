// Offline support. Installing caches the app: the page, its scripts and styles,
// and every resort's trail data. Trail maps are cached as they're viewed (the
// app also asks for the other panels of the resort it opens: src/offline.ts),
// so a first visit doesn't download every resort's map. Pages are
// network-first (so a new deploy is picked up when online); everything else is
// cache-first.
//
// `vite build` fills in BUILD (vite.config.ts): a version that changes with
// every deploy and the built files to precache. Dev builds don't register the
// worker.
const BUILD = { version: 'dev', assets: [] };
const CACHE = `myskiruns-${BUILD.version}`;
const PRECACHE = ['/', '/manifest.webmanifest', '/icon-192.png', ...BUILD.assets];

const isMap = (url) => new URL(url).pathname.startsWith('/maps/');

/** Copy the maps an earlier version cached into this one, so a deploy doesn't
 * cost a phone its offline maps. Each is revalidated (a map can change between
 * seasons; an unchanged one costs a 304) and kept as it was if that fails. */
async function carryOverMaps(cache) {
  for (const key of await caches.keys()) {
    if (key === CACHE) continue;
    const old = await caches.open(key);
    for (const req of await old.keys()) {
      if (!isMap(req.url) || (await cache.match(req))) continue;
      const fresh = await fetch(req, { cache: 'no-cache' }).catch(() => null);
      const res = fresh && fresh.ok ? fresh : await old.match(req);
      if (res) await cache.put(req, res);
    }
  }
}

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      .then((c) => c.addAll(PRECACHE).then(() => carryOverMaps(c)))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== self.location.origin) return;
  // live data (trail conditions) always goes to the network
  if (url.pathname.startsWith('/api/')) return;

  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put('/', copy));
          return res;
        })
        .catch(() => caches.match('/')),
    );
    return;
  }

  event.respondWith(
    caches.match(req).then(
      (hit) =>
        hit ||
        fetch(req).then((res) => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        }),
    ),
  );
});
