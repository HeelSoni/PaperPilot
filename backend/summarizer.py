import os
import requests

# HuggingFace Inference API — no local model needed
_HF_API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
_HF_TOKEN = os.environ.get("HF_API_TOKEN", "")  # Optional: set for higher rate limits

class Summarizer:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {_HF_TOKEN}"} if _HF_TOKEN else {}
        print("Summarizer ready (using HuggingFace Inference API — no local model)")

    def summarize(self, text, max_length=150, min_length=40):
        # Truncate input to keep API response fast
        if len(text) > 1500:
            text = text[:1500]

        payload = {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": False
            }
        }

        try:
            response = requests.post(_HF_API_URL, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("summary_text", "No summary available.")
            elif response.status_code == 503:
                # Model is loading — return a friendly message
                return "Model is warming up on HuggingFace. Please try again in 20 seconds."
            print(f"HF API error: {response.status_code} — {response.text[:200]}")
            return self._fallback_summary(text)
        except Exception as e:
            print(f"Summarizer error: {e}")
            return self._fallback_summary(text)

    def _fallback_summary(self, text):
        """Simple extractive fallback: return first 2 sentences."""
        sentences = text.replace('\n', ' ').split('. ')
        return '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else text[:300]

# Global instance
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = Summarizer()
    return summarizer
