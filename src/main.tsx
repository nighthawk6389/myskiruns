import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { startAccounts } from './account/account'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// optional sign-in and trip sync (src/account/account.ts); off unless set up
startAccounts()

// offline support (see public/sw.js); dev builds skip it so hot reload works
if ('serviceWorker' in navigator && import.meta.env.PROD) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      // offline caching is optional; the app works without it
    })
  })
}
