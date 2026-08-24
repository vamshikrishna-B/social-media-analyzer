"""
Unit Tests for Social Media Content Analyzer app logic.
"""

from app import analyze_content, extract_text_from_pdf, extract_text_from_image


def test_analyze_content_basic():
    sample_text = (
        "Are you struggling to boost your engagement rate? 🚀\n"
        "Check out our 3 simple tips to grow faster!\n"
        "Comment 'GROWTH' below to get your free guide. #SocialMedia #Marketing @GrowthHub"
    )

    result = analyze_content(sample_text)

    assert result["wordCount"] > 15
    assert result["characterCount"] > 50
    assert result["questionCount"] == 1
    assert result["hashtagCount"] == 2
    assert "#SocialMedia" in result["hashtags"]
    assert "#Marketing" in result["hashtags"]
    assert result["mentionCount"] == 1
    assert "@GrowthHub" in result["mentions"]
    assert result["hasCallToAction"] is True
    assert result["sentiment"] == "Positive"
    assert result["engagementScore"] >= 70
    assert len(result["suggestions"]) >= 0


def test_analyze_content_missing_cta_and_hashtags():
    sample_text = "We released a minor update today fixing background color bugs."
    result = analyze_content(sample_text)

    assert result["hasCallToAction"] is False
    assert result["hashtagCount"] == 0
    assert result["questionCount"] == 0

    # Ensure suggestions flag missing CTA & Hashtags
    categories = [s["category"] for s in result["suggestions"]]
    assert "Call-to-Action" in categories
    assert "Hashtags" in categories


def test_readability_calculation():
    easy_text = "The cat sat on the mat. It was happy."
    result = analyze_content(easy_text)
    assert result["readabilityScore"] > 60
    assert result["readabilityLabel"] in ("Easy to Read", "Standard / Moderate")


if __name__ == "__main__":
    test_analyze_content_basic()
    test_analyze_content_missing_cta_and_hashtags()
    test_readability_calculation()
    print("ALL UNIT TESTS PASSED SUCCESSFULLY!")
