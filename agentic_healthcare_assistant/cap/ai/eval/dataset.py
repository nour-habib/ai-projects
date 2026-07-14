"""Reference Q&A pairs for the semantic (LLM-judged) evaluation.

Each example has a `query` (what the user asks) and an `answer` (the ground
truth the agent's response is graded against). `module` groups examples so we
can report accuracy per capability.
"""

QA_EXAMPLES = [
    {
        "module": "clinic_faq",
        "query": "Where can I park at the clinic?",
        "answer": (
            "There is paid parking in the building's underground garage off Maple "
            "Avenue, and patients can get their ticket validated at reception for a "
            "reduced flat rate."
        ),
    },
    {
        "module": "clinic_faq",
        "query": "What are the clinic's opening hours?",
        "answer": "The clinic is open on weekdays during standard business hours.",
    },
    {
        "module": "clinic_faq",
        "query": "Do you accept insurance?",
        "answer": "Yes, the clinic accepts major insurance plans and bills them directly.",
    },
    {
        "module": "medline",
        "query": "What is type 2 diabetes?",
        "answer": (
            "Type 2 diabetes is a chronic condition where the body does not use "
            "insulin properly, causing high blood sugar. It is managed with diet, "
            "exercise, and medication."
        ),
    },
    {
        "module": "medline",
        "query": "What are common symptoms of asthma?",
        "answer": (
            "Asthma commonly causes wheezing, shortness of breath, chest tightness, "
            "and coughing, often worse at night or with triggers."
        ),
    },
]
