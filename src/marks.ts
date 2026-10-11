// A run marked skied (or unmarked) counts toward the season's tallies across
// every resort (api/marks.ts, api/_lib/season.ts): anonymous, once per device,
// trail and day, for rankings of the season's most-skied runs. Sent and
// forgotten: offline, or with no server set up, the mark simply isn't counted;
// the trip itself is unaffected.
import { deviceId } from './hooks/useConditions';

export function reportMark(resort: string, trailId: string, marked: boolean) {
  let device: string;
  try {
    device = deviceId();
  } catch {
    return; // storage blocked: no stable device to count once a day
  }
  fetch('/api/marks', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ resort, trailId, deviceId: device, marked }),
    keepalive: true,
  }).catch(() => {});
}
