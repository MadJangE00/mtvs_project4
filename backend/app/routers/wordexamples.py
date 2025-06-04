from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from dotenv import load_dotenv, find_dotenv
from ..ai_utils import generate_examples_with_gpt, evaluate_user_example
from .. import crud, models, schemas, database
import os

# 설정값들을 app.config에서 가져옵니다.
from app.config import (
    OPENSEARCH_HOST,
    OPENSEARCH_PORT,
    OPENSEARCH_USER,
    OPENSEARCH_PASSWORD,
    OPENSEARCH_INDEX_NAME,
    EMBEDDING_MODEL_NAME,
    # SIMILARITY_THRESHOLD # get_related_words_knn 에서는 사용 안 함 (RAG 노드에서 사용)
)

from sentence_transformers import SentenceTransformer
from opensearchpy import (
    OpenSearch,
    ConnectionError as OpenSearchConnectionError,
    NotFoundError,
    RequestError,
)

from app.langgraph_logic.graph_builder import compiled_graph
from ..crud.word_examples import bring_exsen

# --- OpenSearch 클라이언트 및 임베딩 모델 초기화 (config 값 사용) ---
embedding_model = None
opensearch_client = None

# OpenSearch 클라이언트에 전달할 hosts 리스트 및 auth 설정
OPENSEARCH_HOSTS_CONFIG = [
    {"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}
]  # config에서 가져온 값 사용
OPENSEARCH_AUTH_CONFIG = (
    (OPENSEARCH_USER, OPENSEARCH_PASSWORD)
    if OPENSEARCH_USER and OPENSEARCH_PASSWORD
    else None
)

try:
    if EMBEDDING_MODEL_NAME:  # 모델 이름이 설정된 경우에만 로드 시도
        print(
            f"Attempting to load embedding model: '{EMBEDDING_MODEL_NAME}' from config."
        )
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print(f"Embedding model '{EMBEDDING_MODEL_NAME}' loaded successfully.")
    else:
        print(
            "Warning: EMBEDDING_MODEL_NAME is not set in config. Embedding model not loaded."
        )

    if OPENSEARCH_HOST:  # 호스트 정보가 있을 때만 연결 시도
        print(
            f"Attempting to connect to OpenSearch at {OPENSEARCH_HOSTS_CONFIG} "
            f"with user '{OPENSEARCH_USER if OPENSEARCH_USER else 'N/A'}'"
        )
        opensearch_client = OpenSearch(
            hosts=OPENSEARCH_HOSTS_CONFIG,
            http_auth=OPENSEARCH_AUTH_CONFIG,
            use_ssl=False,  # 필요에 따라 True 및 관련 설정 (ca_certs 등) 추가
            verify_certs=False,
            timeout=30,
        )
        if not opensearch_client.ping():
            raise OpenSearchConnectionError(
                "Failed to connect to OpenSearch (ping failed)."
            )
        print("Successfully connected to OpenSearch.")
    else:
        print(
            "Warning: OPENSEARCH_HOST is not set in config. OpenSearch client not initialized."
        )

    if embedding_model and opensearch_client:
        print(
            "RAG components (Embedding Model & OpenSearch Client) initialized successfully for k-NN."
        )
    else:
        print("Warning: One or more RAG components for k-NN could not be initialized.")


except OpenSearchConnectionError as e:
    print(f"Error connecting to OpenSearch: {e}")
    opensearch_client = None
except Exception as e:
    import traceback

    print(f"Error initializing RAG components for k-NN: {e}")
    traceback.print_exc()  # 더 자세한 에러 로그
    embedding_model = None  # 임베딩 모델 로드 중 에러 발생 시 None으로 설정
    opensearch_client = None


router = APIRouter(
    prefix="/words",  # 이 라우터의 모든 경로는 /words 로 시작
    tags=["words"],  # Swagger UI에서 그룹화될 태그
)


# 특정 단어의 모든 예문 조회
# @router.get(
#     "/{user_id}/{word_name}/get_examples",  # 경로에 user_id 추가 (사용자별 단어 이름 조회 가정)
#     response_model=List[schemas.WordExample],
#     summary="특정 사용자의 특정 단어 이름에 대한 모든 예문(용례) 조회",
# )
# def read_examples_for_word_by_name(  # 함수 이름도 약간 변경하여 명확화
#     user_id: str = Path(..., description="단어를 소유한 사용자의 ID"),  # user_id 추가
#     word_name: str = Path(
#         ..., description="예문을 조회할 단어의 이름"
#     ),  # word_id -> word_name
#     db: Session = Depends(database.get_db),
#     # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 실제 사용자 ID 사용
# ):
#     # 1. user_id와 word_name으로 단일 Word 객체를 가져옵니다.
#     # (crud.py에 get_word_by_name_and_user 함수가 있다고 가정)
#     db_word = crud.words.get_word_by_name_and_user(
#         db, user_id=user_id, word_name=word_name
#     )
#     if not db_word:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"사용자 ID '{user_id}'에게 '{word_name}'이라는 단어를 찾을 수 없습니다.",
#         )

#     # 단어 조회 성공 시 word_count 증가
#     # (이 부분은 선택 사항입니다. 예문 조회 시에도 카운트를 올릴지 결정 필요)
#     try:
#         crud.words.increment_word_count_atomic(db, word_id=db_word.words_id)
#     except Exception as e:
#         # print(f"Error incrementing word count for word_id {db_word.words_id} during example read: {e}")
#         pass


#     # 2. word_examples 테이블에서 특정 words_id에 해당하는 모든 예문을 가져옵니다.
#     examples = crud.words.get_word_examples_by_word_id(db, word_id=db_word.words_id)
#     return examples
@router.get(
    "/{user_id}/{word_id}/get_examples",  # 경로 변경: word_name -> word_id
    response_model=List[schemas.WordExample],
    summary="특정 사용자의 특정 단어 ID에 대한 모든 예문(용례) 조회",  # Summary 수정
)
def read_examples_for_word_by_id(  # 함수 이름 변경
    user_id: str = Path(..., description="단어를 소유한 사용자의 ID"),
    word_id: int = Path(
        ..., description="예문을 조회할 단어의 ID"
    ),  # word_name -> word_id, 타입 int로 변경
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 실제 사용자 ID 사용
):
    # 1. word_id로 단일 Word 객체를 가져옵니다.
    # (crud.py에 get_word_by_id 함수가 있다고 가정)
    db_word = crud.words.get_word_by_id(db, word_id=word_id)

    # 1a. 단어가 존재하지 않거나, 해당 사용자의 단어가 아닌 경우 오류 처리
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {word_id}인 단어를 찾을 수 없습니다.",  # 오류 메시지 수정
        )
    # 1b. (중요) 조회된 단어의 user_id와 경로로 받은 user_id가 일치하는지 확인
    #     실제 인증 시스템에서는 current_user.user_id 와 db_word.user_id를 비교해야 합니다.
    #     여기서는 경로로 받은 user_id를 사용합니다.
    if db_word.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # 또는 404 NOT FOUND
            detail=f"사용자 ID '{user_id}'는 ID가 {word_id}인 단어에 접근할 권한이 없습니다.",
        )

    # 단어 조회 성공 시 word_count 증가 (선택 사항)
    # 이 로직은 예문 조회 시에도 word_count를 증가시킬지 여부에 따라 유지하거나 제거합니다.
    try:
        # db_word.words_id는 word_id와 동일합니다.
        crud.words.increment_word_count_atomic(db, word_id=db_word.words_id)
    except Exception as e:
        # print(f"Error incrementing word count for word_id {db_word.words_id} during example read: {e}")
        pass  # 실패해도 예문 조회는 계속 진행

    # 2. word_examples 테이블에서 특정 words_id에 해당하는 모든 예문을 가져옵니다.
    # db_word.words_id는 조회된 단어의 PK이므로, 이를 사용합니다.
    examples = crud.words.get_word_examples_by_word_id(db, word_id=db_word.words_id)
    return examples


