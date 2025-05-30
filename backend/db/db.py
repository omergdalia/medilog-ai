import os
from uuid import UUID

from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, UTC
from typing import Optional

GENDERS = ('male', 'female')

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

    def add_patient(self, patient_id: UUID, email: str, age: int, gender: str, allergies: list = None, chronic_diseases: list = None, medications: list = None) -> dict:
        gender = gender.lower()
        if gender not in GENDERS:
            raise ValueError(f"Gender should be one of {GENDERS}, but got {gender}")
        if age < 0:
            raise ValueError("Age must be a non-negative integer")
        if allergies is None:
            allergies = []
        if chronic_diseases is None:
            chronic_diseases = []
        if medications is None:
            medications = []
        try:
            response = self.supabase.table("patients").insert({
                "patient_id": str(patient_id),
                'email': email,
                "age": age,
                "gender": gender,
                "allergies": allergies,
                "chronic_diseases": chronic_diseases,
                "medications": medications
            }).execute()
        except Exception as e:
            raise Exception(f"Insert failed: {str(e)}")
        return response.data[0]["patient_id"]

    def update_patient_data(self, patient_id: UUID, email: Optional[str] = None,
                            age: Optional[int] = None, gender: Optional[str] = None, allergies: Optional[list] = None,
                            chronic_diseases: Optional[list] = None, medications: Optional[list] = None) -> dict:
        if gender is not None and gender not in GENDERS:
            raise ValueError(f"Gender should be one of {GENDERS}, but got {gender}")
        if age is not None and age < 0:
            raise ValueError("Age must be a non-negative integer")
        update_fields = {k: v for k, v in {
            "email": email,
            "age": age,
            "gender": gender,
            "allergies": allergies,
            "chronic_diseases": chronic_diseases,
            "medications": medications
        }.items() if v is not None}

        try:
            response = self.supabase.table("patients").update(update_fields).eq("patient_id", patient_id).execute()
        except Exception as e:
            raise Exception(f"Update failed: {str(e)}")
        return response.data[0]

    def get_patient(self, patient_id: UUID) -> dict:
        try:
            response = self.supabase.table("patients").select("*").eq("patient_id", patient_id).single().execute()
        except Exception as e:
            raise Exception(f"Fetch failed: {str(e)}")
        return response.data

    # ------------
    # Symptoms
    # ------------

    def add_symptom(self, patient_id: UUID, symptom_summary: str, title: str,
                    timestamp: Optional[datetime] = None) -> dict:
        if timestamp is None:
            timestamp = datetime.now(UTC)

        try:
            response = self.supabase.table("symptoms").insert({
                "patient_id": str(patient_id),
                "timestamp": timestamp.isoformat(),
                "title": title,
                "summary": symptom_summary
            }).execute()
        except Exception as e:
            raise Exception(f"Insert failed: {str(e)}")

        # return the symptom without the patient_id and id fields
        if not response.data or len(response.data) == 0:
            raise Exception("Insert did not return any data")

        return response.data[0]  # usually returns a list

    def get_symptoms_for_patient(self, patient_id: UUID) -> list[dict]:
        try:
            response = self.supabase.table("symptoms") \
                .select("timestamp, title, summary") \
                .eq("patient_id", str(patient_id)) \
                .order("timestamp", desc=False) \
                .execute()
        except Exception as e:
            raise Exception(f"Fetch failed: {str(e)}")
        return response.data  # List of rows

    def get_patient_by_email(self, email: str) -> UUID:
        """
        Fetch a user by their email address.
        Returns None if no user is found.
        """
        try:
            response = self.supabase.table("patients").select("*").eq("email", email).single().execute()
            return UUID(response.data["patient_id"])
        except Exception as e:
            raise Exception(f"Fetch failed: {str(e)}")

# Example usage:
# db = Database(url="...", key="...")
#
# # Record a symptom report
# db.add_symptom(
#     patient_id="abc123",
#     symptom_summary="Recurring sharp headaches in the morning"
# )
