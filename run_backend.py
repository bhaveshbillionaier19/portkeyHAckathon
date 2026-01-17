"""
Enhanced Backend with Smart Chat Endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="LLM Evaluation & Smart Chat API",
    description="API for LLM evaluation results and smart chat routing",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://localhost:8080",  # Vanilla JS frontend
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ClassifyRequest(BaseModel):
    prompt: str

class ChatRequest(BaseModel):
    prompt: str
    conversation_history: list = []

class ChatResponse(BaseModel):
    response: str
    model_used: str
    category: str
    metrics: dict
    model_switched: bool
    switch_reason: str = ""

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "healthy",
        "service": "LLM Evaluation & Smart Chat API",
        "version": "1.0.0"
    }

@app.get("/api/evaluation-results")
async def get_evaluation_results():
    """Get complete evaluation results with all metrics"""
    try:
        results_path = os.path.join('data', 'real_evaluation_results.json')
        with open(results_path, 'r', encoding='utf-8') as f:  # Fixed: UTF-8 encoding
            results = json.load(f)
        return results
    except FileNotFoundError:
        return {
            "error": "No evaluation results found",
            "message": "Run: python evaluate_portkey.py ... first"
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/metrics-documentation")
async def get_metrics_docs():
    """Get metrics documentation"""
    try:
        docs_path = os.path.join('data', 'metrics_documentation.json')
        with open(docs_path, encoding='utf-8') as f:
            docs = json.load(f)
        return docs
    except FileNotFoundError:
        return {"error": "Metrics documentation not found"}

@app.get("/api/metrics-snapshot")
async def get_metrics_snapshot():
    """Get current metrics snapshot"""
    try:
        snapshot_path = os.path.join('data', 'current_metrics_snapshot.json')
        with open(snapshot_path, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)
        return snapshot
    except FileNotFoundError:
        return {"error": "Metrics snapshot not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading metrics: {str(e)}")


@app.post("/api/classify")
async def classify_prompt(request: ClassifyRequest):
    """Classify a prompt into a category"""
    try:
        from src.smart_classifier import classify_sentence
        
        category = classify_sentence(request.prompt)
        
        return {
            "category": category,
            "prompt": request.prompt,
            "confidence": 0.95  # Placeholder - actual confidence from classifier
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@app.get("/api/best-model")
async def get_best_model(category: str):
    """Get best model for a specific category"""
    try:
        from src.smart_router import SmartRouter
        
        router = SmartRouter()
        result = router.route(category)
        
        return {
            "model": result['model'],
            "category": result['category'],
            "reason": f"Best quality for {category} category",
            "metrics": {
                "quality": result['metrics']['average_score'],
                "min_score": result['metrics'].get('min_score', 0),
                "max_score": result['metrics'].get('max_score', 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Routing error: {str(e)}")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint - classifies prompt, routes to best model, returns response with metrics
    """
    try:
        from src.demo_classifier import demo_classify
        from src.smart_router import SmartRouter
        from src.demo_llm_client import DemoLLMClient  # Demo mode - shows all models working
        
        # 1. Classify the prompt
        category = demo_classify(request.prompt)
        
        # 2. Get best model for category
        router = SmartRouter()
        routing_result = router.route(category)
        
        # 3. Get response from the selected model
        model_name = routing_result['model']
        
        # Initialize demo client (works without API keys, shows all models)
        client = DemoLLMClient(model_name)
        
        # Generate response (returns tuple)
        response_text, metadata = client.generate(request.prompt)
        
        if response_text is None:
            raise HTTPException(status_code=500, detail=f"Generation failed: {metadata.get('error')}")
        
        # 4. Prepare response with metrics
        return ChatResponse(
            response=response_text,
            model_used=model_name,
            category=category,
            metrics={
                "cost": metadata['cost_usd'],
                "tokens": metadata['total_tokens'],
                "latency_ms": metadata['latency_ms'],
                "tokens_input": metadata['tokens_input'],
                "tokens_output": metadata['tokens_output']
            },
            model_switched=routing_result['switched'],
            switch_reason=routing_result.get('reason', '')
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("="*70)
    print("🚀 Starting Smart Chat API Server")
    print("="*70)
    print("\n✅ Server will start at: http://localhost:8001")
    print("✅ API Docs at: http://localhost:8001/docs")
    print("\n📊 Endpoints:")
    print("   GET  /api/evaluation-results")
    print("   GET  /api/metrics-documentation")
    print("   POST /api/classify")
    print("   GET  /api/best-model?category=...")
    print("   POST /api/chat")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
