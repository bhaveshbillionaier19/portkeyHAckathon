# 🚀 LLM Evaluation & Smart Routing System

> **Intelligent LLM model selection powered by automated evaluation and real-time routing**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Portkey](https://img.shields.io/badge/Portkey-AI-orange.svg)](https://portkey.ai/)

A comprehensive system for evaluating Large Language Models (LLMs) across multiple categories and automatically routing user prompts to the best-performing model. Built for the **Portkey AI Hackathon**.

## ✨ Features

- 🎯 **Smart Routing**: Automatically routes prompts to the optimal model based on category
- 📊 **Comprehensive Evaluation**: 400-question evaluation across 5 categories
- 🤖 **Multi-Model Support**: Gemini, GPT-4, Claude with easy extensibility
- 💰 **Cost Tracking**: Real-time API cost monitoring via Portkey
- ⚖️ **Debate Mechanism**: Multi-judge peer review scoring system
- 🔄 **Weekly Automation**: Automated pipeline to keep models up-to-date
- 🎨 **Beautiful UI**: Modern vanilla JavaScript frontend
- 📈 **Live Metrics**: Real-time performance dashboards

## 🏗️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Portkey AI** - Unified API gateway for multiple LLM providers
- **Python 3.11+** - Core language

### Frontend
- **Vanilla JavaScript** - No framework overhead
- **HTML5/CSS3** - Modern, responsive design
- **SPA Architecture** - Single-page application routing

### Evaluation
- **Multi-Judge Peer Review** - Quality scoring system
- **Category-Based Testing** - Knowledge, Math, Code, Business, Analysis
- **Automated Pipeline** - Weekly model competitions

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.11 or higher** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Portkey API Key** ([Get one free](https://portkey.ai))
- **Text Editor** (VS Code recommended)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/bhaveshbillionaier19/portkeyHAckathon.git
cd portkeyHAckathon
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
PORTKEY_API_KEY=your_portkey_api_key_here
```

> **Note**: Get your Portkey API key from [portkey.ai](https://portkey.ai)

### 4. Run the Backend

```bash
python run_backend.py
```

You should see:
```
🚀 Starting Smart Chat API Server
✅ Server will start at: http://localhost:8001
✅ API Docs at: http://localhost:8001/docs
```

### 5. Run the Frontend

Open a **new terminal** window:

```bash
cd web
python -m http.server 8080
```

### 6. Open in Browser

Navigate to: **http://localhost:8080**

🎉 **You're all set!** The application is now running locally.

## 📖 Usage Guide

### Smart Chat

1. Go to **http://localhost:8080/chat.html**
2. Type any prompt (e.g., "What is DNA?", "Calculate 2+2", "Write Python code")
3. Watch the system:
   - Classify your prompt
   - Route to the best model
   - Display response with metrics

### View Results

1. Go to **http://localhost:8080/results.html**
2. See evaluation battle results:
   - **400 questions** evaluated
   - **3 models** tested
   - **5 categories** compared
   - Best model per category

### Run Automated Pipeline

```bash
python pipeline/master.py
```

This will:
- Evaluate all models
- Run debate mechanism
- Calculate rankings
- Generate report in `logs/weekly/YYYY-MM-DD/`

## 🎮 Demo Mode vs Real API Mode

### Demo Mode (Default - No API Key Required)

The system runs in **demo mode** by default, using mock responses. Perfect for:
- ✅ Testing the interface
- ✅ Understanding the workflow
- ✅ Hackathon presentations
- ✅ No cost, no API keys needed

### Real API Mode (Requires Portkey Setup)

To use actual AI models:

1. **Get Portkey API Key**: Sign up at [portkey.ai](https://portkey.ai)
2. **Add to `.env`**: 
   ```env
   PORTKEY_API_KEY=your_actual_key
   ```
3. **Configure Virtual Keys** (optional): See `PORTKEY_SETUP.md` for details
4. Backend will automatically use real models!

> **Cost Warning**: Real API mode incurs costs (~$0.01-0.05 per request)

## 📊 Project Structure

```
portkeyHAckathon/
├── src/                          # Backend source code
│   ├── config.py                # Model configurations
│   ├── simple_llm_client.py     # Real API client (Portkey)
│   ├── demo_llm_client.py       # Demo mode client
│   ├── demo_classifier.py       # Prompt classifier
│   └── smart_router.py          # Intelligent routing
│
├── web/                          # Frontend application
│   ├── home.html                # Landing page
│   ├── chat.html                # Smart chat interface
│   ├── results.html             # Evaluation results
│   ├── home.js, chat.js, results.js
│   └── styles.css               # Styling
│
├── pipeline/                     # Automated evaluation pipeline
│   ├── master.py                # Main orchestrator
│   ├── config.yaml              # Pipeline configuration
│   └── README.md                # Pipeline guide
│
├── data/                         # Evaluation data
│   ├── real_evaluation_results.json  # 400-question results
│   ├── metrics_documentation.json    # Metrics explained
│   └── pricing_cache.json       # Model pricing
│
├── run_backend.py               # FastAPI server entry point
├── requirements.txt             # Python dependencies
└── .env                         # API keys (create this!)
```

## 🔧 Configuration

### Backend Models

Edit `src/config.py` to change model configurations:

```python
PORTKEY_MODELS = {
    "gemini": "@google/gemini-2.0-flash-exp",
    "gpt": "@openai/gpt-4o",
    "claude": "@anthropic/claude-sonnet-4-5"
}
```

### Pipeline Settings

Edit `pipeline/config.yaml` for automation:

```yaml
evaluation:
  questions_per_category: 80  # Adjust evaluation size
  
schedule:
  frequency: weekly
  day: sunday
  hour: 2
```

## 📈 Evaluation Metrics

The system evaluates models on:

- **Quality Score** (0-5): Peer review by judge models
- **Cost**: Actual API costs via Portkey
- **Latency**: Response time in milliseconds
- **Safety**: PII detection, toxicity checks
- **Performance**: Accuracy, precision, false positive rate

See `data/metrics_documentation.json` for complete details.

## 🏆 Current Results (400 Questions)

Based on comprehensive evaluation:

| Category | Winner | Score |
|----------|--------|-------|
| 📚 Knowledge | **CLAUDE** | 4.22/5 |
| 🔢 Math | **CLAUDE** | 4.50/5 |
| 💻 Code | **CLAUDE** | 4.50/5 |
| 💼 Business | **GEMINI** | 4.20/5 |
| 📈 Analysis | **GPT** | 4.27/5 |

*Results automatically update as models improve!*

## 🔄 Weekly Automation

The pipeline can run automatically every week to:

1. Check for latest model versions (Gemini 3.5, GPT-5, etc.)
2. Run 400-question evaluation
3. Calculate new rankings
4. Update routing to best models
5. Send notification reports

See `pipeline/README.md` for setup instructions.

## 🛠️ Troubleshooting

### Backend won't start

```bash
# Check if port 8001 is available
netstat -ano | findstr :8001  # Windows
lsof -i :8001  # Mac/Linux

# Kill process if needed
```

### Frontend 404 errors

Make sure you're running from the `web/` directory:
```bash
cd web
python -m http.server 8080
```

### API errors

Check `.env` file:
```bash
cat .env  # Mac/Linux
type .env  # Windows
```

Ensure `PORTKEY_API_KEY` is set correctly.

### More Help

- See `TROUBLESHOOTING.md` for common issues
- Check `PORTKEY_SETUP.md` for API configuration
- Review `pipeline/README.md` for automation setup

## 📚 Documentation

- **`README.md`** (this file) - Getting started
- **`PORTKEY_SETUP.md`** - API key configuration
- **`MODEL_ROUTING_GUIDE.md`** - Routing logic explained
- **`pipeline/README.md`** - Automation pipeline
- **`GITHUB_READY.md`** - Publishing guide

## 🎯 Use Cases

- **Production LLM Routing**: Route to optimal models in production
- **Cost Optimization**: Save 30-50% by using cheaper models where appropriate
- **Model Evaluation**: Benchmark new models before deployment
- **Research**: Study LLM performance across categories
- **Hackathons**: Demonstrate intelligent AI systems

## 🚧 Roadmap

- [ ] **Milestone 2**: Automatic model version detection
- [ ] **Milestone 3**: Full evaluation pipeline integration
- [ ] **Milestone 4**: Weekly auto-scheduler
- [ ] Multi-language support
- [ ] Custom model fine-tuning integration
- [ ] Advanced analytics dashboard

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Portkey AI** - For the amazing unified API gateway
- **FastAPI** - For the blazing-fast Python framework
- **OpenAI, Google, Anthropic** - For their incredible language models

## 📞 Contact

**Developer**: Bhavesh  
**Project**: LLM Evaluation & Smart Routing System  
**Hackathon**: Portkey AI Hackathon 2026

---

## ⚡ Quick Commands Reference

```bash
# Setup
git clone <repo-url>
cd portkeyHAckathon
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run
python run_backend.py          # Backend on :8001
python -m http.server 8080     # Frontend on :8080 (in web/ dir)
python pipeline/master.py      # Run evaluation pipeline

# Development
pip install -r requirements.txt  # Install dependencies
python -m pytest                 # Run tests
```

---

**⭐ Star this repo if you find it useful!**

**🎉 Built with ❤️ for the Portkey AI Hackathon**
