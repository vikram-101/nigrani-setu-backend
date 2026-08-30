# Nigrani Setu — Backend

FastAPI + MongoDB backend for the DoSJE Real-Time Monitoring & Inspection prototype.

## Local Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# now edit .env: paste your MongoDB Atlas URI and a random JWT secret

uvicorn main:app --reload
```

API docs auto-generate at: http://127.0.0.1:8000/docs — use this to test every
endpoint by hand before wiring up the frontend.

## How roles work

There is no single "login" that asks you to pick a role. Instead there are
three signup endpoints:

- `POST /auth/signup/inspector`
- `POST /auth/signup/department`
- `POST /auth/signup/admin` (keep this one private — don't expose it publicly
  in the deployed demo; create your one admin account locally then remove or
  protect this route)

Whichever endpoint creates the account is what tags it with that role in the
database. `POST /auth/login` is shared by everyone — the JWT it returns
already encodes the role, and every protected route checks that role via
`app/dependencies.py`.

## Request flow to test end-to-end

1. Sign up an admin, an inspector, and a department official (3 separate
   `/auth/signup/...` calls). Save each returned `access_token`.
2. As admin: `POST /institutes`, `POST /inspectors`, then `POST
   /assignments/draw`.
3. As the inspector: `GET /assignments/mine` to see the draw, then `POST
   /reports` (multipart form — include a `photo` file field).
4. As department/admin: `GET /reports` and `GET /alerts` to see it land, or
   connect a WebSocket to `/ws/dashboard?token=<jwt>` to see it pushed live.

## Deploying (Render)

1. Push this folder to GitHub.
2. On Render: New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example` in Render's dashboard —
   don't commit the real `.env` file.
6. Once live, add the Render URL's frontend counterpart (your Vercel domain)
   to `CORS_ORIGINS`.

Note: local file uploads (`/uploads`) don't persist across Render's free-tier
redeploys. Fine for a demo; swap `save_upload()` in `app/utils.py` for
S3/Cloudinary if you need photos to survive restarts.
