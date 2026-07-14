import os
import sys

# Make the repo root importable so `backend` resolves when run via streamlit.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime

import streamlit as st

from apiService import book_appointment, handle_query, run_agent
from backend import repository
from backend.schedule import Scheduler


@st.cache_data(show_spinner=False)
def cached_disease_search(query: str) -> dict:
    """Cache disease searches by query so unrelated reruns don't re-call the API."""
    return handle_query(query)

st.set_page_config(page_title="Agentic Healthcare Assistant", layout="wide")
st.title("🏥 Agentic Healthcare Assistant")

patient_tab, doctor_tab = st.tabs(["👤 Patient View", "🩺 Doctor View"])


def render_patient(patient: dict) -> None:
    """Render a single patient's record (single-column; lives in the main area)."""
    st.caption(patient["summary"])
    st.markdown(
        f"**Age:** {patient['age']} &nbsp;·&nbsp; **Sex:** {patient['sex']} "
        f"&nbsp;·&nbsp; **Active diagnoses:** {len(patient['diagnoses'])}"
    )

    for alert in patient["alerts"]:
        st.warning(alert, icon="⚠️")

    st.subheader("Diagnoses")
    for dx in patient["diagnoses"]:
        st.markdown(f"- **{dx['condition']}** — since {dx['since']}")

    st.subheader("Medications")
    for med in patient["medications"]:
        st.markdown(f"- {med}")

    st.subheader("Allergies")
    st.markdown(
        "\n".join(f"- {a}" for a in patient["allergies"]) or "_None recorded_"
    )

    st.subheader("Visit history")
    for v in patient["visits"]:
        st.markdown(f"- **{v['date']}** — {v['provider']}: {v['note']}")


def _fmt_slot(start_ts: str) -> str:
    """Human-friendly label for an ISO timestamp, e.g. 'Tue Jun 23, 10:00'."""
    return datetime.fromisoformat(start_ts).strftime("%a %b %d, %H:%M")


def _slot_picker(doctor_id: str, key_prefix: str, default_date=None, include_ts: str | None = None):
    """Render date + time pickers; return the selected slot start_ts (or None)."""
    appt_date = st.date_input("Date", value=default_date or date.today(), key=f"{key_prefix}_date")
    if appt_date is None:
        st.caption("Pick a date to see open slots.")
        return None
    date_str = appt_date.strftime("%Y-%m-%d")

    slots = Scheduler().find_slots(doctor_id, date_str)
    # When editing, surface the appointment's own slot so the time can be kept.
    if include_ts and include_ts.startswith(date_str) and include_ts not in {s["start_ts"] for s in slots}:
        slots.append({"start_ts": include_ts})
        slots.sort(key=lambda s: s["start_ts"])

    if not slots:
        st.caption("No open slots on that date (weekends are closed).")
        return None

    labels = {_fmt_slot(s["start_ts"]): s["start_ts"] for s in slots}
    index = list(labels.values()).index(include_ts) if include_ts in labels.values() else 0
    chosen = st.selectbox("Time", list(labels.keys()), index=index, key=f"{key_prefix}_time")
    return labels[chosen]


def _render_booking_form(patient: dict) -> None:
    st.markdown("**Book appointment**")
    doctors = repository.list_doctors()
    doctor = st.selectbox(
        "Doctor", doctors, format_func=lambda d: f"{d['name']} — {d['specialty']}", key="book_doctor"
    )
    start_ts = _slot_picker(doctor["id"], "book")
    reason = st.text_input("Reason", key="book_reason")

    c1, c2 = st.columns(2)
    if c1.button("Confirm", key="book_confirm", use_container_width=True, disabled=start_ts is None):
        book_appointment(patient["id"], doctor["id"], start_ts, reason or None)
        st.session_state["appt_mode"] = "list"
        st.rerun(scope="fragment")
    if c2.button("Back", key="book_back", use_container_width=True):
        st.session_state["appt_mode"] = "list"
        st.rerun(scope="fragment")


