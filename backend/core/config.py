import os
from dotenv import load_dotenv

load_dotenv()

API_KEYS = {
    "adzuna": os.getenv("ADZUNA_API_KEY"),
    "serpapi": os.getenv("SERPAPI_API_KEY"),
    # Add more as needed
}
