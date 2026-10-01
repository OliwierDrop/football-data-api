from app.utils.names import clean_team_name


def test_clean_team_name_strips_marker():
    assert clean_team_name("Słupczanka Słupca (k)") == "Słupczanka Słupca"
    assert clean_team_name("KKP Warszawa (k)") == "KKP Warszawa"
    assert clean_team_name("Wisła Płock") == "Wisła Płock"
    assert clean_team_name("  Medyk II Konin (K)  ") == "Medyk II Konin"
