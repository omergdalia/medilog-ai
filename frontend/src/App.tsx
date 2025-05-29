
import React, { useEffect, useState } from 'react';
import { SymptomLogger } from './components/SymptomLogger';
import { ReportGenerator } from './components/ReportGenerator';
import { type SymptomEntry } from './types';
import { StethoscopeIcon, Edit3Icon, FileTextIcon } from 'lucide-react';

import { getSymptomHistory } from './services/apiService';

enum AppView {
  Logger,
  Reporter,
  History
}

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<AppView>(AppView.Logger);

  const renderView = () => {
    switch (currentView) {
      case AppView.Logger:
        return <SymptomLogger />;
      case AppView.Reporter:
        return <ReportGenerator />;
      case AppView.History:
        return <SymptomHistoryView />;
      default:
        return <SymptomLogger />;
    }
  };
  
  const NavButton: React.FC<{
    Icon: React.ElementType;
    label: string;
    isActive: boolean;
    onClick: () => void;
  }> = ({ Icon, label, isActive, onClick }) => (
    <button
      onClick={onClick}
      className={`flex items-center space-x-2 px-4 py-3 rounded-lg transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-400
        ${isActive 
          ? 'bg-indigo-600 text-white shadow-lg transform scale-105' 
          : 'bg-white text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 shadow-sm hover:shadow-md'
        }`}
    >
      <Icon className="w-5 h-5" />
      <span>{label}</span>
    </button>
  );

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

      <nav className="w-full max-w-md mb-8 p-2 bg-slate-200/50 rounded-xl shadow-md flex justify-around space-x-2 backdrop-blur-sm">
        <NavButton 
          Icon={Edit3Icon} 
          label="Log Symptoms" 
          isActive={currentView === AppView.Logger}
          onClick={() => setCurrentView(AppView.Logger)} 
        />
        <NavButton 
          Icon={FileTextIcon} 
          label="Doctor Report" 
          isActive={currentView === AppView.Reporter}
          onClick={() => setCurrentView(AppView.Reporter)} 
        />
         <NavButton 
          Icon={FileTextIcon} 
          label="View History" 
          isActive={currentView === AppView.History}
          onClick={() => setCurrentView(AppView.History)} 
        />
      </nav>

      <main className="w-full max-w-3xl bg-white p-6 md:p-8 rounded-xl shadow-2xl">
        {renderView()}
      </main>
      
      <footer className="mt-12 text-center text-slate-500 text-sm">
        <p>&copy; {new Date().getFullYear()} MediLogAI. For demonstration purposes only. Not for real medical use.</p>
        <p>Ensure your <code>API_KEY</code> environment variable is set for AI features.</p>
      </footer>
    </div>
  );
};


const SymptomHistoryView: React.FC = () => {

  const [symptomEntries, setSymptomEntries] = useState<SymptomEntry[]>([]);
  useEffect(() => {
    getSymptomHistory('00000000-0000-0000-0000-000000000000').then(entries => setSymptomEntries(entries));
  }, []);

if (symptomEntries.length === 0) {
    return <div className="text-center text-slate-500 py-10">No symptom entries logged yet.</div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-indigo-700 mb-6 border-b pb-2">Symptom History</h2>
      {symptomEntries.slice().map((entry, index) => (
        <div
          key={index}
          className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <p className="text-xl font-semibold text-slate-800">{entry.title}</p>
            <p className="text-sm text-slate-500 mt-1 sm:mt-0">
              {new Date(entry.timestamp).toLocaleString()}
            </p>
          </div>

          <details className="mt-4 group">
            <summary className="cursor-pointer text-indigo-600 hover:text-indigo-800 font-medium transition">
              <span className="underline underline-offset-2 group-open:hidden">View Summary</span>
              <span className="underline underline-offset-2 hidden group-open:inline">Hide Summary</span>
            </summary>
            <div className="mt-2 bg-indigo-50 text-slate-800 p-4 rounded-lg border border-indigo-100">
              {entry.summary}
            </div>
          </details>
        </div>
      ))}
    </div>
  );
};

export default App;
    