# app/crud/characters.py

from sqlalchemy.orm import Session
from typing import List, Optional

# models.py와 schemas.py는 프로젝트 구조에 맞게 import
# 이 파일(characters.py)은 crud 디렉토리 안에 있으므로,
# 상위 디렉토리(app)에 있는 models.py와 schemas.py를 참조하려면 '..'를 사용합니다.
from .. import models, schemas


def get_character_by_id(db: Session, character_id: int) -> Optional[models.Character]:
    """
    캐릭터 ID로 특정 캐릭터를 조회합니다.
    """
    return (
        db.query(models.Character)
        .filter(models.Character.character_id == character_id)
        .first()
    )


def get_character_by_id_and_work_id(
    db: Session, work_id: int, character_id: int
) -> Optional[models.Character]:
    """
    작품 ID와 캐릭터 ID로 특정 캐릭터를 조회합니다.
    (해당 작품에 속한 캐릭터인지 확인용)
    """
    return (
        db.query(models.Character)
        .filter(
            models.Character.character_id == character_id,
            models.Character.works_id == work_id,
        )
        .first()
    )


def get_characters_by_work_id(
    db: Session, work_id: int, skip: int = 0, limit: int = 100
) -> List[models.Character]:
    """
    특정 작품 ID에 속한 모든 캐릭터 목록을 조회합니다 (페이지네이션 지원).
    """
    return (
        db.query(models.Character)
        .filter(models.Character.works_id == work_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_work_character(
    db: Session, work_id: int, character: schemas.CharacterCreate
) -> models.Character:
    """
    특정 작품(work_id)에 새로운 캐릭터를 생성합니다.
    """
    db_character = models.Character(
        works_id=work_id,
        character_name=character.character_name,
        character_settings=character.character_settings,
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


def update_character(
    db: Session, character_id: int, character_update: schemas.CharacterUpdate
) -> Optional[models.Character]:
    """
    특정 캐릭터 ID의 정보를 수정합니다.
    수정 전 해당 캐릭터가 존재하는지 get_character_by_id로 확인합니다.
    API 레벨에서는 해당 작품의 캐릭터인지 추가 확인이 필요할 수 있습니다.
    """
    db_character = get_character_by_id(
        db, character_id=character_id
    )  # 먼저 ID로 캐릭터를 찾음
    if not db_character:
        return None  # 캐릭터가 없으면 None 반환

    update_data = character_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_character, key):
            setattr(db_character, key, value)

    db.commit()
    db.refresh(db_character)
    return db_character


def delete_character(db: Session, character_id: int) -> Optional[models.Character]:
    """
    특정 캐릭터 ID의 캐릭터를 삭제합니다.
    삭제 전 해당 캐릭터가 존재하는지 get_character_by_id로 확인합니다.
    API 레벨에서는 해당 작품의 캐릭터인지 추가 확인이 필요할 수 있습니다.
    """
    db_character = get_character_by_id(
        db, character_id=character_id
    )  # 먼저 ID로 캐릭터를 찾음
    if not db_character:
        return None  # 캐릭터가 없으면 None 반환

    # 삭제된 객체의 정보를 반환하고 싶다면, Pydantic 모델로 변환 후 삭제
    # Pydantic v2: character_data_to_return = schemas.Character.model_validate(db_character)
    # Pydantic v1: character_data_to_return = schemas.Character.from_orm(db_character)

    db.delete(db_character)
    db.commit()
    # return character_data_to_return # 변환된 Pydantic 객체 반환
    return db_character  # 또는 SQLAlchemy 객체 반환 (세션 만료 후 주의)
    # 또는 단순히 True (성공) 반환도 가능
