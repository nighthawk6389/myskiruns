import { useState } from 'react';
import type { ReportKind } from '../../reports';
import styles from './ImageMap.module.css';

const KINDS: { kind: ReportKind; label: string }[] = [
  { kind: 'name', label: 'Wrong name' },
  { kind: 'line', label: 'Wrong line on the map' },
  { kind: 'rating', label: 'Wrong difficulty' },
  { kind: 'other', label: 'Something else' },
];

interface ReportFormProps {
  /** what's being reported, for the screen reader and the heading */
  subject: string;
  /** a trail missing from the map: no kind to pick */
  missing?: boolean;
  onSend: (kind: ReportKind, note: string) => Promise<boolean>;
  onClose: () => void;
}

/** "Something wrong?": what's wrong (a chip) and a note, sent for review. */
export function ReportForm({ subject, missing = false, onSend, onClose }: ReportFormProps) {
  const [kind, setKind] = useState<ReportKind | null>(missing ? 'missing' : null);
  const [note, setNote] = useState('');
  const [state, setState] = useState<'editing' | 'sending' | 'sent' | 'failed'>('editing');

  if (state === 'sent') {
    return (
      <div className={styles.report} role="status">
        Thanks! We&apos;ll check {missing ? 'the map here' : 'it'} and fix the map.
        <button className={styles.reportCancel} onClick={onClose}>
          Close
        </button>
      </div>
    );
  }

  const send = async () => {
    if (!kind) return;
    setState('sending');
    setState((await onSend(kind, note)) ? 'sent' : 'failed');
  };

  return (
    <div className={styles.report} role="group" aria-label={`Report a problem: ${subject}`}>
      {!missing && (
        <div className={styles.reportKinds} role="radiogroup" aria-label="What's wrong?">
          {KINDS.map((k) => (
            <button
              key={k.kind}
              role="radio"
              aria-checked={kind === k.kind}
              className={`${styles.tagChip} ${kind === k.kind ? styles.tagOn : ''}`}
              onClick={() => setKind(k.kind)}
            >
              {k.label}
            </button>
          ))}
        </div>
      )}
      <textarea
        className={styles.reportNote}
        maxLength={500}
        rows={2}
        placeholder={missing ? 'Which trail is missing, and where? (optional)' : 'What should it be? (optional)'}
        aria-label="Note"
        value={note}
        onChange={(e) => setNote(e.target.value)}
      />
      <div className={styles.reportActions}>
        {state === 'failed' && <span className={styles.reportError}>Couldn&apos;t send. Are you offline?</span>}
        <button className={styles.reportCancel} onClick={onClose}>
          Cancel
        </button>
        <button className={styles.reportSend} onClick={send} disabled={!kind || state === 'sending'}>
          {state === 'sending' ? 'Sending…' : 'Send'}
        </button>
      </div>
    </div>
  );
}
