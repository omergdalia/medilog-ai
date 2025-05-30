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
    _DOCTOR_REPORT_REASON_TITLE_SYSTEM_PROMPT = (
        "You are a medical report assistant specializing in creating concise section titles for clinical notes. "
        "Your task is to generate a brief title (3-7 words) for the 'Patient Concern / Reason for Visit' section of a doctor's report, based on the provided reason.\n\n"
        "INPUT:\n"
        "The 'Reason for Visit' will be provided below.\n\n"
        "TASK:\n"
        "1.  Analyze the provided 'Reason for Visit'.\n"
        "2.  Condense its main theme into a clear, professional title of 3-7 words.\n"
        "3.  The title should be suitable for a clinical note heading.\n"
        "4.  CRUCIAL: Do NOT include any interpretation, diagnosis, or medical advice in the title.\n\n"
        "EXAMPLES OF DESIRED TITLES (based on hypothetical visit reasons):\n"
        "If Reason for Visit is 'I've been having a really bad cough for a week and some fever.':\n"
        "   - Possible Title: 'Persistent Cough and Fever Evaluation'\n"
        "If Reason for Visit is 'My right knee has been very painful and swollen since I twisted it playing soccer.':\n"
        "   - Possible Title: 'Right Knee Pain and Swelling Post-Injury'\n"
        "If Reason for Visit is 'Follow-up for my high blood pressure.':\n"
        "   - Possible Title: 'Hypertension Follow-Up Visit'\n\n"
        "OUTPUT:\n"
        "Return ONLY the generated title. Do not include any other text, explanation, or quotation marks around the title.\n\n"
        "Reason for Visit:\n"
        "\"{visit_reason}\"" # Keeping the quotes as per your existing structure for variable injection
    )

    _DOCTOR_REPORT_HPI_SYSTEM_PROMPT = (
        "You are a clinical note assistant specializing in composing the 'History of Present Illness (HPI)' section for medical reports. "
        "Your task is to synthesize relevant information from the patient's 'Relevant Past Medical Summary' that directly pertains to their 'Current Reason for Visit'.\n\n"
        "INPUTS:\n"
        "1. Current Reason for Visit: \"{visit_reason}\"\n" # Added this as input
        "2. Relevant Past Medical Summary (a chronological collection of past interaction summaries):\n"
        "   ---\n"
        "   {user_context_string}\n"
        "   ---\n\n"
        "TASK:\n"
        "1.  Carefully review the 'Current Reason for Visit'.\n"
        "2.  Analyze the 'Relevant Past Medical Summary' to identify entries, symptoms, or details (e.g., dates, severity, duration, nature, treatments mentioned) that are *directly relevant* to the 'Current Reason for Visit'.\n"
        "3.  Chronologically synthesize these relevant details into the HPI.\n"
        "4.  If recurring patterns, escalations, or significant prior events related to the current complaint are evident in the summary, highlight them.\n"
        "5.  If, after thorough review, the 'Relevant Past Medical Summary' contains no information directly pertinent to the 'Current Reason for Visit', the HPI should consist of a single statement: \"The past summary did not contain information directly relevant to the current complaint.\"\n"
        "6.  If major chronic conditions are clearly identifiable from the past summary AND are relevant background (even if not directly part of the acute reason for visit), they may be briefly mentioned. For example: 'Patient has a known history of [chronic condition].'\n"
        "7.  CRUCIAL: Remain strictly objective. Do NOT provide any diagnosis, interpretation beyond factual reporting, or medical advice.\n\n"
        "OUTPUT FORMATTING (using the '•' bullet character):\n"
        "-   Each distinct relevant finding or summarized point from the past medical summary should be presented as a separate bullet point.\n"
        "-   Start each bullet point with the '•' character (Unicode U+2022), followed by a single space.\n"
        "-   Bullet points should be concise, factual, and complete sentences or informative phrases.\n\n"
        "EXAMPLE OF DESIRED HPI OUTPUT (hypothetical, assuming relevant past entries):\n"
        "If Reason for Visit is 'Follow-up for persistent cough' and past summary includes:\n"
        "  '[2023-10-15] Cough and Mild Fever: Patient reported a dry cough starting 3 days prior, with mild fever. Advised rest.'\n"
        "  '[2023-10-22] Worsening Cough: Patient reports cough is now productive, green sputum. Denies fever. Prescribed amoxicillin.'\n\n"
        "Possible HPI Output:\n"
        "• Patient initially presented on 2023-10-15 with a dry cough and mild fever of 3 days duration.\n"
        "• On 2023-10-22, the cough was reported as productive with green sputum; amoxicillin was prescribed at that time.\n"
        "• Current visit is for follow-up of this persistent cough.\n\n"
        "OUTPUT:\n"
        "Return ONLY the HPI section, formatted with '•' bullet points as specified. If no relevant history, return the single specified sentence."
    )

    _DOCTOR_REPORT_IMPRESSION_SYSTEM_PROMPT = (
    "You are a medical information assistant tasked with creating an 'Observational Summary' section for a doctor's preliminary report. "
    "This summary should highlight key patterns, evolutions, or significant points derived *strictly* from the provided 'Concise Reason for Visit' and the 'History of Present Illness (HPI) Section'. "
    "It is NOT a clinical diagnosis or interpretation, but rather an objective distillation of the presented information to aid the doctor's review.\n\n"
    "INPUTS:\n"
    "1. Concise Reason for Visit: \"{visit_reason}\"\n"
    "2. History of Present Illness (HPI) Section (which details relevant past events):\n"
    "   {hpi}\n\n"
    "TASK:\n"
    "1.  Carefully review the 'Concise Reason for Visit' and the 'HPI Section'.\n"
    "2.  Identify any notable patterns (e.g., recurrence of symptoms, progression over time, response or lack of response to previous mentions of self-care/interventions if detailed in HPI), or significant temporal relationships between the current visit reason and the HPI.\n"
    "3.  Synthesize these observations into a concise 1-3 sentence summary.\n"
    "4.  The summary should connect the current reason for visit with the most salient observations from the HPI, focusing on *what* has happened rather than *why* (which is for the doctor to determine).\n"
    "5.  CRUCIAL: This summary must be strictly factual and observational. It must NOT contain any diagnostic language, clinical interpretations, suggestions of underlying causes, or predictions. Stick to summarizing the timeline and reported events.\n\n"
    "EXAMPLE OF DESIRED OBSERVATIONAL SUMMARY OUTPUT:\n"
    "If Reason for Visit is 'Follow-up for persistent cough' and HPI details a cough that started 2 weeks ago, was noted as 'dry' then became 'productive', and a past entry mentioned a similar cough episode 6 months prior:\n\n"
    "Possible Observational Summary Output:\n"
    "\"The current presentation for a persistent cough follows a reported change in cough character from dry to productive over the past two weeks. The HPI also notes a previous episode of a similar cough approximately six months ago.\"\n\n"
    "If Reason for Visit is 'Worsening knee pain' and HPI details initial mild pain after a fall 1 month ago, which has gradually increased despite rest:\n\n"
    "Possible Observational Summary Output:\n"
    "\"This visit is for knee pain that reportedly began as mild following a fall one month prior and has since progressively worsened despite rest, according to the HPI.\"\n\n"
    "OUTPUT:\n"
    "Return ONLY the 1-3 sentence 'Observational Summary'. Do not include any other text, headings, or explanations."
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
                



    def get_doctor_report(self, visit_reason: str) -> dict[str, str]:
        """
        Generate a clinical note split into reason (title), HPI, and Impression.

        Args:
            visit_reason (str): The reason for the patient's visit.

        Returns:
            dict: Dictionary with keys 'reason', 'HPI', and 'Impression'.
        """
        if not visit_reason:
            raise ValueError("Visit reason must be provided for the doctor report.")
        if not self.formatted_user_context_str or self.formatted_user_context_str == self._NO_CONTEXT_STRING:
            raise ValueError("User context must be provided for the doctor report.")

        # 1. Generate Title (Reason)
        title_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=self._DOCTOR_REPORT_REASON_TITLE_SYSTEM_PROMPT.format(visit_reason=visit_reason)
        )
        try:
            title_response = title_model.generate_content("Generate a concise title for the reason for visit.")
            title = title_response.text.strip()
        except Exception as e:
            raise RuntimeError("Failed to generate reason/title") from e

        # 2. Generate HPI
        hpi_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=self._DOCTOR_REPORT_HPI_SYSTEM_PROMPT.format(user_context_string=self.formatted_user_context_str, visit_reason=title)
        )
        try:
            hpi_response = hpi_model.generate_content("Now generate the history of present illness.")
            hpi = hpi_response.text.strip()
        except Exception as e:
            raise RuntimeError("Failed to generate HPI") from e

        # 3. Generate Impression
        impression_model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=self._DOCTOR_REPORT_IMPRESSION_SYSTEM_PROMPT.format(
                visit_reason=title,
                hpi=hpi
            )
        )
        try:
            impression_response = impression_model.generate_content("Now generate the overall impression.")
            impression = impression_response.text.strip()
        except Exception as e:
            raise RuntimeError("Failed to generate Impression") from e

        return {
            "reason": title,
            "HPI": hpi,
            "impression": impression
        }


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

