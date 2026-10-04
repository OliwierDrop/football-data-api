"""Fallback crest URLs and reserve-team profile mappings."""

TEAM_LOGO_URL_FALLBACKS: dict[str, str] = {
    # Słupczanka Słupca — profil klubu w FootyStats
    "23495": "https://cdn.footystats.org/img/teams/poland-kkp-slupczanka-slupca-women.png",
    # KU-AZS UW Warszawa — oficjalna strona klubu
    "14594": "https://azscdn.stellis.one/imgsize-xxl/documents/9224429/0/AZS_UW_Logo_granat.pdf.png/fd543b80-0002-f212-d3f8-62a41ad34b0a?t=1730288048265&download=true",
    # LFA Szczecin — logo z nagłówka oficjalnej strony klubu
    "22346": "https://storage.sportbm.com/app/38266c9e415e1ad7556acc15d89bcb14_8d175672-319a-4af2-9b9e-b3971c322664.jpg",
    # TAF Toruń — profil drużyny kobiecej na stronie Chemika Bydgoszcz
    "26922": "https://chemikbydgoszcz.pl/wp-content/uploads/2022/08/taf-torun.png",
    # MOSiR Lubartów — oficjalna strona MOSiR
    "22493": "https://mosir.umlubartow.pl/wp-content/themes/mosir/img/logo.png",
    # Wisła Płock
    "25949": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Wisla_P%C5%82ock.png",
    # KKP Warszawa
    "27783": "https://kobiecyfutbol.pl/wp-content/uploads/2024/08/kkp_warszawa-removebg-preview.png",
    # Loczki Wyszków
    "18068": "https://uksmazovia.pl/wp-content/uploads/2022/03/logo_uks_loczki_wyszkow.jpg",
    # AKS SMS Łódź
    "25982": "https://akssmslodz.pl/wp-content/uploads/2023/08/cropped-logo_aks-pantera-bialetlo.png",
    # Legionistki II Warszawa (Legia Ladies)
    "26717": "https://kobiecyfutbol.pl/wp-content/uploads/2024/08/legia-ladies-herb.png",
}

TEAM_LOGO_FALLBACKS: dict[str, tuple[str, str]] = {
    # Polonia II Środa Wielkopolska -> Polonia Środa Wielkopolska
    "20229": ("1474", "67"),
}
