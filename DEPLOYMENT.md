# Deployment

## Local full stack

1. Copy `backend/.env.example` to `backend/.env`.
2. Set a strong `SECRET_KEY`, PostgreSQL credentials, and `DEBUG=False` for production-like runs.
3. Start PostgreSQL and Django with `docker compose up --build`.
4. Run migrations with `docker compose run --rm backend python manage.py migrate`.
5. Optionally seed local demo data with `docker compose run --rm backend python manage.py seed_data`.

The frontend remains a Vite application and should be built with `npm run build`, then served by a static host or reverse proxy. Set `VITE_API_BASE_URL` to the deployed API base URL.

## Production requirements

- Use PostgreSQL via `DB_ENGINE=django.db.backends.postgresql`.
- Set `DEBUG=False`, a long random `SECRET_KEY`, and explicit `ALLOWED_HOSTS`.
- Configure SMTP values for verification and password-reset emails.
- Serve Django through Gunicorn behind HTTPS.
- Provide Azure storage settings before enabling production media storage.
- Azure SAS upload generation is intentionally deferred; the current upload path uses Django's configured storage adapter.
