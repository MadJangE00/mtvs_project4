# # app/routers/worlds.py

# from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
# from sqlalchemy.orm import Session
# from typing import List, Optional

# from .. import crud, models, schemas, database # 경로에 맞게 조정
# # from ..auth import get_current_active_user

# router = APIRouter(
#     prefix="/works/{work_id}", # 모든 경로는 특정 work_id에 종속
#     tags=["worlds"], # Swagger UI 태그
# )


# # POST /works/{work_id}/worlds/ - 새 세계관 추가
# @router.post(
#     "/worlds",
#     response_model=schemas.World,
#     status_code=status.HTTP_201_CREATED,
#     summary="특정 작품에 새로운 세계관 추가",
# )
# def create_world_for_work_route(
#     work_id: int = Path(..., description="세계관을 추가할 작품의 ID"),
#     *,
#     world_data: schemas.WorldCreate,
#     db: Session = Depends(database.get_db),
#     # current_user: models.User = Depends(get_current_active_user) # TODO: 인증 및 작품 소유권 확인
# ):
#     # 1. 작품 존재 여부 확인
#     db_work = crud.works.get_work_by_id(db, work_id=work_id) # crud.works.get_work_by_id 필요
#     if not db_work:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다."
#         )
#     # TODO: 인증 및 작품 소유권 확인 로직 (current_user 사용)

#     # 2. 세계관 생성
#     try:
#         created_world = crud.worlds.create_work_world(db=db, work_id=work_id, world_data=world_data)
#         return created_world
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"세계관 추가 중 오류 발생: {str(e)}"
#         )


# # GET /works/{work_id}/worlds/ - 해당 작품의 모든 세계관 조회
# @router.get(
#     "/worlds",
#     response_model=List[schemas.World],
#     summary="특정 작품의 모든 세계관 목록 조회",
# )
# def read_worlds_for_work_route(
#     work_id: int = Path(..., description="세계관 목록을 조회할 작품의 ID"),
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

#     # 2. 세계관 목록 조회
#     worlds_list = crud.worlds.get_worlds_by_work_id(db=db, work_id=work_id)
#     return worlds_list


# # GET /works/{work_id}/worlds/{world_id} - 특정 세계관 조회
# @router.get(
#     "/worlds/{world_id}",
#     response_model=schemas.World,
#     summary="특정 작품의 특정 세계관 상세 정보 조회",
# )
# def read_world_route(
#     work_id: int = Path(..., description="세계관이 속한 작품의 ID"),
#     world_id: int = Path(..., description="조회할 세계관의 ID"),
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

#     # 2. 특정 작품에 속한 세계관 조회
#     db_world = crud.worlds.get_world_by_id_and_work_id(db=db, work_id=work_id, world_id=world_id)
#     if db_world is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"작품 ID {work_id}에 ID가 {world_id}인 세계관을 찾을 수 없습니다."
#         )
#     return db_world


# # PUT /works/{work_id}/worlds/{world_id} - 특정 세계관 정보 수정
# @router.put(
#     "/worlds/{world_id}",
#     response_model=schemas.World,
#     summary="특정 작품의 특정 세계관 정보 수정",
# )
# def update_world_route(
#     work_id: int = Path(..., description="세계관이 속한 작품의 ID"),
#     world_id: int = Path(..., description="수정할 세계관의 ID"),
#     *,
#     world_update_data: schemas.WorldUpdate,
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
#     # TODO: 인증 및 작품 소유권 확인 로직

#     # 2. 수정할 세계관이 해당 작품에 속하는지 확인
#     db_world_to_update = crud.worlds.get_world_by_id_and_work_id(db=db, work_id=work_id, world_id=world_id)
#     if not db_world_to_update:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"수정할 세계관 ID {world_id}를 작품 ID {work_id}에서 찾을 수 없습니다."
#         )

#     # 3. 세계관 정보 업데이트
#     updated_world = crud.worlds.update_world(db=db, world_id=world_id, world_update_data=world_update_data)
#     if updated_world is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"세계관 ID {world_id} 업데이트에 실패했습니다."
#         )
#     return updated_world


