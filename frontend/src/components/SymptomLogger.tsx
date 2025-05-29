
import React, { useState, useEffect, useRef } from 'react';
import { type SymptomEntry, type ChatMessage } from '../types';
import { sendMessageInChat } from '../services/apiService';
// Fix: Import Edit3Icon
import { SendIcon, RotateCwIcon, SaveIcon, AlertCircleIcon, MessageSquareIcon, UserIcon, ZapIcon, Edit3Icon, InfoIcon } from 'lucide-react';
import { LoadingSpinner } from './LoadingSpinner';

import { saveSymptom } from '../services/apiService'; // Placeholder import, replace with actual service

enum LoggingStage {
  InitialInput,
  Chatting,
  Saving,
  Error,
  Done
}

// create uuid with library for uuids
// For simplicity, using a placeholder UUID. In production, use a library like uuid.
// import { v4 as uuidv4 } from 'uuid';


const MY_UUID: string = "00000000-0000-0000-0000-000000000000";

export const SymptomLogger: React.FC = () => {
  const [initialSymptom, setInitialSymptom] = useState<string>('');
  const [conversation, setConversation] = useState<ChatMessage[]>([]);
  const [currentUserMessage, setCurrentUserMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [stage, setStage] = useState<LoggingStage>(LoggingStage.InitialInput);
  
  const chatMessagesEndRef = useRef<HTMLDivElement | null>(null);
  const MAX_AI_TURNS = 3; // Initial + 2 follow-ups + 1 activity question
  const aiTurnCountRef = useRef<number>(0);

  useEffect(() => {
    chatMessagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation]);

  const handleStartSymptomAnalysis = async () => {
    if (!initialSymptom.trim()) {
      setError("Please describe your main symptom first.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setStage(LoggingStage.Chatting);
    aiTurnCountRef.current = 0;

    try {
      const userMessage: ChatMessage = { sender: 'user', text: initialSymptom, timestamp: new Date() };
      setConversation([userMessage]);
      
      const aiResponseText = await sendMessageInChat(MY_UUID, initialSymptom);
      setConversation(prev => [...prev, { sender: 'ai', text: aiResponseText, timestamp: new Date() }]);
      aiTurnCountRef.current++;
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "An unknown error occurred during AI analysis.");
      setStage(LoggingStage.Error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!currentUserMessage.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);
    const userMessage: ChatMessage = { sender: 'user', text: currentUserMessage, timestamp: new Date() };
    setConversation(prev => [...prev, userMessage]);
    setCurrentUserMessage('');

    try {
      const aiResponseText = await sendMessageInChat(MY_UUID, userMessage.text);
      setConversation(prev => [...prev, { sender: 'ai', text: aiResponseText, timestamp: new Date() }]);
      aiTurnCountRef.current++;
      if (aiTurnCountRef.current >= MAX_AI_TURNS) {
        // Optionally, can add a "final thoughts" AI message or directly enable saving
        setConversation(prev => [...prev, {sender: 'ai', text: "Thank you for the information. You can now save this entry.", timestamp: new Date()}]);
        setStage(LoggingStage.Saving);
      }
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "An unknown error occurred while sending message.");
      setStage(LoggingStage.Error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveEntry = () => {
    saveSymptom('00000000-0000-0000-0000-000000000000');
    setStage(LoggingStage.Done);
    // Optionally reset for new entry after a delay or user action
    setTimeout(() => resetLogger(), 3000);
  };
  
  const resetLogger = () => {
    setInitialSymptom('');
    setConversation([]);
    setCurrentUserMessage('');
    setIsLoading(false);
    setError(null);
    aiTurnCountRef.current = 0;
    setStage(LoggingStage.InitialInput);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-indigo-700 flex items-center">
        <Edit3Icon className="w-7 h-7 mr-3 text-indigo-500"/> Log New Symptom Entry
      </h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg relative flex items-center" role="alert">
          <AlertCircleIcon className="w-5 h-5 mr-2"/>
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      
      {stage === LoggingStage.Done && (
         <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg" role="alert">
          Symptom entry saved successfully!
        </div>
      )}

      {stage === LoggingStage.InitialInput && (
        <div className="space-y-4 p-4 bg-slate-50 rounded-lg shadow">
          <label htmlFor="initialSymptom" className="block text-md font-medium text-slate-700">
            What's your primary symptom or concern right now?
          </label>
          <textarea
            id="initialSymptom"
            value={initialSymptom}
            onChange={(e) => setInitialSymptom(e.target.value)}
            placeholder="e.g., 'Sharp pain in my lower back for 3 days,' or 'Feeling constantly tired and having trouble sleeping.'"
            rows={3}
            className="w-full p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors bg-white text-slate-900"
            disabled={isLoading}
            aria-describedby="symptom-helper-text"
          />
          <p id="symptom-helper-text" className="text-xs text-slate-500 flex items-start">
            <InfoIcon className="w-3 h-3 mr-1 mt-0.5 flex-shrink-0" />
            <span>Be specific about what you're feeling, when it started, and how it affects you. This helps the AI ask better follow-up questions.</span>
          </p>
          <button
            onClick={handleStartSymptomAnalysis}
            disabled={isLoading || !initialSymptom.trim()}
            className="w-full flex items-center justify-center px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 transition-all duration-150 ease-in-out"
          >
            {isLoading ? <LoadingSpinner size="sm" /> : <ZapIcon className="w-5 h-5 mr-2"/>}
            Start AI Symptom Analysis
          </button>
        </div>
      )}

      {(stage === LoggingStage.Chatting || stage === LoggingStage.Saving || (stage === LoggingStage.Error && conversation.length > 0)) && (
        <div className="space-y-4">
          <div className="h-80 overflow-y-auto p-4 bg-slate-100 rounded-lg shadow-inner custom-scrollbar space-y-3">
            {conversation.map((msg, index) => (
              <ChatMessageDisplay key={index} message={msg} />
            ))}
            {isLoading && conversation.length > 0 && conversation[conversation.length -1].sender === 'user' && (
                <div className="flex items-center justify-start space-x-2 p-2">
                    <MessageSquareIcon className="w-8 h-8 text-indigo-400 animate-pulse" />
                    <span className="text-slate-500 italic">AI is typing...</span>
                </div>
            )}
            <div ref={chatMessagesEndRef} />
          </div>

          {stage === LoggingStage.Chatting && (
            <div className="flex items-center space-x-2">
              <input
                type="text"
                value={currentUserMessage}
                onChange={(e) => setCurrentUserMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSendMessage()}
                placeholder="Type your answer..."
                className="flex-grow p-3 border border-slate-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors bg-white text-slate-900"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !currentUserMessage.trim()}
                className="p-3 bg-indigo-500 text-white rounded-lg shadow hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1 disabled:opacity-50 transition-colors"
                aria-label="Send message"
              >
                <SendIcon className="w-5 h-5" />
              </button>
            </div>
          )}
          
          {stage === LoggingStage.Saving && (
             <button
              onClick={handleSaveEntry}
              className="w-full flex items-center justify-center px-6 py-3 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-150 ease-in-out"
            >
              <SaveIcon className="w-5 h-5 mr-2"/> Save Entry
            </button>
          )}

          {(stage === LoggingStage.Chatting || stage === LoggingStage.Saving || stage === LoggingStage.Error) && (
            <button
                onClick={resetLogger}
                className="w-full flex items-center justify-center px-4 py-2 mt-2 text-sm bg-slate-200 text-slate-700 font-medium rounded-lg hover:bg-slate-300 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-1 transition-colors"
                aria-label="Start new log"
              >
              <RotateCwIcon className="w-4 h-4 mr-2"/> Start New Log / Reset
            </button>
          )}
        </div>
      )}
    </div>
  );
};


const ChatMessageDisplay: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const isUser = message.sender === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-xs md:max-w-md lg:max-w-lg p-3 rounded-xl shadow ${
          isUser 
            ? 'bg-sky-500 text-white rounded-br-none' 
            : 'bg-white text-slate-700 rounded-bl-none border border-slate-200'
        }`}
      >
        <div className="flex items-center mb-1">
          {isUser ? <UserIcon className="w-4 h-4 mr-2" /> : <MessageSquareIcon className="w-4 h-4 mr-2 text-indigo-500" />}
          <span className={`font-semibold text-sm ${isUser ? 'text-sky-100' : 'text-indigo-600'}`}>
            {isUser ? 'You' : 'MediLogAI'}
          </span>
        </div>
        <p className="text-sm whitespace-pre-wrap">{message.text}</p>
        <p className={`text-xs mt-1 ${isUser ? 'text-sky-200 text-right' : 'text-slate-400 text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
};
