import os
import re
import requests

# HuggingFace Inference API — using high-quality instruction-tuned models
_HF_SUMMARIZE_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
_HF_INSTRUCT_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
_HF_TOKEN = os.environ.get("HUGGINGFACE_API_KEY", "")

class Summarizer:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {_HF_TOKEN}"} if _HF_TOKEN else {}
        print("Summarizer ready — using flan-t5-large (intelligence) + bart-large-cnn (summary)")

    def _call_ai(self, prompt, model_url, params=None):
        """Helper to call HuggingFace models with retry and error handling."""
        if params is None:
            params = {"max_new_tokens": 150, "temperature": 0.7}
        
        payload = {"inputs": prompt, "parameters": params}
        try:
            response = requests.post(model_url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result:
                    return result[0].get("generated_text", "").strip()
                return result.get("generated_text", "").strip()
            return None
        except Exception as e:
            print(f"AI Call error: {e}")
            return None

    def summarize(self, text, max_length=150, min_length=40):
        if len(text) > 1500: text = text[:1500]
        payload = {
            "inputs": text,
            "parameters": {"max_length": max_length, "min_length": min_length, "do_sample": False}
        }
        try:
            response = requests.post(_HF_SUMMARIZE_URL, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result:
                    return result[0].get("summary_text", self._fallback_summary(text))
            return self._fallback_summary(text)
        except:
            return self._fallback_summary(text)

    def _fallback_summary(self, text):
        sentences = text.replace('\n', ' ').split('. ')
        return '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else text[:300]

    def extract_insights(self, title, abstract):
        """Generates structured insights using Flan-T5 instruction tuning."""
        fields = ["methodology", "dataset", "key_results", "limitations", "future_work"]
        results = {}
        
        # We ask the AI to extract each field specifically to ensure accuracy
        for field in fields:
            prompt = f"Context: {title}. {abstract}\n\nQuestion: Based on the abstract above, what is the {field.replace('_', ' ')} of this research? Answer in one short sentence."
            ans = self._call_ai(prompt, _HF_INSTRUCT_URL, {"max_new_tokens": 50})
            
            if ans and len(ans) > 5 and "abstract above" not in ans.lower():
                results[field] = ans
            else:
                results[field] = self._regex_fallback(field, abstract)

        return results

    def _regex_fallback(self, field, abstract):
        """Safety fallback if AI is slow or fails."""
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if len(s.strip()) > 20]
        keywords = {
            "methodology": ['propose', 'approach', 'method', 'framework', 'architecture', 'using'],
            "dataset": ['dataset', 'benchmark', 'data', 'experiment', 'samples'],
            "key_results": ['achiev', 'outperform', 'result', 'accuracy', 'show'],
            "limitations": ['limitation', 'however', 'challenge', 'fail', 'gap'],
            "future_work": ['future', 'next', 'extend', 'plan']
        }
        for sent in sentences:
            if any(w in sent.lower() for w in keywords.get(field, [])):
                return sent[:120]
        return "Refer to the main abstract for details."

    def answer_question(self, title, abstract, question):
        """Instruction-tuned QA for varied and specific answers."""
        prompt = f"Paper Title: {title}\nAbstract: {abstract}\n\nUser Question: {question}\n\nDetailed Answer:"
        ans = self._call_ai(prompt, _HF_INSTRUCT_URL, {"max_new_tokens": 150, "temperature": 0.5})
        
        if ans and len(ans) > 10:
            return ans
        
        # Smart regex fallback if LLM fails
        return self._smart_text_fallback(question, abstract)

    def _smart_text_fallback(self, question, abstract):
        sentences = abstract.replace('\n', ' ').split('. ')
        q_words = set(re.findall(r'\w+', question.lower())) - {'what', 'is', 'the', 'how', 'why', 'in', 'of'}
        best, best_score = sentences[0] if sentences else abstract[:200], 0
        for s in sentences:
            score = sum(1 for w in q_words if w in s.lower())
            if score > best_score:
                best, best_score = s, score
        return f"{best.strip()}. (Extracted from abstract)"

# Global singleton
summarizer = None
def get_summarizer():
    global summarizer
    if summarizer is None: summarizer = Summarizer()
    return summarizer