# # DELETE /works/{work_id}/worlds/{world_id} - 특정 세계관 삭제
# @router.delete(
#     "/worlds/{world_id}",
#     response_model=Optional[schemas.World],
#     summary="특정 작품의 특정 세계관 삭제",
# )
# def delete_world_route(
#     work_id: int = Path(..., description="세계관이 속한 작품의 ID"),
#     world_id: int = Path(..., description="삭제할 세계관의 ID"),
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
#     # TODO: 인증 및 작품 소유권 확인 로직

#     # 2. 삭제할 세계관이 해당 작품에 속하는지 확인
#     db_world_to_delete = crud.worlds.get_world_by_id_and_work_id(db=db, work_id=work_id, world_id=world_id)
#     if not db_world_to_delete:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"삭제할 세계관 ID {world_id}를 작품 ID {work_id}에서 찾을 수 없습니다."
#         )

#     # 3. 세계관 삭제
#     deleted_world_info = crud.worlds.delete_world(db=db, world_id=world_id)
#     if deleted_world_info is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"세계관 ID {world_id} 삭제에 실패했습니다."
#         )
#     return deleted_world_info
# app/routers/worlds.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
    Body,
)  # Body 추가
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, models, schemas, database  # 경로에 맞게 조정

# OpenSearch CRUD 함수 임포트
from ..crud import opensearch_crud  # opensearch_crud.py가 crud 폴더 내에 있다고 가정

router = APIRouter(
    prefix="/works/{work_id}",  # 모든 경로는 특정 work_id에 종속
    tags=["worlds"],  # Swagger UI 태그
)


# POST /works/{work_id}/worlds/ - 새 세계관 추가
@router.post(
    "/worlds",
    response_model=schemas.World,
    status_code=status.HTTP_201_CREATED,
    summary="특정 작품에 새로운 세계관 추가",
)
def create_world_for_work_route(
    work_id: int = Path(..., description="세계관을 추가할 작품의 ID"),
    world_data: schemas.WorldCreate = Body(...),  # Body 명시
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    try:
        created_world = crud.worlds.create_work_world(
            db=db, work_id=work_id, world_data=world_data
        )

        # RDB에 세계관 생성 성공 후 OpenSearch에 인덱싱 (worlds_content가 있는 경우)
        if created_world and created_world.worlds_content:
            try:
                opensearch_crud.update_opensearch_document_for_world(
                    db, created_world.worlds_id
                )
                print(f"World {created_world.worlds_id} content indexed in OpenSearch.")
            except Exception as os_exc:
                print(
                    f"Error indexing world {created_world.worlds_id} content in OpenSearch: {os_exc}"
                )
                # OpenSearch 인덱싱 실패는 주 RDB 저장 성공을 롤백하지 않음 (로깅 후 계속 진행)

        return created_world
    except Exception as e:
        print(f"Error creating world for work {work_id}: {e}")  # 상세 로깅
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"세계관 추가 중 오류 발생: {str(e)}",
        )


