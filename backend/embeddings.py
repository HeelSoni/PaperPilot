from sentence_transformers import SentenceTransformer
import torch
import os

class Embedder:
    def __init__(self, model_name=None):
        if model_name is None:
            model_name = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        try:
            print(f"Loading embedder: {model_name}...")
            self.model = SentenceTransformer(model_name).to(self.device)
            print(f"Loaded model {model_name} on {self.device}")
        except Exception as e:
            print(f"Failed to load embedder {model_name}: {e}")
            self.model = None

    def embed_text(self, text):
        if not self.model:
            # Fallback or error
            raise RuntimeError("Embedding model not loaded.")
            
        if isinstance(text, str):
            text = [text]
        embeddings = self.model.encode(text, convert_to_tensor=True)
        return embeddings

# Global instance
embedder = None

def get_embedder():
    global embedder
    if embedder is None:
        embedder = Embedder()
    return embedder
