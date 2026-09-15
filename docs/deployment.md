# Deployment

For judging, run the backend on port 8000 and frontend on port 5173, or use `docker compose up --build` and open port 80.

Production checklist: disable `DEV_OTP_MODE`, use a long random `JWT_SECRET`, terminate TLS at a trusted reverse proxy, connect a real email/SMS provider, persist OTP challenges in Redis, use Postgres, and run database migrations.