# GET /works/{work_id}/worlds/ - 해당 작품의 모든 세계관 조회
@router.get(
    "/worlds",
    response_model=List[schemas.World],
    summary="특정 작품의 모든 세계관 목록 조회",
)
def read_worlds_for_work_route(
    work_id: int = Path(..., description="세계관 목록을 조회할 작품의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )
    worlds_list = crud.worlds.get_worlds_by_work_id(db=db, work_id=work_id)
    return worlds_list


# GET /works/{work_id}/worlds/{world_id} - 특정 세계관 조회
@router.get(
    "/worlds/{world_id}",
    response_model=schemas.World,
    summary="특정 작품의 특정 세계관 상세 정보 조회",
)
def read_world_route(
    work_id: int = Path(..., description="세계관이 속한 작품의 ID"),
    world_id: int = Path(..., description="조회할 세계관의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )
    db_world = crud.worlds.get_world_by_id_and_work_id(
        db=db, work_id=work_id, world_id=world_id
    )
    if db_world is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"작품 ID {work_id}에 ID가 {world_id}인 세계관을 찾을 수 없습니다.",
        )
    return db_world


# PUT /works/{work_id}/worlds/{world_id} - 특정 세계관 정보 수정
@router.put(
    "/worlds/{world_id}",
    response_model=schemas.World,
    summary="특정 작품의 특정 세계관 정보 수정",
)
def update_world_route(
    work_id: int = Path(..., description="세계관이 속한 작품의 ID"),
    world_id: int = Path(..., description="수정할 세계관의 ID"),
    world_update_data: schemas.WorldUpdate = Body(...),  # Body 명시
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    db_world_to_update = crud.worlds.get_world_by_id_and_work_id(
        db=db, work_id=work_id, world_id=world_id
    )
    if not db_world_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"수정할 세계관 ID {world_id}를 작품 ID {work_id}에서 찾을 수 없습니다.",
        )

    # RDB 업데이트
    updated_world = crud.worlds.update_world(
        db=db, world_id=world_id, world_update_data=world_update_data
    )
    if updated_world is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"세계관 ID {world_id} 업데이트에 실패했습니다.",
        )

    # RDB 업데이트 성공 후 OpenSearch 업데이트
    # worlds_content 필드가 요청에 포함되어 변경되었는지 확인
    content_updated_in_request = False
    if hasattr(world_update_data, "model_fields_set"):  # Pydantic v2
        if "worlds_content" in world_update_data.model_fields_set:
            content_updated_in_request = True
    elif hasattr(world_update_data, "__fields_set__"):  # Pydantic v1
        if "worlds_content" in world_update_data.__fields_set__:
            content_updated_in_request = True
    else:  # 위 방법으로 확인 불가 시, 그냥 항상 업데이트 시도 (또는 None이 아니면 업데이트)
        if (
            world_update_data.worlds_content is not None
        ):  # 요청 스키마에 worlds_content가 Optional[str]일 경우
            content_updated_in_request = True

    if (
        content_updated_in_request
    ):  # worlds_content가 요청에 포함되어 변경되었을 가능성이 있을 때
        try:
            # opensearch_crud.update_opensearch_document_for_world는 내부적으로
            # world_id로 RDB에서 최신 worlds_content를 다시 읽어와서 처리함
            opensearch_crud.update_opensearch_document_for_world(
                db, updated_world.worlds_id
            )
            print(f"World {updated_world.worlds_id} content updated in OpenSearch.")
        except Exception as os_exc:
            print(
                f"Error updating world {updated_world.worlds_id} content in OpenSearch: {os_exc}"
            )
            # OpenSearch 업데이트 실패는 RDB 업데이트 성공을 무효화하지 않음

    return updated_world


# DELETE /works/{work_id}/worlds/{world_id} - 특정 세계관 삭제
@router.delete(
    "/worlds/{world_id}",
    response_model=Optional[schemas.World],
    summary="특정 작품의 특정 세계관 삭제",
)
def delete_world_route(
    work_id: int = Path(..., description="세계관이 속한 작품의 ID"),
    world_id: int = Path(..., description="삭제할 세계관의 ID"),
    db: Session = Depends(database.get_db),
):
    db_work = crud.works.get_work_by_id(db, work_id=work_id)
    if not db_work:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {work_id}인 작품을 찾을 수 없습니다.",
        )

    db_world_to_delete = crud.worlds.get_world_by_id_and_work_id(
        db=db, work_id=work_id, world_id=world_id
    )
    if not db_world_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"삭제할 세계관 ID {world_id}를 작품 ID {work_id}에서 찾을 수 없습니다.",
        )

    # RDB에서 세계관 삭제
    deleted_world_info = crud.worlds.delete_world(db=db, world_id=world_id)
    if deleted_world_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"세계관 ID {world_id} 삭제에 실패했습니다.",
        )

    # RDB 삭제 성공 후 OpenSearch에서 해당 문서 삭제
    # OpenSearch 문서 ID는 "world_{world_id}" 형식으로 가정
    opensearch_doc_id = f"world_{world_id}"
    try:
        opensearch_crud.delete_opensearch_document(opensearch_doc_id)
        print(f"World document {opensearch_doc_id} deleted from OpenSearch.")
    except Exception as os_exc:
        print(
            f"Error deleting world document {opensearch_doc_id} from OpenSearch: {os_exc}"
        )
        # OpenSearch 삭제 실패가 RDB 삭제 성공을 무효화하지 않음

    return deleted_world_info
