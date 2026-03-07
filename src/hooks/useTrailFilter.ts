import { useState, useCallback, useMemo } from 'react';
import type { Difficulty, Trail } from '../types';

export type FilterMode = 'all' | 'skied' | 'not-skied';

export function useTrailFilter(trails: Trail[], skiedTrails: Set<string>) {
  const [activeDifficulties, setActiveDifficulties] = useState<Set<Difficulty>>(
    new Set(['green', 'blue', 'black', 'double-black'])
  );
  const [filterMode, setFilterMode] = useState<FilterMode>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const toggleDifficulty = useCallback((difficulty: Difficulty) => {
    setActiveDifficulties((prev) => {
      const next = new Set(prev);
      if (next.has(difficulty)) {
        if (next.size > 1) next.delete(difficulty);
      } else {
        next.add(difficulty);
      }
      return next;
    });
  }, []);

  const setAllDifficulties = useCallback(() => {
    setActiveDifficulties(new Set(['green', 'blue', 'black', 'double-black']));
  }, []);

  const filteredTrails = useMemo(() => {
    return trails.filter((trail) => {
      if (!activeDifficulties.has(trail.difficulty)) return false;
      if (filterMode === 'skied' && !skiedTrails.has(trail.id)) return false;
      if (filterMode === 'not-skied' && skiedTrails.has(trail.id)) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        if (
          !trail.name.toLowerCase().includes(q) &&
          !trail.peak.toLowerCase().includes(q)
        )
          return false;
      }
      return true;
    });
  }, [trails, activeDifficulties, filterMode, searchQuery, skiedTrails]);

  return {
    activeDifficulties,
    filterMode,
    searchQuery,
    filteredTrails,
    toggleDifficulty,
    setAllDifficulties,
    setFilterMode,
    setSearchQuery,
  };
}
