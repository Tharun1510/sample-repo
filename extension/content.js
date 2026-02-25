// Prevent multiple injections
let dulaWidgetInjected = false;

function createDulaWidget() {
    const widget = document.createElement('div');
    widget.id = 'dula-timeline-widget';
    widget.className = 'timeline-comment-group js-minimizable-comment-group';
    widget.style.marginBottom = '16px';

    widget.innerHTML = `
        <div style="position: relative; width: 100%;">
            <a class="d-none d-md-block" href="#" style="position: absolute; left: 0; top: 0;">
                <img class="avatar avatar-user" src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="40" height="40" alt="DULA" style="border-radius: 50%;">
            </a>
            <div class="timeline-comment color-bg-default dula-glow-box" style="margin-left: 56px;">
                <div class="timeline-comment-header clearfix dula-header">
                <h3 class="timeline-comment-header-text f5 text-normal">
                    <strong class="css-truncate">
                       <span class="css-truncate-target" style="color: #9333ea;">🧠 DULA Bot</span>
                    </strong>
                    native analysis agent
                </h3>
            </div>
            <div class="edit-comment-hide">
                <div class="comment-body markdown-body">
                    <!-- State 1: Setup -->
                    <div id="dula-state-1">
                        <p><strong>Optimize Review Request</strong></p>
                        <select id="dula-review-type" class="form-select width-full mb-2">
                            <option value="Perform a comprehensive security and structural code review.">Deep Structural & Security Review</option>
                            <option value="Check for memory leaks and time complexity performance.">Performance & Optimization Review</option>
                            <option value="Check for architectural alignment and clean code principles.">Architectural Alignment Review</option>
                        </select>
                        <button id="dula-trigger-btn" class="btn btn-primary">Synthesize Enhanced Prompt</button>
                    </div>
                    
                    <!-- State 2: Loading Layer 1 -->
                    <div id="dula-state-2" style="display: none;">
                        <p>⏳ <strong>Layer 1 Analyzing Context:</strong> Parsing repository tree and tracking semantic dependencies...</p>
                    </div>

                    <!-- State 3: Editable Confirmation -->
                    <div id="dula-state-3" style="display: none;">
                        <p><strong>Layer 1 Context Synthesis Complete.</strong> You may edit the constraint matrix before final execution:</p>
                        <textarea id="dula-prompt-editor" class="form-control width-full mb-2" style="height: 250px; font-family: monospace; font-size: 12px;"></textarea>
                        <button id="dula-confirm-btn" class="btn btn-primary">Confirm and Execute Layer 2</button>
                        <button id="dula-cancel-btn" class="btn btn-outline float-right">Cancel</button>
                    </div>

                    <!-- State 4: Loading Layer 2 -->
                    <div id="dula-state-4" style="display: none;">
                        <p>🚀 <strong>Layer 2 Executing:</strong> Running deep deterministic analysis. Generating final structured Markdown report...</p>
                    </div>
                    
                    <!-- State 5: Success -->
                    <div id="dula-state-5" style="display: none;">
                        <p>✅ <strong>Analysis Completed:</strong> The report has been successfully appended to the timeline.</p>
                        <button id="dula-reset-btn" class="btn btn-sm">Start New Review</button>
                    </div>
                </div>
            </div>
        </div>
        </div>
    `;
    return widget;
}

function injectDulaWidget() {
    if (document.getElementById('dula-timeline-widget')) return;

    // Is it a PR page?
    if (!window.location.pathname.includes('/pull/')) return;

    // Find the new comment box at the bottom of the discussion
    const newCommentBox = document.querySelector('.timeline-new-comment');
    if (!newCommentBox) return;

    const widget = createDulaWidget();
    newCommentBox.parentNode.insertBefore(widget, newCommentBox);
    dulaWidgetInjected = true;

    // Attach Event Listeners
    document.getElementById('dula-trigger-btn').addEventListener('click', handleTriggerLayer1);
    document.getElementById('dula-confirm-btn').addEventListener('click', handleTriggerLayer2);
    document.getElementById('dula-cancel-btn').addEventListener('click', () => switchState(1));
    document.getElementById('dula-reset-btn').addEventListener('click', () => switchState(1));
}

function switchState(stateNumber) {
    for (let i = 1; i <= 5; i++) {
        const el = document.getElementById(`dula-state-${i}`);
        if (el) el.style.display = (i === stateNumber) ? 'block' : 'none';
    }
}

// Extract Repo Info
function getPrContext() {
    const urlParts = window.location.pathname.split('/');
    return {
        repoFullName: `${urlParts[1]}/${urlParts[2]}`,
        prNumber: parseInt(urlParts[4])
    };
}

async function handleTriggerLayer1() {
    switchState(2);
    const instruction = document.getElementById('dula-review-type').value;
    const ctx = getPrContext();

    try {
        // Must match your backend URL. If testing locally, make sure Uvicorn is running.
        const response = await fetch('http://localhost:8000/api/layer1', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                repo_full_name: ctx.repoFullName,
                pr_number: ctx.prNumber,
                instruction: instruction
            })
        });

        if (!response.ok) throw new Error("API Failed");
        const data = await response.json();

        document.getElementById('dula-prompt-editor').value = data.enhanced_prompt;
        switchState(3);

    } catch (e) {
        console.error(e);
        alert("DULA Layer 1 Failed to connect to backend. Is uvicorn running?");
        switchState(1);
    }
}

async function handleTriggerLayer2() {
    switchState(4);
    const confirmedPrompt = document.getElementById('dula-prompt-editor').value;
    const ctx = getPrContext();

    try {
        const response = await fetch('http://localhost:8000/api/layer2', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                repo_full_name: ctx.repoFullName,
                pr_number: ctx.prNumber,
                confirmed_prompt: confirmedPrompt
            })
        });

        if (!response.ok) throw new Error("API Failed");

        // Success
        switchState(5);
        // Reload page to show the newly posted comment
        setTimeout(() => window.location.reload(), 1500);

    } catch (e) {
        console.error(e);
        alert("DULA Layer 2 Failed to connect to backend.");
        switchState(3); // Go back to editable state
    }
}

// SPA observer
const observer = new MutationObserver(() => {
    injectDulaWidget();
});
observer.observe(document.body, { childList: true, subtree: true });

// Initial Check
injectDulaWidget();
