# 🚨 RESPOND

**Multimodal Disaster Response Coordination System using Qdrant as Evolving Situational Memory**

*Convolve 4.0 | Qdrant MAS Track*

---

## 🎯 What is RESPOND?

RESPOND transforms chaotic disaster reports into prioritized, actionable intelligence. During emergencies, reports flood in from social media, sensors, and calls. RESPOND ingests, understands, prioritizes, and evolves—helping responders save lives faster.

**Key Innovation:** Unlike static databases, RESPOND treats incidents as *evolving memories*—they update, reinforce, and decay over time without re-embedding vectors.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Hybrid Search** | Semantic + geo + temporal + status filters |
| 🧠 **Memory Evolution** | Incidents transition: pending → acknowledged → resolved |
| 📊 **Confidence Reinforcement** | Multi-source verification boosts confidence |
| ⏱️ **Time Decay** | Fresh incidents automatically prioritized |
| 🎯 **Action Recommendations** | Evidence-grounded operational decisions |
| 🖼️ **Image & Audio** | Multimodal support (CLIP & Whisper) |

---

## � Deliverables & Reproducibility

This project is designed to be **fully reproducible** and **end-to-end runnable**.

### 🛠️ Prerequisites
- **Python 3.10+** installed
- **Qdrant** (Vector Database) - Running via Docker (Local) OR Cloud (Free Tier)
- **Git**

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/bytebender77/RESPOND.git
cd RESPOND
```

### Step 2: Create Virtual Environment

A virtual environment keeps dependencies isolated from your system Python.

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
# venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs `fastapi`, `uvicorn`, `qdrant-client`, `sentence-transformers` (Text), `whisper` (Audio), and `CLIP` (Images).

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory.

**Option A: Local Qdrant (Docker)**
If you have Docker installed, this is the easiest way.
```bash
docker run -p 6333:6333 qdrant/qdrant
```
Then your `.env` file can be:
```env
QDRANT_URL=http://localhost:6333
LOG_LEVEL=INFO
```

**Option B: Qdrant Cloud (Free Tier)**
1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io/).
2. Create a free cluster -> Get **URL** and **API Key**.
3. Update `.env`:
```env
QDRANT_URL=https://your-cluster-url.qdrant.io
QDRANT_API_KEY=your-api-key-here
```

---

## ▶️ Running the Application

### Step 1: Start the Backend API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
It will run at **http://localhost:8000**.
Visit **http://localhost:8000/docs** to explore the interactive API documentation.

### Step 2: Initialize Qdrant Collections

Open a **new terminal** (keep API running) and run:
```bash
curl http://localhost:8000/setup
```
*Expected output: `{"status":"ok","collections":{...}}`*

### Step 3: Start the Frontend Dashboard

You can simply open `frontend_basic/index.html` in your browser, or for a better experience:

```bash
cd frontend_basic
python3 -m http.server 3000
# or if you have 'serve' installed: npx serve
```
Visit **http://localhost:3000**.

---

## ☁️ Deployment

We have specific guides for deploying to the cloud:
- **Backend**: Render (using `render.yaml`)
- **Frontend**: Vercel

👉 **[Read the Deployment Guide](DEPLOYMENT_GUIDE.md)** for detailed cloud instructions.

---

## 🎮 How to Test (Demo Flow)

1. **Quick Start**: Check the **[Demo Files Index](demo/DEMO_FILES_INDEX.md)** for comprehensive testing resources.
2. **Ingest Incident**:
   - Go to **Ingest** tab in the frontend.
   - Text: "Massive fire reported at Central Market, people trapped."
   - Click "Submit".
2. **Search**:
   - Go to **Search** tab.
   - Query: "fire near market".
   - You will see your incident.
3. **Reinforce (Audio)**:
   - Go to **Media** tab.
   - Use the Incident ID from step 1.
   - Upload an audio file (e.g., voice recording saying "The fire is spreading to the west wing").
   - Watch the confidence score increase!
4. **Action Recommendations**:
   - Go to **Actions** tab.
   - Get AI-driven recommendations based on the incidents.

---

## 📁 Project Structure

```
respond/
├── api/                    # FastAPI routes
├── config/                 # Configuration & Settings
├── src/
│   ├── embeddings/        # Text (MiniLM) & Image (CLIP) embedders
│   ├── audio/             # Whisper transcriber
│   ├── ingestion/         # Incident processing pipeline
│   ├── memory/            # Evolution, decay, reinforcement logic
│   ├── search/            # Hybrid search implementation
│   └── qdrant/            # Database client
├── frontend_basic/        # Dashboard UI (HTML/CSS/JS)
├── docs/                  # Technical documentation
└── requirements.txt       # Dependencies
```

---

## � Documentation Links
- **[Judge's Guide](JUDGE_GUIDE.md)** - Simplified run instructions.
- **[Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md)** - Deep dive into architecture.
