import csv
import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[3] / "data"

def _read_csv(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / "csv" / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def _parse(value: str) -> Any:
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return value

def _compare(actual: Any, operator: str, expected: str) -> bool | None:
    if actual is None or actual == "":
        return None
    value = _parse(expected)
    try:
        if operator == "EQ":
            return str(actual).strip().lower() == str(value).strip().lower()
        if operator in {"GTE", "LTE"}:
            return float(actual) >= float(value) if operator == "GTE" else float(actual) <= float(value)
        if operator == "BETWEEN":
            low, high = (float(part.strip()) for part in str(value).split(","))
            return low <= float(actual) <= high
        if operator == "IN":
            return str(actual).strip().lower() in {part.strip().lower() for part in str(value).split(",")}
    except (TypeError, ValueError):
        return False
    raise ValueError(f"Unsupported rule operator: {operator}")

def schemes() -> list[dict[str, str]]:
    return _read_csv("schemes.csv")

def match(profile: dict[str, Any], scheme_ids: list[str] | None = None) -> list[dict[str, Any]]:
    rules = _read_csv("eligibility_rules.csv")
    docs = {row["scheme_id"]: row for row in _read_csv("scheme_documents.csv")}
    catalog = {row["scheme_id"]: row for row in schemes()}
    selected = scheme_ids or list(catalog)
    results = []
    for scheme_id in selected:
        scheme = catalog.get(scheme_id)
        if not scheme:
            continue
        reasons, missing, manual, excluded = [], set(), [], []
        for rule in [row for row in rules if row["scheme_id"] == scheme_id]:
            if rule["automation_status"].startswith("MANUAL_REVIEW") or rule["automation_status"] in {"MERIT_LIST_LOOKUP_REQUIRED", "MANUAL_REVIEW_SENSITIVE_DOCUMENT"}:
                manual.append(rule["condition_explanation"])
                continue
            result = _compare(profile.get(rule["field_name"]), rule["operator"], rule["value"])
            if result is None:
                missing.add(rule["field_name"])
            elif rule["action"] == "EXCLUDE" and result:
                excluded.append(rule["condition_explanation"])
            elif rule["action"] == "REQUIRE" and not result:
                reasons.append(rule["condition_explanation"])
        if excluded or reasons:
            status, details = "NOT_MATCHED", excluded + reasons
        elif manual:
            status, details = "MANUAL_REVIEW", manual[:5]
        elif missing:
            status, details = "NEED_MORE_INFORMATION", [f"Confirm {field}." for field in sorted(missing)]
        else:
            status, details = "POTENTIAL_MATCH", ["Encoded checks passed; verify official records and documents."]
        results.append({"scheme_id": scheme_id, "scheme_name": scheme["scheme_name"], "status": status, "reasons": details, "official_source_url": scheme["official_source_url"], "documents": [docs[scheme_id]["documents_or_evidence_to_prepare"]] if scheme_id in docs else []})
    return results

def ask_sources(question: str, scheme_id: str | None = None) -> dict[str, Any]:
    rows = _read_csv("official_sources.csv")
    terms = {term for term in question.lower().split() if len(term) > 3}
    known_ids = {row["scheme_id"] for row in schemes()}
    if scheme_id and scheme_id not in known_ids:
        ranked = []
    else:
        ranked = [row for row in rows if any(term in (row["source_title"] + " " + row["data_used"]).lower() for term in terms)]
    citations = [{"title": row["source_title"], "url": row["url"], "section": row["usage_note"]} for row in ranked[:3]]
    if not citations:
        return {"answer": "No supplied official source matched this question. Please ask for department verification instead of relying on an unsourced answer.", "citations": [], "source_found": False}
    return {"answer": "The supplied source records contain relevant guidance. Review the cited official page and confirm the current rule before acting.", "citations": citations, "source_found": True}