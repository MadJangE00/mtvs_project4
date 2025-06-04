from datasets import load_dataset
import sys
import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # SBERTEmbedder 경로에 맞게 조정
# from app.sbert_model import SBERTEmbedder # SBERTEmbedder 경로에 맞게 조정
from sentence_transformers import (
    SentenceTransformer,
)  # 직접 SentenceTransformer 사용 예시
from opensearchpy import OpenSearch, NotFoundError
import uuid
import ast  # 문자열을 파이썬 리터럴로 안전하게 파싱하기 위해 import


# --- SBERTEmbedder 클래스 정의 (만약 별도 파일에 있다면 import) ---
class SBERTEmbedder:
    def __init__(self, model_name="snunlp/KR-SBERT-V40K-klueNLI-augSTS"):
        self.model = SentenceTransformer(model_name)
        print(f"SBERT Embedder initialized with model: {model_name}")

    def encode(self, texts, batch_size=32, show_progress_bar=True):
        print(f"Encoding {len(texts)} texts...")
        return self.model.encode(
            texts, batch_size=batch_size, show_progress_bar=show_progress_bar
        )


# --- SBERTEmbedder 클래스 정의 끝 ---

# 1. 데이터 로드
print("Loading dataset...")
dataset = load_dataset("binjang/NIKL-korean-english-dictionary", split="train")
print("Dataset loaded.")

print(f"Dataset columns: {dataset.column_names}")

# 2. 임베딩 대상 텍스트 구성
# item이 None이거나 'Form' 키가 없는 경우를 대비해 item.get('Form') 사용
texts = [item.get("Form") for item in dataset if item and item.get("Form")]
# Form이 None이거나 빈 문자열인 경우를 제외 (이미 위에서 처리되지만 명시적으로)
texts = [text for text in texts if text]
print(f"Number of texts to embed: {len(texts)}")

# 3. 임베딩
embedder = SBERTEmbedder()
vectors = embedder.encode(texts)  # texts가 비어있으면 vectors도 비게 됨

vector_dimension = 768  # 기본값
if vectors is not None and vectors.size > 0:
    print(
        f"Generated {len(vectors)} vectors. Shape of first vector: {vectors[0].shape}"
    )
    vector_dimension = vectors[0].shape[0]
else:
    print(
        f"Warning: No vectors were generated (texts list might be empty or embedding failed). Defaulting dimension to {vector_dimension}."
    )
    if not texts:
        print("Error: No valid 'Form' data found in dataset to embed. Aborting.")
        sys.exit(1)


# 4. OpenSearch 연결
client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
    verify_certs=False,
    timeout=60,
)
print("Connected to OpenSearch.")

# 5. 인덱스 이름 정의
index_name = "korean-english-dictionary"  # FastAPI 코드와 일치하는지 확인

# 6. 기존 인덱스 삭제 (주의!)
try:
    if client.indices.exists(index=index_name):
        print(f"Deleting existing index: {index_name}...")
        client.indices.delete(index=index_name)
        print(f"Index {index_name} deleted.")
except NotFoundError:
    print(f"Index {index_name} not found, no need to delete.")
except Exception as e:
    print(f"Error deleting index {index_name}: {e}")


# 7. 새 인덱스 생성
print(f"Creating new index: {index_name}...")
try:
    client.indices.create(
        index=index_name,
        body={
            "settings": {  # k-NN 쿼리 사용 시 필요할 수 있는 설정
                "index.knn": True,
                "index.knn.space_type": "cosinesimil",
            },
            "mappings": {
                "properties": {
                    "form": {"type": "text"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": vector_dimension,
                    },  # 제공된 코드 기준 유지
                    "korean_definition": {"type": "text"},
                    "english_definition": {"type": "text"},
                    "usages": {"type": "text"},  # 매핑은 text로 유지, 저장 시 리스트로
                }
            },
        },
    )
    print(f"Index {index_name} created successfully.")
except Exception as e:
    print(f"Error creating index {index_name}: {e}")
    sys.exit(f"Failed to create index. Aborting.")


# 8. 문서 삽입 (usages 필드 처리 수정)
print(f"Indexing documents...")
indexed_count = 0

# 'Form'이 있는 아이템들만 필터링 (texts 리스트 생성 시 사용된 로직과 유사하게)
# vectors 배열은 이 필터링된 아이템들에 대한 임베딩임
valid_items_for_indexing = [item for item in dataset if item and item.get("Form")]

