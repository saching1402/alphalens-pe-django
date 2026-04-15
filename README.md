# AlphaLens PE — Django + React

Production-grade PE Fund Manager Intelligence Platform.

**Stack:** React 18 · Django 5 · Django REST Framework · PostgreSQL 16 · Docker · Nginx

---

## Quick Start (Local with Docker)

```bash
cp .env.example .env
docker compose up --build
```

Then open http://localhost — the app is live.

- Frontend: http://localhost
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

---

## Local Dev (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env         # edit with your local DB settings
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173 and proxies `/api` to Django at port 8000.

---

## Deploy to Railway

### Step 1 — Backend service
1. New project → Deploy from GitHub repo
2. Set root directory: `/` (uses `railway.toml` at root)
3. Add environment variables:
   - `DATABASE_URL` — Railway PostgreSQL connection string
   - `SECRET_KEY` — random 50-char string
   - `ALLOWED_HOSTS` — your Railway domain
   - `CORS_ALLOWED_ORIGINS` — your frontend Railway URL
   - `DEBUG` — False

### Step 2 — PostgreSQL
1. New → PostgreSQL → attach to backend service
2. Railway auto-sets `DATABASE_URL`

### Step 3 — Frontend service
1. Add service → same GitHub repo
2. Set root directory: `frontend/`
3. Add build variable: `VITE_API_URL` = your backend Railway URL

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/managers/` | List all managers with metrics |
| POST | `/api/managers/` | Create manager |
| GET/PATCH/DELETE | `/api/managers/{id}/` | Manager detail |
| GET | `/api/funds/` | List funds |
| POST | `/api/funds/` | Create fund |
| GET/PATCH/DELETE | `/api/funds/{id}/` | Fund detail |
| GET | `/api/analytics/dashboard/` | KPI summary |
| GET | `/api/analytics/scatter/` | Scatter data |
| GET | `/api/analytics/top-managers/` | Top N managers |
| GET | `/api/analytics/quartile-dist/` | Quartile breakdown |
| GET/POST | `/api/workflows/` | Workflows |
| GET/PATCH/DELETE | `/api/workflows/{id}/` | Workflow detail |
| POST | `/api/workflows/{id}/comments/` | Add comment |
| POST | `/api/import/excel/` | Import Excel file |

---

## Project Structure

```
alphalens-pe-django/
├── backend/
│   ├── alphalens/         # Django project (settings, urls, wsgi)
│   ├── api/               # Django app (models, serializers, views, urls, importer)
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/         # Overview, Managers, Funds, Analytics, Workflows, Import
│   │   ├── lib/           # api.js, utils.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── railway.toml
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── railway.toml
├── .env.example
└── .gitignore
```
