import os
from dotenv import load_dotenv, find_dotenv
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from langchain_openai import ChatOpenAI

from .. import crud, models, schemas, database # 경로는 프로젝트 구조에 맞게 조정
from ..llm_service import llm_service
from ..crud.opensearch_crud import search_relevant_documents  # OpenSearch RAG 함수


env_loaded = load_dotenv(find_dotenv(usecwd=True))
if env_loaded:
    print(".env 파일이 성공적으로 로드되었습니다.")
else:
    print("Warning: .env 파일을 찾지 못했습니다.")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME_ENV = os.getenv("MODEL_NAME")

chat_model = None

chat_model = ChatOpenAI(
    temperature=0.1,  # 창의력 지수
    model=MODEL_NAME_ENV,  # .env에서 읽어온 모델명 사용
)
print("========================================")
print(f"Chat model initialized with model: {chat_model.model_name}")

router = APIRouter(
    prefix="/episodes", # 기본 prefix 설정
    tags=["episodes"],
)

# POST /episodes/{work_id}/ - 특정 작품에 새 에피소드 추가
@router.post(
    "/{work_id}/",
    response_model=schemas.Episode,
    status_code=status.HTTP_201_CREATED,
    summary="특정 작품에 새로운 에피소드 추가"
)
def create_episode_for_work(
    work_id: int = Path(..., description="에피소드를 추가할 작품의 ID"),
    *,
    episode_data: schemas.EpisodeCreate, # 요청 본문 파라미터
    # 여기에 다른 경로/쿼리 파라미터가 있다면 먼저 와야 함
    db: Session = Depends(database.get_db), # Depends 파라미터는 뒤로
    # current_user: models.User = Depends(get_current_active_user) # Depends 파라미터는 뒤로
):
    # ... (함수 본문은 이전과 동일)
    # 1. 작품 존재 여부 및 소유권/권한 확인
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.")
    # if current_user and db_work.user_id != current_user.user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="이 작품에 에피소드를 추가할 권한이 없습니다.")

    try:
        created_episode = crud.episodes.create_work_episode(db=db, work_id=work_id, episode_data=episode_data)
        return created_episode
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"에피소드 추가 중 오류 발생: {str(e)}",
        )

# GET (추가 제안) /episodes/{work_id}/ - 특정 작품의 모든 에피소드 목록 조회
@router.get(
    "/{work_id}/",
    response_model=List[schemas.Episode],
    summary="특정 작품의 모든 에피소드 목록 조회"
)
def get_episodes_for_work(
    work_id: int = Path(..., description="에피소드 목록을 조회할 작품의 ID"),
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 접근 권한 확인
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.")
    # TODO: 작품 접근 권한 확인

    episodes_list = crud.episodes.get_episodes_by_work_id(db=db, work_id=work_id)
    return episodes_list


# DELETE /episodes/{work_id}/{episode_id} - 특정 작품의 특정 에피소드 삭제
@router.delete(
    "/{work_id}/{episode_id}",
    response_model=Optional[schemas.Episode], # 또는 schemas.Msg, 또는 None (204 No Content)
    summary="특정 작품의 특정 에피소드 삭제"
)
def delete_episode_from_work(
    work_id: int = Path(..., description="에피소드가 속한 작품의 ID"),
    episode_id: int = Path(..., description="삭제할 에피소드의 ID"),
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품/에피소드 소유권 확인
):
    # 1. 작품 존재 여부 및 소유권/권한 확인
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.")
    # if current_user and db_work.user_id != current_user.user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="이 작품의 에피소드를 삭제할 권한이 없습니다.")

    # 2. 해당 작품에 속한 에피소드인지 확인 후 삭제
    # crud.episodes.delete_episode_by_id_and_work_id 와 같은 함수 필요
    deleted_episode = crud.episodes.delete_episode_by_id_and_work_id(db=db, work_id=work_id, episode_id=episode_id)
    if not deleted_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {work_id}에 ID가 {episode_id}인 에피소드를 찾을 수 없거나 삭제에 실패했습니다."
        )
    return deleted_episode # 또는 성공 메시지


@router.put( # POST 대신 PUT으로 (리소스의 특정 속성 전체 교체 또는 생성)
    "/{work_id}/{episode_id}/episode_content",
    response_model=schemas.Episode,
    summary="특정 에피소드의 내용(content) 설정/수정"
)
def set_episode_content(
    work_id: int = Path(..., description="에피소드가 속한 작품의 ID"),
    episode_id: int = Path(..., description="내용을 설정/수정할 에피소드의 ID"),
    *,
    content_data: schemas.EpisodeContentUpdate, # 요청 본문으로 내용 받기
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 권한 확인
):
    # 1. 작품 및 에피소드 존재, 소유권/권한 확인
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.")
    # if current_user and db_work.user_id != current_user.user_id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="이 작품의 에피소드 내용을 수정할 권한이 없습니다.")

    # crud.episodes.update_episode_content 와 같은 함수 필요
    updated_episode = crud.episodes.update_episode_content(
        db=db,
        work_id=work_id, # work_id도 전달하여 해당 작품의 에피소드인지 추가 확인 가능
        episode_id=episode_id,
        content=content_data.episode_content
    )
    if not updated_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {work_id}에 ID가 {episode_id}인 에피소드를 찾을 수 없거나 내용 업데이트에 실패했습니다."
        )
    return updated_episode


