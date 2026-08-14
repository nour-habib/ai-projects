import { useState, useRef, useEffect } from "react";
import { Send, Loader2, CheckCircle2, XCircle } from "lucide-react";

// ---------------------------------------------------------------------------
// Basic chat interface for OpsPilot.
//
// This is intentionally plain: message list + input + a tool-call
// confirmation card for write actions (update_ticket_status, reassign_ticket).
// Wire `sendMessage` up to your FastAPI /chat endpoint — the shape it expects
// is noted inline below.
// ---------------------------------------------------------------------------

const INK = "#1c1c1e";
const PAPER = "#fafaf8";
const LINE = "#e4e2dd";
const ACCENT = "#3a5a78"; // muted slate blue — calm, not decorative, fits an ops tool
const ACCENT_SOFT = "#eef2f5";

function MessageBubble({ role, content }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className="max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed"
        style={{
          background: isUser ? INK : "white",
          color: isUser ? PAPER : INK,
          border: isUser ? "none" : `1px solid ${LINE}`,
          borderBottomRightRadius: isUser ? 4 : 16,
          borderBottomLeftRadius: isUser ? 16 : 4,
        }}
      >
        {content}
      </div>
    </div>
  );
}

function ToolConfirmCard({ toolName, args, onConfirm, onCancel }) {
  const label =
    toolName === "update_ticket_status"
      ? `Change ticket #${args.ticket_id} status to "${args.new_status}"`
      : toolName === "reassign_ticket"
      ? `Reassign ticket #${args.ticket_id} to ${args.assignee_name ?? `user ${args.new_assignee_id}`}`
      : `Run ${toolName}`;

  return (
    <div className="flex justify-start mb-3">
      <div
        className="max-w-[75%] rounded-2xl px-4 py-3 text-sm"
        style={{ background: ACCENT_SOFT, border: `1px solid ${LINE}` }}
      >
        <p className="mb-3" style={{ color: INK }}>
          The assistant wants to: <span className="font-medium">{label}</span>
        </p>
        <div className="flex gap-2">
          <button
            onClick={onConfirm}
            className="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium text-white transition-opacity hover:opacity-90"
            style={{ background: ACCENT }}
          >
            <CheckCircle2 size={14} /> Confirm
          </button>
          <button
            onClick={onCancel}
            className="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-colors hover:bg-white"
            style={{ color: INK, border: `1px solid ${LINE}` }}
          >
            <XCircle size={14} /> Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start mb-3">
      <div
        className="flex items-center gap-1 rounded-2xl px-4 py-3"
        style={{ background: "white", border: `1px solid ${LINE}` }}
      >
        <Loader2 size={14} className="animate-spin" style={{ color: ACCENT }} />
        <span className="text-xs" style={{ color: "#8a8a8e" }}>
          thinking…
        </span>
      </div>
    </div>
  );
}

export default function ChatbotInterface() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hi — I can look up tickets, search the knowledge base, or update a ticket for you. What do you need?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [pendingTool, setPendingTool] = useState(null); // { toolName, args }
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading, pendingTool]);

  async function sendMessage(text) {
    if (!text.trim() || isLoading) return;

    const nextMessages = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setIsLoading(true);

    try {
      // Expected FastAPI contract, e.g.:
      //   POST /chat  { messages: [...] }
      //   -> { type: "message", content: "..." }
      //      | { type: "tool_confirmation", tool_name: "...", args: {...} }
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: nextMessages }),
      });
      const data = await res.json();

      if (data.type === "tool_confirmation") {
        setPendingTool({ toolName: data.tool_name, args: data.args });
      } else {
        setMessages((prev) => [...prev, { role: "assistant", content: data.content }]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong reaching the assistant. Try again?" },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  async function resolveTool(confirmed) {
    const tool = pendingTool;
    setPendingTool(null);
    setIsLoading(true);
    try {
      // POST /chat/confirm  { tool_name, args, confirmed }
      const res = await fetch("/api/chat/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tool_name: tool.toolName, args: tool.args, confirmed }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.content }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Couldn't complete that action. Try again?" },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div
      className="flex flex-col h-full rounded-2xl overflow-hidden"
      style={{ background: PAPER, border: `1px solid ${LINE}` }}
    >
      <div
        className="px-4 py-3 flex items-center gap-2"
        style={{ borderBottom: `1px solid ${LINE}`, background: "white" }}
      >
        <div className="w-2 h-2 rounded-full" style={{ background: ACCENT }} />
        <span className="text-sm font-medium" style={{ color: INK }}>
          OpsPilot Assistant
        </span>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4">
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} content={m.content} />
        ))}
        {pendingTool && (
          <ToolConfirmCard
            toolName={pendingTool.toolName}
            args={pendingTool.args}
            onConfirm={() => resolveTool(true)}
            onCancel={() => resolveTool(false)}
          />
        )}
        {isLoading && !pendingTool && <TypingIndicator />}
      </div>

      <div className="px-3 py-3 flex items-center gap-2" style={{ borderTop: `1px solid ${LINE}` }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage(input)}
          placeholder="Ask about a ticket, or search the knowledge base…"
          className="flex-1 rounded-full px-4 py-2 text-sm outline-none"
          style={{ border: `1px solid ${LINE}`, color: INK }}
          disabled={isLoading || !!pendingTool}
        />
        <button
          onClick={() => sendMessage(input)}
          disabled={isLoading || !!pendingTool || !input.trim()}
          className="flex items-center justify-center w-9 h-9 rounded-full text-white transition-opacity disabled:opacity-40"
          style={{ background: ACCENT }}
        >
          <Send size={15} />
        </button>
      </div>
    </div>
  );
}
