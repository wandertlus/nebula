import json
import sys
import time
from nebula_processor import ProjectNebulaProcessor
from config import CONFIG

def run_simulation():
    processor = ProjectNebulaProcessor(CONFIG)
    
    # Simulate a sequence of signals to observe Identity Drift
    test_signals = [
        # --- Stage 1: Engineering Consolidation ---
        {"content": "Designing a scalable microservices architecture for the nebula cloud", "signal_type": "Work", "priority": "high", "duration": 60, "result_value": 8.0, "effort_signals": {"custom": {"focus": "deep"}}},
        {"content": "Implementing asynchronous message processing logic", "signal_type": "Work", "priority": "medium", "duration": 45, "result_value": 5.0},
        {"content": "Writing unit tests for the core physics engine", "signal_type": "Work", "priority": "low", "duration": 30, "result_value": 2.0},
        
        # --- Stage 2: Sudden Shift (Fitness) ---
        # With high inertia, these signals should only slowly pull the global identity
        {"content": "Deadlifting heavy at the gym and pushing personal limits", "signal_type": "Health", "priority": "high", "duration": 50, "result_value": 9.0},
        {"content": "Sprinting and anaerobic interval training session", "signal_type": "Health", "priority": "medium", "duration": 40, "result_value": 7.0},
        
        # --- Stage 3: Culinary Exploration ---
        {"content": "Baking professional-grade sourdough with hydrated dough", "signal_type": "Work", "priority": "medium", "duration": 120, "result_value": 15.0}
    ]

    print(f"🚀 Starting Drift Simulation ({len(test_signals)} signals)...")
    print(f"Engine: {processor.backend} | Inertia: {processor.inertia}")

    for i, signal in enumerate(test_signals):
        payload = {"body": signal}
        result_json = processor.project_signal_state(json.dumps(payload))
        result = json.loads(result_json)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Signal {i+1}: {result['dominant_attractor']} -> GLOBAL: {result['global_dominant_identity']} (Drift: {result['drift_delta']:.4f})")
            time.sleep(0.1)

    print("\n✨ Simulation complete. Check the 'Identity Drift' section in your Dashboard.")

if __name__ == "__main__":
    run_simulation()