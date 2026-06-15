"""
nebula_processor.py
═══════════════════
Physics engine for Project Nebula.

Core formula:
    Impact(t) = Alignment × Weight × DurationNorm^β × Effort^γ

    where:
        Alignment    = cosine similarity between action and dominant North Star
        Weight       = category impact tone (constructive or entropic)
        DurationNorm = duration_minutes / duration_baseline  (30 min = 1.0)
        β (beta)     = 0.7  → diminishing returns on time
        γ (gamma)    = 1.3  → increasing returns on cognitive effort

Identity drift (EMA):
    I(t+1) = α · I(t) + (1 - α) · A(t)
    α = inertia (0.9) — identity is heavy, resists sudden change

Efficiency (retrospective, per category):
    Efficiency(t) = result_value / duration_minutes   (when result exists)
    EMA tracked in identity_state.json per category
    efficiency_ratio = Efficiency(t) / historical_EMA  (> 1 = above baseline)
"""

import json
import uuid
import numpy as np
import nltk

from datetime import datetime
from enum import Enum
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, TypedDict

from coherence_engine import compute_coherence
from config import CONFIG
from physics_domain import (
    IdentityDrift,
    SignalDrift,
    infer_resource_transformation,
    resolve_trajectory,
)
from storage import load_events, load_identity_state, save_identity_state, save_event
from venture_system import apply_venture_signal


class EventType(Enum):
    STRUCTURED = "structured"
    CASUAL = "casual"
    DEGENERATE = "degenerate"


class PhysicsProfile(TypedDict):
    mass_gain: float
    momentum_gain: float
    decay_resistance: float
    visual_weight: float


EVENT_PHYSICS: Dict[EventType, PhysicsProfile] = {
    EventType.STRUCTURED: {
        "mass_gain": 0.8,
        "momentum_gain": 0.2,
        "decay_resistance": 0.9,
        "visual_weight": 1.0,
    },
    EventType.CASUAL: {
        "mass_gain": 0.05,
        "momentum_gain": 0.9,
        "decay_resistance": 0.2,
        "visual_weight": 0.3,
    },
    EventType.DEGENERATE: {
        "mass_gain": -0.4,
        "momentum_gain": -0.8,
        "decay_resistance": 0.5,
        "visual_weight": 0.8,
    },
}

# ── NLTK bootstrap ───────────────────────────────────────────────────────────
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt")
    nltk.download("punkt_tab")


