import requests
import xml.etree.ElementTree as ET

query = "face recognition deep learning"
params = {
    "search_query": f"all:{query}",
    "start": 0,
    "max_results": 10
}
base_url = "http://export.arxiv.org/api/query?"

print(f"Requesting: {base_url} with params {params}")
response = requests.get(base_url, params=params)
print(f"Status: {response.status_code}")
print(f"Content Length: {len(response.content)}")

if response.status_code == 200:
    root = ET.fromstring(response.content)
    entries = root.findall('{http://www.w3.org/2005/Atom}entry')
    print(f"Found {len(entries)} entries.")
    for i, entry in enumerate(entries[:2]):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        print(f"{i+1}. {title.strip()}")
