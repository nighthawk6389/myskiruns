// Usage counts through Vercel Web Analytics: page views, plus a few custom
// events (what people do: open a resort, mark a run, share a day). No cookies
// and nothing that names a person; a shared day's link has its trip taken out
// of the URL before it is sent. Only builds made on Vercel turn it on
// (__ANALYTICS__, vite.config.ts): local builds and the browser checks send
// nothing. Custom events show in the dashboard on Vercel's paid plans; on the
// free plan they are dropped and page views still count.
import { inject, track as vercelTrack } from '@vercel/analytics';

declare const __ANALYTICS__: boolean;

const ON = typeof __ANALYTICS__ !== 'undefined' && __ANALYTICS__;

export function startAnalytics() {
  if (!ON) return;
  inject({
    mode: 'production',
    beforeSend: (event) => {
      const url = new URL(event.url);
      url.searchParams.delete('recap');
      return { ...event, url: url.toString() };
    },
  });
}

export type EventName =
  | 'Resort opened'
  | 'Run marked'
  | 'Trip created'
  | 'Summary opened'
  | 'Share dialog opened'
  | 'Recap shared'
  | 'Recap viewed'
  | 'Recap: track your own';

export function track(name: EventName, properties?: Record<string, string | number | boolean>) {
  if (!ON) return;
  try {
    vercelTrack(name, properties);
  } catch {
    // analytics must never get in the way
  }
}
