const wsUrl = `ws://${window.location.host}/ws/dashboard`;
let ws;
let devices = [];
let testCases = [];

// DOM Elements
const wsStatus = document.getElementById('ws-status');
const deviceList = document.getElementById('device-list');
const addTestForm = document.getElementById('add-test-form');
const testList = document.getElementById('test-list');
const runnerStatus = document.getElementById('runner-status');
const gallery = document.getElementById('gallery');
const suiteList = document.getElementById('suite-list');
const suiteTestSelection = document.getElementById('suite-test-selection');
let testSuites = [];
let allRuns = [];

const runningStates = { suites: {}, tests: {} };
const selectedAgents = { suites: {}, tests: {} };

function handleAgentChange(type, id, value) {
    selectedAgents[type][id] = value;
}

function getAgentDropdownHtml(type, id) {
    const currentVal = selectedAgents[type][id] || 'auto';
    let optionsHtml = `<option value="auto" ${currentVal === 'auto' ? 'selected' : ''}>Auto-assign</option>`;
    
    devices.forEach(d => {
        if (d.role === 'pc_agent' && (d.status === 'online' || d.status === 'idle' || d.status === 'running_test')) {
            const selected = currentVal === d.device_id ? 'selected' : '';
            optionsHtml += `<option value="${d.device_id}" ${selected}>${d.device_id} (${d.status})</option>`;
        }
    });
    
    return `<select class="agent-dropdown" id="agent-${type}-${id}" style="width: 180px; padding: 4px; border-radius: 4px; background: var(--bg-color); color: var(--text-color); border: 1px solid var(--border-color);" onchange="handleAgentChange('${type}', '${id}', this.value)" onclick="event.stopPropagation();">
        ${optionsHtml}
    </select>`;
}

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
    
    const agentSelect = document.getElementById('agent-select');
    if (agentSelect) {
        const currentVal = agentSelect.value;
        agentSelect.innerHTML = '<option value="auto">Auto-assign (Idle Agent)</option>';
        
        devices.forEach(device => {
            if (device.role === 'pc_agent' && (device.status === 'online' || device.status === 'idle' || device.status === 'running_test')) {
                const opt = document.createElement('option');
                opt.value = device.device_id;
                opt.textContent = `${device.device_id} (${device.status})`;
                agentSelect.appendChild(opt);
            }
        });
        
        // Restore selection if still exists
        if (Array.from(agentSelect.options).some(o => o.value === currentVal)) {
            agentSelect.value = currentVal;
        }
    }
    
    // Also re-render the combined list to update dropdown options
    renderCombinedList();
    
    devices.forEach(device => {
        const div = document.createElement('div');
        div.className = 'item';
        
        let progressHtml = '';
        if (device.status === 'running_test' && device.current_suite_name && device.current_test_progress) {
            progressHtml = `<div style="font-size: 0.85rem; color: var(--accent-color); margin-top: 5px;">
                Đang chạy: ${device.current_suite_name} (Test ${device.current_test_progress})
            </div>`;
        }

        div.innerHTML = `
            <div style="flex-direction: column; align-items: flex-start; display: flex;">
                <div>
                    <strong>${device.device_id}</strong>
                    <span class="badge status-${device.status.toLowerCase()}">${device.status}</span>
                </div>
                ${progressHtml}
            </div>
            <div class="badge" style="align-self: flex-start;">💻 PC Agent</div>
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
    if (!testList) return;
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

let selectedAudioFile = null;
const audioDropZone = document.getElementById('audio-drop-zone');
const testAudioFileInput = document.getElementById('test-audio-file');
const audioFileName = document.getElementById('audio-file-name');

const _preventDefaults = (e) => {
    e.preventDefault();
    e.stopPropagation();
};

if (audioDropZone) {
    audioDropZone.addEventListener('click', () => testAudioFileInput.click());
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        audioDropZone.addEventListener(eventName, _preventDefaults, false);
    });
    ['dragenter', 'dragover'].forEach(eventName => {
        audioDropZone.addEventListener(eventName, () => audioDropZone.classList.add('dragover'), false);
    });
    ['dragleave', 'drop'].forEach(eventName => {
        audioDropZone.addEventListener(eventName, () => audioDropZone.classList.remove('dragover'), false);
    });
    audioDropZone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files.length > 0) {
            selectedAudioFile = e.dataTransfer.files[0];
            audioFileName.textContent = selectedAudioFile.name;
        }
    });
    testAudioFileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            selectedAudioFile = this.files[0];
            audioFileName.textContent = selectedAudioFile.name;
        }
    });
}

addTestForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('test-name').value;
    const utterance = document.getElementById('test-utterance').value;
    const desc = document.getElementById('test-desc').value;

    if (!selectedAudioFile) {
        alert("Please select an audio file");
        return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('utterance', utterance);
    formData.append('description', desc);
    formData.append('audio', selectedAudioFile);

    try {
        await fetch('/api/tests/upload', {
            method: 'POST',
            body: formData
        });
        addTestForm.reset();
        selectedAudioFile = null;
        if(audioFileName) audioFileName.textContent = "";
        fetchTests();
        testModal.style.display = 'none';
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
    if (!suiteList) return;
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
                <button style="background-color: var(--accent-color);" onclick="window.open('/verify.html?suite_id=${suite.id}', '_blank')">Verify</button>
                <button onclick="runSuite('${suite.id}')">Run</button>
                <button onclick="queueSuite('${suite.id}')">Queue</button>
                <button style="background-color: var(--error);" onclick="deleteSuite('${suite.id}')">Del</button>
            </div>
        `;
        suiteList.appendChild(div);
    });
}
async function deleteSuite(id) {
    if(confirm('Delete suite?')) {
        await fetch(`/api/suites/${id}`, { method: 'DELETE' });
        fetchSuites();
    }
}

