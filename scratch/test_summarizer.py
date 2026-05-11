from backend.summarizer import get_summarizer
import torch

test_text = "This is a test abstract about artificial intelligence and its applications in modern healthcare systems to improve patient outcomes."

try:
    print("Initializing summarizer...")
    s = get_summarizer()
    print("Summarizing...")
    res = s.summarize(test_text)
    print(f"Result: {res}")
except Exception as e:
    print(f"FAILED: {e}")
