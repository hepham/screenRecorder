document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const suiteId = urlParams.get('suite_id');
    const testIdParam = urlParams.get('test_id');

    if (!suiteId && !testIdParam) {
        alert("No Suite ID or Test ID provided!");
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
            // Fetch tests
            const testsRes = await fetch('/api/tests');
            allTests = await testsRes.json();

            // Fetch runs
            const runsRes = await fetch('/api/runs');
            allRuns = await runsRes.json();

            if (suiteId) {
                // Fetch suite
                const suiteRes = await fetch(`/api/suites/${suiteId}`);
                if (!suiteRes.ok) throw new Error("Suite not found");
                currentSuite = await suiteRes.json();
                suiteTitleEl.textContent = `Suite: ${currentSuite.name}`;
            } else if (testIdParam) {
                const test = allTests.find(t => t.id === testIdParam);
                if (!test) throw new Error("Test not found");
                currentSuite = { name: "Individual Test", test_case_ids: [testIdParam] };
                suiteTitleEl.textContent = `Test Case: ${test.name}`;
            }

            // Map data
            buildTestDataMap();
            renderSidebar();

            // Auto-select if there's only one test case (in individual mode)
            if (testIdParam && testDataMap.has(testIdParam)) {
                selectTestCase(testIdParam);
            }

        } catch (e) {
            console.error("Error loading data:", e);
            suiteTitleEl.textContent = "Error loading data";
        }
    }

    function buildTestDataMap() {
        testDataMap.clear();
        
        if (!currentSuite.test_case_ids) return;

        currentSuite.test_case_ids.forEach(testId => {
            const test = allTests.find(t => t.id === testId);
            if (!test) return;

            // Find all runs for this test in this suite (or independent if suiteId is null)
            let testRuns = [];
            if (suiteId) {
                testRuns = allRuns.filter(r => r.test_id === testId && r.suite_id === suiteId);
            } else {
                testRuns = allRuns.filter(r => r.test_id === testId && !r.suite_id);
            }
            
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
        testUtteranceEl.textContent = data.test.utterance || data.test.description || data.test.name;
        testAudioEl.src = data.test.audio_url;

        const capsuleIdDisplay = document.getElementById('capsule-id-display');
        const capsuleDetailLink = document.getElementById('capsule-detail-link');

        if (data.latest_run && data.latest_run.video_filename) {
            testVideoEl.parentElement.style.display = 'flex';
            testVideoEl.src = `/recordings/${data.latest_run.video_filename}`;
            const date = new Date(data.latest_run.timestamp * 1000).toLocaleString();
            runInfoEl.innerHTML = `Run Date: ${date} <br>Run ID: ${data.latest_run.test_run_id}`;
            
            // Capsule ID
            const capsuleId = data.latest_run.capsule_id || data.test.capsule_id || 'N/A';
            capsuleIdDisplay.textContent = capsuleId;
            if (capsuleId !== 'N/A') {
                capsuleDetailLink.href = `/capsules/${capsuleId}`;
                capsuleDetailLink.style.pointerEvents = 'auto';
            } else {
                capsuleDetailLink.removeAttribute('href');
                capsuleDetailLink.style.pointerEvents = 'none';
            }

            // Load existing verification state
            verificationState.pass_lng = data.latest_run.pass_lng;
            verificationState.pass_asr = data.latest_run.pass_asr;
            verificationState.pass_capsule = data.latest_run.pass_capsule;
            verificationState.pass_tts = data.latest_run.pass_tts;
            verificationState.reason = data.latest_run.reason || "";
            
            updateValidationUI();
        } else {
            testVideoEl.parentElement.style.display = 'none';
            testVideoEl.src = "";
            testVideoEl.removeAttribute('src');
            runInfoEl.innerHTML = `<span style="color: var(--error-color);">No completed run available for this test case.</span>`;
            
            capsuleIdDisplay.textContent = data.test.capsule_id || 'N/A';
            capsuleDetailLink.removeAttribute('href');
            capsuleDetailLink.style.pointerEvents = 'none';
            
            // Reset state
            verificationState = {
                pass_lng: null, pass_asr: null, pass_capsule: null, pass_tts: null, reason: ""
            };
            updateValidationUI();
        }
    }

    // Toggle logic
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const group = e.target.closest('.toggle-group');
            if (!group) return;
            
            const field = group.dataset.field;
            const val = e.target.dataset.val === 'true';
            
            verificationState[field] = val;
            updateValidationUI();
            
            // Auto-save immediately when a toggle is clicked
            await autoSaveCurrent();
        });
    });

    let autoSaveTimeout = null;
    reasonInput.addEventListener('input', (e) => {
        verificationState.reason = e.target.value;
        
        // Debounce auto-save for text input
        if (autoSaveTimeout) clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(() => {
            autoSaveCurrent();
        }, 1000); // 1s debounce
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

        saveStatusEl.classList.add('visible');
        saveStatusEl.classList.remove('success', 'error');
        saveStatusEl.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg> Saving...`;
        
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
            
            saveStatusEl.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg> Saved`;
            saveStatusEl.classList.add('success');
            
            setTimeout(() => { 
                saveStatusEl.classList.remove('visible'); 
            }, 2000);
            
            // Re-render sidebar to update status indicators
            renderSidebar();
            
        } catch (e) {
            console.error("Save error:", e);
            saveStatusEl.innerHTML = `<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg> Error saving`;
            saveStatusEl.classList.add('error');
            
            setTimeout(() => { 
                saveStatusEl.classList.remove('visible'); 
            }, 3000);
        }
    }

    if (manualSaveBtn) {
        manualSaveBtn.addEventListener('click', autoSaveCurrent);
    }

    // Layout Resizer
    const layoutResizer = document.getElementById('layout-resizer');
    const sidebarEl = document.getElementById('test-sidebar');
    let isResizing = false;

    if (layoutResizer && sidebarEl) {
        layoutResizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            document.body.style.cursor = 'col-resize';
            layoutResizer.classList.add('resizing');
            e.preventDefault(); // Prevent text selection
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            // Calculate width as a percentage
            const newWidth = (e.clientX / window.innerWidth) * 100;
            if (newWidth >= 15 && newWidth <= 60) {
                sidebarEl.style.width = `${newWidth}%`;
            }
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = 'default';
                layoutResizer.classList.remove('resizing');
            }
        });
    }

    // Initial load
    loadData();
});
