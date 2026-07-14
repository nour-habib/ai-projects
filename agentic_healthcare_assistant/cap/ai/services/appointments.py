from backend import repository
from backend.schedule import Scheduler


def find_slots(doctor_id: str, date: str):
    try:
        return Scheduler().find_slots(doctor_id, date)
    except Exception as e:
        return f"Error finding an appointment: {e}"


def book(patient_id: str, doctor_id: str, start_ts: str, reason: str):
    try:
        return Scheduler().book(patient_id, doctor_id, start_ts, reason)
    except Exception as e:
        return f"Error booking: {e}"


def cancel(appointment_id: str):
    try:
        return Scheduler().cancel(appointment_id)
    except Exception as e:
        return f"Error cancelling appointment: {e}"


def list_appointments(patient_id: str | None = None, doctor_id: str | None = None):
    try:
        return repository.list_appointments(patient_id, doctor_id)
    except Exception as e:
        return f"Error listing appointments: {e}"
