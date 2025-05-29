
import React, { useState } from 'react';
import { type SymptomEntry } from '../types';
import { generateDoctorReport } from '../services/geminiService';
import { FileTextIcon, AlertCircleIcon, ZapIcon } from 'lucide-react';
import { LoadingSpinner } from './LoadingSpinner';

interface ReportGeneratorProps {
  symptomEntries: SymptomEntry[];
}

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({ symptomEntries }) => {
  const [reasonForVisit, setReasonForVisit] = useState<string>('');
  const [generatedReport, setGeneratedReport] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateReport = async () => {
    if (!reasonForVisit.trim()) {
      setError("Please provide the reason for your doctor visit.");
      return;
    }
    if (symptomEntries.length === 0) {
      setError("No symptom entries available to generate a report. Please log some symptoms first.");
      // Optionally, could still generate a very basic report with just the reason.
      // For now, require entries.
      return;
    }

    setIsLoading(true);
    setError(null);
    setGeneratedReport(null);

    try {
      // For simplicity, send all entries. The AI prompt will guide relevance.
      // In a more complex app, filtering or selection could happen here.
      const report = await generateDoctorReport("00000000-0000-0000-0000-000000000000", reasonForVisit, symptomEntries);
      setGeneratedReport(report);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "An unknown error occurred while generating the report.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-indigo-700 flex items-center">
        <FileTextIcon className="w-7 h-7 mr-3 text-indigo-500"/> Prepare Doctor Visit Report
      </h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg relative flex items-center" role="alert">
          <AlertCircleIcon className="w-5 h-5 mr-2"/>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <div className="space-y-4 p-4 bg-slate-50 rounded-lg shadow">
        <label htmlFor="reasonForVisit" className="block text-md font-medium text-slate-700">
          What is the primary reason for your upcoming doctor visit?
        </label>
        <textarea
          id="reasonForVisit"
          value={reasonForVisit}
          onChange={(e) => setReasonForVisit(e.target.value)}
          placeholder="e.g., Annual check-up, follow-up on persistent cough, new concerns about joint pain."
          rows={3}
          className="w-full p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors bg-white text-slate-900"
          disabled={isLoading}
        />
        <button
          onClick={handleGenerateReport}
          disabled={isLoading || !reasonForVisit.trim() || symptomEntries.length === 0}
          className="w-full flex items-center justify-center px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150 ease-in-out"
        >
          {isLoading ? <LoadingSpinner size="sm" /> : <ZapIcon className="w-5 h-5 mr-2"/>}
          Generate Report
        </button>
        {symptomEntries.length === 0 && (
            <p className="text-sm text-amber-700 bg-amber-50 p-2 rounded-md text-center">
                <AlertCircleIcon className="w-4 h-4 inline mr-1" /> 
                No symptom entries found. Please log symptoms first to generate a comprehensive report.
            </p>
        )}
      </div>

      {isLoading && (
        <div className="flex flex-col items-center justify-center p-6 bg-slate-50 rounded-lg shadow">
          <LoadingSpinner />
          <p className="mt-3 text-slate-600">AI is generating your report...</p>
        </div>
      )}

      {generatedReport && !isLoading && (
        <div className="mt-6 p-6 bg-sky-50 border border-sky-200 rounded-lg shadow-lg">
          <h3 className="text-xl font-semibold text-sky-700 mb-4">Generated Doctor Visit Summary</h3>
          <div 
            className="prose prose-sm max-w-none text-slate-800 whitespace-pre-wrap"
            // Using Tailwind Typography plugin classes (prose) if available,
            // otherwise, basic formatting via whitespace-pre-wrap.
            // For explicit formatting, one might parse Markdown here if AI returns it.
          >
            {generatedReport}
          </div>
           <button
            onClick={() => navigator.clipboard.writeText(generatedReport)}
            className="mt-4 px-4 py-2 bg-sky-600 text-white text-sm font-medium rounded-md hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-1"
          >
            Copy Report to Clipboard
          </button>
        </div>
      )}
    </div>
  );
};
