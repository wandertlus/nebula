"""
capability_engine.py
════════════════════
A capability forms when TWO conditions are simultaneously met:

1. Mass threshold — the thermodynamic cluster of the linked identity field
   has accumulated enough evidence (mass >= threshold).
2. Recent consistency — at least 5 signals in the last 30 days for that
   trajectory. High-priority signals count double.

Capabilities are informational. They expose auditable formation evidence
for the Ventures subsystem to consume.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, List


CONSISTENCY_WINDOW_DAYS = 30
CONSISTENCY_MIN_SIGNALS = 5

# capability_key → (trajectory_key, thermo_field, mass_threshold)
CAPABILITY_DEFINITIONS: Dict[str, tuple] = {
    "engineering_capability":   ("engineering",      "engineering", 3.0),
    "communication_capability": ("language_fluency", "be_fluent",   2.0),
    "physical_capability":      ("health",           "fitness",     2.0),
    "business_ops_capability":  ("entrepreneurship", "engineering", 4.0),
    "financial_capability":     ("employment",       "find_job",    3.0),
}


def _trajectory_key(ev: dict) -> str:
    traj = ev.get("trajectory")
    if isinstance(traj, dict):
        return traj.get("key", "unclassified")
    return str(traj) if traj else "unclassified"


def _parse_ts(ev: dict):
    raw = ev.get("timestamp")
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def _cluster_mass(thermo_field: str, thermo_state: dict) -> float:
    cluster = thermo_state.get(thermo_field)
    if isinstance(cluster, dict):
        return float(cluster.get("mass", 1.0) or 1.0)
    return 1.0


def _count_recent_signals(
    trajectory: str,
    events: List[dict],
    window_days: int = CONSISTENCY_WINDOW_DAYS,
) -> int:
    """
    Count weighted signals for a trajectory in the last window_days.
    High-priority signals count as 2; all others count as 1.
    System commands and zero-duration events are excluded.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    count  = 0

    for ev in events:
        if ev.get("category") == "System":
            continue
        if (ev.get("duration") or 0) <= 0:
            continue
        if _trajectory_key(ev) != trajectory:
            continue
        ts = _parse_ts(ev)
        if ts is None or ts < cutoff:
            continue
        weight = 2 if str(ev.get("priority", "")).lower() == "high" else 1
        count += weight

    return count


def compute_capabilities(
    events: List[dict],
    thermo_state: dict,
) -> dict:
    """
    Returns:
    {
        "capabilities": {
            "engineering_capability": {
                "exists": bool,
                "strength": float,
                "mass_score": float,
                "consistency_score": float,
                "linked_trajectory": str,
                "signals_last_30d": int
            },
            ...
        },
        "active_capabilities": list[str],
        "formation_threshold": {
            "mass_required": float,
            "signals_required": int,
            "window_days": int
        }
    }
    """
    capabilities: dict = {}
    active: List[str] = []

    for cap_key, (trajectory, thermo_field, mass_threshold) in CAPABILITY_DEFINITIONS.items():
        current_mass    = _cluster_mass(thermo_field, thermo_state)
        recent_signals  = _count_recent_signals(trajectory, events)

        mass_score        = round(min(1.0, current_mass / mass_threshold), 6)
        consistency_score = round(min(1.0, recent_signals / CONSISTENCY_MIN_SIGNALS), 6)

        mass_met        = current_mass >= mass_threshold
        consistency_met = recent_signals >= CONSISTENCY_MIN_SIGNALS
        exists          = mass_met and consistency_met

        # Strength: geometric mean of both scores when both conditions are met,
        # otherwise a partial score showing how far away the capability is
        if exists:
            strength = round((mass_score * consistency_score) ** 0.5, 6)
        else:
            strength = round((mass_score * consistency_score) ** 0.5 * 0.5, 6)

        capabilities[cap_key] = {
            "exists":             exists,
            "strength":           strength,
            "mass_score":         mass_score,
            "consistency_score":  consistency_score,
            "linked_trajectory":  trajectory,
            "signals_last_30d":   recent_signals,
            "mass_current":       round(current_mass, 6),
            "mass_threshold":     mass_threshold,
        }

        if exists:
            active.append(cap_key)

    return {
        "capabilities": capabilities,
        "active_capabilities": active,
        "formation_threshold": {
            "mass_required":    "per_capability (see mass_threshold field)",
            "signals_required": CONSISTENCY_MIN_SIGNALS,
            "window_days":      CONSISTENCY_WINDOW_DAYS,
        },
    }
