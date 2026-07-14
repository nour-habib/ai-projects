"""Banking Customer Support — Streamlit dashboard.

Self-contained demo UI with dummy data so it runs without the DB/repository
being finished. Swap the DUMMY_* lookups for `backend.repository` calls later.
"""

import sys
from pathlib import Path

# Ensure the project root is importable (ai.*, ui.*) when Streamlit runs this
# script from inside ui/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from ui.services.service import process_query
from backend.db import init_db


@st.cache_resource
def _ensure_db():
    """Create tables once per app session (idempotent — CREATE TABLE IF NOT EXISTS)."""
    init_db()


_ensure_db()

# --------------------------------------------------------------------------- #
# Dummy data (stand-ins for backend.repository.* until the DB is wired up)
# --------------------------------------------------------------------------- #
DUMMY_CUSTOMERS = {
    1: {"id": 1, "name": "Jane Doe",    "address": "123 Main St, Springfield", "dob": "1990-04-12"},
    2: {"id": 2, "name": "Carlos Ruiz", "address": "88 Elm Ave, Riverside",     "dob": "1985-11-30"},
    3: {"id": 3, "name": "Aisha Khan",  "address": "5 Oak Court, Lakeview",      "dob": "1998-07-03"},
}

DUMMY_ACCOUNTS = {
    1: [
        {"id": 101, "account_type": "Checking", "balance": 4_250.75,  "opened_at": "2018-03-01"},
        {"id": 102, "account_type": "Savings",  "balance": 18_900.00, "opened_at": "2019-06-15"},
    ],
    2: [
        {"id": 201, "account_type": "Checking", "balance": 1_120.40, "opened_at": "2020-01-22"},
        {"id": 202, "account_type": "Credit",   "balance": -640.10,  "opened_at": "2021-09-09"},
    ],
    3: [
        {"id": 301, "account_type": "Savings",  "balance": 7_530.00, "opened_at": "2022-05-30"},
    ],
}

# status in {Unresolved, In Progress} -> active;  {Resolved, Closed} -> past
DUMMY_TICKETS = {
    1: [
        {"id": 784521, "subject": "Debit card replacement not received", "status": "Unresolved",  "created_at": "2026-06-20"},
        {"id": 650932, "subject": "Net banking login issue",             "status": "Resolved",    "created_at": "2026-05-11"},
    ],
    2: [
        {"id": 410233, "subject": "Disputed transaction",                "status": "In Progress", "created_at": "2026-06-18"},
        {"id": 222194, "subject": "Statement request",                   "status": "Closed",      "created_at": "2026-03-02"},
    ],
    3: [
        {"id": 905017, "subject": "Mobile app crash on transfer",        "status": "Resolved",    "created_at": "2026-04-27"},
    ],
}

ACTIVE_STATUSES = {"Unresolved", "In Progress"}


# --------------------------------------------------------------------------- #
# Page config + a little CSS to pin the chatbot to the bottom-right
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="Banking Support", page_icon="🏦", layout="wide")

st.markdown(
    """
    <style>
    /* Float the chatbot popover in the bottom-right corner */
    div[data-testid="stPopover"] {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: auto;
        z-index: 9999;
    }
    /* Make the trigger a round floating action button */
    div[data-testid="stPopover"] > div > button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        padding: 0;
        font-size: 1.6rem;
        line-height: 60px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- #
# Sidebar — retractable menu (Streamlit sidebars collapse via the » / « arrow)
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.title("🏦 Banking Support")
    page = st.radio(
        "Menu",
        ["Dashboard", "Tickets", "Logs", "Settings"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Applied GenAI Capstone")


# --------------------------------------------------------------------------- #
# Customer selector (3 dummy customers) — shortened, above the search bar
# --------------------------------------------------------------------------- #
sel_col, _ = st.columns([1, 3])
with sel_col:
    selected_id = st.selectbox(
        "Customer",
        options=list(DUMMY_CUSTOMERS.keys()),
        format_func=lambda cid: DUMMY_CUSTOMERS[cid]["name"],
    )


# --------------------------------------------------------------------------- #
# Top bar — search
# --------------------------------------------------------------------------- #
st.text_input("Search", placeholder="🔍 Search customers, tickets, accounts…",
              label_visibility="collapsed")
st.divider()

customer = DUMMY_CUSTOMERS[selected_id]

st.subheader(f"👤 {customer['name']}")
meta = st.columns(3)
meta[0].metric("Customer ID", customer["id"])
meta[1].caption(f"**Address**\n\n{customer['address']}")
meta[2].caption(f"**Date of birth**\n\n{customer['dob']}")
st.divider()


# --------------------------------------------------------------------------- #
# Two containers side by side: Accounts | Tickets
# --------------------------------------------------------------------------- #
left, right = st.columns(2)

with left:
    with st.container(border=True):
        st.markdown("### 💳 Accounts")
        accounts = DUMMY_ACCOUNTS.get(selected_id, [])
        if not accounts:
            st.info("No accounts on file.")
        for acc in accounts:
            with st.container(border=True):
                top = st.columns([2, 1])
                top[0].markdown(f"**{acc['account_type']}**  \n`#{acc['id']}`")
                top[1].metric("Balance", f"${acc['balance']:,.2f}")
                st.caption(f"Opened {acc['opened_at']}")

with right:
    with st.container(border=True):
        st.markdown("### 🎫 Tickets")
        tickets = DUMMY_TICKETS.get(selected_id, [])
        active = [t for t in tickets if t["status"] in ACTIVE_STATUSES]
        past = [t for t in tickets if t["status"] not in ACTIVE_STATUSES]

        st.markdown("**Active**")
        if not active:
            st.success("No active tickets 🎉")
        for t in active:
            with st.container(border=True):
                st.markdown(f"**#{t['id']}** — {t['subject']}")
                st.caption(f"Status: `{t['status']}` · Opened {t['created_at']}")

        st.markdown("**Past**")
        if not past:
            st.caption("No past tickets.")
        for t in past:
            with st.container(border=True):
                st.markdown(f"**#{t['id']}** — {t['subject']}")
                st.caption(f"Status: `{t['status']}` · Opened {t['created_at']}")


# --------------------------------------------------------------------------- #
# Chatbot — bottom-right floating window (via the pinned popover above)
# --------------------------------------------------------------------------- #
if "chat" not in st.session_state:
    st.session_state.chat = [
        {"role": "assistant", "text": "Hi! How can I help with your banking support today?"}
    ]

with st.popover("💬", use_container_width=False):
    st.markdown("**Support Assistant**")
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.write(msg["text"])

    with st.form("chat_form", clear_on_submit=True):
        user_msg = st.text_input("Message", label_visibility="collapsed",
                                 placeholder="Type a message…")
        sent = st.form_submit_button("Send")

    if sent and user_msg:
        st.session_state.chat.append({"role": "user", "text": user_msg})
        # Send the chatbot input to the service layer -> orchestrator.
        with st.spinner("Waiting for a response…"):
            reply = process_query(user_msg)
        st.session_state.chat.append({"role": "assistant", "text": reply})
        st.rerun()
