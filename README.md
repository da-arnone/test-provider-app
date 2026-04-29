# provider-app

Provider management component with public/private question visibility.

## Stack

- Backend: Django + DRF (`backend/`)
- Frontend: React + webpack module federation (`frontend/`)

## URL surfaces

- Admin: `/admin/provider/` (full lifecycle)
- App: `/api/provider/` (provider-user/admin; sees public + private questions)
- Third: `/third/provider/` (consultation/view-only; only public questions)

Third-party consultation endpoints:

- `GET /third/provider/providers/`
- `GET /third/provider/providers/<id>/`
- `GET /third/provider/providers/<id>/forms/`
- `GET /third/provider/providers/<id>/answers/`
- `GET /third/provider/forms/<id>/`

## Run backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python manage.py migrate
python manage.py loaddata provider_app/fixtures/seed.json
python manage.py runserver 8002
```

## Run frontend

```bash
cd frontend
npm install
npm start
```

## Run with Docker compose

The repository now follows the same philosophy as `test-org-app`:

- root `docker-compose.yml` for backend + frontend local orchestration
- `docker/Dockerfile` for standalone backend container build
- `.env` for local port and integration values

```bash
docker compose up --build
```

Standalone backend-only compose is also available:

```bash
docker compose -f docker/docker-compose.yml up --build
```