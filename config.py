# Project Nebula Configuration - Live Reload Triggered
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CONFIG = {
    # ── NORTH STARS ──────────────────────────────────────────────────────────
    # These are the gravitational attractors. Each string is the semantic
    # description used to compute cosine similarity against incoming signals.
    "identity_fields": {
        "engineering": (
            "Building systems, solving technical problems, and improving "
            "engineering capability through consistent learning and execution. "
            "Focus on architecture, software design, code, programming, development, "
            "and scalable infrastructure."
        ),
        "fitness": (
            "Cultivating elite physical performance through disciplined training, "
            "progressive overload, workout, exercise, and physiological optimization. "
            "Focus on strength, metabolic health, and athletic longevity."
        ),
        "be_fluent": (
            "Achieving native-level English fluency through daily immersion. "
            "Learning one word every day, listening to one hour of advanced "
            "English, writing letters, talking, and technical documents."
        ),
    },

    # ── IDENTITY COLORS ──────────────────────────────────────────────────────
    # Colores específicos para cada campo de identidad (usados en nodos y cards).
    "identity_colors": {
        "engineering": "#00D1FF",  # Azul Tecnológico
        "fitness":     "#FF3D00",  # Naranja/Rojo Energía
        "be_fluent":   "#4CAF50",  # Verde Crecimiento
    },

    # ── CATEGORY WEIGHTS (impact_tones) ──────────────────────────────────────
    # Multiplier applied to alignment score based on the signal's category.
    # Positive = constructive force. Negative = entropic force.
    "impact_tones": {
        "Work":        2.0,
        "Education":   1.8,
        "Health":      1.2,
        "space_news":  1.0,
        "Rest":        0.5,
        "Distraction": -2.0,
        "Void":        -4.0,
    },

    # ── EFFORT INFERENCE ─────────────────────────────────────────────────────
    # Base cognitive effort per category (0.0 to 1.0).
    # This is inferred deterministically to preserve auditability.
    # Future: override via effort_signals.custom in the event payload.
    "effort_by_category": {
        "Work":        0.8,
        "Education":   0.9,
        "Health":      0.7,
        "space_news":  0.4,
        "Rest":        0.2,
        "Distraction": 0.3,   # Increased from 0.1 to give distractions more "mass" in the formula
        "Void":        0.1,
    },

    # ── PHYSICS PARAMETERS ───────────────────────────────────────────────────
    # beta_duration: exponent on normalized duration.
    #   < 1.0 = diminishing returns (4h study ≠ 4x value of 1h study)
    "beta_duration": 0.7,

    # gamma_effort: exponent on effort.
    #   > 1.0 = increasing returns (high cognitive intensity amplifies impact)
    "gamma_effort": 1.3,

    # duration_baseline: reference duration in minutes for normalization.
    #   A 30-min event gives duration_norm = 1.0
    #   A 60-min event gives duration_norm = 2.0 → 2.0^0.7 ≈ 1.62
    #   A 15-min event gives duration_norm = 0.5 → 0.5^0.7 ≈ 0.62
    "duration_baseline": 30,

    # ── STATE THRESHOLDS ─────────────────────────────────────────────────────
    # These are relative to the new normalized impact score.
    # Friction:          final_score > friction_threshold
    # Degenerate Matter: black_hole_threshold <= final_score <= friction_threshold
    # Black Hole:        final_score < black_hole_threshold
    #
    # Calibration notes:
    #   Impact = Alignment × Weight × DurationNorm^0.7 × Effort^1.3
    #   Typical alignment scores from cosine similarity: 0.1 – 0.4
    #   A Work/High/45min signal realistically yields: 0.10 – 0.30
    #   Friction threshold must be reachable for constructive work signals.
    "thresholds": {
        "friction":    0.08,   # Slightly lowered to make Friction more common
        "black_hole": -0.01,  # Significantly raised to catch almost any negative score
    },

    # ── IDENTITY DRIFT ENGINE ────────────────────────────────────────────────
    # inertia (alpha): resistance to sudden identity change.
    #   I(t+1) = alpha * I(t) + (1 - alpha) * A(t)
    #   0.9 = identity is heavy, changes slowly
    "inertia": 0.9,

    # efficiency_alpha: EMA smoothing factor for historical efficiency per category.
    #   Low value = slow adaptation (memory of past performance)
    #   High value = fast adaptation (recent performance dominates)
    "efficiency_alpha": 0.1,

    # ── CANONICAL RESOURCE MODEL ─────────────────────────────────────────────
    # Resources are transferable capacities. They are not identities.
    "resources": [
        "time",
        "energy",
        "attention",
        "money",
        "knowledge",
        "relationships",
    ],

    # Trajectories are recurring resource-transformation patterns.
    # Existing identity fields remain as the current emergent-layer bridge.
    "trajectories": [
        "entrepreneurship",
        "engineering",
        "language_fluency",
        "employment",
        "health",
    ],

    # ── ENGINE SETTINGS ──────────────────────────────────────────────────────
    # Options: "tfidf" (fast, lexical) | "minilm" (semantic, recommended)
    "semantic_backend": "minilm",

    # ── STORAGE ──────────────────────────────────────────────────────────────
    "event_log_path":     BASE_DIR / "events.jsonl",
    "identity_state_path": BASE_DIR / "identity_state.json",
}
