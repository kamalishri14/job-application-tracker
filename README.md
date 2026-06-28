# Job Trail — Job Application Tracker

A full-stack web app to track job applications end to end: log every
application, move it through stages (Applied → Interview → Offer / Rejected),
and see your conversion funnel at a glance.

You can explore and interact with the live deployment of the application here:
[Job Trail on Render](https://job-trail.onrender.com)

Built with Python (Flask) on the backend and server-rendered HTML/CSS with
vanilla JavaScript on the frontend — no frontend framework, no build step.

## Features

- Add, edit, and delete job applications (company, role, location, link, notes)
- Filter by status, search by company/role/location
- Inline status updates (dropdown on the board updates instantly via `fetch`,
  no page reload)
- Funnel page: interview rate, offer rate, stage breakdown, and a monthly
  applications trend chart (Chart.js)
- Flash messages for create/update/delete actions
- Responsive layout, keyboard-accessible forms

## Tech stack

| Layer      | Tools                                  |
|------------|-----------------------------------------|
| Backend    | Python 3, Flask, Flask-SQLAlchemy       |
| Database   | SQLite (dev) / PostgreSQL (production)  |
| Frontend   | Jinja2 templates, HTML, CSS, vanilla JS |
| Charts     | Chart.js (CDN, no build step)           |
| Deployment | Gunicorn + Render / Railway / Heroku    |

## Project structure

```
job-tracker/
├── app.py                 # Flask app factory + all routes
├── models.py               # SQLAlchemy model (Application)
├── seed.py                  # Optional script to load sample data
├── requirements.txt
├── Procfile                 # For Render/Heroku
├── .gitignore
├── templates/
│   ├── base.html
│   ├── dashboard.html       # Main board: list + filters + search
│   ├── form.html            # Shared add/edit form
│   ├── stats.html           # Funnel + trend chart
│   └── 404.html
└── static/
    ├── css/style.css
    └── js/app.js             # Inline status update logic (fetch API)
```

## Running locally

```bash
# 1. Clone and enter the project
git clone https://github.com/<your-username>/job-trail.git
cd job-trail

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```



### Optional: load sample data

```bash
python seed.py
```

This adds a handful of realistic sample applications so the board and funnel
page aren't empty when you first open them.

## Deploying

### Render (recommended — free tier, simplest)

1. Push this project to a GitHub repository.
2. On [render.com](https://render.com), create a **New Web Service** and
   connect your repo.
3. Render auto-detects Python. Set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
4. Add a free **PostgreSQL** instance on Render (optional but recommended for
   persistence — SQLite on Render's free tier resets on redeploy). Copy its
   **Internal Database URL** into your web service's environment variables as
   `DATABASE_URL`.
5. Deploy. Render gives you a live URL like `https://job-trail.onrender.com`.

### Railway / Heroku

Same idea: push to GitHub, connect the repo, set `DATABASE_URL` if using
Postgres, and the included `Procfile` (`web: gunicorn app:app`) handles the
start command.

### Environment variables

| Variable       | Required | Description                                  |
|-----------------|----------|-----------------------------------------------|
| `SECRET_KEY`    | Recommended | Flask session secret. Set a random string in production. |
| `DATABASE_URL`  | Optional | Postgres connection string. Falls back to local SQLite if not set. |
| `PORT`          | Set by host | Used by Render/Heroku automatically. |

## Why this project

Most "to-do app" portfolio projects look the same. This one is a genuine
day-to-day tool — built and used while actually job hunting — that
demonstrates:

- CRUD with a real-world data model (status workflow, not just text fields)
- Server-side filtering and search with SQLAlchemy
- A lightweight REST-style JSON endpoint consumed by vanilla JS (`fetch`)
- Basic data aggregation/analytics (funnel %, monthly trends) without needing
  a separate analytics stack

## License

MIT — free to use, modify, and deploy.
