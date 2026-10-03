/** Puts every map panel of the open resort in the offline cache, not only the
 * one on screen: once Vail has been opened, all three of its panels work
 * without signal. The service worker (public/sw.js) caches what it serves, so
 * this asks for them through it, a few seconds after the resort opens so the
 * panel on screen loads first. On a first visit the worker takes over the page
 * only after the page has loaded; this waits for it. */
export function keepForOffline(urls: string[]): () => void {
  if (!import.meta.env.PROD || !('serviceWorker' in navigator)) return () => {};
  const sw = navigator.serviceWorker;
  let timer = 0;
  const start = () => {
    timer = window.setTimeout(() => urls.forEach((u) => void fetch(u).catch(() => {})), 3000);
  };
  if (sw.controller) start();
  else sw.addEventListener('controllerchange', start, { once: true });
  return () => {
    clearTimeout(timer);
    sw.removeEventListener('controllerchange', start);
  };
}
