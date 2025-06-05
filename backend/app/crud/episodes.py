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


from ..models import Episode as EpisodeModel  # 예시 경로


# 저장 형식 정의 (프로젝트 전역에서 일관되게 사용)
EPISODE_DESCRIPTION_TAG_START = "[에피소드 설명]"
GENERATED_DIALOGUE_TAG_START = "[생성된 대사]"
CONTENT_SEPARATOR = "\n\n"  # 설명과 대사 사이, 또는 다른 주요 섹션 사이에 사용될 구분자


def format_episode_content_for_db(episode_description: str, llm_dialogue: str) -> str:
    """episode_description과 llm_dialogue를 결합하여 DB에 저장할 문자열로 포맷합니다."""
    return (
        f"{EPISODE_DESCRIPTION_TAG_START}\n{episode_description}"
        f"{CONTENT_SEPARATOR}"
        f"{GENERATED_DIALOGUE_TAG_START}\n{llm_dialogue}"
    )


def parse_episode_content_from_db(
    db_content: str,
) -> tuple[Optional[str], Optional[str]]:
    """DB에 저장된 content에서 episode_description과 llm_dialogue를 분리합니다."""
    description = None
    dialogue = None

    try:
        # [에피소드 설명] 태그와 [생성된 대사] 태그를 기준으로 분리 시도
        if (
            EPISODE_DESCRIPTION_TAG_START in db_content
            and GENERATED_DIALOGUE_TAG_START in db_content
        ):
            # 설명 부분 추출
            desc_start_index = db_content.find(EPISODE_DESCRIPTION_TAG_START) + len(
                EPISODE_DESCRIPTION_TAG_START
            )
            # 설명과 대사 태그 사이의 내용이 설명임
            dialogue_tag_index_for_desc_end = db_content.find(
                GENERATED_DIALOGUE_TAG_START
            )
            # CONTENT_SEPARATOR를 고려하여 실제 설명 내용의 끝을 찾음
            actual_desc_end_index = db_content.rfind(
                CONTENT_SEPARATOR, desc_start_index, dialogue_tag_index_for_desc_end
            )
            if actual_desc_end_index != -1:
                description = db_content[desc_start_index:actual_desc_end_index].strip()
            else:  # CONTENT_SEPARATOR가 없다면, 대사 태그 바로 앞까지
                description = db_content[
                    desc_start_index:dialogue_tag_index_for_desc_end
                ].strip()

            # 대사 부분 추출
            dialogue_start_index = db_content.find(GENERATED_DIALOGUE_TAG_START) + len(
                GENERATED_DIALOGUE_TAG_START
            )
            dialogue = db_content[dialogue_start_index:].strip()

        elif (
            EPISODE_DESCRIPTION_TAG_START in db_content
        ):  # 설명 태그만 있는 경우 (오래된 데이터 호환 또는 오류)
            desc_start_index = db_content.find(EPISODE_DESCRIPTION_TAG_START) + len(
                EPISODE_DESCRIPTION_TAG_START
            )
            description = db_content[
                desc_start_index:
            ].strip()  # 나머지를 설명으로 간주

        elif GENERATED_DIALOGUE_TAG_START in db_content:  # 대사 태그만 있는 경우
            dialogue_start_index = db_content.find(GENERATED_DIALOGUE_TAG_START) + len(
                GENERATED_DIALOGUE_TAG_START
            )
            dialogue = db_content[dialogue_start_index:].strip()  # 나머지를 대사로 간주

        else:  # 태그가 전혀 없는 경우, 전체를 대사로 간주 (기존 데이터 호환)
            dialogue = db_content.strip()

    except Exception as e:
        print(f"Error parsing episode content: {e}. Content: '{db_content[:100]}...'")
        # 오류 발생 시, 안전하게 전체를 dialogue로 취급하거나, None, None 반환
        if not dialogue:  # dialogue가 위에서 할당되지 않았다면
            dialogue = db_content  # 원본 내용이라도 반환하도록

    return description, dialogue


