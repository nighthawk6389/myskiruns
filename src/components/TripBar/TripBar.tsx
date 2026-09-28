import { useRef, useState } from 'react';
import type { Trip } from '../../hooks/useTrips';
import { defaultTripName } from '../../hooks/useTrips';
import styles from './TripBar.module.css';

interface TripBarProps {
  trips: Trip[];
  activeTrip: Trip | null;
  onSelect: (id: string) => void;
  onCreate: (name: string, startDate: string) => void;
  onUpdate: (id: string, patch: { name?: string; startDate?: string }) => void;
  onDelete: (id: string) => void;
  onExport: () => string;
  onImport: (text: string) => number;
}

const today = () => new Date().toISOString().slice(0, 10);

function tripLabel(t: Trip) {
  const trails = new Set(t.runs.map((r) => r.trailId)).size;
  return `${t.name} · ${trails} trail${trails === 1 ? '' : 's'}`;
}

export function TripBar({ trips, activeTrip, onSelect, onCreate, onUpdate, onDelete, onExport, onImport }: TripBarProps) {
  const [mode, setMode] = useState<'idle' | 'new' | 'edit' | 'menu'>('idle');
  const [name, setName] = useState('');
  const [date, setDate] = useState(today());
  const [message, setMessage] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  const openNew = () => {
    const d = today();
    setDate(d);
    setName(defaultTripName(d));
    setMode('new');
  };
  const openEdit = () => {
    if (!activeTrip) return;
    setName(activeTrip.name);
    setDate(activeTrip.startDate);
    setMode('edit');
  };
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (mode === 'new') onCreate(name, date);
    else if (mode === 'edit' && activeTrip) onUpdate(activeTrip.id, { name: name.trim() || activeTrip.name, startDate: date });
    setMode('idle');
  };

  const exportFile = () => {
    const blob = new Blob([onExport()], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `myskiruns-${today()}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
    setMode('idle');
  };
  const importFile = async (file: File) => {
    try {
      const added = onImport(await file.text());
      setMessage(added ? `Imported ${added} trip${added === 1 ? '' : 's'}.` : 'Those trips are already here.');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Could not read that file.');
    }
    setMode('idle');
  };
  const remove = () => {
    if (!activeTrip) return;
    const n = new Set(activeTrip.runs.map((r) => r.trailId)).size;
    if (window.confirm(`Delete "${activeTrip.name}" and its ${n} logged trail${n === 1 ? '' : 's'}? This can't be undone.`)) {
      onDelete(activeTrip.id);
    }
    setMode('idle');
  };

  if (mode === 'new' || mode === 'edit') {
    return (
      <form className={styles.bar} onSubmit={submit}>
        <input
          id="trip-name"
          className={styles.input}
          value={name}
          onChange={(e) => setName(e.target.value)}
          aria-label="Trip name"
          autoFocus
        />
        <input
          id="trip-date"
          className={styles.input}
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          aria-label="Trip start date"
        />
        <button type="submit" className={styles.primary}>{mode === 'new' ? 'Start trip' : 'Save'}</button>
        <button type="button" className={styles.button} onClick={() => setMode('idle')}>Cancel</button>
      </form>
    );
  }

  return (
    <div className={styles.bar}>
      {trips.length ? (
        <select
          id="trip-select"
          className={styles.select}
          value={activeTrip?.id ?? ''}
          onChange={(e) => onSelect(e.target.value)}
          aria-label="Current trip"
        >
          {[...trips]
            .sort((a, b) => b.startDate.localeCompare(a.startDate))
            .map((t) => (
              <option key={t.id} value={t.id}>{tripLabel(t)}</option>
            ))}
        </select>
      ) : (
        <span className={styles.hint}>No trip yet — marking a trail starts one for today</span>
      )}
      <button className={styles.primary} onClick={openNew}>New trip</button>
      <div className={styles.menuWrap}>
        <button className={styles.button} onClick={() => setMode(mode === 'menu' ? 'idle' : 'menu')} aria-expanded={mode === 'menu'}>
          ⋯
        </button>
        {mode === 'menu' && (
          <div className={styles.menu} role="menu">
            <button role="menuitem" onClick={openEdit} disabled={!activeTrip}>Rename trip</button>
            <button role="menuitem" onClick={remove} disabled={!activeTrip}>Delete trip</button>
            <button role="menuitem" onClick={exportFile} disabled={!trips.length}>Export backup</button>
            <button role="menuitem" onClick={() => fileRef.current?.click()}>Import backup</button>
          </div>
        )}
      </div>
      <input
        ref={fileRef}
        type="file"
        accept="application/json,.json"
        hidden
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) void importFile(f);
          e.target.value = '';
        }}
      />
      {message && (
        <span className={styles.hint} role="status" onClick={() => setMessage('')}>
          {message}
        </span>
      )}
    </div>
  );
}
