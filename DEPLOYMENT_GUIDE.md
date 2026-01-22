# Deployment Guide

## 1. GitHub Repository
Ensure all your latest changes are pushed to GitHub.
- Repository: https://github.com/bytebender77/RESPOND

## 2. Backend Deployment (Render)
The backend is configured to use `render.yaml` for infrastructure as code, or you can set it up manually.

### Option A: Blueprints (Recommended)
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** -> **Blueprint**.
3. Connect your GitHub repository `bytebender77/RESPOND`.
4. Render will automatically detect `render.yaml` and set up the `respond-api` service.
5. **Environment Variables**: You will be prompted to enter values for:
   - `QDRANT_URL`: Your Qdrant Cloud URL.
   - `QDRANT_API_KEY`: Your Qdrant API Key.
6. Click **Apply**.

### Option B: Manual Web Service
1. Go to **New +** -> **Web Service**.
2. Connect `bytebender77/RESPOND`.
3. Settings:
   - **Name**: `respond-api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables**: Add `QDRANT_URL` and `QDRANT_API_KEY`.

## 3. Frontend Deployment (Vercel)
1. Go to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New ...** -> **Project**.
3. Import `bytebender77/RESPOND`.
4. **Configure Project**:
   - **Framework Preset**: Other
   - **Root Directory**: `frontend_basic` (Important! Click "Edit" and select this folder).
5. **Environment Variables** (if needed): 
   - Since this is a static frontend communicating with the backend, you might need to update the API URL in `frontend_basic/app.js` if it's hardcoded to localhost, or ensure the frontend learns about the production backend URL.
   *(Note: Check if `app.js` points to `respond-api.onrender.com` or has a configuration for it)*.
6. Click **Deploy**.

## 4. Final Check
- **Backend Health**: Visit `https://respond-api.onrender.com/health` (or your assigned URL) and check for `{"status":"healthy"}`.
- **Frontend**: Visit your Vercel URL and test the search functionality.
