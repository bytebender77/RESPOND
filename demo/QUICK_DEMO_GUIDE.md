# 🚀 Quick Demo Guide - RESPOND

**3-Minute Setup → 5-Minute Demo**

---

## ✅ Pre-Flight Checklist

```bash
# 1. Start backend (Terminal 1)
source venv/bin/activate
uvicorn api.main:app --reload

# 2. Initialize Qdrant (Terminal 2)
curl http://127.0.0.1:8000/setup

# 3. Start frontend (Terminal 3)
cd frontend_basic
python3 -m http.server 5500

# 4. Open browser
# → http://127.0.0.1:5500
```

**Status check:** Header should show "🟢 Qdrant Memory Online"

---

## 🎯 5-Minute Demo Flow

### 1️⃣ Ingest Incident (30 sec)

**Left panel:**
```
Description: Building fire at Central Tower, multiple floors affected, residents trapped
Source: Call
Urgency: Critical
→ Submit
```

🎯 **Show:** 
- ✅ Incident ID appears
- ✅ "Last ingest: just now"
- ✅ Click "📋 Copy ID" (save for later)

---

### 2️⃣ Test Deduplication (30 sec)

**Same panel:**
```
Description: Fire reported at Central Tower with people trapped inside
Source: Social
Urgency: Critical
→ Submit
```

🎯 **Show:** 
- 🔄 "DEDUPLICATED" status
- Same incident ID as before

---

### 3️⃣ Search Incidents (45 sec)

**Right panel:**
```
Query: fire emergency trapped
Limit: 10
→ 🔍 Search
```

🎯 **Show:**
- Results appear with confidence bars
- Click evidence chain toggle
- Point out: Final Score, Decay, Age metrics

---

### 4️⃣ Upload Media (1 min)

**Switch to Media tab:**

Click **"🖼️ Use for Media"** button OR manually paste incident ID

```
Incident ID: {paste}
Image File: {select any image}
Type: Photo
→ 📤 Upload
```

🎯 **Show:** 
- Upload success
- Image embedded with CLIP

*Optional: Upload audio for Whisper demo*

---

### 5️⃣ Image Search (45 sec)

**Scroll to Image Search section:**
```
Query: fire smoke building
→ 🔍 Search Images
```

🎯 **Show:**
- Gallery appears with uploaded image
- Similarity score
- Click image to open

---

### 6️⃣ Get Recommendations (30 sec)

**Back to Incidents tab:**
```
Query: fire emergency rescue
→ 🎯 Recommend Actions
```

🎯 **Show:**
- AI-generated action cards
- Priority scores
- Linked incidents

---

### 7️⃣ Create Deployment (45 sec)

**Switch to Deployments tab:**

```
Action Type: Dispatch Fire Unit
Incident IDs: {paste incident ID}
Assigned Unit: Fire Rescue Unit 5
Zone: zone-1
→ 🚀 Create Deployment
```

🎯 **Show:**
- Deployment created
- Copy deployment ID

---

### 8️⃣ Update Status (30 sec)

**Update deployment:**
```
Deployment ID: {paste}
Status: En Route
Notes: Team dispatched, ETA 5 mins
→ 📝 Update
```

**Update incident (back to Incidents tab):**
```
Find incident card → dropdown → Acknowledged → Update
```

🎯 **Show:** Full workflow complete! 🎉

---

## 🎨 Feature Highlights

| Feature | Location | What to Show |
|---------|----------|--------------|
| **Deduplication** | Incidents tab | Same ID for similar reports |
| **Multi-source** | Evidence chain | ✓ Badge when confirmed |
| **Time Decay** | Search results | Older = lower decay factor |
| **CLIP Images** | Media tab | Text→Image search works |
| **Whisper Audio** | Media tab | Auto-transcription |
| **AI Actions** | Incidents tab | Context-aware suggestions |
| **Deployments** | Deployments tab | Full lifecycle tracking |

---

## 🔥 Power User Tips

### Quick Test Data

**Critical Fire:**
```
Building fire at residential tower, multiple floors affected, heavy smoke, residents trapped on floors 8-12
```

**Flood Emergency:**
```
Severe flooding in residential area, water level rising rapidly, 50+ families stranded, rescue boats needed
```

**Collapse:**
```
Bridge collapse on highway near metro station, multiple vehicles trapped underneath
```

### API Shortcuts

```bash
# Reset everything
curl -X DELETE http://127.0.0.1:8000/reset

# Batch ingest via script
python3 scripts/simulate_disaster.py

# Direct search
curl -X POST "http://127.0.0.1:8000/search/incidents" \
  -H "Content-Type: application/json" \
  -d '{"query": "fire", "limit": 5}'
```

### Keyboard Shortcuts

- `Cmd/Ctrl + Shift + C` - Open browser console (check API calls)
- Copy incident ID immediately after ingestion
- Use browser back/forward for quick tab switching

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| "Connection refused" | Check backend running on 8000 |
| No search results | Run `/setup` to initialize |
| Images not loading | Check `uploads/` directory exists |
| Dedup not working | Ensure incidents within 5 min |

---

## 📊 Demo Metrics to Mention

- **Embedding Model:** MiniLM-L6 (384-dim)
- **Image Model:** CLIP (512-dim)
- **Audio Model:** Whisper (base)
- **Vector DB:** Qdrant Cloud
- **Dedup Window:** 5 minutes
- **Time Decay:** Exponential (halflife=12h)

---

## 🎬 One-Liner Pitch

> "RESPOND transforms chaotic disaster reports into prioritized, actionable intelligence using Qdrant's vector memory—incidents evolve, reinforce, and decay in real-time without re-embedding."

---

## 📱 Mobile Testing

Frontend is responsive! Test on:
- Chrome DevTools mobile view (Cmd+Shift+M)
- Actual mobile device (use ngrok for external access)

---

## 🔗 Essential Links

- **Frontend:** http://127.0.0.1:5500
- **API Docs:** http://127.0.0.1:8000/docs
- **Qdrant Dashboard:** https://cloud.qdrant.io

---

## 📝 Post-Demo Q&A Prep

**Q: How does deduplication work?**
→ Cosine similarity + time window + source diversity check

**Q: What if confidence is low?**
→ Incident stays in DB but lower priority in search ranking

**Q: Can you update past incidents?**
→ Yes! Reinforce evidence, update status, add media—all without re-embedding

**Q: What makes this different from traditional DB?**
→ Vector semantic search + evolving memory + temporal ranking

---

**Time breakdown:**
- Setup: 3 min
- Demo: 5 min  
- Q&A: 2 min
- **Total: 10 min** ✅

---

*Ready to impress! 🚀*
