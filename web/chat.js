// Chat Page Logic
const API_BASE = 'http://localhost:8001';

const state = {
    messages: [],
    totalCost: 0
};

// Setup on load
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});

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

    if (state.messages.length === 0) {
        messagesDiv.innerHTML = `
            <div style="text-align: center; padding: 3rem 0; color: var(--text-secondary);">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🤖</div>
                <p style="font-size: 1.125rem; margin-bottom: 0.5rem;">Start a conversation!</p>
                <p style="font-size: 0.875rem;">Try: "What is DNA?" or "Write Python code"</p>
            </div>
        `;
        return;
    }

    messagesDiv.innerHTML = state.messages.map((msg) => {
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
