from fastapi import FastAPI
from pathlib import Path
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

# routers 폴더에서 words 모듈 임포트
from .routers import words, works, episodes, characters, worlds, plannings, search, wordexamples
from . import kafka_producer

# from . import models # 만약 테이블 생성이 필요하다면
# from .database import engine # 만약 테이블 생성이 필요하다면

# .env 파일 로드 (main.py가 app 폴더 내에 있다고 가정)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)  # database.py에서도 로드하지만, 여기서도 확인차
if DATABASE_URL is None:
    print(
        "경고: DATABASE_URL 환경 변수가 .env 파일에 설정되지 않았거나 로드되지 않았습니다."
    )

app = FastAPI()

origins = [
    "http://localhost:3000",  # 프론트엔드 도메인
    "http://192.168.0.75:3000",  # 혹은 IP 주소 버전
    # 필요하다면 다른 도메인 추가 가능
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 출처 리스트
    allow_credentials=True,
    allow_methods=["*"],  # 허용 HTTP 메서드 전체
    allow_headers=["*"],  # 허용 헤더 전체
)


# models.Base.metadata.create_all(bind=engine)

app.include_router(words.router)  
app.include_router(works.router)
app.include_router(episodes.router)
app.include_router(characters.router)
app.include_router(worlds.router)
app.include_router(plannings.router)
app.include_router(search.router)
app.include_router(wordexamples. router)

@app.get("/")
async def root():
    return {"message": "Welcome to Personal Dictionary API"}


# python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
