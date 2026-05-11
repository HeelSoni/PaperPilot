from typing import List, Dict
import random

def analyze_trends(topic: str) -> Dict:
    """
    Simulates trend analysis for a topic.
    In production, this would aggregate data from arXiv or Semantic Scholar.
    """
    # Simulate a growth trend for AI topics
    base_count = random.randint(50, 200)
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    trends = []
    
    current_count = base_count
    for year in years:
        growth = random.uniform(1.1, 1.5)
        current_count = int(current_count * growth)
        trends.append({"year": year, "count": current_count})
        
    return {
        "topic": topic,
        "trends": trends
    }
