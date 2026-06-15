"""
Seed de validación — señales reales para probar que Nebula procesa correctamente.

Uso:
    python seed_real_data.py              # envía todas las señales
    python seed_real_data.py --dry-run    # muestra sin enviar
    python seed_real_data.py --identity be_fluent   # solo una identidad
"""

import argparse
import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from typing import Optional

BASE_URL = "http://localhost:8000/api/signal"

@dataclass
class Signal:
    action_text: str
    category: str
    duration: int
    priority: str = "high"
    result_type: Optional[str] = None
    result_value: Optional[float] = None
    result_unit: Optional[str] = None
    result_text: Optional[str] = None
    tag: str = ""   # solo para agrupar en este script, no se envía

    def payload(self):
        d = {
            "action_text": self.action_text,
            "category": self.category,
            "duration": self.duration,
            "priority": self.priority,
        }
        if self.result_type:
            d["result_type"] = self.result_type
            d["result_value"] = self.result_value
            d["result_unit"] = self.result_unit
            d["result_text"] = self.result_text
        return d


SIGNALS: list[Signal] = [

    # ── BE FLUENT — Escuchar ────────────────────────────────────────────────
    Signal(
        action_text="Listened to Real Exam English podcast: IELTS speaking part 2 band 9 sample",
        category="Education", duration=35, tag="be_fluent",
    ),
    Signal(
        action_text="Listened to 6 Minute English BBC: The psychology of decision making",
        category="Education", duration=20, tag="be_fluent",
    ),
    Signal(
        action_text="Watched English video: TED Talk by Simon Sinek — How great leaders inspire action",
        category="Education", duration=18, tag="be_fluent",
    ),
    Signal(
        action_text="Listened to All Ears English podcast: How to sound natural using collocations",
        category="Education", duration=25, tag="be_fluent",
    ),

    # ── BE FLUENT — Escribir ────────────────────────────────────────────────
    Signal(
        action_text="Wrote technical documentation in English for Nebula API endpoints",
        category="Education", duration=30, tag="be_fluent",
    ),
    Signal(
        action_text="Wrote English notes and reflections on leadership and decision making",
        category="Education", duration=20, tag="be_fluent",
    ),
    Signal(
        action_text="Wrote professional email in English to university admission office asking about requirements",
        category="Education", duration=25, tag="be_fluent",
    ),

    # ── BE FLUENT — Hablar ──────────────────────────────────────────────────
    Signal(
        action_text="English shadowing and pronunciation practice with Real Exam English band 9 samples",
        category="Education", duration=20, tag="be_fluent",
    ),
    Signal(
        action_text="Practiced English conversation on topic: describing past experiences and future goals",
        category="Education", duration=30, tag="be_fluent",
    ),

    # ── ENGINEERING — Construir ─────────────────────────────────────────────
    Signal(
        action_text="Built Nebula real-time signal seed script with CLI args and dry-run support",
        category="Work", duration=60, tag="engineering",
    ),
    Signal(
        action_text="Refactored Nebula coherence engine to support multi-week scoring window",
        category="Work", duration=75, tag="engineering",
    ),
    Signal(
        action_text="Fixed alignment score returning 0.0 for short descriptive action texts in MiniLM backend",
        category="Work", duration=45, tag="engineering",
    ),
    Signal(
        action_text="Built FastAPI dependency injection system for authentication middleware",
        category="Work", duration=90, tag="engineering",
    ),
    Signal(
        action_text="Worked on Nebula frontend: wired CoherencePanel to live /api/coherence endpoint",
        category="Work", duration=60, tag="engineering",
    ),

    # ── ENGINEERING — Estudiar ──────────────────────────────────────────────
    Signal(
        action_text="Read FastAPI official documentation on background tasks and lifespan events",
        category="Education", duration=30, tag="engineering",
    ),
    Signal(
        action_text="Read technical paper on sentence-transformers: all-MiniLM-L6-v2 architecture and benchmarks",
        category="Education", duration=40, tag="engineering",
        result_type="numeric", result_value=1, result_unit="papers",
        result_text="Understood why MiniLM outperforms TF-IDF on short semantic similarity tasks",
    ),
    Signal(
        action_text="Watched tutorial on React Zustand state management for large-scale dashboards",
        category="Education", duration=45, tag="engineering",
    ),
    Signal(
        action_text="Read documentation on SQLite WAL mode for concurrent reads without blocking writes",
        category="Education", duration=25, tag="engineering",
    ),

    # ── FITNESS — Fuerza ────────────────────────────────────────────────────
    Signal(
        action_text="Strength training session: chest and triceps — bench press, incline dumbbell, cable triceps",
        category="Health", duration=75, tag="fitness",
    ),
    Signal(
        action_text="Strength training: deadlift — worked up to 120 kg for 3 sets of 5",
        category="Health", duration=80, tag="fitness",
        result_type="numeric", result_value=120, result_unit="kg",
        result_text="New training max, form held on all reps",
    ),
    Signal(
        action_text="Strength training session: back and biceps — pull-ups, barbell rows, hammer curls",
        category="Health", duration=70, tag="fitness",
    ),
    Signal(
        action_text="Mobility and warm-up session before gym: hip flexors, thoracic spine, shoulder rotations",
        category="Health", duration=20, tag="fitness",
    ),

    # ── DISTRACCIÓN — registrar para calibrar el modelo ────────────────────
    Signal(
        action_text="Scrolled social media: Instagram reels and Twitter feed",
        category="Distraction", duration=25, tag="distraction",
    ),
    Signal(
        action_text="Watched YouTube shorts and news without intention",
        category="Distraction", duration=20, tag="distraction",
    ),
]


def send_signal(signal: Signal, verbose: bool = True) -> dict:
    payload = signal.payload()
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
    if verbose:
        score = result.get("final_score", None)
        state = result.get("state", "?")
        align = result.get("semantic_alignment", result.get("alignment_score", None))
        dominant = result.get("dominant_attractor", "?")
        score_s = f"{score:.3f}" if isinstance(score, (int, float)) else "?"
        align_s = f"{align:.3f}" if isinstance(align, (int, float)) else "?"
        print(f"  score={score_s}  align={align_s}  state={state}  dominant={dominant}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Seed real signals into Nebula")
    parser.add_argument("--dry-run", action="store_true", help="Print without sending")
    parser.add_argument("--identity", choices=["engineering", "be_fluent", "fitness", "distraction"],
                        help="Filter by identity tag")
    parser.add_argument("--delay", type=float, default=0.3, help="Seconds between requests (default 0.3)")
    args = parser.parse_args()

    signals = [s for s in SIGNALS if not args.identity or s.tag == args.identity]

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Sending {len(signals)} signals to {BASE_URL}\n")

    ok = 0
    errors = 0

    for i, sig in enumerate(signals, 1):
        tag_label = f"[{sig.tag.upper()}]"
        print(f"{i:02d}. {tag_label:<15} {sig.action_text[:70]}")

        if args.dry_run:
            print(f"      payload: {json.dumps(sig.payload())}")
            continue

        try:
            send_signal(sig)
            ok += 1
        except urllib.error.URLError as e:
            print(f"  ERROR: {e.reason}")
            errors += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1

        if i < len(signals):
            time.sleep(args.delay)

    if not args.dry_run:
        print(f"\nDone — {ok} ok / {errors} errors")


if __name__ == "__main__":
    main()
