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
        print("Summarizer ready — bart-large-cnn (summary) + roberta-squad2 (chat) + regex (insights)")

    # ------------------------------------------------------------------ #
    # 1. AI EXECUTIVE SUMMARY — facebook/bart-large-cnn                   #
    # ------------------------------------------------------------------ #
    def summarize(self, text, max_length=150, min_length=40):
        if len(text) > 1500:
            text = text[:1500]
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
    # 2. KEY INSIGHTS — Smart regex (always works, no API needed)          #
    # ------------------------------------------------------------------ #
    def extract_insights(self, title, abstract):
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if len(s.strip()) > 20]

        # Broad keyword lists to handle both technical and theoretical papers
        method_kw = ['propose', 'present', 'introduce', 'method', 'approach', 'framework',
                     'architecture', 'using', 'based on', 'leverage', 'design', 'develop',
                     'train', 'apply', 'algorithm', 'analyze', 'study', 'investigate',
                     'examine', 'explore', 'classify', 'model', 'technique', 'strategy']
        data_kw = ['dataset', 'benchmark', 'corpus', 'evaluated on', 'tested on',
                   'trained on', 'imagenet', 'coco', 'experiment', 'collected', 'samples',
                   'real-world', 'task', 'validation', 'test set']
        result_kw = ['achiev', 'outperform', 'improv', 'state-of-the-art', 'sota',
                     'accuracy', 'performance', 'demonstrat', 'show', 'result', 'gain',
                     'reduce', 'increase', 'surpass', 'beat', 'significant', 'effective']
        limit_kw = ['limitation', 'however', 'drawback', 'challenge', 'difficult',
                    'fail', 'cannot', 'does not', 'restricted', 'constrain', 'despite',
                    'lack', 'issue', 'problem', 'concern', 'gap']
        future_kw = ['future', 'will ', 'plan to', 'next step', 'extend',
                     'promising', 'hope to', 'intend to', 'ongoing', 'open question']

        methodology = None
        dataset = None
        key_results = None
        limitations = None
        future_work = None

        for sent in sentences:
            slow = sent.lower()
            if methodology is None and any(w in slow for w in method_kw):
                methodology = sent[:130]
            if dataset is None and any(w in slow for w in data_kw):
                dataset = sent[:130]
            if key_results is None and any(w in slow for w in result_kw):
                key_results = sent[:130]
            if limitations is None and any(w in slow for w in limit_kw):
                limitations = sent[:130]
            if future_work is None and any(w in slow for w in future_kw):
                future_work = sent[:130]

        # Smart fallbacks using actual abstract content
        all_sentences = sentences if sentences else [abstract[:200]]
        return {
            "methodology": methodology or (all_sentences[0] if all_sentences else "See abstract"),
            "dataset": dataset or "Not explicitly mentioned in abstract",
            "key_results": key_results or (all_sentences[-1] if len(all_sentences) > 1 else "See summary above"),
            "limitations": limitations or "Not explicitly stated",
            "future_work": future_work or "Not specified"
        }

    # ------------------------------------------------------------------ #
    # 3. CHAT — Question-aware fallback (always gives relevant answer)     #
    # ------------------------------------------------------------------ #
    def answer_question(self, title, abstract, question):
        context = f"{title}. {abstract}"
        payload = {"inputs": {"question": question, "context": context[:2000]}}

        try:
            response = requests.post(_HF_QA_URL, headers=self.headers, json=payload, timeout=25)
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "").strip()
                score = result.get("score", 0)
                if answer and score > 0.05:
                    return f"{answer} (from the paper's abstract)"
            elif response.status_code == 503:
                return "The AI model is warming up. Please try again in 20 seconds."
            print(f"Chat QA error: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            print(f"Chat exception: {e}")

        return self._smart_fallback(question, abstract)

    def _smart_fallback(self, question, abstract):
        """Returns a question-specific answer by matching question type to relevant sentences."""
        q_lower = question.lower()
        sentences = [s.strip() for s in abstract.replace('\n', ' ').split('. ') if len(s.strip()) > 20]
        if not sentences:
            return f"Based on the abstract: {abstract[:200]}"

        # Map question intent to relevant keywords in the abstract
        intent_map = [
            (['method', 'how', 'approach', 'technique', 'algorithm', 'architecture', 'work'],
             ['propose', 'method', 'approach', 'using', 'based on', 'framework', 'algorithm',
              'architecture', 'design', 'implement', 'apply', 'technique']),
            (['dataset', 'data', 'train', 'benchmark', 'corpus', 'collect'],
             ['dataset', 'benchmark', 'trained', 'evaluated', 'data', 'corpus', 'collected',
              'experiment', 'sample', 'task']),
            (['result', 'performance', 'accuracy', 'achieve', 'beat', 'contribution', 'main', 'novel'],
             ['achiev', 'outperform', 'result', 'accuracy', 'improve', 'demonstrate', 'show',
              'propose', 'novel', 'introduce', 'first']),
            (['limitation', 'problem', 'challenge', 'weakness', 'drawback', 'issue'],
             ['limitation', 'however', 'challenge', 'difficult', 'drawback', 'fail',
              'cannot', 'despite', 'lack', 'gap']),
            (['future', 'next', 'plan', 'extend', 'direction'],
             ['future', 'next', 'extend', 'plan', 'promising', 'ongoing']),
        ]

        for q_keywords, text_keywords in intent_map:
            if any(w in q_lower for w in q_keywords):
                for sent in sentences:
                    if any(w in sent.lower() for w in text_keywords):
                        return f"{sent} (extracted from abstract)"

        # General word-overlap fallback
        q_words = set(re.findall(r'\w+', q_lower)) - {
            'what', 'is', 'the', 'a', 'of', 'in', 'how', 'why', 'did',
            'does', 'was', 'are', 'this', 'that', 'it', 'be', 'to', 'for'
        }
        best, best_score = sentences[0], 0
        for s in sentences:
            score = sum(1 for w in q_words if w in s.lower())
            if score > best_score:
                best, best_score = s, score
        return f"{best} (extracted from abstract)"


# Global singleton
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = Summarizer()
    return summarizer
