from sentence_transformers import SentenceTransformer
import torch

class Embedder:
    def __init__(self, model_name='sentence-transformers/allenai-specter'):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model_name).to(self.device)
        print(f"Loaded model {model_name} on {self.device}")

    def embed_text(self, text):
        """
        Generates embedding for a single string or list of strings.
        """
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
