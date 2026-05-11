from backend.recommender import get_search_engine

engine = get_search_engine()
query = "face recognition deep learning"
print(f"Testing search for: {query}")

results = engine.fetch_from_semantic_scholar(query, max_results=5)
print(f"Found {len(results)} results from Semantic Scholar.")

for i, r in enumerate(results):
    print(f"{i+1}. {r['title']}")
