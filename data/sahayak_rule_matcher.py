"""
Conservative Sahayak eligibility pre-screen.
Install: pip install pandas
Run: python sahayak_rule_matcher.py profile.json eligibility_rules.csv

This engine is a prototype: it never declares an official entitlement.
It returns POTENTIAL_MATCH, NOT_MATCHED, NEED_MORE_INFORMATION or MANUAL_REVIEW.
"""
import csv, json, sys

def parse_value(v):
    try:
        return json.loads(v)
    except Exception:
        return v

def compare(actual, op, expected):
    if actual is None or actual == "":
        return None
    expected = parse_value(expected)
    try:
        if op == "EQ":
            return str(actual).strip().lower() == str(expected).strip().lower()
        if op == "GTE":
            return float(actual) >= float(expected)
        if op == "LTE":
            return float(actual) <= float(expected)
        if op == "BETWEEN":
            lo, hi = [float(x.strip()) for x in str(expected).split(",")]
            return lo <= float(actual) <= hi
        if op == "IN":
            choices = [x.strip().lower() for x in str(expected).split(",")]
            return str(actual).strip().lower() in choices
        raise ValueError(f"Unsupported operator: {op}")
    except (ValueError, TypeError):
        return False

def evaluate(profile, rules):
    by_scheme = {}
    for r in rules:
        by_scheme.setdefault(r["scheme_id"], []).append(r)
    output = []
    for scheme_id, scheme_rules in by_scheme.items():
        reasons, missing, manual, excluded = [], [], [], []
        for r in scheme_rules:
            if r["automation_status"].startswith("MANUAL_REVIEW") or r["automation_status"] in {
                "MERIT_LIST_LOOKUP_REQUIRED", "MANUAL_REVIEW_SENSITIVE_DOCUMENT"
            }:
                manual.append(r["condition_explanation"])
                continue
            actual = profile.get(r["field_name"])
            result = compare(actual, r["operator"], r["value"])
            if result is None:
                missing.append(r["field_name"])
            elif r["action"] == "EXCLUDE" and result:
                excluded.append(r["condition_explanation"])
            elif r["action"] == "REQUIRE" and not result:
                reasons.append(r["condition_explanation"])
        if excluded:
            status = "NOT_MATCHED"
            detail = excluded
        elif reasons:
            status = "NOT_MATCHED"
            detail = reasons
        elif manual:
            status = "MANUAL_REVIEW"
            detail = manual[:5]
        elif missing:
            status = "NEED_MORE_INFORMATION"
            detail = sorted(set(missing))
        else:
            status = "POTENTIAL_MATCH"
            detail = ["Encoded checks passed; official records and scheme authority must confirm."]
        output.append({"scheme_id": scheme_id, "status": status, "details": detail})
    return output

def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python sahayak_rule_matcher.py profile.json eligibility_rules.csv")
    with open(sys.argv[1], encoding="utf-8") as f:
        profile = json.load(f)
    with open(sys.argv[2], newline="", encoding="utf-8-sig") as f:
        rules = list(csv.DictReader(f))
    for item in evaluate(profile, rules):
        print(json.dumps(item, ensure_ascii=False))
if __name__ == "__main__":
    main()
