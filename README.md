# KPITB Hackathon Platform

A full-stack event management platform designed for province-wide hackathons in Khyber Pakhtunkhwa. It supports the complete journey from participant onboarding and individual event enrollment to team formation, project submission, judging, and organizer administration.

> This repository is a hackathon platform prototype. Review branding, policies, event content, and production security settings before an official deployment.

## What the platform supports

### Participants

- Create an account and maintain a reusable participant profile
- Browse hackathons, tracks, timelines, rules, prizes, and official problem statements
- Enroll individually in an event before joining a team
- Share role, experience level, attendance mode, team preference, motivation, and problem interest
- Create a team as its lead or join through an invitation/code
- Manage a roster of up to the limit configured for each hackathon
- Select an official problem statement and lock the final roster
- Submit a proposal, repository/demo links, attachments, pitch deck, and short recorded introduction
- Contact organizers through project inquiries and follow notifications

### Organizers

- Create and manage hackathons and their registration windows
- Publish official challenges, rules, prizes, tracks, and judging criteria
- Review participant enrollments, profiles, teams, and final registrations
- Monitor proposals and respond to participant inquiries
- Manage data through a protected organizer dashboard and Django Admin

### Judges

- View assigned hackathons and projects
- Score projects against event-specific weighted criteria
- Save comments and review aggregate results

## Registration journey

1. **Account and profile** — the participant provides contact, district, institution, education, and skills information.
2. **Individual event enrollment** — every team member enrolls in the selected hackathon and accepts its rules.
3. **Team formation** — a participant creates a team as lead or joins an existing team.
4. **Roster confirmation** — the lead selects the challenge and locks the team roster.
5. **Project submission** — the team submits its working prototype, proposal, short video, pitch deck, and supporting links.

Keeping event enrollment separate from project submission makes registration faster and lets participants form teams before committing to a final solution.

## Technology stack

| Layer | Technology |
| --- | --- |
| Frontend | React 18, TypeScript, Vite, React Router, Tailwind CSS, Framer Motion |
| Backend | Django 5.1, Django REST Framework |
| Authentication | JWT access/refresh tokens with Simple JWT |
| Database | SQLite for local development; PostgreSQL for deployment |
| File storage | Local Django storage; optional Azure Blob Storage |
| Testing | Django test suite, Vitest, React Testing Library, ESLint |
| Deployment | Docker Compose, Gunicorn |

## Project structure

```text
.
|-- backend/
|   |-- accounts/       # Authentication and participant profiles
|   |-- hackathons/     # Events, problems, criteria, and enrollments
|   |-- teams/          # Team creation, invitations, and roster controls
|   |-- projects/       # Proposals, attachments, and inquiries
|   |-- judging/        # Judge assignments and scoring
|   |-- notifications/  # Participant notifications
|   `-- kpitb_hackathon/# Django settings and root URLs
|-- frontend/
|   `-- src/
|       |-- components/ # Shared UI and application layout
|       |-- hooks/      # API and state hooks
|       `-- pages/      # Public, participant, judge, and admin pages
|-- docker-compose.yml
`-- DEPLOYMENT.md
```

## Local setup

### Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- Git

### 1. Backend

From the repository root on Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

For the simplest local setup, open `backend/.env`, leave `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` empty, and keep `DEBUG=True`. Django will use SQLite.

Prepare and run the API:

```powershell
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/v1/` and Django Admin at `http://127.0.0.1:8000/admin/`.

Create your own organizer account when needed:

```powershell
python manage.py createsuperuser
```

### 2. Frontend

Open a second terminal from the repository root:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://127.0.0.1:5173/`.

### Demo accounts

Running `python manage.py seed_data` creates local-only demonstration accounts:

| Role | Email | Password |
| --- | --- | --- |
| Participant | `participant.demo@kpitb.test` | `DemoPass!123` |
| Judge | `judge.demo@kpitb.test` | `DemoPass!123` |

These accounts are intended only for local development. The seed command does not create a superuser.

## Docker setup

Docker Compose starts Django and PostgreSQL:

```powershell
Copy-Item backend/.env.example backend/.env
docker compose up --build
```

In another terminal:

```powershell
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py seed_data
```

The frontend remains a separate Vite application. For deployment, build it with `npm run build` and set `VITE_API_BASE_URL` to the public API URL.

## Quality checks

Backend:

```powershell
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Frontend:

```powershell
cd frontend
npm run typecheck
npm run lint
npm run test
npm run build
```

## Main API groups

- `/api/v1/accounts/` — registration, login, current user, verification, and password recovery
- `/api/v1/hackathons/` — events, challenges, criteria, individual enrollments, and team registration
- `/api/v1/teams/` — teams, invitations, membership, and roster controls
- `/api/v1/projects/` — project proposals, attachments, and organizer inquiries
- `/api/v1/judging/` — assignments, scores, and aggregate results
- `/api/v1/notifications/` — participant notifications

Browsable API endpoints and Django Admin permissions depend on the signed-in user's role.

## Environment and security

- Never commit `backend/.env`, `frontend/.env`, `db.sqlite3`, uploaded media, or real credentials.
- Use a long random `SECRET_KEY` and `DEBUG=False` in production.
- Configure explicit hosts, CORS origins, HTTPS, secure cookies, SMTP, PostgreSQL, and production file storage before launch.
- Rotate any credential that has previously been shared or committed.
- Review [`DEPLOYMENT.md`](DEPLOYMENT.md) for the production checklist.

## Current status

The implemented flow covers participant profiles, individual event enrollment, official challenges, team formation, roster controls, proposals and attachments, recorded introductions, organizer inquiries, judge scoring, notifications, and admin management.

Recommended next production steps are automated CI, rate limiting, audit logs, cloud media uploads, email delivery, accessibility testing, and a staging deployment.
