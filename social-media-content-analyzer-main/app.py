"""
Social Media Content Analyzer — Main Streamlit Application
A polished, production-quality tool for uploading PDFs and post images,
extracting text using PyMuPDF and Tesseract OCR, analyzing content metrics,
and generating actionable engagement improvement suggestions with Gemini AI.
"""

import os
import re
import io
import math
import shutil
import tempfile
from typing import Dict, List, Any, Tuple, Optional

import streamlit as st
from PIL import Image

# -----------------------------------------------------------------------------
# Dependency Imports & Dynamic Tesseract Path Configuration
# -----------------------------------------------------------------------------
try:
    import pymupdf  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True

    def find_tesseract_binary() -> Optional[str]:
        """
        Dynamically detects Tesseract OCR binary path:
        1. Checks C:\\Program Files\\Tesseract-OCR\\tesseract.exe (local Windows)
        2. Checks shutil.which('tesseract') (Linux / Streamlit Cloud / system PATH)
        3. Probes standard fallback installation directories
        """
        # 1. Primary Windows local environment path check
        win_primary = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(win_primary):
            return win_primary

        # 2. System PATH check (Linux / Streamlit Cloud / macOS)
        which_path = shutil.which("tesseract")
        if which_path:
            return which_path

        # 3. Additional fallback paths
        win_fallbacks = [
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
            os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
            "/opt/homebrew/bin/tesseract",
        ]
        for path in win_fallbacks:
            if os.path.exists(path):
                return path

        return None

    tesseract_path = find_tesseract_binary()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False


