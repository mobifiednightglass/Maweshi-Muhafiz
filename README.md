# Maweshi Muhafiz |  مویشی محافظ 
**AI-powered livestock health companion for farmers — built in Urdu-first, for the field.**

## About the Project

**Maweshi Muhafiz** ("Livestock Guardian") is an AI-assisted livestock health tracking platform built for farmers to keep track of their animals and monitor their health with the help of a vision-based AI assistant.

A farmer photographs a sick animal, describes the symptoms (by typing **or speaking in Urdu**), and receives an AI generated preliminary health assessment in both **Urdu and English**, complete with urgency level, safe next steps, and when the case looks serious, an automatic emergency flag. Every animal gets a running health record: assessment history, vaccination/deworming reminders, a vet-ready case summary a doctor can review in seconds, and a simplified "health card" that can be shared when selling the animal.

The interface defaults to **Urdu (RTL layout)** and can be switched to **English** at any time, so the same product serves both a farmer in the field and a veterinarian reviewing the case later.

---

## Key Features

### 🐄 Animal Records (CRUD)
- Full create / read / update / delete for animal profiles: name, type, breed, gender, age, weight, color, health status, region, and notes; each scoped to the logged-in owner.

### 🩺 AI Health Assessment
- Upload a photo of the animal plus a symptom description and get a **structured AI diagnosis** (possible conditions, explanation, confidence note, urgency level) 
- **Image quality gate**: photos are checked locally for blur/darkness/resolution *before* being sent to the AI, so farmers get instant, cheap feedback instead of waiting on a bad request.
- The model itself also rejects images that are **too blurry to analyze** or that **don't contain an animal at all**, cleaning up the pending record automatically.

### 🎙️ Urdu Voice Symptom Reporting
- Farmers can **record a voice note in Urdu** describing the animal's symptoms instead of typing.
- The audio is transcribed to Urdu text, then fed into the exact same assessment pipeline as typed symptoms.
- The AI's recommended safe next steps can be **read back out loud in Urdu**, turning the guidance into playable audio for low-literacy users.

### 🚩 Red-Flag Emergency Detection
- A fast, local **keyword based safety net** scans symptom text for emergency signs, independent of and running alongside the AI call, so a farmer still gets an emergency warning even if the AI is slow or fails.
- Combined with the AI's own urgency judgment, this drives an `is_red_flag` marker shown prominently in the UI.

### 📋 Health History & Assessment Comparison
- Every assessment is stored against the animal, giving a full **health timeline**.
- A dedicated **compare view** lets a farmer place two assessments (e.g. "before" and "after" treatment) side by side.

### 🩹 Vet-Ready Case Summary
- One click compiles an assessment (symptoms, images, diagnosis, red-flag reasons) plus an animal snapshot into a clean, shareable summary a veterinarian can review quickly 

