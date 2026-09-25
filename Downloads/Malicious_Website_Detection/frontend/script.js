document.addEventListener('DOMContentLoaded', () => {
    const form        = document.getElementById('scan-form');
    const urlInput    = document.getElementById('url-input');
    const loading     = document.getElementById('loading');
    const results     = document.getElementById('results');
    const resultStatus   = document.getElementById('result-status');
    const scoreText      = document.getElementById('score-text');
    const categoryBars   = document.getElementById('category-bars');
    const securityWarning = document.getElementById('security-warning');

    // Show inline error message below input
    function showInputError(message) {
        let errorEl = document.getElementById('url-error');
        if (!errorEl) {
            errorEl = document.createElement('p');
            errorEl.id = 'url-error';
            errorEl.style.cssText = 'color:#ff4d4d;font-size:0.85rem;margin-top:8px;text-align:left;padding-left:4px;';
            urlInput.parentElement.appendChild(errorEl);
        }
        errorEl.textContent = message;
        urlInput.style.borderColor = '#ff4d4d';
    }

    function clearInputError() {
        const errorEl = document.getElementById('url-error');
        if (errorEl) errorEl.textContent = '';
        urlInput.style.borderColor = '';
    }

    // Basic client-side URL format check
    function isValidURL(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch (_) {
            return false;
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearInputError();
        results.classList.add('hidden');

        const url = urlInput.value.trim();

        // Client-side validation first
        if (!url) {
            showInputError('Please enter a URL.');
            return;
        }

        if (!isValidURL(url)) {
            showInputError('Please enter a valid URL starting with https:// or http:// — e.g., https://google.com');
            return;
        }

        loading.classList.remove('hidden');

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            loading.classList.add('hidden');

            if (response.status === 400) {
                const err = await response.json();
                showInputError(err.detail || 'Invalid URL. Please enter a valid URL like https://example.com');
                return;
            }

            if (!response.ok) throw new Error('Server error');

            const data = await response.json();
            clearInputError();
            updateUI(data);

        } catch (error) {
            loading.classList.add('hidden');
            showInputError('Error connecting to server. Please try again.');
        }
    });

    // Clear error when user starts typing
    urlInput.addEventListener('input', () => {
        clearInputError();
        results.classList.add('hidden');
    });

    function updateUI(data) {
        const title = data.is_safe ? 'SAFE WEBSITE' : 'THREAT DETECTED';
        const desc  = data.is_safe
            ? 'No malicious activity detected.'
            : `Classified as ${data.prediction.toUpperCase()}.`;

        resultStatus.innerHTML = `<h2>${title}</h2><p>${desc}</p>`;

        let displayScore = data.is_safe
            ? (data.class_probabilities['benign'] * 100)
            : data.threat_score;
        scoreText.textContent = `${displayScore.toFixed(1)}%`;

        categoryBars.innerHTML = '';
        const sortedClasses = Object.entries(data.class_probabilities)
            .sort((a, b) => b[1] - a[1]);

        sortedClasses.forEach(([cat, prob]) => {
            const percent = (prob * 100).toFixed(1);
            categoryBars.insertAdjacentHTML('beforeend', `
                <div class="category-row">
                    <span>${cat}</span>
                    <span>${percent}%</span>
                </div>
            `);
        });

        securityWarning.innerHTML = data.is_safe
            ? 'SAFE TO BROWSE'
            : 'WARNING: PROCEEDING PUTS YOUR DATA AT RISK';

        results.classList.remove('hidden');
    }
});