# PUT /episodes/{work_id}/{episode_id}/ai_episode_content - AI 콘텐츠 생성 및 업데이트
@router.put(
    "/{work_id}/{episode_id}/ai_episode_content",
    response_model=schemas.Episode,
    summary="Generate and update AI episode content",
    description="Retrieves existing episode content, generates new/modified content based on it and an additional prompt, and updates the episode's content.",
)
async def generate_and_update_ai_episode_content(
    work_id: int = Path(..., description="The ID of the work"),
    episode_id: int = Path(..., description="The ID of the episode to update"),
    request_body: Optional[schemas.AIEpisodeContentGenerateRequest] = Body(
        None,
        description="Additional prompt for AI content generation",
    ),
    db: Session = Depends(database.get_db),
):
    # 0. AI 모델 사용 가능 여부 확인 (핸들러 시작 시)
    if not chat_model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI model is not available. Please check server configuration.",
        )

    # 1. 기존 에피소드 정보 조회
    db_episode = crud.episodes.get_episode_by_work_and_episode_id(
        db=db, work_id=work_id, episode_id=episode_id
    )
    if not db_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found"
        )

    existing_content = db_episode.episode_content if db_episode.episode_content else ""

    user_additional_prompt = ""
    if request_body and request_body.additional_prompt:
        user_additional_prompt = request_body.additional_prompt

    # 2. LangChain을 사용하여 AI 콘텐츠 생성
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser

    print("AI 모델을 사용하여 콘텐츠 생성 시도...")

    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "당신은 주어진 내용을 바탕으로 창의적이고 흥미로운 에피소드 콘텐츠를 작성하거나 수정하는 AI 작가입니다. 기존 내용을 참고하여 요청에 따라 더 발전된 내용을 생성해주세요.",
            ),
            (
                "human",
                "기존 에피소드 내용:\n"
                "--------------------\n"
                "{existing_content}\n"
                "--------------------\n\n"
                "다음은 이 내용을 바탕으로 추가적으로 고려해야 할 사항 또는 방향입니다 (만약 이 내용이 비어있다면, 기존 내용을 바탕으로 자유롭게 더 흥미롭게 발전시켜주세요):\n"
                "--------------------\n"
                "{additional_prompt}\n"
                "--------------------\n\n"
                "위 정보를 종합하여 새롭거나 수정된 에피소드 콘텐츠를 작성해주세요. 다른 부연 설명 없이, 최종 결과물인 에피소드 콘텐츠 본문만 제공해주세요.",
            ),
        ]
    )
    chain = prompt_template | chat_model | StrOutputParser()

    try:
        generated_or_modified_content = await chain.ainvoke(
            {
                "existing_content": (
                    existing_content if existing_content else "내용 없음"
                ),
                "additional_prompt": (
                    user_additional_prompt
                    if user_additional_prompt
                    else "특별한 추가 요청 없음"
                ),
            }
        )
        print(
            f"AI 모델로부터 생성된 내용 (첫 200자): {generated_or_modified_content[:200]}..."
        )
    except Exception as e:
        print(f"AI 콘텐츠 생성 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI content generation failed: {str(e)}",  # 사용자에게는 간략한 메시지, 서버 로그에는 상세 내용
        )

    # 3. 생성된 콘텐츠 유효성 검사
    if not generated_or_modified_content or not generated_or_modified_content.strip():
        print("AI가 유효한 콘텐츠를 생성하지 못했습니다 (결과가 비어 있음).")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI failed to generate valid content. The response was empty.",
        )

    # 4. DB 업데이트
    updated_db_episode = crud.episodes.update_episode_content(
        db=db,
        work_id=work_id,
        episode_id=episode_id,
        content=generated_or_modified_content,  # CRUD 함수 매개변수명에 맞게 'content' 또는 'new_ai_content' 사용
    )
    if not updated_db_episode:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update episode with new AI content in the database.",
        )

    return updated_db_episode


