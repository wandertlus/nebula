# Project Nebula: Rules & System Architecture v1.0

## 1. System Philosophy (The Core)
*   **Emergent Identity:** The system is not a diary; it is a mirror. User identity is defined by the vector sum of real-time actions, not declared intentions.
*   **Attractors:** The states Violet, Orange, and Black function as gravitational wells. The system assumes inertia tends toward disorder (entropy) unless an "Alignment" force is applied.
*   **No Moralization:** Classifications are descriptive, not value judgments. The "Black Hole" is simply a state of low alignment and high repetition that consumes system resources.
*   **Temporal Dynamics:** The relevance of an event is governed by a decay function. The impact of an action decreases proportionally to the time elapsed since its execution.

## 2. Systems Architecture
*   **Ingestion (n8n):** The "Central Nervous System." Manages incoming Webhooks, normalizes data, and sends it to the processor.
*   **NLP Engine (Python/Cerebral Cortex):** Transforms natural language into spatial coordinates.
    *   *Current Tool:* TF-IDF / Scikit-learn (Base).
    *   *Next Step:* Sentence Transformers (BERT).
*   **Persistence:** Storage of events in JSON/NoSQL format to maintain the "celestial trajectory" history.
*   **Visualization (Future):** Projection in Streamlit/D3.js to represent system mass and friction in 2D/3D space.

## 3. Physics Engine (Calculation Logic)
The state of each data particle is determined by:
1.  **Alignment ($\cos \theta$):** Measure of similarity between the `input` vector and the `North Star` vector.
2.  **Impact ($W$):** Weight assigned based on task magnitude (inferred or declared).
3.  **Temporal Inertia:** Factor that resists sudden state changes. (e.g., 3 consecutive "Violet" events increase resistance to falling into a "Black Hole").
4.  **Drift:** Automatic displacement toward the center of the system if no activity is recorded within a defined interval.

## 5. Current Limitations (Technical Debt)
TF-IDF Semantic Weakness: The current engine does not understand context or synonyms. If the goal is "Engineering" and the input is "Development," similarity will be low.

No Temporal Inertia: Each event is calculated in isolation. The system does not remember if you are coming from a productive streak or a distraction loop.

Static Thresholds: Limits (0.5, -0.5) are rigid and do not consider external factors like time of day or previous workload.

Single Active Identity: (Deprecated) Moving toward multiple "North Stars" to allow for complex role coexistence.

## Planned Evolution (The Roadmap)
Phase 1: Sentence Transformers. Migrate to dense embeddings to capture the real meaning of actions.

Phase 2: Adaptive Thresholds. Algorithms that adjust state limits based on historical behavior from the last 7 days.

Phase 3: Identity Drift Engine. Capacity to handle multiple objectives and measure how the "gravity" of one affects others.

Phase 4: Graph-based Memory. Implementation of a graph database to map non-linear relationships between tasks and states.

Phase 5: Orbit Visualization. Dynamic interface where task "mass" visually deforms the dashboard space.

## Engineering Principles
Interpretability First: Every classification must be explainable via Physics Engine parameters.

Avoid Black-Box AI: Prioritize clear vector logic over opaque generative language models.

Observable State Transitions: Every state change must be recorded as an analyzable physical event.

Semantic Auditability: Ability to track exactly which vector dimensions caused a shift in the system.

## 4. Event Schema (Data Contract)
All processed events must strictly follow this structure:
```json
{
  "event_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "action_text": "string",
  "category": "string",
  "alignment_score": "float",
  "weight": "float",
  "final_score": "float",
  "state": "Violet | Orange | Black",
  "duration": "int",
  "physics_params": {
    "alignment": "float",
    "impact_weight": "float",
    "all_alignments": "object"
  }
}
```