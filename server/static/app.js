const wsUrl = `ws://${window.location.host}/ws/dashboard`;
let ws;
let devices = [];
let testCases = [];

// DOM Elements
const wsStatus = document.getElementById('ws-status');
const deviceList = document.getElementById('device-list');
const playerSelect = document.getElementById('player-select');
const recorderSelect = document.getElementById('recorder-select');
const pairBtn = document.getElementById('pair-btn');
const addTestForm = document.getElementById('add-test-form');
const testList = document.getElementById('test-list');
const runnerStatus = document.getElementById('runner-status');
const gallery = document.getElementById('gallery');
const suiteList = document.getElementById('suite-list');
const addSuiteForm = document.getElementById('add-suite-form');
const suiteTestSelection = document.getElementById('suite-test-selection');
let testSuites = [];

// Initialize WebSocket
function connectWebSocket() {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        wsStatus.textContent = 'Connected';
        wsStatus.className = 'connection-status connected';
    };

    ws.onclose = () => {
        wsStatus.textContent = 'Disconnected. Reconnecting...';
        wsStatus.className = 'connection-status disconnected';
        setTimeout(connectWebSocket, 3000);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'device_update') {
            devices = data.devices;
            renderDevices();
        } else if (data.type === 'suite_started') {
            const suiteName = testSuites.find(s => s.id === data.suite_id)?.name || data.suite_id;
            runnerStatus.textContent = `Suite '${suiteName}' started on agent ${data.agent_id} with ${data.total_tests} tests.`;
            fetchRuns();
        } else if (data.type === 'test_run_completed') {
            fetchRuns();
            fetchRecordings(); // Show new video immediately
        } else if (data.type === 'suite_completed') {
            const suiteName = testSuites.find(s => s.id === data.suite_id)?.name || data.suite_id;
            runnerStatus.textContent = `Suite '${suiteName}' fully completed!`;
        }
    };
}

// Render Devices
function renderDevices() {
    deviceList.innerHTML = '';
    devices.forEach(device => {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `
            <div>
                <strong>${device.device_id}</strong>
                <span class="badge status-${device.status.toLowerCase()}">${device.status}</span>
            </div>
            <div class="badge">💻 PC Agent</div>
        `;
        deviceList.appendChild(div);
    });
}

// Test Cases API
async function fetchTests() {
    try {
        const res = await fetch('/api/tests');
        testCases = await res.json();
        renderTests();
    } catch (e) {
        console.error('Error fetching tests:', e);
    }
}

function renderTests() {
    testList.innerHTML = '';
    testCases.forEach(test => {
        const div = document.createElement('div');
        div.className = 'item';
        div.innerHTML = `
            <div>
                <strong>${test.name}</strong>
                <div style="font-size: 0.8rem; color: #aaa;">${test.audio_url}</div>
            </div>
            <div class="test-actions">
                <button onclick="runTest('${test.id}')">Run Test</button>
                <button style="background-color: var(--error);" onclick="deleteTest('${test.id}')">Delete</button>
            </div>
        `;
        testList.appendChild(div);
    });
    
    // Also update suite test selection checkboxes
    suiteTestSelection.innerHTML = '';
    testCases.forEach(test => {
        const lbl = document.createElement('label');
        lbl.style.display = 'block';
        lbl.style.marginBottom = '4px';
        lbl.innerHTML = `<input type="checkbox" value="${test.id}" class="suite-test-cb"> ${test.name}`;
        suiteTestSelection.appendChild(lbl);
    });
}

addTestForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('test-name').value;
    const audio_url = document.getElementById('test-audio-url').value;
    const desc = document.getElementById('test-desc').value;

    try {
        await fetch('/api/tests', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, audio_url, description: desc })
        });
        addTestForm.reset();
        fetchTests();
    } catch (e) {
        console.error('Error adding test:', e);
    }
});

async function deleteTest(id) {
    if(confirm('Delete test?')) {
        await fetch(`/api/tests/${id}`, { method: 'DELETE' });
        fetchTests();
    }
}

// Suites API
async function fetchSuites() {
    try {
        const res = await fetch('/api/suites');
        testSuites = await res.json();
        renderSuites();
    } catch (e) {
        console.error('Error fetching suites:', e);
    }
}

function renderSuites() {
    suiteList.innerHTML = '';
    testSuites.forEach(suite => {
        const div = document.createElement('div');
        div.className = 'item';
        const caseCount = suite.test_case_ids ? suite.test_case_ids.length : 0;
        div.innerHTML = `
            <div>
                <strong>${suite.name}</strong>
                <div style="font-size: 0.8rem; color: #aaa;">${caseCount} cases</div>
            </div>
            <div class="test-actions">
                <button onclick="runSuite('${suite.id}')">Run</button>
                <button onclick="queueSuite('${suite.id}')">Queue</button>
                <button style="background-color: var(--error);" onclick="deleteSuite('${suite.id}')">Del</button>
            </div>
        `;
        suiteList.appendChild(div);
    });
}

addSuiteForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('suite-name').value;
    const desc = document.getElementById('suite-desc').value;
    const checkboxes = document.querySelectorAll('.suite-test-cb:checked');
    const test_case_ids = Array.from(checkboxes).map(cb => cb.value);

    if (test_case_ids.length === 0) {
        alert('Please select at least one test case.');
        return;
    }

    try {
        await fetch('/api/suites', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description: desc, test_case_ids })
        });
        addSuiteForm.reset();
        fetchSuites();
    } catch (e) {
        console.error('Error adding suite:', e);
    }
});

async function deleteSuite(id) {
    if(confirm('Delete suite?')) {
        await fetch(`/api/suites/${id}`, { method: 'DELETE' });
        fetchSuites();
    }
}

// Run Test
async function runTest(id) {
    if (devices.length === 0) {
        alert('No PC Agents connected!');
        return;
    }
    
    // For simplicity, pick the first available agent
    const agentId = devices[0].device_id;
    runnerStatus.textContent = `Starting test on agent ${agentId}...`;
    
    try {
        const res = await fetch(`/api/tests/${id}/run?agent_id=${agentId}`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to run test');
        }
        const data = await res.json();
        
        // Simple polling for UI demo (in real app, we'd use WS events for status)
        let dots = '';
        const pollInterval = setInterval(() => {
            dots = dots.length > 3 ? '' : dots + '.';
            runnerStatus.textContent = `Test ${data.test_run_id} running${dots}\nCheck device status panel...`;
        }, 500);

        // Assume test takes ~60s, then upload takes some time
        setTimeout(() => {
            clearInterval(pollInterval);
            runnerStatus.textContent = 'Test likely completed. Refreshing gallery...';
            setTimeout(fetchRecordings, 5000);
        }, 65000);

    } catch (e) {
        runnerStatus.textContent = `Error: ${e.message}`;
    }
}

// Excel Import Logic
const toggleImportBtn = document.getElementById('toggle-import-btn');
const importSuiteForm = document.getElementById('import-suite-form');
const importPreviewContainer = document.getElementById('import-preview-container');
const previewTableBody = document.getElementById('preview-table-body');
const importErrors = document.getElementById('import-errors');
const confirmImportBtn = document.getElementById('confirm-import-btn');
const cancelImportBtn = document.getElementById('cancel-import-btn');
let pendingImportData = null;

toggleImportBtn.addEventListener('click', () => {
    const isHidden = importSuiteForm.style.display === 'none';
    importSuiteForm.style.display = isHidden ? 'block' : 'none';
    if (!isHidden) {
        importPreviewContainer.style.display = 'none';
        importSuiteForm.reset();
    }
});

cancelImportBtn.addEventListener('click', () => {
    importPreviewContainer.style.display = 'none';
    importSuiteForm.style.display = 'none';
    importSuiteForm.reset();
    pendingImportData = null;
});

importSuiteForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('excel-file');
    if (!fileInput.files.length) return;
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        const res = await fetch('/api/test-suites/parse-import', {
            method: 'POST',
            body: formData
        });
        
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Import failed');
        
        pendingImportData = data.preview_data;
        
        // Render preview table
        previewTableBody.innerHTML = '';
        let hasErrors = false;
        
        if (data.errors && data.errors.length > 0) {
            importErrors.textContent = data.errors.join('\n');
            hasErrors = true;
        } else {
            importErrors.textContent = '';
        }
        
        data.preview_data.forEach(suite => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid #333';
            
            if (suite.is_duplicate) {
                tr.style.color = 'var(--error)';
                hasErrors = true;
            }
            
            tr.innerHTML = `
                <td style="padding: 5px;">${suite.suite_name}</td>
                <td style="padding: 5px;">${suite.case_count}</td>
                <td style="padding: 5px;">${suite.is_duplicate ? 'Duplicate' : 'Valid'}</td>
            `;
            previewTableBody.appendChild(tr);
        });
        
        importPreviewContainer.style.display = 'block';
        confirmImportBtn.disabled = hasErrors || data.preview_data.length === 0;
        
    } catch (e) {
        alert(e.message);
    }
});

