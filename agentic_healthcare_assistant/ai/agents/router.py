from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition

from ai.agents.tools.tools import tools
from ai.models.models import MessageState

from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are a friendly healthcare assistant in a medical task-automation app. "
        "Answer health questions clearly and concisely, and help with booking, "
        "searching, and cancelling appointments using your tools. You can share "
        "general disease information but must not provide a diagnosis. Always remind "
        "the user to consult a healthcare professional for medical advice."
    )
)

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: MessageState) -> dict:
    response = llm_with_tools.invoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": [response]}


tool_node = ToolNode(tools=tools)


def build_router():
    graph = StateGraph(MessageState)

    graph.add_node("chatbot", chatbot)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chatbot")
    graph.add_conditional_edges("chatbot", tools_condition)
    graph.add_edge("tools", "chatbot")

    return graph.compile()
