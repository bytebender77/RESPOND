# RESPOND — Project Summary

**Multimodal Disaster Response Coordination System using Qdrant as Evolving Situational Memory**

---

## 🎯 What is RESPOND?

RESPOND is a disaster response coordination system that transforms chaotic incident reports into **prioritized, actionable intelligence**. It uses **Qdrant** as the core memory engine to store, search, and evolve incident information.

---

## 🔄 How It Works (Overview)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   INGEST    │ ──▶ │    EMBED    │ ──▶ │    STORE    │ ──▶ │   SEARCH    │
│  Incident   │     │   Text →    │     │   Qdrant    │     │   Hybrid    │
│   Report    │     │   Vector    │     │   Cloud     │     │   Query     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                    ┌─────────────┐     ┌─────────────┐            │
                    │  RECOMMEND  │ ◀── │   MEMORY    │ ◀──────────┘
                    │   Actions   │     │   Evolve    │
                    └─────────────┘     └─────────────┘
```

---

## 📥 Ingestion Flow

### Step-by-Step Process

```
1. RECEIVE INCIDENT
   └── Text: "Fire at Central Mall, heavy smoke visible"
   └── Source: social / sensor / call / report
   └── Urgency: critical / high / medium / low
   └── Location: {lat, lon}
   └── Zone: zone-1

2. CREATE EMBEDDING
   └── Model: all-MiniLM-L6-v2
   └── Output: [0.023, -0.045, 0.112, ...] (384 floats)
   └── Time: ~50ms

3. BUILD PAYLOAD
   └── text, source_type, urgency, zone_id
   └── timestamp_unix (current time)
   └── status: "pending" (default)
   └── confidence_score: 0.5 (default)
   └── evidence_chain: [] (empty)
   └── location: {lat, lon}

4. INSERT INTO QDRANT
   └── Collection: respond_situation_reports
   └── Point: {id, vector, payload}
   └── Indexes: timestamp, urgency, status, zone_id, location
```

### What Gets Stored

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Unique identifier |
| `vector` | float[384] | Semantic representation |
| `text` | string | Original incident text |
| `source_type` | keyword | social / sensor / call / report |
| `urgency` | keyword | critical / high / medium / low |
| `status` | keyword | pending / acknowledged / resolved |
| `timestamp_unix` | integer | When incident was ingested |
| `confidence_score` | float | Reliability (0.5 to 1.0) |
| `evidence_chain` | array | List of confirming reports |
| `location` | geo | lat/lon coordinates |
| `zone_id` | keyword | Geographic zone |

---

## 🔍 Query Flow

### Step-by-Step Process

```
1. RECEIVE QUERY
   └── Query: "fire smoke emergency"
   └── Filters: urgency=critical, last_hours=24, limit=10

2. EMBED QUERY
   └── Convert query text → 384-dim vector
   └── Time: ~50ms

3. BUILD QDRANT FILTER
   └── urgency == "critical"
   └── timestamp_unix >= (now - 24 hours)
   └── Optional: geo_radius, status

4. EXECUTE HYBRID SEARCH
   └── Semantic: query vector vs stored vectors (cosine similarity)
   └── Filters: applied in parallel
   └── Result: top-K matching points

5. APPLY TIME DECAY
   └── Age ≤ 1 hour  → decay = 1.0
   └── Age ≤ 6 hours → decay = 0.8
   └── Age ≤ 24 hours → decay = 0.5
   └── Age > 24 hours → decay = 0.2
   └── final_score = score × decay

6. EXTRACT EVIDENCE
   └── confidence_score
   └── evidence_count
   └── is_multi_source_confirmed

7. RETURN RESULTS
   └── Ranked by final_score (descending)
