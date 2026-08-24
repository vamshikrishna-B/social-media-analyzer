# Social Media Content Analyzer 🚀
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://social-media-content-analyzer-shaik.streamlit.app/)

- **Hosted Application URL:** [Live Demo](https://social-media-content-analyzer-shaik.streamlit.app/)

An end-to-end, production-ready web application built with **Streamlit**, **PyMuPDF**, **Tesseract OCR**, and **Google Gemini AI** (`google-genai`) for analyzing social media content drafts, extracting post text, evaluating engagement potential, and generating actionable optimizations.

---

## 🔗 Live Application Demo
-**Hosted Application URL:** [Live Demo](https://social-media-content-analyzer-shaik.streamlit.app/)
- **GitHub Repository**: [https://github.com/SHAIK7230/social-media-content-analyzer.git](https://github.com/SHAIK7230/social-media-content-analyzer.git)

---

## 📐 Approach & Architecture

The **Social Media Content Analyzer** implements a resilient, multi-stage content intelligence pipeline:

1. **Ingestion & Validation**: Uploaded PDF documents and post image graphics (PNG, JPG, JPEG) are validated for file format and size (<10MB). Image streams are buffered via `io.BytesIO` with pointer resets (`seek(0)`) and converted to `RGB`.
2. **Text Extraction**: PDF files are parsed page-by-page using PyMuPDF (`pymupdf`), maintaining text layout and line structures. Image graphics undergo Optical Character Recognition via Tesseract OCR (`pytesseract`), utilizing dynamic path resolution across Windows (`C:\Program Files\Tesseract-OCR\tesseract.exe`) and Linux environments.
3. **Analysis Pipeline**: Extracted text is presented in an editable text area for manual review before triggering analysis. The system executes a dual-tier evaluation:
   - *Deterministic Heuristics*: Calculates word/char counts, hashtags (`#`), mentions (`@`), questions (`?`), CTAs, readability, sentiment, and an Engagement Opportunity Score (0–100).
   - *Structured AI Evaluation*: Queries Google Gemini AI (`google-genai`) to generate structured insights: Engagement Score (/10), Key Strengths, Actionable Improvements, Optimized Post Copy, and Recommended Hashtags.

---

## ✨ Core Features Breakdown

- **Document & Image Ingestion**: Drag-and-drop or file browser support for `.pdf`, `.png`, `.jpg`, `.jpeg` files up to 10 MB.
- **PDF Layout Extraction**: High-performance text parsing using **PyMuPDF** (`pymupdf`) preserving paragraph indents and line breaks.
- **OCR Image Recognition**: Optical character recognition for scanned image graphics using **Tesseract OCR** (`pytesseract`) with PIL `RGB` preprocessing and `io.BytesIO` buffer resets.
- **Editable Text Interface**: Review, edit, or correct OCR typos in an interactive text area before triggering content analysis.
- **Deterministic Metrics Engine**: Calculates quantitative metrics (words, chars, sentences, hashtags, mentions, questions, emoji density, Flesch Reading Ease score, sentiment polarity).
- **Structured Google Gemini AI Evaluation**: Queries Google Gemini API (`google-genai`) to deliver structured insights:
  - 📊 **Engagement Score** (out of 10)
  - 💪 **Key Strengths**
  - 🎯 **Actionable Improvements**
  - ✨ **Optimized Post Copy**
  - #️⃣ **Recommended Hashtags**

---

## 🛠️ Tech Stack

- **Frontend & Web Framework**: [Streamlit](https://streamlit.io/)
- **PDF Parsing**: [PyMuPDF](https://pymupdf.readthedocs.io/) (`pymupdf`)
- **OCR Engine**: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) via `pytesseract`
- **Image Preprocessing**: [Pillow](https://python-pillow.org/) (`PIL`)
- **AI Integration**: [Google GenAI SDK](https://github.com/googleapis/python-genai) (`google-genai`)
- **Language & Runtime**: Python 3.10+

---

## ⚙️ Local Setup and Run Instructions

### 1. Prerequisites
- Python 3.10 or higher
- Git
- Tesseract OCR (installed locally on Windows or via package manager on Linux/macOS)

### 2. Clone Repository
```bash
git clone https://github.com/your-username/social-media-content-analyzer.git
cd social-media-content-analyzer
```

### 3. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Application Locally
```bash
streamlit run app.py
```

The application will launch automatically in your web browser at `http://localhost:8501`.

---

## 🔤 Tesseract OCR Installation

### Windows
1. Download installer from [UB-Mannheim Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install to default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`.
3. `app.py` dynamically auto-detects Tesseract at standard Windows paths and system `PATH`.

### Linux (Ubuntu/Debian) / Streamlit Cloud
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```
*(Streamlit Cloud automatically installs Tesseract via `packages.txt`).*

---

## 🔑 Environment Variables (Optional)

To enable Google Gemini AI analysis locally, create a `.env` file or pass in sidebar:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 📝 Technical Assessment Requirements Matrix

| Requirement | Implementation Status | Location / Details |
| ----------- | -------------------- | ------------------ |
| **PDF Document Upload** | ✅ Implemented & Verified | `app.py` (`st.file_uploader`) |
| **Image Upload (PNG/JPG)** | ✅ Implemented & Verified | `app.py` (`st.file_uploader`) |
| **PDF Parsing Layout** | ✅ Implemented & Verified | PyMuPDF (`pymupdf`) page extraction |
| **OCR Technology** | ✅ Implemented & Verified | Tesseract OCR + PIL (`RGB` / `BytesIO`) |
| **Editable Text Area** | ✅ Implemented & Verified | `st.text_area` review before analysis |
| **Structured AI Insights** | ✅ Implemented & Verified | Google Gemini (`google-genai`) 5-section evaluation |
| **Deterministic Metrics** | ✅ Implemented & Verified | Words, Chars, Sentences, Hashtags, Mentions, Readability |
| **Documentation** | ✅ Implemented & Verified | Complete `README.md` with <200 word approach write-up |

---

## 🏆 License

MIT License. Free for evaluation and assessment review.
