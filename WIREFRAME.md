# RESPOND — Project Wireframe

**Simple Explanation of How the System Works**

---

## 🔄 The Big Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   INCIDENT HAPPENS                                                      │
│   (fire, flood, collapse)                                               │
│           │                                                             │
│           ▼                                                             │
│   ┌─────────────┐       ┌─────────────┐       ┌─────────────┐          │
│   │  SOURCES    │──────▶│   INGEST    │──────▶│   QDRANT    │          │
│   │  - Social   │       │  - Validate │       │  - Vectors  │          │
│   │  - Sensor   │       │  - Embed    │       │  - Payloads │          │
│   │  - Call     │       │  - Store    │       │  - Indexes  │          │
│   └─────────────┘       └─────────────┘       └──────┬──────┘          │
│                                                       │                 │
│                                                       ▼                 │
│   ┌─────────────┐       ┌─────────────┐       ┌─────────────┐          │
│   │  DASHBOARD  │◀──────│  RECOMMEND  │◀──────│   SEARCH    │          │
│   │  - View     │       │  - Actions  │       │  - Semantic │          │
│   │  - Update   │       │  - Priority │       │  - Filters  │          │
│   │  - Act      │       │  - Trace    │       │  - Decay    │          │
│   └─────────────┘       └─────────────┘       └─────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 Step-by-Step Flow

### Step 1: Something Happens

```
🔥 Fire at mall
🌊 Flood rising
🏚️ Building collapses
```

People report via social media, sensors detect it, or someone calls emergency services.

---

### Step 2: INGEST (Report Comes In)

```
Input: "Fire spotted at Central Mall, heavy smoke visible"
```

**What happens:**
1. Validate the report
2. Convert text → vector (384 numbers)
3. Add metadata (urgency, zone, timestamp)
4. Store in Qdrant

**What gets stored:**
```
┌────────────────────────────────────────────────────┐
│  ID: abc-123                                       │
│  Vector: [0.02, -0.04, 0.11, ...]  ← meaning      │
│  Payload:                                          │
│    - text: "Fire at Central Mall..."              │
│    - urgency: "critical"                          │
│    - status: "pending"                            │
│    - confidence: 0.5                              │
│    - timestamp: 1705123456                        │
│    - location: {lat, lon}                         │
│    - evidence_chain: []                           │
└────────────────────────────────────────────────────┘
```

---

### Step 3: SEARCH (Responder Looks for Incidents)

```
Query: "fire smoke emergency"
```

**What happens:**
1. Convert query → vector
2. Find similar vectors (semantic search)
3. Apply filters (urgency, time, zone)
4. Apply decay (fresh incidents rank higher)
5. Return ranked results

**Result:** Fire incident → score 0.92, priority #1

---

### Step 4: MEMORY EVOLVES

**A) Status Changes:**
```
pending  ──▶  acknowledged  ──▶  resolved
   │              │                 │
   └── new        └── handling      └── done
```

**B) Confidence Reinforcement:**
```
Original: "Fire at mall" (confidence 0.5)
    +
Phone call confirms: "Mall on fire"
    =
New confidence: 0.578 (boosted!)
```

**C) Time Decay:**
```
Fresh (< 1 hour)   → score × 1.0
Old (> 24 hours)   → score × 0.2
```

---

### Step 5: RECOMMEND (Suggest Actions)

```
IF "fire"    → DISPATCH_FIRE_BRIGADE
IF "flood"   → ISSUE_EVACUATION
IF "trapped" → SEARCH_AND_RESCUE
```

**Output:**
```json
{
  "action": "DISPATCH_SEARCH_AND_RESCUE",
  "priority": 5,
  "reason": "Detected 'trapped'; urgency=critical",
  "incident_ids": ["abc-123"]
}
```

---

## 🏗️ Code Structure

```
RESPOND/
├── api/                    ← FastAPI endpoints
│   └── routes/
│       ├── ingest.py       → POST /ingest/incident
│       ├── search.py       → POST /search/incidents
│       ├── memory.py       → PATCH /memory/.../status
│       └── recommend.py    → POST /recommend/actions
│
├── src/
│   ├── embeddings/         ← Text → Vector
│   ├── ingestion/          ← Validate + Store
│   ├── search/             ← Hybrid Search + Decay
│   ├── memory/             ← Status + Reinforcement
│   ├── evidence/           ← Evidence Chain
│   ├── recommendation/     ← Rule-based Actions
│   └── qdrant/             ← Qdrant Client
│
├── frontend/               ← HTML Dashboard
└── scripts/
    └── simulate_disaster.py
```

---

## 🎯 One-Sentence Summary

> **RESPOND takes messy disaster reports → embeds them → stores in Qdrant → enables smart search → evolves memory → recommends actions — all traceable, no hallucination.**

---

## 🚀 Quick Start

```bash
# Setup
git clone <repo> && cd quadrant
pip install -r requirements.txt
cp .env.example .env  # Add QDRANT_URL + QDRANT_API_KEY

# Run
uvicorn api.main:app --reload
curl http://127.0.0.1:8000/setup

# Demo
python3 scripts/simulate_disaster.py
cd frontend && python3 -m http.server 5500
```

---

*Built for Convolve 4.0 | Qdrant MAS Track*
