from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime


# --- WordExample ---
class WordExampleBase(BaseModel):
    word_example_content: Optional[str] = ""


class WordExampleCreate(WordExampleBase):
    word_example_content: str


class WordExample(WordExampleBase):
    example_sequence: int
    words_id: int

    model_config = {"from_attributes": True}  # Pydantic V2


class WordExampleUpdate(WordExampleBase):
    # 수정 시에는 모든 필드가 선택적일 수 있도록 Optional 사용
    pass


# --- Word ---
class WordBase(BaseModel):
    word_name: str
    word_content: Optional[str] = ""


class WordCreate(WordBase):
    user_id: str
    examples: Optional[List[WordExampleCreate]] = Field(
        default=[],
        # 이 필드 레벨 examples는 OpenAPI UI에서 'examples' 필드 입력 시 참고용입니다.
        # 이 부분은 모델 전체 예시가 아닌, 'examples' 필드 자체에 대한 예시입니다.
        # 따라서 여기서 제공하는 예시는 List[WordExampleCreate]의 형태여야 합니다.
        examples=[  # List[WordExampleCreate] 형태의 예시
            [  # 첫 번째 예시 세트 (리스트 안의 리스트로 여러 세트 제공 가능)
                {"word_example_content": "예시 문장 1입니다."},
                {"word_example_content": "이것은 두 번째 예시 문장입니다."},
            ],
            [{"word_example_content": "또 다른 예시 문장입니다."}],  # 두 번째 예시 세트
        ],
        description="단어에 대한 예문 목록입니다. 각 예문은 'word_example_content' 키를 가져야 합니다.",  # 설명 추가
    )


class Word(WordBase):
    words_id: int
    user_id: str
    word_created_time: datetime
    word_count: Optional[int] = 0
    examples: List[WordExample] = []

    model_config = {"from_attributes": True}


class RelatedWordBase(BaseModel):
    form: str
    korean_definition: Optional[str] = None
    usages: Optional[List[str]] = None
    english_definition: Optional[str] = None


class RelatedWord(RelatedWordBase):
    score: Optional[float] = None

    class Config:
        from_attributes = False  # SqlAlchemy 모델과 호환되도록 설정, OpenSearch결과이므로 False로 설정, 기능 확장성 고려해서 코드 유지


class WordRequest(BaseModel):
    query: str = Field(..., description="검색할 핵심 구문 또는 단어")
    target_word_count: int = Field(
        default=5, ge=1, le=20, description="최종적으로 받고 싶은 단어의 수 (1~20)"
    )
    # initial_rag_content: Optional[str] = None # check_rag가 사용할 초기값 예시 (현재는 사용 안함)


class WordResponse(BaseModel):
    query: str
    final_words: List[str]
    target_word_count: int
    source_counts: Dict[str, int]  # 각 소스에서 몇 개의 단어가 왔는지


# --- WordExample Schemas ---

class WordExampleBase(BaseModel):
    """WordExample의 기본 내용 (생성 및 조회 시 공통)"""
    word_example_content: Optional[str] = Field(default="", description="예문 내용")


class WordExampleCreate(WordExampleBase):
    """
    WordExample 생성을 위한 요청 본문 스키마.
    실제 생성될 내용만 포함합니다.
    (words_id와 example_sequence는 경로 및 서버 로직에서 결정)
    """

    pass  # WordExampleBase와 동일한 필드만 필요


class WordExample(WordExampleBase):
    """
    WordExample 조회(응답)를 위한 스키마.
    DB 모델의 필드를 반영합니다.
    """

    words_id: int  # 부모 단어의 ID
    example_sequence: int  # 해당 단어 내 예문의 순서
    # word_example_content: str # WordExampleBase 에서 상속

    model_config = {"from_attributes": True}


# --- User ---
class UserBase(BaseModel):
    user_id: str
    # password 필드는 생성/수정 시에만 사용하고, 응답 스키마에서는 제외하는 것이 일반적입니다.


class UserCreate(UserBase):
    password: str  # 비밀번호는 생성 시에만 받도록


class User(UserBase):  # 응답용 스키마
    # 여기에 user_id 외 다른 반환할 사용자 정보 (예: username, email 등)
    # password 필드는 보안상 제외
    pass

    model_config = {"from_attributes": True}


# --- Character ---
class CharacterBase(BaseModel):
    character_name: Optional[str] = Field("unnamed", max_length=200)
    character_settings: Optional[str] = ""


class CharacterCreate(CharacterBase):
    pass  # works_id는 CRUD 함수에서 work_id 파라미터로 받음


class CharacterUpdate(BaseModel):  # 모든 필드를 Optional로
    character_name: Optional[str] = None
    character_settings: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)  # 부분 업데이트 시 필요


class Character(CharacterBase):
    character_id: int
    works_id: int
    model_config = ConfigDict(from_attributes=True)


# --- World ---
class WorldBase(BaseModel):
    worlds_content: Optional[str] = ""


class WorldCreate(WorldBase):
    pass  # works_id는 CRUD 함수에서 work_id 파라미터로 받음


class WorldUpdate(BaseModel):
    worlds_content: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class World(WorldBase):
    worlds_id: int
    works_id: int
    model_config = ConfigDict(from_attributes=True)


# --- Plan ---
class PlanningBase(BaseModel):
    plan_title: Optional[str] = Field("unnamed", max_length=200)
    plan_content: Optional[str] = ""


class PlanningCreate(PlanningBase):
    pass  # works_id는 CRUD 함수에서 work_id 파라미터로 받음