# 단어별 예문 추가 (기존 코드 스타일 반영)
@router.post(
    "/{word_id}/examples",  # 경로 변경: /words/{word_id}/examples
    response_model=schemas.WordExample,  # 응답 모델 변경 (WordExample이 Usage 역할)
    status_code=status.HTTP_201_CREATED,
    summary="특정 단어에 예문(용례) 추가",
)
def add_example_to_word(  # 함수 이름 변경 (add_usage_to_word -> add_example_to_word)
    example_data: schemas.WordExampleCreate,  # 요청 본문 스키마 변경
    word_id: int = Path(..., description="예문을 추가할 단어의 ID"),
    # user_id_in_body: str = Body(..., alias="user_id"), # 만약 본문에 user_id를 계속 받아야 한다면
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증된 사용자 정보
):
    # 1. 단어 존재 여부 확인 (그리고 해당 사용자의 단어인지도 확인해야 함)
    # TODO: current_user.user_id를 사용하여 해당 사용자의 단어인지 확인
    #       db_word = crud.get_word_by_id_and_user_id(db, word_id=word_id, user_id=current_user.user_id)
    #       만약 요청 본문에 user_id를 받는다면, current_user.user_id와 body의 user_id가 일치하는지도 확인해야 함.
    db_word = crud.words.get_word_by_id(db, word_id=word_id)  # 우선 ID로 단어 조회
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {word_id}인 단어를 찾을 수 없습니다.",
        )

    # (선택적 검증) 만약 요청 본문에 user_id를 받고, 그것이 단어 소유자와 일치해야 한다면:
    # if hasattr(example_data, 'user_id') and db_word.user_id != example_data.user_id:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="요청된 사용자 ID가 단어 소유자와 일치하지 않습니다.")

    try:
        # crud.create_word_example 함수는 word_id와 example_create 스키마를 받는다고 가정
        created_example = crud.words.create_word_example(
            db=db,
            word_id=db_word.words_id,  # Word 모델의 PK 컬럼명 (words_id로 가정)
            example_create=example_data,
        )
        return created_example
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예문 추가 중 오류 발생: {str(e)}",
        )


