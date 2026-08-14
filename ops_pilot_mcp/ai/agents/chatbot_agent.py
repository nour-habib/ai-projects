
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from .mcp_client import get_openai_tools, client

load_dotenv()

class ChatbotAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"
    
    def chat(self, messages: list[dict]) -> dict:
        async with client: #opens the MCP connection for this turn
            tools = await get_openai_tools()
            
            response = await openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
            )

            choice = response.choices[0]
            if choice.message.tool_calls:
                tool_call = choice.message.tool_calls[0]
                args = json.loads(tool_call.function.arguments)

                if tool.call.function.name in ("update_ticket_status", "reassign_ticket"):
                    return {"type": "tool_confirmation", "tool_name": tool_call.function.name, "args": args}

                result = await call_mcp_tool(tool_call.function.name, args)
                messages.append(choice.message)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})

                follow_up = await openai_client.chat.completions.create(model=self.model, messages=messages)
                return {
                    "type": "message", "content": follow_up.choices[0].message.content
                }
            
            return {"type": "message", "content": choice.message.content}
        


