/**
 * RESPOND Dashboard - Professional Frontend
 */

// Configure API_BASE: set window.API_BASE before loading this script for production
const API_BASE = window.API_BASE || (
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://respond-api-bdub.onrender.com'
);
let currentResults = [];

// DOM Elements
const ingestForm = document.getElementById('ingestForm');
const searchForm = document.getElementById('searchForm');
const recommendBtn = document.getElementById('recommendBtn');
const ingestResult = document.getElementById('ingestResult');
const resultsContainer = document.getElementById('resultsContainer');
const resultsHeader = document.getElementById('resultsHeader');
const resultsTitle = document.getElementById('resultsTitle');
const actionsSection = document.getElementById('actionsSection');
const actionsContainer = document.getElementById('actionsContainer');
const sortSelect = document.getElementById('sortSelect');
const lastIngestTime = document.getElementById('lastIngestTime');

// =====================
// API Functions
// =====================

async function ingestIncident(data) {
  const response = await fetch(`${API_BASE}/ingest/incident`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error((await response.json()).detail || 'Ingestion failed');
  return response.json();
}

async function searchIncidents(params) {
  const response = await fetch(`${API_BASE}/search/incidents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!response.ok) throw new Error((await response.json()).detail || 'Search failed');
  return response.json();
}

async function updateStatus(incidentId, newStatus) {
  const response = await fetch(`${API_BASE}/memory/incident/${incidentId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus }),
  });
  if (!response.ok) throw new Error((await response.json()).detail || 'Update failed');
  return response.json();
}