class ProjectNebulaProcessor:

    def __init__(self, config=CONFIG):
        self.config = config

        # North Stars
        self.identity_fields = config["identity_fields"]
        self.identities = list(self.identity_fields.keys())
        identity_texts = [self.identity_fields[i] for i in self.identities]

        # Physics constants
        self.beta     = config.get("beta_duration",   0.7)
        self.gamma    = config.get("gamma_effort",    1.3)
        self.baseline = config.get("duration_baseline", 30)
        self.inertia  = config.get("inertia",         0.9)
        self.eff_alpha = config.get("efficiency_alpha", 0.1)

        self.backend = config.get("semantic_backend", "tfidf")

        # ── TF-IDF (baseline, always available) ──────────────────────────────
        self.vectorizer = TfidfVectorizer()
        self.target_vectors_tfidf = self.vectorizer.fit_transform(identity_texts)

        # ── MiniLM (semantic, preferred) ─────────────────────────────────────
        self.minilm_available = False
        try:
            from sentence_transformers import SentenceTransformer  # pyrefly: ignore
            self.model_minilm = SentenceTransformer("all-MiniLM-L6-v2")
            self.target_vectors_minilm = self.model_minilm.encode(identity_texts)
            self.minilm_available = True
        except (ImportError, OSError, Exception):
            pass

        # ── Identity state ────────────────────────────────────────────────────
        dim = 384 if (self.backend == "minilm" and self.minilm_available) else len(self.vectorizer.get_feature_names_out())
        self.current_identity, self.efficiency_by_cat = load_identity_state(dim, config)

    # ── TEXT PREPROCESSING ───────────────────────────────────────────────────

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        tokens = word_tokenize(text.lower())
        return " ".join(t for t in tokens if t.isalnum())

    # ── ALIGNMENT CALCULATION ─────────────────────────────────────────────────

    def calculate_alignment(self, action_text: str) -> dict:
        """
        Returns cosine similarity against every North Star for both backends.
        {
            "tfidf":  {"engineering": 0.24, "fitness": 0.0, "be_fluent": 0.0},
            "minilm": {"engineering": 0.40, "fitness": 0.02, "be_fluent": 0.11},
        }
        """
        results = {}

        if not action_text:
            zero = {i: 0.0 for i in self.identities}
            return {"tfidf": zero, "minilm": zero}

        # TF-IDF
        v_tfidf = self.vectorizer.transform([action_text])
        sims_tfidf = cosine_similarity(v_tfidf, self.target_vectors_tfidf)[0]
        results["tfidf"] = {self.identities[i]: float(sims_tfidf[i])
                            for i in range(len(self.identities))}

        # MiniLM
        if self.minilm_available:
            v_minilm = self.model_minilm.encode([action_text])
            sims_minilm = cosine_similarity(v_minilm, self.target_vectors_minilm)[0]
            results["minilm"] = {self.identities[i]: float(sims_minilm[i])
                                 for i in range(len(self.identities))}

        return results

    def calculate_alignment_for_vector(self, vector: np.ndarray) -> dict:
        """Similarity between the accumulated identity vector and all North Stars."""
        target = (self.target_vectors_minilm
                  if (self.backend == "minilm" and self.minilm_available)
                  else self.target_vectors_tfidf.toarray())
        v = vector.reshape(1, -1)
        sims = cosine_similarity(v, target)[0]
        return {self.identities[i]: float(sims[i]) for i in range(len(self.identities))}

    # ── EFFORT INFERENCE ──────────────────────────────────────────────────────

    def infer_effort(self, category: str, priority: str) -> float:
        """
        Deterministic effort inference from category + priority.
        Preserves auditability (Engineering Principle: Interpretability First).
        Future override point: effort_signals.custom in payload.
        """
        base = self.config.get("effort_by_category", {}).get(category, 0.5)
        if priority == "high":
            base = min(1.0, base * 1.15)
        elif priority == "low":
            base = base * 0.85
        return round(base, 4)

    # ── PHYSICS FORMULA ───────────────────────────────────────────────────────

    def compute_impact(
        self,
        alignment: float,
        weight: float,
        duration_minutes: int,
        effort: float,
    ) -> float:
        """
        Impact(t) = Alignment × Weight × DurationNorm^β × Effort^γ

        DurationNorm = duration / baseline (30 min = 1.0)
        β = 0.7  → diminishing returns on time
        γ = 1.3  → amplified returns on cognitive intensity
        """
        # Ensure negative weights always produce a negative impact
        # even if semantic alignment is 0.0
        effective_alignment = alignment
        if weight < 0:
            effective_alignment = max(alignment, 0.15)

        duration_norm = max(duration_minutes, 1) / self.baseline
        duration_factor = duration_norm ** self.beta
        effort_factor   = effort ** self.gamma
        return effective_alignment * weight * duration_factor * effort_factor

    # ── STATE CLASSIFICATION ──────────────────────────────────────────────────

    def determine_state(self, final_score: float) -> dict:
        t = self.config.get("thresholds", {"friction": 0.4, "black_hole": -0.3})
        if final_score > t["friction"]:
            return {"state": "Friction"}
        elif final_score >= t["black_hole"]:
            return {"state": "Degenerate Matter"}
        else:
            return {"state": "Black Hole"}

    def resolve_event_type(self, payload: dict, weight: float, duration: int, result_value) -> EventType:
        raw_type = (
            payload.get("behavioral_type")
            or payload.get("event_type")
            or payload.get("type")
        )
        if raw_type:
            normalized = str(raw_type).lower().strip()
            for event_type in EventType:
                if normalized == event_type.value:
                    return event_type

        if weight < 0:
            return EventType.DEGENERATE

        category = str(payload.get("category", "")).lower()
        priority = str(payload.get("priority", "medium")).lower()
        has_result = result_value is not None and float(result_value) > 0
        is_deep_session = duration >= self.baseline * 1.5

        if has_result or is_deep_session or priority == "high":
            return EventType.STRUCTURED
        if category in {"rest", "space_news"} or duration < self.baseline:
            return EventType.CASUAL
        return EventType.STRUCTURED

    def build_physics_payload(self, alignment_score: float, event_type: EventType) -> dict:
        profile = EVENT_PHYSICS[event_type]
        mass_impact = alignment_score * profile["mass_gain"]
        return {
            "mass_impact": round(mass_impact, 6),
            "momentum_burst": round(profile["momentum_gain"], 6),
            "decay_resistance": round(profile["decay_resistance"], 6),
            "visual_scale": round(profile["visual_weight"], 6),
        }

    # ── EFFICIENCY TRACKING ───────────────────────────────────────────────────

    def compute_efficiency(
        self,
        category: str,
        result_value,
        duration_minutes: int,
    ) -> tuple:
        """
        Computes instantaneous efficiency and compares against historical EMA.

        efficiency        = result_value / duration_minutes
        historical_ema    = EMA of past efficiency for this category
        efficiency_ratio  = efficiency / historical_ema  (None if no history)

        Returns (efficiency, efficiency_ratio, updated_ema)
        """
        if result_value is None or duration_minutes <= 0:
            return None, None, self.efficiency_by_cat.get(category)

        efficiency = float(result_value) / float(duration_minutes)
        historical = self.efficiency_by_cat.get(category)

        if historical is None or historical == 0.0:
            # First data point — bootstrap EMA
            new_ema = efficiency
            ratio = None
        else:
            ratio = round(efficiency / historical, 4)
            new_ema = (self.eff_alpha * efficiency) + ((1 - self.eff_alpha) * historical)

        return round(efficiency, 6), ratio, round(new_ema, 6)

    # ── MAIN SIGNAL PROCESSOR ────────────────────────────────────────────────

    def project_signal_state(self, input_data) -> str:
        """
        Processes an incoming signal through the full physics engine.

        Input schema:
            action_text   : str   — description of what was done
            category      : str   — Work | Education | Health | Rest | Distraction | ...
            priority      : str   — low | medium | high
            duration      : int   — minutes spent
            effort_signals: dict  — optional {result_type, result_value, result_unit,
                                               result_text, custom}

        Returns: JSON string with full event including physics_params.
        """
        try:
            data = json.loads(input_data) if isinstance(input_data, str) else input_data
            payload = data.get("body", data)

            # ── 1. EXTRACT PAYLOAD FIELDS ─────────────────────────────────────
            action_text = payload.get("content") or payload.get("action_text", "")
            category    = payload.get("signal_type") or payload.get("category", "Void")
            priority    = payload.get("priority", "medium")
            duration    = int(payload.get("duration", 0))

            # Effort signals (optional, extensible)
            raw_effort_signals = payload.get("effort_signals", {})
            result_type  = raw_effort_signals.get("result_type")   # "numeric" | "text" | None
            result_value = raw_effort_signals.get("result_value") or payload.get("result_value")
            result_unit  = raw_effort_signals.get("result_unit")   # "pages" | "reps" | etc
            result_text  = raw_effort_signals.get("result_text")   # free text description
            custom       = raw_effort_signals.get("custom", {})    # future extensibility port

            # ── 2. RESOLVE WEIGHT & EFFORT (before any calculations) ──────────
            # FIX: weight must be resolved here, before dynamic_pull uses it
            weight = self.config["impact_tones"].get(category, 0.0)
            if priority == "high":
                weight *= 1.2
            elif priority == "low":
                weight *= 0.9

            effort = self.infer_effort(category, priority)

            # ── 3. SEMANTIC ALIGNMENT ─────────────────────────────────────────
            cleaned_text   = self.clean_text(action_text)
            multi_align    = self.calculate_alignment(cleaned_text)
            alignments     = multi_align.get(self.backend, multi_align["tfidf"])

            # All 3 scores are visible — dominant takes priority but others are tracked
            dominant_attractor  = max(alignments, key=alignments.get)
            alignment_score     = alignments[dominant_attractor]

            event_type = self.resolve_event_type(payload, weight, duration, result_value)
            physics_payload = self.build_physics_payload(alignment_score, event_type)

            # ── 4. PHYSICS: IMPACT SCORE ──────────────────────────────────────
            final_score = self.compute_impact(alignment_score, weight, duration, effort)

            # Aggregated info (result_value) amplification: Ensure results create significant mass
            if result_value is not None and float(result_value) > 0:
                # Logarithmic boost: 1 -> +13%, 10 -> +47%, 100 -> +92%
                final_score *= (1.0 + np.log1p(result_value) * 0.2)

            # ── 5. STATE CLASSIFICATION ───────────────────────────────────────
            state_result = self.determine_state(final_score)

            # ── 6. EFFICIENCY ─────────────────────────────────────────────────
            efficiency, efficiency_ratio, new_ema = self.compute_efficiency(
                category, result_value, duration
            )
            if new_ema is not None:
                self.efficiency_by_cat[category] = new_ema

            # ── 7. IDENTITY DRIFT ENGINE ──────────────────────────────────────
            identity_before = np.array(self.current_identity).copy()

            # Get signal vector in the active backend's space
            if self.backend == "minilm" and self.minilm_available:
                signal_vector = self.model_minilm.encode([cleaned_text])[0]
            else:
                signal_vector = self.vectorizer.transform([cleaned_text]).toarray()[0]

            # Dynamic pull: scales with weight and duration, capped at 0.5
            # Baseline: 30 min medium-priority task pulls by (1 - inertia)
            base_duration  = self.baseline
            duration_factor = max(0.1, duration / base_duration)
            dynamic_pull   = min(0.5, (1 - self.inertia) * abs(weight) * duration_factor)

            # I(t+1) = α · I(t) + (1 - α) · A(t)
            self.current_identity = (
                identity_before * (1 - dynamic_pull)
                + signal_vector  * dynamic_pull
            )
            self.current_identity = self.current_identity.tolist()

            # Drift delta: Euclidean distance moved in identity space
            drift_delta = float(np.linalg.norm(
                np.array(self.current_identity) - identity_before
            ))

            # Global dominance: who are you becoming?
            global_dominance = self.calculate_alignment_for_vector(
                np.array(self.current_identity)
            )
            global_dominant_identity = max(global_dominance, key=global_dominance.get)

            dominant_trajectory = resolve_trajectory(
                category,
                dominant_attractor,
                action_text,
            )
            signal_drift = SignalDrift(
                magnitude=round(drift_delta, 8),
                dynamic_pull=round(dynamic_pull, 6),
                dominant_trajectory=dominant_trajectory,
                dominant_attractor=dominant_attractor,
                vector_space=self.backend,
            )
            identity_drift = IdentityDrift(
                global_dominant_identity=global_dominant_identity,
                global_dominance={k: round(v, 6) for k, v in global_dominance.items()},
                accumulated_vector_dimension=len(self.current_identity),
            )

            # ── 8. PERSIST STATE ──────────────────────────────────────────────
            save_identity_state(
                self.current_identity,
                self.efficiency_by_cat,
                self.config,
            )

            # ── 8b. COHERENCE (over full event history) ───────────────────────
            recent_events  = load_events(self.config)
            coherence_result = compute_coherence(
                events=recent_events,
                thermo_state={},   # no thermo access here; /api/coherence uses live state
            )

            # ── 9. BUILD EVENT ────────────────────────────────────────────────
            event_id = str(uuid.uuid4())
            inferred_transformation = infer_resource_transformation(
                event_id=event_id,
                action_text=action_text,
                category=category,
                duration=duration,
                dominant_trajectory=dominant_trajectory,
                effort=effort,
                result_value=result_value,
            )
            resource_transformation = payload.get("resource_transformation") or inferred_transformation.to_dict()
            venture_update = apply_venture_signal(
                payload=payload,
                alignments=alignments,
                weight=weight,
            )
            event = {
                "event_id":                event_id,
                "timestamp":               datetime.utcnow().isoformat(),
                "action_text":             action_text,
                "category":                category,
                "duration":                duration,
                "priority":                priority,
                "alignment_score":         round(alignment_score, 6),
                "weight":                  round(weight, 4),
                "final_score":             round(final_score, 6),
                "state":                   state_result["state"],
                "dominant_attractor":      dominant_attractor,
                "global_dominant_identity": global_dominant_identity,
                "event_name":              action_text,
                "semantic_alignment":      round(alignment_score, 6),
                "behavioral_type":         event_type.value,
                "physics":                 physics_payload,
                "resource_transformation": resource_transformation,
                "trajectory": {
                    "key": dominant_trajectory,
                    "source": "rule_based_bridge",
                    "linked_identity_field": dominant_attractor,
                },
                "drift": {
                    "signal": signal_drift.to_dict(),
                    "identity": identity_drift.to_dict(),
                },
                "coherence": coherence_result,
                "venture": venture_update,

                # Effort signals — extensible schema
                "effort_signals": {
                    "effort":            effort,
                    "result_type":       result_type,
                    "result_value":      result_value,
                    "result_unit":       result_unit,
                    "result_text":       result_text,
                    "efficiency":        efficiency,
                    "efficiency_ratio":  efficiency_ratio,
                    "historical_ema":    self.efficiency_by_cat.get(category),
                    "custom":            custom,
                },

                # Full physics audit trail
                "physics_params": {
                    "alignment":        round(alignment_score, 6),
                    "fundamental_impact": physics_payload["mass_impact"],
                    "behavioral_type":   event_type.value,
                    "event_physics_profile": EVENT_PHYSICS[event_type],
                    "impact_weight":    round(weight, 4),
                    "effort":           effort,
                    "beta_duration":    self.beta,
                    "gamma_effort":     self.gamma,
                    "duration_norm":    round(max(duration, 1) / self.baseline, 4),
                    "all_alignments":   {k: round(v, 6) for k, v in alignments.items()},
                    "multi_backend_comparison": {
                        b: {k: round(v, 6) for k, v in scores.items()}
                        for b, scores in multi_align.items()
                    },
                    "active_backend":   self.backend,
                    "identity_snapshot": {
                        "drift_delta":              round(drift_delta, 8),
                        "drift_scope":              "identity",
                        "dynamic_pull":             round(dynamic_pull, 6),
                        "inertia":                  self.inertia,
                        "duration_factor":          round(duration_factor, 4),
                        "global_dominance":         {k: round(v, 6) for k, v in global_dominance.items()},
                        "global_dominant_identity": global_dominant_identity,
                    },
                },
            }

            save_event(event, self.config)

            # Identity-based color (match with cards)
            id_colors = self.config.get("identity_colors", {})
            display_color = id_colors.get(dominant_attractor, "#888888")

            # ── 10. RETURN SUMMARY ────────────────────────────────────────────
            return json.dumps({
                "event_id":                event_id,
                "event_name":              action_text,
                "category":                dominant_attractor,
                "semantic_alignment":      round(alignment_score, 6),
                "behavioral_type":         event_type.value,
                "physics":                 physics_payload,
                "resource_transformation": resource_transformation,
                "trajectory":              dominant_trajectory,
                "drift": {
                    "signal": signal_drift.to_dict(),
                    "identity": identity_drift.to_dict(),
                },
                "coherence":               coherence_result,
                "venture":                 venture_update,
                "state":                   state_result["state"],
                "color":                   display_color,
                "dominant_attractor":      dominant_attractor,
                "global_dominant_identity": global_dominant_identity,
                "all_alignments":          {k: round(v, 6) for k, v in alignments.items()},
                "final_score":             round(final_score, 6),
                "effort":                  effort,
                "efficiency":              efficiency,
                "efficiency_ratio":        efficiency_ratio,
                "drift_delta":             round(drift_delta, 8),
                "active_backend":          self.backend,
            }, indent=2)

        except Exception as e:
            return json.dumps({"error": str(e), "type": type(e).__name__})


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    processor = ProjectNebulaProcessor()

    if len(sys.argv) > 1:
        test_input = sys.argv[1]
    else:
        # Default test: engineering signal with a result
        test_input = json.dumps({
            "action_text": "Designed and implemented a distributed event processing pipeline",
            "category":    "Work",
            "priority":    "high",
            "duration":    45,
            "effort_signals": {
                "result_type":  "numeric",
                "result_value": 3,
                "result_unit":  "modules",
                "result_text":  "Completed ingestion, processing, and storage modules",
            }
        })

    output = processor.project_signal_state(test_input)
    print(f"\nNebula Engine Output:\n{output}\n")
