let started = false;

/** Install the service worker (public/sw.js) once the first map is on screen
 * (main.tsx also starts it after a while, in case no map loads). It then
 * downloads every resort's data in the background, which shouldn't compete
 * with that map; and taking over the page while the map is still loading
 * would make the map download twice (React sets an image's src twice, and
 * the second request would go through the new worker). */
export function startOffline() {
  if (started || !import.meta.env.PROD || !('serviceWorker' in navigator)) return;
  started = true;
  navigator.serviceWorker.register('/sw.js').catch(() => {
    // offline caching is optional; the app works without it
  });
}

/** Puts every map panel of the open resort in the offline cache, not only the
 * one on screen: once Vail has been opened, all three of its panels work
 * without signal. The service worker (public/sw.js) caches what it serves, so
 * this asks it for the panels it doesn't have yet. Call it once the panel on
 * screen has loaded: asked for while that one is still downloading, the
 * worker would fetch it a second time. On a first visit the worker takes over
 * the page only after the page has loaded; this waits for it. */
export function keepForOffline(urls: string[]): () => void {
  if (!import.meta.env.PROD || !('serviceWorker' in navigator)) return () => {};
  const sw = navigator.serviceWorker;
  let timer = 0;
  const fetchMissing = () =>
    urls.forEach(async (u) => {
      try {
        if (await caches.match(u, { ignoreVary: true })) return;
        await fetch(u);
      } catch {
        // offline or storage blocked: the next visit tries again
      }
    });
  const start = () => {
    timer = window.setTimeout(fetchMissing, 3000);
  };
  if (sw.controller) start();
  else sw.addEventListener('controllerchange', start, { once: true });
  return () => {
    clearTimeout(timer);
    sw.removeEventListener('controllerchange', start);
  };
}
