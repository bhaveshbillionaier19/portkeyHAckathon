// Main App State
const state = {
    currentPage: 'home',
    messages: [],
    totalCost: 0,
    evaluationData: null
};

const API_BASE = 'http://localhost:8001';

// Router
function navigate(page) {
    state.currentPage = page;

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });

    // Render page
    render();
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Setup navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navigate(link.dataset.page);
        });
    });

    // Initial render
    render();
});

// Main Render Function
function render() {
    const app = document.getElementById('app');

    switch (state.currentPage) {
        case 'home':
            app.innerHTML = renderHomePage();
            break;
        case 'chat':
            app.innerHTML = renderChatPage();
            setupChatListeners();
            break;
        case 'results':
            app.innerHTML = renderResultsPage();
            loadEvaluationData();
            break;
    }
}

// ==================== HOME PAGE ====================
function renderHomePage() {
    return `
        <div class="container fade-in">
            <!-- Hero -->
            <div style="text-align: center; max-width: 800px; margin: 0 auto 4rem;">
                <h1 style="font-size: 3.5rem; margin-bottom: 1.5rem;">
                    Intelligent LLM <span class="text-gradient">Evaluation</span>
                </h1>
                <p style="font-size: 1.25rem; color: var(--text-secondary); margin-bottom: 2rem;">
                    Auto-classify prompts, route to optimal models, and track costs in real-time
                </p>
                <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                    <button class="btn-primary" onclick="navigate('chat')">💬 Try Smart Chat</button>
                    <button class="btn-secondary" onclick="navigate('results')">📊 View Results</button>
                </div>
            </div>

            <!-- Stats -->
            <div class="grid grid-4" style="margin-bottom: 3rem;">
                ${renderStatCard('🎯', '4', 'Metric Types')}
                ${renderStatCard('🤖', '3+', 'LLM Models')}
                ${renderStatCard('⚡', 'Auto', 'Routing')}
                ${renderStatCard('💰', 'Real', 'Cost Track')}
            </div>

            <!-- Features -->
            <div class="grid grid-3" style="margin-bottom: 3rem;">
                ${renderFeatureCard('⚖️', 'Quality Scores', 'Peer review evaluation across categories', ['Multi-judge reviews', 'Category scoring', 'Detailed metrics'])}
                ${renderFeatureCard('💰', 'Cost Analysis', 'Real-time API cost tracking', ['Actual costs', 'Token breakdown', 'Latency metrics'])}
                ${renderFeatureCard('🛡️', 'Safety Checks', 'Comprehensive guardrails', ['PII detection', 'Toxicity flags', 'Safety scoring'])}
            </div>

            <!-- Smart Chat Highlight -->
            <div class="card" style="background: linear-gradient(to right, rgba(168, 85, 247, 0.1), rgba(236, 72, 153, 0.1)); border-color: rgba(168, 85, 247, 0.3); margin-bottom: 3rem;">
                <div class="grid grid-2" style="align-items: center;">
                    <div>
                        <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
                        <h2 style="font-size: 2rem; margin-bottom: 1rem;">Smart Chat</h2>
                        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                            Auto-classifies prompts and routes to the best model for each category. 
                            See costs, metrics, and reasoning in real-time.
                        </p>
                        <button class="btn-primary" onclick="navigate('chat')">Start Chatting →</button>
                    </div>
                    <div style="display: grid; gap: 0.75rem;">
                        ${renderInfoBox('🎯', 'Auto-Classify', 'GPT-4o powered')}
                        ${renderInfoBox('⚡', 'Smart Route', 'Best model/category')}
                        ${renderInfoBox('📊', 'Live Metrics', 'Real-time cost')}
                    </div>
                </div>
            </div>

            <!-- How It Works -->
            <div style="max-width: 800px; margin: 0 auto;">
                <h2 style="text-align: center; font-size: 2rem; margin-bottom: 2rem;">How It Works</h2>
                <div style="display: grid; gap: 1rem;">
                    ${renderStep('1', 'Evaluate', 'Models tested on quality, cost, safety')}
                    ${renderStep('2', 'Analyze', 'AI identifies best models per category')}
                    ${renderStep('3', 'Route', 'Prompts auto-sent to optimal model')}
                    ${renderStep('4', 'Track', 'Real-time cost and performance monitoring')}
                </div>
            </div>
        </div>
    `;
}

