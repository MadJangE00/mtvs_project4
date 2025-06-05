from fastapi import FastAPI
from contextlib import asynccontextmanager  # lifespan을 위해 필요
from pathlib import Path
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

# routers 폴더에서 words 모듈 임포트
from .routers import words, works, episodes, characters, worlds, plannings, search, wordexamples
from . import kafka_producer
from .crud.opensearch_crud import create_works_content_index  # 인덱스 생성 함수 임포트
from . import config


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행될 코드
    print("Application startup (lifespan)...")
    print(
        f"Attempting to ensure OpenSearch index '{config.OPENSEARCH_RAG_INDEX_NAME}' exists..."
    )
    try:
        # create_works_content_index 함수는 동기 함수이므로,
        # 비동기 컨텍스트 내에서 직접 호출해도 일반적으로 문제는 없으나,
        # 만약 해당 함수가 매우 오래 걸리는 I/O 작업을 포함하고 있다면
        # asyncio.to_thread (Python 3.9+) 등으로 실행하여 이벤트 루프를 막지 않도록 할 수 있습니다.
        # 현재 opensearch-py 클라이언트가 동기 방식이므로 직접 호출합니다.
        create_works_content_index()
        print(
            f"OpenSearch index '{config.OPENSEARCH_RAG_INDEX_NAME}' check/creation complete."
        )
    except Exception as e:
        print(
            f"!!! Critical Error during OpenSearch index setup on startup (lifespan): {e}"
        )
        # 여기서 애플리케이션 실행을 중단하고 싶다면, 적절한 방법으로 처리
        # 예를 들어, 특정 플래그를 설정하거나, 로깅 후 sys.exit(1) (단, uvicorn 등 서버 프로세스 관리에 영향 줄 수 있음)
        # 여기서는 에러를 출력하고 계속 진행하도록 둡니다.
        # raise # 에러를 다시 발생시켜 FastAPI가 시작되지 않도록 할 수도 있습니다.

    yield  # 애플리케이션이 실행되는 동안 이 지점에서 대기

    # 애플리케이션 종료 시 실행될 코드 (필요하다면)
    print("Application shutdown (lifespan)...")


app = FastAPI(lifespan=lifespan)

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
