from llm.llm_manager import LLMManager
from db.db import Database
from uuid import UUID
from datetime import datetime as dt, UTC
END_REPORT_TOKEN = "<END_REPORT>"

# format 
class User:
    def __init__(self, database: Database, user_id: UUID = None):
        # initialize context load from database
        self.database = database
        user_context = database.get_symptoms_for_patient(user_id)
        self.llm = LLMManager(user_context=user_context)
        self.user_id = user_id
        # initialize context load from database

    def get_response(self, prompt: str):
        response = self.llm.get_response(prompt)
        if END_REPORT_TOKEN in response[-10:]:
            response = response.split(END_REPORT_TOKEN)[0]
            self.save_summary_and_update()
        return response
    
    def get_summary(self):
        return self.llm.get_summary()
    
    def save_summary_and_update(self) -> None:
        '''
        This function updates the database, asks it for a new 
        report, and updates the llm with the updated user context. 
        '''
        try:
            summary = self.get_summary()
        except ValueError as e:
            # if the summary is None, it means that there were no new prompts
            # since the last conversation, so we don't need to update the database
            return
        
        
        summary["timestamp"] = dt.now(UTC).isoformat()
        # update llm user context to include new summary
        self.llm.extend_user_context([summary])

        # add the user_id to the summary
        summary["patient_id"] = self.user_id
        # add the summary to the database
        self.database.add_symptom(timestamp=dt.fromisoformat(summary["timestamp"]), 
                                  patient_id=self.user_id, 
                                  symptom_summary=summary["summary"], 
                                  title=summary["title"] )

    def get_doctor_report(self, reason_for_visit): 
        """
        Makes sure that the user context in the LLM chat is updated
        and creates a doctors report from it.
        """
        # update the user context in the LLM
        self.save_summary_and_update()
        # get the doctor report from the LLM
        return self.llm.get_doctor_report(reason_for_visit)
    