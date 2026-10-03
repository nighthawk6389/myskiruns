import { useEffect, useState } from 'react';
import { deleteAccount, sendCode, signOut, syncNow, useAccount, verifyCode } from '../../account/account';
import styles from './AccountDialog.module.css';

const RESEND_AFTER_S = 60;

function syncedLabel(at: string | null): string {
  if (!at) return 'Not synced yet';
  const d = new Date(at);
  const sameDay = d.toDateString() === new Date().toDateString();
  const time = d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  return `Synced ${sameDay ? time : `${d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}, ${time}`}`;
}

/** Sign in with an emailed code, then the account's sync status, sign out and
 * delete (src/account/account.ts). */
export function AccountDialog({ onClose }: { onClose: () => void }) {
  const account = useAccount();
  const [step, setStep] = useState<'email' | 'code'>('email');
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [cooldown, setCooldown] = useState(0);
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  const run = async (action: () => Promise<void>) => {
    setBusy(true);
    setError('');
    try {
      await action();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const requestCode = () =>
    run(async () => {
      await sendCode(email.trim());
      setStep('code');
      setCode('');
      setCooldown(RESEND_AFTER_S);
    });

  // back to the email step once signed out
  const signedOut = (action: () => Promise<void>) => async () => {
    await action();
    setStep('email');
    setConfirmDelete(false);
  };

  const signedIn = account.status === 'signed-in';
  const title = signedIn ? 'Account' : step === 'code' ? 'Check your email' : 'Back up & sync your trips';

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div
        className={styles.dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="account-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className={styles.header}>
          <h2 id="account-title" className={styles.title}>{title}</h2>
          <button className={styles.close} onClick={onClose} aria-label="Close">
            ✕
          </button>
        </header>

        <div className={styles.body}>
          {account.status === 'loading' && <p className={styles.muted}>Loading…</p>}

          {account.status === 'signed-out' && step === 'email' && (
            <form
              className={styles.form}
              onSubmit={(e) => {
                e.preventDefault();
                void requestCode();
              }}
            >
              <p>
                Sign in with your email to keep your trips in your account and see them on your other devices. No
                password: we email you a code. Without an account the app works as before, with trips on this device
                only.
              </p>
              <label className={styles.label} htmlFor="account-email">Email</label>
              <input
                id="account-email"
                className={styles.input}
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setError('');
                }}
                disabled={busy}
                autoFocus
                required
              />
              <button type="submit" className={styles.primary} disabled={busy || !email.includes('@')}>
                {busy ? 'Sending…' : 'Email me a code'}
              </button>
            </form>
          )}

          {account.status === 'signed-out' && step === 'code' && (
            <form
              className={styles.form}
              onSubmit={(e) => {
                e.preventDefault();
                void run(() => verifyCode(email.trim(), code));
              }}
            >
              <p>
                We sent a sign-in code to <b>{email.trim()}</b>. It can take a minute to arrive; check spam too.
              </p>
              <label className={styles.label} htmlFor="account-code">Code</label>
              <input
                id="account-code"
                className={`${styles.input} ${styles.code}`}
                inputMode="numeric"
                autoComplete="one-time-code"
                pattern="[0-9]*"
                maxLength={10}
                value={code}
                onChange={(e) => {
                  setCode(e.target.value.replace(/\D/g, ''));
                  setError('');
                }}
                disabled={busy}
                autoFocus
              />
              <button type="submit" className={styles.primary} disabled={busy || code.length < 6}>
                {busy ? 'Signing in…' : 'Sign in'}
              </button>
              <div className={styles.links}>
                <button type="button" className={styles.link} onClick={() => setStep('email')} disabled={busy}>
                  Use a different email
                </button>
                <button type="button" className={styles.link} onClick={() => void requestCode()} disabled={busy || cooldown > 0}>
                  {cooldown > 0 ? `Send a new code in ${cooldown}s` : 'Send a new code'}
                </button>
              </div>
            </form>
          )}

          {signedIn && (
            <>
              <p>
                Signed in as <b>{account.email}</b>. Your trips are saved in your account and kept in step on every
                device you sign in on.
              </p>
              <p className={styles.status} role="status">
                {account.sync === 'syncing'
                  ? 'Syncing…'
                  : account.sync === 'offline'
                    ? `Offline: changes sync when you’re back online. ${syncedLabel(account.lastSyncedAt)}.`
                    : account.sync === 'error'
                      ? `Couldn’t sync: ${account.error}`
                      : `${syncedLabel(account.lastSyncedAt)}.`}
              </p>
              <div className={styles.row}>
                <button className={styles.button} onClick={() => void syncNow()} disabled={account.sync === 'syncing'}>
                  Sync now
                </button>
                <button className={styles.button} onClick={() => void run(signedOut(signOut))} disabled={busy}>
                  Sign out
                </button>
              </div>
              <p className={styles.muted}>Signing out keeps your trips on this device.</p>

              <div className={styles.danger}>
                {confirmDelete ? (
                  <>
                    <p>
                      Delete your account and the trips saved in it? Trips on this device stay. This can’t be undone.
                    </p>
                    <div className={styles.row}>
                      <button className={styles.destructive} onClick={() => void run(signedOut(deleteAccount))} disabled={busy}>
                        {busy ? 'Deleting…' : 'Delete account'}
                      </button>
                      <button className={styles.button} onClick={() => setConfirmDelete(false)} disabled={busy}>
                        Cancel
                      </button>
                    </div>
                  </>
                ) : (
                  <button className={styles.link} onClick={() => setConfirmDelete(true)}>
                    Delete account…
                  </button>
                )}
              </div>
            </>
          )}

          {(error || (account.status === 'signed-out' && account.error)) && (
            <p className={styles.error} role="alert">{error || account.error}</p>
          )}
        </div>
      </div>
    </div>
  );
}
