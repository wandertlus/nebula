import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from storage import load_events, load_identity_state
from nebula_processor import ProjectNebulaProcessor
from config import CONFIG, BASE_DIR

DYNAMIC_FIELDS_PATH = BASE_DIR / "dynamic_fields.json"

def load_all_fields():
    fields = CONFIG["identity_fields"].copy()
    if DYNAMIC_FIELDS_PATH.exists():
        try:
            with open(DYNAMIC_FIELDS_PATH, "r") as f:
                dynamic = json.load(f)
                fields.update(dynamic)
        except Exception as e:
            print(f"Error loading dynamic fields: {e}")
    return fields

# Inject dynamic fields into CONFIG for initial load
CONFIG["identity_fields"] = load_all_fields()

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

@app.get("/api/field-mass")
async def get_field_mass():
    """
    Accumulated mass per identity field + pairwise connection strengths.
    Mass      = sum of alignment[field] × max(final_score, 0) across all events.
    Connection = sum of alignment[A] × alignment[B] across all events (regardless of sign).
                 Represents how often a signal activates two fields simultaneously.
    """
    events = load_events(CONFIG)
    fields = list(CONFIG["identity_fields"].keys())

    accumulated = {f: 0.0 for f in fields}
    connections = {}

    # Init all pairs
    for i, fa in enumerate(fields):
        for fb in fields[i+1:]:
            connections[f"{fa}:{fb}"] = 0.0

    for ev in events:
        all_alignments = ev.get("physics_params", {}).get("all_alignments", {})
        final_score    = ev.get("final_score", 0.0)
        contribution   = max(final_score, 0.0)

        for field in fields:
            accumulated[field] += all_alignments.get(field, 0.0) * contribution

        # Pairwise co-activation (not gated by sign — we want to see cross-field overlap even in mixed signals)
        for i, fa in enumerate(fields):
            for fb in fields[i+1:]:
                score_a = all_alignments.get(fa, 0.0)
                score_b = all_alignments.get(fb, 0.0)
                connections[f"{fa}:{fb}"] += score_a * score_b

    total = sum(accumulated.values()) or 1.0
    normalized = {f: round(accumulated[f] / total, 6) for f in fields}
    dominant   = max(accumulated, key=accumulated.get)

    # Normalize connection strengths to [0..1] range
    max_conn = max(connections.values()) if connections else 1.0
    norm_connections = {
        k: round(v / max_conn, 6) if max_conn > 0 else 0.0
        for k, v in connections.items()
    }

    return {
        "field_masses":  normalized,
        "raw_masses":    {f: round(v, 6) for f, v in accumulated.items()},
        "connections":   norm_connections,   # { "engineering:fitness": 0.72, ... }
        "dominant":      dominant,
        "total_events":  len(events),
    }

@app.post("/api/signal")
async def process_signal(payload: SignalPayload):
    # ── COMMAND HANDLING ──────────────────────────────────────────────────────
    if payload.action_text.startswith("/") or payload.action_text.startswith("!"):
        cmd_parts = payload.action_text.split(" ", 2)
        cmd = cmd_parts[0][1:].lower()
        
        if cmd in ["add-field", "field", "north-star"]:
            if len(cmd_parts) < 3:
                return {"status": "error", "message": "Format: /add-field <key> <description>"}
            
            field_key = cmd_parts[1].lower().strip()
            field_desc = cmd_parts[2].strip()
            
            # Save to dynamic_fields.json
            dynamic = {}
            if DYNAMIC_FIELDS_PATH.exists():
                with open(DYNAMIC_FIELDS_PATH, "r") as f:
                    dynamic = json.load(f)
            
            dynamic[field_key] = field_desc
            with open(DYNAMIC_FIELDS_PATH, "w") as f:
                json.dump(dynamic, f, indent=4)
            
            # Reload and Re-initialize
            CONFIG["identity_fields"] = load_all_fields()
            global processor
            processor = ProjectNebulaProcessor(CONFIG)
            
            return {
                "status": "command_success",
                "message": f"Identity field '{field_key}' registered. Semantic core re-encoded.",
                "event": {
                    "timestamp": "2026-05-17T00:00:00", # Dummy for feed feedback
                    "action_text": f"SYSTEM: Identity expansion — Core '{field_key}' initialized.",
                    "category": "System",
                    "state": "Command",
                    "final_score": 0.0
                }
            }

    # ── SIGNAL PROCESSING ─────────────────────────────────────────────────────
    payload_dict = payload.model_dump(exclude_none=True)
    result_json = processor.project_signal_state(payload_dict)
    
    try:
        result = json.loads(result_json)
        return result
    except json.JSONDecodeError:
        return {"error": "Failed to decode processor output"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
