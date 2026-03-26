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
            <div class="timeline-comment color-bg-default dula-premium-card" style="margin-left: 56px;">
                <div class="timeline-comment-header clearfix dula-premium-header">
                <h3 class="timeline-comment-header-text f5 text-normal">
                    <span style="font-size: 16px; margin-right: 6px;">🧠</span> 
                    <strong class="css-truncate">
                       <span class="css-truncate-target" style="color: #ffffff;">Code Review AI</span>
                    </strong>
                    <span style="float: right; font-size: 12px; color: rgba(255,255,255,0.7); background: rgba(0,0,0,0.3); padding: 2px 8px; border-radius: 12px;">Project Dashboard</span>
                </h3>
            </div>
            <div class="edit-comment-hide">
                <div class="comment-body markdown-body" style="padding: 20px;">
                    <!-- State 1: Setup -->
                    <div id="dula-state-1">
                        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                            <!-- LEFT PANEL -->
                            <div style="flex: 2; min-width: 300px;">
                                <h4 style="margin-top: 0; font-size: 14px; color: #57606a;">Review Prompt</h4>
                                <input type="text" id="dula-custom-instruction" class="form-control width-full mb-3 dula-premium-input" placeholder="e.g., Check for SQL injection vulnerabilities, or leave blank for a general review...">
                                
                                <button id="dula-expand-btn" class="btn btn-sm btn-outline mb-3" style="border-radius: 12px; font-size: 12px; box-shadow: none;">⚙ Expand Advanced Options</button>
                                
                                <!-- ADVANCED OPTIONS (Hidden by default) -->
                                <div id="dula-advanced-options" style="display: none; padding: 12px; border: 1px dashed #d0d7de; border-radius: 8px; margin-bottom: 16px; background: rgba(255,255,255,0.5);">
                                    <h4 style="margin-top: 0; font-size: 14px; color: #57606a;">Review Intent</h4>
                                    <select id="dula-review-intent" class="form-select width-full mb-3 dula-premium-input">
                                        <option value="General Improvement">General Improvement</option>
                                        <option value="Production Readiness">Production Readiness</option>
                                        <option value="Interview Prep">Interview Preparation</option>
                                        <option value="Security Audit">Strict Security Audit</option>
                                    </select>
                                    
                                    <h4 style="font-size: 14px; color: #57606a; margin-top: 16px;">Focus Categories</h4>
                                    <div id="dula-categories" class="dula-chip-group">
                                        <label class="dula-chip"><input type="checkbox" value="Security" checked> 🛡 Security</label>
                                        <label class="dula-chip"><input type="checkbox" value="Performance" checked> ⚡ Performance</label>
                                        <label class="dula-chip"><input type="checkbox" value="Code Quality" checked> 🧹 Quality</label>
                                        <label class="dula-chip"><input type="checkbox" value="Architecture" checked> 🧱 Architecture</label>
                                        <label class="dula-chip"><input type="checkbox" value="Bugs" checked> 🐞 Bugs</label>
                                        <label class="dula-chip"><input type="checkbox" value="Testing"> 🧪 Testing</label>
                                        <label class="dula-chip"><input type="checkbox" value="DevOps"> 🚀 DevOps</label>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- RIGHT PANEL (SUMMARY INFO) -->
                            <div style="flex: 1; min-width: 200px; padding: 16px; background: rgba(147, 51, 234, 0.05); border-radius: 8px; border: 1px solid rgba(147, 51, 234, 0.1); display: flex; flex-direction: column; justify-content: center; text-align: center;">
                                <div style="font-size: 32px; margin-bottom: 8px;">🚀</div>
                                <h4 style="font-size: 14px; margin-bottom: 4px; color: #9333ea;">Ready for Analysis</h4>
                                <p style="font-size: 12px; color: #57606a; margin: 0;">We will automatically extract Project Context & Dependencies.</p>
                            </div>
                        </div>
                        
                        <div style="margin-top: 20px; border-top: 1px solid #e1e4e8; padding-top: 16px; text-align: right;">
                             <button id="dula-trigger-btn" class="btn btn-primary dula-run-btn">Execute Analysis</button>
                        </div>
                    </div>
                    
                    <!-- State 2: Loading Layer 1 -->
                    <div id="dula-state-2" style="display: none;">
                        <div style="display: flex; align-items: center; gap: 10px; padding: 20px 0;">
                            <div class="dula-spinner"></div>
                            <p style="margin: 0; font-size: 14px;"><strong>Layer 1 Analyzing Context:</strong> Parsing repository tree and semantics...</p>
                        </div>
                    </div>

                    <!-- State 3: Editable Confirmation -->
                    <div id="dula-state-3" style="display: none;">
                        <h4 style="margin-top: 0; font-size: 14px; color: #57606a;">Layer 1 Context Synthesis Complete</h4>
                        <textarea id="dula-prompt-editor" class="form-control width-full mb-3" style="height: 200px; font-family: 'Courier New', monospace; font-size: 12px;"></textarea>
                        <div style="text-align: right;">
                             <button id="dula-cancel-btn" class="btn btn-outline" style="margin-right: 8px;">Cancel</button>
                             <button id="dula-confirm-btn" class="btn btn-primary dula-run-btn">⚡ Run Layer 2 Code Review</button>
                        </div>
                    </div>

                    <!-- State 4: Loading Layer 2 -->
                    <div id="dula-state-4" style="display: none;">
                        <div style="display: flex; align-items: center; gap: 10px; padding: 20px 0;">
                            <div class="dula-spinner"></div>
                            <p style="margin: 0; font-size: 14px;"><strong>Layer 2 Executing:</strong> Running deep deterministic analysis. Generating final report...</p>
                        </div>
                    </div>
                    
                    <!-- State 5: Success -->
                    <div id="dula-state-5" style="display: none;">
                        <div style="padding: 20px 0; text-align: center;">
                            <h3 style="color: #2da44e; margin-bottom: 8px;">✅ Analysis Successfully Placed</h3>
                            <p style="color: #57606a; font-size: 13px; margin-bottom: 8px;">The structural review report has been appended to the PR timeline.</p>
                            <p style="color: #0969da; font-size: 12px; margin-bottom: 16px; font-weight: bold;">Please refresh the page to view the AI Code Review comment.</p>
                            <button id="dula-reset-btn" class="btn btn-sm">Start New Review</button>
                        </div>
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
    
    document.getElementById('dula-expand-btn').addEventListener('click', () => {
        const advOptions = document.getElementById('dula-advanced-options');
        const isHidden = advOptions.style.display === 'none';
        advOptions.style.display = isHidden ? 'block' : 'none';
        document.getElementById('dula-expand-btn').innerText = isHidden ? '⬆ Collapse Advanced Options' : '⚙ Expand Advanced Options';
    });
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
    const intent = document.getElementById('dula-review-intent').value;
    
    // Gather checked categories
    const categoryCheckboxes = document.querySelectorAll('#dula-categories input[type="checkbox"]:checked');
    const categories = Array.from(categoryCheckboxes).map(cb => cb.value);
    const categoryString = categories.length > 0 ? categories.join(', ') : 'all';
    
    let extra = document.getElementById('dula-custom-instruction').value.trim();
    
    let instruction = `Intent: ${intent}. Categories: ${categoryString}.`;
    if (extra) instruction += ` Additional focus: ${extra}`;
    const ctx = getPrContext();

    try {
        const response = await fetch('https://code-review-bot-5kl5.onrender.com/api/layer1', {
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
        const response = await fetch('https://code-review-bot-5kl5.onrender.com/api/layer2', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                repo_full_name: ctx.repoFullName,
                pr_number: ctx.prNumber,
                confirmed_prompt: confirmedPrompt
            })
        });

        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`API Failed: ${response.status} - ${errText}`);
        }

        // Success
        switchState(5);
        // We removed the forced reload so the user doesn't lose their train of thought.

    } catch (e) {
        console.error(e);
        alert("DULA Layer 2 Error: " + e.message);
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
