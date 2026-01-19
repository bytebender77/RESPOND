# RESPOND — Architecture Guide

**Technical Design & Qdrant Deep Dive**

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Data Flow](#2-data-flow)
3. [Qdrant Schema Design](#3-qdrant-schema-design)
4. [Component Architecture](#4-component-architecture)
5. [Embedding Strategy](#5-embedding-strategy)
6. [Search Architecture](#6-search-architecture)
7. [Memory System](#7-memory-system)
8. [API Design](#8-api-design)
9. [Frontend Architecture](#9-frontend-architecture)
10. [Deployment Considerations](#10-deployment-considerations)

---

## 1. System Overview

RESPOND is a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│  ┌───────────────────┐  ┌───────────────────────────────┐   │
│  │  Frontend (HTML)  │  │  REST API (FastAPI)           │   │
│  │  • Dashboard      │  │  • /ingest  • /search         │   │
│  │  • Forms          │  │  • /memory  • /recommend      │   │
│  └───────────────────┘  └───────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                      Business Logic Layer                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │  Ingestion  │ │   Search    │ │  Recommendation     │   │
│  │  Pipeline   │ │   Engine    │ │  Engine             │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Memory Management Layer                 │   │
│  │  • Evolution  • Reinforcement  • Decay              │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                      Infrastructure Layer                    │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │  Text Embedder  │  │  Qdrant Client Wrapper          │  │
│  │  (MiniLM-L6)    │  │  • Connection pooling           │  │
│  └─────────────────┘  │  • Collection management        │  │
│                       └─────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      External Services                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Qdrant Cloud                       │   │
│  │  Collections: situation_reports, disaster_events,   │   │
│  │               resource_deployments, historical      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow

### 2.1 Ingestion Flow

```
┌──────────┐     ┌────────────┐     ┌───────────┐     ┌────────┐
│  Source  │────▶│  Validate  │────▶│   Embed   │────▶│ Qdrant │
│  Report  │     │  & Parse   │     │  (MiniLM) │     │ Upsert │
└──────────┘     └────────────┘     └───────────┘     └────────┘
                       │
                       ▼
              ┌────────────────┐
              │ Build Payload  │
              │ • timestamp    │
              │ • urgency      │
              │ • location     │
              │ • zone_id      │
              └────────────────┘
```

### 2.2 Search Flow

```
┌─────────┐     ┌─────────┐     ┌──────────────┐     ┌─────────┐
│  Query  │────▶│  Embed  │────▶│  Qdrant      │────▶│ Results │
│  Text   │     │  Query  │     │  Hybrid      │     │ (raw)   │
└─────────┘     └─────────┘     │  Search      │     └────┬────┘
                               └──────────────┘          │
         ┌───────────────────────────────────────────────┘
         │
         ▼
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│ Apply Decay │────▶│  Extract     │────▶│  Sort by       │
│ Factor      │     │  Evidence    │     │  final_score   │
└─────────────┘     └──────────────┘     └────────────────┘
```

### 2.3 Memory Update Flow

```
┌──────────────┐     ┌────────────────┐     ┌─────────────────┐
│  Update      │────▶│  Validate      │────▶│  Qdrant         │
│  Request     │     │  Transition    │     │  set_payload()  │
│  (status)    │     │  Rules         │     │                 │
└──────────────┘     └────────────────┘     └─────────────────┘

┌──────────────┐     ┌────────────────┐     ┌─────────────────┐
│  Reinforce   │────▶│  Compute       │────▶│  Update Payload │
│  Request     │     │  Similarity    │     │  • confidence   │
│              │     │  & Confidence  │     │  • evidence[]   │
└──────────────┘     └────────────────┘     └─────────────────┘
```

---

## 3. Qdrant Schema Design

### 3.1 Collections

| Collection | Purpose | Primary Use |
|------------|---------|-------------|
| `respond_situation_reports` | Active incident reports | Real-time search |
| `respond_disaster_events` | Major event groupings | Analytics |
| `respond_resource_deployments` | Resource tracking | Allocation |
| `respond_historical_patterns` | Past incidents | Learning |

### 3.2 Vector Configuration

```python
VectorParams(
    size=384,           # MiniLM-L6-v2 output dimension
    distance=Distance.COSINE,
)
```

### 3.3 Payload Schema (situation_reports)

```json
{
  "text": "Building collapse near school, people trapped",
  "source_type": "social",
  "timestamp": "2026-01-19T01:30:00+00:00",
  "timestamp_unix": 1768766200,
  "urgency": "critical",
  "status": "pending",
  "zone_id": "zone-4",
  "confidence_score": 0.5,
  "location": {
    "lat": 28.6139,
    "lon": 77.2090
  },
  "created_at": "2026-01-19T01:30:00+00:00",
  "updated_at": "2026-01-19T01:35:00+00:00",
  "evidence_chain": [
    {
      "source_type": "call",
      "text": "Confirming collapse...",
      "similarity": 0.78,
      "timestamp": "2026-01-19T01:35:00+00:00",
      "accepted": true
    }
  ],
  "reinforced_count": 1
}
```

### 3.4 Payload Indexes

```python
PAYLOAD_INDEX_SCHEMA = {
    "timestamp": PayloadSchemaType.KEYWORD,
    "timestamp_unix": PayloadSchemaType.INTEGER,    # For Range queries
    "source_type": PayloadSchemaType.KEYWORD,
    "urgency": PayloadSchemaType.KEYWORD,
    "status": PayloadSchemaType.KEYWORD,
    "zone_id": PayloadSchemaType.KEYWORD,
    "confidence_score": PayloadSchemaType.FLOAT,
    "location": PayloadSchemaType.GEO,              # For geo-radius
}
```

### 3.5 Why These Indexes?

| Index | Query Type | Example |
|-------|-----------|---------|
| `timestamp_unix` (INT) | Range | `last 24 hours` |
| `urgency` (KEYWORD) | Exact match | `urgency = critical` |
| `status` (KEYWORD) | Exact match | `status = pending` |
| `zone_id` (KEYWORD) | Exact match | `zone_id = zone-4` |
| `location` (GEO) | Geo-radius | `within 5km of HQ` |
| `confidence_score` (FLOAT) | Range | `confidence > 0.7` |

---

## 4. Component Architecture

### 4.1 Directory Structure

```
src/
├── embeddings/
│   ├── base.py              # Abstract BaseEmbedder
│   └── text_embedder.py     # MiniLM-L6 implementation
│
├── qdrant/
│   ├── client.py            # Singleton client wrapper
│   ├── collections.py       # Collection management
│   ├── indexer.py           # Upsert operations
│   └── searcher.py          # Query operations
│
├── ingestion/
│   ├── base_ingester.py     # Abstract BaseIngester
│   └── incident_ingester.py # Incident-specific logic
│
├── memory/
│   ├── memory_manager.py    # CRUD operations
│   ├── evolution.py         # Status transitions
│   ├── reinforcement.py     # Confidence boosting
│   └── decay.py             # Time-based scoring
│
├── search/
│   ├── filters.py           # Filter builders
│   └── hybrid_search.py     # Combined search logic
│
├── evidence/
│   └── tracer.py            # Evidence extraction
│
├── recommendation/
│   └── action_recommender.py # Action generation
│
└── utils/
    ├── logger.py            # Logging
    ├── time_utils.py        # Time helpers
    ├── geo_utils.py         # Geo helpers
    └── ids.py               # UUID generation
```

### 4.2 Dependency Graph

```
                    ┌─────────────────┐
                    │     config/     │
                    │   settings.py   │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   src/utils/    │ │ src/embeddings/ │ │   src/qdrant/   │
│   • logger      │ │ • text_embedder │ │   • client      │
│   • time_utils  │ └────────┬────────┘ │   • collections │
│   • geo_utils   │          │          │   • indexer     │
│   • ids         │          │          │   • searcher    │
└────────┬────────┘          │          └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ src/ingestion/  │ │   src/memory/   │ │  src/search/    │
│ • incident_     │ │ • memory_mgr    │ │ • filters       │
│   ingester      │ │ • evolution     │ │ • hybrid_search │
└─────────────────┘ │ • reinforcement │ └────────┬────────┘
                    │ • decay         │          │
                    └────────┬────────┘          │
                             │                   │
                             └───────────────────┘
                                       │
                             ┌─────────▼─────────┐
                             │  src/recommend/   │
                             │ action_recommender│
                             └─────────┬─────────┘
                                       │
                             ┌─────────▼─────────┐
                             │     api/routes/   │
                             │ • ingest • search │
                             │ • memory • recommend
                             └───────────────────┘
```

---

## 5. Embedding Strategy

### 5.1 Model Selection

**Model**: `sentence-transformers/all-MiniLM-L6-v2`

| Attribute | Value |
|-----------|-------|
| Dimensions | 384 |
| Sequence length | 256 tokens |
| Speed | ~50ms per embedding |
| Quality | Good for semantic similarity |

### 5.2 Singleton Loading

```python
_model = None

def _load_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model
```

### 5.3 Fallback Mode

For offline/demo environments, a hash-based embedding:

```python
def _hash_to_vector(text: str, size: int) -> list[float]:
    result = []
    counter = 0
    while len(result) < size:
        hash_bytes = hashlib.sha256(f"{text}:{counter}".encode()).digest()
        for b in hash_bytes:
            if len(result) >= size:
                break
            result.append(b / 255.0)
        counter += 1
    return result
```

---

## 6. Search Architecture

### 6.1 Filter Builder Pattern

Each filter type has a dedicated builder:

```python
def build_time_filter(last_hours: int | None) -> FieldCondition | None:
    if last_hours is None:
        return None
    cutoff_unix = int(datetime.now(timezone.utc).timestamp()) - (last_hours * 3600)
    return FieldCondition(
        key="timestamp_unix",
        range=Range(gte=cutoff_unix)
    )
```

### 6.2 Filter Combination

```python
def combine_filters(filters: list) -> Filter | None:
    valid = [f for f in filters if f is not None]
    if not valid:
        return None
    return Filter(must=valid)
```

### 6.3 Search Pipeline

```python
def search_incidents(self, query, limit, zone_id, urgency, status, last_hours, center, radius_km):
    # 1. Embed query
    query_vector = self._embedder.embed_text(query)
    
    # 2. Build filters
    filters = [
        build_status_filter(status),
        build_urgency_filter(urgency),
        build_zone_filter(zone_id),
        build_time_filter(last_hours),
        build_geo_filter(center, radius_km),
    ]
    combined = combine_filters(filters)
    
    # 3. Execute Qdrant search
    results = search(SITUATION_REPORTS, query_vector, limit, combined)
    
    # 4. Post-process: decay + evidence
    reranked = []
    for r in results:
        decay = apply_decay(r["score"], r["payload"].get("timestamp_unix"))
        evidence = extract_evidence(r["payload"])
        reranked.append({...r, **decay, "evidence": evidence})
    
    # 5. Sort by final_score
    reranked.sort(key=lambda x: x["final_score"], reverse=True)
    return reranked
```

---

## 7. Memory System

### 7.1 Status Evolution

State machine for incident lifecycle:

```
┌─────────┐      acknowledge      ┌──────────────┐      resolve      ┌──────────┐
│ PENDING │ ────────────────────▶ │ ACKNOWLEDGED │ ────────────────▶ │ RESOLVED │
└─────────┘                       └──────────────┘                   └──────────┘
     │                                                                     │
     └─────────────────────────── (invalid) ◀──────────────────────────────┘
```

### 7.2 Reinforcement Algorithm

```python
def reinforce_incident(payload, new_source_type, new_text, similarity):
    old_conf = payload.get("confidence_score", 0.5)
    evidence_chain = payload.get("evidence_chain", [])
    
    accepted = similarity >= 0.65
    
    if accepted:
        boost = min(0.15, similarity * 0.1)
        new_conf = min(1.0, old_conf + boost)
    else:
        new_conf = old_conf
    
    evidence_chain.append({
        "source_type": new_source_type,
        "text": new_text,
        "similarity": similarity,
        "timestamp": utc_now_iso(),
        "accepted": accepted,
    })
    
    return {
        "confidence_score": new_conf,
        "evidence_chain": evidence_chain,
        "reinforced_count": payload.get("reinforced_count", 0) + (1 if accepted else 0),
    }
```

### 7.3 Decay Function

```python
def compute_decay_factor(age_seconds: int) -> float:
    if age_seconds <= 3600:      # 1 hour
        return 1.0
    elif age_seconds <= 21600:   # 6 hours
        return 0.8
    elif age_seconds <= 86400:   # 24 hours
        return 0.5
    else:
        return 0.2
```

---

## 8. API Design

### 8.1 RESTful Endpoints

| Method | Path | Body | Response |
|--------|------|------|----------|
| `GET` | `/health` | — | `{"status": "ok"}` |
| `GET` | `/setup` | — | `{"created": [...], "existing": [...]}` |
| `POST` | `/ingest/incident` | `IncidentIngestRequest` | `IngestResponse` |
| `POST` | `/search/incidents` | `IncidentSearchRequest` | `SearchResponse` |
| `PATCH` | `/memory/incident/{id}/status` | `StatusUpdateRequest` | `StatusUpdateResponse` |
| `POST` | `/memory/incident/{id}/reinforce` | `ReinforceRequest` | `ReinforceResponse` |
| `POST` | `/recommend/actions` | `RecommendRequest` | `ActionResponse` |

### 8.2 Request/Response Models

```python
class IncidentSearchRequest(BaseModel):
    query: str
    limit: int = 10
    zone_id: str | None = None
    urgency: str | None = None
    status: str | None = None
    last_hours: int | None = None
    center: dict | None = None      # {"lat": float, "lon": float}
    radius_km: float | None = None

class SearchResultItem(BaseModel):
    id: str
    score: float
    payload: dict
    final_score: float
    decay_factor: float
    age_seconds: int
    evidence: dict
```

### 8.3 CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 9. Frontend Architecture

### 9.1 Technology

- **HTML5**: Semantic structure
- **CSS3**: Custom properties, flexbox, grid
- **Vanilla JS**: Fetch API, DOM manipulation

### 9.2 Component Structure

```
frontend/
├── index.html      # Layout: header, forms, results
├── styles.css      # Dark theme, cards, badges
└── app.js          # API calls, rendering, events
```

### 9.3 API Integration

```javascript
async function searchIncidents(params) {
    const response = await fetch(`${API_BASE}/search/incidents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
    });
    return response.json();
}
```

---

## 10. Deployment Considerations

### 10.1 Environment Variables

```env
ENV=dev
QDRANT_URL=https://<cluster>.cloud.qdrant.io:6333
QDRANT_API_KEY=<api-key>
QDRANT_PREFIX=respond_
LOG_LEVEL=INFO
```

### 10.2 Production Checklist

- [ ] Use HTTPS for API
- [ ] Add authentication (OAuth/JWT)
- [ ] Rate limiting on ingestion
- [ ] Qdrant collection backup
- [ ] Monitoring and alerting
- [ ] Auto-scaling for API servers

### 10.3 Scaling Strategy

| Component | Scaling Approach |
|-----------|------------------|
| API Servers | Horizontal (load balancer) |
| Embedder | GPU instances for batch |
| Qdrant | Qdrant Cloud auto-scaling |
| Frontend | CDN + static hosting |

---

*Architecture document for RESPOND — Qdrant Hackathon 2026*