# 단어별 예문 수정
@router.put(
    "/{word_id}/examples/{example_sequence}",
    response_model=schemas.WordExample,
    summary="특정 단어의 특정 예문 수정",
)
def update_word_example_endpoint(  # 함수 이름 명확화
    word_id: int = Path(..., description="예문이 속한 단어의 ID"),
    example_sequence: int = Path(..., description="수정할 예문의 시퀀스 번호"),
    example_update_data: schemas.WordExampleUpdate = Body(...),  # 요청 본문 스키마
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증
):
    # 1. 단어 존재 여부 확인
    db_word = crud.words.get_word_by_id(db, word_id=word_id)
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {word_id}인 단어를 찾을 수 없습니다.",
        )

    # TODO: if current_user.user_id != db_word.user_id: (권한 확인)
    #       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="이 단어의 예문을 수정할 권한이 없습니다.")

    # 2. 해당 단어에 속한 특정 예문 조회
    # WordExample의 PK는 (words_id, example_sequence) 복합키
    db_example = crud.word_examples.get_word_example_by_ids(
        db, word_id=word_id, example_sequence=example_sequence
    )
    if not db_example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"단어 ID {word_id}에 시퀀스 번호 {example_sequence}인 예문을 찾을 수 없습니다.",
        )

    # 3. 예문 업데이트
    try:
        updated_example = crud.word_examples.update_word_example(
            db=db, db_example=db_example, example_update_data=example_update_data
        )
        return updated_example
    except Exception as e:
        # 구체적인 예외 처리가 필요할 수 있음
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예문 수정 중 오류 발생: {str(e)}",
        )


# 단어별 예문 삭제
@router.delete(
    "/{word_id}/examples/{example_sequence}",
    response_model=Optional[schemas.WordExample],  # 삭제된 객체 또는 메시지 반환
    # 또는 response_model=schemas.Msg,
    # 또는 status_code=status.HTTP_204_NO_CONTENT 로 하고 response_model=None
    summary="특정 단어의 특정 예문 삭제",
)
def delete_word_example_endpoint(
    word_id: int = Path(..., description="예문이 속한 단어의 ID"),
    example_sequence: int = Path(..., description="삭제할 예문의 시퀀스 번호"),
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증
):
    # 1. 단어 존재 여부 확인
    db_word = crud.words.get_word_by_id(db, word_id=word_id)
    if not db_word:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {word_id}인 단어를 찾을 수 없습니다.",
        )

    # TODO: if current_user.user_id != db_word.user_id: (권한 확인)
    #       raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="이 단어의 예문을 삭제할 권한이 없습니다.")

    # 2. 해당 단어에 속한 특정 예문 조회
    # WordExample 모델의 PK는 (words_id, example_sequence) 복합키
    db_example = crud.word_examples.get_word_example_by_ids(  # crud.words 또는 crud.word_examples 모듈 확인
        db, word_id=word_id, example_sequence=example_sequence
    )
    if not db_example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"단어 ID {word_id}에 시퀀스 번호 {example_sequence}인 예문을 찾을 수 없습니다.",
        )

    # 3. 예문 삭제
    try:
        # Pydantic V2: model_validate 사용 (from_orm 대신)
        # 삭제 전에 데이터를 복사하여 반환하기 위함 (선택적)
        deleted_example_data = schemas.WordExample.model_validate(db_example)

        # CRUD 함수 호출 (모듈 경로 확인: crud.words 또는 crud.word_examples)
        crud.word_examples.delete_word_example(
            db=db, db_example=db_example
        )  # 예시: crud.words에 있다고 가정

        # 옵션 1: 삭제된 객체 정보 반환 (클라이언트에서 활용 가능)
        return deleted_example_data

        # 옵션 2: 204 No Content 반환 (반환할 내용 없음)
        # response_model=None 으로 API 데코레이터 수정 필요
        # return Response(status_code=status.HTTP_204_NO_CONTENT)

        # 옵션 3: 간단한 성공 메시지 반환
        # response_model=schemas.Msg 로 API 데코레이터 수정 필요
        # return schemas.Msg(message=f"단어 ID {word_id}의 예문(seq: {example_sequence})이 성공적으로 삭제되었습니다.")

    except Exception as e:
        # 구체적인 예외 처리가 필요할 수 있음
        # 예: 어떤 CRUD 함수가 실패했는지 등
        import traceback

        traceback.print_exc()  # 개발 중 상세 오류 확인
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예문 삭제 중 오류 발생: {str(e)}",
        )
