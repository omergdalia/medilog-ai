from db import Database
from uuid import UUID

PATIENT_ID = UUID("00000000-0000-0000-0000-000000000000")

SUMMARIES = {
    'headache': "Patient reports a headache that started yesterday. The pain is moderate and located at the temples. No nausea or vomiting reported.",
    'stomachache': "Patient reports a stomachache that started after eating lunch. The pain is crampy and located in the lower abdomen. No diarrhea or constipation reported.",
    'ear_pain': "Patient reports ear pain that started last night. The pain is sharp and located in the right ear. No hearing loss or discharge reported."
}


def add_symptom(db, patient, title):
    # Test adding a symptom
    added_symptom = db.add_symptom(patient_id=patient, title=title, symptom_summary=SUMMARIES[title])
    print("Added Symptom:", added_symptom)
    # Test getting symptoms for the patient
    symptoms = db.get_symptoms_for_patient(patient_id=patient)
    print("Symptoms for Patient:", symptoms)


def tests():
    db = Database()
    # Test adding a patient
    try:
        patient = db.add_patient(patient_id=PATIENT_ID, email="aaa@gmail.com", age=50, gender='male')
    except Exception as e:
        patient = db.get_patient_by_email('aaa@gmail.com')
    print(patient)
    for title in SUMMARIES.keys():
        add_symptom(db, patient, title)
    # Test getting the patient
    fetched_patient = db.get_patient(patient_id=PATIENT_ID)
    print(fetched_patient)

if __name__ == '__main__':
    tests()