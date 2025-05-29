from db import Database
from uuid import UUID

PATIENT_ID = UUID("00000000-0000-0000-0000-000000000000")

def tests():
    db = Database()

    # Test adding a patient
    # patient = db.add_patient(PATIENT_ID, age=30, gender='male')
    # print("Added Patient:", patient)
    # Test updating the patient
    # updated_patient = db.update_patient_data(patient_id=PATIENT_ID, age=31)
    # print("Updated Patient:", updated_patient)
    # Test getting the patient
    fetched_patient = db.get_patient(patient_id=PATIENT_ID)
    # assert fetched_patient == updated_patient, "Fetched patient does not match updated patient"
    # Test adding a symptom
    added_symptom = db.add_symptom(patient_id=PATIENT_ID, title='pain in the butt', symptom_summary="Buttache")
    print("Added Symptom:", added_symptom)
    # Test getting symptoms for the patient
    symptoms = db.get_symptoms_for_patient(patient_id=PATIENT_ID)
    print("Symptoms for Patient:", symptoms)

if __name__ == '__main__':
    tests()