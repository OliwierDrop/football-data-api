# Football Data API

Niezależny backend do pobierania i udostępniania danych piłkarskich ze strony [90minut.pl](http://www.90minut.pl).

Docelowy klub: **Słupczanka Słupca** (`id_klub=23495`, sezon `109`).

## Architektura

```text
90minut.pl
    ↓
Python scraper (cykliczny)
    ↓
PostgreSQL
    ↓
FastAPI REST API
    ↓
Frontend (Astro + React + TypeScript)
```

FastAPI **nie scrapuje** 90minut.pl podczas requestów użytkownika. Scraper działa okresowo (domyślnie co 30 minut) i zapisuje dane do PostgreSQL. API czyta wyłącznie z bazy.

## Stack

- Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic
- httpx + BeautifulSoup4 / lxml
- PostgreSQL 16 (Docker)
- APScheduler (synchronizacja w tle)

## Szybki start

```bash
cp .env.example .env
docker compose up -d --build
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs  
Health: http://localhost:8000/health

Pierwsza automatyczna synchronizacja następuje 30 minut po starcie backendu, a kolejne co 30 minut. Odstęp można zmienić przez `SYNC_INTERVAL_MINUTES`.

Ręczny sync (dev/ops):

```bash
curl -X POST http://localhost:8000/api/admin/sync
```

## Endpointy

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/health` | Status API + DB + ostatni sync |
| GET | `/api/home` | Ostatni mecz, następny mecz, tabela |
| GET | `/api/matches` | Wszystkie mecze drużyny |
| GET | `/api/matches/upcoming` | Nadchodzące mecze |
| GET | `/api/matches/latest` | Rozegrane mecze |
| GET | `/api/matches/{id}` | Szczegóły meczu |
| GET | `/api/standings` | Tabela ligowa |
| GET | `/api/team` | Dane drużyny |
| GET | `/api/competitions` | Lista rozgrywek |
| POST | `/api/admin/sync` | Ręczna synchronizacja |

## Konfiguracja (.env)

```text
TEAM_EXTERNAL_ID=23495
TEAM_NAME=Słupczanka Słupca (k)
SEASON_EXTERNAL_ID=109
LEAGUE_PATH=/liga/1/liga14872.html
LEAGUE_NAME=II liga kobiet, grupa: północna
SYNC_INTERVAL_MINUTES=30
DATABASE_URL=postgresql+psycopg://football:...@postgres:5432/football
```

## Upsert / idempotencja

Mecze są identyfikowane przez `external_id` składany z daty, rozgrywek, kolejki i nazw drużyn. Ponowne uruchomienie scrapera aktualizuje istniejące rekordy (`UPDATE`), nie tworzy duplikatów.

Przy błędzie scrapera dane w PostgreSQL nie są usuwane – API nadal serwuje ostatni poprawny stan. Historia synchronizacji jest w tabeli `scrape_runs`.

## Migracje

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic revision --autogenerate -m "opis"
```

## Lokalny development (bez Dockera dla API)

Wymaga działającego PostgreSQL (np. `docker compose up -d postgres`):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# ustaw DATABASE_URL na localhost
alembic upgrade head
uvicorn app.main:app --reload
```

## Struktura

```text
app/
  api/          # endpointy FastAPI
  scraper/      # client + scrapery + parsery HTML
  models/       # SQLAlchemy
  schemas/      # Pydantic
  repositories/ # dostęp do DB
  services/     # sync + scheduler
  database/     # session, base
  config.py
```
