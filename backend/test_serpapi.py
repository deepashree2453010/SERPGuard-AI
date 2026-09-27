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


# ============================================================
# SERPGUARD AI - MAIN SERPAPI TEST
# ============================================================

QUERY = "Java developer fresher"
LOCATION = "Chennai, Tamil Nadu, India"

TOP_N = 5


# ============================================================
# 1. DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# 2. START
# ============================================================

print("\n")
print("=" * 60)
print("                    SERPGUARD AI")
print("=" * 60)

print("\nSearch Configuration")
print("-" * 60)
print("Query    :", QUERY)
print("Location :", LOCATION)


# ============================================================
# 3. SEARCH SERPAPI
# ============================================================

print("\nSearching SerpApi...")

try:

    results = search_jobs(
        QUERY,
        LOCATION
    )

except Exception as error:

    print("\nERROR: SerpApi search failed.")
    print("Reason:", error)

    raise SystemExit(1)


jobs = results.get(
    "jobs_results",
    []
)


print(
    "Jobs received:",
    len(jobs)
)


# ============================================================
# 4. VALIDATION + DEDUPLICATION
# ============================================================

unique_jobs = deduplicate_jobs(
    jobs
)


print(
    "Unique jobs:",
    len(unique_jobs)
)


if not unique_jobs:

    print("\nNo valid jobs were found.")

    raise SystemExit(0)


# ============================================================
# 5. HYBRID AI MATCHING
# ============================================================

print("\n")
print("=" * 60)
print("                 HYBRID AI MATCHING")
print("=" * 60)


matched_jobs = []


for job in unique_jobs:

    try:

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

    except Exception as error:

        print(
            "\nWarning: Could not analyze job:",
            job.get(
                "title",
                "Unknown"
            )
        )

        print(
            "Reason:",
            error
        )


# ============================================================
# 6. SORT BY FINAL MATCH SCORE
# ============================================================

matched_jobs.sort(
    key=lambda job: job["match"]["match_score"],
    reverse=True
)


# ============================================================
# 7. DISPLAY TOP MATCHED JOBS
# ============================================================

print("\n")
print("=" * 60)
print("                    TOP JOB MATCHES")
print("=" * 60)


for index, job in enumerate(
    matched_jobs[:TOP_N],
    start=1
):

    match = job["match"]

    title = job.get(
        "title",
        "Unknown Title"
    )

    company = job.get(
        "company_name",
        "Unknown Company"
    )

    location = job.get(
        "location",
        "Unknown Location"
    )

    final_score = match.get(
        "match_score",
        0
    )

    rule_score = match.get(
        "rule_score",
        0
    )

    semantic_score = match.get(
        "semantic_score",
        0
    )

    matched_skills = match.get(
        "matched_skills",
        []
    )

    missing_skills = match.get(
        "missing_skills",
        []
    )


    print(f"\n{index}. {title}")

    print(
        "   Company          :",
        company
    )

    print(
        "   Location         :",
        location
    )

    print(
        "   Final Match      :",
        f"{final_score}%"
    )

    print(
        "   Rule-Based Match :",
        f"{rule_score}%"
    )

    print(
        "   Semantic AI Match:",
        f"{semantic_score}%"
    )

    print(
        "   Matched Skills   :",
        ", ".join(matched_skills)
        if matched_skills
        else "None"
    )

    print(
        "   Missing Skills   :",
        ", ".join(missing_skills)
        if missing_skills
        else "None"
    )


# ============================================================
# 8. PREVIOUS SNAPSHOT
# ============================================================

previous_snapshot_id = get_previous_snapshot(
    QUERY,
    LOCATION
)


# ============================================================
# 9. CHANGE DETECTION
# ============================================================

if previous_snapshot_id:

    print("\n")
    print("=" * 60)
    print("                 CHANGE INTELLIGENCE")
    print("=" * 60)

    print(
        "\nPrevious Snapshot ID:",
        previous_snapshot_id
    )


    previous_jobs = get_snapshot_jobs(
        previous_snapshot_id
    )


    changes = compare_snapshots(
        previous_jobs,
        matched_jobs
    )


    new_jobs = changes.get(
        "new",
        []
    )

    removed_jobs = changes.get(
        "removed",
        []
    )

    unchanged_jobs = changes.get(
        "unchanged",
        []
    )

    score_changed_jobs = changes.get(
        "score_changed",
        []
    )


    # --------------------------------------------------------
    # CHANGE SUMMARY
    # --------------------------------------------------------

    print("\nChange Summary")
    print("-" * 60)

    print(
        "New Jobs       :",
        len(new_jobs)
    )

    print(
        "Removed Jobs   :",
        len(removed_jobs)
    )

    print(
        "Unchanged Jobs :",
        len(unchanged_jobs)
    )

    print(
        "Score Changed  :",
        len(score_changed_jobs)
    )


    # ========================================================
    # NEW JOBS
    # ========================================================

    if new_jobs:

        print("\n🟢 NEW JOBS")
        print("-" * 60)


        for job in new_jobs:

            print(
                "-",
                job.get(
                    "title",
                    "Unknown"
                ),
                "|",
                job.get(
                    "company_name",
                    "Unknown"
                )
            )


    # ========================================================
    # REMOVED JOBS
    # ========================================================

    if removed_jobs:

        print("\n🔴 REMOVED JOBS")
        print("-" * 60)


        for job in removed_jobs:

            company = job.get(
                "company_name",
                job.get(
                    "company",
                    "Unknown"
                )
            )


            print(
                "-",
                job.get(
                    "title",
                    "Unknown"
                ),
                "|",
                company
            )


    # ========================================================
    # MATCH SCORE CHANGES
    # ========================================================

    if score_changed_jobs:

        print("\n🟡 MATCH SCORE CHANGES")
        print("-" * 60)


        for job in score_changed_jobs:

            old_score = job.get(
                "previous_match_score",
                0
            )

            new_score = job.get(
                "current_match_score",
                0
            )

            difference = job.get(
                "score_difference",
                0
            )


            print(
                f"- {job.get('title', 'Unknown')} | "
                f"{old_score}% → {new_score}% "
                f"({difference:+d}%)"
            )


else:

    print("\n")
    print("=" * 60)
    print("                 CHANGE INTELLIGENCE")
    print("=" * 60)

    print("\nNo previous snapshot found.")
    print("This is the first search for this query/location.")


# ============================================================
# 10. SAVE CURRENT SNAPSHOT
# ============================================================

snapshot_id = create_snapshot(
    QUERY,
    LOCATION,
    matched_jobs
)


print("\n")
print("=" * 60)
print("                 SNAPSHOT SAVED")
print("=" * 60)

print(
    "Snapshot ID:",
    snapshot_id
)


# ============================================================
# 11. COMPLETE
# ============================================================

print("\n")
print("=" * 60)
print("              SEARCH COMPLETE")
print("=" * 60)

print(
    "\nSERPGUARD AI successfully completed the search."
)

print(
    "Jobs analyzed:",
    len(matched_jobs)
)

print(
    "Top matches displayed:",
    min(
        TOP_N,
        len(matched_jobs)
    )
)

print(
    "Snapshot stored:",
    snapshot_id
)

print("\n")