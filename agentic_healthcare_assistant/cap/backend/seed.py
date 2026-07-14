"""Initialize the SQLite database and load seed data.

Idempotent: creates tables, upserts the seed patients and doctors, and adds a
couple of sample appointments if none exist yet. Run via `make seed`.
"""

from backend import repository
from backend.db import init_db
from backend.schedule import Scheduler
from backend.seed_data import DOCTORS, PATIENTS


def seed() -> None:
    init_db()

    for patient in PATIENTS.values():
        repository.upsert_patient(patient)

    for doctor in DOCTORS:
        repository.upsert_doctor(doctor)

    # Add a couple of sample appointments only if the table is empty.
    if not repository.list_appointments():
        client = Scheduler()
        # Robert Chen with Dr. Nguyen.
        slots = client.find_slots("dr_nguyen", "2026-06-22")
        if slots:
            client.book("robert_chen", "dr_nguyen", slots[0]["start_ts"], reason="CKD follow-up")
        # Maria Gomez with Dr. Lee.
        slots = client.find_slots("dr_lee", "2026-06-23")
        if slots:
            client.book("maria_gomez", "dr_lee", slots[2]["start_ts"], reason="Post-MI review")

    print(
        f"Seeded {len(PATIENTS)} patients, {len(DOCTORS)} doctors, "
        f"{len(repository.list_appointments())} appointments."
    )


if __name__ == "__main__":
    seed()
