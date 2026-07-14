"""Functional evaluation: deterministic checks of the appointment module.

Booking/cancellation are not fuzzy, so we don't use an LLM judge here. We drive
the same service functions the agent's tools call and assert the resulting DB
state, reporting a pass/fail success rate per check.
"""

from datetime import date, timedelta

from ai.services import appointments
from backend import repository

PATIENT_ID = "james_okafor"
DOCTOR_ID = "dr_nguyen"


def _future_weekday(days_ahead: int = 60) -> str:
    """A date well past the seed data, rolled forward to a weekday."""
    day = date.today() + timedelta(days=days_ahead)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day.isoformat()


def run_functional_eval() -> dict:
    """Run the booking-module checks and return success rate + details."""
    results = []

    def check(name: str, passed: bool, note: str = ""):
        results.append({"check": name, "passed": bool(passed), "note": note})

    test_date = _future_weekday()

    # 1. Slots are available for a weekday.
    slots = appointments.find_slots(DOCTOR_ID, test_date)
    has_slots = isinstance(slots, list) and len(slots) > 0
    check("find_slots_returns_slots", has_slots, f"{len(slots) if has_slots else 0} slots")
    if not has_slots:
        return _summarize(results)

    start_ts = slots[0]["start_ts"]

    # 2. Booking creates an appointment with status "booked".
    booked = appointments.book(PATIENT_ID, DOCTOR_ID, start_ts, "eval test")
    appt_id = booked.get("id") if isinstance(booked, dict) else None
    stored = repository.get_appointment(appt_id) if appt_id else None
    check(
        "book_creates_appointment",
        bool(stored) and stored["status"] == "booked",
        f"id={appt_id}",
    )

    # 3. The booked slot is no longer offered.
    after = appointments.find_slots(DOCTOR_ID, test_date)
    still_open = any(s["start_ts"] == start_ts for s in after)
    check("booked_slot_removed_from_availability", not still_open)

    # 4. Cancelling flips the status to "cancelled".
    if appt_id:
        appointments.cancel(appt_id)
        after_cancel = repository.get_appointment(appt_id)
        check(
            "cancel_sets_status_cancelled",
            bool(after_cancel) and after_cancel["status"] == "cancelled",
        )

    # 5. The cancelled slot is offered again.
    freed = appointments.find_slots(DOCTOR_ID, test_date)
    reopened = any(s["start_ts"] == start_ts for s in freed)
    check("cancelled_slot_reopened", reopened)

    return _summarize(results)


def _summarize(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(r["passed"] for r in results)
    return {
        "module": "appointments",
        "success_rate": round(passed / total, 3) if total else 0.0,
        "passed": passed,
        "total": total,
        "details": results,
    }
