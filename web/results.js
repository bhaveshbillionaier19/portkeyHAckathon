// Results Page Logic - Loads data from backend API
const API_BASE = 'http://localhost:8001';

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadEvaluationData();
});

async function loadEvaluationData() {
    try {
        const response = await fetch(`${API_BASE}/api/evaluation-results`);
        const data = await response.json();

        const content = document.getElementById('results-content');
        if (!content) return;

        // Extract data
        const totalQuestions = data.total_questions || 0;
        const models = data.models || [];
        const modelsCount = Array.isArray(models) ? models.length : Object.keys(models).length;
        const categoryStats = data.category_statistics || {};
        const categoriesCount = Object.keys(categoryStats).length;

        // Get best model per category (filter out invalid categories)
        const categoryBest = {};
        const validCategories = ['knowledge', 'math', 'code', 'business', 'analysis', 'health', 'home', 'technology'];

        for (const [category, modelsData] of Object.entries(categoryStats)) {
            // Skip invalid categories (parsing errors like "---", "4.", "is_prime(12)")
            if (!validCategories.includes(category.toLowerCase())) continue;

            let bestModel = null;
            let bestScore = 0;

            for (const [model, stats] of Object.entries(modelsData)) {
                const score = stats.average_score || 0;
                if (score > bestScore) {
                    bestScore = score;
                    bestModel = model;
                }
            }

            if (bestModel) {
                categoryBest[category] = { model: bestModel, score: bestScore };
            }
        }

        content.innerHTML = `
            <div class="grid grid-3" style="margin-bottom: 2rem;">
                <div class="card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
                    <div style="font-size: 2rem; font-weight: 700;" class="text-gradient">${totalQuestions}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Total Questions Evaluated</div>
                </div>
                <div class="card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
                    <div style="font-size: 2rem; font-weight: 700;" class="text-gradient">${modelsCount}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Models Tested</div>
                </div>
                <div class="card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-size: 2rem; font-weight: 700;" class="text-gradient">${Object.keys(categoryBest).length}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Valid Categories</div>
                </div>
            </div>

            <div class="card" style="margin-bottom: 2rem;">
                <h2 style="font-size: 1.75rem; font-weight: 700; margin-bottom: 1.5rem; text-align: center;">
                    🏆 Model Battle Results - Winners by Category
                </h2>
                <p style="text-align: center; color: var(--text-secondary); margin-bottom: 2rem;">
                    Based on comprehensive evaluation across quality, cost, and performance metrics
                </p>
                <div class="grid grid-2" style="gap: 1rem;">
                    ${Object.entries(categoryBest).map(([cat, data]) => `
                        <div class="card" style="background: linear-gradient(to right, rgba(168, 85, 247, 0.1), rgba(236, 72, 153, 0.05)); border-color: rgba(168, 85, 247, 0.3);">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">${getCategoryIcon(cat)} ${cat}</div>
                                    <div style="font-size: 1.75rem; font-weight: 700; background: linear-gradient(to right, var(--purple-500), var(--pink-500)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${data.model.toUpperCase()}</div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 2.5rem; font-weight: 700;" class="text-gradient">${data.score.toFixed(2)}</div>
                                    <div style="font-size: 0.875rem; color: var(--text-secondary);">out of 5.0</div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="card" style="background: rgba(74, 222, 128, 0.05); border-color: rgba(74, 222, 128, 0.2);">
                <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem;">✅ Smart Routing Active</h3>
                <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1rem;">
                    The system automatically routes prompts to the best-performing model for each category based on these evaluation results.
                    Try the <a href="chat.html" style="color: var(--purple-500); text-decoration: underline;">Smart Chat</a> to see it in action!
                </p>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                    <div style="padding: 0.75rem; background: rgba(255, 255, 255, 0.05); border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">🎯</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">Auto Classification</div>
                    </div>
                    <div style="padding: 0.75rem; background: rgba(255, 255, 255, 0.05); border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">⚡</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">Optimal Routing</div>
                    </div>
                    <div style="padding: 0.75rem; background: rgba(255, 255, 255, 0.05); border-radius: 0.5rem; text-align: center;">
                        <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">💰</div>
                        <div style="font-size: 0.75rem; color: var(--text-secondary);">Cost Tracking</div>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        const content = document.getElementById('results-content');
        if (content) {
            content.innerHTML = `
                <div class="card">
                    <p style="color: #f87171; margin-bottom: 1rem; font-size: 1.25rem;">❌ Failed to load evaluation results</p>
                    <p style="color: var(--text-secondary); margin-bottom: 0.5rem;">
                        Make sure the backend is running at <code style="background: rgba(255,255,255,0.1); padding: 0.25rem 0.5rem; border-radius: 0.25rem;">http://localhost:8001</code>
                    </p>
                    <p style="color: var(--text-secondary); font-size: 0.875rem;">
                        Error: ${error.message}
                    </p>
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