def _render_edit_form(patient: dict) -> None:
    appt = repository.get_appointment(st.session_state.get("appt_edit_id"))
    if not appt:
        st.session_state["appt_mode"] = "list"
        st.rerun(scope="fragment")

    doctors = {d["id"]: d for d in repository.list_doctors()}
    doc = doctors.get(appt["doctor_id"], {})
    st.markdown(f"**Edit appointment** — {doc.get('name', '?')}")

    current = datetime.fromisoformat(appt["start_ts"])
    start_ts = _slot_picker(appt["doctor_id"], "edit", default_date=current.date(), include_ts=appt["start_ts"])
    reason = st.text_input("Reason", value=appt["reason"] or "", key="edit_reason")

    c1, c2 = st.columns(2)
    if c1.button("Save", key="edit_save", use_container_width=True, disabled=start_ts is None):
        # No backend "update": reschedule = cancel old + book new (also sets reason).
        Scheduler().cancel(appt["id"])
        Scheduler().book(patient["id"], appt["doctor_id"], start_ts, reason or None)
        st.session_state["appt_mode"] = "list"
        st.session_state.pop("appt_edit_id", None)
        st.rerun(scope="fragment")
    if c2.button("Back", key="edit_back", use_container_width=True):
        st.session_state["appt_mode"] = "list"
        st.session_state.pop("appt_edit_id", None)
        st.rerun(scope="fragment")


def _render_appt_list(patient: dict) -> None:
    doctors = {d["id"]: d for d in repository.list_doctors()}
    appts = [a for a in repository.list_appointments(patient_id=patient["id"]) if a["status"] == "booked"]

    if not appts:
        st.caption("No current bookings.")

    for a in appts:
        doc = doctors.get(a["doctor_id"], {})
        st.markdown(
            f"**{_fmt_slot(a['start_ts'])}**  \n"
            f"{doc.get('name', '?')} · {doc.get('specialty', '')}  \n"
            f"_{a['reason'] or 'no reason given'}_"
        )
        if st.session_state.get("appt_cancel_id") == a["id"]:
            st.warning("Confirm cancel?")
            cc1, cc2 = st.columns(2)
            if cc1.button("Yes, cancel", key=f"yes_{a['id']}", use_container_width=True):
                Scheduler().cancel(a["id"])
                st.session_state.pop("appt_cancel_id", None)
                st.rerun(scope="fragment")
            if cc2.button("No", key=f"no_{a['id']}", use_container_width=True):
                st.session_state.pop("appt_cancel_id", None)
                st.rerun(scope="fragment")
        else:
            c1, c2 = st.columns(2)
            if c1.button("Cancel", key=f"cancel_{a['id']}", use_container_width=True):
                st.session_state["appt_cancel_id"] = a["id"]
                st.rerun(scope="fragment")
            if c2.button("Edit", key=f"edit_{a['id']}", use_container_width=True):
                st.session_state["appt_mode"] = "edit"
                st.session_state["appt_edit_id"] = a["id"]
                st.rerun(scope="fragment")
        st.divider()

    if st.button("📅 Book appointment", key="book_btn", use_container_width=True):
        st.session_state["appt_mode"] = "book"
        st.rerun(scope="fragment")


@st.fragment
def render_appointment_module(patient: dict) -> None:
    """Right-hand appointment panel — reruns in isolation so the page stays put."""
    st.subheader("📅 Appointments")

    # Reset transient view state when the selected patient changes.
    if st.session_state.get("appt_patient") != patient["id"]:
        st.session_state["appt_patient"] = patient["id"]
        st.session_state["appt_mode"] = "list"
        st.session_state.pop("appt_edit_id", None)
        st.session_state.pop("appt_cancel_id", None)

    mode = st.session_state.get("appt_mode", "list")
    if mode == "book":
        _render_booking_form(patient)
    elif mode == "edit":
        _render_edit_form(patient)
    else:
        _render_appt_list(patient)


def _clear_disease_search(key: str) -> None:
    """Reset the search box (runs as a button callback before the widget reloads)."""
    st.session_state[key] = ""


def render_disease_search(key: str = "disease_query") -> None:
    """Disease-information search bar — retrieves from MedlinePlus and summarizes."""
    col_input, col_btn = st.columns([6, 1], vertical_alignment="bottom")
    with col_input:
        query = st.text_input(
            "🔎 Search disease-related information",
            key=key,
            placeholder="e.g. latest treatments for chronic kidney disease",
        )
    with col_btn:
        st.button(
            "Clear",
            key=f"{key}_clear",
            on_click=_clear_disease_search,
            args=(key,),
            use_container_width=True,
        )

    if not query:
        return

    with st.spinner("Searching MedlinePlus…"):
        result = cached_disease_search(query)

    if result["error"]:
        st.error(result["error"])
        return

    if not result["sources"]:
        st.info("No results found.")
        return

    for s in result["sources"]:
        org = f" · {s['organization']}" if s["organization"] else ""
        st.markdown(f"#### [{s['title']}]({s['url']}){org}")
        if s["summary"]:
            st.write(s["summary"])


def _parse_lines(text: str) -> list[str]:
    return [ln.strip() for ln in text.splitlines() if ln.strip()]


