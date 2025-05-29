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
    "You are an empathetic and helpful medical assistant. Your primary goal is to thoroughly understand a user's current symptoms. "
    "The user will describe their initial symptom(s). Your task is to ask concise, relevant follow-up questions to get more details. "
    "Ask exactly ONE concise and relevant follow-up question per response. Frame your questions empathetically and clearly.\n\n"
    "To gather comprehensive details, aim to understand the most relevant following aspects for each reported symptom:\n"
    "1. Severity: The intensity or degree (e.g., pain on a scale of 1-10, impact on daily activities).\n"
    "2. Nature/Quality: The type or characteristic (e.g., sharp, dull, throbbing pain; dry, productive cough).\n"
    "3. Onset and Duration: When it started, how it started (sudden/gradual), and how long it's been present (constant/intermittent).\n"
    "4. Location: The specific area(s) of the body affected, and if it radiates.\n"
    "5. Accompanying Symptoms: Any other symptoms or changes noticed, even if seemingly minor.\n"
    "6. Triggers and Relievers: Specific activities, foods, positions, or treatments that make it better or worse.\n"
    "7. Mechanism of Injury (if applicable): If an injury/trauma is mentioned, how it occurred.\n\n"
    "8. Any other relevant info, based on the user's initial description.\n\n"
    "If any of these aspects are clear based on the user's initial description, or the type of symptom, you may skip asking about them.\n\n"
    "After asking 2-5 targeted questions to clarify a specific symptom (or if the user initially provides comprehensive details), inquire: 'Do you have any other symptoms you'd like to discuss?'\n"
    "For each symptom, judiciously select questions to gain a clear understanding, avoiding redundancy or excessive questioning.\n\n"
    "If the user indicates they have no other symptoms to discuss, or confirms they are finished, respond ONLY with the exact text: '{end_text}'.\n\n"
    "Historical Context (For your reference to avoid redundant questions and identify potential patterns. Focus questioning on the CURRENT episode):\n"
    "{user_context_string}\n\n"
    "Begin by waiting for the user's initial symptom description. If they have already provided one, ask your first clarifying question."
)
    _SUMMARY_TITLE_SYSTEM_PROMPT = (
    "You are a medical title generation assistant. Your task is to create a very concise title (2-5 words) "
    "that best describes the main symptom(s) discussed in the provided medical interaction summary. \n"
    "The title should be suitable for a quick overview, similar to a medical chart entry subject line.\n\n"
    "Examples of good titles:\n"
    "- 'Acute Headache'\n"
    "- 'Persistent Chest Pain'\n"
    "- 'Fever and Productive Cough'\n"
    "- 'Right Lower Abdominal Pain'\n"
    "- 'Chronic Low Back Pain'\n"
    "- 'Left Knee Swelling and Pain'\n\n"
    "Based on the summary you will be given, provide ONLY the title."
)
    
    _SUMMARY_SYSTEM_PROMPT = (
        "You are a medical summarization assistant. Your task is to generate a concise, factual summary "
        "of the *current* medical interaction provided. Present this summary using clear, well-structured bullet points.\n\n"
        "The summary should:\n"
        "- Focus solely on symptoms reported *during this specific conversation*.\n"
        "- For each distinct symptom or key piece of information, create a separate bullet point.\n"
        "- Each bullet point should be a complete, descriptive sentence or a well-formed, informative phrase.\n"
        "- Detail characteristics for symptoms such as: onset (when it started, how it started), duration (constant/intermittent), severity (e.g., pain scale 0-10, impact on activities), nature/quality (e.g., sharp, dull, burning; type of cough), specific location, any radiation, aggravating factors, alleviating factors, timing/frequency, and any directly associated symptoms mentioned by the user.\n"
        "- Include any other pertinent positive or negative findings shared by the user *during this conversation* (e.g., 'denies fever,' 'recent travel noted,' 'reports attempting [self-care measure] with no relief').\n"
        "- Exclude conversational filler (greetings, thanks), your own questions as the assistant, and any prior medical history unless it was *explicitly re-stated and discussed by the user as directly relevant within this current conversation*.\n\n"
        "**Formatting Instructions for Bullet Points:**\n"
        "1.  **Use the '•' character (Unicode U+2022) at the beginning of each bullet point, followed by a single space.**\n"
        "2.  Ensure each bullet point conveys a specific piece of information clearly and stands as a self-contained statement or phrase.\n"
        "3.  Maintain a professional and objective tone throughout.\n\n"
        "**Example of Desired Bullet Point Format and Content:**\n"
        "Consider a user states: 'I've had a really bad headache since yesterday morning. It's a throbbing pain, mainly behind my left eye, and it's pretty constant, maybe an 8 out of 10. Bright lights make it much worse. I also feel a bit sick to my stomach but haven't thrown up. No fever. I tried taking ibuprofen, but it only helped a little for an hour.'\n\n"
        "Your summary should be formatted like this:\n"
        "• Reports onset of severe headache since yesterday morning.\n"
        "• Describes headache character as throbbing, located primarily behind the left eye.\n"
        "• Notes the headache has been constant in nature.\n"
        "• Rates headache severity as 8/10.\n"
        "• Identifies bright lights as an aggravating factor (photophobia).\n"
        "• Reports associated symptom of nausea, without emesis.\n"
        "• Denies fever.\n"
        "• States trial of ibuprofen provided minimal and temporary relief.\n\n"
        "Your output should be ONLY the bullet-point summary using this exact format and style."
    )

    _DOCTOR_REPORT_SYSTEM_PROMPT_BASE = (
    "You are a medical report assistant. Your task is to generate a concise, organized, and objective clinical note for a doctor. "
    "The note should be based on the 'Current Reason for Visit' and the 'Relevant Past Medical Summary' provided below.\n\n"
    "Current Reason for Visit:\n"
    "\"{visit_reason}\"\n\n"
    "Relevant Past Medical Summary:\n"
    "---\n"
    "{user_context_string}\n"  # This will be your NO_CONTEXT_STRING if empty
    "---\n\n"
    "Instructions for the Clinical Note:\n"
    "1.  **Patient Concern / Reason for Visit:** Clearly state the patient's current reason for the visit as provided: \"{visit_reason}\".\n"
    "2.  **History of Present Illness (HPI) - from Past Summaries:**\n"
    "    - If the 'Relevant Past Medical Summary' section above IS EXACTLY \"{_NO_CONTEXT_STRING}\", then state: \"No past medical summary was provided.\" under this HPI section.\n"
    "    - Otherwise (if past summary IS provided):\n"
    "        - Chronologically summarize information from the 'Relevant Past Medical Summary' that is *directly relevant* to the 'Current Reason for Visit'.\n"
    "        - When detailing specific points from past interactions, use the bullet point style defined in section 4 ('Formatting and Tone').\n" # Explicitly refer to the style
    "        - Focus on dates, initial symptoms, key details (like severity, duration, nature of symptoms, related activities or treatments mentioned).\n"
    "        - Highlight any recurring symptoms, significant patterns, or escalations evident from the logs that pertain to the current visit's reason.\n"
    "        - If multiple past entries exist, synthesize them. Do not just list them verbatim unless a direct quote is essential for context. Individual key findings from different entries can be presented as separate bullet points.\n"
    "        - If, after reviewing the provided past summary, no entries seem relevant to the current reason, briefly state that 'The past summary did not contain information directly relevant to the current complaint.' However, still list any major chronic conditions if these are clearly identifiable from the past summary, potentially using the specified bullet point style for these conditions.\n"
    "3.  **Overall Impression (Factual Summary, No Diagnosis):** Briefly combine the current reason with highly relevant historical points (if any) into a 1-2 sentence factual overview of the patient's situation leading to this visit. This section is typically narrative, not bulleted.\n"
    "4.  **Formatting and Tone:**\n"
    "    - The report must be objective, clear, and factual. Use professional medical terminology where appropriate, but ensure overall understandability.\n"
    "    - Use clear headings for sections (e.g., 'Patient Concern', 'History of Present Illness', 'Impression').\n"
    "    - **Bullet Point Style:** When using bullet points for lists or to itemize specific details (especially in the HPI or when listing multiple findings):\n"
    "        *   **Use the '•' character (Unicode U+2022) at the beginning of each bullet point, followed by a single space.**\n"
    "        *   Each bullet point should be a complete, descriptive sentence or a well-formed, informative phrase conveying a specific piece of information.\n"
    "        *   For example, if summarizing a past headache entry: \"• Reported onset of severe headache on 2023-10-15.\"\n" # Short example of style application
    "    - Be concise. Doctors appreciate brevity.\n"
    "5.  **Crucial Exclusions:**\n"
    "    - Do NOT provide any diagnosis.\n"
    "    - Do NOT suggest any medical advice or treatments.\n"
    "    - Do NOT interpret findings beyond what is stated; stick to reporting the provided information.\n\n"
    "For context, the current time when this report is being generated is: {current_time}.\n\n"
    "Generate the clinical note now based on these instructions."
)

    def __init__(self, api_key: str=api_key, model_name: str = 'gemini-2.5-flash-preview-05-20', user_context: Any = None, end_text: str = "FINISHED"):
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
        
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        doctor_report_prompt_instruction = self._DOCTOR_REPORT_SYSTEM_PROMPT_BASE.format(
            visit_reason=visit_reason,
            user_context_string=self.formatted_user_context_str,
            current_time=current_time
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

