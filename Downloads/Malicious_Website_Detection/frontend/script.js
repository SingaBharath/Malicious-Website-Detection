document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('scan-form');
    const urlInput = document.getElementById('url-input');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    const resultStatus = document.getElementById('result-status');
    const scoreText = document.getElementById('score-text');
    const categoryBars = document.getElementById('category-bars');
    const securityWarning = document.getElementById('security-warning');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        if (!url) return;

        results.classList.add('hidden');
        loading.classList.remove('hidden');
        
        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            if (!response.ok) throw new Error('Server error');
            const data = await response.json();
            
            loading.classList.add('hidden');
            updateUI(data);
        } catch (error) {
            loading.classList.add('hidden');
            alert('Error analyzing the URL.');
        }
    });

    function updateUI(data) {
        const title = data.is_safe ? 'SAFE WEBSITE' : 'THREAT DETECTED';
        const desc = data.is_safe ? 'No malicious activity detected.' : `Classified as ${data.prediction.toUpperCase()}.`;
            
        resultStatus.innerHTML = `<h2>${title}</h2><p>${desc}</p>`;

        let displayScore = data.is_safe ? data.class_probabilities['benign'] * 100 : data.threat_score;
        scoreText.textContent = `${displayScore.toFixed(1)}%`;

        categoryBars.innerHTML = '';
        const sortedClasses = Object.entries(data.class_probabilities).sort((a, b) => b[1] - a[1]);

        sortedClasses.forEach(([cat, prob]) => {
            const percent = (prob * 100).toFixed(1);
            categoryBars.insertAdjacentHTML('beforeend', `
                <div class="category-row">
                    <span>${cat}</span>
                    <span>${percent}%</span>
                </div>
            `);
        });

        if (data.is_safe) {
            securityWarning.innerHTML = `SAFE TO BROWSE`;
        } else {
            securityWarning.innerHTML = `WARNING: PROCEEDING PUTS YOUR DATA AT RISK`;
        }

        results.classList.remove('hidden');
    }
});
