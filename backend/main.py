from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from serpapi_client import search_jobs
from validator import deduplicate_jobs
from hybrid_matcher import calculate_hybrid_match
from user_profile import USER_PROFILE

from snapshot_manager import (
    initialize_database,
    create_snapshot,
    get_previous_snapshot,
    get_snapshot_jobs,
    compare_snapshots,
)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

APP_TITLE = "SERPGuard AI"
APP_DESCRIPTION = (
    "AI-powered job discovery, semantic matching, "
    "and job change intelligence API."
)
APP_VERSION = "1.0.0"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# REQUEST MODEL
# ============================================================

class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Job search query",
    )

    location: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Job search location",
    )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root() -> Dict[str, Any]:
    """
    Root endpoint used to verify that the API is running.
    """

    return {
        "application": APP_TITLE,
        "version": APP_VERSION,
        "status": "running",
        "message": "SERPGuard AI backend is running successfully.",
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health() -> Dict[str, Any]:
    """
    Health-check endpoint.
    """

    return {
        "status": "healthy",
        "service": APP_TITLE,
    }


# ============================================================
# SEARCH ENDPOINT
# ============================================================

@app.get("/api/search")
def search_jobs_api(
    query: str,
    location: str,
) -> Dict[str, Any]:
    """
    Search jobs using SerpApi.

    Pipeline:
        1. Search jobs
        2. Remove duplicate jobs
        3. Calculate hybrid AI match
        4. Sort jobs by match score
        5. Compare with previous snapshot
        6. Save current snapshot
        7. Return top matching jobs
    """

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    query = query.strip()
    location = location.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Job search query cannot be empty.",
        )

    if not location:
        raise HTTPException(
            status_code=400,
            detail="Location cannot be empty.",
        )

    try:

        # ====================================================
        # 1. SEARCH SERPAPI
        # ====================================================

        print()
        print("=" * 60)
        print("SERPGUARD AI - JOB SEARCH")
        print("=" * 60)

        print("Query:", query)
        print("Location:", location)
        print()
        print("Searching SerpApi...")

        results = search_jobs(
            query,
            location,
        )

        if not isinstance(results, dict):
            raise HTTPException(
                status_code=502,
                detail="Invalid response received from SerpApi.",
            )

        jobs = results.get(
            "jobs_results",
            [],
        )

        if not isinstance(jobs, list):
            jobs = []

        print("Jobs received:", len(jobs))


        # ====================================================
        # 2. REMOVE DUPLICATES
        # ====================================================

        unique_jobs = deduplicate_jobs(
            jobs
        )

        print(
            "Unique jobs:",
            len(unique_jobs)
        )


        # ====================================================
        # 3. HYBRID AI MATCHING
        # ====================================================

        print()
        print("Calculating hybrid AI matches...")

        matched_jobs: List[Dict[str, Any]] = []

        for job in unique_jobs:

            try:

                match_result = calculate_hybrid_match(
                    job,
                    USER_PROFILE,
                )

            except Exception as match_error:

                print(
                    "Match calculation failed:",
                    match_error,
                )

                match_result = {
                    "match_score": 0,
                    "rule_score": 0,
                    "semantic_score": 0,
                    "matched_skills": [],
                    "missing_skills": [],
                }

            job_with_match = {
                **job,
                "match": match_result,
            }

            matched_jobs.append(
                job_with_match
            )


        # ====================================================
        # 4. SORT BY MATCH SCORE
        # ====================================================

        matched_jobs.sort(
            key=lambda job: (
                job.get(
                    "match",
                    {}
                ).get(
                    "match_score",
                    0,
                )
            ),
            reverse=True,
        )


        # ====================================================
        # 5. GET PREVIOUS SNAPSHOT
        # ====================================================

        previous_snapshot_id = get_previous_snapshot(
            query,
            location,
        )


        # ====================================================
        # 6. CHANGE DETECTION
        # ====================================================

        changes = {
            "new": [],
            "removed": [],
            "unchanged": [],
            "score_changed": [],
        }

        if previous_snapshot_id:

            print(
                "Previous snapshot:",
                previous_snapshot_id,
            )

            previous_jobs = get_snapshot_jobs(
                previous_snapshot_id
            )

            changes = compare_snapshots(
                previous_jobs,
                matched_jobs,
            )


        # ====================================================
        # 7. CREATE NEW SNAPSHOT
        # ====================================================

        snapshot_id = create_snapshot(
            query,
            location,
            matched_jobs,
        )


        # ====================================================
        # 8. TOP JOBS
        # ====================================================

        top_jobs = matched_jobs[:5]


        # ====================================================
        # 9. CHANGE SUMMARY
        # ====================================================

        change_summary = {
            "new": len(
                changes.get(
                    "new",
                    [],
                )
            ),

            "removed": len(
                changes.get(
                    "removed",
                    [],
                )
            ),

            "unchanged": len(
                changes.get(
                    "unchanged",
                    [],
                )
            ),

            "score_changed": len(
                changes.get(
                    "score_changed",
                    [],
                )
            ),
        }


        # ====================================================
        # 10. FINAL RESPONSE
        # ====================================================

        response = {
            "success": True,

            "application": APP_TITLE,

            "search": {
                "query": query,
                "location": location,
            },

            "statistics": {
                "jobs_received": len(jobs),
                "unique_jobs": len(unique_jobs),
                "jobs_analyzed": len(matched_jobs),
                "top_matches": len(top_jobs),
            },

            "jobs": top_jobs,

            "changes": changes,

            "change_summary": change_summary,

            "snapshot": {
                "id": snapshot_id,
                "previous_id": previous_snapshot_id,
            },
        }


        # ====================================================
        # SEARCH COMPLETE
        # ====================================================

        print()
        print("=" * 60)
        print("SEARCH COMPLETE")
        print("=" * 60)
        print(
            "Jobs analyzed:",
            len(matched_jobs),
        )
        print(
            "Top matches:",
            len(top_jobs),
        )
        print(
            "Snapshot ID:",
            snapshot_id,
        )
        print("=" * 60)

        return response


    # ========================================================
    # HTTP EXCEPTION
    # ========================================================

    except HTTPException:
        raise


    # ========================================================
    # UNEXPECTED ERROR
    # ========================================================

    except Exception as error:

        print()
        print("=" * 60)
        print("SERPGUARD SEARCH ERROR")
        print("=" * 60)
        print(
            type(error).__name__,
            ":",
            error,
        )
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=(
                "An internal error occurred while "
                "processing the job search."
            ),
        )


# ============================================================
# STARTUP EVENT
# ============================================================

@app.on_event("startup")
def startup_event():
    """
    Runs when FastAPI starts.
    """

    initialize_database()

    print()
    print("=" * 60)
    print("             SERPGUARD AI BACKEND")
    print("=" * 60)
    print("Status : ONLINE")
    print("API    : http://127.0.0.1:8000")
    print("Docs   : http://127.0.0.1:8000/docs")
    print("Health : http://127.0.0.1:8000/health")
    print("=" * 60)