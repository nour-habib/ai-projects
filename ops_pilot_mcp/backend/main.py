from fastapi import fastapi


app = FastAPI(
    title="Ops Pilot",
    description="MCP powered internal support assistant",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:8100"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/chat")
def chat(message: str):
    from ai.agents.chatbot_agent import ChatbotAgent
    agent = ChatbotAgent()
    return agent.chat(message)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
