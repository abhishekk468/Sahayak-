from app.services.scheme_service import ask_sources, match


def test_sunita_does_not_match_pm_kisan_maandhan_by_age():
    results = match({"age_years": 52, "occupation": "farmer"}, ["PM_KMY", "PM_KISAN"])
    by_id = {result["scheme_id"]: result for result in results}
    assert by_id["PM_KMY"]["status"] == "NOT_MATCHED"
    assert by_id["PM_KISAN"]["status"] == "MANUAL_REVIEW"
    assert by_id["PM_KISAN"]["official_source_url"] == "https://pmkisan.gov.in/"


def test_student_with_missing_details_needs_more_information():
    results = match({"occupation": "student"}, ["HP_MVKY"])
    assert results[0]["status"] == "NEED_MORE_INFORMATION"
    assert "class_level" in " ".join(results[0]["reasons"])


def test_rag_returns_citations_and_safe_no_source_fallback():
    sourced = ask_sources("What is the PM-KISAN landholding verification?", "PM_KISAN")
    assert sourced["source_found"] is True
    assert sourced["citations"][0]["url"] == "https://pmkisan.gov.in/"

    missing = ask_sources("What is an unrelated unsourced question?", "UNKNOWN")
    assert missing == {
        "answer": "No supplied official source matched this question. Please ask for department verification instead of relying on an unsourced answer.",
        "citations": [],
        "source_found": False,
    }