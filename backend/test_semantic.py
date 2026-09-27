from user_profile import USER_PROFILE
from semantic_matcher import semantic_match


# ==========================================
# TEST JOB
# ==========================================

job = {

    "title": "Java Backend Developer",

    "company_name": "Example Technologies",

    "location": "Chennai, Tamil Nadu, India",

    "description": """
    We are looking for a Junior Backend Developer.

    Candidates should have knowledge of Java,
    Python, SQL and REST APIs.

    Fresh graduates are welcome.

    Experience with Spring Boot is an advantage.
    """
}


# ==========================================
# RUN SEMANTIC MATCHING
# ==========================================

result = semantic_match(
    job,
    USER_PROFILE
)


# ==========================================
# DISPLAY RESULT
# ==========================================

print("\n===================================")
print("       SERPGUARD AI")
print("     SEMANTIC MATCH TEST")
print("===================================")

print("\nJOB DETAILS")
print("-----------------------------------")

print(
    "Title:",
    job["title"]
)

print(
    "Company:",
    job["company_name"]
)

print(
    "Location:",
    job["location"]
)


print("\nUSER PROFILE")
print("-----------------------------------")

print(
    "Skills:",
    ", ".join(USER_PROFILE["skills"])
)

print(
    "Experience:",
    USER_PROFILE["experience"]
)

print(
    "Preferred Roles:",
    ", ".join(
        USER_PROFILE["preferred_roles"]
    )
)

print(
    "Preferred Locations:",
    ", ".join(
        USER_PROFILE["preferred_locations"]
    )
)


print("\nSEMANTIC AI RESULT")
print("-----------------------------------")

print(
    "Semantic Match:",
    result["semantic_score"],
    "%"
)


# ==========================================
# INTERPRET SCORE
# ==========================================

score = result["semantic_score"]


if score >= 80:

    level = "Highly relevant"

elif score >= 60:

    level = "Relevant"

elif score >= 40:

    level = "Partially relevant"

else:

    level = "Low relevance"


print(
    "Relevance:",
    level
)


print("\n===================================")
print("       SEMANTIC TEST COMPLETE")
print("===================================")