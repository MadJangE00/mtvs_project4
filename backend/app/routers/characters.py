# from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, Body
# from sqlalchemy.orm import Session
# from typing import List, Optional

# # 프로젝트 구조에 맞게 crud, models, schemas, database를 import 합니다.
# # 이 파일(app/routers/characters.py)에서 crud 패키지 내의 characters 모듈을 사용합니다.
# from .. import crud, models, schemas, database
# # from ..auth import get_current_active_user # 실제 인증 함수 경로

# router = APIRouter(
#     prefix="/works/{work_id}", # 모든 경로는 특정 work_id에 종속됨
#     tags=["characters"], # Swagger UI 태그
# )


# # POST /works/{work_id}/characters/ - 새 캐릭터 추가 (요청하신 "POST character"에 해당)
# @router.post(
#     "/characters",  # POST 요청은 이 라우터의 prefix에 대한 루트 ("/")로 매핑됩니다.
#     response_model=schemas.Character,
#     status_code=status.HTTP_201_CREATED,
#     summary="특정 작품에 새로운 캐릭터 추가",
# )
# def create_character_for_work_route(
#     work_id: int = Path(..., description="캐릭터를 추가할 작품의 ID"),
#     *,
#     character_data: schemas.CharacterCreate, # 요청 본문은 CharacterCreate 스키마 사용
#     db: Session = Depends(database.get_db),
#     # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 소유권 확인
# ):
#     # 1. 작품 존재 여부 확인 (소유권 확인은 인증 구현 후 추가)
#     db_work = crud.works.get_work_by_id(db, work_id=work_id) # crud.works.get_work_by_id 필요
#     if not db_work:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
#         )
#     # TODO: if current_user and db_work.user_id != current_user.user_id:
#     #           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한 없음")

#     # 2. 캐릭터 생성
#     try:
#         created_character = crud.characters.create_work_character(
#             db=db, work_id=work_id, character=character_data
#         )
#         return created_character
#     except Exception as e: # CRUD 계층에서 발생할 수 있는 다른 예외 처리
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"캐릭터 추가 중 오류 발생: {str(e)}"
#         )


# # GET /works/{work_id}/characters/ - 해당 작품의 모든 캐릭터 조회
# @router.get(
#     "/characters",
#     response_model=List[schemas.Character],
#     summary="특정 작품의 모든 캐릭터 목록 조회",
# )
# def read_characters_for_work_route(
#     work_id: int = Path(..., description="캐릭터 목록을 조회할 작품의 ID"),
#     skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
#     limit: int = Query(100, ge=1, le=200, description="반환할 최대 항목 수"),
#     db: Session = Depends(database.get_db),
#     # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 접근 권한 확인
# ):
#     # 1. 작품 존재 여부 확인
#     db_work = crud.works.get_work_by_id(db, work_id=work_id)
#     if not db_work:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
#         )
#     # TODO: 작품 접근 권한 확인 (예: 공개 작품이거나, current_user가 소유자)

#     # 2. 캐릭터 목록 조회
#     characters_list = crud.characters.get_characters_by_work_id(
#         db=db, work_id=work_id, skip=skip, limit=limit
#     )
#     return characters_list


# # GET /works/{work_id}/characters/{character_id} - 특정 캐릭터 조회
# @router.get(
#     "/characters/{character_id}",
#     response_model=schemas.Character,
#     summary="특정 작품의 특정 캐릭터 상세 정보 조회",
# )
# def read_character_route(
#     work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
#     character_id: int = Path(..., description="조회할 캐릭터의 ID"),
#     db: Session = Depends(database.get_db),
#     # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 접근 권한 확인
# ):
#     # 1. 작품 존재 여부 확인
#     db_work = crud.works.get_work_by_id(db, work_id=work_id)
#     if not db_work:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
#         )
#     # TODO: 작품 접근 권한 확인

#     # 2. 특정 작품에 속한 캐릭터 조회
#     db_character = crud.characters.get_character_by_id_and_work_id(
#         db=db, work_id=work_id, character_id=character_id
#     )
#     if db_character is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"작품 ID {work_id}에 ID가 {character_id}인 캐릭터를 찾을 수 없습니다."
#         )
#     return db_character