def _parse_diagnoses(text: str) -> list[dict]:
    out = []
    for ln in _parse_lines(text):
        parts = [p.strip() for p in ln.split("|")]
        out.append({"condition": parts[0], "since": parts[1] if len(parts) > 1 else ""})
    return out


def _parse_visits(text: str) -> list[dict]:
    out = []
    for ln in _parse_lines(text):
        parts = [p.strip() for p in ln.split("|")]
        out.append(
            {
                "date": parts[0] if len(parts) > 0 else "",
                "provider": parts[1] if len(parts) > 1 else "",
                "note": parts[2] if len(parts) > 2 else "",
            }
        )
    return out


def render_patient_editor(patient: dict, edit_key: str) -> None:
    """Editable form for a patient's record; saves back to SQLite."""
    with st.form(f"form_{patient['id']}"):
        name = st.text_input("Name", patient["name"])
        age = st.number_input("Age", min_value=0, max_value=120, value=int(patient["age"] or 0))
        sex = st.text_input("Sex", patient["sex"] or "")
        summary = st.text_area("Summary", patient["summary"] or "")
        diagnoses_text = st.text_area(
            "Diagnoses (one per line: condition | since)",
            "\n".join(f"{d['condition']} | {d.get('since', '')}" for d in patient["diagnoses"]),
        )
        medications_text = st.text_area("Medications (one per line)", "\n".join(patient["medications"]))
        allergies_text = st.text_area("Allergies (one per line)", "\n".join(patient["allergies"]))
        alerts_text = st.text_area("Alerts (one per line)", "\n".join(patient["alerts"]))
        visits_text = st.text_area(
            "Visit history (one per line: date | provider | note)",
            "\n".join(f"{v.get('date', '')} | {v.get('provider', '')} | {v.get('note', '')}" for v in patient["visits"]),
        )

        col_save, col_cancel = st.columns(2)
        save = col_save.form_submit_button("💾 Save", use_container_width=True)
        cancel = col_cancel.form_submit_button("Cancel", use_container_width=True)

    if cancel:
        st.session_state[edit_key] = False
        st.rerun()
    if save:
        repository.upsert_patient(
            {
                "id": patient["id"],
                "name": name.strip(),
                "age": int(age),
                "sex": sex.strip(),
                "summary": summary.strip(),
                "diagnoses": _parse_diagnoses(diagnoses_text),
                "medications": _parse_lines(medications_text),
                "allergies": _parse_lines(allergies_text),
                "alerts": _parse_lines(alerts_text),
                "visits": _parse_visits(visits_text),
            }
        )
        st.session_state[edit_key] = False
        st.success(f"Saved changes to {name.strip()}.")
        st.rerun()


def render_patient_search() -> None:
    """Look up a patient by name; expand to view, then edit the record."""
    query = st.text_input(
        "🔍 Search patients by name",
        key="patient_search_query",
        placeholder="e.g. Robert",
    )
    if not query:
        st.caption("Type a patient's name to search.")
        return

    matches = [p for p in repository.list_patients() if query.lower() in p["name"].lower()]
    if not matches:
        st.caption("No matching patients.")
        return

    for p in matches:
        with st.expander(f"{p['name']} ({p['age']}, {p['sex']})"):
            edit_key = f"edit_{p['id']}"
            if st.session_state.get(edit_key):
                render_patient_editor(p, edit_key)
            else:
                render_patient(p)
                if st.button("✏️ Edit", key=f"edit_btn_{p['id']}"):
                    st.session_state[edit_key] = True
                    st.rerun()


with patient_tab:
    patients = repository.list_patients()
    if not patients:
        st.info("No patients found. Run `make seed` to load sample data.")
    else:
        labels = {f"{p['name']} ({p['age']}, {p['sex']})": p for p in patients}
        label = st.selectbox("Select a patient", list(labels.keys()))
        patient = labels[label]
        st.session_state["active_patient"] = patient

        render_disease_search()
        st.divider()

        main_col, appt_col = st.columns([3, 1])
        with main_col:
            render_patient(patient)
        with appt_col:
            render_appointment_module(patient)


with doctor_tab:
    doctors = repository.list_doctors()
    if not doctors:
        st.info("No doctors found. Run `make seed` to load sample data.")
    else:
        label = st.selectbox(
            "Select a doctor",
            doctors,
            format_func=lambda d: f"{d['name']} — {d['specialty']}",
        )
        st.divider()

        patient_col, medline_col = st.columns(2)
        with patient_col:
            st.markdown("#### 🔍 Patient search")
            render_patient_search()
        with medline_col:
            st.markdown("#### 🌐 Medline search")
            render_disease_search(key="doctor_disease_query")

        st.divider()
        st.subheader(f"{label['name']} — {label['specialty']} · Appointments")
        appts = repository.list_appointments(doctor_id=label["id"])
        if not appts:
            st.write("No appointments booked.")
        else:
            patient_names = {p["id"]: p["name"] for p in repository.list_patients()}
            for a in appts:
                st.markdown(
                    f"- **{a['start_ts']}** — {patient_names.get(a['patient_id'], a['patient_id'])} "
                    f"({a['reason'] or 'no reason given'}) · _{a['status']}_"
                )



