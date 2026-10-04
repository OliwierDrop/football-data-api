# Herby klubów

Synchronizacja `/api/admin/sync` po meczach i tabeli sprawdza profile klubów
`/skarb.php?id_klub=...&id_sezon=...` i zapisuje znaleziony adres w `teams.logo_url`.
Nie pobiera pliku obrazu. Parser rozpoznaje obrazy w katalogach `logo`, `logos`,
`herb`, `herby` lub oznaczone jako herb w `alt`/`title`.

Każdy klub z identyfikatorem jest sprawdzany najwyżej raz dziennie (także gdy
nie znaleziono herbu). Błędy sieci będą ponawiane przy następnej synchronizacji.
Brak obrazu lub błąd nie usuwa istniejącego adresu ani nie cofa synchronizacji
meczów i tabeli. Błędy są zapisywane w osobnym przebiegu `logos`.

Opcję można wyłączyć przez `SCRAPE_TEAM_LOGOS=false` w `.env`.

Pola API:
- `/api/team`: `logo_url`
- `/api/standings`: `logo_url`
- `/api/matches`: `home_team_logo_url`, `away_team_logo_url`
- `/api/home`: te same pola w meczach i tabeli

Brak herbu jest reprezentowany jako `null`.

Rezerwy mogą korzystać z profilu pierwszej drużyny, jeśli własny profil nie
zawiera herbu. Przypisania są w `app/scraper/logo_sources.py`, według identyfikatora
rezerw: `20229` (Polonia II Środa Wielkopolska) korzysta z klubu `1474`, sezon `67`.
Własny herb rezerw ma pierwszeństwo. Nowe przypisanie przy pustym `logo_url`
jest sprawdzane przy następnej synchronizacji, także po niedawnym sprawdzeniu.
Kolejne rezerwy należy dopisać z potwierdzonym identyfikatorem pierwszej drużyny.

Stałe adresy obrazów znajdują się w `TEAM_LOGO_URL_FALLBACKS` w tym samym pliku.

Źródła dodatkowych fallbacków:

| Drużyna | ID | Strona z potwierdzonym obrazem |
| --- | --- | --- |
| Słupczanka Słupca | 23495 | [Profil FootyStats](https://footystats.org/clubs/kkp-slupczanka-slupca-women-1270646) |
| KU-AZS UW Warszawa | 14594 | [Oficjalna strona sekcji piłki nożnej kobiet](https://azs.uw.edu.pl/sekcje/akademickie/pilka-nozna-kobiet/) |
| LFA Szczecin | 22346 | [Oficjalna strona klubu](https://lfaszczecin.sportbm.com/) |
| TAF Toruń | 26922 | [Profil drużyny kobiecej na stronie Chemika](https://chemikbydgoszcz.pl/klub/taf-torun-k/) |
| MOSiR Lubartów | 22493 | [Oficjalna strona MOSiR](https://mosir.umlubartow.pl/) |

Adresy obrazów sprawdzono: odpowiedź HTTP 200 i typ `image/*`.
KU-AZS UW używa logo całego klubu z jego oficjalnej strony, a MOSiR logo ośrodka.

Legionistki II Warszawa (`26717`) mają przypisany herb Legii Ladies z kobiecyfutbol.pl.
Stały URL jest używany dopiero gdy parser nie znajdzie herbu na 90minut.pl
(ani na przypisanym profilu pierwszej drużyny, jeśli taki istnieje).
Obowiązuje dzienny odstęp sprawdzania. Błąd pobrania zachowuje poprzedni adres
i pozwala ponowić próbę przy następnej synchronizacji.

Po aktualizacji uruchom `alembic upgrade head` (entrypoint Dockera robi to
automatycznie), a następnie synchronizację. W Dockerze:

```sh
docker compose up -d --build
curl -X POST http://localhost:8000/api/admin/sync
```

Sprawdzono aktualne profile na 90minut.pl: Legia Warszawa udostępnia herb
w katalogu `/logo/dobazy/`, natomiast profil Słupczanki (`23495`, sezon `109`)
nie zawierał obrazu herbu podczas weryfikacji. W takim przypadku API zwróci `null`.