# # PUT /works/{work_id}/characters/{character_id} - 특정 캐릭터 정보 수정
# @router.put(
#     "characters/{character_id}",
#     response_model=schemas.Character,
#     summary="특정 작품의 특정 캐릭터 정보 수정",
# )
# def update_character_route(
#     work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
#     character_id: int = Path(..., description="수정할 캐릭터의 ID"),
#     *,
#     character_update: schemas.CharacterUpdate, # 요청 본문은 CharacterUpdate 스키마 사용
#     db: Session = Depends(database.get_db),
#     # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 소유권 확인
# ):
#     # 1. 작품 존재 여부 및 소유권 확인
#     db_work = crud.works.get_work_by_id(db, work_id=work_id)
#     if not db_work:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
#         )
#     # TODO: if current_user and db_work.user_id != current_user.user_id:
#     #           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한 없음")

#     # 2. 수정할 캐릭터가 해당 작품에 속하는지 확인 (get_character_by_id_and_work_id 사용)
#     db_character_to_update = crud.characters.get_character_by_id_and_work_id(
#         db=db, work_id=work_id, character_id=character_id
#     )
#     if not db_character_to_update:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"수정할 캐릭터 ID {character_id}를 작품 ID {work_id}에서 찾을 수 없습니다."
#         )

#     # 3. 캐릭터 정보 업데이트
#     updated_character = crud.characters.update_character(
#         db=db, character_id=character_id, character_update=character_update
#     )
#     # crud.characters.update_character 내부에서 character_id로 다시 조회하므로,
#     # 위에서 db_character_to_update를 찾았다면 updated_character는 None이 아닐 것임 (이론상)
#     if updated_character is None: # 이중 확인 또는 crud 함수가 다르게 동작할 경우 대비
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, # 또는 500, 상황에 따라
#             detail=f"캐릭터 ID {character_id} 업데이트에 실패했습니다."
#         )
#     return updated_character


# # DELETE /works/{work_id}/characters/{character_id} - 특정 캐릭터 삭제
# @router.delete(
#     "characters/{character_id}",
#     response_model=Optional[schemas.Character],  # 삭제된 객체 또는 메시지 반환 가능
#     # status_code=status.HTTP_204_NO_CONTENT, # 내용 없이 성공만 알릴 경우
#     summary="특정 작품의 특정 캐릭터 삭제",
# )
# def delete_character_route(
#     work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
#     character_id: int = Path(..., description="삭제할 캐릭터의 ID"),
#     db: Session = Depends(database.get_db),
#     # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 소유권 확인
# ):
#     # 1. 작품 존재 여부 및 소유권 확인
#     db_work = crud.works.get_work_by_id(db, work_id=work_id)
#     if not db_work:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
#         )
#     # TODO: if current_user and db_work.user_id != current_user.user_id:
#     #           raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="권한 없음")

#     # 2. 삭제할 캐릭터가 해당 작품에 속하는지 확인
#     db_character_to_delete = crud.characters.get_character_by_id_and_work_id(
#         db=db, work_id=work_id, character_id=character_id
#     )
#     if not db_character_to_delete:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"삭제할 캐릭터 ID {character_id}를 작품 ID {work_id}에서 찾을 수 없습니다."
#         )

#     # 3. 캐릭터 삭제
#     deleted_character_info = crud.characters.delete_character(db=db, character_id=character_id)
#     if deleted_character_info is None: # crud 함수가 삭제 실패 시 None을 반환한다면
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, # 또는 500
#             detail=f"캐릭터 ID {character_id} 삭제에 실패했습니다."
#         )

#     # 삭제 성공 시, 삭제된 객체 정보나 성공 메시지를 반환할 수 있음
#     # 또는 HTTP 204 No Content를 사용하고 응답 본문을 비울 수 있음 (이 경우 response_model=None)
#     return deleted_character_info # crud.characters.delete_character의 반환값에 따라 달라짐


# routers/characters.py (또는 실제 라우터 파일)

import os  # 필요시
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Body,
    status,
    Query,
)  # Query 추가
from sqlalchemy.orm import Session
from typing import List, Optional

# 프로젝트 내부 모듈 임포트
from .. import crud, models, schemas, database

# OpenSearch CRUD 함수 임포트
from ..crud import opensearch_crud  # opensearch_crud.py가 crud 폴더 내에 있다고 가정

# 라우터 파일 상단에 있던 LLM 초기화 등은 이 파일과 직접 관련 없으므로 생략합니다.
# 필요하다면 해당 초기화 코드는 유지합니다.

# router = APIRouter(...) # APIRouter 인스턴스 생성
# 만약 이 코드가 기존 라우터 파일에 추가되는 것이라면, 해당 파일의 router 인스턴스를 사용합니다.
# 여기서는 새로운 router 인스턴스를 만든다고 가정하지 않고,
# 기존 파일에 아래 엔드포인트들이 추가/수정된다고 가정합니다.
# 예시: from .main_router import router (만약 별도 파일에 router가 있다면)

