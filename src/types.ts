export type Difficulty = 'green' | 'blue' | 'black' | 'double-black';

export interface Trail {
  id: string;
  name: string;
  difficulty: Difficulty;
  peak: string;
  isGlade?: boolean;
  isTerrainPark?: boolean;
}

export interface PeakData {
  id: string;
  name: string;
  elevation: number;
  x: number;
  y: number;
  baseY: number;
  width: number;
}

export const DIFFICULTY_COLORS: Record<Difficulty, string> = {
  green: '#22c55e',
  blue: '#3b82f6',
  black: '#111827',
  'double-black': '#111827',
};

/** Difficulty colors for markers on the dark UI (black diamonds show light;
 * DIFFICULTY_COLORS is for lines drawn on the light trail map). */
export const DIFFICULTY_UI_COLORS: Record<Difficulty, string> = {
  green: '#22c55e',
  blue: '#3b82f6',
  black: '#e5e7eb',
  'double-black': '#ef4444',
};

export const DIFFICULTY_LABELS: Record<Difficulty, string> = {
  green: 'Easy',
  blue: 'Intermediate',
  black: 'Advanced',
  'double-black': 'Expert',
};

export const DIFFICULTY_ICONS: Record<Difficulty, string> = {
  green: '●',
  blue: '■',
  black: '◆',
  'double-black': '◆◆',
};
