import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import OpeningPage from "./pages/OpeningPage.tsx";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Router>
      <Routes>
        <Route path="/login" element={<OpeningPage />} />
        <Route path="/" element={<App />} />
      </Routes>
    </Router>
  </StrictMode>,
)
