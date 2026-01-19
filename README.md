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

---

## 🛠️ Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **Qdrant Cloud account** (free tier works) — [Sign up here](https://cloud.qdrant.io/)
- **Git** for cloning the repository

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/respond.git
cd respond
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

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` + `uvicorn` — API server
- `qdrant-client` — Vector database client
- `sentence-transformers` — Text embeddings
- `pydantic` — Data validation
- Other supporting libraries

### Step 4: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Now edit `.env` with your Qdrant credentials:

```env
# Get these from https://cloud.qdrant.io/
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your-api-key-here

# Other settings (defaults work fine)
QDRANT_PREFIX=respond_
LOG_LEVEL=INFO
```

**How to get Qdrant credentials:**
1. Go to [cloud.qdrant.io](https://cloud.qdrant.io/)
2. Create a free cluster
3. Copy the **URL** and **API Key** from the dashboard

---

## ▶️ Running the Application

### Step 1: Start the Backend API

```bash
uvicorn api.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process
```

The API is now running at **http://127.0.0.1:8000**

### Step 2: Initialize Qdrant Collections

Open a **new terminal** (keep the API running) and run:

```bash
curl http://127.0.0.1:8000/setup
```

Expected response:
```json
{"status":"ok","collections":{"created":["respond_situation_reports",...]}}
```

This creates the vector database collections needed for RESPOND.

### Step 3: Start the Frontend Dashboard

In another terminal:

```bash
cd frontend
python3 -m http.server 5500
```

Now open your browser: **http://127.0.0.1:5500**

---

## 🎮 Using RESPOND

### Option A: Use the Dashboard UI

1. Open **http://127.0.0.1:5500**
2. **Ingest Incident**: Fill the left form and click "Submit Incident"
3. **Search**: Enter a query like "fire emergency" and click "Search"
4. **Update Status**: Use dropdown on each card
5. **Recommend Actions**: Click "Recommend Actions" button

### Option B: Use the API Directly

**Ingest an incident:**
```bash
curl -X POST "http://127.0.0.1:8000/ingest/incident" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Building collapse near metro station, people trapped",
    "source_type": "call",
    "urgency": "critical",
    "zone_id": "zone-4",
    "location": {"lat": 28.6139, "lon": 77.2090}
  }'
```

**Search incidents:**
```bash
curl -X POST "http://127.0.0.1:8000/search/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "collapse trapped rescue",
    "limit": 10,
    "last_hours": 24
  }'
```

**Update status:**
```bash
curl -X PATCH "http://127.0.0.1:8000/memory/incident/<INCIDENT_ID>/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "acknowledged"}'
```

**Reinforce with evidence:**
```bash
curl -X POST "http://127.0.0.1:8000/memory/incident/<INCIDENT_ID>/reinforce" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "sensor",
    "text": "Seismic sensors confirm building collapse in zone-4"
  }'
```

**Get recommendations:**
```bash
curl -X POST "http://127.0.0.1:8000/recommend/actions" \
  -H "Content-Type: application/json" \
  -d '{"query": "emergency rescue", "limit": 5}'
```

---

## 🎬 Running the Disaster Simulator

To simulate live disaster events for demo purposes:

```bash
python3 scripts/simulate_disaster.py
```

This generates realistic incidents every 3 seconds:
```
[16:22:44] #1 | fire       | critical | zone-3 | ID: bca57afe...
[16:22:47] #2 | flood      | high     | zone-1 | ID: fd6e4f16...
[16:22:50] #3 | collapse   | critical | zone-4 | ID: ac9818d4...
```

Press `Ctrl+C` to stop.

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/setup` | Initialize collections |
| `POST` | `/ingest/incident` | Ingest new incident |
| `POST` | `/search/incidents` | Hybrid semantic search |
| `PATCH` | `/memory/incident/{id}/status` | Update status |
| `POST` | `/memory/incident/{id}/reinforce` | Add corroborating evidence |
| `POST` | `/recommend/actions` | Get action recommendations |
| `DELETE` | `/reset` | Clear all data |

**Interactive API Docs:** http://127.0.0.1:8000/docs

---

## 📁 Project Structure

```
respond/
├── api/                    # FastAPI routes
│   ├── main.py            # App entry point
│   └── routes/            # Endpoint handlers
├── config/                 # Configuration
│   ├── settings.py        # Environment settings
│   └── qdrant_config.py   # Qdrant constants
├── src/
│   ├── embeddings/        # Text embedder (MiniLM-L6)
│   ├── evidence/          # Evidence tracer
│   ├── ingestion/         # Incident ingester
│   ├── memory/            # Evolution, decay, reinforcement
│   ├── qdrant/            # Client & collections
│   ├── recommendation/    # Action recommender
│   └── search/            # Hybrid search & filters
├── scripts/               # Simulation scripts
├── frontend/              # Dashboard UI
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
└── .env.example          # Environment template
```

---

## 🔧 Troubleshooting

### "Connection refused" error
- Make sure the API is running: `uvicorn api.main:app --reload`
- Check if port 8000 is available

### "Cannot connect to Qdrant"
- Verify your `.env` has correct `QDRANT_URL` and `QDRANT_API_KEY`
- Check if your Qdrant cluster is running at [cloud.qdrant.io](https://cloud.qdrant.io/)

### "Module not found" error
- Make sure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Reset all data
```bash
curl -X DELETE http://127.0.0.1:8000/reset
```

---

## 🏗️ Tech Stack

| Component | Technology |
|-----------|------------|
| Vector Database | Qdrant Cloud |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Backend | FastAPI + Pydantic |
| Frontend | Vanilla HTML/CSS/JS |
| Python | 3.10+ |

---

## 📄 Documentation

- [Final Report](docs/FINAL_REPORT.md) — Technical documentation
- [Architecture](docs/architecture.md) — System design details
- [Submission Checklist](SUBMISSION_CHECKLIST.md) — Demo preparation

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License

---

*Built with ❤️ for Convolve 4.0 | Qdrant MAS Track*
