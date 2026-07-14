"""Doctor Schedule API.

A SQLite-backed scheduler: availability is derived from fixed working hours
minus existing bookings in the appointments table.
"""

from datetime import datetime, time, timedelta

from backend import repository

# Working hours: weekdays, 30-minute slots.
WORK_START = time(9, 0)
WORK_END = time(17, 0)
SLOT_MINUTES = 30


class Scheduler:
    """Discovers doctors/slots and creates or cancels bookings (SQLite-backed)."""

    def find_doctors(self, specialty: str | None = None) -> list[dict]:
        return repository.list_doctors(specialty=specialty)

    def find_slots(self, doctor_id: str, date: str) -> list[dict]:
        """Return open slots for a doctor on a given YYYY-MM-DD date."""
        day = datetime.strptime(date, "%Y-%m-%d").date()
        if day.weekday() >= 5:  # weekend
            return []

        booked = {
            appt["start_ts"]
            for appt in repository.list_appointments(doctor_id=doctor_id)
            if appt["status"] == "booked" and appt["start_ts"].startswith(date)
        }

        slots = []
        cursor = datetime.combine(day, WORK_START)
        end_of_day = datetime.combine(day, WORK_END)
        while cursor < end_of_day:
            start_iso = cursor.isoformat()
            slot_end = cursor + timedelta(minutes=SLOT_MINUTES)
            if start_iso not in booked:
                slots.append({"start_ts": start_iso, "end_ts": slot_end.isoformat()})
            cursor = slot_end
        return slots

    def book(self, patient_id: str, doctor_id: str, start_ts: str, reason: str | None = None) -> dict:
        start = datetime.fromisoformat(start_ts)
        end = start + timedelta(minutes=SLOT_MINUTES)
        return repository.create_appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            start_ts=start.isoformat(),
            end_ts=end.isoformat(),
            reason=reason,
        )

    def cancel(self, appointment_id: str) -> None:
        repository.set_appointment_status(appointment_id, "cancelled")
