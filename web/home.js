// Home Page - Load live metrics from evaluation results (400 questions)
const API_BASE = 'http://localhost:8001';

document.addEventListener('DOMContentLoaded', () => {
    loadMetricsSnapshot();
});

async function loadMetricsSnapshot() {
    try {
        // Load from real evaluation results (400 questions)
        const response = await fetch(`${API_BASE}/api/evaluation-results`);
        const data = await response.json();

        const container = document.getElementById('metrics-snapshot');
        if (!container) return;

        // Extract data from real evaluation
        const totalQuestions = data.total_questions || 0;
        const models = data.models || [];
        const modelsCount = Array.isArray(models) ? models.length : Object.keys(models).length;

        // Get category statistics
        const categoryStats = data.category_statistics || {};

        // Find best model across all categories
        let bestQualityScore = 0;

        for (const [category, modelsData] of Object.entries(categoryStats)) {
            for (const [model, stats] of Object.entries(modelsData)) {
                const score = stats.average_score || 0;
                if (score > bestQualityScore) {
                    bestQualityScore = score;
                }
            }
        }

        // Get winners by category
        const validCategories = ['knowledge', 'math', 'code', 'business', 'analysis'];
        const categoryBest = {};

        for (const cat of validCategories) {
            if (categoryStats[cat]) {
                let bestModel = null;
                let bestScore = 0;

                for (const [model, stats] of Object.entries(categoryStats[cat])) {
                    const score = stats.average_score || 0;
                    if (score > bestScore) {
                        bestScore = score;
                        bestModel = model;
                    }
                }

                if (bestModel) {
                    categoryBest[cat] = { model: bestModel, score: bestScore };
                }
            }
        }

        container.innerHTML = `
            <!-- Stats Overview -->
            <div class="grid grid-4" style="margin-bottom: 2rem;">
                <div class="card" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
                    <div style="font-size: 1.5rem; font-weight: 700;" class="text-gradient">${totalQuestions}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Questions Evaluated</div>
                </div>
                <div class="card" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
                    <div style="font-size: 1.5rem; font-weight: 700;" class="text-gradient">${modelsCount}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Models Tested</div>
                </div>
                <div class="card" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                    <div style="font-size: 1.5rem; font-weight: 700;" class="text-gradient">${bestQualityScore ? bestQualityScore.toFixed(2) : 'N/A'}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Best Quality Score</div>
                </div>
                <div class="card" style="text-align: center; padding: 1.5rem;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-size: 1.5rem; font-weight: 700;" class="text-gradient">${Object.keys(categoryBest).length}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Categories</div>
                </div>
            </div>

            <!-- Top 3 Category Winners -->
            <div class="grid grid-3" style="gap: 1rem;">
                ${Object.entries(categoryBest).slice(0, 3).map(([cat, data]) => `
                <div class="card" style="background: rgba(168, 85, 247, 0.1); border-color: rgba(168, 85, 247, 0.3);">
                    <div style="font-size: 2rem; margin-bottom: 0.75rem;">${getCategoryIcon(cat)}</div>
                    <h3 style="font-size: 1.125rem; font-weight: 700; margin-bottom: 0.5rem; text-transform: capitalize;">${cat}</h3>
                    <div style="font-size: 1.75rem; font-weight: 700; margin-bottom: 0.5rem;" class="text-gradient">${data.model.toUpperCase()}</div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem;">
                        <span style="color: var(--text-secondary);">Score:</span>
                        <span style="font-weight: 600;">${data.score.toFixed(2)}/5</span>
                    </div>
                </div>
                `).join('')}
            </div>
        `;

    } catch (error) {
        console.error('Failed to load metrics:', error);
        const container = document.getElementById('metrics-snapshot');
        if (container) {
            container.innerHTML = `
                <div class="card" style="text-align: center; padding: 2rem;">
                    <p style="color: var(--text-secondary);">Unable to load live metrics. Make sure backend is running at localhost:8001</p>
                </div>
            `;
        }
    }
}

function getCategoryIcon(category) {
    const icons = {
        'knowledge': '📚',
        'math': '🔢',
        'code': '💻',
        'business': '💼',
        'analysis': '📈'
    };
    return icons[category] || '📊';
}
