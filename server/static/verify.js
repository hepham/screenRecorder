document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const suiteId = urlParams.get('suite_id');

    if (!suiteId) {
        alert("No Suite ID provided!");
        return;
    }

    let currentSuite = null;
    let allTests = [];
    let allRuns = [];
    let testDataMap = new Map(); // test_id -> { test, latest_run }
    let currentTestId = null;

    // DOM Elements
    const suiteTitleEl = document.getElementById('suite-title');
    const testCaseListEl = document.getElementById('test-case-list');
    const emptyStateEl = document.getElementById('empty-state');
    const verificationAreaEl = document.getElementById('verification-area');
    
    // Media elements
    const testTitleEl = document.getElementById('current-test-title');
    const testUtteranceEl = document.getElementById('test-utterance');
    const testVideoEl = document.getElementById('test-video');
    const testAudioEl = document.getElementById('test-audio');
    const runInfoEl = document.getElementById('run-info');
    
    // Validation controls
    const reasonInput = document.getElementById('verify-reason');
    const saveStatusEl = document.getElementById('save-status');
    const manualSaveBtn = document.getElementById('manual-save-btn');

    // Current verification state
    let verificationState = {
        pass_lng: null,
        pass_asr: null,
        pass_capsule: null,
        pass_tts: null,
        reason: ""
    };

    // Load Data
    async function loadData() {
        try {
            // Fetch suite
            const suiteRes = await fetch(`/api/suites/${suiteId}`);
            if (!suiteRes.ok) throw new Error("Suite not found");
            currentSuite = await suiteRes.json();
            suiteTitleEl.textContent = `Suite: ${currentSuite.name}`;

            // Fetch tests
            const testsRes = await fetch('/api/tests');
            allTests = await testsRes.json();

            // Fetch runs
            const runsRes = await fetch('/api/runs');
            allRuns = await runsRes.json();

            // Map data
            buildTestDataMap();
            renderSidebar();

        } catch (e) {
            console.error("Error loading data:", e);
            suiteTitleEl.textContent = "Error loading suite data";
        }
    }

    function buildTestDataMap() {
        testDataMap.clear();
        
        if (!currentSuite.test_case_ids) return;

        currentSuite.test_case_ids.forEach(testId => {
            const test = allTests.find(t => t.id === testId);
            if (!test) return;

            // Find all runs for this test in this suite
            const testRuns = allRuns.filter(r => r.test_id === testId && r.suite_id === suiteId);
            
            // Sort by timestamp descending to get the latest
            testRuns.sort((a, b) => b.timestamp - a.timestamp);
            const latestRun = testRuns.length > 0 ? testRuns[0] : null;

            testDataMap.set(testId, {
                test: test,
                latest_run: latestRun
            });
        });
    }

    function renderSidebar() {
        testCaseListEl.innerHTML = '';
        
        for (const [testId, data] of testDataMap.entries()) {
            const div = document.createElement('div');
            div.className = `test-case-item ${testId === currentTestId ? 'active' : ''}`;
            div.dataset.id = testId;
            
            // Determine status
            let statusClass = 'status-norun';
            let statusText = 'No Run';
            
            if (data.latest_run) {
                if (data.latest_run.verified) {
                    statusClass = 'status-verified';
                    statusText = 'Verified';
                } else if (data.latest_run.status === 'completed') {
                    statusClass = 'status-pending';
                    statusText = 'Needs Verification';
                } else {
                    statusClass = 'status-failed';
                    statusText = data.latest_run.status;
                }
            }
            
            div.innerHTML = `
                <div style="font-weight: bold; margin-bottom: 5px;">${data.test.name}</div>
                <div style="font-size: 0.8rem; color: #aaa; display: flex; align-items: center;">
                    <span class="status-indicator ${statusClass}"></span> ${statusText}
                </div>
            `;
            
            div.addEventListener('click', () => selectTestCase(testId));
            testCaseListEl.appendChild(div);
        }
    }

    async function selectTestCase(testId) {
        // Auto-save previous before switching if needed
        if (currentTestId && currentTestId !== testId) {
            await autoSaveCurrent();
        }

        currentTestId = testId;
        
        // Update active class
        document.querySelectorAll('.test-case-item').forEach(el => {
            el.classList.toggle('active', el.dataset.id === testId);
        });

        const data = testDataMap.get(testId);
        if (!data) return;

        emptyStateEl.style.display = 'none';
        verificationAreaEl.style.display = 'block';

        testTitleEl.textContent = data.test.name;
        testUtteranceEl.textContent = data.test.description || data.test.name;
        testAudioEl.src = data.test.audio_url;

        if (data.latest_run && data.latest_run.video_filename) {
            testVideoEl.src = `/recordings/${data.latest_run.video_filename}`;
            const date = new Date(data.latest_run.timestamp * 1000).toLocaleString();
            runInfoEl.innerHTML = `Run Date: ${date} <br>Run ID: ${data.latest_run.test_run_id}`;
            
            // Load existing verification state
            verificationState.pass_lng = data.latest_run.pass_lng;
            verificationState.pass_asr = data.latest_run.pass_asr;
            verificationState.pass_capsule = data.latest_run.pass_capsule;
            verificationState.pass_tts = data.latest_run.pass_tts;
            verificationState.reason = data.latest_run.reason || "";
            
            updateValidationUI();
        } else {
            testVideoEl.src = "";
            testVideoEl.removeAttribute('src');
            runInfoEl.innerHTML = `<span style="color: var(--error);">No completed run available for this test case.</span>`;
            
            // Reset state
            verificationState = {
                pass_lng: null, pass_asr: null, pass_capsule: null, pass_tts: null, reason: ""
            };
            updateValidationUI();
        }
    }

    // Toggle logic
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const group = e.target.closest('.toggle-group');
            if (!group) return;
            
            const field = group.dataset.field;
            const val = e.target.dataset.val === 'true';
            
            verificationState[field] = val;
            updateValidationUI();
        });
    });

    reasonInput.addEventListener('input', (e) => {
        verificationState.reason = e.target.value;
    });

    function updateValidationUI() {
        document.querySelectorAll('.toggle-group').forEach(group => {
            const field = group.dataset.field;
            const val = verificationState[field];
            
            group.querySelector('.pass').classList.toggle('active', val === true);
            group.querySelector('.fail').classList.toggle('active', val === false);
        });
        reasonInput.value = verificationState.reason || "";
    }

    async function autoSaveCurrent() {
        const data = testDataMap.get(currentTestId);
        if (!data || !data.latest_run || !data.latest_run.test_run_id) return;
        
        // Skip saving if nothing has been set
        if (verificationState.pass_lng === null && 
            verificationState.pass_asr === null && 
            verificationState.pass_capsule === null && 
            verificationState.pass_tts === null && 
            !verificationState.reason) {
            return;
        }

        saveStatusEl.style.display = 'inline-block';
        saveStatusEl.textContent = 'Saving...';
        
        try {
            const res = await fetch(`/api/runs/${data.latest_run.test_run_id}/verify`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(verificationState)
            });
            
            if (!res.ok) throw new Error("Save failed");
            
            const updatedRun = await res.json();
            
            // Update local data
            data.latest_run = updatedRun;
            
            saveStatusEl.textContent = 'Saved';
            setTimeout(() => { saveStatusEl.style.display = 'none'; }, 2000);
            
            // Re-render sidebar to update status indicators
            renderSidebar();
            
        } catch (e) {
            console.error("Save error:", e);
            saveStatusEl.textContent = 'Error saving';
            saveStatusEl.style.color = 'var(--error)';
        }
    }

    manualSaveBtn.addEventListener('click', autoSaveCurrent);

    // Initial load
    loadData();
});
