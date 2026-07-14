# Agentic Healthcare Assistant

A virtual medical assistant: a LangGraph + OpenAI agent behind a Streamlit UI,
with SQLite for patient/appointment data, MedlinePlus for disease lookups, and a
FAISS RAG index over the clinic's documentation.

## Setup

Run these once, in order, from the project root.

```bash
make install   # create the venv and install dependencies
make seed      # initialize the SQLite DB and load sample data
make rag       # build the clinic-docs FAISS index from the corpus
make ui        # run the Streamlit dashboard
```

### Environment

Create a `.env` file in the project root with your OpenAI key:

```
OPENAI_API_KEY=sk-...
```

`make rag` and the chat assistant both call the OpenAI API, so the key must be
set before running them.

## Notes

- **`make rag` is required before `make ui`.** The FAISS index is a regenerated
  build artifact (gitignored), not committed. Without it the retriever fails to
  load and the app won't start.
- **Rebuild the index when the corpus changes.** After editing any file in
  `ai/agents/tools/rag/corpus/`, rerun `make rag` to regenerate the index.
- `make clean` removes the virtual environment.
