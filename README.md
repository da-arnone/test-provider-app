# provider-app

Provider management component with public/private question visibility.

## Stack

- Backend: Django + DRF (`backend/`)
- Frontend: React + webpack module federation (`frontend/`)

## URL surfaces

- Admin: `/admin/provider/` (full lifecycle)
- App: `/api/provider/` (provider-user/admin; sees public + private questions)
- Third: `/third/provider/` (consultation/view-only; only public questions)

Incoming subscription submissions for provider processing:

- `GET /api/provider/subscriptions/incoming/`
  - Lists submissions where `submitee_entity_type="provider"` and `submitee_entity_id`
    is one of the provider IDs authorized for the current token.
- `POST /api/provider/subscriptions/incoming/<id>/decision/`
  - Body: `{ "provider_id": <int>, "decision": "handled" | "rejected", "decision_note": "...", "decision_metadata": {...} }`
  - provider-app owns this lifecycle action and delegates the cross-component update
    to subscription-app `/third/subscription/requests/<id>/decision/`.

Third-party consultation endpoints:

- `GET /third/provider/providers/`
- `GET /third/provider/providers/<id>/`
- `GET /third/provider/providers/<id>/forms/`
- `GET /third/provider/providers/<id>/answers/`
- `GET /third/provider/forms/<id>/`

Private-data behavior for third-party consultation:

- Default: only public questions/answers are returned.
- If the caller token belongs to an `org-app` profile with a handled subscription
  to the target provider, these endpoints also return private questions/answers.
- Third-party responses expose `private_access_granted` so consumers can detect
  whether private data is expected in the payload.

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