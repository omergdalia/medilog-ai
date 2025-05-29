import { type SymptomEntry } from '../types';
import axios from 'axios';


export const sendMessageInChat = async (id: string, message: string): Promise<string> => {
  const url = `${process.env.API_BASE}/response/${id}?prompt=${encodeURIComponent(message)}`;
  const res = await axios.get<{ answer: string }>(url, {
      headers: {
        'Accept': 'application/json',
      },
    });
  return res.data.answer; 
  };

export const generateDoctorReport = async (id: string, reasonForVisit: string, entries: SymptomEntry[]): Promise<string> => {
  try {
    const url = `${process.env.API_BASE}/doctor_report/${id}?prompt=${encodeURIComponent(reasonForVisit)}`;
    const res = await axios.get<{ answer: string }>(url, {
        headers: {
          'Accept': 'application/json',
        },
      });
    return res.data.answer;
    
    // if (!response.ok) {
    //   throw new Error(`Error: ${response.status} ${response.statusText}`);
    // }
    // const data = await response.json();
    // return data; // Assuming the backend returns string response

  } catch (error) {
    console.error("Error sending message to Gemini chat:", error);
    throw new Error("Failed to get response from AI. Please check your connection or API key.");
  }
};