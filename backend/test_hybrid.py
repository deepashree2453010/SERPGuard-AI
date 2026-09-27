from user_profile import USER_PROFILE
from hybrid_matcher import calculate_hybrid_match


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
# RUN HYBRID MATCHING
# ==========================================

result = calculate_hybrid_match(
    job,
    USER_PROFILE
)


# ==========================================
# DISPLAY RESULT
# ==========================================

print("\n===================================")
print("          SERPGUARD AI")
print("       HYBRID AI MATCH TEST")
print("===================================")


print("\nJOB")
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


print("\nMATCH ANALYSIS")
print("-----------------------------------")

print(
    "Rule-based Match:",
    result["rule_score"],
    "%"
)

print(
    "Semantic AI Match:",
    result["semantic_score"],
    "%"
)

print(
    "Final Hybrid Match:",
    result["match_score"],
    "%"
)


print("\nMATCHED SKILLS")
print("-----------------------------------")

if result["matched_skills"]:

    print(
        ", ".join(
            result["matched_skills"]
        )
    )

else:

    print("None")


print("\nMISSING SKILLS")
print("-----------------------------------")

if result["missing_skills"]:

    print(
        ", ".join(
            result["missing_skills"]
        )
    )

else:

    print("None")


# ==========================================
# INTERPRET RESULT
# ==========================================

score = result["match_score"]


print("\nMATCH LEVEL")
print("-----------------------------------")


if score >= 80:

    print("Highly relevant")

elif score >= 60:

    print("Relevant")

elif score >= 40:

    print("Partially relevant")

else:

    print("Low relevance")


print("\n===================================")
print("       HYBRID TEST COMPLETE")
print("===================================")