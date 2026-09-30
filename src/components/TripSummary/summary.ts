import type { Difficulty, PeakData, Trail } from '../../types';
import type { Trip } from '../../hooks/useTrips';

export const DIFFICULTY_ORDER: Difficulty[] = ['green', 'blue', 'black', 'double-black'];

export interface DayLog {
  /** YYYY-MM-DD, local time */
  date: string;
  runs: { trail: Trail; at: Date; isNew: boolean }[];
}

export interface TripStats {
  trails: Trail[];
  /** trails this trip skied for the first time on any trip */
  newTrails: Trail[];
  byDifficulty: Record<Difficulty, number>;
  byPeak: { peak: PeakData; skied: number; total: number }[];
  days: DayLog[];
  /** hardest difficulty skied, with the trails at that level */
  hardest: { difficulty: Difficulty; trails: Trail[] } | null;
}

const localDate = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

/** Everything the trip summary shows, from the trip's runs and all trips
 * (to tell which trails were new). */
export function summarizeTrip(trip: Trip, allTrips: Trip[], trails: Trail[], peaks: PeakData[]): TripStats {
  const byId = new Map(trails.map((t) => [t.id, t]));
  const runs = trip.runs
    .map((r) => ({ trail: byId.get(r.trailId), at: new Date(r.at) }))
    .filter((r): r is { trail: Trail; at: Date } => !!r.trail)
    .sort((a, b) => a.at.getTime() - b.at.getTime());

  // a trail is new if no other trip logged it before this trip did
  const firstElsewhere = new Map<string, number>();
  for (const t of allTrips) {
    if (t.id === trip.id) continue;
    for (const r of t.runs) {
      const at = new Date(r.at).getTime();
      if (!(firstElsewhere.get(r.trailId)! <= at)) firstElsewhere.set(r.trailId, at);
    }
  }
  const isNew = (trailId: string, at: Date) => !(firstElsewhere.get(trailId)! < at.getTime());

  const days: DayLog[] = [];
  for (const r of runs) {
    const date = localDate(r.at);
    if (days.at(-1)?.date !== date) days.push({ date, runs: [] });
    days.at(-1)!.runs.push({ ...r, isNew: isNew(r.trail.id, r.at) });
  }

  const skied = runs.map((r) => r.trail);
  const byDifficulty = Object.fromEntries(DIFFICULTY_ORDER.map((d) => [d, 0])) as Record<Difficulty, number>;
  for (const t of skied) byDifficulty[t.difficulty]++;
  const hardestLevel = [...DIFFICULTY_ORDER].reverse().find((d) => byDifficulty[d] > 0);

  return {
    trails: skied,
    newTrails: days.flatMap((d) => d.runs.filter((r) => r.isNew).map((r) => r.trail)),
    byDifficulty,
    byPeak: peaks
      .map((peak) => ({
        peak,
        skied: skied.filter((t) => t.peak === peak.id).length,
        total: trails.filter((t) => t.peak === peak.id).length,
      }))
      .filter((p) => p.total > 0),
    days,
    hardest: hardestLevel ? { difficulty: hardestLevel, trails: skied.filter((t) => t.difficulty === hardestLevel) } : null,
  };
}

/** Plain-text version for sharing. */
export function summaryText(trip: Trip, s: TripStats, totalTrails: number, resortName: string): string {
  const icons: Record<Difficulty, string> = { green: '🟢', blue: '🟦', black: '◆', 'double-black': '◆◆' };
  const mix = DIFFICULTY_ORDER.filter((d) => s.byDifficulty[d]).map((d) => `${icons[d]} ${s.byDifficulty[d]}`);
  const lines = [
    `⛷ ${trip.name}`,
    `${s.trails.length} of ${totalTrails} ${resortName} trails${s.newTrails.length ? `, ${s.newTrails.length} new to me` : ''}` +
      (s.days.length > 1 ? ` over ${s.days.length} days` : ''),
  ];
  if (mix.length) lines.push(mix.join('  '));
  if (s.hardest && (s.hardest.difficulty === 'black' || s.hardest.difficulty === 'double-black')) {
    lines.push(`Toughest: ${s.hardest.trails.slice(0, 3).map((t) => t.name).join(', ')}`);
  }
  return lines.join('\n');
}
