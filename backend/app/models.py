from sqlalchemy import (
    Column,
    BigInteger,
    String,
    ForeignKey,
    DateTime,
    Text,
    Integer,
)  # Integer 추가
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import (
    text,
)  # server_default에 숫자형 기본값을 명시적으로 사용하기 위해 추가
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file")

# 실제 DB 생성 시 사용 예시
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    user_id = Column(String(200), primary_key=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)

    # 관계 설정
    words = relationship("Word", back_populates="user", cascade="all, delete-orphan")
    works = relationship("Work", back_populates="user", cascade="all, delete-orphan")


class Word(Base):
    __tablename__ = "words"

    words_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        String(200), ForeignKey("user.user_id"), nullable=False, index=True
    )
    word_name = Column(String(200), nullable=False)
    # ERD 변경: VARCHAR(200) -> TEXT
    word_content = Column(
        Text, nullable=True, server_default=""
    )  # NULLABLE(default: empty)
    # ERD 변경: DATETIME 명시, NOTNULL
    word_created_time = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # ERD 변경: VARCHAR(200) -> INT, default: 0
    word_count = Column(
        Integer, nullable=True, server_default=text("0")
    )  # NULLABLE(default: 0)

    # 관계 설정
    user = relationship("User", back_populates="words")
    examples = relationship(
        "WordExample", back_populates="word", cascade="all, delete-orphan"
    )


class WordExample(Base):
    __tablename__ = "word_examples"

    example_sequence = Column(BigInteger, primary_key=True, nullable=False)
    words_id = Column(
        BigInteger, ForeignKey("words.words_id"), primary_key=True, nullable=False
    )
    # ERD 변경: VARCHAR(200) -> TEXT
    word_example_content = Column(
        Text, nullable=True, server_default=""
    )  # NULLABLE(default: empty)

    # 관계 설정
    word = relationship("Word", back_populates="examples")


class Work(Base):
    __tablename__ = "works"

    works_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        String(200), ForeignKey("user.user_id"), nullable=False, index=True
    )
    works_title = Column(
        String(200), nullable=True, server_default="unnamed"
    )  # NULLABLE(default: unnamed)

    # 관계 설정
    user = relationship("User", back_populates="works")
    characters = relationship(
        "Character", back_populates="work", cascade="all, delete-orphan"
    )
    worlds = relationship("World", back_populates="work", cascade="all, delete-orphan")
    plannings = relationship(
        "Planning", back_populates="work", cascade="all, delete-orphan"
    )
    episodes = relationship(
        "Episode", back_populates="work", cascade="all, delete-orphan"
    )


class Character(Base):
    __tablename__ = "characters"

    character_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    works_id = Column(
        BigInteger, ForeignKey("works.works_id"), nullable=False, index=True
    )
    character_name = Column(
        String(200), nullable=True, server_default="unnamed"
    )  # NULLABLE(default: unnamed)
    # ERD 변경: VARCHAR(200) -> TEXT
    character_settings = Column(
        Text, nullable=True, server_default=""
    )  # NULLABLE(default: empty)

    # 관계 설정
    work = relationship("Work", back_populates="characters")


class World(Base):
    __tablename__ = "worlds"

    worlds_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    works_id = Column(
        BigInteger, ForeignKey("works.works_id"), nullable=False, index=True
    )
    # ERD 변경: VARCHAR(200) -> TEXT
    worlds_content = Column(
        Text, nullable=True, server_default=""
    )  # NULLABLE(default: empty)

    # 관계 설정
    work = relationship("Work", back_populates="worlds")


class Planning(Base):
    __tablename__ = "planning"

    plan_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    works_id = Column(
        BigInteger, ForeignKey("works.works_id"), nullable=False, index=True
    )
    plan_title = Column(
        String(200), nullable=True, server_default="unnamed"
    )  # NULLABLE(default: unnamed)
    # ERD 변경: VARCHAR(200) -> TEXT
    plan_content = Column(
        Text, nullable=True, server_default=""
    )  # NULLABLE(default: empty)

    # 관계 설정
    work = relationship("Work", back_populates="plannings")


class Episode(Base):
    __tablename__ = "episodes"

    episode_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    works_id = Column(
        BigInteger, ForeignKey("works.works_id"), nullable=False, index=True
    )
    episode_content = Column(
        Text, nullable=True, server_default=""
    )  # NULLABLE(default: unnamed)

    # 관계 설정
    work = relationship("Work", back_populates="episodes")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ 테이블 생성 완료")
