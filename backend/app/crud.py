# from sqlalchemy.orm import Session
# from . import models, schemas
# from sqlalchemy.inspection import inspect
# from fastapi import HTTPException
# from sqlalchemy.sql import func
# from typing import Optional, List


# # 유저 조회
# def get_user_by_id(db: Session, user_id: str) -> Optional[models.User]:
#     return db.query(models.User).filter(models.User.user_id == user_id).first()


# # 유저별 단어 추가
# def create_user_word(db: Session, word_data: schemas.WordCreate):
#     # 이미 해당 유저에게 같은 이름의 단어가 있는지 확인(동음이의의 경우 때문에 생략략)
#     db_word = get_word_by_name_and_user(
#         db, word_name=word_data.word_name, user_id=word_data.user_id
#     )
#     if db_word:
#         # 이미 존재할 경우 처리 (예: 예외 발생 또는 업데이트 로직)
#         raise HTTPException(status_code=400, detail="Word already exists for this user")

#     # Word 객체 생성 (예문 제외)
#     db_word = models.Word(
#         user_id=word_data.user_id,
#         word_name=word_data.word_name,
#         word_content=word_data.word_content,
#     )
#     db.add(db_word)
#     db.flush()  # words_id를 얻기 위해 flush

#     # 예문 추가
#     if word_data.examples:
#         for i, example_data in enumerate(word_data.examples):
#             db_example = models.WordExample(
#                 words_id=db_word.words_id,  # 방금 생성된 단어의 ID
#                 example_sequence=i + 1,  # 단어 내 예문 순서 (1부터 시작)
#                 word_example_content=example_data.word_example_content,
#             )
#             db.add(db_example)

#     db.commit()
#     db.refresh(db_word)  # 관계형 데이터(예문)까지 로드하려면 옵션 필요
#     return db_word


# # --- Word CRUD (예문 추가 시 단어 조회용) ---
# def get_word_by_id_and_user_id(
#     db: Session, word_id: int, user_id: str
# ) -> Optional[models.Word]:
#     """특정 사용자의 특정 단어를 ID로 조회합니다."""
#     return (
#         db.query(models.Word)
#         .filter(models.Word.words_id == word_id, models.Word.user_id == user_id)
#         .first()
#     )


# # 단어 이름으로 단어 조회
# def get_word_by_name_and_user(db: Session, word_name: str, user_id: str):
#     return (
#         db.query(models.Word)
#         .filter(models.Word.word_name == word_name, models.Word.user_id == user_id)
#         .first()
#     )


# # 특정 단어를 메인key로 조회
# def get_word_by_id(db: Session, word_id: int):
#     return db.query(models.Word).filter(models.Word.words_id == word_id).first()


# # 단어 삭제
# def delete_word(db: Session, word_id: int):
#     word = db.query(models.Word).filter(models.Word.words_id == word_id).first()
#     if word:
#         db.delete(word)
#         db.commit()
#         return word
#     return None


# # 단어 이름으로 단어 조회
# def get_word_by_name(db: Session, word_name: str):
#     return db.query(models.Word).filter(models.Word.word_name == word_name).first()


# # 단어 예문 추가
# def create_word_example(
#     db: Session,
#     word_id: int,
#     example_create: schemas.WordExampleCreate,  # 요청 본문 스키마 사용
# ) -> models.WordExample:
#     """
#     특정 단어(word_id)에 대한 새 예문(WordExample)을 생성합니다.
#     example_sequence는 자동으로 다음 순번으로 할당됩니다.
#     """
#     # 해당 words_id에 대한 다음 example_sequence 결정
#     # (동시성 이슈가 민감한 시스템에서는 DB 레벨 시퀀스 또는 락킹 고려)
#     last_sequence = (
#         db.query(func.max(models.WordExample.example_sequence))
#         .filter(models.WordExample.words_id == word_id)
#         .scalar()
#     )  # 단일 값 반환

#     next_sequence = (last_sequence + 1) if last_sequence is not None else 1

#     db_example = models.WordExample(
#         words_id=word_id,
#         example_sequence=next_sequence,
#         word_example_content=example_create.word_example_content,
#     )
#     db.add(db_example)
#     try:
#         db.commit()
#         db.refresh(db_example)
#     except Exception as e:
#         db.rollback()
#         # 로깅 권장
#         raise e  # API 레이어에서 처리하도록 예외를 다시 발생
#     return db_example


