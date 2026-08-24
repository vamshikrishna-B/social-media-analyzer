# Social Media Content Analyzer 🚀

An end-to-end web application built with **Streamlit, PyMuPDF, Tesseract OCR, Pillow, and Google Gemini AI** for analyzing social media content, extracting text from PDF documents and images, evaluating engagement potential, and generating actionable content improvements.

## 🔗 GitHub Repository

**Repository:**
https://github.com/vamshikrishna-B/social-media-analyzer/tree/main/social-media-content-analyzer-main

---

## 📌 Project Overview

The **Social Media Content Analyzer** is designed to help users evaluate and improve social media content before publishing.

Users can upload a social media content draft as a **PDF document or image**. The application extracts the text, allows the user to review and edit it, and then performs both **rule-based analysis and AI-powered evaluation**.

The system provides engagement-related metrics along with AI-generated suggestions for improving the content.

---

## 📐 Approach & Architecture

The application follows a multi-stage content analysis pipeline.

### 1. Ingestion & Validation

The application accepts:

* PDF documents
* PNG images
* JPG/JPEG images

Uploaded files are validated before processing.

Image files are handled using `io.BytesIO` and converted to RGB format using Pillow when required.

### 2. Text Extraction

For PDF documents, **PyMuPDF (`pymupdf`)** is used to extract text page by page.

For image files, **Tesseract OCR** is used through `pytesseract` to recognize text from the image.

The extracted text is then displayed in an editable text area so users can correct any extraction or OCR errors.

### 3. Content Analysis

The extracted content is analyzed using two approaches.

#### Deterministic Analysis

The application calculates metrics such as:

* Word count
* Character count
* Sentence count
* Hashtag count
* Mention count
* Question count
* CTA detection
* Readability
* Sentiment
* Engagement Opportunity Score

#### AI-Based Analysis

Google Gemini AI is used to generate structured insights including:

* Engagement Score
* Key Strengths
* Actionable Improvements
* Optimized Post Copy
* Recommended Hashtags

---

## ✨ Core Features

### 📄 Document & Image Upload

Supports:

* `.pdf`
* `.png`
* `.jpg`
* `.jpeg`

### 🔍 PDF Text Extraction

Uses **PyMuPDF** to extract text from PDF documents while preserving the basic structure of the content.

### 🖼️ OCR Image Recognition

Uses **Tesseract OCR** through `pytesseract` to extract text from social media graphics and other images.

### ✏️ Editable Extracted Text

The extracted content is displayed in an editable text area, allowing users to review and correct the text before analysis.

### 📊 Deterministic Content Metrics

The application calculates:

* Words
* Characters
* Sentences
* Hashtags
* Mentions
* Questions
* Emoji density
* Readability
* Sentiment polarity
* Engagement Opportunity Score

### 🤖 Google Gemini AI Analysis

The application integrates Google Gemini AI to provide:

* 📊 Engagement Score
* 💪 Key Strengths
* 🎯 Actionable Improvements
* ✨ Optimized Post Copy
* #️⃣ Recommended Hashtags

---

## 🛠️ Tech Stack

| Technology                       | Purpose                        |
| -------------------------------- | ------------------------------ |
| **Python**                       | Main programming language      |
| **Streamlit**                    | Web application framework      |
| **PyMuPDF**                      | PDF text extraction            |
| **Tesseract OCR**                | Optical character recognition  |
| **Pytesseract**                  | Python interface for Tesseract |
| **Pillow (PIL)**                 | Image processing               |
| **Google Gemini / google-genai** | AI-powered content analysis    |
| **io.BytesIO**                   | In-memory file processing      |

---

## ⚙️ Local Setup

### 1. Prerequisites

Install:

* Python 3.10 or higher
* Git
* Tesseract OCR

### 2. Clone Repository

```bash
git clone https://github.com/vamshikrishna-B/social-media-analyzer.git
cd social-media-analyzer/social-media-content-analyzer-main
```

### 3. Create Virtual Environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Gemini API

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in the browser at:

```text
http://localhost:8501
```

---

## 🔤 Tesseract OCR Installation

### Windows

Install Tesseract OCR and ensure it is available at a standard location such as:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

The application can detect Tesseract from standard Windows locations and the system `PATH`.

### Linux

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

---

## 🔑 Environment Variables

The application uses the following environment variable for Gemini AI:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Do not commit API keys to the repository.

Add the following to `.gitignore`:

```text
.env
.venv/
__pycache__/
```

---

## 🔄 Application Workflow

```text
Upload PDF / Image
        ↓
File Validation
        ↓
Text Extraction
        ↓
    ┌───────────────┐
    │               │
    ▼               ▼
PDF → PyMuPDF    Image → Tesseract OCR
    │               │
    └───────┬───────┘
            ▼
     Extracted Text
            ↓
    User Reviews/Edits
            ↓
   Deterministic Metrics
            ↓
      Gemini AI Analysis
            ↓
   ┌──────────────────────┐
   │ Engagement Score     │
   │ Key Strengths        │
   │ Improvements         │
   │ Optimized Post Copy  │
   │ Recommended Hashtags │
   └──────────────────────┘
```

---

## 📝 Technical Assessment Requirements

| Requirement             | Implementation  |
| ----------------------- | --------------- |
| PDF Document Upload     | ✅ Implemented   |
| Image Upload            | ✅ Implemented   |
| PDF Text Extraction     | ✅ PyMuPDF       |
| OCR Technology          | ✅ Tesseract OCR |
| Editable Text Area      | ✅ Streamlit     |
| AI-Based Analysis       | ✅ Google Gemini |
| Deterministic Metrics   | ✅ Implemented   |
| Engagement Analysis     | ✅ Implemented   |
| Content Recommendations | ✅ Implemented   |

---

## 🚀 Future Improvements

* Platform-specific content recommendations
* Support for additional document formats
* Historical content comparison
* Content performance dashboard
* Multi-language support
* User authentication
* Advanced engagement prediction
* Social media platform integrations

---

## 🏆 License

MIT License.
