from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional

# 프로젝트 구조에 맞게 crud, models, schemas, database를 import 합니다.
# 이 파일(app/routers/characters.py)에서 crud 패키지 내의 characters 모듈을 사용합니다.
from .. import crud, models, schemas, database
# from ..auth import get_current_active_user # 실제 인증 함수 경로

router = APIRouter(
    prefix="/works/{work_id}", # 모든 경로는 특정 work_id에 종속됨
    tags=["characters"], # Swagger UI 태그
)


# POST /works/{work_id}/characters/ - 새 캐릭터 추가 (요청하신 "POST character"에 해당)
@router.post(
    "/characters",  # POST 요청은 이 라우터의 prefix에 대한 루트 ("/")로 매핑됩니다.
    response_model=schemas.Character,
    status_code=status.HTTP_201_CREATED,
    summary="특정 작품에 새로운 캐릭터 추가",
)
def create_character_for_work_route(
    work_id: int = Path(..., description="캐릭터를 추가할 작품의 ID"),
    *,
    character_data: schemas.CharacterCreate, # 요청 본문은 CharacterCreate 스키마 사용
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 소유권 확인
):
    # 1. 작품 존재 여부 확인 (소유권 확인은 인증 구현 후 추가)
    db_work = crud.works.get_work_by_id(db, work_id=work_id) # crud.works.get_work_by_id 필요
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
        )
    # TODO: if current_user and db_work.user_id != current_user.user_id:
    #           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한 없음")

    # 2. 캐릭터 생성
    try:
        created_character = crud.characters.create_work_character(
            db=db, work_id=work_id, character=character_data
        )
        return created_character
    except Exception as e: # CRUD 계층에서 발생할 수 있는 다른 예외 처리
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"캐릭터 추가 중 오류 발생: {str(e)}"
        )


# GET /works/{work_id}/characters/ - 해당 작품의 모든 캐릭터 조회
@router.get(
    "/characters",
    response_model=List[schemas.Character],
    summary="특정 작품의 모든 캐릭터 목록 조회",
)
def read_characters_for_work_route(
    work_id: int = Path(..., description="캐릭터 목록을 조회할 작품의 ID"),
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=200, description="반환할 최대 항목 수"),
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 접근 권한 확인
):
    # 1. 작품 존재 여부 확인
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
        )
    # TODO: 작품 접근 권한 확인 (예: 공개 작품이거나, current_user가 소유자)

    # 2. 캐릭터 목록 조회
    characters_list = crud.characters.get_characters_by_work_id(
        db=db, work_id=work_id, skip=skip, limit=limit
    )
    return characters_list


# GET /works/{work_id}/characters/{character_id} - 특정 캐릭터 조회
@router.get(
    "/characters/{character_id}",
    response_model=schemas.Character,
    summary="특정 작품의 특정 캐릭터 상세 정보 조회",
)
def read_character_route(
    work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
    character_id: int = Path(..., description="조회할 캐릭터의 ID"),
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 접근 권한 확인
):
    # 1. 작품 존재 여부 확인
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
        )
    # TODO: 작품 접근 권한 확인

    # 2. 특정 작품에 속한 캐릭터 조회
    db_character = crud.characters.get_character_by_id_and_work_id(
        db=db, work_id=work_id, character_id=character_id
    )
    if db_character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {work_id}에 ID가 {character_id}인 캐릭터를 찾을 수 없습니다."
        )
    return db_character


# PUT /works/{work_id}/characters/{character_id} - 특정 캐릭터 정보 수정
@router.put(
    "characters/{character_id}",
    response_model=schemas.Character,
    summary="특정 작품의 특정 캐릭터 정보 수정",
)
def update_character_route(
    work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
    character_id: int = Path(..., description="수정할 캐릭터의 ID"),
    *,
    character_update: schemas.CharacterUpdate, # 요청 본문은 CharacterUpdate 스키마 사용
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 소유권 확인
):
    # 1. 작품 존재 여부 및 소유권 확인
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
        )
    # TODO: if current_user and db_work.user_id != current_user.user_id:
    #           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한 없음")

    # 2. 수정할 캐릭터가 해당 작품에 속하는지 확인 (get_character_by_id_and_work_id 사용)
    db_character_to_update = crud.characters.get_character_by_id_and_work_id(
        db=db, work_id=work_id, character_id=character_id
    )
    if not db_character_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"수정할 캐릭터 ID {character_id}를 작품 ID {work_id}에서 찾을 수 없습니다."
        )

    # 3. 캐릭터 정보 업데이트
    updated_character = crud.characters.update_character(
        db=db, character_id=character_id, character_update=character_update
    )
    # crud.characters.update_character 내부에서 character_id로 다시 조회하므로,
    # 위에서 db_character_to_update를 찾았다면 updated_character는 None이 아닐 것임 (이론상)
    if updated_character is None: # 이중 확인 또는 crud 함수가 다르게 동작할 경우 대비
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, # 또는 500, 상황에 따라
            detail=f"캐릭터 ID {character_id} 업데이트에 실패했습니다."
        )
    return updated_character


# DELETE /works/{work_id}/characters/{character_id} - 특정 캐릭터 삭제
@router.delete(
    "characters/{character_id}",
    response_model=Optional[schemas.Character],  # 삭제된 객체 또는 메시지 반환 가능
    # status_code=status.HTTP_204_NO_CONTENT, # 내용 없이 성공만 알릴 경우
    summary="특정 작품의 특정 캐릭터 삭제",
)
def delete_character_route(
    work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
    character_id: int = Path(..., description="삭제할 캐릭터의 ID"),
    db: Session = Depends(database.get_db),
    # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 소유권 확인
):
    # 1. 작품 존재 여부 및 소유권 확인
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
        )
    # TODO: if current_user and db_work.user_id != current_user.user_id:
    #           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한 없음")

    # 2. 삭제할 캐릭터가 해당 작품에 속하는지 확인
    db_character_to_delete = crud.characters.get_character_by_id_and_work_id(
        db=db, work_id=work_id, character_id=character_id
    )
    if not db_character_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"삭제할 캐릭터 ID {character_id}를 작품 ID {work_id}에서 찾을 수 없습니다."
        )

    # 3. 캐릭터 삭제
    deleted_character_info = crud.characters.delete_character(db=db, character_id=character_id)
    if deleted_character_info is None: # crud 함수가 삭제 실패 시 None을 반환한다면
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, # 또는 500
            detail=f"캐릭터 ID {character_id} 삭제에 실패했습니다."
        )

    # 삭제 성공 시, 삭제된 객체 정보나 성공 메시지를 반환할 수 있음
    # 또는 HTTP 204 No Content를 사용하고 응답 본문을 비울 수 있음 (이 경우 response_model=None)
    return deleted_character_info # crud.characters.delete_character의 반환값에 따라 달라짐