class PlanningUpdate(BaseModel):
    plan_title: Optional[str] = None
    plan_content: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class Planning(PlanningBase):
    plan_id: int
    works_id: int
    model_config = ConfigDict(from_attributes=True)


# --- Episode ---
class AIEpisodeContentGenerateRequest(BaseModel):
    additional_prompt: Optional[str] = Field(
        None, description="AI가 콘텐츠를 생성/수정할 때 참고할 추가 프롬프트"
    )


# --- Episode 관련 스키마 ---


# 기본 Episode 스키마 (SQLAlchemy 모델의 공통 필드 정의)
class EpisodeBase(BaseModel):
    works_id: int
    episode_content: Optional[str] = Field(
        None, description="에피소드의 내용"
    )  # 기본값을 None으로 하거나, ""로 할 수 있음
    # 모델의 server_default="" 와 일치시키려면 ""가 나을 수 있음
    # 여기서는 API 응답 시 null이 될 수 있도록 Optional[str]=None 유지


# 에피소드 생성 시 요청 본문에 사용될 수 있는 스키마
class EpisodeCreate(EpisodeBase):
    # works_id와 episode_content 외에 생성 시 필요한 다른 필드가 있다면 추가
    pass


# DB에서 읽어온 에피소드 정보 또는 대부분의 API 응답에 사용될 스키마
class Episode(EpisodeBase):
    episode_id: int  # 모든 에피소드 응답에는 ID가 포함되도록

    model_config = ConfigDict(from_attributes=True)  # SQLAlchemy 모델과 매핑


# 에피소드 내용만 업데이트할 때 사용될 수 있는 요청 스키마 (단순 텍스트 업데이트용)
class EpisodeContentUpdate(BaseModel):
    episode_content: str = Field(..., description="업데이트할 새로운 에피소드 내용")


# --- AI 콘텐츠 생성/업데이트 API의 특정 응답을 위한 스키마 (선택 사항) ---
# 만약 AI가 생성/수정한 내용'만' 명시적으로 반환하고 싶다면 이 스키마를 사용
class EpisodeAIContentResponse(BaseModel):
    episode_id: int
    works_id: int
    updated_episode_content: str = Field(
        description="AI에 의해 생성 또는 수정된 에피소드 내용"
    )

    model_config = ConfigDict(from_attributes=True)  # 필요시


# --- API 응답을 위한 좀 더 구체적인 스키마 (선택 사항) ---
# 만약 AI 콘텐츠 업데이트 후 전체 에피소드 객체 대신 특정 정보만 반환하고 싶다면 별도 정의
class EpisodeAIContentResponse(BaseModel):
    episode_id: int
    works_id: int
    updated_episode_content: str # 명확하게 업데이트된 내용을 지칭

    model_config = ConfigDict(from_attributes=True) # 필요시

# --- Work ---
class WorkBase(BaseModel):
    works_title: Optional[str] = Field(
        "unnamed", max_length=200
    )  # 기본값 및 길이 제한 예시


class WorkCreate(WorkBase):  # WorkBase 상속
    user_id: str  # 작품 생성 시 사용자 ID는 여전히 필요 (경로 또는 인증 통해)


class Work(WorkBase):
    works_id: int
    user_id: str
    # 조회 시 하위 요소들은 여전히 포함될 수 있습니다. (lazy loading 또는 eager loading 설정에 따라)
    characters: List[Character] = []
    worlds: List[World] = []
    plannings: List[Planning] = []
    episodes: List[Episode] = []

    model_config = ConfigDict(from_attributes=True)


# WorkUpdate 스키마도 works_title만 포함하도록 유지 (또는 필요에 따라 다른 Work 자체의 필드 추가)
class WorkUpdate(BaseModel):
    works_title: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# --- Dialogue ---
class DialogueContextIDs(BaseModel):
    # world_id: Optional[int] = None # 세계관은 작품(Work) 자체에 포함된다고 가정
    episode_id: Optional[int] = Field(None, description="참고할 에피소드 ID")
    character_id: Optional[int] = Field(
        None, description="참고할 캐릭터 ID"
    )  # 단일 캐릭터 ID로 가정, 여러 캐릭터면 List[int]
    plan_id: Optional[int] = Field(None, description="참고할 스토리 계획(플롯) ID")


class DialogueGenerationRequest(BaseModel):
    context_ids: DialogueContextIDs = Field(
        ..., description="참고할 컨텐츠들의 ID 정보"
    )
    prompt: str = Field(..., description="생성할 대사에 대한 구체적인 지시")

    class Config:
        json_schema_extra = {
            "example": {
                "context_ids": {"episode_id": 1, "character_id": 1, "plan_id": 1},
                "prompt": "주인공 알렉스가 적에게 마지막 일격을 가하며 외치는 짧고 강렬한 대사를 만들어주세요.",
            }
        }


class DialogueResponse(BaseModel):
    generated_dialogue: str
    # 디버깅이나 추가 정보용으로 컨텍스트 내용을 포함할 수도 있음
    # worlds_content_used: Optional[str] = None
    # episode_content_used: Optional[str] = None
    # character_settings_used: Optional[str] = None
    # plan_content_used: Optional[str] = None

    class Config:
        json_schema_extra = {"example": {"generated_dialogue": "이것으로... 끝이다!"}}


# 범기님 코드
class ExampleEvaluationRequest(BaseModel):
    sentence: str


# 윤정님 코드
class WordRequestAI(BaseModel):
    word: str


class ExampleResponse(BaseModel):
    word: str
    examples: str
    success: bool
    message: str = ""
