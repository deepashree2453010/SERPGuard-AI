from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from serpapi_client import search_jobs
from validator import deduplicate_jobs
from user_profile import USER_PROFILE
from hybrid_matcher import calculate_hybrid_match

from snapshot_manager import (
    initialize_database,
    create_snapshot,
    get_previous_snapshot,
    get_snapshot_jobs,
    compare_snapshots
)


# ==========================================
# APPLICATION
# ==========================================

app = FastAPI(
    title="SERPGuard AI",
    description="AI-powered job monitoring and change intelligence system",
    version="1.0.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# DATABASE
# ==========================================

initialize_database()


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def root():

    return {
        "status": "success",
        "message": "SERPGuard AI API is running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==========================================
# SEARCH JOBS
# ==========================================

@app.get("/api/search")
def search(
    query: str = "Java developer fresher",
    location: str = "Chennai, Tamil Nadu, India"
):

    try:

        # ----------------------------------
        # SERPAPI SEARCH
        # ----------------------------------

        results = search_jobs(
            query,
            location
        )

        jobs = results.get(
            "jobs_results",
            []
        )

        # ----------------------------------
        # DEDUPLICATION
        # ----------------------------------

        unique_jobs = deduplicate_jobs(
            jobs
        )

        # ----------------------------------
        # HYBRID AI MATCHING
        # ----------------------------------

        matched_jobs = []

        for job in unique_jobs:

            match = calculate_hybrid_match(
                job,
                USER_PROFILE
            )

            job_with_match = {
                **job,
                "match": match
            }

            matched_jobs.append(
                job_with_match
            )

        # ----------------------------------
        # SORT BY MATCH SCORE
        # ----------------------------------

        matched_jobs.sort(
            key=lambda x:
                x["match"]["match_score"],
            reverse=True
        )

        # ----------------------------------
        # PREVIOUS SNAPSHOT
        # ----------------------------------

        previous_snapshot_id = (
            get_previous_snapshot(
                query,
                location
            )
        )

        changes = {
            "new": [],
            "removed": [],
            "unchanged": [],
            "score_changed": []
        }

        # ----------------------------------
        # CHANGE INTELLIGENCE
        # ----------------------------------

        if previous_snapshot_id:

            previous_jobs = (
                get_snapshot_jobs(
                    previous_snapshot_id
                )
            )

            changes = compare_snapshots(
                previous_jobs,
                matched_jobs
            )

        # ----------------------------------
        # SAVE SNAPSHOT
        # ----------------------------------

        snapshot_id = create_snapshot(
            query,
            location,
            matched_jobs
        )

        # ----------------------------------
        # RESPONSE
        # ----------------------------------

        return {

            "success": True,

            "query": query,

            "location": location,

            "jobs_received": len(jobs),

            "jobs_analyzed": len(
                unique_jobs
            ),

            "top_matches": matched_jobs[:5],

            "changes": {

                "new": changes["new"],

                "removed": changes["removed"],

                "unchanged": changes[
                    "unchanged"
                ],

                "score_changed":
                    changes[
                        "score_changed"
                    ]
            },

            "change_summary": {

                "new":
                    len(changes["new"]),

                "removed":
                    len(changes["removed"]),

                "unchanged":
                    len(changes["unchanged"]),

                "score_changed":
                    len(
                        changes[
                            "score_changed"
                        ]
                    )
            },

            "snapshot_id": snapshot_id

        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )