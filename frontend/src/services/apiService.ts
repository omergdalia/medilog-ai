import axios from 'axios';


export const sendMessageInChat = async (id: string, message: string): Promise<string> => {
  const url = `${process.env.API_BASE}/response/${id}?prompt=${encodeURIComponent(message)}`;
  try {
    const res = await axios.get<{ answer: string }>(url, {headers: {'Accept': 'application/json'}});
    if (res.status >= 200 && res.status < 300) {
        return res.data.answer;
    } else {
      throw new Error(`Request failed with status: ${res.status}`);
    }
  } catch (error) {
    throw new Error("Failed to send message in chat: " + (error instanceof Error ? error.message : "Unknown error"));
  }
};

export const generateDoctorReport = async (id: string, reasonForVisit: string): Promise<string> => {
  const url = `${process.env.API_BASE}/doctor_report/${id}?prompt=${encodeURIComponent(reasonForVisit)}`;
  try {
    const res = await axios.get<{ answer: string }>(url, {headers: {'Accept': 'application/json'}});
    if (res.status >= 200 && res.status < 300) {
        return res.data.answer;
    } else {
      throw new Error(`Request failed with status: ${res.status}`);
    }
  } catch (error) {
    console.error("Error sending message to Gemini chat:", error);
    throw new Error("Failed to generate doctor report: " + (error instanceof Error ? error.message : "Unknown error"));
  }
};

export const hasSymptomHistory = async (id: string): Promise<boolean> => {
  const url = `${process.env.API_BASE}/has_history/${id}`;
  try {
    const res = await axios.get<boolean>(url, {headers: {'Accept': 'application/json'}});
    if (res.status >= 200 && res.status < 300) {
        return res.data;
    } else {
      throw new Error(`Request failed with status: ${res.status}`);
    }
  } catch (error) {
    throw new Error("Failed to check symptom history: " + (error instanceof Error ? error.message : "Unknown error"));
  }
};

export const saveSymptom = async (id: string) => {
  const url = `${process.env.API_BASE}/save_summary/${id}`;
  try {
    const res = await axios.post<{status: string}>(url, {headers: {'Accept': 'application/json'}});
    if (res.status < 200 && res.status >= 300) {
      throw new Error(`Request failed with status: ${res.status}`);
    }
  } catch (error) {
    throw new Error("Failed to check symptom history: " + (error instanceof Error ? error.message : "Unknown error"));
  }
};