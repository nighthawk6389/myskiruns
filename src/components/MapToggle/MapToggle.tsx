export type MapView = 'schematic' | 'image';

interface MapToggleProps {
  view: MapView;
  onChange: (view: MapView) => void;
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    background: 'var(--bg-tertiary)',
    borderRadius: 8,
    padding: 3,
    gap: 2,
  },
  button: {
    padding: '5px 14px',
    borderRadius: 6,
    border: 'none',
    fontSize: 13,
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  active: {
    background: 'var(--bg-primary)',
    color: 'var(--text-primary)',
  },
  inactive: {
    background: 'transparent',
    color: 'var(--text-muted)',
  },
};

export function MapToggle({ view, onChange }: MapToggleProps) {
  return (
    <div style={styles.container}>
      <button
        style={{ ...styles.button, ...(view === 'schematic' ? styles.active : styles.inactive) }}
        onClick={() => onChange('schematic')}
      >
        Schematic
      </button>
      <button
        style={{ ...styles.button, ...(view === 'image' ? styles.active : styles.inactive) }}
        onClick={() => onChange('image')}
      >
        Trail Map
      </button>
    </div>
  );
}
