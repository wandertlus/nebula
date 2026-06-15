"""
coherence_engine.py
═══════════════════
Measures whether resources concentrate on constructive trajectories
or disperse into opposing directions.

Formula:
    constructive_ratio = constructive_time / total_time
    consistency_avg    = mean(active_days / window_days) per constructive trajectory
    coherence          = constructive_ratio * 0.6 + consistency_avg * 0.4

Window per trajectory:
    window_days(T) = clamp(mass(T) * 7, min=7, max=90)
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, List


ENTROPIC_TRAJECTORIES = {"unstructured_drain", "unclassified"}
ENTROPIC_CATEGORIES   = {"Distraction", "Void"}

TRAJECTORY_TO_FIELD: Dict[str, str] = {
    "engineering":      "engineering",
    "language_fluency": "be_fluent",
    "health":           "fitness",
    "employment":       "find_job",
    "entrepreneurship": "engineering",
}

DEFINITION = (
    "Coherence measures whether time and effort concentrate on constructive "
    "trajectories (constructive_ratio) and whether that activity is distributed "
    "consistently across days within a dynamic window proportional to accumulated mass "
    "(consistency_avg). Score 0.0–1.0."
)


def _trajectory_key(ev: dict) -> str:
    traj = ev.get("trajectory")
    if isinstance(traj, dict):
        return traj.get("key", "unclassified")
    return str(traj) if traj else "unclassified"


def _is_entropic(ev: dict) -> bool:
    return (
        _trajectory_key(ev) in ENTROPIC_TRAJECTORIES
        or str(ev.get("category", "")).strip() in ENTROPIC_CATEGORIES
    )


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


def _day_in_window(day_str: str, cutoff: datetime, now: datetime) -> bool:
    try:
        d = datetime.strptime(day_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return cutoff <= d <= now
    except ValueError:
        return False


def _cluster_mass(trajectory: str, thermo_state: dict) -> float:
    field = TRAJECTORY_TO_FIELD.get(trajectory)
    if field and field in thermo_state:
        cluster = thermo_state[field]
        if isinstance(cluster, dict):
            return float(cluster.get("mass", 1.0) or 1.0)
    return 1.0


def _window_days(mass: float) -> int:
    return int(min(90, max(7, mass * 7)))


def compute_coherence(
    events: List[dict],
    thermo_state: dict,
) -> dict:
    """
    Returns:
    {
        "score": float,
        "status": str,
        "window_days_per_trajectory": dict,
        "constructive_ratio": float,
        "consistency_avg": float,
        "active_trajectories": list[str],
        "entropic_ratio": float,
        "signals_analyzed": int,
        "definition": str
    }
    """
    signals = [
        ev for ev in events
        if ev.get("category") != "System"
        and not str(ev.get("action_text", "")).startswith("/")
        and (ev.get("duration") or 0) > 0
    ]

    if len(signals) < 5:
        return {
            "score":                      0.0,
            "status":                     "insufficient_data",
            "window_days_per_trajectory": {},
            "constructive_ratio":         0.0,
            "consistency_avg":            0.0,
            "active_trajectories":        [],
            "entropic_ratio":             0.0,
            "signals_analyzed":           len(signals),
            "definition":                 DEFINITION,
        }

    now = datetime.now(timezone.utc)

    total_minutes        = 0.0
    constructive_minutes = 0.0
    entropic_minutes     = 0.0
    constructive_days: Dict[str, set] = {}

    for ev in signals:
        duration = float(ev.get("duration", 0) or 0)
        traj_key = _trajectory_key(ev)
        ts       = _parse_ts(ev)

        total_minutes += duration

        if _is_entropic(ev):
            entropic_minutes += duration
        else:
            constructive_minutes += duration
            if traj_key not in constructive_days:
                constructive_days[traj_key] = set()
            if ts:
                constructive_days[traj_key].add(ts.strftime("%Y-%m-%d"))

    constructive_ratio = constructive_minutes / total_minutes if total_minutes > 0 else 0.0
    entropic_ratio     = entropic_minutes / total_minutes if total_minutes > 0 else 0.0

    window_days_map: Dict[str, int] = {}
    consistency_scores: List[float] = []

    for traj_key, day_set in constructive_days.items():
        mass   = _cluster_mass(traj_key, thermo_state)
        window = _window_days(mass)
        window_days_map[traj_key] = window

        cutoff = now - timedelta(days=window)
        active_in_window = sum(
            1 for d in day_set if _day_in_window(d, cutoff, now)
        )
        consistency_scores.append(min(1.0, active_in_window / window))

    consistency_avg = (
        sum(consistency_scores) / len(consistency_scores)
        if consistency_scores else 0.0
    )

    coherence = round(constructive_ratio * 0.6 + consistency_avg * 0.4, 6)

    if coherence >= 0.7:
        status = "high"
    elif coherence >= 0.4:
        status = "moderate"
    else:
        status = "low"

    return {
        "score":                      coherence,
        "status":                     status,
        "window_days_per_trajectory": window_days_map,
        "constructive_ratio":         round(constructive_ratio, 6),
        "consistency_avg":            round(consistency_avg, 6),
        "active_trajectories":        list(constructive_days.keys()),
        "entropic_ratio":             round(entropic_ratio, 6),
        "signals_analyzed":           len(signals),
        "definition":                 DEFINITION,
    }
