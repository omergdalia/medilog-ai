import os
from uuid import UUID

from dotenv import load_dotenv
from pydantic.v1 import UUID4
from supabase import create_client, Client
from datetime import datetime, UTC
from typing import Optional, List


load_dotenv()  # Load variables from .env

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials in environment variables")

class Database:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # ------------
    # Patients
    # ------------

    # def add_patient(self, name: str, age: int, gender: str) -> dict:
    #     response = self.supabase.table("patients").insert({
    #         "name": name,
    #         "age": age,
    #         "gender": gender
    #     }).execute()
    #     if response.error:
    #         raise Exception(f"Add patient failed: {response.error.message}")
    #     return response.data[0]
    #
    # def update_patient_data(self, patient_id: str, name: Optional[str] = None,
    #                         age: Optional[int] = None, gender: Optional[str] = None) -> dict:
    #     update_fields = {k: v for k, v in {
    #         "name": name,
    #         "age": age,
    #         "gender": gender
    #     }.items() if v is not None}
    #
    #     response = self.supabase.table("patients").update(update_fields).eq("id", patient_id).execute()
    #     if response.error:
    #         raise Exception(f"Update patient failed: {response.error.message}")
    #     return response.data[0]
    #
    # def get_patient(self, patient_id: UUID) -> dict:
    #     response = self.supabase.table("patients").select("*").eq("id", patient_id).single().execute()
    #     if response.error:
    #         raise Exception(f"Get patient failed: {response.error.message}")
    #     return response.data

    # ------------
    # Symptoms
    # ------------

    def add_symptom(self, patient_id: UUID, symptom_summary: str,
                    timestamp: Optional[datetime] = None) -> dict:
        if timestamp is None:
            timestamp = datetime.now(UTC)

        try:
            response = self.supabase.table("symptoms").insert({
                "patient_id": str(patient_id),
                "symptom_summary": symptom_summary,
                "timestamp": timestamp.isoformat()
            }).execute()
        except Exception as e:
            raise Exception(f"Insert failed: {str(e)}")

        return response.data[0]  # usually returns a list

    def get_symptoms_for_patient(self, patient_id: UUID) -> list[dict]:
        try:
            response = self.supabase.table("symptoms") \
                .select("*") \
                .eq("patient_id", str(patient_id)) \
                .order("timestamp", desc=False) \
                .execute()
        except Exception as e:
            raise Exception(f"Fetch failed: {str(e)}")

        return response.data  # List of rows

# Example usage:
# db = Database(url="...", key="...")
#
# # Record a symptom report
# db.add_symptom(
#     patient_id="abc123",
#     symptom_summary="Recurring sharp headaches in the morning"
# )
