# AI Business Analyst Assistant

Ask natural-language business questions and receive data-backed insights. The application uses a static HTML/CSS/JavaScript frontend, a Flask API deployed as a Vercel Python function, PostgreSQL, and Google Gemini.

## Architecture

`Vercel frontend → Vercel Flask API → PostgreSQL → Gemini API`

The API queries the `orders` table and never exposes database or Gemini credentials to the browser.

## Local development

1. Create `.env` from `.env.example` and set `DATABASE_URL` and `GEMINI_API_KEY`.
2. Install dependencies: `pip install -r requirements.txt`
3. Run with the Vercel CLI: `vercel dev`

To import `data/superstore.csv` into an existing PostgreSQL database, run `python import_to_postgres.py`. This replaces the `orders` table.

## Deployment

Deploy the repository to Vercel and configure the two environment variables listed in `.env.example`. `vercel.json` serves the frontend and routes `/api/*` to `api/index.py`.