_CHAT_SIZES = {
    "normal": {"width": "360px", "max_height": "70vh"},
    "large": {"width": "600px", "max_height": "88vh"},
}

_CHAT_CSS_TEMPLATE = """
<style>
/* Expanded chat panel, pinned bottom-right */
.st-key-chat_panel {
    position: fixed !important;
    bottom: 1.5rem !important;
    right: 1.5rem !important;
    left: auto !important;
    width: __WIDTH__ !important;
    max-height: __MAX_HEIGHT__;
    overflow-y: auto;
    background: var(--background-color, #ffffff);
    color: var(--text-color, #1f2937);
    border: 1px solid rgba(128, 128, 128, 0.3);
    border-radius: 14px;
    padding: 0.75rem 1rem 1rem;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
    z-index: 1000;
}
/* Collapsed floating bubble button */
.st-key-chat_bubble {
    position: fixed !important;
    bottom: 1.5rem !important;
    right: 1.5rem !important;
    left: auto !important;
    width: 60px !important;
    min-width: 60px !important;
    z-index: 1000;
}
.st-key-chat_bubble button {
    border-radius: 50%;
    width: 60px;
    height: 60px;
    font-size: 26px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}
</style>
"""


def _chat_css(size: str = "normal") -> str:
    dims = _CHAT_SIZES.get(size, _CHAT_SIZES["normal"])
    return (
        _CHAT_CSS_TEMPLATE
        .replace("__WIDTH__", dims["width"])
        .replace("__MAX_HEIGHT__", dims["max_height"])
    )


def _render_trace(trace: list[dict]) -> None:
    """Show the agent's planning/tool steps under a reply (memory trace)."""
    with st.expander(f"🧠 Agent trace ({len(trace)} steps)"):
        if not trace:
            st.caption("Answered directly — no tools called.")
        for step in trace:
            if step["kind"] == "tool_call":
                st.markdown(f"**🛠 Plan → call `{step['name']}`**")
                st.json(step["args"])
            else:
                st.markdown(f"**📋 Result from `{step['name']}`**")
                st.code(step["content"], language="text")


def render_chatbot() -> None:
    """Floating, minimizable health-assistant chat widget (bottom-right)."""
    st.session_state.setdefault("chat_open", False)
    st.session_state.setdefault("chat_messages", [])
    st.session_state.setdefault("chat_size", "normal")
    st.markdown(_chat_css(st.session_state.chat_size), unsafe_allow_html=True)

    if not st.session_state.chat_open:
        with st.container(key="chat_bubble"):
            if st.button("💬", key="chat_open_btn", help="Chat with the health assistant"):
                st.session_state.chat_open = True
                st.rerun()
        return

    with st.container(key="chat_panel"):
        header, resize, minimize = st.columns([4, 1, 1], vertical_alignment="center")
        header.markdown("**💬 Health Assistant**")
        is_large = st.session_state.chat_size == "large"
        if resize.button(
            "⤡" if is_large else "⤢",
            key="chat_size_btn",
            help="Shrink" if is_large else "Enlarge",
        ):
            st.session_state.chat_size = "normal" if is_large else "large"
            st.rerun()
        if minimize.button("—", key="chat_min_btn", help="Minimize"):
            st.session_state.chat_open = False
            st.rerun()

        for m in st.session_state.chat_messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                if m.get("trace"):
                    _render_trace(m["trace"])

        with st.form("chat_form", clear_on_submit=True):
            prompt = st.text_input(
                "Message",
                placeholder="Ask a health question…",
                label_visibility="collapsed",
            )
            sent = st.form_submit_button("Send", use_container_width=True)

        if sent and prompt.strip():
            st.session_state.chat_messages.append({"role": "user", "content": prompt.strip()})
            with st.spinner("Thinking…"):
                result = run_agent(
                    st.session_state.chat_messages,
                    patient=st.session_state.get("active_patient"),
                )
            st.session_state.chat_messages.append(
                {"role": "assistant", "content": result["reply"], "trace": result["trace"]}
            )
            st.rerun()


render_chatbot()
