/**
 * RESPOND Dashboard - Professional Frontend
 * Includes: Phase 11 (Dedup), Phase 12 (Images), Phase 13 (Audio), Phase 14/15 (Deployments)
 */

// Configure API_BASE: set window.API_BASE before loading this script for production
// Configure API_BASE: set window.API_BASE before loading this script for production
const API_BASE = window.API_BASE || (
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'https://respond-api-6qf6.onrender.com'
);
let currentResults = [];
let recentIncidents = []; // Store recent incident IDs for easy access
let lastIncidentId = null; // Most recent incident ID

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
// Tab Navigation
// =====================

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
      tab.style.display = 'none';
      tab.classList.remove('active');
    });

    // Show selected tab
    const tabId = btn.getAttribute('data-tab') + '-tab';
    const tabContent = document.getElementById(tabId);
    if (tabContent) {
      tabContent.style.display = 'grid';
      tabContent.classList.add('active');
    }
  });
});

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

// Phase 12: Image Upload
async function uploadImage(incidentId, file, imageType, zoneId) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('image_type', imageType);
  if (zoneId) formData.append('zone_id', zoneId);

  const response = await fetch(`${API_BASE}/ingest/incident/${incidentId}/image`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error((await response.json()).detail || 'Image upload failed');
  return response.json();
}

// Phase 13: Audio Upload
async function uploadAudio(incidentId, file, sourceType) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('source_type', sourceType);

  const response = await fetch(`${API_BASE}/memory/incident/${incidentId}/reinforce_audio`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error((await response.json()).detail || 'Audio upload failed');
  return response.json();
}

// Image Search (Text to Image via CLIP)
async function searchImages(query, imageType = null, limit = 10) {
  const params = { query, limit };
  if (imageType) params.image_type = imageType;

  const response = await fetch(`${API_BASE}/search/images`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!response.ok) throw new Error((await response.json()).detail || 'Image search failed');
  return response.json();
}

