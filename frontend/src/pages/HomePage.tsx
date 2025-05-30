import React, { useEffect, useState } from 'react';
import { Edit3Icon, StethoscopeIcon, FileTextIcon } from 'lucide-react';
import { SymptomLogger } from '../components/SymptomLogger';
import { ReportGenerator } from '../components/ReportGenerator';
import SymptomHistoryView from '../pages/SymptomHistoryView';

enum AppView {
  Logger,
  Reporter,
  History
}

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

const HomePage:React.FC = () => {
    const [currentView, setCurrentView] = useState<AppView>(AppView.Logger);
    const [isHistory, setIsHistory] = useState<boolean>(false);

    useEffect(() => {
      if (currentView === AppView.History) {
        setIsHistory(true);
      }        
    }, [currentView]);


    const renderView = () => {
        switch (currentView) {
          case AppView.Logger:
            return <SymptomLogger />;
          case AppView.Reporter:
            return <ReportGenerator />;
          case AppView.History:
            return <SymptomHistoryView isSelected={isHistory} />;
          default:
            return <SymptomLogger />;
        }
      };

    return (
      <>
      <header className="w-full max-w-4xl mb-8 text-center">
              <div className="flex items-center justify-center space-x-3 mb-2">
                <StethoscopeIcon className="w-12 h-12 text-indigo-600" />
                <h1 className="text-4xl md:text-5xl font-bold text-indigo-700 tracking-tight">
                  Medi<span className="text-sky-500"></span>
                </h1>
              </div>
              <p className="text-slate-600 text-lg">
                Your intelligent partner for tracking symptoms and preparing for doctor visits.
              </p>
            </header>
      <div className="flex flex-col items-center justify-start min-h-screen w-full p-4">
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
        <p>&copy; {new Date().getFullYear()} Medi. For demonstration purposes only. Not for real medical use.</p>
        <p>Ensure your <code>API_KEY</code> environment variable is set for AI features.</p>
      </footer>
    </div>
    </>
    );
}

export default HomePage;