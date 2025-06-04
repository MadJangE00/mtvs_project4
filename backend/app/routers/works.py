from fastapi import APIRouter, Depends, HTTPException, Path, status, Body
from sqlalchemy.orm import Session
from typing import List
from ..crud import dialogue_generator  # 대사 생성 함수

# models.py, schemas.py, database.py, crud.py는 프로젝트 구조에 맞게 상대 경로로 import합니다.
# 여기서는 일반적인 상대 경로를 사용합니다.
from .. import (
    crud,
    models,
    schemas,
    database,
)  # crud.works 모듈에 관련 함수가 있다고 가정

router = APIRouter(
    prefix="/works",  # 이 라우터의 모든 경로는 /works 로 시작
    tags=["works"],  # Swagger UI에서 그룹화될 태그
)


# POST /works - 작품 추가
@router.post(
    "/",  # user_id를 경로에서 제거하고, 요청 본문의 WorkCreate 스키마를 통해 받음
    response_model=schemas.Work,
    status_code=status.HTTP_201_CREATED,
    summary="새로운 작품 추가 (기본 정보만)",
)
def create_work(  # 함수 이름 변경 (user_id를 경로에서 받지 않으므로)
    work_data: schemas.WorkCreate,  # user_id 필드가 있는 WorkCreate 사용
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 실제 인증 로직 추가
):
    # 만약 current_user를 사용한다면, work_data.user_id를 current_user.user_id로 설정하거나 검증
    # if current_user:
    #     if work_data.user_id != current_user.user_id:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="자신의 user_id로만 작품을 생성할 수 있습니다.")
    # else: # 인증 없이 user_id를 본문으로 받는 경우 (보안상 주의)
    #     pass

    # (선택적이지만 권장) 요청 본문의 user_id 사용자가 DB에 존재하는지 확인
    db_user = crud.users.get_user_by_id(db, user_id=work_data.user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"사용자 ID '{work_data.user_id}'를 찾을 수 없습니다. 작품을 생성할 수 없습니다.",
        )

    try:
        created_work = crud.works.create_user_work(db=db, work_data=work_data)
        return created_work
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"작품 추가 중 오류 발생: {str(e)}",
        )


# GET /works/{user_id}/user_works - 특정 사용자의 모든 작품 목록 조회
@router.get(
    "/{user_id}/user_works",
    response_model=List[schemas.Work],  # Work 스키마의 리스트
    summary="특정 사용자의 모든 작품 목록 조회",
)
def get_user_works(
    user_id: str = Path(..., description="작품 목록을 조회할 사용자의 ID"),
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 본인/관리자 확인
):
    # TODO: 요청한 user_id가 current_user.user_id와 일치하거나, 관리자 권한이 있는지 확인
    # TODO: 해당 user_id의 사용자가 존재하는지 확인하는 로직 추가 가능 (옵션)
    #       db_user = crud.users.get_user_by_id(db, user_id=user_id)
    #       if not db_user:
    #           raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")

    try:
        # crud.get_works_by_user_id 함수가 해당 사용자의 모든 작품을 반환한다고 가정
        user_works = crud.works.get_works_by_user_id(db=db, user_id=user_id)
        if not user_works:
            return []  # 작품이 없을 경우 빈 리스트 반환
        return user_works
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 작품 목록 조회 중 오류 발생: {str(e)}",
        )


# GET /works/{work_id}/work - 개별 작품 확인
@router.get(
    "/{work_id}/work",  # 경로를 명확히 하기 위해 /work 추가 (또는 /{work_id} 만 사용도 가능)
    response_model=schemas.Work,
    summary="ID로 개별 작품 상세 정보 조회",
)
def get_work_by_id(
    work_id: int = Path(
        ..., description="조회할 작품의 ID"
    ),  # models.Work.works_id 타입에 맞춰 int 또는 BigInteger
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 소유권/공개 여부 확인
):
    # TODO: 작품이 비공개일 경우, current_user가 소유자인지 또는 접근 권한이 있는지 확인
    try:
        db_work = crud.works.get_work_by_id(db=db, work_id=work_id)
        if not db_work:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
            )
        # TODO: 작품 조회수 증가 로직이 필요하다면 여기에 추가 (increment_work_view_count 등)
        return db_work
    except HTTPException as e:  # 이미 발생한 HTTPException은 그대로 전달
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"작품 조회 중 오류 발생: {str(e)}",
        )