// Phase 15: Deployments
async function createDeployment(data) {
  const response = await fetch(`${API_BASE}/deployments/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error((await response.json()).detail || 'Deployment creation failed');
  return response.json();
}

async function updateDeploymentStatus(deploymentId, status, notes) {
  const response = await fetch(`${API_BASE}/deployments/${deploymentId}/status`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, notes }),
  });
  if (!response.ok) throw new Error((await response.json()).detail || 'Status update failed');
  return response.json();
}

// =====================
// UI Helpers
// =====================

function showResult(element, message, isError = false) {
  element.innerHTML = message;
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
        <button class="btn btn-small btn-info" onclick="copyIncidentId('${id}')">📋 Copy ID</button>
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

window.copyIncidentId = function (id) {
  navigator.clipboard.writeText(id);
  alert(`✓ Copied: ${id}`);
};

// Copy to clipboard helper
window.copyToClipboard = function (text) {
  navigator.clipboard.writeText(text);
  alert(`✓ Copied to clipboard!`);
};

// Auto-fill incident ID in Media tab and switch to it
window.useForMedia = function (incidentId) {
  // Fill both image and audio fields
  document.getElementById('image_incident_id').value = incidentId;
  document.getElementById('audio_incident_id').value = incidentId;

  // Switch to Media tab
  document.querySelectorAll('.tab-btn')[1].click();

  alert(`✓ Incident ID filled in Media tab. Select your file and upload!`);
};

// Auto-fill incident ID in Deployments tab and switch to it
window.useForDeployment = function (incidentId) {
  document.getElementById('deploy_incident_ids').value = incidentId;

  // Switch to Deployments tab
  document.querySelectorAll('.tab-btn')[2].click();

  alert(`✓ Incident ID added to Deployments. Fill in unit details and create!`);
};

// =====================
// Event Listeners - Incidents
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

    // Store the incident ID for easy access
    lastIncidentId = result.incident_id;
    recentIncidents.unshift({ id: result.incident_id, text: data.text.substring(0, 30) });
    if (recentIncidents.length > 10) recentIncidents.pop(); // Keep last 10

    // Phase 11: Show deduplication status
    const isDeduplicated = result.message.includes('deduplicated');
    const icon = isDeduplicated ? '🔄' : '✓';
    const statusText = isDeduplicated ? 'DEDUPLICATED' : 'NEW';

    showResult(ingestResult, `
      ${icon} <strong>${statusText}</strong>: <code>${result.incident_id}</code><br>
      <small>${result.message}</small><br><br>
      <button class="btn btn-small btn-info" onclick="copyToClipboard('${result.incident_id}')">📋 Copy ID</button>
      <button class="btn btn-small btn-success" onclick="useForMedia('${result.incident_id}')">🖼️ Use for Media</button>
      <button class="btn btn-small btn-secondary" onclick="useForDeployment('${result.incident_id}')">🚒 Use for Deployment</button>
    `);

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
// Event Listeners - Image Upload (Phase 12)
// =====================

document.getElementById('imageUploadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const resultEl = document.getElementById('imageUploadResult');
  hideResult(resultEl);

  const incidentId = document.getElementById('image_incident_id').value;
  const file = document.getElementById('image_file').files[0];
  const imageType = document.getElementById('image_type').value;
  const zoneId = document.getElementById('image_zone_id').value;

  if (!file) {
    showResult(resultEl, '✗ Please select an image file', true);
    return;
  }

  try {
    showResult(resultEl, '⏳ Uploading and embedding image...');
    const result = await uploadImage(incidentId, file, imageType, zoneId);
    showResult(resultEl, `
      ✓ <strong>Image uploaded!</strong><br>
      <small>Image ID: ${result.image_point_id.substring(0, 12)}...</small>
    `);
    document.getElementById('imageUploadForm').reset();
  } catch (error) {
    showResult(resultEl, `✗ ${error.message}`, true);
  }
});

// =====================
// Event Listeners - Audio Upload (Phase 13)
// =====================

document.getElementById('audioUploadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const resultEl = document.getElementById('audioUploadResult');
  const transcriptEl = document.getElementById('transcriptPreview');
  hideResult(resultEl);
  transcriptEl.classList.add('hidden');

  const incidentId = document.getElementById('audio_incident_id').value;
  const file = document.getElementById('audio_file').files[0];
  const sourceType = document.getElementById('audio_source_type').value;

  if (!file) {
    showResult(resultEl, '✗ Please select an audio file', true);
    return;
  }

  try {
    showResult(resultEl, '⏳ Transcribing audio with Whisper...');
    const result = await uploadAudio(incidentId, file, sourceType);

    const acceptedIcon = result.accepted ? '✅' : '❌';
    showResult(resultEl, `
      ${acceptedIcon} <strong>${result.accepted ? 'Reinforcement Accepted' : 'Reinforcement Rejected'}</strong><br>
      <small>Similarity: ${(result.similarity * 100).toFixed(1)}% | Confidence: ${result.old_confidence?.toFixed(2)} → ${result.new_confidence?.toFixed(2)}</small>
    `);

    // Show transcript
    if (result.transcript) {
      transcriptEl.innerHTML = `
        <h4>📝 Transcript</h4>
        <p>${result.transcript}</p>
      `;
      transcriptEl.classList.remove('hidden');
    }

    document.getElementById('audioUploadForm').reset();
  } catch (error) {
    showResult(resultEl, `✗ ${error.message}`, true);
  }
});

// =====================
// Event Listeners - Deployments (Phase 15)
// =====================

document.getElementById('deploymentForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const resultEl = document.getElementById('deploymentResult');
  hideResult(resultEl);

  const incidentIdsRaw = document.getElementById('deploy_incident_ids').value;
  const incidentIds = incidentIdsRaw.split(',').map(id => id.trim()).filter(id => id);

  const data = {
    action_type: document.getElementById('deploy_action_type').value,
    incident_ids: incidentIds,
    assigned_unit: document.getElementById('deploy_assigned_unit').value,
    zone_id: document.getElementById('deploy_zone_id').value || null,
    notes: document.getElementById('deploy_notes').value || null,
  };

  try {
    const result = await createDeployment(data);
    showResult(resultEl, `
      🚀 <strong>Deployment Created!</strong><br>
      <small>ID: ${result.deployment_id.substring(0, 12)}... | Unit: ${result.assigned_unit}</small>
    `);
    document.getElementById('deploymentForm').reset();
  } catch (error) {
    showResult(resultEl, `✗ ${error.message}`, true);
  }
});

document.getElementById('updateDeploymentForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const resultEl = document.getElementById('updateDeploymentResult');
  hideResult(resultEl);

  const deploymentId = document.getElementById('update_deployment_id').value;
  const status = document.getElementById('update_status').value;
  const notes = document.getElementById('update_notes').value;

  try {
    const result = await updateDeploymentStatus(deploymentId, status, notes);
    showResult(resultEl, `
      ✓ <strong>Status Updated!</strong><br>
      <small>${result.old_status} → ${result.new_status}</small>
    `);
    document.getElementById('updateDeploymentForm').reset();
  } catch (error) {
    showResult(resultEl, `✗ ${error.message}`, true);
  }
});

// =====================
// Event Listeners - Image Search
// =====================

document.getElementById('imageSearchForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const resultEl = document.getElementById('imageSearchResult');
  const galleryEl = document.getElementById('imageGallery');
  const gridEl = document.getElementById('imageGalleryGrid');

  hideResult(resultEl);
  galleryEl.classList.add('hidden');

  const query = document.getElementById('image_search_query').value;
  const imageType = document.getElementById('image_search_type').value;

  try {
    showResult(resultEl, '⏳ Searching images with CLIP...');
    const result = await searchImages(query, imageType || null);

    if (result.count === 0) {
      showResult(resultEl, `🔍 No images found for "${query}"`);
      return;
    }

    showResult(resultEl, `✓ Found ${result.count} image(s) for "${query}"`);

    // Render gallery
    gridEl.innerHTML = result.results.map(img => `
      <div class="gallery-item" onclick="window.open('/${img.image_path}', '_blank')">
        <img src="/${img.image_path}" alt="${img.image_type}" loading="lazy">
        <div class="gallery-item-info">
          <span class="badge badge-${img.image_type}">${img.image_type}</span>
          <span class="gallery-score">${(img.score * 100).toFixed(0)}%</span>
        </div>
        <div class="gallery-item-meta">
          <small>Incident: ${img.incident_id.substring(0, 8)}...</small>
        </div>
      </div>
    `).join('');

    galleryEl.classList.remove('hidden');

  } catch (error) {
    showResult(resultEl, `✗ ${error.message}`, true);
  }
});

// =====================
// Initialize
// =====================

console.log('🚨 RESPOND Dashboard initialized');
console.log('📡 API Base:', API_BASE);
console.log('✅ Features: Dedup, Images (CLIP), Audio (Whisper), Deployments, Image Search');

