from fastapi import APIRouter
from app.sbert_model import SBERTEmbedder
from opensearchpy import OpenSearch
import numpy as np

router = APIRouter()
client = OpenSearch(hosts=[{"host": "localhost", "port": 9200}])
embedder = SBERTEmbedder()

@router.get("/search/")
def search(query: str):
    vector = embedder.encode([query])[0]
    
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": vector}
            }
        }
    }

    response = client.search(index="korean-texts", body={"query": script_query})
    return [{"score": hit["_score"], "sentence": hit["_source"]["sentence"]} for hit in response["hits"]["hits"]]
