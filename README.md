# AI Business Analyst Assistant

Ask common business questions and receive data-backed insights. The application uses a static HTML/CSS/JavaScript frontend, a rule-based Flask API deployed as a Vercel Python function, and PostgreSQL.

## Architecture

`Vercel frontend → Vercel Flask API → PostgreSQL`

The API matches supported question patterns to safe, predefined PostgreSQL queries against the `orders` table. It never exposes database credentials to the browser.

## Local development

1. Create `.env` from `.env.example` and set `DATABASE_URL`.
2. Install dependencies: `pip install -r requirements.txt`
3. Run with the Vercel CLI: `vercel dev`

To import `data/superstore.csv` into an existing PostgreSQL database, run `python import_to_postgres.py`. This replaces the `orders` table.

## Deployment

Deploy the repository to Vercel and configure `DATABASE_URL`. `vercel.json` serves the frontend and leaves `/api/*` for the Flask app in `api/index.py`.
