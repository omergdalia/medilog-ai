
export interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

export interface SymptomEntry {
  timestamp: Date;
  title: string;
  summary: string; 
}
    