async function recommendActions(query, limit = 5, zoneId = null) {
  const params = { query, limit };
  if (zoneId) params.zone_id = zoneId;
  const response = await fetch(`${API_BASE}/recommend/actions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!response.ok) throw new Error((await response.json()).detail || 'Recommendation failed');
  return response.json();
}

// =====================
// UI Helpers
// =====================

function showResult(element, message, isError = false) {
  element.textContent = message;
  element.className = `result-box ${isError ? 'error' : 'success'}`;
}

function hideResult(element) {
  element.className = 'result-box';
}

function formatAge(seconds) {
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

function renderLoading() {
  resultsContainer.innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      <p>Searching incidents...</p>
    </div>
  `;
}

// =====================
// Render Functions
// =====================

function renderIncidentCard(result) {
  const { id, score, payload, final_score, decay_factor, age_seconds, evidence } = result;

  const isConfirmed = evidence.is_multi_source_confirmed;
  const confidencePercent = Math.round(evidence.confidence_score * 100);

  const evidenceChainHtml = evidence.evidence_chain.length > 0
    ? evidence.evidence_chain.map(e => `
        <div class="evidence-item">
          <div class="evidence-item-header">
            <span>${e.source_type.toUpperCase()} • ${e.accepted ? '✅ Accepted' : '❌ Rejected'}</span>
            <span>Similarity: ${(e.similarity * 100).toFixed(1)}%</span>
          </div>
          <p>${e.text}</p>
        </div>
      `).join('')
    : '<p style="color: var(--muted); font-size: 12px;">No evidence chain</p>';

  return `
    <div class="incident-card ${isConfirmed ? 'confirmed' : ''}" data-id="${id}">
      <div class="card-header">
        <span class="card-id">ID: ${id.substring(0, 8)}...</span>
        <div class="card-badges">
          <span class="badge badge-${payload.urgency}">${payload.urgency}</span>
          <span class="badge badge-${payload.status}">${payload.status}</span>
          ${isConfirmed ? '<span class="badge badge-confirmed">✓ Multi-source</span>' : ''}
        </div>
      </div>
      
      <p class="card-text">${payload.text}</p>
      
      <div class="confidence-bar-container">
        <div class="confidence-label">
          <span>Confidence</span>
          <span>${confidencePercent}%</span>
        </div>
        <div class="confidence-bar">
          <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
        </div>
      </div>
      
      <div class="card-metrics">
        <div class="metric">
          <div class="metric-value">${final_score.toFixed(3)}</div>
          <div class="metric-label">Final Score</div>
        </div>
        <div class="metric">
          <div class="metric-value">${decay_factor}</div>
          <div class="metric-label">Decay</div>
        </div>
        <div class="metric">
          <div class="metric-value">${formatAge(age_seconds)}</div>
          <div class="metric-label">Age</div>
        </div>
        <div class="metric">
          <div class="metric-value">${payload.zone_id || 'N/A'}</div>
          <div class="metric-label">Zone</div>
        </div>
        <div class="metric">
          <div class="metric-value">${evidence.accepted_evidence_count}/${evidence.evidence_count}</div>
          <div class="metric-label">Evidence</div>
        </div>
      </div>
      
      <div class="evidence-section">
        <div class="evidence-toggle" onclick="toggleEvidence('${id}')">
          <span>📋 Evidence Chain (${evidence.evidence_count})</span>
          <span>▼</span>
        </div>
        <div class="evidence-chain" id="evidence-${id}">
          ${evidenceChainHtml}
        </div>
      </div>
      
      <div class="card-actions">
        <select class="status-select" id="status-${id}">
          <option value="pending" ${payload.status === 'pending' ? 'selected' : ''}>Pending</option>
          <option value="acknowledged" ${payload.status === 'acknowledged' ? 'selected' : ''}>Acknowledged</option>
          <option value="resolved" ${payload.status === 'resolved' ? 'selected' : ''}>Resolved</option>
        </select>
        <button class="btn btn-small btn-secondary" onclick="handleStatusUpdate('${id}')">Update</button>
        ${payload.status === 'pending' ? `<button class="btn btn-small btn-success" onclick="quickAcknowledge('${id}')">✓ Acknowledge</button>` : ''}
      </div>
    </div>
  `;
}

function renderResults(data) {
  currentResults = data.results;
  resultsHeader.style.display = 'flex';
  resultsTitle.textContent = `${data.count} incident${data.count !== 1 ? 's' : ''} found`;

  if (data.count === 0) {
    resultsContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🔍</div>
        <p>No incidents found matching your query</p>
      </div>
    `;
    return;
  }

  resultsContainer.innerHTML = data.results.map(renderIncidentCard).join('');
}

function renderActions(data) {
  actionsSection.classList.remove('hidden');

  if (data.actions.length === 0) {
    actionsContainer.innerHTML = '<p style="color: var(--muted);">No actions recommended</p>';
    return;
  }

  actionsContainer.innerHTML = data.actions.map(action => `
    <div class="action-card">
      <div class="action-header">
        <span class="action-type">${action.action_type.replace(/_/g, ' ')}</span>
        <span class="action-priority">Priority ${action.priority}/5</span>
      </div>
      <p class="action-reason">${action.reason}</p>
      <p class="action-incidents">Linked incidents: ${action.incident_ids.map(id => id.substring(0, 8)).join(', ')}</p>
    </div>
  `).join('');
}

function sortResults(sortBy) {
  if (!currentResults.length) return;

  const sorted = [...currentResults].sort((a, b) => {
    if (sortBy === 'final_score') return b.final_score - a.final_score;
    if (sortBy === 'confidence_score') return b.evidence.confidence_score - a.evidence.confidence_score;
    if (sortBy === 'age_seconds') return a.age_seconds - b.age_seconds;
    return 0;
  });

  resultsContainer.innerHTML = sorted.map(renderIncidentCard).join('');
}

// =====================
// Global Functions
// =====================

window.toggleEvidence = function (id) {
  const el = document.getElementById(`evidence-${id}`);
  el.classList.toggle('open');
};

window.handleStatusUpdate = async function (id) {
  const newStatus = document.getElementById(`status-${id}`).value;
  try {
    const result = await updateStatus(id, newStatus);
    alert(`✓ Status updated: ${result.old_status} → ${result.new_status}`);
    searchForm.dispatchEvent(new Event('submit'));
  } catch (error) {
    alert(`✗ Error: ${error.message}`);
  }
};

window.quickAcknowledge = async function (id) {
  try {
    const result = await updateStatus(id, 'acknowledged');
    alert(`✓ Incident acknowledged`);
    searchForm.dispatchEvent(new Event('submit'));
  } catch (error) {
    alert(`✗ Error: ${error.message}`);
  }
};

// =====================
// Event Listeners
// =====================

ingestForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideResult(ingestResult);

  const data = {
    text: document.getElementById('text').value,
    source_type: document.getElementById('source_type').value,
    urgency: document.getElementById('urgency').value,
    status: document.getElementById('status').value,
    zone_id: document.getElementById('zone_id').value || 'unknown',
    location: {
      lat: parseFloat(document.getElementById('lat').value) || 28.6139,
      lon: parseFloat(document.getElementById('lon').value) || 77.2090,
    },
  };

  try {
    const result = await ingestIncident(data);
    showResult(ingestResult, `✓ Ingested: ${result.incident_id.substring(0, 8)}...`);
    lastIngestTime.textContent = `Last ingest: just now`;
    document.getElementById('text').value = '';
  } catch (error) {
    showResult(ingestResult, `✗ ${error.message}`, true);
  }
});

searchForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  actionsSection.classList.add('hidden');
  renderLoading();

  const params = {
    query: document.getElementById('query').value,
    limit: parseInt(document.getElementById('search_limit').value) || 10,
  };

  const lastHours = document.getElementById('search_last_hours').value;
  if (lastHours) params.last_hours = parseInt(lastHours);

  const urgency = document.getElementById('search_urgency').value;
  if (urgency) params.urgency = urgency;

  const status = document.getElementById('search_status').value;
  if (status) params.status = status;

  try {
    const result = await searchIncidents(params);
    renderResults(result);
  } catch (error) {
    resultsHeader.style.display = 'none';
    resultsContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">⚠️</div>
        <p>Error: ${error.message}</p>
      </div>
    `;
  }
});

recommendBtn.addEventListener('click', async () => {
  const query = document.getElementById('query').value;
  if (!query) {
    alert('Please enter a search query first');
    return;
  }

  try {
    const result = await recommendActions(query, 5);
    renderActions(result);
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
});

sortSelect.addEventListener('change', (e) => {
  sortResults(e.target.value);
});

// =====================
// Initialize
// =====================

console.log('🚨 RESPOND Dashboard initialized');
console.log('📡 API Base:', API_BASE);
