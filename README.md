# 🚨 RESPOND - AI Disaster Coordination System

**Convolve 4.0 | Qdrant MAS Track**

RESPOND transforms chaotic disaster reports into prioritized, actionable intelligence. It treats incidents as **evolving memories**—ingesting text, audio, and images to create a single, clear operating picture for responders.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Hybrid Search** | Semantic + Geo + Status + Time filtering |
| 🧠 **Memory Evolution** | Incidents transition statuses (Pending → Resolved) |
| 🔄 **Auto-Deduplication** | Merges similar reports (e.g., "Fire" vs "Blaze") |
| 🎙️ **Audio Reinforcement** | Verifies incidents using OpenAI Whisper (Audio-to-Text) |
| 🖼️ **Contextual Vision** | Searches images using CLIP (Text-to-Image) |
| 🚀 **Resource Deployment** | Dispatches units and tracks response lifecycle |

---

## 🛠️ Prerequisites

Ensure you have the following installed:

1.  **Python 3.10+**
2.  **Qdrant** (Vector Database) - [Cloud Free Tier](https://cloud.qdrant.io/) OR Local Docker
3.  **FFmpeg** (Required for Audio Processing)
    *   *Mac:* `brew install ffmpeg`
    *   *Windows:* `winget install ffmpeg`
    *   *Linux:* `sudo apt install ffmpeg`

---

## 🚀 Installation (Step-by-Step)

### 1. Clone & Setup Environment

```bash
git clone https://github.com/bytebender77/RESPOND.git
cd RESPOND

# Create Virtual Environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Configuration (.env)

Create a `.env` file in the root directory:

```env
# Database Configuration
QDRANT_URL=https://your-cluster-url.qdrant.io  # OR http://localhost:6333
QDRANT_API_KEY=your-api-key-here              # Leave empty if using local Docker

# API Settings
LOG_LEVEL=INFO
QDRANT_PREFIX=respond_
```

---

## ▶️ Running the Application

### Terminal 1: Backend API

Start the FastAPI server. It will handle ingestion, AI processing, and database interactions.

```bash
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
> API Docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### Terminal 2: Database Setup (One-Time)

Initialize the Qdrant collections with the correct vector configuration.

```bash
curl http://localhost:8000/setup
# Expected output: {"status":"ok", "collections": ...}
```

### Terminal 3: Frontend Dashboard

Serve the lightweight dashboard.

```bash
cd frontend_basic
python3 -m http.server 3000
```
> Dashboard available at: [http://localhost:3000](http://localhost:3000)

---

## ✅ Verification Checklist

From the Dashboard ([http://localhost:3000](http://localhost:3000)):

1.  **Data Ingestion:** Enter a text incident and submit. Ensure you see a green "Success" card.
2.  **Deduplication:** Submit a similar report. Ensure it says **"🔄 DEDUPLICATED"**.
3.  **Search:** Go to the Search tab and query your incident.
4.  **Audio:** Go to Media tab, upload an audio file. Ensure it says **"✅ Reinforcement Accepted"**.

---

## 📄 Documentation

*   **[Judge's Guide](JUDGE_GUIDE.md)**: Simplified instructions for evaluation.
*   **[Demo Scenarios](demo/DEMO_TEST_SCENARIOS.md)**: Copy-paste incidents for testing.
*   **[Video Script](VIDEO_DEMO_SCRIPT.md)**: Narration script for the demo video.
*   **[Technical Docs](docs/TECHNICAL_DOCUMENTATION.md)**: Architecture deep dive.
