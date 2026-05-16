"""
main.py
═══════
Entry point for Project Nebula.

Usage:
    # Process a single signal interactively
    python main.py

    # Process a JSON signal from the command line
    python main.py '{"action_text": "Studied English for 20 minutes", "category": "Education", "priority": "high", "duration": 20}'

    # Process with a result for efficiency tracking
    python main.py '{"action_text": "Read technical paper on distributed systems", "category": "Education", "priority": "high", "duration": 30, "effort_signals": {"result_type": "numeric", "result_value": 1, "result_unit": "papers", "result_text": "Finished CAP theorem deep dive"}}'
"""

import sys
import json
from nebula_processor import ProjectNebulaProcessor


def main():
    processor = ProjectNebulaProcessor()

    if len(sys.argv) > 1:
        raw = sys.argv[1]
    else:
        # Interactive mode
        print("\n── Nebula Engine ─────────────────────────────")
        print("Paste a JSON signal or press Enter for default test:\n")
        raw = input("> ").strip()

        if not raw:
            raw = json.dumps({
                "action_text": "Built scalable microservices architecture",
                "category":    "Work",
                "priority":    "high",
                "duration":    60,
            })

    output = processor.project_signal_state(raw)
    print(f"\n{output}\n")


if __name__ == "__main__":
    main()