import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(PROJECT_ROOT / ".env")

# Get API key.  The argument to ``getenv`` must be the variable name, not
# the key value stored in .env.
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. "
        "Please check the .env file in the project root."
    )

# Gemini client
client = genai.Client(api_key=api_key)

# Test Gemini
response = client.models.generate_content(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    contents="Explain business analytics in one sentence."
)

print(response.text)