# DELETE /works/{work_id} - 작품 삭제
@router.delete(
    "/{work_id}",
    response_model=schemas.Work,  # 삭제된 작품 정보를 반환하거나, 또는 schemas.Msg 등으로 변경 가능
    summary="ID로 특정 작품 삭제",
)
def delete_work_by_id(
    work_id: int = Path(..., description="삭제할 작품의 ID"),
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 소유권 확인
):
    # TODO: 삭제 전, 해당 work_id의 작품이 current_user의 소유인지 확인하는 로직 필요
    #       db_work_to_delete = crud.works.get_work_by_id_and_user_id(db, work_id=work_id, user_id=current_user.user_id)
    #       if not db_work_to_delete:
    #           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="작품을 삭제할 권한이 없습니다.")

    # 우선 ID로 작품 조회 (소유권 확인은 위 TODO에서 처리 가정)
    db_work_to_delete = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    try:
        # crud.delete_work_by_id 함수가 작품을 삭제하고 삭제된 객체를 반환한다고 가정
        deleted_work = crud.works.delete_work_by_id(db=db, work_id=work_id)
        # 또는 삭제 성공 시 메시지만 반환하거나, status_code=status.HTTP_204_NO_CONTENT 와 빈 응답을 사용할 수 있음
        return deleted_work
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"작품 삭제 중 오류 발생: {str(e)}",
        )


# PUT /works/{work_id}/update_work - 작품 정보 수정
@router.put(
    "/{work_id}/update_work",
    response_model=schemas.Work,
    summary="ID로 특정 작품의 제목 수정",
)
def update_work_title(
    work_id: int = Path(..., description="수정할 작품의 ID"),
    *,  # 이 뒤부터는 키워드 전용 인수
    work_update: schemas.WorkUpdate,  # 이제 키워드 전용
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user)
):
    # ... 함수 본문 ...
    updated_work = crud.works.update_work(
        db=db, work_id=work_id, work_update_data=work_update
    )
    if not updated_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없거나 업데이트에 실패했습니다.",
        )
    return updated_work


# POST /works/{work_id}/generate-dialogue - 작품 정보를 바탕으로 AI 대사 생성
@router.post(
    "/{work_id}/generate-dialogue-with-context",  # 경로 명확화
    response_model=schemas.DialogueResponse,
    summary="DB에서 작품 컨텍스트를 조회하여 AI 대사 생성",
)
async def generate_dialogue_with_context_route(
    work_id: int = Path(..., description="대사를 생성할 작품 ID"),
    request: schemas.DialogueGenerationRequest = Body(
        ..., description="대사 생성 요청 본문 (컨텍스트 ID 포함)"
    ),
    db: Session = Depends(database.get_db),
):
    # 1. 작품 존재 확인 (worlds_content 여기서 가져옴)
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )
    worlds_content_data = (
        db_work.worlds_content
        if hasattr(db_work, "worlds_content")
        else "세계관 정보 없음"
    )

    # 2. 에피소드 내용 조회 (episode_id가 제공된 경우)
    episode_content_data = "에피소드 정보 없음"
    if request.context_ids.episode_id is not None:
        db_episode = (
            crud.episodes.get_episode_by_id_and_work_id(  # crud.episodes 모듈로 가정
                db, work_id=work_id, episode_id=request.context_ids.episode_id
            )
        )
        if not db_episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작품 ID {work_id}에 에피소드 ID {request.context_ids.episode_id}를 찾을 수 없습니다.",
            )
        episode_content_data = (
            db_episode.episode_content
            if hasattr(db_episode, "episode_content")
            else "에피소드 내용 없음"
        )

    # 3. 캐릭터 설정 조회 (character_id가 제공된 경우)
    character_settings_data = "캐릭터 설정 정보 없음"
    if request.context_ids.character_id is not None:
        if hasattr(crud, "characters") and hasattr(
            crud.characters, "get_character_by_id_and_work_id"
        ):
            db_character = crud.characters.get_character_by_id_and_work_id(
                db, work_id=work_id, character_id=request.context_ids.character_id
            )
            if not db_character:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"작품 ID {work_id}에 캐릭터 ID {request.context_ids.character_id}를 찾을 수 없습니다.",
                )
            character_settings_data = (
                db_character.character_settings
                if hasattr(db_character, "character_settings")
                else "캐릭터 설정 없음"
            )
        else:
            print(
                f"Warning: crud.characters.get_character_by_id_and_work_id function not found. Skipping character settings."
            )

    # 4. 스토리 계획 내용 조회 (plan_id가 제공된 경우)
    plan_content_data = "스토리 계획 정보 없음"
    if request.context_ids.plan_id is not None:
        db_plan = (
            crud.plannings.get_planning_by_id_and_work_id(  # crud.plannings 모듈로 가정
                db, work_id=work_id, plan_id=request.context_ids.plan_id
            )
        )
        if not db_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"작품 ID {work_id}에 계획 ID {request.context_ids.plan_id}를 찾을 수 없습니다.",
            )
        plan_content_data = (
            db_plan.plan_content
            if hasattr(db_plan, "plan_content")
            else "스토리 계획 내용 없음"
        )

    # 5. 대사 생성
    try:
        generated_text = dialogue_generator.generate_dialogue_from_context(
            worlds_content=worlds_content_data,
            episode_content=episode_content_data,
            character_settings=character_settings_data,
            plan_content=plan_content_data,
            prompt=request.prompt,
        )
        return schemas.DialogueResponse(
            generated_dialogue=generated_text
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대사 생성 중 오류 발생: {str(e)}",
        )
