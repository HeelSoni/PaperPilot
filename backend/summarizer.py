import os
import re
import requests

_HF_SUMMARIZE_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
_HF_TOKEN = os.environ.get("HUGGINGFACE_API_KEY", "")


class Summarizer:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {_HF_TOKEN}"} if _HF_TOKEN else {}
        print("Summarizer ready — bart-large-cnn + smart clause extraction")

    # ─────────────────────────────────────────────
    # 1.  AI SUMMARY (always works)
    # ─────────────────────────────────────────────
    def summarize(self, text, max_length=150, min_length=40):
        if len(text) > 1500:
            text = text[:1500]
        payload = {
            "inputs": text,
            "parameters": {"max_length": max_length, "min_length": min_length, "do_sample": False}
        }
        try:
            r = requests.post(_HF_SUMMARIZE_URL, headers=self.headers, json=payload, timeout=30)
            if r.status_code == 200:
                result = r.json()
                if isinstance(result, list) and result:
                    return result[0].get("summary_text", self._fallback_summary(text))
            return self._fallback_summary(text)
        except:
            return self._fallback_summary(text)

    def _fallback_summary(self, text):
        parts = text.replace('\n', ' ').split('. ')
        return '. '.join(parts[:2]) + '.' if len(parts) >= 2 else text[:300]

    # ─────────────────────────────────────────────
    # 2.  KEY INSIGHTS — clause-aware extraction
    # ─────────────────────────────────────────────
    def extract_insights(self, title, abstract):
        """
        Extracts 5 insight fields from any abstract, even single-sentence ones,
        by splitting into clauses and scoring each against the field's intent.
        """
        parts = self._get_all_parts(abstract)

        methodology  = self._find_best(parts, ['propose', 'present', 'attempt', 'define',
                                                 'introduce', 'develop', 'design', 'use',
                                                 'apply', 'study', 'explore', 'investigate',
                                                 'analyze', 'examine', 'approach', 'evaluate',
                                                 'method', 'framework', 'architecture', 'model'])
        dataset      = self._find_best(parts, ['dataset', 'benchmark', 'corpus', 'data',
                                                'experiment', 'train', 'test', 'sample',
                                                'imagenet', 'coco', 'evaluated on', 'collected',
                                                'real-world', 'simulation'])
        key_results  = self._find_best(parts, ['result', 'achieve', 'outperform', 'improve',
                                                'show', 'demonstrate', 'conclude', 'find',
                                                'accuracy', 'performance', 'significant',
                                                'better', 'higher', 'lower', 'increase'])
        limitations  = self._find_best(parts, ['limitation', 'however', 'challenge', 'drawback',
                                                'fail', 'cannot', 'does not', 'restricted',
                                                'constrain', 'despite', 'lack', 'gap', 'issue'])
        future_work  = self._find_best(parts, ['future', 'will', 'plan', 'next', 'extend',
                                                'promising', 'open question', 'direction'])

        # Smart fallbacks: use actual abstract content, never generic placeholders
        if not methodology:
            methodology = parts[0] if parts else "See abstract"
        if not dataset:
            dataset = "Theoretical/survey — no specific dataset mentioned in abstract"
        if not key_results:
            # Use the last clause as conclusion
            key_results = parts[-1] if len(parts) > 1 else parts[0] if parts else "See summary above"
        if not limitations:
            limitations = "No explicit limitations stated in abstract"
        if not future_work:
            future_work = "Not specified in abstract"

        return {
            "methodology": methodology[:130],
            "dataset": dataset[:130],
            "key_results": key_results[:130],
            "limitations": limitations[:130],
            "future_work": future_work[:130]
        }

    def _get_all_parts(self, text):
        """Split abstract into sentences AND sub-clauses for short/single-sentence abstracts."""
        # First split by sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 15]

        all_parts = list(sentences)

        # If very few sentences, also split by clause markers
        if len(sentences) <= 2:
            for s in sentences:
                clauses = re.split(
                    r',\s*(?:and\s+(?:we|it|the|this|our)|but\s+(?:we|it)|which\s+(?:we|is|are|may)|'
                    r'conclude\s+|explore\s+|evaluate\s+|show\s+)',
                    s, flags=re.IGNORECASE
                )
                for c in clauses:
                    c = c.strip()
                    if len(c) > 15 and c not in all_parts:
                        all_parts.append(c)

        return all_parts

    def _find_best(self, parts, keywords):
        """Return the first clause/sentence containing any of the keywords."""
        for part in parts:
            low = part.lower()
            if any(kw in low for kw in keywords):
                return part
        return None

    # ─────────────────────────────────────────────
    # 3.  CHAT — question-type-aware answers
    # ─────────────────────────────────────────────
    def answer_question(self, title, abstract, question):
        parts = self._get_all_parts(abstract)
        q = question.lower()

        # ── Route by question type ─────────────────
        if any(w in q for w in ['method', 'how', 'approach', 'technique', 'algorithm', 'architecture', 'work']):
            ans = self._find_best(parts, ['propose', 'present', 'attempt', 'define', 'introduce',
                                           'develop', 'use', 'apply', 'approach', 'method', 'framework'])
            if ans:
                return f"**Methodology**: {ans}"
            return f"The paper '{title}' focuses on: {parts[0] if parts else abstract[:200]}"

        elif any(w in q for w in ['dataset', 'data', 'train', 'benchmark', 'corpus']):
            ans = self._find_best(parts, ['dataset', 'benchmark', 'corpus', 'data',
                                           'experiment', 'train', 'test', 'evaluated'])
            if ans:
                return f"**Dataset**: {ans}"
            return "This appears to be a theoretical or survey paper — no specific dataset is mentioned in the abstract."

        elif any(w in q for w in ['result', 'performance', 'accuracy', 'achieve', 'outperform', 'contribution', 'main', 'novel']):
            ans = self._find_best(parts, ['result', 'achieve', 'outperform', 'improve', 'show',
                                           'demonstrate', 'conclude', 'find', 'propose', 'novel'])
            if ans:
                return f"**Key Result / Contribution**: {ans}"
            return f"The main contribution of this paper is: {parts[-1] if parts else abstract[:200]}"

        elif any(w in q for w in ['limitation', 'problem', 'challenge', 'weakness', 'drawback']):
            ans = self._find_best(parts, ['limitation', 'however', 'challenge', 'drawback',
                                           'fail', 'cannot', 'despite', 'lack'])
            if ans:
                return f"**Limitation**: {ans}"
            return "No explicit limitations are stated in the abstract. Check the full paper's conclusion section."

        elif any(w in q for w in ['future', 'next', 'plan', 'extend', 'direction']):
            ans = self._find_best(parts, ['future', 'will', 'plan', 'next', 'extend', 'promising'])
            if ans:
                return f"**Future Work**: {ans}"
            return "No specific future work is mentioned in the abstract."

        # General fallback — score each clause against the question
        q_words = set(re.findall(r'\w+', q)) - {
            'what', 'is', 'the', 'a', 'of', 'in', 'how', 'why', 'did',
            'does', 'was', 'are', 'this', 'that', 'it', 'be', 'to', 'for', 'which'
        }
        best, best_score = (parts[0] if parts else abstract[:200]), 0
        for part in parts:
            score = sum(1 for w in q_words if w in part.lower())
            if score > best_score:
                best, best_score = part, score

        return f"{best} (extracted from abstract)"


# Global singleton
summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        summarizer = Summarizer()
    return summarizer
