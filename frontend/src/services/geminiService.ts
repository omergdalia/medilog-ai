import { type SymptomEntry } from '../types';


export const sendMessageInChat = async (id: number, message: string): Promise<string> => {
  // send request to backend get_response(uid, message)
  try {
    // const response: GenerateContentResponse = await chat.sendMessage({ message });
    const response = await fetch(`/api/get_response/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    return data; // Assuming the backend returns string response

  } catch (error) {
    console.error("Error sending message to Gemini chat:", error);
    throw new Error("Failed to get response from AI. Please check your connection or API key.");
  }
};

export const generateDoctorReport = async (id: number, reasonForVisit: string, entries: SymptomEntry[]): Promise<string> => {
  try {
    // const response: GenerateContentResponse = await chat.sendMessage({ message });
    const response = await fetch(`/api/doctors_report/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ reasonForVisit }),
    });
    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    return data; // Assuming the backend returns string response

  } catch (error) {
    console.error("Error sending message to Gemini chat:", error);
    throw new Error("Failed to get response from AI. Please check your connection or API key.");
  }
};