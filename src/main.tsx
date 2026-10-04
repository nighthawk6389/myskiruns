import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { startAccounts } from './account/account'
import { startOffline } from './offline'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// optional sign-in and trip sync (src/account/account.ts); off unless set up
startAccounts()

// offline support (public/sw.js; dev builds skip it so hot reload works).
// The map starts it once it has loaded (src/offline.ts); this is the fallback
// for a visit where no map loads.
window.addEventListener('load', () => setTimeout(startOffline, 20000))
