import google.generativeai as genai
import os
from typing import Optional, List, Any
from dotenv import load_dotenv
import datetime

# Load environment variables from .env file
load_dotenv()
# Ensure the API key is set in the environment
api_key = os.getenv('API_KEY')

class LLMManager:
    _NO_CONTEXT_STRING = "No past medical summary provided."
    _SYMPTOM_SYSTEM_PROMPT_TEMPLATE = (
        "You are an empathetic medical assistant. Your primary role is to understand the user's current symptoms "
        "by asking concise, clarifying questions. Ask only one question at a time. Do not provide diagnoses or treatment advice. "
        "After gathering sufficient details for a symptom (typically 2-4 questions), inquire if the user has other symptoms. "
        "If they report no other symptoms, respond ONLY with the exact text: '{end_text}'.\n"
        "Consider the following historical context: dates, symptom titles, and summaries of past medical interactions:\n"
         "{user_context_string}\n"
    )
    _SUMMARY_SYSTEM_PROMPT = (
        "Generate a concise, factual, bullet-point summary of the *current* medical interaction provided below. "
        "Focus solely on reported symptoms, their characteristics (onset, duration, severity, nature), and any "
        "pertinent information shared by the user during this specific conversation. Exclude conversational filler and any prior history not part of this interaction."
    )

    _SUMMARY_TITLE_SYSTEM_PROMPT = (
        "Generate a concise title describing the main symptom the user complained of in the current medical interaction summary. "
        "Examples of titles: 'Headache', 'Chest Pain', 'Fever and Cough', 'Abdominal Pain', 'Back Pain', 'Joint Swelling'.\n"
    )

    _DOCTOR_REPORT_SYSTEM_PROMPT_BASE = (
        "You are tasked with creating a clinical note for a doctor. Base this note on the provided 'Reason for Visit' and the 'Relevant Past Medical Summary'. "
        "Structure the note to be informative for a physician. If the past summary is extensive, focus on aspects most relevant to the stated reason for visit. "
        "The note should include:\n"
        "1. Reason for Visit: {visit_reason}\n"
        "2. Relevant Past Medical Summary Overview: \n{user_context_string}\n"
        "Synthesize this into a coherent note. If the past summary is 'No past medical summary provided.', state that clearly."
    )

    def __init__(self, api_key: str, model_name: str = 'gemini-2.5-flash-preview-05-20', user_context: Any = None, end_text: str = "FINISHED"):
        genai.configure(api_key=api_key)
        self._model_name: str = model_name
        self.formatted_user_context_str: str = self.__format_user_context(user_context)
        self._end_text: str = end_text
        current_symptom_prompt = self._SYMPTOM_SYSTEM_PROMPT_TEMPLATE.format(
            end_text=self._end_text,
            user_context_string=self.formatted_user_context_str
        )
        self.symptom_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=current_symptom_prompt
        )
        self.chat_session: Optional[genai.ChatSession] = self.symptom_model.start_chat(history=[])

    def __format_user_context(self, context_data: List[dict[str, Any]]) -> str:
        """
        Receives a list of dicts with keys 'title', 'summary', and 'timestamp',
        and returns a nicely formatted string for historical context in prompts.
        """
        if not context_data:
            return self._NO_CONTEXT_STRING
        if isinstance(context_data, str):
            return context_data
        elif isinstance(context_data, list):
            formatted_entries = []
            for item in context_data:
                title = item.get('title', 'No Title')
                summary = item.get('summary', 'No Summary')
                timestamp = item.get('timestamp', None)
                if isinstance(timestamp, (int, float)):
                    # If timestamp is a Unix timestamp
                    try:
                        dt = datetime.datetime.fromtimestamp(timestamp)
                        timestamp_str = dt.strftime('%Y-%m-%d %H:%M')
                    except Exception:
                        timestamp_str = str(timestamp)
                elif isinstance(timestamp, str):
                    timestamp_str = timestamp
                else:
                    timestamp_str = 'Unknown Time'
                formatted_entries.append(f"[{timestamp_str}] {title}: {summary}")
            return "\n".join(formatted_entries)
        else:
            raise ValueError("Not supported user context type.")

    def __format_history_to_string(self, history: List[Any]) -> str:
        if not history:
            return "No conversation history."
        return "\n".join(
            f"{'User' if msg.role == 'user' else 'Assistant'}: {msg.parts[0].text}"
            for msg in history if msg.parts and msg.parts[0].text
        )

    def get_response(self, user_text: str) -> str:
        """
        Send user input to the chat session and return the assistant's response.

        Args:
            user_text (str): The user's message to send to the assistant.

        Returns:
            str: The assistant's response text.
        """
        if not self.chat_session:
            raise ValueError("Session not started. Call reset_symptom_session() or initialize the class again.")
        try:
            response = self.chat_session.send_message(user_text)
            return response.text
        except Exception as e:
            raise

    def get_summary(self) -> dict[str, str]:
        """
        Summarize the current chat session as a concise medical interaction summary.

        Returns:
            dict: A dictionary with keys 'title' and 'summary' for the current medical interaction.
        """
        if not self.chat_session or not self.chat_session.history:
            raise ValueError("No current interaction history available to summarize.")

        summary_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=self._SUMMARY_SYSTEM_PROMPT
        )
        conversation_text = self.__format_history_to_string(self.chat_session.history)
        prompt_for_summary = f"Current medical interaction details:\n{conversation_text}"
        answer_dict =  {"title": "", "summary": ""}
        try:
            response = summary_model.generate_content(prompt_for_summary)
            answer_dict['summary'] = response.text.strip()
        except Exception as e:
            raise e
        title_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=self._SUMMARY_TITLE_SYSTEM_PROMPT
        )
        try:
            response = title_model.generate_content(answer_dict['summary'])
            answer_dict['title'] = response.text.strip()
        except Exception as e:
            raise e
        if not answer_dict['summary']:
            raise ValueError("Summary generation failed. No summary text returned.")
        if not answer_dict['title']:
            raise ValueError("Title generation failed. No title text returned.")
        return answer_dict
                



    def get_doctor_report(self, visit_reason: str) -> str:
        """
        Generate a clinical note for a doctor based on the visit reason and user context.

        Args:
            visit_reason (str): The reason for the patient's visit.

        Returns:
            str: The generated clinical note for the doctor.
        """
        if not visit_reason:
            raise ValueError("Visit reason must be provided for the doctor report.")
        if not self.formatted_user_context_str or self.formatted_user_context_str == self._NO_CONTEXT_STRING:
            raise ValueError("User context must be provided for the doctor report.")
        
        doctor_report_prompt_instruction = self._DOCTOR_REPORT_SYSTEM_PROMPT_BASE.format(
            visit_reason=visit_reason,
            user_context_string=self.formatted_user_context_str
        )
        
        report_generation_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=doctor_report_prompt_instruction
        )
        
        final_prompt_for_report = f"Please generate the clinical note for a patient visiting due to: {visit_reason}."

        try:
            response = report_generation_model.generate_content(final_prompt_for_report)
            return response.text
        except Exception as e:
            raise

    def reset_symptom_session(self, new_user_context: Optional[Any] = None) -> None:
        """
        Reset the symptom chat session, optionally updating the user context.

        Args:
            new_user_context (Optional[Any]): New user context to use for the session (default: None).

        Returns:
            None
        """
        if new_user_context is not None:
            self.formatted_user_context_str = self.__format_user_context(new_user_context)
        
        current_symptom_prompt = self._SYMPTOM_SYSTEM_PROMPT_TEMPLATE.format(
            end_text=self._end_text,
            user_context_string=self.formatted_user_context_str
        )
        self.symptom_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=current_symptom_prompt
        )
        self.chat_session = self.symptom_model.start_chat(history=[])

    def extend_user_context(self, new_context_entries: Any) -> None:
        """
        Extend the user context with new entries and update the chat session.

        Args:
            new_context_entries (Any): New context information to append to the existing user context.

        Returns:
            None
        """
        new_context_string = self.__format_user_context(new_context_entries)
        if not new_context_string or new_context_string == self._NO_CONTEXT_STRING:
            return
        if not self.formatted_user_context_str or self.formatted_user_context_str == self._NO_CONTEXT_STRING:
            self.formatted_user_context_str = new_context_string
        elif self.formatted_user_context_str != self._NO_CONTEXT_STRING:
            self.formatted_user_context_str += "\n" + new_context_string

        # Update system prompt for symptom model and re-initialize session with current history
        current_symptom_prompt = self._SYMPTOM_SYSTEM_PROMPT_TEMPLATE.format(
            end_text=self._end_text,
            user_context_string=self.formatted_user_context_str
        )
        current_history = self.chat_session.history if self.chat_session else []
        self.symptom_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=current_symptom_prompt
        )
        self.chat_session = self.symptom_model.start_chat(history=current_history)

    def replace_user_context(self, new_full_context: Any) -> None:
        """
        Replace the user context entirely and update the chat session.

        Args:
            new_full_context (Any): The new user context to replace the existing context.

        Returns:
            None
        """
        self.formatted_user_context_str = self.__format_user_context(new_full_context)
        current_symptom_prompt = self._SYMPTOM_SYSTEM_PROMPT_TEMPLATE.format(
            end_text=self._end_text,
            user_context_string=self.formatted_user_context_str
        )
        current_history = self.chat_session.history if self.chat_session else []
        self.symptom_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=current_symptom_prompt
        )
        self.chat_session = self.symptom_model.start_chat(history=current_history)