# 이 파일이 app/routers/characters.py 이고, prefix가 "/works/{work_id}" 로 설정된
# 메인 라우터에 include 된다고 가정하고 엔드포인트 경로를 작성합니다.
# router = APIRouter() # 이 파일 내에서 독립적인 라우터로 사용한다면 이렇게 선언

# 만약 이 파일 자체가 특정 prefix를 가진 라우터 모듈이라면:
# router = APIRouter(
#     prefix="/works/{work_id}/characters", # 예시 prefix
#     tags=["characters"]
# )
# 이 경우, 아래 엔드포인트들의 경로는 이 prefix에 상대적으로 정의됩니다.
# 여기서는 제공해주신 코드의 경로 스타일을 따르겠습니다.
router = APIRouter(
    prefix="/works/{work_id}", # 모든 경로는 특정 work_id에 종속됨
    tags=["characters"], # Swagger UI 태그
)


# POST /works/{work_id}/characters/ - 새 캐릭터 추가
@router.post(  # router 변수가 이 파일 스코프 또는 임포트된 스코프에 정의되어 있어야 함
    "/characters",  # 전체 경로 명시 (prefix 방식이 아니라면)
    response_model=schemas.Character,
    status_code=status.HTTP_201_CREATED,
    summary="특정 작품에 새로운 캐릭터 추가",
)
def create_character_for_work_route(
    work_id: int = Path(..., description="캐릭터를 추가할 작품의 ID"),
    character_data: schemas.CharacterCreate = Body(...),  # Body 명시
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    try:
        created_character = crud.characters.create_work_character(
            db=db, work_id=work_id, character=character_data
        )
        # RDB에 캐릭터 생성 성공 후 OpenSearch에 인덱싱 (character_settings가 있는 경우)
        if created_character and created_character.character_settings:
            try:
                # opensearch_crud.py에 정의된 함수 사용
                opensearch_crud.update_opensearch_document_for_character(
                    db, created_character.character_id
                )
                print(
                    f"Character {created_character.character_id} settings indexed in OpenSearch."
                )
            except Exception as os_exc:
                # OpenSearch 인덱싱 실패는 캐릭터 생성 자체를 롤백하지는 않음 (선택 사항)
                # 하지만 로깅은 중요
                print(
                    f"Error indexing character {created_character.character_id} settings in OpenSearch: {os_exc}"
                )
                # 필요하다면 여기서 별도의 오류 처리를 할 수 있으나,
                # 주 기능인 RDB 저장이 성공했으므로 201을 반환할 수 있음.
                # 또는, 인덱싱 실패 시 500 에러를 발생시킬 수도 있음 (엄격한 경우)

        return created_character
    except Exception as e:
        print(f"Error creating character for work {work_id}: {e}")  # 상세 로깅
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"캐릭터 추가 중 오류 발생: {str(e)}",
        )


# GET /works/{work_id}/characters/ - 해당 작품의 모든 캐릭터 조회
@router.get(
    "/characters",  # 전체 경로 명시
    response_model=List[schemas.Character],
    summary="특정 작품의 모든 캐릭터 목록 조회",
)
def read_characters_for_work_route(
    work_id: int = Path(..., description="캐릭터 목록을 조회할 작품의 ID"),
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=200, description="반환할 최대 항목 수"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )
    characters_list = crud.characters.get_characters_by_work_id(
        db=db, work_id=work_id, skip=skip, limit=limit
    )
    return characters_list