### 📇 Health Passport & Buyer-Facing Health Card
- **Health Passport**: a complete bundle for one animal; profile, full assessment history, linked vet summaries, and reminders split into upcoming/past.
- **Health Card**: an intentionally *redacted*, simplified public-facing view (identity + preventive care standing + whether there's an active warning) designed to be shown to a **buyer** without exposing private diagnosis details.

### ⏰ Preventive Care Reminders
- Create and track vaccination, deworming, and routine check up reminders per animal, with due dates.

### 🔐 Authentication
- JWT-based signup/login, password hashing via, and a `require_auth` middleware that protects every data route and scopes all data to the requesting user (ownership is verified on every animal/assessment/reminder lookup).

### 🌐 Bilingual, RTL-First UI
- Urdu is the **default language** with proper **RTL layout**; a language toggle switches to English (LTR) instantly, with the choice persisted in the browser.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Python 3.10+, Flask 3 (Application Factory + Blueprints) |
| **Database** | MongoDB Atlas (via `pymongo`), GridFS for image storage |
| **Authentication** | JWT (`PyJWT`), password hashing (`werkzeug.security`) |
| **AI — Vision** | Google Gemini (`google-genai`), multimodal image + text diagnosis |
| **AI — Voice** | Google Gemini speech-to-text (Urdu transcription) & text-to-speech (Urdu narration) |
| **Image Processing** | OpenCV (`opencv-python-headless`), NumPy — local blur/darkness/resolution checks |
| **Frontend** | Vanilla HTML5, CSS3, JavaScript (no framework/build step) |
| **Testing** | `pytest`, `pytest-flask`, plus a standalone end-to-end script |
| **CORS** | `Flask-Cors` |

---

## Project Structure

```
Maweshi-Muhafiz/
├── backend/                          # Flask REST API
│   ├── app/
│   │   ├── __init__.py               # Application factory — registers blueprints,
│   │   │                             # wires services/repositories (DI container)
│   │   ├── config.py                 # Env-based config (Development/Testing/Production)
│   │   ├── models/                   # Schemaless (MongoDB) — placeholder for future models
│   │   ├── routes/                   # One Flask Blueprint per feature
│   │   │   ├── auth.py               # POST /auth/signup, /auth/login, GET /auth/me
│   │   │   ├── animals.py            # Animal CRUD
│   │   │   ├── health_assessments.py # AI diagnosis, voice symptoms, images, speech, compare
│   │   │   ├── vet_summary.py        # Vet-ready case summary
│   │   │   ├── passport.py           # Animal health passport (full bundle)
│   │   │   ├── health_card.py        # Buyer-facing redacted health card
│   │   │   ├── reminders.py          # Preventive-care reminders CRUD
│   │   │   ├── insights.py           # Regional health insights
│   │   │   └── health.py             # GET /health — liveness check
│   │   ├── services/                 # Business logic, decoupled from routes
│   │   │   ├── vision_provider.py    # GeminiVisionProvider — AI diagnosis + safe fallback
│   │   │   ├── voice_service.py      # Gemini STT/TTS for Urdu voice notes
│   │   │   ├── red_flag_service.py   # Keyword-based emergency detection
│   │   │   ├── next_steps_service.py # Server-generated safe-next-steps guidance
│   │   │   ├── image_quality.py      # OpenCV pre-upload image quality checks
│   │   │   ├── image_storage.py      # GridFS-backed image storage
│   │   │   ├── animal_service.py     # Animal CRUD business logic
│   │   │   ├── auth_service.py       # Signup/login, JWT issuance
│   │   │   ├── health_assessment_service.py
│   │   │   ├── health_card_service.py
│   │   │   ├── passport_service.py
│   │   │   ├── insight_service.py
│   │   │   ├── reminder_service.py
│   │   │   └── *_validation.py       # Standalone input validators per resource
│   │   ├── repositories/             # Data-access layer — see "Architecture" below
│   │   ├── utils/
│   │   │   └── auth_middleware.py    # @require_auth JWT decorator
│   ├── tests/                        # pytest suite (one file per feature)
│   ├── e2e_test.py                   # Standalone end-to-end script against a running server
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py                        # Entry point — `python run.py`
│
├── frontend/                         # Static multi-page web client (no build step)
│   ├── index.html                    # Landing page
│   ├── auth.html                     # Login / signup
│   ├── dashboard.html                # Animal records dashboard
│   ├── animal-profile.html           # Single animal profile + new assessment
│   ├── assessment-result.html        # AI diagnosis result view
│   ├── assessment-compare.html       # Side-by-side assessment comparison
│   ├── health-history.html           # Full assessment timeline for an animal
│   ├── health-passport.html          # Complete animal health bundle
│   ├── health-card.html              # Redacted buyer-facing health card
│   ├── vet-summary.html              # Vet-ready case summary view
│   ├── preventive-care.html          # Reminders (vaccination/deworming/check-ups)
│   └── static/
│       ├── css/                      # One stylesheet per page + shared styles.css
│       ├── js/                       # One script per page + shared app.js, auth.js, i18n.js
│       └── images/                   # Logo and hero imagery
│
└── voice_scripts/                    # Standalone scripts used to prototype/test the voice
    ├── speech_to_text.py             # feature (Gemini Urdu STT) independently of the API
    ├── text_to_speech.py             # (Gemini Urdu TTS)
    └── sample_urdu.txt / sample_output.wav / WhatsApp Audio sample — test fixtures
```

---

## Architecture

The health assessment pipeline is the heart of the project. Both the **typed-symptoms** flow and the **Urdu voice-note** flow funnel into it:

```
 Farmer input                                              Result
┌────────────────┐   ┌───────────────┐   ┌───────────────────────────────┐
│ Photo + symptoms│──▶│ 1. Validate    │──▶│ 5. Gemini vision assessment   │
│  (typed) OR      │   │    symptoms    │   │    (image + symptoms → JSON) │
│ Voice note (Urdu)│──▶│ 2. OpenCV image│   │    with retry on malformed   │
│  → Gemini STT    │   │    quality gate│   │    response, safe fallback   │
│  → Urdu transcript│  │ 3. Store image │   │    on any provider failure   │
└────────────────┘   │    (GridFS)    │   ├───────────────────────────────┤
                       │ 4. Red-flag    │   │ 6. Reject if AI flags:       │
                       │    keyword scan│   │    image_too_blurry OR       │
                       └───────────────┘   │    contains_animal = false   │
                                             ├───────────────────────────────┤
                                             │ 7. Merge keyword + AI        │
                                             │    urgency → final red-flag  │
                                             │ 8. Attach server-generated    │
                                             │    safe-next-steps (EN + UR) │
                                             │ 9. Persist final record       │
                                             └───────────────────────────────┘
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- A MongoDB Atlas connection string (or run in `testing` mode with in memory repositories)
- A Google Gemini API key (for vision assessment and voice features)

### 1. Clone the repository
```bash
git clone https://github.com/mobifiednightglass/Maweshi-Muhafiz.git
cd Maweshi-Muhafiz
```

### 2. Backend setup
```bash
cd backend
python -m venv venv

# Activate the virtual environment
source venv\bin\activate        # macOS / Linux
source venv\Scripts\activate    # Windows (Git Bash)

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net
MONGODB_DB_NAME=maweshi_muhafiz
GEMINI_API_KEY=your-gemini-api-key
```

### 3. Run the backend
```bash
python run.py
```
The API starts at `http://127.0.0.1:5000`. Verify it's up:
```bash
curl http://127.0.0.1:5000/api/health
```

### 4. Run the frontend
The frontend is static HTML/CSS/JS with no build step. Serve the `frontend/` folder with any static file server, e.g.:
```bash
cd frontend
python -m http.server 5500
```
Then open `http://127.0.0.1:5500/index.html`. 

---

## Testing

The backend ships with a full `pytest` suite covering validation, auth protection, every route group, and individual services (image quality, red-flag detection, next-steps generation), all running against **in-memory repositories** so no live database is required.

```bash
cd backend
pytest          # run the suite
pytest -v       # verbose output
```

An additional standalone script, `backend/e2e_test.py`, exercises the API end-to-end against a running server instance.

---

## Team

- **Ayesha Abbas** — Frontend & UI
- **Hafsa Nazir** — Core Backend & Diagnosis
- **Aila Siddiqui** — Extended Backend
- **Alishba Azmat** — QA, Documentation & Reliability