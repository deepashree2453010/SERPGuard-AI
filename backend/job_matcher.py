from user_profile import USER_PROFILE


def calculate_match(job, profile):

    # --------------------------------
    # GET JOB INFORMATION
    # --------------------------------

    title = job.get("title", "").lower()

    description = job.get(
        "description",
        ""
    ).lower()

    location = job.get(
        "location",
        ""
    ).lower()


    # --------------------------------
    # COMBINE JOB TEXT
    # --------------------------------

    job_text = title + " " + description


    # --------------------------------
    # SKILL MATCHING
    # --------------------------------

    matched_skills = []
    missing_skills = []

    for skill in profile["skills"]:

        skill_lower = skill.lower()

        if skill_lower in job_text:

            matched_skills.append(skill)

        else:

            missing_skills.append(skill)


    # --------------------------------
    # SKILL SCORE
    # --------------------------------

    total_skills = len(profile["skills"])

    if total_skills > 0:

        skill_score = (
            len(matched_skills)
            / total_skills
        ) * 100

    else:

        skill_score = 0


    # --------------------------------
    # LOCATION MATCH
    # --------------------------------

    location_match = False

    for preferred_location in profile[
        "preferred_locations"
    ]:

        if preferred_location.lower() in location:

            location_match = True
            break


    # --------------------------------
    # ROLE MATCH
    # --------------------------------

    role_match = False

    for role in profile["preferred_roles"]:

        if role.lower() in title:

            role_match = True
            break


    # --------------------------------
    # EXPERIENCE
    # --------------------------------

    experience_match = False

    if profile["experience"] == "fresher":

        fresher_keywords = [
            "fresher",
            "entry level",
            "entry-level",
            "junior",
            "graduate",
            "0-1",
            "0 to 1"
        ]

        for keyword in fresher_keywords:

            if keyword in job_text:

                experience_match = True
                break


    # --------------------------------
    # FINAL SCORE
    # --------------------------------

    score = skill_score * 0.60


    if location_match:

        score += 15


    if role_match:

        score += 15


    if experience_match:

        score += 10


    # Make sure score stays between 0-100

    score = min(
        round(score),
        100
    )


    # --------------------------------
    # RETURN RESULT
    # --------------------------------

    return {

        "match_score": score,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "location_match": location_match,

        "role_match": role_match,

        "experience_match": experience_match
    }