import os
import requests

# HuggingFace Inference API — stable models
_HF_SUMMARIZE_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
_HF_TOKEN = os.environ.get("HUGGINGFACE_API_KEY", "")

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
            response = requests.post(_HF_SUMMARIZE_URL, headers=self.headers, json=payload, timeout=30)
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
        insight_model_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
        
        prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nExtract technical details as JSON with keys: methodology, dataset, key_results, limitations, future_work. Keep values under 15 words.<|eot_id|><|start_header_id|>user<|end_header_id|>\nTitle: {title}\nAbstract: {abstract}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"

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
                # 1. Try to find JSON
                import json
                import re
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    try:
                        parsed = json.loads(match.group(0))
                        # Ensure all keys exist
                        for key in ["methodology", "dataset", "key_results", "limitations", "future_work"]:
                            if key not in parsed:
                                parsed[key] = "Check abstract"
                        return parsed
                    except:
                        pass
                
                # 2. Fallback: Try to parse line by line if AI sends plain text
                lines = text.split('\n')
                result = self._fallback_insights()
                for line in lines:
                    low = line.lower()
                    if 'method' in low: result['methodology'] = line.split(':')[-1].strip()[:50]
                    if 'data' in low: result['dataset'] = line.split(':')[-1].strip()[:50]
                    if 'result' in low: result['key_results'] = line.split(':')[-1].strip()[:50]
                    if 'limit' in low: result['limitations'] = line.split(':')[-1].strip()[:50]
                    if 'future' in low: result['future_work'] = line.split(':')[-1].strip()[:50]
                return result
            
            print(f"Insight API error {response.status_code}: {response.text[:100]}")
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
        if not os.getenv('HUGGINGFACE_API_KEY'):
            return "Please set HUGGINGFACE_API_KEY in environment variables to enable chat."

        # Use Mistral-7B-Instruct-v0.2 for proven stability
        chat_model_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        
        prompt = f"<s>[INST] You are a research assistant. Answer based on this paper.\nTitle: {title}\nAbstract: {abstract}\n\nQuestion: {question} [/INST]"

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
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "No answer available.").split("[/INST]")[-1].strip()
            
            # Log the error for the user to see in Railway
            print(f"Chat AI Error: {response.status_code} - {response.text}")
            return "I'm having trouble connecting to my brain right now. Please try again."
        except Exception as e:
            print(f"Chat AI Exception: {e}")
            return "I'm having trouble connecting to my brain right now. Please try again."

# Global instance
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = Summarizer()
    return summarizer