# GET /works/{work_id}/characters/{character_id} - 특정 캐릭터 조회
@router.get(
    "/characters/{character_id}",  # 전체 경로 명시
    response_model=schemas.Character,
    summary="특정 작품의 특정 캐릭터 상세 정보 조회",
)
def read_character_route(
    work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
    character_id: int = Path(..., description="조회할 캐릭터의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )
    db_character = crud.characters.get_character_by_id_and_work_id(
        db=db, work_id=work_id, character_id=character_id
    )
    if db_character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {work_id}에 ID가 {character_id}인 캐릭터를 찾을 수 없습니다.",
        )
    return db_character


# PUT /works/{work_id}/characters/{character_id} - 특정 캐릭터 정보 수정
@router.put(
    "/characters/{character_id}",  # 전체 경로 명시
    response_model=schemas.Character,
    summary="특정 작품의 특정 캐릭터 정보 수정",
)
def update_character_route(
    work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
    character_id: int = Path(..., description="수정할 캐릭터의 ID"),
    character_update: schemas.CharacterUpdate = Body(...),  # Body 명시
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    db_character_to_update = crud.characters.get_character_by_id_and_work_id(
        db=db, work_id=work_id, character_id=character_id
    )
    if not db_character_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"수정할 캐릭터 ID {character_id}를 작품 ID {work_id}에서 찾을 수 없습니다.",
        )

    # RDB 업데이트
    updated_character = crud.characters.update_character(
        db=db, character_id=character_id, character_update=character_update
    )
    if updated_character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"캐릭터 ID {character_id} 업데이트에 실패했습니다.",
        )

    # RDB 업데이트 성공 후 OpenSearch 업데이트
    # character_update.character_settings가 None이 아니고 실제 값이 있는 경우,
    # 또는 character_settings가 요청에 포함되었는지 여부로 판단할 수 있음
    # 여기서는 character_update 스키마에 character_settings가 있고,
    # crud.characters.update_character가 이를 반영했다고 가정.
    # updated_character.character_settings 를 기준으로 OpenSearch 업데이트.
    # 또는, character_update.model_fields_set (Pydantic v2) / character_update.__fields_set__ (Pydantic v1)
    # 를 확인하여 character_settings가 명시적으로 요청에 포함되었는지 확인할 수 있음.

    settings_updated_in_request = False
    if hasattr(character_update, "model_fields_set"):  # Pydantic v2
        if "character_settings" in character_update.model_fields_set:
            settings_updated_in_request = True
    elif hasattr(character_update, "__fields_set__"):  # Pydantic v1
        if "character_settings" in character_update.model_fields_set:
            settings_updated_in_request = True
    else:  # 위 방법으로 확인 불가 시, 그냥 항상 업데이트 시도 (또는 None이 아니면 업데이트)
        if (
            character_update.character_settings is not None
        ):  # 요청 스키마에 character_settings가 Optional[str]일 경우
            settings_updated_in_request = True

    if (
        settings_updated_in_request
    ):  # character_settings가 요청에 포함되어 변경되었을 가능성이 있을 때
        try:
            # opensearch_crud.update_opensearch_document_for_character는 내부적으로
            # character_id로 RDB에서 최신 character_settings를 다시 읽어와서 처리함
            opensearch_crud.update_opensearch_document_for_character(
                db, updated_character.character_id
            )
            print(
                f"Character {updated_character.character_id} settings updated in OpenSearch."
            )
        except Exception as os_exc:
            print(
                f"Error updating character {updated_character.character_id} settings in OpenSearch: {os_exc}"
            )
            # OpenSearch 업데이트 실패가 RDB 업데이트 성공을 무효화하지는 않음
            # 필요시 여기서 500 에러 발생 가능

    return updated_character


# DELETE /works/{work_id}/characters/{character_id} - 특정 캐릭터 삭제
@router.delete(
    "/characters/{character_id}",  # 전체 경로 명시
    response_model=Optional[schemas.Character],
    summary="특정 작품의 특정 캐릭터 삭제",
)
def delete_character_route(
    work_id: int = Path(..., description="캐릭터가 속한 작품의 ID"),
    character_id: int = Path(..., description="삭제할 캐릭터의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    db_character_to_delete = crud.characters.get_character_by_id_and_work_id(
        db=db, work_id=work_id, character_id=character_id
    )
    if not db_character_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"삭제할 캐릭터 ID {character_id}를 작품 ID {work_id}에서 찾을 수 없습니다.",
        )

    # RDB에서 캐릭터 삭제
    deleted_character_info = crud.characters.delete_character(
        db=db, character_id=character_id
    )
    if deleted_character_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"캐릭터 ID {character_id} 삭제에 실패했습니다.",
        )

    # RDB 삭제 성공 후 OpenSearch에서 해당 문서 삭제
    # OpenSearch 문서 ID는 "char_{character_id}" 형식으로 가정
    opensearch_doc_id = f"char_{character_id}"
    try:
        opensearch_crud.delete_opensearch_document(opensearch_doc_id)
        print(f"Character document {opensearch_doc_id} deleted from OpenSearch.")
    except Exception as os_exc:
        print(
            f"Error deleting character document {opensearch_doc_id} from OpenSearch: {os_exc}"
        )
        # OpenSearch 삭제 실패가 RDB 삭제 성공을 무효화하지는 않음
        # 필요시 여기서 500 에러 발생 가능

    return deleted_character_info
