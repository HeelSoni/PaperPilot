from transformers import pipeline
import torch
import os

class Summarizer:
    def __init__(self, model_name=None):
        # Default to a smaller model for deployment compatibility
        if model_name is None:
            model_name = os.environ.get("SUMMARIZER_MODEL", "sshleifer/distilbart-cnn-6-6")
            
        self.device = 0 if torch.cuda.is_available() else -1
        try:
            print(f"Loading summarizer: {model_name}...")
            self.summarizer = pipeline("summarization", model=model_name, device=self.device)
            print(f"Loaded summarizer on {'gpu' if self.device == 0 else 'cpu'}")
        except Exception as e:
            print(f"Failed to load model {model_name}: {e}")
            self.summarizer = None

    def summarize(self, text, max_length=150, min_length=40):
        if not self.summarizer:
            return "Summarizer model not loaded due to memory or initialization error."
            
        try:
            # BART 1024 token limit check (rough estimation by characters)
            if len(text) > 3000: 
                text = text[:3000]
                
            summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            if summary:
                return summary[0]['summary_text']
            return "No summary could be generated."
        except Exception as e:
            print(f"Summarization error: {e}")
            return f"Error during summarization: {str(e)}"

# Global instance
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = Summarizer()
    return summarizer
