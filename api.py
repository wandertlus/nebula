import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from storage import load_events, load_identity_state
from nebula_processor import ProjectNebulaProcessor
from config import CONFIG

app = FastAPI(title="Project Nebula API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = ProjectNebulaProcessor()

class EffortSignals(BaseModel):
    result_type: Optional[str] = None
    result_value: Optional[float] = None
    result_unit: Optional[str] = None
    result_text: Optional[str] = None
    custom: Optional[Dict[str, Any]] = None

class SignalPayload(BaseModel):
    action_text: str
    category: str
    priority: str = "medium"
    duration: int = 0
    effort_signals: Optional[EffortSignals] = None

@app.get("/api/events")
async def get_events():
    events = load_events(CONFIG)
    return {"events": events}

@app.get("/api/state")
async def get_state():
    dim = 384 if (processor.backend == "minilm" and processor.minilm_available) else len(processor.vectorizer.get_feature_names_out())
    identity_vector, efficiency_by_cat = load_identity_state(dim, CONFIG)
    return {
        "identity_vector": identity_vector,
        "efficiency_by_category": efficiency_by_cat,
        "identities": processor.identities
    }

@app.post("/api/signal")
async def process_signal(payload: SignalPayload):
    # Convert payload to dict, removing None values in effort_signals
    payload_dict = payload.model_dump(exclude_none=True)
    
    # Send through the processor
    result_json = processor.project_signal_state(payload_dict)
    
    try:
        result = json.loads(result_json)
        return result
    except json.JSONDecodeError:
        return {"error": "Failed to decode processor output"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