confirmImportBtn.addEventListener('click', async () => {
    if (!pendingImportData) return;
    
    confirmImportBtn.disabled = true;
    confirmImportBtn.textContent = 'Saving...';
    
    try {
        const res = await fetch('/api/test-suites/confirm-import', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pendingImportData)
        });
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to save imported suites');
        }
        
        alert('Suites imported successfully!');
        importPreviewContainer.style.display = 'none';
        importSuiteForm.style.display = 'none';
        importSuiteForm.reset();
        pendingImportData = null;
        
        fetchTests();
        fetchSuites();
    } catch (e) {
        alert(e.message);
    } finally {
        confirmImportBtn.disabled = false;
        confirmImportBtn.textContent = 'Confirm & Save';
    }
});

// Run Suite
async function runSuite(id) {
    if (devices.length === 0) {
        alert('No PC Agents connected!');
        return;
    }
    
    const agentId = devices[0].device_id;
    const executedBy = document.getElementById('executor-name').value;
    runnerStatus.textContent = `Starting suite on agent ${agentId}...`;
    
    try {
        const res = await fetch(`/api/suites/${id}/run?agent_id=${agentId}&executed_by=${encodeURIComponent(executedBy)}`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to run suite');
        }
        const data = await res.json();
        
        runnerStatus.textContent = `Suite started with ${data.run_statuses.length} tests on agent ${agentId}. Executed by: ${executedBy}`;
    } catch (e) {
        runnerStatus.textContent = `Error: ${e.message}`;
    }
}

async function queueSuite(id) {
    const executedBy = document.getElementById('executor-name').value;
    try {
        const res = await fetch(`/api/suites/${id}/queue?executed_by=${encodeURIComponent(executedBy)}`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to queue suite');
        }
        runnerStatus.textContent = `Suite enqueued. Waiting for agents...`;
    } catch (e) {
        runnerStatus.textContent = `Error: ${e.message}`;
    }
}

// Recordings API
async function fetchRecordings() {
    try {
        const res = await fetch('/api/recordings');
        const recordings = await res.json();
        renderGallery(recordings);
    } catch (e) {
        console.error('Error fetching recordings:', e);
    }
}

function renderGallery(recordings) {
    gallery.innerHTML = '';
    recordings.forEach(file => {
        const div = document.createElement('div');
        div.className = 'video-card';
        div.innerHTML = `
            <video controls src="/recordings/${file}" preload="metadata"></video>
            <div class="video-info">
                ${file}
            </div>
        `;
        gallery.appendChild(div);
    });
}

const historyList = document.getElementById('history-list');

async function fetchRuns() {
    try {
        const res = await fetch('/api/runs');
        const runs = await res.json();
        renderHistory(runs);
        
        // Calculate suite progress
        const suiteProgress = {};
        runs.forEach(run => {
            if (run.suite_id) {
                if (!suiteProgress[run.suite_id]) {
                    suiteProgress[run.suite_id] = { total: 0, completed: 0, executed_by: run.executed_by };
                }
                suiteProgress[run.suite_id].total++;
                if (run.status === 'completed' || run.status === 'failed') {
                    suiteProgress[run.suite_id].completed++;
                }
            }
        });
        
        // Update suite progress in UI
        let progressMsg = '';
        for (const [suiteId, prog] of Object.entries(suiteProgress)) {
            if (prog.completed < prog.total) {
                const suiteName = testSuites.find(s => s.id === suiteId)?.name || suiteId;
                progressMsg += `Suite '${suiteName}' by ${prog.executed_by || 'Auto'}: ${prog.completed}/${prog.total} completed. `;
            }
        }
        if (progressMsg && runnerStatus.textContent.indexOf('Error') === -1) {
            runnerStatus.textContent = progressMsg;
        }

    } catch (e) {
        console.error('Error fetching runs:', e);
    }
}

function renderHistory(runs) {
    if (!historyList) return;
    historyList.innerHTML = '';
    // Sort by newest first
    runs.sort((a, b) => b.timestamp - a.timestamp).forEach(run => {
        const div = document.createElement('div');
        div.style.padding = '4px';
        div.style.borderBottom = '1px solid #444';
        div.style.fontSize = '0.85rem';
        const date = new Date(run.timestamp * 1000).toLocaleTimeString();
        const testName = testCases.find(t => t.id === run.test_id)?.name || run.test_id;
        let executorInfo = run.executed_by ? ` (by ${run.executed_by})` : '';
        div.innerHTML = `[${date}] ${testName}${executorInfo}: <span class="badge status-${run.status.toLowerCase()}">${run.status}</span>`;
        historyList.appendChild(div);
    });
}

// Poll runs every 2s
setInterval(fetchRuns, 2000);

// Init
connectWebSocket();
fetchTests();
fetchSuites();
fetchRecordings();
fetchRuns();
