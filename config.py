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
            "Focus on architecture, software design, and scalable infrastructure."
        ),
        "fitness": (
            "Cultivating elite physical performance through disciplined training, "
            "progressive overload, and physiological optimization. Focus on "
            "strength, metabolic health, and athletic longevity."
        ),
        "be_fluent": (
            "Achieving native-level English fluency through daily immersion. "
            "Learning one word every day, listening to one hour of advanced "
            "English, writing letters and technical documents."
        ),
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
        "Distraction": -1.5,
        "Void":        -2.5,
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
        "Distraction": 0.1,
        "Void":        0.0,
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
    "thresholds": {
        "friction":    0.4,
        "black_hole": -0.3,
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

    # ── ENGINE SETTINGS ──────────────────────────────────────────────────────
    # Options: "tfidf" (fast, lexical) | "minilm" (semantic, recommended)
    "semantic_backend": "minilm",

    # ── STORAGE ──────────────────────────────────────────────────────────────
    "event_log_path":     BASE_DIR / "events.jsonl",
    "identity_state_path": BASE_DIR / "identity_state.json",
}