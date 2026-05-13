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

    def extract_insights(self, title, abstract):
        """Extracts structured insights using an instruction-tuned model."""
        # Use a more capable model for instructions
        insight_model_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        
        prompt = f"""
        Extract key technical details from this research paper abstract.
        Format the response as a JSON object with these keys: methodology, dataset, key_results, limitations, future_work.
        Keep each value under 20 words. If not mentioned, write "Not specified".

        Title: {title}
        Abstract: {abstract}
        
        JSON Result:
        """

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 250,
                "return_full_text": False
            }
        }

        try:
            response = requests.post(insight_model_url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                text = result[0].get("generated_text", "")
                # Basic cleanup to find JSON in the response
                import json
                import re
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            
            print(f"Insight API error: {response.status_code}")
            return self._fallback_insights()
        except Exception as e:
            print(f"Insight extraction error: {e}")
            return self._fallback_insights()

    def _fallback_insights(self):
        return {
            "methodology": "See abstract for details",
            "dataset": "Not explicitly mentioned",
            "key_results": "Refer to summary",
            "limitations": "Not specified",
            "future_work": "Not specified"
        }

    def answer_question(self, title, abstract, question):
        """Answers a question about the paper using the abstract."""
        chat_model_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        
        prompt = f"""
        You are an AI research assistant. Answer the question about the research paper based on the title and abstract provided.
        If the answer is not in the abstract, say "I couldn't find that specific detail in the abstract."
        Keep the answer concise (under 3 sentences).

        Paper Title: {title}
        Paper Abstract: {abstract}
        
        Question: {question}
        
        Answer:
        """

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 150,
                "return_full_text": False
            }
        }

        try:
            response = requests.post(chat_model_url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result[0].get("generated_text", "").strip()
            
            print(f"Chat API error: {response.status_code}")
            return "I'm having trouble connecting to my brain right now. Please try again."
        except Exception as e:
            print(f"Chat error: {e}")
            return "An error occurred while trying to answer your question."

# Global instance
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = Summarizer()
    return summarizer
