from job_matcher import calculate_match
from semantic_matcher import semantic_match


# ==========================================
# HYBRID JOB MATCHER
# ==========================================

def calculate_hybrid_match(job, profile):
    """
    Calculate the final job match score by combining:

    - Rule-based matching: 40%
    - Semantic AI matching: 60%

    Returns a complete matching result.
    """

    # ======================================
    # 1. RULE-BASED MATCHING
    # ======================================

    rule_result = calculate_match(
        job,
        profile
    )

    rule_score = float(
        rule_result.get(
            "match_score",
            0
        )
    )


    # ======================================
    # 2. SEMANTIC AI MATCHING
    # ======================================

    semantic_result = semantic_match(
        job,
        profile
    )

    semantic_score = float(
        semantic_result.get(
            "semantic_score",
            0
        )
    )


    # ======================================
    # 3. HYBRID SCORE
    # ======================================

    # Rule-based matching = 40%
    # Semantic AI matching = 60%

    final_score = (
        rule_score * 0.40
        +
        semantic_score * 0.60
    )

    final_score = round(
        final_score
    )


    # ======================================
    # 4. KEEP SCORE WITHIN 0-100
    # ======================================

    final_score = max(
        0,
        min(
            100,
            final_score
        )
    )


    # ======================================
    # 5. RETURN RESULT
    # ======================================

    return {

        "match_score": final_score,

        "rule_score": round(
            rule_score
        ),

        "semantic_score": round(
            semantic_score
        ),

        "matched_skills": rule_result.get(
            "matched_skills",
            []
        ),

        "missing_skills": rule_result.get(
            "missing_skills",
            []
        )

    }