if len(valid_items_for_indexing) != len(vectors):
    print(
        f"Warning: Mismatch in item count ({len(valid_items_for_indexing)}) and vector count ({len(vectors)}). Indexing up to the smaller count."
    )
num_to_process = min(len(valid_items_for_indexing), len(vectors))


for i in range(num_to_process):
    item = valid_items_for_indexing[i]
    vec = vectors[i].tolist()  # NumPy 배열을 리스트로 변환

    # --- usages 필드 처리 ---
    raw_usages_data = item.get("Usages")  # 데이터셋에서 Usages 값 가져오기
    processed_usages = []  # 최종적으로 저장될 리스트 (문자열 요소만 포함)

    if isinstance(raw_usages_data, list):
        # Usages가 이미 리스트인 경우, 내부 요소들을 문자열로 변환하고 펼치기
        for sub_item in raw_usages_data:
            if isinstance(sub_item, list):  # 중첩 리스트 처리
                processed_usages.extend(map(str, sub_item))
            else:
                processed_usages.append(str(sub_item))
    elif isinstance(raw_usages_data, str):
        # Usages가 문자열인 경우
        stripped_usages = raw_usages_data.strip()
        if stripped_usages.startswith("[") and stripped_usages.endswith("]"):
            # 리스트처럼 보이는 문자열 (예: "['text1', 'text2']") 파싱 시도
            try:
                evaluated_data = ast.literal_eval(stripped_usages)
                if isinstance(evaluated_data, (list, tuple)):
                    for sub_item in evaluated_data:
                        if isinstance(sub_item, (list, tuple)):  # 중첩 리스트/튜플 처리
                            processed_usages.extend(map(str, sub_item))
                        else:
                            processed_usages.append(str(sub_item))
                else:  # ast.literal_eval 결과가 리스트/튜플이 아닌 다른 타입일 경우
                    processed_usages.append(
                        str(evaluated_data)
                    )  # 해당 값을 문자열로 변환하여 추가
            except (ValueError, SyntaxError):
                # 파싱 실패 시, 원본 문자열을 단일 요소로 리스트에 추가
                print(
                    f"Warning: Could not parse usages string for form '{item.get('Form')}': '{raw_usages_data}'. Storing as a single string in the list."
                )
                if stripped_usages:  # 비어있지 않은 경우에만 추가
                    processed_usages.append(stripped_usages)
        elif stripped_usages:  # 일반 문자열 (리스트 형태 아님)이고 비어있지 않은 경우
            processed_usages.append(stripped_usages)
    # raw_usages_data가 None이거나, 위 조건에 안 맞고 파싱도 안 되면 processed_usages는 빈 리스트로 유지됨
    # Pydantic에서 Optional[List[str]]이므로 빈 리스트도 유효함.
    # 만약 빈 리스트 대신 None(null)으로 저장하고 싶다면 아래 doc 구성 시 조건부 할당.

    doc = {
        "form": item.get(
            "Form"
        ),  # Form이 확실히 있다고 가정 (valid_items_for_indexing)
        "embedding": vec,
        "korean_definition": item.get("Korean Definition", ""),
        "english_definition": item.get("English Definition", ""),
        "usages": (
            processed_usages if processed_usages else None
        ),  # 빈 리스트일 경우 None으로 저장 (선택 사항)
        # 항상 리스트로 저장하려면 그냥 processed_usages
    }

    # --- 디버깅: 저장 직전의 doc['usages'] 값과 타입 확인 ---
    # print(f"--- Indexing for form: {doc['form']} ---")
    # print(f"Type of doc['usages'] to be indexed: {type(doc['usages'])}")
    # print(f"Value of doc['usages'] to be indexed: {doc['usages']}")
    # --- 디버깅 끝 ---

    try:
        client.index(index=index_name, id=str(uuid.uuid4()), body=doc) # 'document'를 'body'로 변경
        indexed_count += 1
        # ...
    except Exception as e_doc:
        print(f"ERROR indexing document for form '{item.get('Form')}': {e_doc}")
        # print(f"Problematic document data: {doc}") # 필요시 주석 해제

print(f"{indexed_count} documents were successfully indexed into '{index_name}'.")
