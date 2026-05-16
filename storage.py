import json
from datetime import datetime
from config import CONFIG

def _empty_identity_vector(dim):
    return [0.0] * dim

def _coerce_identity_vector(vector, dim):
    if len(vector) == 1 and isinstance(vector[0], list):
        vector = vector[0]

    if len(vector) != dim:
        return _empty_identity_vector(dim)

    try:
        return [float(value) for value in vector]
    except (TypeError, ValueError):
        return _empty_identity_vector(dim)

def load_identity_state(dim, config=CONFIG):
    """Loads the persisted identity vector, or returns an empty vector."""
    identity_state_path = config["identity_state_path"]

    if not identity_state_path.exists():
        return _empty_identity_vector(dim)

    try:
        with open(identity_state_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError, TypeError):
        return _empty_identity_vector(dim)

    if not isinstance(data, dict):
        return _empty_identity_vector(dim)

    vector = data.get("identity_vector", data.get("accumulated_vector", []))
    if not isinstance(vector, list):
        return _empty_identity_vector(dim)

    return _coerce_identity_vector(vector, dim)

def save_identity_state(vector, config=CONFIG):
    """Persists the identity vector to the configured JSON state file."""
    identity_state_path = config["identity_state_path"]
    identity_state_path.parent.mkdir(parents=True, exist_ok=True)
    vector = [float(value) for value in vector]

    with open(identity_state_path, "w") as f:
        json.dump({
            "identity_vector": vector,
            "dimension": len(vector),
            "updated_at": datetime.utcnow().isoformat()
        }, f)

def save_event(event):
    """Persists an event to the configured JSONL storage."""
    event_log_path = CONFIG["event_log_path"]
    
    # Ensure the parent directory exists
    event_log_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure timestamp is present
    if "timestamp" not in event:
        event["timestamp"] = datetime.utcnow().isoformat()

    with open(event_log_path, "a") as f:
        f.write(json.dumps(event) + "\n")
