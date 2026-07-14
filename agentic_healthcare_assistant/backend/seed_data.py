"""Seed data for the SQLite database: three patients with distinct histories
and the doctors referenced by their visit notes.

This is the source of truth for `make seed`. It stands in for the EHR / Patient
DB and the doctor roster until real data sources are wired in.
"""

PATIENTS = {
    "robert_chen": {
        "id": "robert_chen",
        "name": "Robert Chen",
        "age": 70,
        "sex": "Male",
        "summary": "Stage 3 chronic kidney disease with comorbid hypertension and type 2 diabetes.",
        "diagnoses": [
            {"condition": "Chronic kidney disease (Stage 3b)", "since": "2021"},
            {"condition": "Hypertension", "since": "2014"},
            {"condition": "Type 2 diabetes mellitus", "since": "2016"},
        ],
        "medications": [
            "Lisinopril 20 mg daily",
            "Metformin 1000 mg twice daily",
            "Furosemide 40 mg daily",
        ],
        "allergies": ["Penicillin"],
        "alerts": [
            "eGFR trending down over last 6 months — monitor renal function.",
            "Avoid NSAIDs (nephrotoxic).",
        ],
        "visits": [
            {"date": "2026-04-12", "provider": "Dr. Patel (Nephrology)", "note": "eGFR 38; adjusted diuretic dose."},
            {"date": "2026-01-08", "provider": "Dr. Nguyen (Primary care)", "note": "Routine diabetes review; HbA1c 7.4%."},
        ],
    },
    "maria_gomez": {
        "id": "maria_gomez",
        "name": "Maria Gomez",
        "age": 54,
        "sex": "Female",
        "summary": "Type 2 diabetes with obesity and a prior myocardial infarction.",
        "diagnoses": [
            {"condition": "Type 2 diabetes mellitus", "since": "2012"},
            {"condition": "Obesity (BMI 34)", "since": "2010"},
            {"condition": "Myocardial infarction (post-MI)", "since": "2022"},
        ],
        "medications": [
            "Atorvastatin 40 mg daily",
            "Aspirin 81 mg daily",
            "Empagliflozin 10 mg daily",
        ],
        "allergies": ["Sulfa drugs"],
        "alerts": [
            "Cardiac history — coordinate any new medication with cardiology.",
        ],
        "visits": [
            {"date": "2026-05-02", "provider": "Dr. Adeyemi (Cardiology)", "note": "Stable; continue statin and antiplatelet."},
            {"date": "2026-02-20", "provider": "Dr. Nguyen (Primary care)", "note": "Weight management counseling; HbA1c 8.1%."},
        ],
    },
    "james_okafor": {
        "id": "james_okafor",
        "name": "James Okafor",
        "age": 38,
        "sex": "Male",
        "summary": "Generally healthy adult with mild persistent asthma and seasonal allergies.",
        "diagnoses": [
            {"condition": "Mild persistent asthma", "since": "2009"},
            {"condition": "Seasonal allergic rhinitis", "since": "2015"},
        ],
        "medications": [
            "Albuterol inhaler as needed",
            "Fluticasone nasal spray (seasonal)",
        ],
        "allergies": ["Pollen", "Dust mites"],
        "alerts": [],
        "visits": [
            {"date": "2026-03-30", "provider": "Dr. Lee (Pulmonology)", "note": "Asthma well controlled; no exacerbations."},
        ],
    },
}

DOCTORS = [
    {"id": "dr_nguyen", "name": "Dr. Nguyen", "specialty": "General Physician"},
    {"id": "dr_lee", "name": "Dr. Lee", "specialty": "General Physician"},
]