function renderStatCard(icon, value, label) {
    return `
        <div class="card" style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">${icon}</div>
            <div style="font-size: 1.5rem; font-weight: 700;" class="text-gradient">${value}</div>
            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">${label}</div>
        </div>
    `;
}

function renderFeatureCard(icon, title, desc, features) {
    return `
        <div class="card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">${icon}</div>
            <h3 style="font-size: 1.25rem; margin-bottom: 0.75rem;">${title}</h3>
            <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1rem;">${desc}</p>
            <ul style="font-size: 0.75rem; color: var(--text-secondary); list-style: none;">
                ${features.map(f => `<li style="margin-bottom: 0.25rem;">✓ ${f}</li>`).join('')}
            </ul>
        </div>
    `;
}

function renderInfoBox(icon, title, desc) {
    return `
        <div style="padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <span style="font-size: 1.25rem;">${icon}</span>
                <span style="font-weight: 600; font-size: 0.875rem;">${title}</span>
            </div>
            <p style="font-size: 0.75rem; color: var(--text-secondary);">${desc}</p>
        </div>
    `;
}

function renderStep(num, title, desc) {
    return `
        <div style="display: flex; align-items: center; gap: 1rem; padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 0.5rem; transition: all 0.2s;">
            <div style="width: 2.5rem; height: 2.5rem; background: var(--purple-600); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0;">${num}</div>
            <div>
                <h3 style="font-weight: 700; margin-bottom: 0.25rem;">${title}</h3>
                <p style="font-size: 0.875rem; color: var(--text-secondary);">${desc}</p>
            </div>
        </div>
    `;
}

// ==================== CHAT PAGE ====================
function renderChatPage() {
    return `
        <div class="container">
            <div style="display: grid; grid-template-columns: 1fr 300px; gap: 1.5rem;">
                
                <!-- Main Chat -->
                <div class="card" style="height: calc(100vh - 12rem); display: flex; flex-direction: column;">
                    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1rem;">
                        <h1 style="font-size: 1.5rem; font-weight: 700;" class="text-gradient">💬 Smart Chat</h1>
                        <p style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">Auto-routed to best model per category</p>
                    </div>

                    <div id="messages" style="flex: 1; overflow-y: auto; margin-bottom: 1rem; padding-right: 0.5rem;">
                        ${state.messages.length === 0 ? `
                            <div style="text-align: center; padding: 3rem 0; color: var(--text-secondary);">
                                <div style="font-size: 4rem; margin-bottom: 1rem;">🤖</div>
                                <p style="font-size: 1.125rem; margin-bottom: 0.5rem;">Start a conversation!</p>
                                <p style="font-size: 0.875rem;">Try: "What is DNA?" or "Write Python code"</p>
                            </div>
                        ` : ''}
                    </div>

                    <div style="display: flex; gap: 0.75rem;">
                        <textarea 
                            id="chat-input" 
                            placeholder="Type your message..."
                            style="flex: 1; background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-color); border-radius: 0.75rem; padding: 0.75rem; color: white; resize: none; font-family: inherit;"
                            rows="2"
                        ></textarea>
                        <button id="send-btn" class="btn-primary" style="padding: 0 2rem;">Send</button>
                    </div>
                </div>

                <!-- Sidebar -->
                <div class="card" style="height: fit-content;">
                    <h3 style="font-size: 1.125rem; font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center;">
                        <span style="margin-right: 0.5rem;">📊</span>
                        Session Stats
                    </h3>
                    
                    <div style="display: grid; gap: 0.75rem;">
                        <div style="padding: 0.75rem; background: rgba(255, 255, 255, 0.05); border-radius: 0.5rem;">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Messages</div>
                            <div id="msg-count" style="font-size: 1.5rem; font-weight: 700;">${state.messages.length}</div>
                        </div>

                        <div style="padding: 0.75rem; background: rgba(74, 222, 128, 0.1); border: 1px solid rgba(74, 222, 128, 0.2); border-radius: 0.5rem;">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Total Cost</div>
                            <div id="total-cost" style="font-size: 1.5rem; font-weight: 700; color: var(--green-400);">
                                $${state.totalCost.toFixed(6)}
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 1.5rem;">
                        <h3 style="font-size: 1.125rem; font-weight: 700; margin-bottom: 0.75rem;">✨ Features</h3>
                        <ul style="list-style: none; font-size: 0.75rem; color: var(--text-secondary);">
                            <li style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span style="color: var(--green-400);">✓</span> Auto classification
                            </li>
                            <li style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span style="color: var(--green-400);">✓</span> Smart routing
                            </li>
                            <li style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span style="color: var(--green-400);">✓</span> Live metrics
                            </li>
                            <li style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="color: var(--green-400);">✓</span> Cost tracking
                            </li>
                        </ul>
                    </div>
                </div>

            </div>
        </div>
    `;
}

