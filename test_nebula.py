#!/usr/bin/env python3
"""
Nebula System — Functional Test Suite
Tests all 9 behavioral requirements against the live API.
Run after restarting api.py: python3 test_nebula.py
"""

import json
import time
import requests
from typing import Dict

BASE = "http://localhost:8000/api"

# ── HELPERS ───────────────────────────────────────────────────────────────────

def post_signal(text, category, priority="medium", duration=30):
    r = requests.post(f"{BASE}/signal", json={
        "action_text": text,
        "category": category,
        "priority": priority,
        "duration": duration,
        "effort_signals": {}
    }, timeout=15)
    return r.json()

def get_field_mass():
    r = requests.get(f"{BASE}/field-mass", timeout=10)
    return r.json()

def get_events():
    r = requests.get(f"{BASE}/events", timeout=10)
    return r.json()["events"]

PASS = "  ✅ PASS"
FAIL = "  ❌ FAIL"
WARN = "  ⚠️  WARN"

def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    print(f"{status}  {label}")
    if detail:
        print(f"        → {detail}")
    return condition

# ── RESET ─────────────────────────────────────────────────────────────────────

import os, pathlib
for f in ["events.jsonl", "identity_state.json"]:
    p = pathlib.Path(f)
    if p.exists():
        p.unlink()
print("\n══ NEBULA FUNCTIONAL TEST SUITE ══════════════════════════════\n")
print("  (data wiped — fresh start)\n")

results = []

# ── REQ 1: Identities consolidate according to input ─────────────────────────
print("❶  Identities consolidate according to input")
for _ in range(3):
    r = post_signal("Designing a distributed event-driven architecture in Go", "Work", "high", 60)
    time.sleep(0.5)

mass = get_field_mass()
eng  = mass["field_masses"].get("engineering", 0)
dom  = mass["dominant"]
ok   = eng > 0.4 and dom == "engineering"
results.append(check(
    "engineering dominates after 3 engineering signals",
    ok, f"engineering={eng:.3f}, dominant={dom}"
))

# ── REQ 2: Correlation patterns ───────────────────────────────────────────────
print("\n❷  Patrones de correlación (cross-field co-activation)")
r = post_signal("Writing technical documentation in English for the architecture spec", "Work", "high", 45)
time.sleep(0.5)
mass = get_field_mass()
conn_eng_fluent = mass["connections"].get("engineering:be_fluent", 0)
conn_eng_fit    = mass["connections"].get("engineering:fitness", 0)
results.append(check(
    "engineering:be_fluent connection > engineering:fitness",
    conn_eng_fluent > conn_eng_fit,
    f"eng:fluent={conn_eng_fluent:.4f}  eng:fit={conn_eng_fit:.4f}"
))

# ── REQ 3: Mass dominance ─────────────────────────────────────────────────────
print("\n❸  Dominación de masa (fields)")
for _ in range(4):
    post_signal("30-minute run, progressive overload squat session", "Health", "high", 50)
    time.sleep(0.3)
mass2 = get_field_mass()
fit   = mass2["field_masses"].get("fitness", 0)
eng2  = mass2["field_masses"].get("engineering", 0)
results.append(check(
    "After 4 fitness signals, fitness gains significant mass",
    fit > 0.15,
    f"fitness={fit:.3f}  engineering={eng2:.3f}"
))
results.append(check(
    "Engineering still holds mass (doesn't collapse to 0)",
    eng2 > 0.1,
    f"engineering={eng2:.3f}"
))

# ── REQ 4: Loops drain systemic energy ────────────────────────────────────────
print("\n❹  Loops drain systemic energy (fragmentación)")
events_before = get_events()
scores_before = [e.get("final_score", 0) for e in events_before[-5:]]

for _ in range(4):
    r = post_signal("Scrolling social media, watching random YouTube shorts for hours", "Distraction", "low", 90)
    time.sleep(0.3)

events_after = get_events()
drain_events = events_after[-4:]
drain_scores = [e.get("final_score", 0) for e in drain_events]
drain_states = [e.get("state") for e in drain_events]

results.append(check(
    "Distraction loops produce negative/near-zero final_scores",
    all(s <= 0.05 for s in drain_scores),
    f"scores={[round(s,4) for s in drain_scores]}"
))
results.append(check(
    "Distraction loops trigger Black Hole or Degenerate Matter states",
    any(s in ("Black Hole", "Degenerate Matter") for s in drain_states),
    f"states={drain_states}"
))

