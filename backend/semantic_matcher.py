import os

import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")


# ==========================================
# VALIDATE HUGGING FACE TOKEN
# ==========================================

if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN not found. "
        "Please add HF_TOKEN to the backend .env file."
    )


# ==========================================
# LOAD EMBEDDING MODEL
# ==========================================

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(
    MODEL_NAME,
    token=HF_TOKEN
)


# ==========================================
# CREATE TEXT FOR USER PROFILE
# ==========================================

def create_profile_text(profile):
    """
    Convert the user's profile into descriptive text
    for semantic comparison.
    """

    skills = ", ".join(
        profile.get("skills", [])
    )

    roles = ", ".join(
        profile.get("preferred_roles", [])
    )

    locations = ", ".join(
        profile.get("preferred_locations", [])
    )

    experience = profile.get(
        "experience",
        ""
    )

    return (
        f"Skills: {skills}. "
        f"Preferred roles: {roles}. "
        f"Preferred locations: {locations}. "
        f"Experience: {experience}."
    )


# ==========================================
# CREATE TEXT FOR JOB
# ==========================================

def create_job_text(job):
    """
    Convert a job listing into descriptive text
    for semantic comparison.
    """

    title = job.get(
        "title",
        ""
    )

    company = job.get(
        "company_name",
        job.get("company", "")
    )

    location = job.get(
        "location",
        ""
    )

    description = job.get(
        "description",
        ""
    )

    return (
        f"Job title: {title}. "
        f"Company: {company}. "
        f"Location: {location}. "
        f"Job description: {description}."
    )


# ==========================================
# COSINE SIMILARITY
# ==========================================

def cosine_similarity(
    vector1,
    vector2
):
    """
    Calculate cosine similarity between
    two embedding vectors.
    """

    vector1 = np.asarray(
        vector1,
        dtype=float
    )

    vector2 = np.asarray(
        vector2,
        dtype=float
    )

    denominator = (
        np.linalg.norm(vector1)
        *
        np.linalg.norm(vector2)
    )

    if denominator == 0:
        return 0.0

    similarity = (
        np.dot(
            vector1,
            vector2
        )
        /
        denominator
    )

    return float(similarity)


# ==========================================
# SEMANTIC JOB MATCH
# ==========================================

def semantic_match(
    job,
    profile
):
    """
    Calculate semantic similarity between
    a user profile and a job description.
    """

    # --------------------------------------
    # CREATE TEXT
    # --------------------------------------

    profile_text = create_profile_text(
        profile
    )

    job_text = create_job_text(
        job
    )


    # --------------------------------------
    # CREATE EMBEDDINGS
    # --------------------------------------

    profile_embedding = model.encode(
        profile_text,
        normalize_embeddings=True
    )

    job_embedding = model.encode(
        job_text,
        normalize_embeddings=True
    )


    # --------------------------------------
    # CALCULATE SIMILARITY
    # --------------------------------------

    similarity = cosine_similarity(
        profile_embedding,
        job_embedding
    )


    # --------------------------------------
    # CONVERT TO PERCENTAGE
    # --------------------------------------

    similarity = max(
        0.0,
        min(
            similarity,
            1.0
        )
    )

    semantic_score = round(
        similarity * 100
    )


    # --------------------------------------
    # RETURN RESULT
    # --------------------------------------

    return {

        "semantic_score": semantic_score,

        "profile_text": profile_text,

        "job_text": job_text

    }