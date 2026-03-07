import { useState, useCallback, useEffect } from 'react';

const STORAGE_KEY = 'killington-skied-trails';

function loadSkiedTrails(): Set<string> {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return new Set(JSON.parse(stored));
    }
  } catch {
    // ignore parse errors
  }
  return new Set();
}

function saveSkiedTrails(skied: Set<string>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...skied]));
}

export function useSkiedTrails() {
  const [skiedTrails, setSkiedTrails] = useState<Set<string>>(loadSkiedTrails);

  useEffect(() => {
    saveSkiedTrails(skiedTrails);
  }, [skiedTrails]);

  const toggle = useCallback((trailId: string) => {
    setSkiedTrails((prev) => {
      const next = new Set(prev);
      if (next.has(trailId)) {
        next.delete(trailId);
      } else {
        next.add(trailId);
      }
      return next;
    });
  }, []);

  const isSkied = useCallback(
    (trailId: string) => skiedTrails.has(trailId),
    [skiedTrails]
  );

  const reset = useCallback(() => {
    setSkiedTrails(new Set());
  }, []);

  return {
    skiedTrails,
    skiedCount: skiedTrails.size,
    toggle,
    isSkied,
    reset,
  };
}