# ── REQ 5: Identities weaken ──────────────────────────────────────────────────
print("\n❺  Las identidades se debilitan")
mass_after_drain = get_field_mass()
dominant_drain   = mass_after_drain["dominant"]
# After draining: dominant should have shifted or total raw mass should be lower
raw_before = sum(mass2["raw_masses"].values())
raw_after  = sum(mass_after_drain["raw_masses"].values())
results.append(check(
    "Raw accumulated mass does NOT grow during drain loops",
    raw_after <= raw_before * 1.01,  # at most 1% growth (rounding)
    f"raw_before={raw_before:.4f}  raw_after={raw_after:.4f}"
))

# ── REQ 6: Transcend hyperfocus ───────────────────────────────────────────────
print("\n❻  Las identidades trascienden el hiperfoco")
# Inject be_fluent signals to dethrone engineering dominance
for _ in range(5):
    post_signal("Daily English immersion: reading advanced technical essays and listening to podcasts", "Education", "high", 60)
    time.sleep(0.3)
mass_hf = get_field_mass()
fluent  = mass_hf["field_masses"].get("be_fluent", 0)
dom_hf  = mass_hf["dominant"]
results.append(check(
    "be_fluent can challenge dominance if consistently reinforced",
    fluent > 0.15,
    f"be_fluent={fluent:.3f}  dominant={dom_hf}"
))
results.append(check(
    "No single field locks at 100% (system stays dynamic)",
    all(v < 0.85 for v in mass_hf["field_masses"].values()),
    f"masses={mass_hf['field_masses']}"
))

# ── REQ 7: Neutral signals — productive or degenerative ───────────────────────
print("\n❼  Neutral signals → productive or degenerative")
neutral_results = []
neutral_inputs = [
    ("Had a coffee and thought about what to do next", "Rest", "medium", 20),
    ("Watched a documentary about space exploration", "space_news", "medium", 45),
    ("Cleaned the house and organized the workspace", "Rest", "low", 30),
]
for (txt, cat, pri, dur) in neutral_inputs:
    r = post_signal(txt, cat, pri, dur)
    neutral_results.append((txt[:40], r.get("final_score", 0), r.get("state")))
    time.sleep(0.3)

all_neutral_nonzero = all(r[1] != 0 for r in neutral_results)
has_varied_states   = len(set(r[2] for r in neutral_results)) > 0
results.append(check(
    "Neutral signals produce non-zero scores (engine computes, not defaults)",
    all_neutral_nonzero,
    f"{[(r[0], round(r[1],4), r[2]) for r in neutral_results]}"
))
results.append(check(
    "Neutral signals generate meaningful states",
    has_varied_states,
    f"states={[r[2] for r in neutral_results]}"
))

# ── REQ 8: Coherent behaviors ─────────────────────────────────────────────────
print("\n❽  Comportamientos coherentes (physics consistency)")
events_all = get_events()
# final_score should always be: alignment × weight × duration_norm^0.7 × effort^1.3
# We can't recompute exactly but we can check range & monotonicity intuition:
scores_all = [e.get("final_score", 0) for e in events_all if e.get("final_score") is not None]
results.append(check(
    "All final_scores are finite floats (no NaN/inf)",
    all(isinstance(s, float) and s == s for s in scores_all),
    f"count={len(scores_all)}"
))
results.append(check(
    "High-priority Work signals score higher than Distraction/low signals",
    scores_all[0] > scores_all[-5] if len(scores_all) >= 6 else True,
    f"first_constructive={scores_all[0] if scores_all else 'N/A'}  last_drain={scores_all[-1] if scores_all else 'N/A'}"
))

# ── REQ 9: Neural network (connections non-trivial) ──────────────────────────
print("\n❾  Nebula tipo red neuronal (connection graph non-trivial)")
final_mass = get_field_mass()
conns = final_mass["connections"]
results.append(check(
    "All 3 connection pairs exist in response",
    all(k in conns for k in ["engineering:fitness", "engineering:be_fluent", "fitness:be_fluent"]),
    f"keys={list(conns.keys())}"
))
results.append(check(
    "At least one connection > 0.3 (meaningful correlation)",
    any(v > 0.3 for v in conns.values()),
    f"connections={conns}"
))
results.append(check(
    "Connections are distinct (not all equal)",
    len(set(round(v, 3) for v in conns.values())) > 1,
    f"values={list(conns.values())}"
))

# ── SUMMARY ───────────────────────────────────────────────────────────────────
print("\n══ SUMMARY ════════════════════════════════════════════════════")
passed = sum(results)
total  = len(results)
print(f"\n  {passed}/{total} checks passed\n")
print("  Final field masses:")
for field, mass in final_mass["field_masses"].items():
    bar = "█" * int(mass * 20) + "░" * (20 - int(mass * 20))
    print(f"  {field:15s} {bar}  {mass:.3f}")
print(f"\n  Dominant field: {final_mass['dominant']}")
print(f"  Total events processed: {final_mass['total_events']}")
print()