function setupChatListeners() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    renderMessages();
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const prompt = input.value.trim();

    if (!prompt) return;

    // Add user message
    state.messages.push({
        role: 'user',
        content: prompt
    });

    input.value = '';
    input.disabled = true;
    sendBtn.disabled = true;

    renderMessages();
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt,
                conversation_history: []
            })
        });

        if (!response.ok) throw new Error('Chat failed');

        const data = await response.json();

        state.messages.push({
            role: 'assistant',
            content: data.response,
            model: data.model_used,
            category: data.category,
            metrics: data.metrics,
            modelSwitched: data.model_switched,
            switchReason: data.switch_reason
        });

        state.totalCost += (data.metrics?.cost || 0);

    } catch (error) {
        state.messages.push({
            role: 'assistant',
            content: 'Error: Make sure backend is running on port 8001'
        });
    }

    input.disabled = false;
    sendBtn.disabled = false;
    renderMessages();
    updateStats();
    input.focus();
}

function renderMessages() {
    const messagesDiv = document.getElementById('messages');
    if (!messagesDiv) return;

    messagesDiv.innerHTML = state.messages.map((msg, idx) => {
        if (msg.role === 'user') {
            return `
                <div style="display: flex; justify-content: flex-end; margin-bottom: 1.5rem;">
                    <div style="background: linear-gradient(to right, var(--purple-600), var(--indigo-600)); border-radius: 1rem; padding: 0.75rem 1.25rem; max-width: 85%;">
                        <div style="white-space: pre-wrap;">${escapeHtml(msg.content)}</div>
                    </div>
                </div>
            `;
        } else {
            return `
                <div style="margin-bottom: 1.5rem;">
                    ${msg.modelSwitched && msg.switchReason ? `
                        <div style="margin-bottom: 0.75rem; padding: 0.75rem; background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 0.5rem;">
                            <span style="color: var(--purple-500);">⚡</span>
                            <span style="font-size: 0.875rem; color: #d8b4fe;">${escapeHtml(msg.switchReason)}</span>
                        </div>
                    ` : ''}
                    
                    <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-color); border-radius: 1rem; padding: 1rem 1.25rem; margin-bottom: 0.75rem;">
                        <div style="white-space: pre-wrap; line-height: 1.6;">${escapeHtml(msg.content)}</div>
                    </div>
                    
                    ${msg.metrics ? `
                        <div style="background: rgba(168, 85, 247, 0.05); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 0.5rem; padding: 1rem;">
                            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem;">
                                <div style="text-align: center;">
                                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Model</div>
                                    <div style="font-weight: 700; color: var(--purple-500); font-size: 0.875rem;">${msg.model.toUpperCase()}</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Category</div>
                                    <div style="font-weight: 600; font-size: 0.875rem;">${msg.category}</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Cost</div>
                                    <div style="font-weight: 600; color: var(--green-400); font-size: 0.875rem;">$${msg.metrics.cost.toFixed(6)}</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Tokens</div>
                                    <div style="font-weight: 600; font-size: 0.875rem;">${msg.metrics.tokens}</div>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }
    }).join('');

    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showLoading() {
    const messagesDiv = document.getElementById('messages');
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading';
    loadingDiv.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-color); border-radius: 1rem; padding: 0.75rem 1.25rem; display: inline-block;">
                <div class="loading-dots">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
            </div>
        </div>
    `;
    messagesDiv.appendChild(loadingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    setTimeout(() => {
        const loader = document.getElementById('loading');
        if (loader) loader.remove();
    }, 500);
}

function updateStats() {
    const msgCount = document.getElementById('msg-count');
    const totalCost = document.getElementById('total-cost');

    if (msgCount) msgCount.textContent = state.messages.length;
    if (totalCost) totalCost.textContent = `$${state.totalCost.toFixed(6)}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== RESULTS PAGE ====================
function renderResultsPage() {
    return `
        <div class="container">
            <h1 style="font-size: 2rem; font-weight: 700; margin-bottom: 2rem; text-align: center;" class="text-gradient">
                📊 Evaluation Results
            </h1>
            
            <div id="results-content" style="text-align: center; padding: 3rem;">
                <div class="loading-dots" style="justify-content: center; margin-bottom: 1rem;">
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                    <div class="loading-dot"></div>
                </div>
                <p style="color: var(--text-secondary);">Loading evaluation data...</p>
            </div>
        </div>
    `;
}

async function loadEvaluationData() {
    try {
        const response = await fetch(`${API_BASE}/api/evaluation-results`);
        const data = await response.json();
        state.evaluationData = data;

        const content = document.getElementById('results-content');
        if (!content) return;

        // Extract data
        const totalQuestions = data.total_questions || 0;
        const models = data.models || [];
        const modelsCount = Array.isArray(models) ? models.length : Object.keys(models).length;
        const categoryStats = data.category_statistics || {};
        const categoriesCount = Object.keys(categoryStats).length;

        // Get best model per category
        const categoryBest = {};
        for (const [category, modelsData] of Object.entries(categoryStats)) {
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
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Total Questions</div>
                </div>
                <div class="card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
                    <div style="font-size: 2rem; font-weight: 700;" class="text-gradient">${modelsCount}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Models Tested</div>
                </div>
                <div class="card">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div style="font-size: 2rem; font-weight: 700;" class="text-gradient">${categoriesCount}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">Categories</div>
                </div>
            </div>

            <div class="card" style="margin-bottom: 2rem;">
                <h3 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem;">🏆 Best Models by Category</h3>
                <div class="grid grid-2" style="gap: 1rem;">
                    ${Object.entries(categoryBest).map(([cat, data]) => `
                        <div style="padding: 1rem; background: rgba(168, 85, 247, 0.1); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 0.5rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.25rem;">${cat}</div>
                                    <div style="font-size: 1.25rem; font-weight: 700; color: var(--purple-500);">${data.model.toUpperCase()}</div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.5rem; font-weight: 700;" class="text-gradient">${data.score.toFixed(2)}</div>
                                    <div style="font-size: 0.75rem; color: var(--text-secondary);">/ 5.0</div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="card">
                <h3 style="font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem;">📈 Evaluation Summary</h3>
                <p style="color: var(--text-secondary); line-height: 1.6;">
                    Comprehensive evaluation of ${modelsCount} models across ${categoriesCount} categories using ${totalQuestions} test questions.
                    Models were scored on quality, cost, safety, and performance metrics.
                </p>
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(74, 222, 128, 0.1); border: 1px solid rgba(74, 222, 128, 0.2); border-radius: 0.5rem;">
                    <p style="font-weight: 600; margin-bottom: 0.5rem;">✅ Smart Routing Active</p>
                    <p style="font-size: 0.875rem; color: var(--text-secondary);">
                        The chat automatically routes prompts to the best-performing model for each category.
                    </p>
                </div>
            </div>
        `;
    } catch (error) {
        const content = document.getElementById('results-content');
        if (content) {
            content.innerHTML = `
                <div class="card">
                    <p style="color: #f87171; margin-bottom: 1rem;">❌ Failed to load evaluation results</p>
                    <p style="color: var(--text-secondary); font-size: 0.875rem;">
                        Make sure the backend is running and evaluation has been completed.
                    </p>
                    <p style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.5rem;">
                        Error: ${error.message}
                    </p>
                </div>
            `;
        }
    }
}

function getBestModel(data) {
    if (!data.models) return 'N/A';
    const models = Object.keys(data.models);
    return models[0] || 'N/A';
}
