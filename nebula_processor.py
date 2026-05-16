import json
import nltk
import uuid
import numpy as np
from nltk.tokenize import word_tokenize
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import CONFIG
from storage import save_event

# Ensure NLTK resources are available
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

class ProjectNebulaProcessor:
    def __init__(self, config=CONFIG):
        self.config = config
        self.identity_fields = self.config["identity_fields"]
        self.identities = list(self.identity_fields.keys())
        self.backend = self.config.get("semantic_backend", "tfidf")
        
        # Initialize TF-IDF (Legacy/Baseline)
        self.vectorizer = TfidfVectorizer()
        identity_texts = [self.identity_fields[i] for i in self.identities]
        self.target_vectors_tfidf = self.vectorizer.fit_transform(identity_texts)
        
        # Initialize MiniLM (New/Candidate)
        try:
                    # pyrefly: ignore [missing-import]
            from sentence_transformers import SentenceTransformer
            self.model_minilm = SentenceTransformer('all-MiniLM-L6-v2')
            self.target_vectors_minilm = self.model_minilm.encode(identity_texts)
            self.minilm_available = True
        except ImportError:
            self.minilm_available = False
        
        # Identity State (Sprint 4)
        self.inertia = self.config.get("inertia", 0.9)
        self.current_identity = self.load_identity_state()

    def clean_text(self, text):
        """Lowercase and tokenize the incoming action text."""
        if not text:
            return ""
        tokens = word_tokenize(text.lower())
        return " ".join([t for t in tokens if t.isalnum()])

    def load_identity_state(self):
        """Loads the current identity centroid from persistence."""
        path = self.config["identity_state_path"]
        if path.exists():
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    return np.array(data["accumulated_vector"])
            except Exception:
                pass
        
        # Initialize with zeros if no state exists
        dim = 384 if self.backend == "minilm" else len(self.identities)
        return np.zeros(dim)

    def save_identity_state(self, vector):
        """Persists the updated identity centroid."""
        path = self.config["identity_state_path"]
        with open(path, "w") as f:
            json.dump({
                "accumulated_vector": vector.tolist(), 
                "updated_at": datetime.utcnow().isoformat()
            }, f)

    def calculate_alignment_for_vector(self, vector):
        """Calculates similarity between a given vector and all attractors."""
        if self.backend == "tfidf":
            target_vectors = self.target_vectors_tfidf
        else:
            target_vectors = self.target_vectors_minilm
            
        # Reshape vector if it's 1D
        v = vector.reshape(1, -1)
        similarities = cosine_similarity(v, target_vectors)[0]
        return {self.identities[i]: float(similarities[i]) for i in range(len(self.identities))}

    def calculate_alignment(self, action_text):
        """Calculates cosine similarity against all target identity vectors using available backends."""
        results = {}
        if not action_text:
            return {"tfidf": {id: 0.0 for id in self.identities}, "minilm": {id: 0.0 for id in self.identities}}
        
        # Calculate TF-IDF
        action_vector_tfidf = self.vectorizer.transform([action_text])
        similarities_tfidf = cosine_similarity(action_vector_tfidf, self.target_vectors_tfidf)[0]
        results["tfidf"] = {self.identities[i]: float(similarities_tfidf[i]) for i in range(len(self.identities))}
        
        # Calculate MiniLM if available
        if self.minilm_available:
            action_vector_minilm = self.model_minilm.encode([action_text])
            similarities_minilm = cosine_similarity(action_vector_minilm, self.target_vectors_minilm)[0]
            results["minilm"] = {self.identities[i]: float(similarities_minilm[i]) for i in range(len(self.identities))}
        
        return results

    def determine_state(self, final_score):
        thresholds = self.config.get("thresholds", {"friction": 0.5, "black_hole": -0.5})
        if final_score > thresholds["friction"]:
            return {"state": "Friction", "color": "#BC13FE"}  # Neon Purple
        elif final_score >= thresholds["black_hole"]:
            return {"state": "Degenerate Matter", "color": "#FFA500"}  # Warning Orange
        else:
            return {"state": "Black Hole", "color": "#000000"}  # The Void

    def project_signal_state(self, input_data):
        """Processes an incoming signal and calculates its physical state."""
        try:
            # Handle both JSON string and dictionary
            if isinstance(input_data, str):
                data = json.loads(input_data)
            else:
                data = input_data

            payload = data.get("body", data)
            
            # Robust field extraction
            action_text = payload.get("content") or payload.get("action_text", "")
            category = payload.get("signal_type") or payload.get("category", "Void")
            priority = payload.get("priority", "medium")
            duration = payload.get("duration", 0)

            cleaned_text = self.clean_text(action_text)
            multi_alignments = self.calculate_alignment(cleaned_text)
            
            # Use configured backend for primary scoring
            alignments = multi_alignments.get(self.backend, multi_alignments["tfidf"])
            
            # Determine dominant attractor for the SIGNAL
            dominant_attractor = max(alignments, key=alignments.get)
            alignment_score = alignments[dominant_attractor]
            
            # --- IDENTITY DRIFT ENGINE (Sprint 4: Phase 4C - Weighted Updates) ---
            identity_before = self.current_identity.copy()
            
            # Get vector for current signal
            if self.backend == "tfidf":
                signal_vector = self.vectorizer.transform([cleaned_text]).toarray()[0]
            else:
                signal_vector = self.model_minilm.encode([cleaned_text])
            
            # Calculate Dynamic Pull (Phase 4C)
            # Baseline: a 30-min medium priority task pulls by (1 - inertia)
            base_duration = 30
            duration_factor = max(0.1, duration / base_duration)
            
            # dynamic_pull scales with impact_weight and duration
            dynamic_pull = (1 - self.inertia) * weight * duration_factor
            
            # Cap dynamic_pull to 0.5 to prevent single-event identity hijacking
            # (Keeping the system "heavy")
            dynamic_pull = min(0.5, dynamic_pull)
            
            # Update global identity using Dynamic Pull
            # new = (old * (1 - pull)) + (signal * pull)
            self.current_identity = (identity_before * (1 - dynamic_pull)) + (signal_vector * dynamic_pull)
            self.save_identity_state(self.current_identity)
            
            # Calculate drift delta (Distance moved)
            drift_delta = float(np.linalg.norm(self.current_identity - identity_before))
            
            # Calculate Global Dominance (Who are you becoming?)
            global_dominance = self.calculate_alignment_for_vector(self.current_identity)
            global_dominant_identity = max(global_dominance, key=global_dominance.get)
            # ----------------------------------------

            weight = self.config["impact_tones"].get(category, 0.0)
            
            if priority == "high":
                weight *= 1.2

            physics = {
                "alignment": alignment_score, 
                "impact_weight": weight,
                "dominant_attractor": dominant_attractor,
                "all_alignments": alignments
            }
            final_score = physics["alignment"] * physics["impact_weight"]
            result = self.determine_state(final_score)

            event_id = str(uuid.uuid4())

            event = {
                "event_id": event_id,
                "timestamp": datetime.utcnow().isoformat(),
                "action_text": action_text,
                "category": category,
                "duration": duration,
                "priority": priority,
                "alignment_score": alignment_score,
                "weight": weight,
                "final_score": final_score,
                "state": result["state"],
                "dominant_attractor": dominant_attractor,
                "global_dominant_identity": global_dominant_identity,
                "physics_params": {
                    "alignment": alignment_score,
                    "impact_weight": weight,
                    "all_alignments": alignments,
                    "multi_backend_comparison": multi_alignments,
                    "active_backend": self.backend,
                    "identity_snapshot": {
                        "drift_delta": drift_delta,
                        "global_dominance": global_dominance,
                        "inertia_base": self.inertia,
                        "dynamic_pull": dynamic_pull,
                        "duration_applied": duration
                    }
                }
            }
            
            save_event(event)

            return json.dumps({
                "event_id": event_id,
                "state": result["state"],
                "color": result["color"],
                "dominant_attractor": dominant_attractor,
                "global_dominant_identity": global_dominant_identity,
                "drift_delta": drift_delta,
                "final_score": final_score,
                "active_backend": self.backend,
                "physics": physics,
                "cleaned_text": cleaned_text
            }, indent=4)

        except Exception as e:
            return json.dumps({"error": str(e)})

if __name__ == "__main__":
    import sys
    processor = ProjectNebulaProcessor()
    
    # Allow passing JSON string as argument or use default sample
    if len(sys.argv) > 1:
        test_input = sys.argv[1]
    else:
        test_input = json.dumps({
            "content": "Exploring the event horizon of code architecture",
            "category": "Work",
            "priority": "high"
        })
    
    output = processor.project_signal_state(test_input)
    print(f"Nebula Analysis Output:\n{output}")