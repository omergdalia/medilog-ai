
import React from 'react';
import { StethoscopeIcon} from 'lucide-react';
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import OpeningPage from "./pages/OpeningPage.tsx";
import HomePage from './pages/HomePage.tsx';

const App: React.FC = () => {  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-sky-100 flex flex-col items-center p-4 md:p-8">
      <header className="w-full max-w-4xl mb-8 text-center">
        <div className="flex items-center justify-center space-x-3 mb-2">
          <StethoscopeIcon className="w-12 h-12 text-indigo-600" />
          <h1 className="text-4xl md:text-5xl font-bold text-indigo-700 tracking-tight">
            MediLog<span className="text-sky-500">AI</span>
          </h1>
        </div>
        <p className="text-slate-600 text-lg">
          Your intelligent partner for tracking symptoms and preparing for doctor visits.
        </p>
      </header>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<OpeningPage />} />
          <Route path="/" element={<HomePage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
};

export default App;
    