def create_ai_generated_episode(
    db: Session,
    works_id: int,
    llm_generated_dialogue: str,  # LLM이 생성한 순수 대사
    episode_description: str,  # 사용자가 입력한 에피소드 설명
) -> EpisodeModel:  # 응답 타입을 모델 객체로 변경 (라우터에서 스키마로 변환)

    # episode_description과 llm_generated_dialogue를 결합
    combined_content = format_episode_content_for_db(
        episode_description, llm_generated_dialogue
    )

    db_episode_obj = EpisodeModel(  # SQLAlchemy 모델 직접 사용
        works_id=works_id,
        episode_content=combined_content,  # 결합된 내용 저장
    )
    db.add(db_episode_obj)
    db.commit()
    db.refresh(db_episode_obj)
    return db_episode_obj  # 모델 객체 반환


def update_ai_generated_content_by_id(
    db: Session,
    episode_id: int,
    new_llm_dialogue: str,  # LLM으로부터 받은 수정된 '순수 대사'
) -> Optional[EpisodeModel]:
    db_episode = (
        db.query(EpisodeModel).filter(EpisodeModel.episode_id == episode_id).first()
    )
    if db_episode:
        # 기존 content에서 original_description 추출
        original_description, _ = parse_episode_content_from_db(
            db_episode.episode_content
        )

        if original_description is None:
            # 설명 부분을 찾지 못한 경우, 어떻게 처리할지 결정 필요
            # 1. 오류를 발생시키거나 로그를 남기고, new_llm_dialogue만으로 업데이트 (설명 유실)
            # 2. 또는 업데이트를 하지 않음
            print(
                f"Warning: Original episode description not found in episode_id {episode_id}. Updating with new dialogue only."
            )
            # 이 경우, 설명 없이 대사만 있는 형태로 저장될 수 있음 (형식 불일치 가능성)
            # 가장 안전한 방법은 설명이 없으면 업데이트를 막거나, 기본 설명을 넣는 것
            # 여기서는 new_llm_dialogue만으로 업데이트하는 대신, 설명을 "알 수 없음" 등으로 채울 수 있음
            # 또는 포맷팅 함수가 description이 None일 때를 처리하도록 수정
            db_episode.episode_content = format_episode_content_for_db(
                original_description or "원본 설명 없음",  # 설명이 없다면 기본값 사용
                new_llm_dialogue,
            )

        else:
            # 추출된 original_description과 new_llm_dialogue를 결합
            db_episode.episode_content = format_episode_content_for_db(
                original_description, new_llm_dialogue
            )

        db.commit()
        db.refresh(db_episode)
        return db_episode
    return None


# work_id까지 검증하는 버전
def update_episode_content_by_ids(
    db: Session, work_id: int, episode_id: int, new_llm_dialogue: str
) -> Optional[EpisodeModel]:
    db_episode = (
        db.query(EpisodeModel)
        .filter(EpisodeModel.works_id == work_id, EpisodeModel.episode_id == episode_id)
        .first()
    )
    if db_episode:
        original_description, _ = parse_episode_content_from_db(
            db_episode.episode_content
        )

        if original_description is None:
            print(
                f"Warning: Original episode description not found in work_id {work_id}, episode_id {episode_id}. Using placeholder."
            )
            # 여기서도 original_description이 None일 경우 처리
            final_description = "원본 설명 없음"  # 또는 다른 기본값
        else:
            final_description = original_description

        db_episode.episode_content = format_episode_content_for_db(
            final_description, new_llm_dialogue
        )
        db.commit()
        db.refresh(db_episode)
        return db_episode
    return None


def get_episode_by_ids(
    db: Session, work_id: int, episode_id: int
) -> Optional[models.Episode]:
    """
    특정 작품(work_id)에 속한 특정 에피소드(episode_id)를 조회합니다.
    """
    return (
        db.query(models.Episode)
        .filter(
            models.Episode.episode_id == episode_id, models.Episode.works_id == work_id
        )
        .first()
    )