# GET /episodes/{work_id}/{episode_id} - 특정 작품의 특정 에피소드 상세 조회 (새로 추가된 엔드포인트)
@router.get(
    "/{work_id}/{episode_id}",
    response_model=schemas.Episode,  # 단일 에피소드를 반환하므로 List[]가 아님
    summary="특정 작품의 특정 에피소드 상세 조회",
)
def get_episode_detail_for_work(
    work_id: int = Path(..., description="에피소드가 속한 작품의 ID"),
    episode_id: int = Path(..., description="조회할 에피소드의 ID"),
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품/에피소드 접근 권한 확인
):
    # 1. 작품 존재 여부 확인
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    # TODO: 작품/에피소드 접근 권한 확인
    # 예: if current_user and not user_has_access_to_work(db, user_id=current_user.id, work_id=work_id):
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="이 작품의 에피소드를 조회할 권한이 없습니다.")
    #     또는, 공개 에피소드인지, 구매한 에피소드인지 등의 로직이 필요할 수 있습니다.

    # 2. 해당 작품에 속한 특정 에피소드 조회
    # 이 CRUD 함수는 work_id와 episode_id를 모두 사용하여 정확한 에피소드를 찾고,
    # 해당 에피소드가 실제로 해당 work_id에 속하는지 확인해야 합니다.
    db_episode = crud.episodes.get_episode_by_id_and_work_id(
        db=db, work_id=work_id, episode_id=episode_id
    )

    if not db_episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {work_id}에서 ID가 {episode_id}인 에피소드를 찾을 수 없습니다.",
        )
    return db_episode


router.get(
    "/works/{works_id}/preview_dialogue_with_rag",
    response_model=schemas.EpisodeContentPreview,  # 결과를 보여줄 새로운 스키마 필요
    summary="RAG를 사용하여 생성될 대사 미리보기 (DB 저장 안 함)",
)


async def preview_dialogue_with_rag_endpoint(
    works_id: int = Path(..., description="대사를 생성할 작품의 ID"),
    # GET 요청이므로 요청 본문(Body) 대신 쿼리 파라미터 사용
    user_input_content: str = Query(
        ..., description="생성할 에피소드의 핵심 설명 (사용자 입력)"
    ),
    additional_prompt: Optional[str] = Query(
        None, description="생성을 위한 추가적인 프롬프트 또는 지시사항"
    ),
    db: Session = Depends(
        database.get_db
    ),  # RDB 접근이 필요 없을 수도 있지만, works_id 유효성 검사 등에 사용 가능
):
    # (선택 사항) 작품 존재 여부 확인
    db_work = crud.works.get_work_by_id(db, work_id=works_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {works_id}인 작품을 찾을 수 없습니다.",
        )

    # 1. RAG: OpenSearch에서 관련 문서 검색 (사용자가 입력한 'user_input_content'를 쿼리로 사용)
    relevant_docs = search_relevant_documents(
        query_text=user_input_content,  # 쿼리 파라미터로 받은 내용 사용
        works_id=works_id,
        top_k=5,
    )
    if not relevant_docs:
        print(
            f"No relevant documents found via RAG for works_id {works_id} (preview) using user input content: '{user_input_content}'"
        )

    # 2. LLM 서비스 호출하여 "순수 대사" 생성
    try:
        llm_pure_dialogue = llm_service.generate_dialogue(
            relevant_docs=relevant_docs,
            user_provided_context=user_input_content,  # llm_service의 파라미터명에 맞춤
            additional_prompt=additional_prompt,
        )
    except ValueError as ve:  # llm_service._call_llm에서 발생시킨 ValueError 처리
        print(f"LLM service error during dialogue preview: {ve}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,  # LLM 서비스 문제로 간주
            detail=str(ve),  # LLM 서비스의 에러 메시지 전달
        )
    except Exception as e:
        print(f"Error calling LLM service for dialogue preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM service failed during dialogue preview.",
        )

    if (
        not llm_pure_dialogue
        or ("LLM Error" in llm_pure_dialogue)
        or ("LLM API call failed" in llm_pure_dialogue)
        or not llm_pure_dialogue.strip()
    ):
        # LLM 서비스가 오류 문자열을 반환하는 경우도 처리
        error_detail = "LLM failed to generate valid dialogue content for preview."
        if (
            "LLM Error" in llm_pure_dialogue
            or "LLM API call failed" in llm_pure_dialogue
        ):
            error_detail = llm_pure_dialogue  # 실제 LLM 서비스 에러 메시지 사용

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        )

    # 3. 결과 반환 (DB 저장 안 함)
    #    사용자가 입력한 'user_input_content' (원본 설명 역할)와 생성된 대사를 함께 반환합니다.
    #    이를 위해 새로운 Pydantic 스키마 (예: EpisodeContentPreview)가 필요합니다.
    return schemas.EpisodeContentPreview(
        user_input_content=user_input_content,
        generated_dialogue=llm_pure_dialogue,
        relevant_context_summary=(
            [doc.get("text_content", "") for doc in relevant_docs]
            if relevant_docs
            else ["관련 컨텍스트 없음"]
        ),  # RAG 컨텍스트 요약 (선택 사항)
    )
