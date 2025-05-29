
export interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

export interface SymptomEntry {
  id: string;
  timestamp: Date;
  initialSymptom: string;
  conversation: ChatMessage[];
  finalSummary?: string; 
}
    