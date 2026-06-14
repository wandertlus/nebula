# Project Nebula FastAPI API Server - Database Reset Triggered
import json
import uuid
import hashlib
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

import threading
import time
from storage import load_events, load_identity_state, save_event
from nebula_processor import ProjectNebulaProcessor
from config import CONFIG, BASE_DIR
from physics_domain import resources_payload, trajectories_payload
from venture_system import load_ventures_state

DYNAMIC_FIELDS_PATH = BASE_DIR / "dynamic_fields.json"
THERMODYNAMIC_STATE_PATH = BASE_DIR / "thermodynamic_state.json"


# ── THERMODYNAMIC STATE ───────────────────────────────────────────────────────

def load_thermodynamic_state() -> dict:
    """
    Load the persisted thermodynamic state from disk.
    Schema: { field: { "mass": float, "momentum": float } }
    If missing, bootstraps from historical event log (mass from accumulated
    mass_impact, momentum starts at floor of 0.01).
    """
    if THERMODYNAMIC_STATE_PATH.exists():
        try:
            with open(THERMODYNAMIC_STATE_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    # Bootstrap from historical events
    fields = list(CONFIG["identity_fields"].keys())
    state = {f: {"mass": 1.0, "momentum": 0.01} for f in fields}
    try:
        events = load_events(CONFIG)
        for ev in events:
            dominant = ev.get("dominant_attractor")
            mass_impact = ev.get("physics", {}).get("mass_impact", 0.0)
            if dominant and dominant in state and mass_impact > 0:
                state[dominant]["mass"] = max(1.0, state[dominant]["mass"] + mass_impact)
    except Exception:
        pass

    save_thermodynamic_state(state)
    return state


def save_thermodynamic_state(state: dict):
    """Persist the thermodynamic state to disk."""
    try:
        with open(THERMODYNAMIC_STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)
    except OSError as e:
        print(f"[Thermodynamics] Could not save state: {e}")


# In-memory thermodynamic state — loaded once on startup
_thermo_state: dict = {}

def load_all_fields():
    fields = CONFIG["identity_fields"].copy()
    if DYNAMIC_FIELDS_PATH.exists():
        try:
            with open(DYNAMIC_FIELDS_PATH, "r") as f:
                dynamic = json.load(f)
                fields.update(dynamic)
        except Exception as e:
            print(f"Error loading dynamic fields: {e}")
    
    # Ensure every field has a color in CONFIG
    if "identity_colors" not in CONFIG:
        CONFIG["identity_colors"] = {}
    
    for field in fields:
        if field not in CONFIG["identity_colors"]:
            # Generate a stable color based on the name
            hash_hex = hashlib.md5(field.encode()).hexdigest()
            CONFIG["identity_colors"][field] = f"#{hash_hex[:6]}"
    return fields

# Inject dynamic fields into CONFIG for initial load
CONFIG["identity_fields"] = load_all_fields()

app = FastAPI(title="Project Nebula API")


# ── THERMODYNAMIC DECAY ENGINE ────────────────────────────────────────────────

def apply_thermodynamic_decay():
    """
    Thermodynamic decay tick — runs every hour via APScheduler.

    Momentum is intentionally temporal: it represents recent activity and
    active trajectory energy, so it decays much faster than stored mass.
    Stored mass represents accumulated evidence and decays slowly.

    Each identity cluster:
      - momentum *= 0.85  (15% decay per tick, floor: 0.01)
      - mass     *= 0.995 (0.5% decay per tick, floor: 1.0)
    """
    global _thermo_state
    fields = list(CONFIG["identity_fields"].keys())
    now = datetime.utcnow().isoformat()

    changed = False
    for field in fields:
        cluster = _thermo_state.setdefault(field, {"mass": 1.0, "momentum": 0.01})
        prev_momentum = cluster["momentum"]
        prev_mass = cluster["mass"]

        cluster["momentum"] = max(0.01, prev_momentum * 0.85)
        cluster["mass"]     = max(1.0,  prev_mass * 0.995)

        if cluster["momentum"] != prev_momentum or cluster["mass"] != prev_mass:
            changed = True

    if changed:
        _thermo_state["_last_decay"] = now
        save_thermodynamic_state(_thermo_state)
        print(f"[Thermodynamics] Decay applied at {now}")


def _ensure_all_fields_in_thermo():
    """Ensure newly added identity fields are present in the thermo state."""
    for field in CONFIG["identity_fields"]:
        _thermo_state.setdefault(field, {"mass": 1.0, "momentum": 0.01})


# Load initial thermodynamic state
_thermo_state = load_thermodynamic_state()
_ensure_all_fields_in_thermo()

# Threading-based background decay scheduler (no external deps)
_decay_stop_event = threading.Event()

def _decay_loop():
    """Background daemon: sleeps 1 hour then fires thermodynamic decay."""
    while not _decay_stop_event.wait(timeout=3600):
        apply_thermodynamic_decay()

_decay_thread = threading.Thread(target=_decay_loop, daemon=True, name="thermo-decay")
_decay_thread.start()
print("[Thermodynamics] Decay scheduler started — interval: 1 hour")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = ProjectNebulaProcessor(CONFIG)

def save_system_command_event(action_text: str, field_key: Optional[str] = None, score: float = 0.0):
    fields = list(CONFIG["identity_fields"].keys())
    dominant = field_key if field_key in CONFIG["identity_fields"] else (fields[0] if fields else "system")
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "action_text": action_text,
        "category": "System",
        "priority": "high",
        "duration": 0,
        "alignment_score": 1.0 if field_key else 0.0,
        "weight": 0.0,
        "final_score": score,
        "state": "Command",
        "dominant_attractor": dominant,
        "global_dominant_identity": dominant,
        "physics_params": {
            "all_alignments": {f: (1.0 if f == field_key else 0.0) for f in fields},
            "active_backend": processor.backend,
            "command": True,
        },
    }
    save_event(event, CONFIG)
    return event

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
    behavioral_type: Optional[str] = None
    event_type: Optional[str] = None
    # Soporte para resultados planos desde scripts de carga
    result_type: Optional[str] = None
    result_value: Optional[float] = None
    result_unit: Optional[str] = None
    result_text: Optional[str] = None
    effort_signals: Optional[EffortSignals] = None
    resource_transformation: Optional[Dict[str, Any]] = None
    venture_id: Optional[str] = None
    money_delta: Optional[float] = None
    energy_delta: Optional[float] = None

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
        "identities": processor.identities,
        "identity_colors": CONFIG.get("identity_colors", {})
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
    
    # Relative visibility boost: If total events are low, ensure minimal mass for visibility
    event_count = len(events)
    if event_count < 10:
        # Distribute a base mass of 0.2 to all fields so they are never "zero" size
        normalized = {f: round((v + 0.2) / (1.0 + (0.2 * len(fields))), 6) for f, v in normalized.items()}

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
        "field_colors":  CONFIG.get("identity_colors", {}),
    }

