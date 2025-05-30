
export interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

export interface ChatResponse {
  answer: string;
  stop: boolean;
}

export interface DoctorReport {
  reason: string;
  HPI: string[];
  impression: string;
}

export interface SymptomResponse {
  timestamp: Date;
  title: string;
  summary: string[];
}