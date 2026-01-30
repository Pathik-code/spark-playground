// API Base URL
const API_BASE = '';

// State
let workers = [
    { memory: '1g', cores: 1 },
    { memory: '1g', cores: 1 }
];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    refreshClusterStatus();
    refreshNotebooks();
    refreshLogs();
    renderWorkers();

    // Auto-refresh status every 5 seconds
    setInterval(refreshClusterStatus, 5000);

    // Auto-refresh logs every 3 seconds
    setInterval(refreshLogs, 3000);
});

// Worker Management
function renderWorkers() {
    const tbody = document.getElementById('workersTableBody');
    tbody.innerHTML = '';

    workers.forEach((worker, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>Worker ${index + 1}</strong></td>
            <td>
                <select class="form-control-small" onchange="updateWorker(${index}, 'memory', this.value)">
                    <option value="512m" ${worker.memory === '512m' ? 'selected' : ''}>512 MB</option>
                    <option value="1g" ${worker.memory === '1g' ? 'selected' : ''}>1 GB</option>
                    <option value="2g" ${worker.memory === '2g' ? 'selected' : ''}>2 GB</option>
                    <option value="4g" ${worker.memory === '4g' ? 'selected' : ''}>4 GB</option>
                    <option value="8g" ${worker.memory === '8g' ? 'selected' : ''}>8 GB</option>
                </select>
            </td>
            <td>
                <select class="form-control-small" onchange="updateWorker(${index}, 'cores', parseInt(this.value))">
                    <option value="1" ${worker.cores === 1 ? 'selected' : ''}>1 Core</option>
                    <option value="2" ${worker.cores === 2 ? 'selected' : ''}>2 Cores</option>
                    <option value="3" ${worker.cores === 3 ? 'selected' : ''}>3 Cores</option>
                    <option value="4" ${worker.cores === 4 ? 'selected' : ''}>4 Cores</option>
                    <option value="6" ${worker.cores === 6 ? 'selected' : ''}>6 Cores</option>
                    <option value="8" ${worker.cores === 8 ? 'selected' : ''}>8 Cores</option>
                </select>
            </td>
            <td>
                <button class="btn-icon-small btn-delete" onclick="removeWorker(${index})" title="Remove Worker">
                    🗑️
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateWorker(index, field, value) {
    workers[index][field] = value;
    console.log(`Updated worker ${index + 1}: ${field} = ${value}`);
}

function addWorker() {
    workers.push({ memory: '1g', cores: 1 });
    renderWorkers();
    showToast('✓ Worker added. Click "Apply Configuration" to restart cluster.', 'info');
}

function removeWorker(index) {
    if (workers.length <= 1) {
        showToast('✗ Cannot remove last worker. Cluster needs at least 1 worker.', 'error');
        return;
    }
    workers.splice(index, 1);
    renderWorkers();
    showToast('✓ Worker removed. Click "Apply Configuration" to restart cluster.', 'info');
}

// Cluster Management
async function refreshClusterStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/cluster/status`);
        const status = await response.json();

        // Update status indicator
        const statusEl = document.getElementById('clusterStatus');
        if (status.running) {
            statusEl.innerHTML = '<span class="status-badge status-online">Online</span>';
            document.getElementById('masterLink').classList.remove('disabled');
        } else {
            statusEl.innerHTML = '<span class="status-badge status-offline">Offline</span>';
            document.getElementById('masterLink').classList.add('disabled');
        }

        // Update worker count
        document.getElementById('workerCount').textContent = status.worker_count;

        // Animate refresh icon
        const refreshIcon = document.getElementById('refreshIcon');
        refreshIcon.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            refreshIcon.style.transform = 'rotate(0deg)';
        }, 500);

    } catch (error) {
        console.error('Error fetching cluster status:', error);
    }
}

async function startCluster() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/api/cluster/start`, {
            method: 'POST'
        });

        if (response.ok) {
            showToast('✓ Cluster start initiated', 'success');
            setTimeout(refreshClusterStatus, 2000);
            setTimeout(refreshLogs, 1000);
        } else {
            const error = await response.json();
            showToast(`✗ Failed to start cluster: ${error.detail}`, 'error');
        }
    } catch (error) {
        showToast(`✗ Error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function stopCluster() {
    if (!confirm('Are you sure you want to stop the Spark cluster?')) {
        return;
    }

    showLoading();
    try {
        const response = await fetch(`${API_BASE}/api/cluster/stop`, {
            method: 'POST'
        });

        if (response.ok) {
            showToast('✓ Cluster stopped successfully', 'success');
            setTimeout(refreshClusterStatus, 2000);
            setTimeout(refreshLogs, 1000);
        } else {
            const error = await response.json();
            showToast(`✗ Failed to stop cluster: ${error.detail}`, 'error');
        }
    } catch (error) {
        showToast(`✗ Error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function applyConfig() {
    const config = {
        workers: workers.map(w => ({
            memory: w.memory,
            cores: w.cores
        }))
    };

    console.log('Applying config:', config);

    showLoading();
    try {
        const response = await fetch(`${API_BASE}/api/cluster/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            const result = await response.json();
            showToast(`✓ ${result.message}`, 'success');
            setTimeout(refreshClusterStatus, 3000);
            setTimeout(refreshLogs, 1000);
        } else {
            const error = await response.json();
            const errorMsg = typeof error.detail === 'string'
                ? error.detail
                : JSON.stringify(error.detail || error);
            showToast(`✗ Failed to apply configuration: ${errorMsg}`, 'error');
            console.error('Configuration error:', error);
            setTimeout(refreshLogs, 1000);
        }
    } catch (error) {
        showToast(`✗ Error: ${error.message}`, 'error');
        console.error('Request error:', error);
    } finally {
        hideLoading();
    }
}

// Logs Management
async function refreshLogs() {
    try {
        const response = await fetch(`${API_BASE}/api/cluster/logs`);
        const data = await response.json();

        const logsContainer = document.getElementById('logsContainer');

        if (data.logs && data.logs.length > 0) {
            logsContainer.innerHTML = data.logs.map(log =>
                `<div class="log-entry">${escapeHtml(log)}</div>`
            ).join('');

            // Auto-scroll to bottom
            logsContainer.scrollTop = logsContainer.scrollHeight;
        } else {
            logsContainer.innerHTML = '<div class="logs-empty">No logs yet. Logs will appear when you perform cluster operations.</div>';
        }
    } catch (error) {
        console.error('Error fetching logs:', error);
    }
}

async function clearLogs() {
    try {
        await fetch(`${API_BASE}/api/cluster/logs/clear`, {
            method: 'POST'
        });
        refreshLogs();
        showToast('✓ Logs cleared', 'success');
    } catch (error) {
        showToast(`✗ Error clearing logs: ${error.message}`, 'error');
    }
}

// Notebook Management
async function refreshNotebooks() {
    try {
        const response = await fetch(`${API_BASE}/api/notebooks/list`);
        const data = await response.json();

        const listEl = document.getElementById('notebookList');

        if (data.notebooks && data.notebooks.length > 0) {
            listEl.innerHTML = data.notebooks.map(nb => `
                <div class="notebook-item">
                    <div class="notebook-info">
                        <div class="notebook-name">${escapeHtml(nb.name)}</div>
                        <div class="notebook-meta">Template: ${escapeHtml(nb.template)} • Created: ${new Date(nb.created_at).toLocaleString()}</div>
                    </div>
                    <div class="notebook-actions">
                        <button class="btn-icon" onclick="openNotebook('${nb.id}')" title="Open">📂</button>
                        <button class="btn-icon btn-delete" onclick="deleteNotebook('${nb.id}')" title="Delete">🗑️</button>
                    </div>
                </div>
            `).join('');
        } else {
            listEl.innerHTML = '<p class="empty-state">No notebooks created yet.</p>';
        }
    } catch (error) {
        console.error('Error fetching notebooks:', error);
    }
}

async function createNotebook(event) {
    event.preventDefault();

    const name = document.getElementById('notebookName').value;
    const template = document.getElementById('notebookTemplate').value;

    showLoading();
    try {
        const response = await fetch(`${API_BASE}/api/notebooks/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, template })
        });

        if (response.ok) {
            showToast('✓ Notebook created successfully', 'success');
            hideCreateNotebookModal();
            refreshNotebooks();
            document.getElementById('createNotebookForm').reset();
        } else {
            const error = await response.json();
            showToast(`✗ Failed to create notebook: ${error.detail}`, 'error');
        }
    } catch (error) {
        showToast(`✗ Error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function openNotebook(notebookId) {
    try {
        const response = await fetch(`${API_BASE}/api/notebooks/${notebookId}/url`);
        const data = await response.json();

        if (data.url) {
            window.open(data.url, '_blank');
        }
    } catch (error) {
        showToast(`✗ Error opening notebook: ${error.message}`, 'error');
    }
}

async function deleteNotebook(notebookId) {
    if (!confirm('Are you sure you want to delete this notebook?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/notebooks/${notebookId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('✓ Notebook deleted', 'success');
            refreshNotebooks();
        } else {
            const error = await response.json();
            showToast(`✗ Failed to delete notebook: ${error.detail}`, 'error');
        }
    } catch (error) {
        showToast(`✗ Error: ${error.message}`, 'error');
    }
}

// Modal Management
function showCreateNotebookModal() {
    document.getElementById('createNotebookModal').classList.add('active');
}

function hideCreateNotebookModal() {
    document.getElementById('createNotebookModal').classList.remove('active');
}

// UI Helpers
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    const container = document.getElementById('toastContainer');
    container.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
