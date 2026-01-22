# 🧪 RESPOND - Complete Demo Test Scenarios

This document provides comprehensive test scenarios to validate all features of the RESPOND disaster response coordination system.

---

## 📋 Table of Contents

- [Setup Instructions](#setup-instructions)
- [Tab 1: Incidents Testing](#tab-1-incidents-testing)
- [Tab 2: Media Testing](#tab-2-media-testing)
- [Tab 3: Deployments Testing](#tab-3-deployments-testing)
- [Advanced Scenarios](#advanced-scenarios)
- [API Testing](#api-testing)

---

## ⚙️ Setup Instructions

### Prerequisites Check

1. ✅ Backend API running on `http://127.0.0.1:8000`
2. ✅ Frontend served on `http://127.0.0.1:5500`
3. ✅ Qdrant collections initialized (run `/setup` endpoint)
4. ✅ Browser console open (F12) for debugging

### Quick Validation

```bash
# Test backend health
curl http://127.0.0.1:8000/health

# Initialize collections
curl http://127.0.0.1:8000/setup
```

---

## 🔥 Tab 1: Incidents Testing

### Test Case 1.1: Basic Incident Ingestion

**Objective:** Test single incident creation

**Steps:**
1. Navigate to **Incidents tab** (should be active by default)
2. Fill in the left panel form:
   ```
   Incident Description: "Fire reported at residential building, multiple floors affected, residents evacuating"
   Source: Call
   Urgency: Critical
   Status: Pending
   Zone ID: zone-1
   Latitude: 28.6139
   Longitude: 77.2090
   ```
3. Click **Submit Incident**

**Expected Result:**
- ✅ Green success message with incident ID (UUID)
- ✅ "Last ingest: just now" updates in header
- ✅ Three action buttons appear: Copy ID, Use for Media, Use for Deployment
- ✅ Form clears automatically

**Copy the Incident ID for later tests!**

---

### Test Case 1.2: Deduplication Testing

**Objective:** Verify duplicate incident detection

**Steps:**
1. Submit first incident:
   ```
   Description: "Building fire on Main Street with heavy smoke"
   Source: Social
   Urgency: High
   Zone: zone-2
   ```
2. Copy the incident ID
3. Submit similar incident within 5 minutes:
   ```
   Description: "Fire at Main Street building, smoke visible"
   Source: Sensor
   Urgency: High
   Zone: zone-2
   ```

**Expected Result:**
- ✅ First submission shows "✓ NEW" status
- ✅ Second submission shows "🔄 DEDUPLICATED" status
- ✅ Both submissions return **same incident ID**
- ✅ Evidence count increases on the deduped incident

---

### Test Case 1.3: Search with Filters

**Objective:** Test hybrid search functionality

**Steps:**
1. Ensure you have at least 3-5 incidents ingested (use different urgencies and statuses)
2. In right panel, enter search query:
   ```
   Query: "fire emergency building"
   Last Hours: 24
   Limit: 10
   Urgency: Critical
   Status: Pending
   ```
3. Click **🔍 Search**

**Expected Result:**
- ✅ Loading spinner appears
- ✅ Results header shows count: "X incidents found"
- ✅ Incident cards display with:
  - Truncated incident ID
  - Urgency and status badges
  - Confidence bar with percentage
  - Metrics: Final Score, Decay, Age, Zone, Evidence count
  - Collapsed evidence chain section

---

### Test Case 1.4: Evidence Chain Verification

**Objective:** Validate multi-source evidence tracking

**Steps:**
1. Create a base incident (copy ID)
2. Use API to reinforce with evidence:
   ```bash
   curl -X POST "http://127.0.0.1:8000/memory/incident/{INCIDENT_ID}/reinforce" \
     -H "Content-Type: application/json" \
     -d '{
       "source_type": "sensor",
       "text": "Thermal sensors confirm fire at reported location"
     }'
   ```
3. Search for the incident in UI
4. Click **📋 Evidence Chain** toggle

**Expected Result:**
- ✅ Evidence section expands
- ✅ Shows 2+ evidence items
- ✅ Each shows: Source type, Accepted/Rejected status, Similarity %
- ✅ Original text visible for each evidence
- ✅ Multi-source badge appears if confirmed

---

### Test Case 1.5: Status Update Flow

**Objective:** Test incident lifecycle management

**Steps:**
1. Search for a "Pending" incident
2. In incident card, change dropdown to **Acknowledged**
3. Click **Update** button
4. Observe alert message
5. Re-run the same search

**Expected Result:**
- ✅ Alert shows: "✓ Status updated: pending → acknowledged"
- ✅ Card refreshes automatically
- ✅ Status badge updates to "acknowledged"
- ✅ Quick acknowledge button disappears

**Alternative:** Use **✓ Acknowledge** button for one-click update

---

### Test Case 1.6: Sort Functionality

**Objective:** Validate result sorting

**Steps:**
1. Search for incidents (get at least 5 results)
2. Try each sort option:
   - Sort by: Relevance (final_score)
   - Sort by: Confidence
   - Sort by: Newest (age_seconds)
3. Observe card order changes

**Expected Result:**
- ✅ Cards reorder without re-querying API
- ✅ Relevance: Higher scores at top
- ✅ Confidence: Higher confidence % at top
- ✅ Newest: Most recent (smallest age) at top

---

### Test Case 1.7: Action Recommendations

**Objective:** Test AI-driven action suggestions

**Steps:**
1. Enter search query: `"fire emergency multiple casualties"`
2. Click **🔍 Search** first to get results
3. Click **🎯 Recommend Actions** button

**Expected Result:**
- ✅ "Recommended Actions" section appears below results
- ✅ Shows action cards with:
  - Action type (e.g., DISPATCH_FIRE_UNIT)
  - Priority score (1-5)
  - Reason explaining why action is recommended
  - Linked incident IDs (truncated)
- ✅ Actions sorted by priority

---

### Test Case 1.8: Copy Incident ID

**Objective:** Test clipboard functionality

**Steps:**
1. Find any incident card in search results
2. Click **📋 Copy ID** button

**Expected Result:**
- ✅ Alert: "✓ Copied: {full-uuid}"
- ✅ Paste into text editor to verify full UUID copied

---

## 🖼️ Tab 2: Media Testing

### Test Case 2.1: Image Upload to Incident

**Objective:** Test CLIP-based image embedding

**Setup:**
1. Ensure you have an incident ID from Tab 1
2. Prepare a test image (fire, flood, collapse, etc.)

**Steps:**
1. Switch to **Media (Image/Audio)** tab
2. In **Upload Image Evidence** section:
   ```
   Incident ID: {paste_incident_id}
   Image File: {select_test_image.jpg}
   Image Type: Photo
   Zone ID: zone-1
   ```
3. Click **📤 Upload Image**

**Expected Result:**
- ✅ "⏳ Uploading and embedding image..." appears
- ✅ Success message: "✓ Image uploaded!"
- ✅ Shows truncated image point ID
- ✅ Form resets automatically

---

### Test Case 2.2: Audio Transcription & Reinforcement

**Objective:** Test Whisper audio-to-text

**Setup:**
1. Prepare an audio file (WAV, MP3, etc.) - can be any speech audio
2. Have an incident ID ready

**Steps:**
1. In **Upload Audio Evidence** section:
   ```
   Incident ID: {paste_incident_id}
   Audio File: {select_test_audio.wav}
   Source Type: Emergency Call
   ```
2. Click **🎤 Transcribe & Reinforce**

**Expected Result:**
- ✅ "⏳ Transcribing audio with Whisper..." message
- ✅ Transcription completes within 5-10 seconds
- ✅ Shows either:
  - "✅ Reinforcement Accepted" (high similarity)
  - "❌ Reinforcement Rejected" (low similarity)
- ✅ Displays similarity % and confidence change (old → new)
- ✅ **Transcript Preview** section appears below with transcribed text

---

### Test Case 2.3: Text-to-Image Search (CLIP)

**Objective:** Search images using natural language

**Setup:**
1. Upload at least 2-3 images to different incidents first (Test 2.1)

**Steps:**
1. Scroll to **Search Images (Text → Image)** section
2. Enter search query:
   ```
   Query: "fire with heavy smoke"
   Image Type: All Types
   ```
3. Click **🔍 Search Images**

**Expected Result:**
- ✅ "⏳ Searching images with CLIP..." message
- ✅ Success: "✓ Found X image(s) for 'fire with heavy smoke'"
- ✅ **Image Gallery** section appears
- ✅ Grid shows matching images with:
  - Image thumbnail
  - Image type badge
  - Similarity score (%)
  - Truncated incident ID
- ✅ Click on image opens full size in new tab

---

### Test Case 2.4: Image Type Filtering

**Objective:** Filter images by type

**Steps:**
1. Upload images of different types:
   - Photo
   - Satellite
   - Drone
   - CCTV
2. Search with type filter:
   ```
   Query: "disaster damage"
   Image Type: Drone
   ```

**Expected Result:**
- ✅ Only shows images with type "drone"
- ✅ Badge shows "drone" type

---

### Test Case 2.5: Quick Workflow - Incident to Media

**Objective:** Test integrated workflow

**Steps:**
1. In **Incidents tab**, ingest a new incident
2. Click **🖼️ Use for Media** button in success message
3. Verify automatic tab switch to Media

**Expected Result:**
- ✅ Automatically switches to Media tab
- ✅ Incident ID pre-filled in both image and audio upload forms
- ✅ Alert: "✓ Incident ID filled in Media tab..."
- ✅ Ready to upload file immediately

---

## 🚒 Tab 3: Deployments Testing

### Test Case 3.1: Create Deployment

**Objective:** Dispatch response units

**Setup:**
1. Have 1-2 incident IDs ready

**Steps:**
1. Switch to **Deployments** tab
2. Fill **Create Deployment** form:
   ```
   Action Type: Dispatch Fire Unit
   Incident IDs: {incident_id_1}, {incident_id_2}
   Assigned Unit: Fire Unit 7
   Zone ID: zone-1
   Notes: High priority response needed
   ```
3. Click **🚀 Create Deployment**

**Expected Result:**
- ✅ Success: "🚀 Deployment Created!"
- ✅ Shows truncated deployment ID
- ✅ Shows assigned unit name
- ✅ Form resets

**Copy deployment ID for next test!**

---

### Test Case 3.2: Update Deployment Status

**Objective:** Track deployment lifecycle

**Steps:**
1. In **Update Deployment Status** section:
   ```
   Deployment ID: {paste_deployment_id}
   New Status: En Route
   Notes: Unit dispatched, ETA 5 minutes
   ```
2. Click **📝 Update Status**

**Expected Result:**
- ✅ Success: "✓ Status Updated!"
- ✅ Shows transition: "assigned → en_route"
- ✅ Form resets

---

### Test Case 3.3: Complete Deployment Lifecycle

**Objective:** Test full deployment workflow

**Steps:**
1. Create deployment (status: assigned)
2. Update to: **En Route**
3. Update to: **On Site**
4. Update to: **Completed**

**Expected Result:**
- ✅ Each update shows correct status transition
- ✅ No errors at any stage

---

### Test Case 3.4: Quick Workflow - Incident to Deployment

**Objective:** Test integrated workflow

**Steps:**
1. In **Incidents tab**, search for critical incidents
2. Click **📋 Copy ID** on an incident
3. Click **🚒 Use for Deployment** (if available in test scenario)
4. Or manually switch to Deployments tab and paste ID

**Expected Result:**
- ✅ Switches to Deployments tab
- ✅ Incident ID pre-filled
- ✅ Ready to assign units

---

### Test Case 3.5: Multi-Incident Deployment

**Objective:** Deploy single unit to multiple incidents

**Steps:**
1. Create 3 separate incidents in same zone
2. Create deployment with all 3 IDs:
   ```
   Action Type: Evacuate Zone
   Incident IDs: {id1}, {id2}, {id3}
   Assigned Unit: Evacuation Team Alpha
   Zone: zone-3
   ```

**Expected Result:**
- ✅ Deployment created successfully
- ✅ Links all 3 incidents

---

## 🎯 Advanced Scenarios

### Scenario A: Multi-Source Confirmation

**Objective:** Achieve multi-source confirmation badge

**Steps:**
1. Ingest base incident from "social" source
2. Reinforce with "sensor" data (API call)
3. Reinforce with "call" data (API call)
4. Upload audio evidence (Whisper)
5. Upload image evidence (CLIP)
6. Search and view incident

**Expected Result:**
- ✅ **✓ Multi-source** badge appears on card
- ✅ Evidence chain shows 4-5 entries
- ✅ Confidence score increases with each addition
- ✅ `is_multi_source_confirmed: true` in payload

---

### Scenario B: Time Decay Visualization

**Objective:** Observe temporal ranking

**Steps:**
1. Ingest 3 identical incidents with 1-minute gaps
2. Search for them immediately
3. Wait 10 minutes
4. Search again
5. Compare final_score and decay_factor

**Expected Result:**
- ✅ Older incidents have lower decay_factor (e.g., 0.95 vs 1.0)
- ✅ Newer incidents rank higher in "Newest" sort
- ✅ Age shown as "Xs ago", "Xm ago", "Xh ago"

---

### Scenario C: Zone-Based Coordination

**Objective:** Test geographical filtering

**Steps:**
1. Create 5 incidents across 3 zones (zone-1, zone-2, zone-3)
2. Search without zone filter → all results
3. Use API to search with zone filter:
   ```bash
   curl -X POST "http://127.0.0.1:8000/search/incidents" \
     -H "Content-Type: application/json" \
     -d '{"query": "emergency", "zone_id": "zone-1"}'
   ```

**Expected Result:**
- ✅ Only zone-1 incidents returned
- ✅ Other zones filtered out

---

### Scenario D: Complete Disaster Response Workflow

**Full End-to-End Test**

1. **Incident Detection** (T+0 min)
   - Ingest: "Building collapse at 123 Main St, multiple trapped"
   - Source: Call, Urgency: Critical
   - Copy incident ID

2. **Evidence Gathering** (T+2 min)
   - Upload image of collapse site
   - Upload audio of emergency call
   - Both auto-reinforce incident

3. **Situation Analysis** (T+5 min)
   - Search: "collapse rescue trapped"
   - Review evidence chain
   - Verify multi-source confirmation

4. **Action Planning** (T+7 min)
   - Click "Recommend Actions"
   - Review AI suggestions

5. **Resource Deployment** (T+10 min)
   - Create deployment: HAZMAT_TEAM
   - Assign unit: Fire Rescue Unit 5
   - Update status: En Route → On Site

6. **Status Tracking** (T+15 min)
   - Update incident: Acknowledged → Resolved
   - Update deployment: Completed

**Expected Timeline:**
- ✅ All steps complete without errors
- ✅ Incident confidence increases with evidence
- ✅ Deployment tracks unit location
- ✅ Final state: Incident resolved, deployment completed

---

## 🧮 API Testing

### Direct API Test Cases

#### Test: Health Check
```bash
curl http://127.0.0.1:8000/health
```
**Expected:** `{"status":"ok"}`

---

#### Test: Ingest with Location
```bash
curl -X POST "http://127.0.0.1:8000/ingest/incident" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Flood waters rising in residential area, evacuations needed",
    "source_type": "sensor",
    "urgency": "high",
    "zone_id": "zone-4",
    "location": {"lat": 28.7041, "lon": 77.1025}
  }'
```
**Expected:** Returns incident ID and dedup status

---

#### Test: Search with All Filters
```bash
curl -X POST "http://127.0.0.1:8000/search/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "fire emergency",
    "limit": 5,
    "last_hours": 12,
    "urgency": "critical",
    "status": "pending",
    "zone_id": "zone-1"
  }'
```
**Expected:** Returns matching incidents with scores

---

#### Test: Reinforce Evidence
```bash
curl -X POST "http://127.0.0.1:8000/memory/incident/{ID}/reinforce" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "report",
    "text": "Official fire department confirms major blaze"
  }'
```
**Expected:** Returns similarity score and acceptance status

---

#### Test: Get Recommendations
```bash
curl -X POST "http://127.0.0.1:8000/recommend/actions" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "building collapse rescue",
    "limit": 3,
    "zone_id": "zone-2"
  }'
```
**Expected:** Returns prioritized action list

---

## 📊 Test Data Sets

### Realistic Test Incidents

```javascript
// Fire Scenarios
[
  {text: "Kitchen fire at apartment complex, residents trapped on upper floors", urgency: "critical", zone: "zone-1"},
  {text: "Wildfire approaching residential area, evacuation order issued", urgency: "critical", zone: "zone-3"},
  {text: "Small electrical fire in office building, extinguished", urgency: "low", zone: "zone-2"}
]

// Medical Emergencies
[
  {text: "Mass casualty incident at metro station, ambulances needed", urgency: "critical", zone: "zone-4"},
  {text: "Elderly person fell, requires medical assistance", urgency: "medium", zone: "zone-1"}
]

// Natural Disasters
[
  {text: "Earthquake detected, magnitude 6.2, buildings swaying", urgency: "critical", zone: "zone-all"},
  {text: "Severe flooding in low-lying areas, water level rising", urgency: "high", zone: "zone-5"},
  {text: "Landslide blocked highway, vehicles trapped", urgency: "high", zone: "zone-6"}
]

// Infrastructure
[
  {text: "Bridge collapse on highway, multiple vehicles involved", urgency: "critical", zone: "zone-2"},
  {text: "Gas leak reported near shopping mall, area evacuated", urgency: "high", zone: "zone-3"},
  {text: "Power lines down after storm, live wires on street", urgency: "high", zone: "zone-1"}
]
```

---

## ✅ Validation Checklist

### Feature Coverage

- [ ] **Incidents Tab**
  - [ ] Ingest incident
  - [ ] Deduplication works
  - [ ] Search with filters
  - [ ] View evidence chain
  - [ ] Update status
  - [ ] Sort results
  - [ ] Recommend actions
  - [ ] Copy incident ID

- [ ] **Media Tab**
  - [ ] Upload image
  - [ ] Upload audio
  - [ ] Transcription works
  - [ ] Image search (text-to-image)
  - [ ] Type filtering
  - [ ] Gallery display
  - [ ] Quick workflow from incidents

- [ ] **Deployments Tab**
  - [ ] Create deployment
  - [ ] Update deployment status
  - [ ] Multi-incident deployment
  - [ ] Quick workflow from incidents

- [ ] **Advanced Features**
  - [ ] Multi-source confirmation
  - [ ] Time decay calculation
  - [ ] Zone-based filtering
  - [ ] Evidence reinforcement
  - [ ] Confidence scoring

---

## 🐛 Expected Edge Cases

### Handled Gracefully

1. **Empty search results** → Shows "No incidents found" message
2. **Invalid incident ID** → Error message displayed
3. **Large file uploads** → Loading indicator shown
4. **Duplicate submissions** → Deduplication triggers
5. **Old incidents** → Decay factor reduces ranking
6. **Low similarity evidence** → Rejected, confidence unchanged

---

## 📈 Performance Benchmarks

### Target Metrics

| Operation | Target | Acceptable |
|-----------|--------|------------|
| Incident Ingestion | < 500ms | < 1s |
| Search Query | < 1s | < 2s |
| Image Upload + Embed | < 2s | < 5s |
| Audio Transcribe | < 5s | < 10s |
| Image Search | < 1s | < 3s |
| Status Update | < 300ms | < 500ms |

---

## 🎬 Demo Script

**For live presentation:**

1. **Setup (Pre-demo)**
   - Reset database: `curl -X DELETE http://127.0.0.1:8000/reset`
   - Initialize: `curl http://127.0.0.1:8000/setup`
   - Open frontend: http://127.0.0.1:5500

2. **Act 1: Crisis Begins** (2 min)
   - Ingest: "Building fire at Central Tower, multiple floors affected"
   - Show incident ID and dedup message
   - Ingest similar: "Fire reported at Central Tower" → Deduplication!

3. **Act 2: Evidence Gathering** (2 min)
   - Switch to Media tab (use quick button)
   - Upload fire image
   - Upload emergency call audio
   - Show transcript

4. **Act 3: Coordination** (2 min)
   - Search: "fire emergency building"
   - Expand evidence chain → Multi-source confirmed!
   - Click "Recommend Actions"
   - Show AI suggestions

5. **Act 4: Response** (1 min)
   - Create deployment: Fire Unit 7
   - Update status: En Route → On Site
   - Acknowledge incident

6. **Act 5: Verification** (1 min)
   - Search images: "fire heavy smoke"
   - Show gallery with uploaded evidence
   - Resolve incident
   - Complete deployment

---

## 🔗 Quick Links

- **Frontend:** http://127.0.0.1:5500
- **API Docs:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/health
- **Setup:** http://127.0.0.1:8000/setup

---

**Test Status:** ⏳ Ready for validation

*Last updated: January 22, 2026*
