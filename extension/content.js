function injectDulaButton() {
    // Avoid injecting multiple times
    if (document.getElementById('dula-review-btn')) return;

    // Find the primary PR header actions area
    const actionMenu = document.querySelector('.gh-header-actions');
    if (!actionMenu) return;

    // Create the DULA button
    const btn = document.createElement('button');
    btn.id = 'dula-review-btn';
    btn.className = 'btn btn-sm btn-primary dula-glow';
    btn.innerHTML = '🧠 Request DULA Review';
    btn.onclick = triggerDulaReview;

    // Inject the button to the start of the menu
    actionMenu.prepend(btn);
}

async function triggerDulaReview() {
    const btn = document.getElementById('dula-review-btn');
    btn.innerHTML = '⏳ DULA Analyzing...';
    btn.disabled = true;

    // Extract repo and PR number from URL
    // URL format: https://github.com/OWNER/REPO/pull/NUMBER
    const urlParts = window.location.pathname.split('/');
    const owner = urlParts[1];
    const repoName = urlParts[2];
    const prNumber = urlParts[4];
    const repoFullName = `${owner}/${repoName}`;

    try {
        // Send payload to the local DULA backend (can be updated to a production URL)
        const response = await fetch('http://localhost:8000/trigger-review', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                repo_full_name: repoFullName,
                pr_number: parseInt(prNumber),
                instruction: 'Perform a comprehensive security and structural code review.'
            })
        });

        if (response.ok) {
            btn.innerHTML = '✅ System Triggered';
            btn.classList.add('btn-outline');
        } else {
            console.error("DULA Backend Returned Error:", response.status);
            btn.innerHTML = '❌ Backend Error';
        }
    } catch (error) {
        console.error("DULA Extension Error:", error);
        btn.innerHTML = '❌ Server Not Found';
        alert("Could not connect to DULA server. Ensure uvicorn is running on http://localhost:8000");
    }

    // Reset button state after a delay
    setTimeout(() => {
        btn.innerHTML = '🧠 Request DULA Review';
        btn.disabled = false;
        btn.classList.remove('btn-outline');
    }, 5000);
}

// GitHub is a Single Page App (SPA) using Turbo, so we observe DOM changes instead of just window.onload
const observer = new MutationObserver((mutations) => {
    injectDulaButton();
});

observer.observe(document.body, { childList: true, subtree: true });

// Attempt initial injection on load
injectDulaButton();
