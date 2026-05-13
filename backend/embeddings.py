from sentence_transformers import SentenceTransformer
import os

class Embedder:
    def __init__(self, model_name=None):
        if model_name is None:
            model_name = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

        try:
            print(f"Loading embedder: {model_name}...")
            self.model = SentenceTransformer(model_name)
            print(f"Embedder loaded: {model_name}")
        except Exception as e:
            print(f"Failed to load embedder {model_name}: {e}")
            self.model = None

    def embed_text(self, text):
        if not self.model:
            raise RuntimeError("Embedding model not loaded.")

        if isinstance(text, str):
            text = [text]
        # Returns a numpy array directly (no .cpu() needed without explicit torch)
        return self.model.encode(text, convert_to_numpy=True)

# Global instance
embedder = None

def get_embedder():
    global embedder
    if embedder is None:
        embedder = Embedder()
    return embedder
