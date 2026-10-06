import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { byRegion, searchResorts, type ResortOption } from '../../resortSearch';
import styles from './ResortPicker.module.css';

interface ResortPickerProps {
  resorts: readonly ResortOption[];
  value: string;
  onChange: (id: string) => void;
  /** the chosen resort's data is still loading */
  busy: boolean;
}

/** A resort was just picked: the header (and this button with it) is rebuilt
 * for the new resort, so the new button takes the focus when it mounts. */
let refocusOnMount = false;

/** The header's resort button: it opens a search box over the resorts, grouped
 * by state until something is typed, then best match first. Arrow keys move,
 * Enter picks, Escape closes. */
export function ResortPicker({ resorts, value, onChange, busy }: ResortPickerProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [active, setActive] = useState(0);
  const wrapRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listId = useId();
  const current = resorts.find((r) => r.id === value);

  const groups = useMemo(
    () => (query.trim() ? [{ region: '', resorts: searchResorts(resorts, query) }] : byRegion(resorts)),
    [resorts, query],
  );
  const options = useMemo(() => groups.flatMap((g) => g.resorts), [groups]);
  const optionId = (i: number) => `${listId}-${i}`;

  const show = () => {
    setQuery('');
    // start on the current resort, so Enter keeps it and the arrows move from it
    setActive(Math.max(0, byRegion(resorts).flatMap((g) => g.resorts).findIndex((r) => r.id === value)));
    setOpen(true);
  };
  const close = (refocus: boolean) => {
    setOpen(false);
    if (refocus) buttonRef.current?.focus();
  };
  const choose = (id: string) => {
    close(true);
    if (id === value) return;
    refocusOnMount = true;
    onChange(id);
  };

  useEffect(() => {
    if (!refocusOnMount) return;
    refocusOnMount = false;
    buttonRef.current?.focus();
  }, []);

  // close on a click or tap outside
  useEffect(() => {
    if (!open) return;
    const outside = (e: PointerEvent) => {
      if (!wrapRef.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('pointerdown', outside);
    return () => document.removeEventListener('pointerdown', outside);
  }, [open]);

  // keep the active option in view
  useEffect(() => {
    if (!open) return;
    document.getElementById(optionId(active))?.scrollIntoView({ block: 'nearest' });
  });

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      if (!options.length) return;
      const step = e.key === 'ArrowDown' ? 1 : -1;
      setActive((a) => (a + step + options.length) % options.length);
    } else if (e.key === 'Home' || e.key === 'End') {
      if (!options.length || query) return; // in a typed query they move the caret
      e.preventDefault();
      setActive(e.key === 'Home' ? 0 : options.length - 1);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const pick = options[active] ?? options[0];
      if (pick) choose(pick.id);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      close(true);
    }
  };

  let index = 0;
  return (
    <div
      className={styles.wrap}
      ref={wrapRef}
      // Tab (or anything else) taking the focus out of the picker closes it
      onBlur={(e) => {
        if (open && !wrapRef.current?.contains(e.relatedTarget as Node | null)) setOpen(false);
      }}
    >
      <button
        ref={buttonRef}
        type="button"
        className={styles.button}
        onClick={() => (open ? close(false) : show())}
        aria-haspopup="dialog"
        aria-expanded={open}
        aria-label={`Resort: ${current?.name ?? ''}. Change resort`}
        aria-busy={busy}
      >
        <span className={styles.name}>{current?.name}</span>
        <span className={styles.chevron} aria-hidden="true">
          ▾
        </span>
      </button>
      {open && (
        <div className={styles.panel} role="dialog" aria-label="Choose a resort">
          <input
            className={styles.search}
            type="search"
            role="combobox"
            aria-expanded="true"
            aria-controls={listId}
            aria-autocomplete="list"
            aria-activedescendant={options.length ? optionId(active) : undefined}
            aria-label="Search resorts"
            placeholder={`Search ${resorts.length} resorts or a state…`}
            value={query}
            autoFocus
            autoComplete="off"
            spellCheck={false}
            onChange={(e) => {
              setQuery(e.target.value);
              setActive(0);
            }}
            onKeyDown={onKeyDown}
          />
          {/* tabIndex -1: the search box drives the list (arrow keys), so Tab skips this scroll box */}
          <ul className={styles.list} id={listId} role="listbox" aria-label="Resorts" tabIndex={-1}>
            {groups.map((g) => (
              <li key={g.region || 'matches'} role="presentation">
                {g.region && (
                  <div className={styles.region} role="presentation">
                    {g.region}
                  </div>
                )}
                <ul role="group" aria-label={g.region || 'Matches'} className={styles.group}>
                  {g.resorts.map((r) => {
                    const i = index++;
                    return (
                      <li
                        key={r.id}
                        id={optionId(i)}
                        role="option"
                        aria-selected={r.id === value}
                        className={`${styles.option} ${i === active ? styles.active : ''}`}
                        onPointerEnter={() => setActive(i)}
                        // pick on click; keep the focus in the search box meanwhile
                        onPointerDown={(e) => e.preventDefault()}
                        onClick={() => choose(r.id)}
                      >
                        <span className={styles.optionName}>{r.name}</span>
                        {!g.region && <span className={styles.optionRegion}>{r.region}</span>}
                        {r.id === value && (
                          <span className={styles.check} aria-hidden="true">
                            ✓
                          </span>
                        )}
                      </li>
                    );
                  })}
                </ul>
              </li>
            ))}
            {!options.length && (
              <li className={styles.empty} role="presentation">
                No resort matches “{query.trim()}”
              </li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
