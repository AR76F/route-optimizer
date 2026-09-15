"""Run the 15-question pilot benchmark."""
from __future__ import annotations
import argparse, json, re
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()

def source_matches(expected: str, actual: str) -> bool:
    expected, actual = normalize(expected), normalize(actual)
    return expected in actual or Path(actual).name == expected

def unique_sources(sources: list[str]) -> list[str]:
    """Deduplicate chunk sources while preserving retrieval order."""
    result = []
    seen = set()
    for source in sources:
        key = normalize(source.replace("\\", "/"))
        if key not in seen:
            seen.add(key)
            result.append(source)
    return result

def score_result(case: dict, run: dict) -> dict:
    expected = case.get("expected", {})
    answer = normalize(run.get("answer", ""))
    actual_sources = unique_sources(run.get("retrieved_sources", []))
    required_sources = unique_sources(expected.get("sources", []))
    allowed_sources = unique_sources(expected.get("allowed_sources", []))
    relevant_sources = unique_sources(required_sources + allowed_sources)
    required_terms = expected.get("required_terms", [])
    required_hits = sum(any(source_matches(s, a) for a in actual_sources) for s in required_sources)
    relevant_hits = sum(
        any(source_matches(expected_source, actual_source) for expected_source in relevant_sources)
        for actual_source in actual_sources
    )
    term_hits = sum(normalize(term) in answer for term in required_terms)
    precision = relevant_hits / len(actual_sources) if actual_sources else 0.0
    recall = required_hits / len(required_sources) if required_sources else 1.0
    coverage = term_hits / len(required_terms) if required_terms else 1.0
    forbidden_terms = expected.get("forbidden_terms", [])
    forbidden_hits = [term for term in forbidden_terms if normalize(term) in answer]
    return {
        "answer_score_0_to_5": round(5 * (0.7 * coverage + 0.3 * recall), 2),
        "required_terms_hit": term_hits, "required_terms_total": len(required_terms),
        "term_coverage": round(coverage, 3), "expected_sources_hit": required_hits,
        "expected_sources_total": len(required_sources),
        "unique_retrieved_sources": len(actual_sources),
        "retrieval_precision": round(precision, 3), "retrieval_recall": round(recall, 3),
        "required_source_recall": round(recall, 3),
        "contextual_precision": round(precision, 3),
        "allowed_sources_total": len(allowed_sources),
        "forbidden_terms_found": forbidden_hits,
        "forbidden_content_pass": not forbidden_hits,
    }

def average(items: list[dict], key: str) -> float:
    values = [x[key] for x in items if isinstance(x.get(key), (int, float))]
    return round(sum(values) / len(values), 3) if values else 0.0

def load_cases(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", type=Path, default=Path("evaluation/gold_standard.jsonl"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--models", nargs="+", default=["gpt-5.6-luna"])
    parser.add_argument("--resume", action="store_true", help="Resume an existing JSON report")
    parser.add_argument("--timeout", type=float, default=90.0, help="Seconds per model attempt")
    parser.add_argument("--retries", type=int, default=1, help="Retries after a failed attempt")
    args = parser.parse_args()
    from service_assistant import run_service_assistant
    cases = load_cases(args.suite)
    output = args.output or Path("evaluation/reports") / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    report = json.loads(output.read_text(encoding="utf-8")) if args.resume and output.exists() else {
        "run_id": datetime.now(timezone.utc).isoformat(), "suite": str(args.suite),
        "case_count": len(cases), "models": {},
    }
    for model in args.models:
        existing = report["models"].get(model, {}) if args.resume else {}
        results = existing.get("results", [])
        completed = {item.get("id") for item in results}
        for index, case in enumerate(cases, start=1):
            if case["id"] in completed:
                print(f"[{model}] {index}/{len(cases)} {case['id']} (skipped)", flush=True)
                continue
            session_id = f"eval-{report['run_id']}-{model}-{case['id']}-{index}"
            started = perf_counter()
            print(f"[{model}] {index}/{len(cases)} {case['id']} starting", flush=True)
            try:
                run = run_service_assistant(
                    case["question"],
                    session_id=session_id,
                    model=model,
                    timeout_seconds=args.timeout,
                    max_retries=args.retries,
                )
                scoring = score_result(case, run)
                item = {**case, "run": run, "scores": scoring, "error": None}
            except Exception as exc:
                item = {**case, "run": {"model": model, "session_id": session_id},
                        "scores": {"answer_score_0_to_5": 0.0},
                        "error": f"{type(exc).__name__}: {exc}"}
            results.append(item)
            print(f"[{model}] {index}/{len(cases)} {case['id']} ({round(perf_counter()-started, 1)}s)", flush=True)
            report["models"][model] = {"summary": {}, "results": results}
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        valid = [item["scores"] for item in results]
        report["models"][model] = {"summary": {
            "overall_score_percent": round(average(valid, "answer_score_0_to_5") * 20, 2),
            "average_answer_score_0_to_5": average(valid, "answer_score_0_to_5"),
            "retrieval_precision": average(valid, "retrieval_precision"),
            "retrieval_recall": average(valid, "retrieval_recall"),
            "contextual_precision": average(valid, "contextual_precision"),
            "required_source_recall": average(valid, "required_source_recall"),
            "term_coverage": average(valid, "term_coverage"),
            "forbidden_content_pass_rate": round(
                sum(item.get("forbidden_content_pass", False) for item in valid) / len(valid), 3
            ) if valid else 0.0,
            "average_latency_seconds": average([item.get("run", {}) for item in results], "latency_seconds"),
            "failed_cases": sum(item.get("error") is not None for item in results),
        }, "results": results}
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({m: d["summary"] for m, d in report["models"].items()}, indent=2))
    print(f"Report written to {output}")

if __name__ == "__main__":
    main()