// Run Test
async function runTest(id) {
    const agentSelect = document.getElementById('agent-select');
    const agentId = agentSelect ? agentSelect.value : 'auto';
    
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

// Modal Logic
const testModal = document.getElementById('test-modal');
const openTestModalBtn = document.getElementById('open-test-modal-btn');
const closeModalBtns = document.querySelectorAll('.close-btn');

if (openTestModalBtn) {
    openTestModalBtn.addEventListener('click', () => {
        testModal.style.display = 'flex';
    });
}

closeModalBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        testModal.style.display = 'none';
    });
});

window.addEventListener('click', (e) => {
    if (e.target === testModal) {
        testModal.style.display = 'none';
    }
});

// Drag and Drop Logic
const dropZone = document.getElementById('drop-zone');
const excelFileInput = document.getElementById('excel-file');
const uploadStatus = document.getElementById('upload-status');

let selectedZipFile = null;
const zipDropZone = document.getElementById('zip-drop-zone');
const zipFileInput = document.getElementById('zip-file');

if (dropZone) {
    dropZone.addEventListener('click', () => {
        excelFileInput.click();
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, _preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        handleFiles(e.dataTransfer.files);
    });

    excelFileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            uploadStatus.textContent = `Selected excel file: ${file.name}`;
            processExcelFile(file);
        }
    }
}

if (zipDropZone) {
    zipDropZone.addEventListener('click', () => zipFileInput.click());
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        zipDropZone.addEventListener(eventName, _preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        zipDropZone.addEventListener(eventName, () => zipDropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        zipDropZone.addEventListener(eventName, () => zipDropZone.classList.remove('dragover'), false);
    });

    zipDropZone.addEventListener('drop', (e) => {
        if (e.dataTransfer.files.length > 0) {
            selectedZipFile = e.dataTransfer.files[0];
            uploadStatus.textContent += ` | Selected ZIP: ${selectedZipFile.name}`;
        }
    });

    zipFileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            selectedZipFile = this.files[0];
            uploadStatus.textContent += ` | Selected ZIP: ${selectedZipFile.name}`;
        }
    });
}

// Excel Import Logic
const importPreviewContainer = document.getElementById('import-preview-container');
const previewTableBody = document.getElementById('preview-table-body');
const importErrors = document.getElementById('import-errors');
const confirmImportBtn = document.getElementById('confirm-import-btn');
const cancelImportBtn = document.getElementById('cancel-import-btn');
let pendingImportData = null;

cancelImportBtn.addEventListener('click', () => {
    importPreviewContainer.style.display = 'none';
    pendingImportData = null;
});

async function processExcelFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    uploadStatus.textContent = 'Processing...';
    
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
}