```

### Query Example

**Input:**
```json
{
  "query": "building collapse trapped people",
  "limit": 5,
  "urgency": "critical",
  "last_hours": 24
}
```

**Output:**
```json
{
  "count": 2,
  "results": [
    {
      "id": "91b1f4f1-...",
      "text": "Building collapsed near school, people trapped",
      "score": 0.92,
      "decay_factor": 1.0,
      "final_score": 0.92,
      "evidence": {
        "confidence_score": 0.65,
        "is_multi_source_confirmed": true
      }
    }
  ]
}
```

---

## 🧠 Memory Evolution

### Status Updates (No Re-Embedding)

```
pending ──────▶ acknowledged ──────▶ resolved
   │                  │                  │
   └── Waiting        └── Being          └── Completed
       for action         handled
```

**How it works:** Only the `payload.status` field is updated. The vector stays the same.

### Confidence Reinforcement

When a new report confirms an existing incident:

```
1. Compute similarity between original and new text
2. If similarity ≥ 0.65:
   └── boost = min(0.15, similarity × 0.1)
   └── new_confidence = old_confidence + boost
   └── Append to evidence_chain
3. If 2+ sources confirm → is_multi_source_confirmed = true
```

**Example:**
```
Original: "Fire at mall" (confidence: 0.5)
    + Call confirms: "Mall fire, heavy smoke" (similarity: 0.78)
    = New confidence: 0.578
    = evidence_chain: [{source: "call", text: "...", similarity: 0.78}]
```

---

## 🎯 Recommendation Engine

### Rule-Based Action Generation

| Detected Keywords | Action Generated |
|-------------------|------------------|
| fire, smoke | DISPATCH_FIRE_BRIGADE |
| flood, water | ISSUE_EVACUATION_ALERT |
| collapse, trapped | PRIORITIZE_HEAVY_EQUIPMENT |
| critical + pending | DISPATCH_SEARCH_AND_RESCUE |

### Priority Boosting

- Multi-source confirmed → +1 priority
- High confidence (>0.7) → +1 priority
- Critical urgency → base priority = 5

### Output Format

```json
{
  "action_type": "DISPATCH_SEARCH_AND_RESCUE",
  "priority": 5,
  "reason": "Detected 'trapped'; urgency=critical; multi-source confirmed",
  "incident_ids": ["91b1f4f1-...", "b10fb3b2-..."]
}
```

---

## 🏗️ Architecture Summary

```
┌─────────────────────────────────────────────────────────────┐
│                        RESPOND SYSTEM                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Sources ──▶ Ingestion ──▶ Qdrant Cloud                    │
│  (social,     (validate,    (situation_reports)             │
│   sensor,      embed,                │                      │
│   call)        index)                ▼                      │
│                              Hybrid Search                  │
│                              (semantic + filters)           │
│                                      │                      │
│  Dashboard ◀── Recommend ◀── Memory Layer                  │
│  (search,      (rules,       (evolution,                    │
│   update,       priority)     reinforcement,                │
│   monitor)                    decay)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Why Qdrant?

| Feature | How RESPOND Uses It |
|---------|---------------------|
| **Vector Search** | Semantic similarity for incident matching |
| **Payload Filters** | urgency, status, zone, time range |
| **Geo Queries** | Find incidents within N km |
| **In-Place Updates** | Status + confidence without re-embedding |
| **Indexing** | Fast filtered queries at scale |

---

## 🚀 Quick Start

```bash
# 1. Setup
git clone <repo> && cd quadrant
pip install -r requirements.txt
cp .env.example .env  # Add QDRANT_URL + QDRANT_API_KEY

# 2. Run
uvicorn api.main:app --reload
curl http://127.0.0.1:8000/setup

# 3. Demo
python3 scripts/simulate_disaster.py
cd frontend && python3 -m http.server 5500
```

---

## 📡 API Endpoints

| Method | Endpoint | Action |
|--------|----------|--------|
| POST | `/ingest/incident` | Add new incident |
| POST | `/search/incidents` | Hybrid search |
| PATCH | `/memory/incident/{id}/status` | Update status |
| POST | `/memory/incident/{id}/reinforce` | Add evidence |
| POST | `/recommend/actions` | Get action recommendations |

---

*Built with ❤️ for Convolve 4.0 | Qdrant MAS Track*
