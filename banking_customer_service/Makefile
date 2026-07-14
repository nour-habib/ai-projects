VENV := .venv
PYTHON := $(VENV)/bin/python
STREAMLIT := $(VENV)/bin/streamlit
APP := ui/app.py

.PHONY: dev
dev:
	$(STREAMLIT) run $(APP)

.PHONY: rag
rag:
	$(PYTHON) -m ai.rag.rag
