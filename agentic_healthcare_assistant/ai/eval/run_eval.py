"""Entry point: run both evaluations, print a report, and log results to JSON.

    python -m ai.eval.run_eval                # run both
    python -m ai.eval.run_eval --functional   # appointment checks only (no API cost)
    python -m ai.eval.run_eval --semantic     # LLM-judged answers only
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from ai.eval.functional_eval import run_functional_eval
from ai.eval.semantic_eval import run_semantic_eval

load_dotenv()

RESULTS_DIR = Path(__file__).parent / "results"


def _print_report(report: dict) -> None:
    print("\n=== Evaluation Report ===")

    func = report.get("functional")
    if func:
        print(f"\n[appointments]  success rate: {func['success_rate']:.0%} "
              f"({func['passed']}/{func['total']})")
        for r in func["details"]:
            mark = "PASS" if r["passed"] else "FAIL"
            note = f" — {r['note']}" if r["note"] else ""
            print(f"  [{mark}] {r['check']}{note}")

    sem = report.get("semantic")
    if sem:
        print(f"\n[semantic]  overall accuracy: {sem['overall_accuracy']:.0%}")
        for module, acc in sem["per_module"].items():
            print(f"  {module}: {acc:.0%}")
        for d in sem["details"]:
            mark = "PASS" if d["correct"] else "FAIL"
            print(f"  [{mark}] ({d['module']}) {d['query']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run agent evaluations.")
    parser.add_argument("--functional", action="store_true", help="appointment checks only")
    parser.add_argument("--semantic", action="store_true", help="LLM-judged answers only")
    args = parser.parse_args()

    run_both = not (args.functional or args.semantic)
    report: dict = {"timestamp": datetime.now().isoformat()}

    if args.functional or run_both:
        report["functional"] = run_functional_eval()
    if args.semantic or run_both:
        report["semantic"] = run_semantic_eval()

    _print_report(report)

    RESULTS_DIR.mkdir(exist_ok=True)
    out = RESULTS_DIR / f"eval_{datetime.now():%Y%m%d_%H%M%S}.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nLogged results to {out}")


if __name__ == "__main__":
    main()