confirmImportBtn.addEventListener('click', async () => {
    if (!pendingImportData) return;
    
    confirmImportBtn.disabled = true;
    confirmImportBtn.textContent = 'Saving...';
    
    const formData = new FormData();
    formData.append('suites_json', JSON.stringify(pendingImportData));
    if (selectedZipFile) {
        formData.append('zip_file', selectedZipFile);
    }
    
    try {
        const res = await fetch('/api/test-suites/confirm-import', {
            method: 'POST',
            body: formData
        });
        
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to save imported suites');
        }
        
        alert('Suites imported successfully!');
        importPreviewContainer.style.display = 'none';
        pendingImportData = null;
        selectedZipFile = null;
        uploadStatus.textContent = '';
        
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
    const agentSelect = document.getElementById('agent-select');
    const agentId = agentSelect ? agentSelect.value : 'auto';
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

async function runSuiteItem(id) {
    runningStates.suites[id] = true;
    renderCombinedList();
    
    const agentId = selectedAgents['suites'][id] || 'auto';
    const executedBy = document.getElementById('executor-name').value;
    
    try {
        const res = await fetch(`/api/suites/${id}/run?agent_id=${agentId}&executed_by=${encodeURIComponent(executedBy)}`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to run suite');
        }
        const data = await res.json();
        console.log(`Suite started on agent ${agentId}`);
    } catch (e) {
        alert(`Error: ${e.message}`);
    } finally {
        delete runningStates.suites[id];
        renderCombinedList();
    }
}

async function runTestItem(id) {
    runningStates.tests[id] = true;
    renderCombinedList();
    
    const agentId = selectedAgents['tests'][id] || 'auto';
    
    try {
        const res = await fetch(`/api/tests/${id}/run?agent_id=${agentId}`, { method: 'POST' });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to run test');
        }
        console.log(`Test started on agent ${agentId}`);
    } catch (e) {
        alert(`Error: ${e.message}`);
    } finally {
        delete runningStates.tests[id];
        renderCombinedList();
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
    if (!gallery) return;
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
        allRuns = await res.json();
        renderHistory(allRuns);
        
        // Calculate suite progress
        const suiteProgress = {};
        allRuns.forEach(run => {
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

        renderCombinedList();

    } catch (e) {
        console.error('Error fetching runs:', e);
    }
}

function renderCombinedList() {
    const combinedList = document.getElementById('combined-list');
    if (!combinedList) return;
    
    combinedList.innerHTML = '';
    
    // Render Suites
    testSuites.forEach(suite => {
        const div = document.createElement('div');
        div.className = 'item';
        div.style.cursor = 'pointer';
        div.onclick = () => window.open(`/verify.html?suite_id=${suite.id}`, '_blank');
        
        let statusHtml = '<span class="badge" style="background-color: var(--border-color);">Unverified</span>';
        const suiteRuns = allRuns.filter(r => r.suite_id === suite.id);
        const hasVerifiedRun = suiteRuns.some(r => r.verified === true);
        if (hasVerifiedRun) {
            statusHtml = '<span class="badge" style="background-color: rgba(3, 218, 198, 0.2); color: var(--success);">Verified</span>';
        }
        
        const isRunning = runningStates.suites[suite.id];
        const btnClass = isRunning ? 'run-btn loading' : 'run-btn';
        const btnText = isRunning ? 'Running...' : 'Run';
        const btnDisabled = isRunning ? 'disabled' : '';
        const dropdownHtml = getAgentDropdownHtml('suites', suite.id);
        
        div.innerHTML = `
            <div style="flex: 1;">
                <strong>📁 Suite: ${suite.name}</strong>
                <div style="font-size: 0.8rem; color: #aaa;">${suite.test_case_ids ? suite.test_case_ids.length : 0} cases</div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                ${statusHtml}
                ${dropdownHtml}
                <button class="${btnClass}" ${btnDisabled} onclick="event.stopPropagation(); runSuiteItem('${suite.id}')">${btnText}</button>
                <button style="background-color: var(--error);" onclick="event.stopPropagation(); deleteSuite('${suite.id}')">Del</button>
            </div>
        `;
        combinedList.appendChild(div);
    });
    
    // Render Individual Tests
    testCases.forEach(test => {
        const div = document.createElement('div');
        div.className = 'item';
        
        let statusHtml = '<span class="badge" style="background-color: var(--border-color);">Unverified</span>';
        const testRuns = allRuns.filter(r => r.test_id === test.id);
        const hasVerifiedRun = testRuns.some(r => r.verified === true);
        if (hasVerifiedRun) {
            statusHtml = '<span class="badge" style="background-color: rgba(3, 218, 198, 0.2); color: var(--success);">Verified</span>';
        }
        
        const isRunning = runningStates.tests[test.id];
        const btnClass = isRunning ? 'run-btn loading' : 'run-btn';
        const btnText = isRunning ? 'Running...' : 'Run';
        const btnDisabled = isRunning ? 'disabled' : '';
        const dropdownHtml = getAgentDropdownHtml('tests', test.id);

        div.innerHTML = `
            <div style="flex: 1;">
                <strong>📄 Test: ${test.name}</strong>
                <div style="font-size: 0.8rem; color: #aaa;">${test.audio_url}</div>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                ${statusHtml}
                ${dropdownHtml}
                <button class="${btnClass}" ${btnDisabled} onclick="event.stopPropagation(); runTestItem('${test.id}')">${btnText}</button>
                <button style="background-color: var(--error);" onclick="event.stopPropagation(); deleteTest('${test.id}')">Del</button>
            </div>
        `;
        combinedList.appendChild(div);
    });
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
