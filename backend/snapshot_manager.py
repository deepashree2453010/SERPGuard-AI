import sqlite3
import json
import hashlib
from datetime import datetime


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DATABASE = "serpguard.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    """
    Create and return a SQLite database connection.
    """
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def initialize_database():
    """
    Create the required snapshot tables if they
    do not already exist.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------
    # SNAPSHOTS TABLE
    # --------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            query TEXT NOT NULL,

            location TEXT NOT NULL,

            created_at TEXT NOT NULL

        )
    """)

    # --------------------------------------
    # SNAPSHOT JOBS TABLE
    # --------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshot_jobs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            snapshot_id INTEGER NOT NULL,

            job_key TEXT NOT NULL,

            title TEXT,

            company TEXT,

            location TEXT,

            description TEXT,

            job_data TEXT NOT NULL,

            FOREIGN KEY (snapshot_id)
                REFERENCES snapshots(id)
                ON DELETE CASCADE

        )
    """)

    # --------------------------------------
    # INDEXES
    # --------------------------------------

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_snapshots_query_location

        ON snapshots(query, location)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_snapshot_jobs_snapshot_id

        ON snapshot_jobs(snapshot_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_snapshot_jobs_job_key

        ON snapshot_jobs(job_key)
    """)

    connection.commit()
    connection.close()


# ==========================================
# CREATE UNIQUE JOB KEY
# ==========================================

def get_job_key(job):
    """
    Generate a stable unique identifier for a job.

    Uses:
        title
        company
        location
    """

    title = str(
        job.get("title") or ""
    ).strip().lower()

    company = str(
        job.get("company_name")
        or job.get("company")
        or ""
    ).strip().lower()

    location = str(
        job.get("location") or ""
    ).strip().lower()

    raw_key = "|".join([
        title,
        company,
        location
    ])

    # Create deterministic SHA256 key
    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()


# ==========================================
# CREATE SNAPSHOT
# ==========================================

def create_snapshot(
    query,
    location,
    jobs
):
    """
    Save a complete search result as a snapshot.

    Returns:
        snapshot_id
    """

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().isoformat()

    # --------------------------------------
    # CREATE SNAPSHOT RECORD
    # --------------------------------------

    cursor.execute(
        """
        INSERT INTO snapshots
        (
            query,
            location,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            query,
            location,
            created_at
        )
    )

    snapshot_id = cursor.lastrowid

    # --------------------------------------
    # SAVE JOBS
    # --------------------------------------

    for job in jobs:

        job_key = get_job_key(job)

        title = (
            job.get("title")
            or ""
        )

        company = (
            job.get("company_name")
            or job.get("company")
            or ""
        )

        job_location = (
            job.get("location")
            or ""
        )

        description = (
            job.get("description")
            or ""
        )

        job_data = json.dumps(
            job,
            ensure_ascii=False
        )

        cursor.execute(
            """
            INSERT INTO snapshot_jobs
            (
                snapshot_id,
                job_key,
                title,
                company,
                location,
                description,
                job_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot_id,
                job_key,
                title,
                company,
                job_location,
                description,
                job_data
            )
        )

    connection.commit()
    connection.close()

    return snapshot_id


# ==========================================
# GET PREVIOUS SNAPSHOT
# ==========================================

def get_previous_snapshot(
    query,
    location
):
    """
    Get the most recent snapshot for a
    specific search query and location.

    Returns:
        snapshot_id or None
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id

        FROM snapshots

        WHERE query = ?
        AND location = ?

        ORDER BY id DESC

        LIMIT 1
        """,
        (
            query,
            location
        )
    )

    row = cursor.fetchone()

    connection.close()

    if row:
        return row["id"]

    return None


# ==========================================
# GET SNAPSHOT JOBS
# ==========================================

def get_snapshot_jobs(
    snapshot_id
):
    """
    Retrieve all jobs belonging to
    a particular snapshot.

    Returns:
        list of job dictionaries
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT job_data

        FROM snapshot_jobs

        WHERE snapshot_id = ?

        ORDER BY id ASC
        """,
        (snapshot_id,)
    )

    rows = cursor.fetchall()

    connection.close()

    jobs = []

    for row in rows:

        try:

            job = json.loads(
                row["job_data"]
            )

            jobs.append(job)

        except (
            json.JSONDecodeError,
            TypeError
        ):

            print(
                "Warning: Invalid job data "
                f"in snapshot {snapshot_id}."
            )

    return jobs


# ==========================================
# COMPARE SNAPSHOTS
# ==========================================

def compare_snapshots(
    previous_jobs,
    current_jobs
):
    """
    Compare two job snapshots.

    Detects:

        NEW
        REMOVED
        UNCHANGED
        SCORE CHANGED
    """

    previous_map = {}
    current_map = {}

    # --------------------------------------
    # BUILD PREVIOUS JOB MAP
    # --------------------------------------

    for job in previous_jobs:

        key = get_job_key(job)

        previous_map[key] = job

    # --------------------------------------
    # BUILD CURRENT JOB MAP
    # --------------------------------------

    for job in current_jobs:

        key = get_job_key(job)

        current_map[key] = job

    # --------------------------------------
    # RESULT LISTS
    # --------------------------------------

    new_jobs = []

    removed_jobs = []

    unchanged_jobs = []

    score_changed_jobs = []

    # ======================================
    # CHECK CURRENT JOBS
    # ======================================

    for key, current_job in current_map.items():

        # ----------------------------------
        # NEW JOB
        # ----------------------------------

        if key not in previous_map:

            new_jobs.append(
                current_job
            )

            continue

        # ----------------------------------
        # EXISTING JOB
        # ----------------------------------

        previous_job = previous_map[key]

        previous_match = (
            previous_job
            .get("match", {})
            .get("match_score")
        )

        current_match = (
            current_job
            .get("match", {})
            .get("match_score")
        )

        # ----------------------------------
        # MATCH SCORE CHANGED
        # ----------------------------------

        if (
            previous_match is not None
            and current_match is not None
            and previous_match != current_match
        ):

            changed_job = {
                **current_job,

                "previous_match_score":
                    previous_match,

                "current_match_score":
                    current_match,

                "score_difference":
                    current_match - previous_match
            }

            score_changed_jobs.append(
                changed_job
            )

        # ----------------------------------
        # UNCHANGED
        # ----------------------------------

        else:

            unchanged_jobs.append(
                current_job
            )

    # ======================================
    # CHECK REMOVED JOBS
    # ======================================

    for key, previous_job in previous_map.items():

        if key not in current_map:

            removed_jobs.append(
                previous_job
            )

    # ======================================
    # RETURN RESULTS
    # ======================================

    return {

        "new": new_jobs,

        "removed": removed_jobs,

        "unchanged": unchanged_jobs,

        "score_changed":
            score_changed_jobs

    }