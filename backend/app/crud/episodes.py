from sqlalchemy.orm import Session
from typing import List, Optional

# models.py와 schemas.py는 프로젝트 구조에 맞게 import
# 예: from .. import models, schemas (만약 crud/episodes.py 라면)
# 예: from . import models, schemas (만약 crud.py 라면)
from .. import models, schemas  # 여기서는 crud 디렉토리의 상위에서 가져온다고 가정


def create_work_episode(
    db: Session, work_id: int, episode_data: schemas.EpisodeCreate
) -> models.Episode:
    """
    특정 작품(work_id)에 새로운 에피소드를 생성합니다.
    """
    # EpisodeCreate 스키마에 episode_content 필드가 있다고 가정
    db_episode = models.Episode(
        works_id=work_id,
        episode_content=episode_data.episode_content,  # 스키마 필드명에 맞게 수정
    )
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode


def get_episodes_by_work_id(db: Session, work_id: int) -> List[models.Episode]:
    """
    특정 작품(work_id)에 속한 모든 에피소드 목록을 조회합니다.
    """
    return db.query(models.Episode).filter(models.Episode.works_id == work_id).all()


def get_episode_by_id_and_work_id(
    db: Session, work_id: int, episode_id: int
) -> Optional[models.Episode]:
    """
    특정 작품(work_id)에 속한 특정 에피소드(episode_id)를 조회합니다.
    삭제나 수정 전에 해당 작품의 에피소드가 맞는지 확인하는 데 사용할 수 있습니다.
    """
    return (
        db.query(models.Episode)
        .filter(
            models.Episode.episode_id == episode_id, models.Episode.works_id == work_id
        )
        .first()
    )


def get_episode_by_work_and_episode_id(
    db: Session, work_id: int, episode_id: int
) -> Optional[models.Episode]:
    """
    주어진 work_id와 episode_id에 해당하는 특정 에피소드를 조회합니다.
    """
    return (
        db.query(models.Episode)
        .filter(
            models.Episode.works_id == work_id, models.Episode.episode_id == episode_id
        )
        .first()
    )


def update_episode_content(
    db: Session, work_id: int, episode_id: int, content: str
) -> Optional[models.Episode]:
    """
    특정 작품(work_id)의 특정 에피소드(episode_id)의 내용(content)을 수정합니다.
    """
    db_episode = get_episode_by_id_and_work_id(
        db, work_id=work_id, episode_id=episode_id
    )
    if not db_episode:
        return None  # 해당 작품의 에피소드가 없으면 None 반환

    db_episode.episode_content = content
    db.commit()
    db.refresh(db_episode)
    return db_episode


def delete_episode_by_id_and_work_id(
    db: Session, work_id: int, episode_id: int
) -> Optional[models.Episode]:
    """
    특정 작품(work_id)의 특정 에피소드(episode_id)를 삭제합니다.
    삭제 성공 시 삭제된 에피소드 객체를 (세션에서 분리된 상태로) 반환하거나,
    단순히 성공 여부를 나타내는 값을 반환할 수 있습니다.
    """
    db_episode = get_episode_by_id_and_work_id(
        db, work_id=work_id, episode_id=episode_id
    )
    if not db_episode:
        return None  # 해당 작품의 에피소드가 없으면 None 반환

    # 삭제 전에 정보를 복사해두고 싶다면 (선택적)
    # Pydantic v2: deleted_episode_data = schemas.Episode.model_validate(db_episode)
    # Pydantic v1: deleted_episode_data = schemas.Episode.from_orm(db_episode)

    db.delete(db_episode)
    db.commit()
    # return deleted_episode_data # Pydantic 모델로 변환된 복사본 반환
    return db_episode  # 또는 SQLAlchemy 객체 반환 (세션 만료 후 주의)
    # 또는 단순히 True 반환


def update_episode_ai_generated_content(
    db: Session, episode_id: int, new_ai_content: str
) -> Optional[models.Episode]:
    db_episode = (
        db.query(models.Episode).filter(models.Episode.episode_id == episode_id).first()
    )
    if db_episode:
        db_episode.episode_content = (
            new_ai_content  # 또는 별도의 ai_episode_content 필드가 있다면 그것을 사용
        )
        db.add(db_episode)
        db.commit()
        db.refresh(db_episode)
        return db_episode
    return None
