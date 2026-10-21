"""Run the evaluation set and save scored results plus rough token estimates."""
import csv
import json
from pathlib import Path
from app import answer_question

ROOT = Path(__file__).parent
TESTS = ROOT / "data" / "evaluation_set.json"
OUT_JSON = ROOT / "results" / "evaluation_results.json"
OUT_CSV = ROOT / "results" / "evaluation_results.csv"

def main():
    cases = json.loads(TESTS.read_text(encoding="utf-8"))
    results = []
    for case in cases:
        got = answer_question(case["question"])
        status_ok = got["status"] == case["expected_status"]
        terms = [t.lower() for t in case.get("must_contain", [])]
        content_ok = all(t in got["answer"].lower() for t in terms)
        passed = status_ok and content_ok
        results.append({
            "id": case["id"],
            "question": case["question"],
            "expected_status": case["expected_status"],
            "actual_status": got["status"],
            "status_ok": status_ok,
            "content_ok": content_ok,
            "passed": passed,
            "sources": got["sources"],
            "input_tokens_est": got["input_tokens_est"],
            "output_tokens_est": got["output_tokens_est"],
            "total_tokens_est": got["total_tokens_est"],
            "answer": got["answer"],
        })
    total = len(results)
    passed = sum(r["passed"] for r in results)
    summary = {
        "evaluation_cases": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate_percent": round(100 * passed / total, 2) if total else 0,
        "total_estimated_tokens": sum(r["total_tokens_est"] for r in results),
        "token_note": "Character-based rough estimate; this app uses no LLM API and has no billed token usage."
    }
    OUT_JSON.write_text(json.dumps({"summary": summary, "results": results}, indent=2), encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(json.dumps(summary, indent=2))
    print(f"Saved: {OUT_JSON.relative_to(ROOT)}")
    print(f"Saved: {OUT_CSV.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
