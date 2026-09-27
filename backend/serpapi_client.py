import os
import requests
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

SERPAPI_URL = "https://serpapi.com/search.json"


# ============================================================
# SEARCH JOBS
# ============================================================

def search_jobs(query: str, location: str) -> dict:

    # --------------------------------------------------------
    # Validate API key
    # --------------------------------------------------------

    if not SERPAPI_KEY:
        raise RuntimeError(
            "SERPAPI_KEY is missing from the .env file."
        )

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    query = query.strip()
    location = location.strip()

    if not query:
        raise ValueError(
            "Search query cannot be empty."
        )

    if not location:
        raise ValueError(
            "Location cannot be empty."
        )

    # --------------------------------------------------------
    # SerpApi parameters
    # --------------------------------------------------------

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }

    try:

        response = requests.get(
            SERPAPI_URL,
            params=params,
            timeout=30,
        )

    except requests.RequestException as error:

        raise RuntimeError(
            f"Unable to connect to SerpApi: {error}"
        )

    # --------------------------------------------------------
    # HTTP error
    # --------------------------------------------------------

    if response.status_code != 200:

        try:
            error_data = response.json()
        except ValueError:
            error_data = response.text

        raise RuntimeError(
            f"SerpApi request failed "
            f"(HTTP {response.status_code}): "
            f"{error_data}"
        )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        data = response.json()

    except ValueError:

        raise RuntimeError(
            "SerpApi returned an invalid JSON response."
        )

    # --------------------------------------------------------
    # SerpApi can return an API error inside JSON
    # --------------------------------------------------------

    if data.get("error"):

        raise RuntimeError(
            f"SerpApi error: {data['error']}"
        )

    # --------------------------------------------------------
    # Validate response
    # --------------------------------------------------------

    if not isinstance(data, dict):

        raise RuntimeError(
            "SerpApi returned an unexpected response format."
        )

    # --------------------------------------------------------
    # Return complete response
    # --------------------------------------------------------

    return data