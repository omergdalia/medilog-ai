import React, { useEffect, useState } from 'react';
import { getSymptomHistory } from '../services/apiService';
import { type SymptomResponse } from '../types.ts';


const SymptomHistoryView: React.FC = () => {

  const [symptomEntries, setSymptomEntries] = useState<SymptomResponse[]>([]);
  useEffect(() => {
    getSymptomHistory(`${process.env.UUID}`).then(entries => setSymptomEntries(entries));
  }, []);

if (symptomEntries.length === 0) {
    return <div className="text-center text-slate-500 py-10">No symptom entries logged yet.</div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-indigo-700 mb-6 border-b pb-2">Symptom History</h2>
      {symptomEntries.slice().reverse().map((entry, index) => (
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
              {entry.summary.map((item, index) => (
                <span key={index} className="block mt-1">
                  {item}<br />
                </span>))
              }
            </div>
          </details>
        </div>
      ))}
    </div>
  );
};

export default SymptomHistoryView;