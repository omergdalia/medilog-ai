
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import OpeningPage from "./pages/OpeningPage.tsx";
import HomePage from './pages/HomePage.tsx';
import SignupPage from "./pages/SignUpPage.tsx";

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-sky-100 flex flex-col items-center p-4 md:p-8">
      <BrowserRouter>
        <div className="w-full max-w-4xl mx-auto flex flex-col items-center">
          <Routes>
            <Route path="/login" element={<OpeningPage />} />
            <Route path="/" element={<HomePage />} />
            <Route path="/signup" element={<SignupPage />} />
          </Routes>
        </div>
      </BrowserRouter>
    </div>
  );
};

export default App;
    