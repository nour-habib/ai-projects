VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

.PHONY: help venv install seed rag ui eval clean

help:
	@echo "Available targets:"
	@echo "  make install    - create venv and install dependencies"
	@echo "  make seed       - initialize the SQLite DB and load sample data"
	@echo "  make rag        - build the clinic-docs FAISS index from the corpus"
	@echo "  make ui         - run the Streamlit dashboard"
	@echo "  make eval       - run the agent evaluations (functional + semantic)"
	@echo "  make clean      - remove the virtual environment"

venv:
	test -d $(VENV) || python3 -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

seed:
	$(PYTHON) -m backend.seed

rag:
	$(PYTHON) -m ai.agents.tools.rag.rag

ui:
	$(STREAMLIT) run ui/app.py

eval:
	$(PYTHON) -m ai.eval.run_eval

clean:
	rm -rf $(VENV)
