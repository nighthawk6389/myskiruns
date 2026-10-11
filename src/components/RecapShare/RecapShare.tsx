import { useEffect, useRef, useState } from 'react';
import type { Resort } from '../../resorts';
import { CARD_SIZES, canvasToBlob, drawRecapCard, type CardSize } from '../../recap/card';
import { recapUrl, type Recap } from '../../recap/link';
import styles from './RecapShare.module.css';

interface RecapShareProps {
  resort: Resort;
  recap: Recap;
  /** "Sat, Feb 14" or "Feb 14 – 16" */
  dates: string;
  /** the plain-text summary, sent along with the link */
  text: string;
  onClose: () => void;
}

const SIZE_KEY = 'myskiruns.recapSize';

function savedSize(): CardSize {
  try {
    const s = localStorage.getItem(SIZE_KEY);
    if (s === 'story' || s === 'square') return s;
  } catch {
    // storage blocked: the default
  }
  return 'story';
}

const slug = (s: string) =>
  s
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'ski-day';

/** "Share your day": the recap card in either size, shared as an image (or
 * saved), and a link that opens the day as a map. */
export function RecapShare({ resort, recap, dates, text, onClose }: RecapShareProps) {
  const [size, setSize] = useState<CardSize>(savedSize);
  const [cards, setCards] = useState<Partial<Record<CardSize, { blob: Blob; url: string }>>>({});
  const [failed, setFailed] = useState(false);
  const [status, setStatus] = useState('');
  const closeRef = useRef<HTMLButtonElement>(null);
  // the cards' object URLs, let go of when the dialog closes
  const objectUrls = useRef<string[]>([]);
  const url = recapUrl(location.origin, resort.id, recap);
  const site = location.host.replace(/^www\./, '');

  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.stopPropagation();
        onClose();
      }
    };
    window.addEventListener('keydown', onKey, true);
    return () => window.removeEventListener('keydown', onKey, true);
  }, [onClose]);

  // draw the card in the size shown, once per size
  const card = cards[size];
  useEffect(() => {
    if (card) return;
    let cancelled = false;
    drawRecapCard(size, {
      resort,
      trailIds: recap.trailIds,
      title: recap.name,
      dates,
      newCount: recap.newCount,
      days: recap.days,
      site,
    })
      .then(canvasToBlob)
      .then((blob) => {
        if (cancelled) return;
        const objectUrl = URL.createObjectURL(blob);
        objectUrls.current.push(objectUrl);
        setCards((c) => ({ ...c, [size]: { blob, url: objectUrl } }));
      })
      .catch(() => !cancelled && setFailed(true));
    return () => {
      cancelled = true;
    };
  }, [size, card, resort, recap, dates, site]);

  useEffect(() => {
    const urls = objectUrls.current;
    return () => urls.forEach((u) => URL.revokeObjectURL(u));
  }, []);

  const pick = (s: CardSize) => {
    setSize(s);
    setStatus('');
    try {
      localStorage.setItem(SIZE_KEY, s);
    } catch {
      // the choice lasts this session
    }
  };

  const fileName = `${slug(resort.name)}-${slug(recap.name)}-${size}.jpg`;

  const save = () => {
    if (!card) return;
    const a = document.createElement('a');
    a.href = card.url;
    a.download = fileName;
    document.body.append(a);
    a.click();
    a.remove();
    setStatus('Image saved');
  };

  const shareImage = async () => {
    if (!card) return;
    const file = new File([card.blob], fileName, { type: 'image/jpeg' });
    if (!navigator.canShare?.({ files: [file] })) {
      save();
      return;
    }
    try {
      await navigator.share({ files: [file], title: recap.name, text: `${text}\n${url}` });
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      setStatus('Could not share the image');
    }
  };

  const shareLink = async () => {
    try {
      if (navigator.share) {
        await navigator.share({ title: recap.name, text, url });
        return;
      }
      await navigator.clipboard.writeText(url);
      setStatus('Link copied');
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      setStatus('Could not share the link');
    }
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setStatus('Link copied');
    } catch {
      setStatus('Could not copy the link');
    }
  };

  const { w, h } = CARD_SIZES[size];

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="recap-share-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className={styles.header}>
          <h2 id="recap-share-title" className={styles.title}>
            Share your day
          </h2>
          <button ref={closeRef} className={styles.close} onClick={onClose} aria-label="Close">
            ✕
          </button>
        </header>

        <div className={styles.sizes} role="radiogroup" aria-label="Card size">
          {(Object.keys(CARD_SIZES) as CardSize[]).map((s) => (
            <button
              key={s}
              role="radio"
              aria-checked={s === size}
              className={`${styles.size} ${s === size ? styles.sizeOn : ''}`}
              onClick={() => pick(s)}
            >
              {CARD_SIZES[s].label}
              <span>{s === 'story' ? 'for stories' : 'for posts'}</span>
            </button>
          ))}
        </div>

        <div className={styles.preview} style={{ aspectRatio: `${w} / ${h}` }}>
          {card ? (
            <img src={card.url} alt={`Recap card: ${recap.trailIds.length} runs at ${resort.name}`} />
          ) : (
            <span className={styles.wait}>{failed ? 'Couldn’t draw the card (the map didn’t load)' : 'Drawing…'}</span>
          )}
        </div>

        <footer className={styles.footer}>
          <div className={styles.actions}>
            <button className={styles.primary} onClick={shareImage} disabled={!card}>
              Share image
            </button>
            <button className={styles.secondary} onClick={save} disabled={!card}>
              Save image
            </button>
          </div>
          <div className={styles.actions}>
            <button className={styles.secondary} onClick={shareLink}>
              Share link
            </button>
            <button className={styles.secondary} onClick={copyLink}>
              Copy link
            </button>
          </div>
          <p className={styles.note}>
            The link opens your runs on the map for anyone, no app or account needed.
            {status && (
              <span className={styles.status} role="status">
                {' '}
                {status}
              </span>
            )}
          </p>
        </footer>
      </div>
    </div>
  );
}