# # 단어 예문 조회
# def get_word_examples_by_word_id(db: Session, word_id: int) -> List[models.WordExample]:
#     """특정 단어에 속한 모든 예문을 조회합니다."""
#     return (
#         db.query(models.WordExample)
#         .filter(models.WordExample.words_id == word_id)
#         .order_by(models.WordExample.example_sequence)
#         .all()
#     )


# # 단어 카운트 수로 정렬
# def get_words_by_user_sorted_by_count(db: Session, user_id: str):
#     return (
#         db.query(models.Word)
#         .filter(models.Word.user_id == user_id)
#         .order_by(models.Word.word_count.desc())
#         .all()
#     )


# # 단어 생성 시간으로 정렬
# def get_words_by_user_sorted_by_created_time(db: Session, user_id: str):
#     return (
#         db.query(models.Word)
#         .filter(models.Word.user_id == user_id)
#         .order_by(models.Word.word_created_time.desc())
#         .all()
#     )


# def increment_word_count_atomic(db: Session, word_id: int):
#     db_word = db.query(models.Word).filter(models.Word.words_id == word_id).first()
#     if db_word:
#         # word_count가 NULL일 수 있는 경우를 대비한 처리
#         if db_word.word_count is None:
#             # 초기값을 0으로 설정하고 시작하거나, DB update 문에서 COALESCE 사용
#             db.query(models.Word).filter(models.Word.words_id == word_id).update(
#                 {models.Word.word_count: 1}, synchronize_session=False
#             )
#         else:
#             db.query(models.Word).filter(models.Word.words_id == word_id).update(
#                 {models.Word.word_count: models.Word.word_count + 1},
#                 synchronize_session=False,
#             )
#             # 또는 models.Word.word_count: F(models.Word.word_count) + 1 사용 가능 (NULL 처리 필요)

#         db.commit()
#         db.refresh(db_word)  # refresh는 여전히 필요
#         return db_word
#     return None


# def create_user_work(
#     db: Session, work_data: schemas.WorkCreate
# ) -> models.Work:  # user_id는 WorkCreate 스키마 안에 포함
#     """
#     새로운 작품(Work)을 생성합니다. 하위 요소는 별도 API로 추가됩니다.
#     """
#     db_work = models.Work(
#         user_id=work_data.user_id,  # WorkCreate 스키마에서 user_id를 받는다고 가정
#         works_title=work_data.works_title,
#     )
#     db.add(db_work)
#     db.commit()
#     db.refresh(db_work)
#     return db_work


# def get_works_by_user_id(db: Session, user_id: str) -> List[models.Work]:
#     """
#     특정 사용자의 모든 작품 목록을 조회합니다.
#     """
#     return db.query(models.Work).filter(models.Work.user_id == user_id).all()


# def get_work_by_id(db: Session, work_id: int) -> Optional[models.Work]:
#     """
#     작품 ID로 특정 작품을 조회합니다.
#     이때 연관된 Characters, Worlds 등도 함께 로드될 수 있도록 relationship 설정이 중요합니다.
#     (기본적으로 lazy='select'이므로, 접근 시 추가 쿼리가 발생할 수 있음)
#     효율을 위해 joined loading (e.g., options(joinedload(models.Work.characters))) 등을 고려할 수 있습니다.
#     """
#     return db.query(models.Work).filter(models.Work.works_id == work_id).first()


# # 소유권 확인을 위한 함수 (선택적)
# def get_work_by_id_and_user_id(
#     db: Session, work_id: int, user_id: str
# ) -> Optional[models.Work]:
#     """
#     작품 ID와 사용자 ID로 특정 작품을 조회합니다. (소유권 확인용)
#     """
#     return (
#         db.query(models.Work)
#         .filter(models.Work.works_id == work_id, models.Work.user_id == user_id)
#         .first()
#     )


# def delete_work_by_id(db: Session, work_id: int) -> Optional[models.Work]:
#     """
#     작품 ID로 특정 작품을 삭제합니다.
#     models.Work에 cascade="all, delete-orphan"이 설정되어 있다면,
#     연관된 Characters, Worlds 등도 함께 삭제됩니다.
#     """
#     db_work = db.query(models.Work).filter(models.Work.works_id == work_id).first()
#     if db_work:
#         db.delete(db_work)
#         db.commit()
#         return db_work  # 삭제된 객체의 복사본 반환 (또는 db_work 자체를 반환할 수도 있으나, 세션 만료 후 문제 가능성)
#         # 또는 단순히 True/None을 반환하거나, 메시지를 반환할 수도 있음
#     return None
