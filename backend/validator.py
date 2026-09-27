import hashlib


# ==========================================
# CREATE UNIQUE JOB KEY
# ==========================================

def get_job_key(job):

    # SerpApi job ID is the best identifier
    if job.get("job_id"):

        return str(job["job_id"])


    # Fallback if job_id is missing
    title = job.get(
        "title",
        ""
    ).strip().lower()

    company = job.get(
        "company_name",
        ""
    ).strip().lower()

    location = job.get(
        "location",
        ""
    ).strip().lower()


    raw_key = (
        title
        + "|"
        + company
        + "|"
        + location
    )


    return hashlib.md5(
        raw_key.encode("utf-8")
    ).hexdigest()


# ==========================================
# VALIDATE JOB
# ==========================================

def validate_job(job):

    if not isinstance(job, dict):

        return False


    title = job.get(
        "title",
        ""
    ).strip()

    company = job.get(
        "company_name",
        ""
    ).strip()


    # Job must have title
    if not title:

        return False


    # Job must have company
    if not company:

        return False


    return True


# ==========================================
# REMOVE DUPLICATES
# ==========================================

def deduplicate_jobs(jobs):

    unique_jobs = []

    seen = set()


    for job in jobs:

        # Ignore invalid jobs
        if not validate_job(job):

            continue


        job_key = get_job_key(job)


        # Ignore duplicate
        if job_key in seen:

            continue


        seen.add(job_key)


        # Store key for later snapshot comparison
        job["job_key"] = job_key


        unique_jobs.append(job)


    return unique_jobs