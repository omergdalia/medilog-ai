import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { GoogleOAuthProvider } from '@react-oauth/google'

console.log(import.meta.env);
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={`${process.env.GOOGLE_CLIENT_ID}`}>
      <App />
    </GoogleOAuthProvider>
  </StrictMode>,
)
