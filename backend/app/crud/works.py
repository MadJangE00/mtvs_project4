from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from typing import Optional, List
from .. import models, schemas
from sqlalchemy.inspection import inspect
from fastapi import HTTPException


def create_user_work(
    db: Session, work_data: schemas.WorkCreate
) -> models.Work:  # user_id는 WorkCreate 스키마 안에 포함
    """
    새로운 작품(Work)을 생성합니다. 하위 요소는 별도 API로 추가됩니다.
    """
    db_work = models.Work(
        user_id=work_data.user_id,  # WorkCreate 스키마에서 user_id를 받는다고 가정
        works_title=work_data.works_title,
    )
    db.add(db_work)
    db.commit()
    db.refresh(db_work)
    return db_work


def get_works_by_user_id(db: Session, user_id: str) -> List[models.Work]:
    """
    특정 사용자의 모든 작품 목록을 조회합니다.
    """
    return db.query(models.Work).filter(models.Work.user_id == user_id).all()


def get_work_by_id(db: Session, work_id: int) -> Optional[models.Work]:
    """
    작품 ID로 특정 작품을 조회합니다.
    이때 연관된 Characters, Worlds 등도 함께 로드될 수 있도록 relationship 설정이 중요합니다.
    (기본적으로 lazy='select'이므로, 접근 시 추가 쿼리가 발생할 수 있음)
    효율을 위해 joined loading (e.g., options(joinedload(models.Work.characters))) 등을 고려할 수 있습니다.
    """
    return db.query(models.Work).filter(models.Work.works_id == work_id).first()


# 소유권 확인을 위한 함수 (선택적)
def get_work_by_id_and_user_id(
    db: Session, work_id: int, user_id: str
) -> Optional[models.Work]:
    """
    작품 ID와 사용자 ID로 특정 작품을 조회합니다. (소유권 확인용)
    """
    return (
        db.query(models.Work)
        .filter(models.Work.works_id == work_id, models.Work.user_id == user_id)
        .first()
    )


def delete_work_by_id(db: Session, work_id: int) -> Optional[models.Work]:
    """
    작품 ID로 특정 작품을 삭제합니다.
    models.Work에 cascade="all, delete-orphan"이 설정되어 있다면,
    연관된 Characters, Worlds 등도 함께 삭제됩니다.
    """
    db_work = db.query(models.Work).filter(models.Work.works_id == work_id).first()
    if db_work:
        db.delete(db_work)
        db.commit()
        return db_work  # 삭제된 객체의 복사본 반환 (또는 db_work 자체를 반환할 수도 있으나, 세션 만료 후 문제 가능성)
        # 또는 단순히 True/None을 반환하거나, 메시지를 반환할 수도 있음
    return None


def update_work(
    db: Session, work_id: int, work_update_data: schemas.WorkUpdate
) -> Optional[models.Work]:
    """
    작품 ID로 특정 작품의 정보를 수정합니다.
    work_update_data에 제공된 필드(여기서는 works_title)만 업데이트합니다.
    """
    db_work = db.query(models.Work).filter(models.Work.works_id == work_id).first()
    if not db_work:
        return None  # 작품이 없으면 None 반환

    # Pydantic 모델에서 제공된 데이터만 업데이트 (exclude_unset=True)
    update_data = work_update_data.model_dump(exclude_unset=True)

    # update_data 딕셔너리에 있는 키-값 쌍으로 db_work 객체의 속성을 업데이트
    # 현재 WorkUpdate 스키마에는 works_title만 있으므로, 이 루프는 works_title에 대해서만 실행됨
    for key, value in update_data.items():
        if hasattr(db_work, key):  # db_work 객체에 해당 속성이 있는지 확인 (안전장치)
            setattr(db_work, key, value)
        # else:
        # log or handle an attempt to update a non-existent attribute (optional)
        # print(f"Warning: Attribute '{key}' not found in models.Work for update.")

    # db.add(db_work) # SQLAlchemy는 객체의 변경을 감지하므로, 명시적인 add는 필수는 아님. 하지만 상태 변경을 명확히 하기도 함.
    db.commit()
    db.refresh(db_work)  # DB에서 최신 상태로 객체를 갱신
    return db_work
