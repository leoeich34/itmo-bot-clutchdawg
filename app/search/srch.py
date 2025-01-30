from googleapiclient.discovery import build
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

def google_search(query, num_results=3):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    res = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=num_results).execute()
    results = []
    if 'items' in res:
        for item in res['items']:
            results.append(item['link'])
    return results