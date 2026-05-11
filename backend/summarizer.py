from transformers import pipeline
import torch

class Summarizer:
    def __init__(self, model_name='facebook/bart-large-cnn'):
        self.device = 0 if torch.cuda.is_available() else -1
        self.summarizer = pipeline("summarization", model=model_name, device=self.device)
        print(f"Loaded summarizer {model_name} on {'gpu' if self.device == 0 else 'cpu'}")

    def summarize(self, text, max_length=150, min_length=40):
        """
        Generates a summary for the given text.
        """
        try:
            print(f"--- Summarizing text (length: {len(text)}) ---")
            # Truncate text if it's too long for the model (BART has a 1024 token limit)
            if len(text) > 1024:
                text = text[:1024]
                
            summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            if summary and len(summary) > 0:
                print("Summary generated successfully.")
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
