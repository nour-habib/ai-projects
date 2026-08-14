<h2>Banking Customer Service App</h2>

<b>Stack</b>: Streamlit, sqlite3, OpenAI, Pydantic, Pytest

<b>Features</b>: Chatbot (create, delete tickets, answer questions about location/services/hours/banking related info, write to sqlite3), RAG system for bank information, services, etc


<h2>Agentic Healthcare Assistant App</h2>

<b>Stack</b>: Streamlit, sqlite3, LangGraph, Pydantic, FAISS

<b>Features</b>: Chatbot (create, delete, edit appointments, can write to sqlite3 RAG system), search bar health related terms making API call to Medline


<h2>OpsPilot — Support Ops Assistant</h2> 

<b>Stack</b>: FastAPI, React, PostgreSQL, OpenAI, FastMCP 

<b>Features</b>: Chatbot that searches and summarizes support tickets, searches a knowledge base, updates ticket status and reassigns tickets (write actions gated behind a human confirmation step), all routed through an MCP server exposing the underlying tools; ticket dashboard for browsing tickets directly
