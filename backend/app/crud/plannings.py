# app/crud/plannings.py

from sqlalchemy.orm import Session
from typing import List, Optional

# models.py와 schemas.py는 프로젝트 구조에 맞게 import
# 이 파일(plannings.py)은 crud 디렉토리 안에 있으므로,
# 상위 디렉토리(app)에 있는 models.py와 schemas.py를 참조하려면 '..'를 사용합니다.
from .. import models, schemas


def get_planning_by_id(db: Session, plan_id: int) -> Optional[models.Planning]:
    """
    플랜 ID로 특정 플랜을 조회합니다.
    """
    return db.query(models.Planning).filter(models.Planning.plan_id == plan_id).first()


def get_planning_by_id_and_work_id(
    db: Session, work_id: int, plan_id: int
) -> Optional[models.Planning]:
    """
    작품 ID와 플랜 ID로 특정 플랜을 조회합니다.
    (해당 작품에 속한 플랜인지 확인용)
    """
    return (
        db.query(models.Planning)
        .filter(models.Planning.plan_id == plan_id, models.Planning.works_id == work_id)
        .first()
    )


def get_plannings_by_work_id(
    db: Session, work_id: int
) -> List[models.Planning]:
    """
    특정 작품 ID에 속한 모든 플랜 목록을 조회합니다 (페이지네이션 지원).
    """
    return (
        db.query(models.Planning)
        .filter(models.Planning.works_id == work_id)
        .all()
    )


def create_work_planning(
    db: Session, work_id: int, planning_data: schemas.PlanningCreate
) -> models.Planning:
    """
    특정 작품(work_id)에 새로운 플랜을 생성합니다.
    """
    db_planning = models.Planning(
        works_id=work_id,
        plan_title=planning_data.plan_title,
        plan_content=planning_data.plan_content,
    )
    db.add(db_planning)
    db.commit()
    db.refresh(db_planning)
    return db_planning


def update_planning(
    db: Session, plan_id: int, planning_update_data: schemas.PlanningUpdate
) -> Optional[models.Planning]:
    """
    특정 플랜 ID의 정보를 수정합니다.
    """
    db_planning = get_planning_by_id(db, plan_id=plan_id)  # 먼저 ID로 플랜을 찾음
    if not db_planning:
        return None  # 플랜이 없으면 None 반환

    update_data = planning_update_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_planning, key):
            setattr(db_planning, key, value)

    db.commit()
    db.refresh(db_planning)
    return db_planning


def delete_planning(db: Session, plan_id: int) -> Optional[models.Planning]:
    """
    특정 플랜 ID의 플랜을 삭제합니다.
    """
    db_planning = get_planning_by_id(db, plan_id=plan_id)  # 먼저 ID로 플랜을 찾음
    if not db_planning:
        return None  # 플랜이 없으면 None 반환

    # 삭제된 객체의 정보를 반환하고 싶다면, Pydantic 모델로 변환 후 삭제
    # Pydantic v2: planning_data_to_return = schemas.Planning.model_validate(db_planning)
    # Pydantic v1: planning_data_to_return = schemas.Planning.from_orm(db_planning)

    db.delete(db_planning)
    db.commit()
    # return planning_data_to_return # 변환된 Pydantic 객체 반환
    return db_planning  # 또는 SQLAlchemy 객체 반환 (세션 만료 후 주의)
    # 또는 단순히 True (성공) 반환도 가능
