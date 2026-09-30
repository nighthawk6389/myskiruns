// Condition tags people can add to a trail report, shared by the app and the
// conditions API (api/_lib/conditions.ts). Keys are stored; order is display
// order. `good` decides the chip color: true good, false bad, null neutral.
export const CONDITION_TAGS = [
  { key: 'groomed', label: 'Groomed', emoji: '🚜', good: true },
  { key: 'powder', label: 'Powder', emoji: '❄️', good: true },
  { key: 'soft', label: 'Soft / spring', emoji: '🌤️', good: true },
  { key: 'moguls', label: 'Moguls', emoji: '〰️', good: null },
  { key: 'packed', label: 'Hardpack', emoji: '🧱', good: null },
  { key: 'icy', label: 'Icy', emoji: '🧊', good: false },
  { key: 'slushy', label: 'Slushy', emoji: '💧', good: false },
  { key: 'thin', label: 'Thin cover', emoji: '🪨', good: false },
  { key: 'crowded', label: 'Crowded', emoji: '👥', good: false },
] as const;

export type ConditionTag = (typeof CONDITION_TAGS)[number]['key'];

export const TAG_KEYS: ReadonlySet<string> = new Set(CONDITION_TAGS.map((t) => t.key));
export const MAX_TAGS = 3;

/** The most-reported tags, most first, as {tag, count}; ties keep display order. */
export function topTags(counts: Record<string, number>, n = 3) {
  return CONDITION_TAGS.map((tag) => ({ tag, count: counts[tag.key] ?? 0 }))
    .filter((t) => t.count > 0)
    .sort((a, b) => b.count - a.count)
    .slice(0, n);
}