@app.get("/api/resources")
async def get_resources():
    """Expose canonical resources as first-class capacities."""
    return {"resources": resources_payload()}

@app.get("/api/trajectories")
async def get_trajectories():
    """Expose trajectory definitions that bridge transformations to identities."""
    return {"trajectories": trajectories_payload()}

@app.get("/api/ventures")
async def get_ventures():
    """Expose venture subsystem state without affecting identity physics."""
    return load_ventures_state()

@app.post("/api/signal")
async def process_signal(payload: SignalPayload):
    global processor

    # ── COMMAND HANDLING ──────────────────────────────────────────────────────
    if payload.action_text.startswith("/") or payload.action_text.startswith("!"):
        cmd_parts = payload.action_text.split(" ", 2)
        cmd = cmd_parts[0][1:].lower()

        if cmd in ["help", "h", "?"]:
            help_text = (
                "═══ NEBULA OBSERVATORY — SYSTEM MANUAL ═══\n"
                "\n"
                "── SIGNAL SUBMISSION ──\n"
                "Type any action, choose CAT / PRI / MIN, then press Execute.\n"
                "Examples:\n"
                "  • \"Built auth module\"  (Work / high / 45 min)\n"
                "  • \"Gym heavy legs\"     (Health / high / 60 min)\n"
                "  • \"Read distributed systems paper\" (Education / medium / 30 min)\n"
                "  • \"Scrolled social media\" (Distraction / low / 20 min)\n"
                "\n"
                "── COMMANDS ──\n"
                "  /help, /h, /?              Show this manual\n"
                "  /add-field <key> <desc>    Create a new identity attractor\n"
                "  /field <key> <desc>        Alias for /add-field\n"
                "  /north-star <key> <desc>   Alias for /add-field\n"
                "  /delete-field <key>        Remove a custom identity field\n"
                "  /remove-field, /rm-field   Aliases for /delete-field\n"
                "\n"
                "── PHYSICS ENGINE ──\n"
                "  Impact = Alignment × Weight × Duration^β × Effort^γ\n"
                "  β = 0.7 (diminishing returns on time)\n"
                "  γ = 1.3 (amplified returns on cognitive effort)\n"
                "  Semantic backend: MiniLM (all-MiniLM-L6-v2) when available, TF-IDF fallback.\n"
                "\n"
                "── BEHAVIORAL TYPES ──\n"
                "  STRUCTURED  → High mass gain (0.8), low momentum (0.2). Deep work sessions.\n"
                "  CASUAL      → Low mass gain (0.05), high momentum (0.9). Quick activities.\n"
                "  DEGENERATE  → Negative mass (-0.4) and momentum (-0.8). Entropic signals.\n"
                "  Auto-classified from category, priority, duration, and results.\n"
                "\n"
                "── DUAL ENERGY MODEL ──\n"
                "  mass_impact     → Permanent growth of the identity cluster sphere.\n"
                "  momentum_burst  → Temporary glow + vibration (decays to zero).\n"
                "\n"
                "── THERMODYNAMIC DECAY ──\n"
                "  Every hour, background engine applies entropy:\n"
                "    momentum × 0.85  (15% decay per hour, floor: 0.01)\n"
                "    mass     × 0.995 (0.5% decay per hour, floor: 1.0)\n"
                "  Inactivity causes clusters to slowly cool and shrink.\n"
                "  Consistent effort counteracts decay and grows the attractor.\n"
                "\n"
                "── IDENTITY DRIFT ──\n"
                "  I(t+1) = α·I(t) + (1-α)·Signal(t)\n"
                "  α = 0.9 (inertia — identity resists sudden change).\n"
                "  Tracks who you are becoming through the semantic centroid.\n"
                "\n"
                "── API ENDPOINTS ──\n"
                "  GET  /api/events                All processed signals\n"
                "  GET  /api/state                 Identity vector + efficiency\n"
                "  GET  /api/field-mass             Cluster masses + connections\n"
                "  GET  /api/thermodynamic-state    Live mass/momentum per cluster\n"
                "  POST /api/signal                 Submit a new signal\n"
                "\n"
                "═══════════════════════════════════════════"
            )
            event = save_system_command_event(help_text)
            return {"status": "command_success", "message": help_text, "event": event}
        
        if cmd in ["add-field", "field", "north-star"]:
            if len(cmd_parts) < 3:
                return {"status": "error", "message": "Format: /add-field <key> <description>"}
            
            field_key = cmd_parts[1].lower().strip().strip("<>[]()")
            field_desc = cmd_parts[2].strip().strip("<>[]()")
            
            # Save to dynamic_fields.json
            dynamic = {}
            if DYNAMIC_FIELDS_PATH.exists():
                with open(DYNAMIC_FIELDS_PATH, "r") as f:
                    dynamic = json.load(f)
            
            dynamic[field_key] = field_desc
            with open(DYNAMIC_FIELDS_PATH, "w") as f:
                json.dump(dynamic, f, indent=4)
            
            # Assign a random/stable color to the new field
            hash_hex = hashlib.md5(field_key.encode()).hexdigest()
            CONFIG["identity_colors"][field_key] = f"#{hash_hex[:6]}"

            # Reload and Re-initialize
            CONFIG["identity_fields"] = load_all_fields()
            processor = ProjectNebulaProcessor(CONFIG)
            
            system_event = save_system_command_event(
                f"SYSTEM: Identity core '{field_key}' initialized semantically.\nDescription: {field_desc}",
                field_key=field_key,
                score=5.0,
            )
            
            return {
                "status": "command_success",
                "message": f"Identity field '{field_key}' registered. Semantic core re-encoded.",
                "event": system_event
            }

        if cmd in ["delete-field", "remove-field", "rm-field"]:
            if len(cmd_parts) < 2:
                return {"status": "error", "message": "Format: /delete-field <key>"}

            field_key = cmd_parts[1].lower().strip().strip("<>[]()")
            dynamic = {}
            if DYNAMIC_FIELDS_PATH.exists():
                with open(DYNAMIC_FIELDS_PATH, "r") as f:
                    dynamic = json.load(f)

            if field_key not in dynamic:
                message = f"Field '{field_key}' is not a removable custom field. Built-in fields must be edited in config.py."
                event = save_system_command_event(f"SYSTEM: {message}")
                return {"status": "error", "message": message, "event": event}

            del dynamic[field_key]
            with open(DYNAMIC_FIELDS_PATH, "w") as f:
                json.dump(dynamic, f, indent=4)

            CONFIG["identity_colors"].pop(field_key, None)
            CONFIG["identity_fields"] = load_all_fields()
            processor = ProjectNebulaProcessor(CONFIG)

            event = save_system_command_event(f"SYSTEM: Identity core '{field_key}' removed from active semantic fields.")
            return {
                "status": "command_success",
                "message": f"Identity field '{field_key}' removed. Semantic core re-encoded.",
                "event": event,
            }

    # ── SIGNAL PROCESSING ─────────────────────────────────────────────────────
    payload_dict = payload.model_dump(exclude_none=True)
    result_json = processor.project_signal_state(payload_dict)
    
    try:
        result = json.loads(result_json)

        # ── THERMODYNAMIC STATE UPDATE ─────────────────────────────────────────
        # On every processed signal, update the target cluster's thermodynamic state
        dominant = result.get("dominant_attractor")
        physics = result.get("physics", {})
        mass_impact    = physics.get("mass_impact", 0.0)
        momentum_burst = physics.get("momentum_burst", 0.0)

        if dominant and dominant in _thermo_state:
            _thermo_state[dominant]["mass"]     = max(1.0, _thermo_state[dominant]["mass"] + mass_impact)
            _thermo_state[dominant]["momentum"] = max(0.01, min(10.0, _thermo_state[dominant]["momentum"] + momentum_burst))
            save_thermodynamic_state(_thermo_state)

        return result
    except json.JSONDecodeError:
        return {"error": "Failed to decode processor output"}

@app.on_event("shutdown")
async def shutdown_scheduler():
    """Signal the decay thread to stop on server exit."""
    _decay_stop_event.set()
    print("[Thermodynamics] Decay scheduler stopped.")


@app.get("/api/thermodynamic-state")
async def get_thermodynamic_state():
    """Expose current thermodynamic mass and momentum for every identity cluster."""
    _ensure_all_fields_in_thermo()
    fields = list(CONFIG["identity_fields"].keys())
    return {
        "clusters": {
            f: {
                "mass":     round(_thermo_state[f]["mass"], 6),
                "momentum": round(_thermo_state[f]["momentum"], 6),
            }
            for f in fields if f in _thermo_state
        },
        "last_decay": _thermo_state.get("_last_decay"),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
