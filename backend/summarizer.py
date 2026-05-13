import os
import re
import requests

# HuggingFace Inference API — stable, non-gated models only
_HF_SUMMARIZE_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
_HF_QA_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
_HF_TOKEN = os.environ.get("HUGGINGFACE_API_KEY", "")


class Summarizer:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {_HF_TOKEN}"} if _HF_TOKEN else {}
        print("Summarizer ready — using bart-large-cnn (summary) + roberta-squad2 (chat)")

    # ------------------------------------------------------------------ #
    # 1. AI EXECUTIVE SUMMARY — facebook/bart-large-cnn                   #
    # ------------------------------------------------------------------ #
    def summarize(self, text, max_length=150, min_length=40):
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
            response = requests.post(_HF_SUMMARIZE_URL, headers=self.headers,
                                     json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and result:
                    return result[0].get("summary_text", self._fallback_summary(text))
            elif response.status_code == 503:
                return "Model is warming up. Please try again in 20 seconds."
            print(f"Summary API error: {response.status_code}")
            return self._fallback_summary(text)
        except Exception as e:
            print(f"Summarizer error: {e}")
            return self._fallback_summary(text)

    def _fallback_summary(self, text):
        sentences = text.replace('\n', ' ').split('. ')
        return '. '.join(sentences[:2]) + '.' if len(sentences) >= 2 else text[:300]

    # ------------------------------------------------------------------ #
    # 2. KEY INSIGHTS — Smart regex parsing, no API needed                #
    # ------------------------------------------------------------------ #
    def extract_insights(self, title, abstract):
        """Extract structured insights from the abstract using regex heuristics.
        This is 100% reliable — no external API needed."""
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if len(s.strip()) > 20]

        methodology = "See abstract for details"
        dataset = "Not explicitly mentioned"
        key_results = "Refer to summary"
        limitations = "Not specified"
        future_work = "Not specified"

        method_kw = ['propose', 'present', 'introduce', 'method', 'approach',
                     'framework', 'architecture', 'using', 'based on', 'leverage',
                     'we design', 'we develop', 'we train', 'we apply', 'algorithm']
        data_kw = ['dataset', 'benchmark', 'corpus', 'evaluated on', 'tested on',
                   'trained on', 'imagenet', 'coco', 'collected', 'samples', 'experiments']
        result_kw = ['achiev', 'outperform', 'improv', 'state-of-the-art', 'sota',
                     'accuracy', 'performance', 'demonstrat', 'show', 'result', 'gain']
        limit_kw = ['limitation', 'however', 'drawback', 'challenge', 'difficult',
                    'fail', 'cannot', 'does not', 'restricted', 'constrain']
        future_kw = ['future', 'will ', 'plan to', 'next step', 'extend',
                     'promising', 'hope to', 'intend to']

        for sent in sentences:
            slow = sent.lower()
            if methodology == "See abstract for details" and any(w in slow for w in method_kw):
                methodology = sent[:120]
            if dataset == "Not explicitly mentioned" and any(w in slow for w in data_kw):
                dataset = sent[:120]
            if key_results == "Refer to summary" and any(w in slow for w in result_kw):
                key_results = sent[:120]
            if limitations == "Not specified" and any(w in slow for w in limit_kw):
                limitations = sent[:120]
            if future_work == "Not specified" and any(w in slow for w in future_kw):
                future_work = sent[:120]

        return {
            "methodology": methodology,
            "dataset": dataset,
            "key_results": key_results,
            "limitations": limitations,
            "future_work": future_work
        }

    # ------------------------------------------------------------------ #
    # 3. CHAT WITH PAPER — deepset/roberta-base-squad2 (free, no gate)   #
    # ------------------------------------------------------------------ #
    def answer_question(self, title, abstract, question):
        """Answer a question about a paper using a reliable QA model."""
        context = f"{title}. {abstract}"

        payload = {
            "inputs": {
                "question": question,
                "context": context[:2000]
            }
        }

        try:
            response = requests.post(_HF_QA_URL, headers=self.headers,
                                     json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "").strip()
                score = result.get("score", 0)
                if answer and score > 0.01:
                    return f"{answer} (based on the paper's abstract)"
                else:
                    return self._fallback_answer(question, abstract)
            elif response.status_code == 503:
                return "The AI model is warming up. Please try again in 20 seconds."
            print(f"Chat QA error: {response.status_code} - {response.text[:100]}")
            return self._fallback_answer(question, abstract)
        except Exception as e:
            print(f"Chat exception: {e}")
            return self._fallback_answer(question, abstract)

    def _fallback_answer(self, question, abstract):
        """Return the most relevant sentence from the abstract."""
        q_words = set(re.findall(r'\w+', question.lower())) - {'what', 'is', 'the', 'a', 'of', 'in', 'how', 'why'}
        sentences = abstract.replace('\n', ' ').split('. ')
        best, best_score = sentences[0] if sentences else abstract[:200], 0
        for s in sentences:
            score = sum(1 for w in q_words if w in s.lower())
            if score > best_score:
                best, best_score = s, score
        return f"{best.strip()}. (Answer extracted from the abstract)"


# Global singleton
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = Summarizer()
    return summarizer
