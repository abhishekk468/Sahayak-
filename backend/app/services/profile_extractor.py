import re
from typing import Any

def extract_profile_from_english(text: str, fallback_district: str | None = None) -> dict[str, Any]:
    """Conservative demo extractor. Missing fields remain null; no guesses."""
    profile: dict[str, Any] = {
        "age_years": None, "district": fallback_district,
        "state": "Himachal Pradesh" if any(
            x in text.lower() for x in ["himachal", "mandi", "kangra"]
        ) else None,
        "occupation": None, "land_area": None, "land_unit": None,
        "annual_income_inr": None, "preferred_language": None,
        "intent": "find_schemes", "field_evidence": {}
    }
    age = re.search(r"\b(?:age|aged|i am)\s*(\d{1,3})\s*(?:years?\s*old)?", text, re.I)
    if age:
        profile["age_years"] = int(age.group(1))
        profile["field_evidence"]["age_years"] = {
            "value": age.group(1), "confidence": 0.75, "evidence_text": age.group(0)
        }
    land = re.search(r"\b(\d+(?:\.\d+)?)\s*(bigha|hectare|hectares|acre|acres)\b", text, re.I)
    if land:
        profile["land_area"] = float(land.group(1))
        unit = land.group(2).lower()
        profile["land_unit"] = "bigha" if unit == "bigha" else unit.rstrip("s")
        profile["field_evidence"]["land_area"] = {
            "value": land.group(0), "confidence": 0.8, "evidence_text": land.group(0)
        }
    if re.search(r"\b(farmer|farming|agriculture)\b", text, re.I):
        profile["occupation"] = "farmer"
        profile["field_evidence"]["occupation"] = {
            "value": "farmer", "confidence": 0.7, "evidence_text": "farmer/farming"
        }
    if re.search(r"\b(student|scholarship|college|school)\b", text, re.I):
        profile["intent"] = "student_scholarship"
    return profile
