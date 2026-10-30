from app.services.profile_extractor import extract_profile_from_english

def test_extracts_age_farmer_and_bigha_without_conversion():
    p = extract_profile_from_english(
        "I am 52 years old. I am a farmer and I have 3 bigha land.", "Mandi"
    )
    assert p["age_years"] == 52
    assert p["occupation"] == "farmer"
    assert p["land_area"] == 3.0
    assert p["land_unit"] == "bigha"
    assert p["district"] == "Mandi"

def test_does_not_guess_missing_values():
    p = extract_profile_from_english("I need information about a government scheme.")
    assert p["age_years"] is None
    assert p["land_area"] is None
    assert p["occupation"] is None