# -----------------------------------------------------------------------------
# Page Configuration & Modern Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Social Media Content Analyzer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Global Styles & Component Badges */
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .score-badge {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .suggestion-card {
        background-color: #FFFFFF;
        border-left: 4px solid #3B82F6;
        border-top: 1px solid #E5E7EB;
        border-right: 1px solid #E5E7EB;
        border-bottom: 1px solid #E5E7EB;
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .suggestion-high { border-left-color: #EF4444; }
    .suggestion-medium { border-left-color: #F59E0B; }
    .suggestion-low { border-left-color: #10B981; }

    .disclaimer-box {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 0.82rem;
        color: #1E40AF;
        margin-top: 8px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Extraction Engines (PyMuPDF & Tesseract OCR)
# -----------------------------------------------------------------------------
def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts text from PDF documents using PyMuPDF (pymupdf / fitz) preserving text layout.
    Returns (extracted_text, metadata).
    """
    if not PYMUPDF_AVAILABLE:
        return "", {"error": "PyMuPDF library is not installed."}

    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        text_pages = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text.strip():
                text_pages.append(text.strip())

        full_text = "\n\n".join(text_pages)
        page_count = len(doc)
        doc.close()

        if not full_text.strip():
            return "", {
                "page_count": page_count,
                "is_empty": True,
                "warning": (
                    "This PDF does not contain extractable text. If it is a scanned document, "
                    "please upload the document as an image file (PNG/JPG) for OCR text recognition."
                )
            }

        return full_text, {"page_count": page_count, "is_empty": False}

    except Exception as e:
        return "", {"error": f"Failed to parse PDF file: {str(e)}"}


def extract_text_from_image(uploaded_file_or_bytes: Any) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts text from image files (JPG, JPEG, PNG) using Tesseract OCR.
    Uses io.BytesIO(file_bytes) with buffer pointer reset (seek(0)) and RGB mode conversion
    to ensure PIL handles large image formats and temporary buffers cleanly.
    """
    if not PYTESSERACT_AVAILABLE:
        return "", {"error": "pytesseract package is not installed."}

    try:
        # Extract raw byte data cleanly
        if hasattr(uploaded_file_or_bytes, "getvalue"):
            file_bytes = uploaded_file_or_bytes.getvalue()
        elif isinstance(uploaded_file_or_bytes, bytes):
            file_bytes = uploaded_file_or_bytes
        else:
            file_bytes = uploaded_file_or_bytes.read()

        # Wrap in BytesIO buffer and reset pointer
        img_buffer = io.BytesIO(file_bytes)
        img_buffer.seek(0)

        # Open via PIL and convert to RGB
        image = Image.open(img_buffer)
        image = image.convert("RGB")

        # Execute OCR string recognition
        extracted_text = pytesseract.image_to_string(image, lang='eng').strip()

        if not extracted_text:
            return "", {
                "is_empty": True,
                "warning": (
                    "OCR executed successfully, but no text could be recognized in this image. "
                    "Ensure the image contains clear, legible text."
                )
            }

        return extracted_text, {"is_empty": False}

    except pytesseract.TesseractNotFoundError:
        return "", {
            "error": (
                "Tesseract OCR executable was not found on the host system. "
                "Please ensure Tesseract-OCR is installed or upload a text-based PDF."
            )
        }
    except Exception as e:
        return "", {"error": f"OCR processing failed: {str(e)}"}


# -----------------------------------------------------------------------------
# Deterministic Content Analysis Engine & Heuristics
# -----------------------------------------------------------------------------
COMMON_CTA_PATTERNS = [
    r"\b(comment|drop a comment)\b",
    r"\b(click|link in bio|link below|check out)\b",
    r"\b(subscribe|follow|share|repost|retweet)\b",
    r"\b(tag a friend|tag someone)\b",
    r"\b(sign up|register|join|download)\b",
    r"\b(dm us|send a message|contact)\b",
    r"\b(let me know|what do you think)\b",
    r"\b(save this|bookmark)\b",
]

POSITIVE_WORDS = {
    "great", "awesome", "amazing", "excellent", "best", "love", "excited",
    "growth", "success", "win", "valuable", "free", "boost", "super", "happy",
    "tip", "tips", "proven", "secret", "powerful", "transform", "leader", "hero"
}

NEGATIVE_WORDS = {
    "bad", "worst", "fail", "failure", "poor", "hate", "terrible", "mistake",
    "avoid", "stop", "never", "wrong", "costly", "danger", "warning", "hard",
    "difficult", "loss", "losing", "problem", "issue", "boring", "waste"
}


def count_syllables(word: str) -> int:
    """Estimates syllable count of an English word."""
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1
    word = re.sub(r'(?:[^laeiouy]es|ed|[^laeiouy]e)$', '', word)
    word = re.sub(r'^y', '', word)
    matches = re.findall(r'[aeiouy]{1,2}', word)
    return max(1, len(matches))


def analyze_content(text: str) -> Dict[str, Any]:
    """
    Analyzes social media post text using deterministic heuristics.
    Returns core metrics, sentiment, readability, heuristic score, and actionable suggestions.
    """
    clean_text = text.strip()
    words = re.findall(r'\b\w+\b', clean_text)
    word_count = len(words)
    char_count = len(clean_text)

    # Sentences regex
    sentences = [s.strip() for s in re.split(r'[.!?]+', clean_text) if s.strip()]
    sentence_count = max(1, len(sentences))

    # Hashtags & Mentions
    hashtags = re.findall(r'#\w+', clean_text)
    mentions = re.findall(r'@\w+', clean_text)

    # Questions
    question_count = clean_text.count('?')

    # Emojis count (Unicode codepoint ranges)
    emoji_count = 0
    for char in clean_text:
        cp = ord(char)
        if (0x1F600 <= cp <= 0x1F64F or 0x1F300 <= cp <= 0x1F5FF or
            0x1F680 <= cp <= 0x1F6FF or 0x1F1E0 <= cp <= 0x1F1FF or
            0x2600 <= cp <= 0x26FF or 0x2700 <= cp <= 0x27BF or
            0x1F900 <= cp <= 0x1F9FF or 0x1FA70 <= cp <= 0x1FAFF):
            emoji_count += 1

    # Call to Action Detection
    cta_matches = []
    for pattern in COMMON_CTA_PATTERNS:
        matches = re.findall(pattern, clean_text, re.IGNORECASE)
        if matches:
            cta_matches.extend(matches)
    has_cta = len(cta_matches) > 0

    # Sentiment Polarity Heuristic
    pos_score = sum(1 for w in words if w.lower() in POSITIVE_WORDS)
    neg_score = sum(1 for w in words if w.lower() in NEGATIVE_WORDS)

    if pos_score > neg_score:
        sentiment = "Positive"
    elif neg_score > pos_score:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    # Readability: Flesch Reading Ease
    total_syllables = sum(count_syllables(w) for w in words) if word_count > 0 else 1
    if word_count > 0 and sentence_count > 0:
        flesch_score = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (total_syllables / word_count))
        flesch_score = max(0.0, min(100.0, flesch_score))
    else:
        flesch_score = 60.0

    if flesch_score >= 70:
        readability_label = "Easy to Read"
    elif flesch_score >= 50:
        readability_label = "Standard / Moderate"
    else:
        readability_label = "Complex / Long-winded"

    # Engagement Opportunity Score (0 - 100) Heuristic
    score = 0
    if has_cta:
        score += 25
    if question_count >= 1:
        score += 20
    if 30 <= word_count <= 180:
        score += 20
    elif 15 <= word_count < 30 or 180 < word_count <= 250:
        score += 12
    elif word_count > 0:
        score += 5

    if 1 <= len(hashtags) <= 5:
        score += 15
    elif len(hashtags) > 5:
        score += 8

    if 1 <= emoji_count <= 5:
        score += 10
    elif emoji_count > 5:
        score += 5

    if sentences and len(sentences[0].split()) <= 14:
        score += 10

    engagement_score = min(100, score)

    # Suggestions Engine
    suggestions = []

    if not has_cta:
        suggestions.append({
            "category": "Call-to-Action",
            "impact": "High",
            "text": "Add a clear Call-to-Action (CTA) such as 'Comment below', 'Click the link in bio', or 'Save this post for later' to drive direct user action."
        })

    if question_count == 0:
        suggestions.append({
            "category": "Interaction",
            "impact": "High",
            "text": "End your post with a thought-provoking question (e.g. 'What is your experience with X?') to encourage comment thread engagement."
        })

    if len(hashtags) == 0:
        suggestions.append({
            "category": "Hashtags",
            "impact": "Medium",
            "text": "Include 2–4 targeted, niche hashtags (e.g., #SocialMediaStrategy #MarketingTips) to increase search discoverability."
        })
    elif len(hashtags) > 5:
        suggestions.append({
            "category": "Hashtags",
            "impact": "Medium",
            "text": "You are using more than 5 hashtags. Consider reducing to 3–5 high-relevance hashtags to prevent the caption from looking spammy."
        })

    if word_count < 25:
        suggestions.append({
            "category": "Content Depth",
            "impact": "Medium",
            "text": "Your post text is quite short (under 25 words). Adding more context or a storytelling angle often increases dwell time and engagement."
        })
    elif word_count > 250:
        suggestions.append({
            "category": "Formatting & Length",
            "impact": "Medium",
            "text": "The text is long (over 250 words). Break up dense paragraphs into bullet points or line breaks to improve mobile skimmability."
        })

    if len(mentions) == 0:
        suggestions.append({
            "category": "Mentions & Tagging",
            "impact": "Low",
            "text": "Consider tagging (@mentioning) relevant collaborators, brands, or industry creators to expand potential reach and quote-shares."
        })

    if emoji_count == 0:
        suggestions.append({
            "category": "Visual Formatting",
            "impact": "Low",
            "text": "Add 1–3 strategic emojis to create visual anchor points and make key lines stand out."
        })

    if sentences and len(sentences[0].split()) > 18:
        suggestions.append({
            "category": "Hook Quality",
            "impact": "High",
            "text": "Your opening line/hook is quite long. Shorten the first sentence (<12 words) to instantly grab scrolling users' attention."
        })

    return {
        "wordCount": word_count,
        "characterCount": char_count,
        "sentenceCount": sentence_count,
        "hashtagCount": len(hashtags),
        "hashtags": hashtags,
        "mentionCount": len(mentions),
        "mentions": mentions,
        "questionCount": question_count,
        "emojiCount": emoji_count,
        "hasCallToAction": has_cta,
        "sentiment": sentiment,
        "readabilityScore": round(flesch_score, 1),
        "readabilityLabel": readability_label,
        "engagementScore": engagement_score,
        "suggestions": suggestions,
    }


# -----------------------------------------------------------------------------
# Structured Google Gemini AI Service
# -----------------------------------------------------------------------------
def get_gemini_insights(text: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Queries Google Gemini API using structured prompting to return:
    1. Engagement Score (out of 10)
    2. Key Strengths
    3. Actionable Improvements
    4. Optimized Post Copy
    5. Recommended Hashtags
    """
    if not GEMINI_AVAILABLE or not api_key:
        return None

    prompt = f"""
You are an expert social media content strategist and copywriter.
Analyze the following social media post text and provide a comprehensive structured analysis with these EXACT 5 sections:

### 1. 📊 Engagement Score
Provide a numerical score out of 10 (e.g. **8.5 / 10**) evaluating hook effectiveness, call-to-action strength, readability, and viral potential. Include a 1-sentence summary justification.

### 2. 💪 Key Strengths
List 2-3 specific elements this post executes well (e.g. clear value proposition, relatable tone, strong hook).

### 3. 🎯 Actionable Improvements
List 3 practical, high-impact recommendations to improve comments, shares, and scroll-stopping power.

### 4. ✨ Optimized Post Copy
Provide a fully rewritten, ready-to-publish version of the post caption incorporating a captivating opening hook, line breaks for mobile readability, and a strong call-to-action.

### 5. #️⃣ Recommended Hashtags
Provide 5-8 highly relevant, targeted hashtags for maximum discoverability.

Post Caption to Analyze:
---
{text}
---
"""

    candidate_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]

    last_error = ""

    if not genai or not hasattr(genai, "Client"):
        return {"error": "Official google-genai SDK is not installed."}

    try:
        client = genai.Client(api_key=api_key)
        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if response and hasattr(response, "text") and response.text:
                    return {"content": response.text}
            except Exception as model_err:
                last_error = str(model_err)
                continue
    except Exception as err:
        last_error = str(err)

    return {"error": f"Gemini API execution failed: {last_error}"}


# -----------------------------------------------------------------------------
# Streamlit Interface & Interactive Workflow
# -----------------------------------------------------------------------------
def main():
    # Sidebar Setup
    with st.sidebar:
        st.title("⚙️ Settings & Samples")

        st.markdown("### 🔑 Optional Gemini AI")
        env_key = os.getenv("GEMINI_API_KEY", "")
        user_api_key = st.text_input(
            "Gemini API Key (Optional)",
            value=env_key,
            type="password",
            help="Unlocks AI structured analysis: Engagement Score (/10), Strengths, Improvements, Optimized Copy, & Hashtags."
        )

        st.divider()
        st.markdown("### 🧪 Load Sample Post")
        sample_choice = st.selectbox(
            "Test without uploading:",
            [
                "-- Select Sample --",
                "Sample 1: High Engagement Post",
                "Sample 2: Short Post without CTA/Hashtags",
                "Sample 3: Long Dense Post"
            ]
        )

        st.divider()
        st.markdown("### 📋 Submission Info")
        st.info(
            "**Unthinkable SE Assessment**\n"
            "- PDF Engine: PyMuPDF (fitz)\n"
            "- OCR Engine: Tesseract OCR + PIL (RGB / BytesIO)\n"
            "- AI Integration: Google Gemini Structured Output\n"
            "- Architecture: Streamlit MVP"
        )

    # Main Header
    st.markdown('<div class="main-header">Social Media Content Analyzer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Upload a PDF document or post image graphic, review & edit the extracted text, and analyze engagement potential.</div>',
        unsafe_allow_html=True
    )

    sample_texts = {
        "Sample 1: High Engagement Post": (
            "Are you struggling to get traction on your social media posts? 🚀\n\n"
            "Here are 3 simple tweaks you can make today to double your comment rate:\n"
            "1. Write short opening hooks.\n"
            "2. Ask a clear question at the end.\n"
            "3. Use 3-5 niche hashtags.\n\n"
            "Comment 'GROWTH' below and I'll send you our free checklist! #ContentMarketing #GrowthHacks #SocialMedia @GrowthHub"
        ),
        "Sample 2: Short Post without CTA/Hashtags": (
            "We just launched our new software feature today. It helps users manage their schedules faster."
        ),
        "Sample 3: Long Dense Post": (
            "In today's fast-paced digital ecosystem, business performance is inextricably tied to modern cloud software capabilities. "
            "Organizations that fail to modernize their legacy infrastructure often find themselves at a severe competitive disadvantage. "
            "We have spent the past eighteen months refactoring our microservice architecture, migrating to scalable containerized clusters, "
            "and establishing CI/CD automation pipelines across all developer teams. The results speak for themselves: deploy velocity has increased by 400 percent."
        )
    }

    # Initialize Session States for Text & Source Tracking
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""
    if "active_filename" not in st.session_state:
        st.session_state.active_filename = ""
    if "file_type_label" not in st.session_state:
        st.session_state.file_type_label = ""

    # Document Upload Dropzone
    uploaded_file = st.file_uploader(
        "Upload PDF document or Image file (PNG, JPG, JPEG)",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Maximum size: 10 MB. Text-based PDFs and scanned post graphics are supported."
    )

    # Handle Uploaded File with Spinners & Error Boundaries
    if uploaded_file is not None:
        filename = uploaded_file.name
        file_bytes = uploaded_file.getvalue()

        # Check File Size Limit (< 10 MB)
        if len(file_bytes) > 10 * 1024 * 1024:
            st.error("❌ File size exceeds the 10 MB limit. Please upload a smaller file.")
            return

        ext = filename.split(".")[-1].lower()

        # Process if filename changed or empty state
        if st.session_state.active_filename != filename:
            st.session_state.active_filename = filename

            with st.spinner("Extracting text from file..."):
                if ext == "pdf":
                    st.session_state.file_type_label = "PDF Document"
                    text, meta = extract_text_from_pdf(file_bytes)
                    if "error" in meta:
                        st.error(f"❌ {meta['error']}")
                        st.session_state.extracted_text = ""
                    elif meta.get("is_empty"):
                        st.warning(f"⚠️ {meta['warning']}")
                        st.session_state.extracted_text = ""
                    else:
                        st.session_state.extracted_text = text
                else:
                    st.session_state.file_type_label = f"Image ({ext.upper()})"
                    text, meta = extract_text_from_image(uploaded_file)
                    if "error" in meta:
                        st.error(f"❌ {meta['error']}")
                        st.session_state.extracted_text = ""
                    elif meta.get("is_empty"):
                        st.warning(f"⚠️ {meta['warning']}")
                        st.session_state.extracted_text = ""
                    else:
                        st.session_state.extracted_text = text

    elif sample_choice != "-- Select Sample --":
        if st.session_state.active_filename != sample_choice:
            st.session_state.active_filename = sample_choice
            st.session_state.file_type_label = "Sample Data"
            st.session_state.extracted_text = sample_texts[sample_choice]

    # Idle Welcome Guide if no text present
    if not st.session_state.extracted_text and uploaded_file is None and sample_choice == "-- Select Sample --":
        st.markdown("---")
        col_guide1, col_guide2 = st.columns(2)
        with col_guide1:
            st.markdown("""
            #### 📄 PDF Text Extraction
            - Extracts text from multi-page & single-page PDFs using **PyMuPDF (fitz)**.
            - Preserves line breaks & paragraph layout.
            - Detects scanned PDFs lacking text layers.
            """)
        with col_guide2:
            st.markdown("""
            #### 📷 Image OCR Recognition
            - Extracts text from PNG, JPG, and JPEG files using **Tesseract OCR**.
            - Preprocesses graphics using PIL (`RGB` mode, `io.BytesIO` seek reset).
            - Dynamic path detection for Windows (`C:\\Program Files\\Tesseract-OCR\\tesseract.exe`) and Linux.
            """)
        return

    # -------------------------------------------------------------------------
    # Editable Text Area & Trigger Section
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📝 Review & Edit Extracted Content")
    st.caption("You can review, fix any OCR typos, or edit the text below before running the content analysis.")

    edited_text = st.text_area(
        "Extracted Caption Text",
        value=st.session_state.extracted_text,
        height=220,
        help="Edit the caption text here if necessary."
    )

    col_btn1, col_btn2 = st.columns([0.25, 0.75])
    with col_btn1:
        run_analysis = st.button("🚀 Analyze Content", type="primary", use_container_width=True)

    # Automatically run analysis if text is available or button pressed
    if not edited_text.strip():
        st.warning("⚠️ Please provide text in the box above to trigger content analysis.")
        return

    # Trigger Analysis Section
    with st.spinner("Analyzing content & computing metrics..."):
        analysis = analyze_content(edited_text)

    effective_key = user_api_key or env_key
    gemini_result = None
    if effective_key:
        with st.spinner("Querying Google Gemini AI for structured insights..."):
            gemini_result = get_gemini_insights(edited_text, effective_key)

    st.success(f"✅ Active Source: **{st.session_state.active_filename or 'Custom Input'}** ({st.session_state.file_type_label or 'Text Box'})")

    # -------------------------------------------------------------------------
    # Heuristic Opportunity Score Banner
    # -------------------------------------------------------------------------
    score = analysis["engagementScore"]
    score_color = "#10B981" if score >= 70 else "#F59E0B" if score >= 45 else "#EF4444"

    st.markdown(f"""
    <div class="score-badge" style="background: linear-gradient(135deg, {score_color} 0%, #1E293B 100%);">
        <div style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.9;">Engagement Opportunity Score</div>
        <div style="font-size: 3rem; font-weight: 800; margin: 4px 0;">{score} <span style="font-size: 1.5rem;">/ 100</span></div>
        <div style="font-size: 0.85rem; opacity: 0.85;">Heuristic indicator based on structural post metrics (Hook, CTA, Questions, Hashtags, Readability)</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-box">
        💡 <b>Disclaimer:</b> The Engagement Opportunity Score is a heuristic indicator based on formatting best practices. It is not a platform performance prediction.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation Tabs
    tab_ai, tab_overview, tab_insights, tab_suggestions = st.tabs([
        "🤖 Google Gemini AI Analysis",
        "📊 Content Metrics",
        "💡 Formatting Insights",
        "🎯 Heuristic Suggestions"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: GOOGLE GEMINI STRUCTURED AI ANALYSIS
    # -------------------------------------------------------------------------
    with tab_ai:
        st.markdown("### 🤖 Google Gemini AI Content Analysis")

        if not effective_key:
            st.info(
                "🔒 **Unlock Gemini AI Analysis**\n\n"
                "Enter your Gemini API key in the sidebar settings to generate a structured AI assessment including:\n"
                "1. **Engagement Score** (out of 10)\n"
                "2. **Key Strengths**\n"
                "3. **Actionable Improvements**\n"
                "4. **Optimized Post Copy**\n"
                "5. **Recommended Hashtags**"
            )
        else:
            if gemini_result and "content" in gemini_result:
                st.markdown(gemini_result["content"])
            elif gemini_result and "error" in gemini_result:
                st.error(f"❌ {gemini_result['error']}")

    # -------------------------------------------------------------------------
    # TAB 2: CONTENT METRICS
    # -------------------------------------------------------------------------
    with tab_overview:
        st.markdown("### 📈 Quantitative Content Metrics")

        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analysis['wordCount']}</div>
                <div class="metric-label">Words</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analysis['characterCount']}</div>
                <div class="metric-label">Characters</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analysis['sentenceCount']}</div>
                <div class="metric-label">Sentences</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        m_col4, m_col5, m_col6 = st.columns(3)
        with m_col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analysis['hashtagCount']}</div>
                <div class="metric-label">Hashtags</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analysis['mentionCount']}</div>
                <div class="metric-label">Mentions</div>
            </div>
            """, unsafe_allow_html=True)
        with m_col6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{analysis['questionCount']}</div>
                <div class="metric-label">Questions</div>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 3: FORMATTING INSIGHTS
    # -------------------------------------------------------------------------
    with tab_insights:
        c1, c2, c3 = st.columns(3)

        with c1:
            cta_status = "Detected ✅" if analysis['hasCallToAction'] else "Missing ❌"
            st.info(f"**Call to Action:** {cta_status}")

        with c2:
            st.info(f"**Sentiment Tone:** {analysis['sentiment']}")

        with c3:
            st.info(f"**Readability:** {analysis['readabilityLabel']} ({analysis['readabilityScore']} Score)")

        st.markdown("---")

        col_hash, col_men = st.columns(2)
        with col_hash:
            st.markdown("#### # Detected Hashtags")
            if analysis['hashtags']:
                st.write(" ".join([f"`{h}`" for h in analysis['hashtags']]))
            else:
                st.caption("No hashtags detected in the text.")

        with col_men:
            st.markdown("#### @ Detected Mentions")
            if analysis['mentions']:
                st.write(" ".join([f"`{m}`" for m in analysis['mentions']]))
            else:
                st.caption("No mentions (@) detected in the text.")

    # -------------------------------------------------------------------------
    # TAB 4: HEURISTIC ENGAGEMENT SUGGESTIONS
    # -------------------------------------------------------------------------
    with tab_suggestions:
        st.markdown("### 💡 Actionable Structural Suggestions")

        suggestions = analysis['suggestions']
        if not suggestions:
            st.success("🎉 Excellent job! Your post adheres to all key social media engagement best practices.")
        else:
            for s in suggestions:
                impact_class = f"suggestion-{s['impact'].lower()}"
                st.markdown(f"""
                <div class="suggestion-card {impact_class}">
                    <span style="font-weight: 700; color: #1E293B;">[{s['category']}]</span>
                    <span style="float: right; font-size: 0.8rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; background: #F3F4F6;">Impact: {s['impact']}</span>
                    <p style="margin-top: 6px; margin-bottom: 0; color: #374151;">{s['text']}</p>
                </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
