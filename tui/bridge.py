import requests

HOSTNAME = "http://localhost:5000"

def list_articles(limit:int=10, offset:int=0):
    r = requests.get(f"{HOSTNAME}/api/articles", params={
        "limit": limit,
        "offset": offset
    })

    return r.json()

def get_article(id:int):
    r = requests.get(f"{HOSTNAME}/api/article/1")
    return r.json()