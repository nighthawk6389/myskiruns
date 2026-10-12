// "Something wrong with this trail?": a skier's report of a wrong name, line or
// rating (or a trail missing from the map) goes to /api/report for review
// (api/_lib/reports.ts). Anonymous: the device id is only used there to cap
// reports at a few a day.
import { deviceId } from './hooks/useConditions';
import { track } from './analytics';

export type ReportKind = 'name' | 'line' | 'rating' | 'missing' | 'other';

export interface ProblemReport {
  resort: string;
  panel: string;
  trailId: string | null;
  kind: ReportKind;
  note: string;
  /** where the skier tapped, percent of the map image (null: opened from the list) */
  x: number | null;
  y: number | null;
}

/** Sends a report; true once the server has it. */
export async function reportProblem(r: ProblemReport): Promise<boolean> {
  try {
    const res = await fetch('/api/report', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ ...r, deviceId: deviceId() }),
    });
    if (res.ok) track('Problem reported', { resort: r.resort, kind: r.kind });
    return res.ok;
  } catch {
    return false;
  }
}
