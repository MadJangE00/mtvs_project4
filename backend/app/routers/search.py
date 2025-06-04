from fastapi import APIRouter
from app.sbert_model import SBERTEmbedder
from opensearchpy import OpenSearch
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import numpy as np
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
client = OpenSearch(hosts=[{"host": "localhost", "port": 9200}])
embedder = SBERTEmbedder()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SIMILARITY_THRESHOLD = 0.7  # 코사인 유사도 기준

# 이건 테스트용 추후 삭제
@router.get("/search/")
def search(query: str):
    vector = embedder.encode([query])[0]

    script_query = {
        "script_score": {
            "query": {
                "match_all": {}
            },
            "script": {
                "source": "cosineSimilarity(params.query_vector, doc['embedding']) + 1.0",
                "params": {
                    "query_vector": vector.tolist()  # numpy array일 경우 .tolist()로 변환
                }
            }
        }
    }

    response = client.search(index="korean-english-dictionary", body={"query": script_query})
    hits = response["hits"]["hits"]

    if not hits:
        return {"generated": [], "reason": "no_hits"}

    top_score = hits[0]["_score"] - 1.0  # cosineSimilarity 원래 값
    top_sentences = [
        hit["_source"]
        for hit in hits
        if (hit["_score"] - 1.0) > SIMILARITY_THRESHOLD
    ]

    # ✅ 충분히 유사한 문장이 있다면
    if top_sentences:
        return {
            "retrieved": [
                {"form": top_sentences[i]["form"], "usages": top_sentences[i]["usages"]}
                for i in range(len(top_sentences))
            ],
            "reason": "high_similarity",
        }

    # ✅ 유사도가 낮으면 LLM으로 생성
    # response = llm([HumanMessage(content=f"'{query}'와 관련된 단어 또는 문장을 3개 생성해줘. 최대한 의미가 유사하게.")])
    # generated_text = response.content.strip().splitlines()
    # return {"generated": generated_text, "reason": "low_similarity"}

    # 현재는 LLM 생성을 주석 처리해둠
    return {
        "retrieved": [
            top_sentences[0],
            top_sentences[2],
            top_sentences[3],
            top_sentences[4],
        ],
        "reason": "low_similarity",
        "note": "LLM 생성은 주석 처리됨",
    }
