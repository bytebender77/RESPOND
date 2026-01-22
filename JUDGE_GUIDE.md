# RESPOND - Judge's Run Guide

Welcome to **RESPOND** (Real-time Emergency System for Priority-Ordered Neighborhood Dispatch).
This guide will help you set up and run the system locally or deploy it to the cloud.

## 🚀 Quick Start (Local Run)

The easiest way to test RESPOND is to run it locally.

### Prerequisites
1. **Python 3.10+**
2. **Pip** (Python package manager)
3. **Qdrant** (Vector Database) - You can run this via Docker OR use a free cloud instance.

### Step 1: Clone & Setup
```bash
# Clone the repository
git clone https://github.com/bytebender77/RESPOND.git
cd RESPOND

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment
Create a `.env` file in the root directory.

**Option A: Local Qdrant (Docker)**
If you have Docker installed:
```bash
# Run Qdrant container
docker run -p 6333:6333 qdrant/qdrant
```
Then your `.env` file can be empty (defaults to localhost) or:
```env
QDRANT_URL=http://localhost:6333
LOG_LEVEL=INFO
```

**Option B: Qdrant Cloud (Free Tier)**
If you don't want to use Docker:
1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io/) (Free).
2. Create a **Cluster**.
3. Get your **Cluster URL** and **API Key**.
4. Create `.env`:
```env
QDRANT_URL=https://your-cluster-url.qdrant.io
QDRANT_API_KEY=your-api-key
```

### Step 3: Run the Backend
```bash
# Start the API server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
Visit `http://localhost:8000/docs` to see the Swagger UI.

### Step 4: Run the Frontend
The frontend is a simple static site.
1. Open `frontend_basic/index.html` in your browser.
   OR
2. Serve it with a simple underlying server (recommended):
```bash
cd frontend_basic
python3 -m http.server 3000
```
Then visit `http://localhost:3000`.

---

## ☁️ Deployment Guide (Render & Vercel)

If you prefer to judge the deployed version.

### 1. Backend (Render)
1. Fork this repo.
2. Go to [Render Dashboard](https://dashboard.render.com/).
3. Create a **New Blueprint Instance**.
4. Connect your repo. Render will use `render.yaml`.
5. **Environment Variables**:
   Render will ask for these because they are defined in `render.yaml` with `sync: false`.
   - `QDRANT_URL`: URL from Qdrant Cloud.
   - `QDRANT_API_KEY`: API Key from Qdrant Cloud.
   - `QDRANT_PREFIX`: `respond_` (default)
6. Deploy. Copy your backend URL (e.g., `https://respond-api.onrender.com`).

### 2. Frontend (Vercel)
1. Go to [Vercel](https://vercel.com).
2. Add New Project -> Import from GitHub.
3. Select `frontend_basic` as the **Root Directory**.
4. **Important**: Before deploying, you must tell the frontend where your backend is.
   - **Option A (Code Edit)**: Edit `frontend_basic/app.js` line 11:
     ```javascript
     : 'https://your-render-app-url.onrender.com'
     ```
     Push this change to GitHub.
   - **Option B (Env Var - Advanced)**: Use Vercel Environment Variables if you modify the code to read them (requires build step). Option A is easier for this static setup.
5. Deploy.

---

## 🧪 Testing the System

1. **Ingest Incident**:
   - Go to "Ingest" tab.
   - Enter text: "Fire reported at Central Park near the lake."
   - Click "Submit Incident".
2. **Search**:
   - Go to "Search" tab.
   - Query: "fire near water".
   - See semantic search results.
3. **Audio**:
   - Go to "Media" tab.
   - Enter Incident ID.
   - Upload an audio file (e.g., recording saying "The fire is spreading fast").
   - See it transcribe and reinforce confidence.
