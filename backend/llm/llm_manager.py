import google.generativeai as genai
import os
from typing import Optional, List, Any
from dotenv import load_dotenv

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
        "Consider the following historical context if available:\n{user_context_string}"
    )
    _SUMMARY_SYSTEM_PROMPT = (
        "Generate a concise, factual, bullet-point summary of the *current* medical interaction provided below. "
        "Focus solely on reported symptoms, their characteristics (onset, duration, severity, nature), and any "
        "pertinent information shared by the user during this specific conversation. Exclude conversational filler and any prior history not part of this interaction."
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

    def __format_user_context(self, context_data: Any) -> str:
        "TODO: implement more complex formatting if needed, e.g., for dicts or lists."
        if not context_data:
            return self._NO_CONTEXT_STRING
        if isinstance(context_data, str):
            return context_data
        else:
            raise ValueError("Not supported user context type. Please provide a string or None.")

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

    def get_summary(self) -> str:
        """
        Summarize the current chat session as a concise medical interaction summary.

        Returns:
            str: A bullet-point summary of the current medical interaction.
        """
        if not self.chat_session or not self.chat_session.history:
            raise ValueError("No current interaction history available to summarize.")

        summary_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=self._SUMMARY_SYSTEM_PROMPT
        )
        conversation_text = self.__format_history_to_string(self.chat_session.history)
        prompt_for_summary = f"Current medical interaction details:\n{conversation_text}" # Pass only current chat
        try:
            response = summary_model.generate_content(prompt_for_summary)
            return response.text
        except Exception as e:
            raise e

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

