from ai.models.models import QueryType, Intent

CLASSIFIER_TEST_CASES = [
    # ── POSITIVE / PRAISE ──────────────────────────────────────────────
    ("Thank you for sorting out my net banking login so quickly!",   QueryType.POSITIVE, Intent.PRAISE),
    ("You guys are amazing, my card arrived earlier than expected.",  QueryType.POSITIVE, Intent.PRAISE),
    ("Great service as always, really appreciate the help.",          QueryType.POSITIVE, Intent.PRAISE),

    # ── NEGATIVE / COMPLAINT ───────────────────────────────────────────
    ("My debit card replacement still hasn't arrived.",               QueryType.NEGATIVE, Intent.COMPLAINT),
    ("I was charged twice for the same transaction, this is unacceptable.", QueryType.NEGATIVE, Intent.COMPLAINT),
    ("The mobile app keeps crashing every time I try to transfer money.",   QueryType.NEGATIVE, Intent.COMPLAINT),

    # ── QUERY / TICKET_STATUS (contains a 6-digit number) ──────────────
    ("Could you check the status of ticket 650932?",                  QueryType.QUERY, Intent.TICKET_STATUS),
    ("Any update on ticket #482915?",                                 QueryType.QUERY, Intent.TICKET_STATUS),
    ("What's happening with my complaint, reference 100042?",         QueryType.QUERY, Intent.TICKET_STATUS),

    # ── QUERY / GENERAL_QUESTION (RAG topics) ──────────────────────────
    ("What are your current mortgage rates?",                         QueryType.QUERY, Intent.GENERAL_QUESTION),
    ("Where is the nearest branch to downtown?",                      QueryType.QUERY, Intent.GENERAL_QUESTION),
    ("What time do you open on Saturdays?",                           QueryType.QUERY, Intent.GENERAL_QUESTION),
    ("How much is the overdraft fee?",                                QueryType.QUERY, Intent.GENERAL_QUESTION),
    ("Do you offer cashback on credit cards?",                        QueryType.QUERY, Intent.GENERAL_QUESTION),
    ("How do I open a student account?",                              QueryType.QUERY, Intent.GENERAL_QUESTION),

    # ── EDGE CASES (the ones that break naive rules) ───────────────────
    # complaint phrased as a question -> still NEGATIVE, not a QUERY
    ("Why hasn't my debit card arrived yet?",                         QueryType.NEGATIVE, Intent.COMPLAINT),
    # praise phrased as a question
    ("How are you all so helpful? Thanks again!",                     QueryType.POSITIVE, Intent.PRAISE),
    # neutral/general question with no sentiment
    ("Is there an ATM at the airport branch?",                        QueryType.QUERY, Intent.GENERAL_QUESTION),
    # ticket number embedded in a complaint -> judgement call (status vs vent)
    ("Ticket 650932 has been open for weeks and nobody has helped!",  QueryType.NEGATIVE, Intent.COMPLAINT),
]