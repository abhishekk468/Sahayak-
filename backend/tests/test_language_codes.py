from app.services.indictrans2_service import SUPPORTED_CODES

def test_hindi_and_english_codes_exist():
    assert "hin_Deva" in SUPPORTED_CODES
    assert "eng_Latn" in SUPPORTED_CODES
