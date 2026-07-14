"""Data-access layer over the SQLite database.

Shared by the Streamlit UI and (later) the agent tools so there is a single
source of truth for reading and writing patients, doctors, and appointments.
"""

import json
import uuid

from backend.db import get_connection

# JSON-encoded list columns on the patients table.
_PATIENT_JSON_FIELDS = ("diagnoses", "medications", "allergies", "alerts", "visits")


def _row_to_patient(row) -> dict:
    patient = dict(row)
    for field in _PATIENT_JSON_FIELDS:
        patient[field] = json.loads(patient[field]) if patient[field] else []
    return patient


# --- Patients -------------------------------------------------------------

def list_patients() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM patients ORDER BY name").fetchall()
    return [_row_to_patient(r) for r in rows]


def get_patient(patient_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    return _row_to_patient(row) if row else None


def upsert_patient(patient: dict) -> None:
    """Insert or update a patient record (the 'manage records' capability)."""
    record = {
        "id": patient["id"],
        "name": patient["name"],
        "age": patient.get("age"),
        "sex": patient.get("sex"),
        "summary": patient.get("summary"),
        **{f: json.dumps(patient.get(f, [])) for f in _PATIENT_JSON_FIELDS},
    }
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO patients (id, name, age, sex, summary, diagnoses,
                                  medications, allergies, alerts, visits)
            VALUES (:id, :name, :age, :sex, :summary, :diagnoses,
                    :medications, :allergies, :alerts, :visits)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name, age=excluded.age, sex=excluded.sex,
                summary=excluded.summary, diagnoses=excluded.diagnoses,
                medications=excluded.medications, allergies=excluded.allergies,
                alerts=excluded.alerts, visits=excluded.visits
            """,
            record,
        )


# --- Doctors --------------------------------------------------------------

def list_doctors(specialty: str | None = None) -> list[dict]:
    query = "SELECT * FROM doctors"
    params: tuple = ()
    if specialty:
        query += " WHERE LOWER(specialty) = LOWER(?)"
        params = (specialty,)
    query += " ORDER BY name"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def upsert_doctor(doctor: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO doctors (id, name, specialty)
            VALUES (:id, :name, :specialty)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name, specialty=excluded.specialty
            """,
            {"id": doctor["id"], "name": doctor["name"], "specialty": doctor["specialty"]},
        )


# --- Appointments ---------------------------------------------------------

def get_appointment(appointment_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,)).fetchone()
    return dict(row) if row else None


def set_appointment_status(appointment_id: str, status: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id)
        )


def list_appointments(patient_id: str | None = None, doctor_id: str | None = None) -> list[dict]:
    query = "SELECT * FROM appointments"
    clauses, params = [], []
    if patient_id:
        clauses.append("patient_id = ?")
        params.append(patient_id)
    if doctor_id:
        clauses.append("doctor_id = ?")
        params.append(doctor_id)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY start_ts"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def create_appointment(
    patient_id: str,
    doctor_id: str,
    start_ts: str,
    end_ts: str,
    reason: str | None = None,
    status: str = "booked",
) -> dict:
    appointment = {
        "id": uuid.uuid4().hex,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "status": status,
        "reason": reason,
    }
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO appointments (id, patient_id, doctor_id, start_ts, end_ts,
                                      status, reason)
            VALUES (:id, :patient_id, :doctor_id, :start_ts, :end_ts,
                    :status, :reason)
            """,
            appointment,
        )
    return appointment
