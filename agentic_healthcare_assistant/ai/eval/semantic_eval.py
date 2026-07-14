"""Semantic evaluation: grade the agent's free-text answers with an LLM judge.

Runs each dataset question through the LangGraph agent, then uses QAEvalChain
to grade the agent's answer against the reference answer (CORRECT/INCORRECT).
Covers the disease-search and clinic-FAQ modules.
"""

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_classic.evaluation.qa import QAEvalChain

from ai.agents.router import build_router
from ai.eval.dataset import QA_EXAMPLES


def _agent_answer(agent, query: str) -> str:
    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    return result["messages"][-1].content


def run_semantic_eval() -> dict:
    """Run the LLM-judged eval and return per-module + overall accuracy."""
    agent = build_router()
    predictions = [{"result": _agent_answer(agent, ex["query"])} for ex in QA_EXAMPLES]

    judge = ChatOpenAI(model="gpt-4o", temperature=0)
    graded = QAEvalChain.from_llm(judge).evaluate(QA_EXAMPLES, predictions)

    per_module: dict[str, dict] = {}
    details = []
    for ex, pred, grade in zip(QA_EXAMPLES, predictions, graded):
        verdict = grade.get("results", "").strip().upper()
        correct = verdict.startswith("CORRECT")
        bucket = per_module.setdefault(ex["module"], {"passed": 0, "total": 0})
        bucket["total"] += 1
        bucket["passed"] += int(correct)
        details.append(
            {
                "module": ex["module"],
                "query": ex["query"],
                "prediction": pred["result"],
                "verdict": verdict,
                "correct": correct,
            }
        )

    total = len(QA_EXAMPLES)
    passed = sum(d["correct"] for d in details)
    return {
        "overall_accuracy": passed / total if total else 0.0,
        "per_module": {
            m: round(v["passed"] / v["total"], 3) for m, v in per_module.items()
        },
        "details": details,
    }
