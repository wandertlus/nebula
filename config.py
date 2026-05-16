from pathlib import Path

# Base directory relative to this file
BASE_DIR = Path(__file__).resolve().parent

CONFIG = {
    "identity_fields": {
        "engineering": "Building systems, solving technical problems, and improving engineering capability through consistent learning and execution. Focus on architecture, software design, and scalable infrastructure.",
        "fitness": "Cultivating elite physical performance through disciplined training, progressive overload, and physiological optimization. Focus on strength, metabolic health, and athletic longevity.",
        "Be_fluent": "learn one word every day, listen to an 1 hour of advanced English,write a letter."
    }, #on the future it will be necesay apply new key work for the context.

    "impact_tones": {
        "Work": 2.0,
        "space_news": 1.0,
        "Education": 1.8,
        "Health": 1.2,
        "Rest": 0.5,
        "Distraction": -1.5,
        "Void": -2.5
    },

    "thresholds": {
        "friction": 0.5,
        "black_hole": -0.5
    },

    # Storage Settings
    "event_log_path": BASE_DIR / "events.jsonl",
    "identity_state_path": BASE_DIR / "identity_state.json",
    
    # Engine Settings
    "semantic_backend": "minilm", # Options: "tfidf", "minilm"
    
    # Physics Parameters (Sprint 4)
    "inertia": 0.9, # Resistance to identity change (0.0 to 1.0)
    "beta_duration": 0.7, # rendimientos decrecientes
    "gamma_effort": 1.3, # rendimientos crecientes hasta límite
    "base_duration": 30.0, # minutos de referencia para normalización
    "efficiency_alpha": 0.1, # EMA de eficiencia histórica por categoría
    "effort_by_category": {
        "Work":       0.8,
        "Education":  0.9,
        "Health":     0.7,
        "Rest":       0.2,
        "Distraction":0.1,
        "space_news": 0.4,
        "Void":       0.0,
    }
}