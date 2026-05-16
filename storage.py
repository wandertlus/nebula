import json
from datetime import datetime
from config import CONFIG


# ── IDENTITY VECTOR ───────────────────────────────────────────────────────────

def _empty_identity_vector(dim):
    return [0.0] * dim


def _coerce_identity_vector(vector, dim):
    if len(vector) == 1 and isinstance(vector[0], list):
        vector = vector[0]
    if len(vector) != dim:
        return _empty_identity_vector(dim)
    try:
        return [float(v) for v in vector]
    except (TypeError, ValueError):
        return _empty_identity_vector(dim)


def load_identity_state(dim, config=CONFIG):
    """
    Loads the full persisted identity state, returning:
        identity_vector   : list[float]  — the accumulated embedding centroid
        efficiency_by_cat : dict[str, float] — EMA of efficiency per category
    """
    path = config["identity_state_path"]

    if not path.exists():
        return _empty_identity_vector(dim), {}

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError, TypeError):
        return _empty_identity_vector(dim), {}

    if not isinstance(data, dict):
        return _empty_identity_vector(dim), {}

    # Support old schema key ("accumulated_vector") transparently
    raw_vector = data.get("identity_vector", data.get("accumulated_vector", []))
    if not isinstance(raw_vector, list):
        raw_vector = []

    vector = _coerce_identity_vector(raw_vector, dim)
    efficiency_by_cat = data.get("efficiency_by_category", {})

    return vector, efficiency_by_cat


def save_identity_state(vector, efficiency_by_cat, config=CONFIG):
    """
    Persists the identity vector and per-category efficiency EMA.
    Schema:
        identity_vector        : list[float]
        dimension              : int
        efficiency_by_category : dict[str, float]
        updated_at             : ISO-8601 string
    """
    path = config["identity_state_path"]
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w") as f:
        json.dump({
            "identity_vector":        [float(v) for v in vector],
            "dimension":              len(vector),
            "efficiency_by_category": efficiency_by_cat,
            "updated_at":             datetime.utcnow().isoformat(),
        }, f, indent=2)


# ── EVENT LOG ─────────────────────────────────────────────────────────────────

def save_event(event, config=CONFIG):
    """Appends a processed event to the JSONL event log."""
    path = config["event_log_path"]
    path.parent.mkdir(parents=True, exist_ok=True)

    if "timestamp" not in event:
        event["timestamp"] = datetime.utcnow().isoformat()

    with open(path, "a") as f:
        f.write(json.dumps(event) + "\n")


def load_events(config=CONFIG):
    """
    Reads all events from the JSONL log.
    Returns a list of dicts, skipping malformed lines silently.
    """
    path = config["event_log_path"]
    if not path.exists():
        return []

    events = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events