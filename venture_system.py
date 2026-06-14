"""
Venture subsystem for Project Nebula.

A venture is a parallel resource-transformation system. It models operational
reality for businesses, projects, and systems without changing identity physics.
"""

from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from config import BASE_DIR


VENTURES_STATE_PATH = BASE_DIR / "ventures_state.json"

DEFAULT_VENTURE = {
    "id": "",
    "name": "",
    "type": "project",
    "resource_flow": {
        "time_in": 0,
        "money_in": 0,
        "money_out": 0,
        "energy_in": 0,
    },
    "capability_demand": {
        "business_operations": 0.0,
        "financial_management": 0.0,
        "communication": 0.0,
    },
    "mass": 0.0,
    "momentum": 0.0,
    "drift": 0.0,
}

CAPABILITY_ALIGNMENT_BRIDGE = {
    "business_operations": ("engineering",),
    "financial_management": ("entrepreneurship", "employment"),
    "communication": ("be_fluent", "relationships"),
}


def _empty_state() -> dict:
    return {
        "ventures": {},
        "schema_version": 1,
        "updated_at": None,
    }


def _coerce_venture(venture_id: str, raw: Optional[dict] = None) -> dict:
    venture = deepcopy(DEFAULT_VENTURE)
    venture["id"] = venture_id
    venture["name"] = venture_id

    if isinstance(raw, dict):
        venture.update({k: v for k, v in raw.items() if k not in {"resource_flow", "capability_demand"}})
        venture["resource_flow"].update(raw.get("resource_flow", {}))
        venture["capability_demand"].update(raw.get("capability_demand", {}))

    venture["id"] = str(venture.get("id") or venture_id)
    venture["name"] = str(venture.get("name") or venture["id"])
    if venture.get("type") not in {"business", "project", "system"}:
        venture["type"] = "project"

    for key in venture["resource_flow"]:
        venture["resource_flow"][key] = float(venture["resource_flow"].get(key, 0) or 0)
    for key in venture["capability_demand"]:
        venture["capability_demand"][key] = float(venture["capability_demand"].get(key, 0.0) or 0.0)

    venture["mass"] = max(0.0, float(venture.get("mass", 0.0) or 0.0))
    venture["momentum"] = float(venture.get("momentum", 0.0) or 0.0)
    venture["drift"] = float(venture.get("drift", 0.0) or 0.0)
    return venture


def load_ventures_state(path: Path = VENTURES_STATE_PATH) -> dict:
    path = Path(path)
    if not path.exists():
        return _empty_state()

    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError, TypeError):
        return _empty_state()

    if not isinstance(data, dict):
        return _empty_state()

    ventures = data.get("ventures", data)
    if not isinstance(ventures, dict):
        ventures = {}

    return {
        "ventures": {
            str(venture_id): _coerce_venture(str(venture_id), venture)
            for venture_id, venture in ventures.items()
        },
        "schema_version": int(data.get("schema_version", 1) or 1),
        "updated_at": data.get("updated_at"),
    }


def save_ventures_state(state: dict, path: Path = VENTURES_STATE_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    clean_state = {
        "ventures": state.get("ventures", {}),
        "schema_version": state.get("schema_version", 1),
        "updated_at": datetime.utcnow().isoformat(),
    }

    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    with open(tmp_path, "w") as f:
        json.dump(clean_state, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp_path, path)


def _capability_signal(capability: str, alignments: Dict[str, float]) -> float:
    linked_keys = CAPABILITY_ALIGNMENT_BRIDGE.get(capability, ())
    if not linked_keys:
        return 0.0
    return max(float(alignments.get(key, 0.0) or 0.0) for key in linked_keys)


def apply_venture_signal(
    payload: dict,
    alignments: Dict[str, float],
    weight: float,
    path: Optional[Path] = None,
) -> Optional[dict]:
    """
    Apply one signal to a venture if payload.venture_id is present.

    Returns an audit payload for the processed event, or None when no venture
    is attached. This function intentionally does not alter identity state.
    """
    venture_id = payload.get("venture_id")
    if not venture_id:
        return None

    venture_id = str(venture_id).strip()
    if not venture_id:
        return None

    path = Path(path) if path is not None else VENTURES_STATE_PATH
    state = load_ventures_state(path)
    ventures = state.setdefault("ventures", {})
    venture = _coerce_venture(venture_id, ventures.get(venture_id))

    previous_scalar = venture["mass"] + venture["momentum"]
    duration = float(payload.get("duration", 0) or 0)
    money_delta = float(payload.get("money_delta", 0) or 0)
    energy_delta = float(payload.get("energy_delta", 0) or 0)

    venture["resource_flow"]["time_in"] += duration
    if money_delta > 0:
        venture["resource_flow"]["money_in"] += money_delta
    elif money_delta < 0:
        venture["resource_flow"]["money_out"] += abs(money_delta)
    if energy_delta > 0:
        venture["resource_flow"]["energy_in"] += energy_delta

    capability_delta = {}
    for capability in venture["capability_demand"]:
        delta = _capability_signal(capability, alignments) * weight
        venture["capability_demand"][capability] += delta
        capability_delta[capability] = round(delta, 6)

    signal_net_money = max(money_delta, 0.0) - (abs(money_delta) if money_delta < 0 else 0.0)
    venture["mass"] = max(0.0, venture["mass"] + (signal_net_money * 0.1))

    activity_signal = 1.0
    venture["momentum"] = (0.9 * venture["momentum"]) + (0.1 * activity_signal)

    current_scalar = venture["mass"] + venture["momentum"]
    venture["drift"] = current_scalar - previous_scalar

    ventures[venture_id] = venture
    save_ventures_state(state, path)

    return {
        "venture_id": venture_id,
        "resource_flow_delta": {
            "time_in": duration,
            "money_in": money_delta if money_delta > 0 else 0.0,
            "money_out": abs(money_delta) if money_delta < 0 else 0.0,
            "energy_in": energy_delta if energy_delta > 0 else 0.0,
        },
        "capability_demand_delta": capability_delta,
        "mass": round(venture["mass"], 6),
        "momentum": round(venture["momentum"], 6),
        "drift": round(venture["drift"], 6),
        "state_after": venture,
    }
