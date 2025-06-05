# app/crud/opensearch_crud.py
from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
from opensearchpy.exceptions import NotFoundError
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from ..sbert_model import (
    get_embedder,
    SBERT_EMBEDDING_DIMENSION,
)
from .. import config  # config.py 사용
from ..models import Character, World


# Global OpenSearch client (기존과 동일)
def get_opensearch_client():
    # ... (기존 코드와 동일) ...
    protocol = "http"
    os_hosts = [{"host": config.OPENSEARCH_HOST, "port": config.OPENSEARCH_PORT}]
    http_auth_tuple = None
    if config.OPENSEARCH_USER and config.OPENSEARCH_PASSWORD:
        http_auth_tuple = (config.OPENSEARCH_USER, config.OPENSEARCH_PASSWORD)
    client = OpenSearch(
        hosts=os_hosts,
        http_auth=http_auth_tuple,
        use_ssl=(protocol == "https"),
        verify_certs=False,
        ssl_assert_hostname=False,
        connection_class=RequestsHttpConnection,
    )
    if client.ping():
        print("Connected to OpenSearch successfully! (opensearch_crud)")
    else:
        print("Could not connect to OpenSearch! (opensearch_crud)")
    return client


os_client = get_opensearch_client()
embedder = get_embedder()


RAG_WORKS_CONTENT_INDEX_NAME = config.OPENSEARCH_RAG_INDEX_NAME # config.py에 해당 변수가 정의되어 있어야 함
# 기존 OPENSEARCH_INDEX_NAME은 다른 용도로 사용될 수 있으므로, RAG용 인덱스 이름을 명확히 분리합니다.
print(f"Using OpenSearch index for RAG: {RAG_WORKS_CONTENT_INDEX_NAME}")


def create_works_content_index():
    # 인덱스 생성 시 새로운 인덱스 이름 사용
    if not os_client.indices.exists(index=RAG_WORKS_CONTENT_INDEX_NAME):
        index_body = {
            "settings": {"index.knn": True, "index.knn.space_type": "cosinesimil"},
            "mappings": {
                "properties": {
                    "works_id": {"type": "integer"},
                    "content_type": {"type": "keyword"},
                    "original_db_id": {"type": "integer"},
                    "character_name": {"type": "text"},
                    "text_content": {
                        "type": "text",
                    },
                    "embedding_vector": {
                        "type": "knn_vector",
                        "dimension": SBERT_EMBEDDING_DIMENSION,
                        "method": {
                            "name": "hnsw",
                            "space_type": "cosinesimil",
                            "engine": "nmslib",  # 또는 "faiss"
                        },
                    },
                }
            },
        }
        try:
            os_client.indices.create(
                index=RAG_WORKS_CONTENT_INDEX_NAME, body=index_body
            )
            print(f"Index '{RAG_WORKS_CONTENT_INDEX_NAME}' created.")
        except Exception as e:
            print(f"Error creating index '{RAG_WORKS_CONTENT_INDEX_NAME}': {e}")
            # ... (오류 메시지 기존과 동일) ...
            raise
    else:
        print(f"Index '{RAG_WORKS_CONTENT_INDEX_NAME}' already exists.")


def index_documents_for_work(db: Session, works_id: int):
    actions = []
    # ... (캐릭터 정보 가져오는 부분은 동일) ...
    characters = db.query(Character).filter(Character.works_id == works_id).all()
    char_texts_to_embed_map = {}
    for char in characters:
        if char.character_settings:
            text = f"캐릭터명: {char.character_name}\n설정: {char.character_settings}"
            char_texts_to_embed_map[char.character_id] = (char, text)

    if char_texts_to_embed_map:
        # ... (임베딩 및 action 생성 부분은 동일) ...
        char_ids_ordered = list(char_texts_to_embed_map.keys())
        texts_to_embed = [char_texts_to_embed_map[cid][1] for cid in char_ids_ordered]
        char_embeddings = embedder.encode(texts_to_embed)
        for i, char_id in enumerate(char_ids_ordered):
            char_obj, original_text = char_texts_to_embed_map[char_id]
            action = {
                "_index": RAG_WORKS_CONTENT_INDEX_NAME,  # << 새로운 인덱스 이름 사용
                "_id": f"char_{char_obj.character_id}",
                # ... (_source 내용은 동일) ...
                "_source": {
                    "works_id": works_id,
                    "content_type": "character",
                    "original_db_id": char_obj.character_id,
                    "character_name": char_obj.character_name,
                    "text_content": original_text,
                    "embedding_vector": char_embeddings[i].tolist(),
                },
            }
            actions.append(action)

    # ... (세계관 정보 가져오는 부분은 동일) ...
    worlds = db.query(World).filter(World.works_id == works_id).all()
    world_texts_to_embed_map = {}
    for world_item in worlds:
        if world_item.worlds_content:
            world_texts_to_embed_map[world_item.worlds_id] = (
                world_item,
                world_item.worlds_content,
            )
    if world_texts_to_embed_map:
        # ... (임베딩 및 action 생성 부분은 동일) ...
        world_ids_ordered = list(world_texts_to_embed_map.keys())
        texts_to_embed = [world_texts_to_embed_map[wid][1] for wid in world_ids_ordered]
        world_embeddings = embedder.encode(texts_to_embed)
        for i, world_id in enumerate(world_ids_ordered):
            world_obj, original_text = world_texts_to_embed_map[world_id]
            action = {
                "_index": RAG_WORKS_CONTENT_INDEX_NAME,  # << 새로운 인덱스 이름 사용
                "_id": f"world_{world_obj.worlds_id}",
                # ... (_source 내용은 동일) ...
                "_source": {
                    "works_id": works_id,
                    "content_type": "world",
                    "original_db_id": world_obj.worlds_id,
                    "text_content": original_text,
                    "embedding_vector": world_embeddings[i].tolist(),
                },
            }
            actions.append(action)

    if actions:
        # ... (벌크 인덱싱 부분은 동일) ...
        try:
            success, errors = helpers.bulk(
                os_client, actions, raise_on_error=False, refresh=True
            )
            print(
                f"Successfully indexed {success} documents for works_id {works_id} into '{RAG_WORKS_CONTENT_INDEX_NAME}'."
            )
            if errors:
                print(f"Errors during indexing for works_id {works_id}: {errors}")
            return {"success": success, "errors": len(errors) if errors else 0}
        except Exception as e:
            print(f"Bulk indexing failed for works_id {works_id}: {e}")
            return {"success": 0, "errors": "Bulk indexing exception"}
    return {"success": 0, "errors": 0, "message": "No content to index."}


def search_relevant_documents(
    query_text: str, works_id: int, top_k: int = 5
) -> List[Dict[str, Any]]:
    # 검색 시 새로운 인덱스 이름 사용
    if not os_client.indices.exists(index=RAG_WORKS_CONTENT_INDEX_NAME):
        print(f"Search failed: Index '{RAG_WORKS_CONTENT_INDEX_NAME}' does not exist.")
        return []

    query_embedding = embedder.encode([query_text])[0].tolist()
    search_body = {
        "size": top_k,
        # ... (쿼리 내용은 동일) ...
        "query": {
            "bool": {
                "filter": [{"term": {"works_id": works_id}}],
                "must": [
                    {
                        "knn": {
                            "embedding_vector": {"vector": query_embedding, "k": top_k}
                        }
                    }
                ],
            }
        },
        "_source": ["text_content", "content_type", "character_name"],
    }
    try:
        response = os_client.search(
            index=RAG_WORKS_CONTENT_INDEX_NAME, body=search_body
        )  # << 새로운 인덱스 이름 사용
        return [hit["_source"] for hit in response["hits"]["hits"]]
    # ... (예외 처리 부분은 동일) ...
    except NotFoundError:
        print(f"Index {RAG_WORKS_CONTENT_INDEX_NAME} not found during search.")
        return []
    except Exception as e:
        print(f"Error during search: {e}")
        return []


# --- OpenSearch 데이터 업데이트/삭제 시 고려사항 ---
# 현재 제공된 CRUD 코드는 Character 또는 World 정보가 RDB에서 수정/삭제될 때
# OpenSearch의 해당 벡터 데이터를 자동으로 업데이트/삭제하는 로직은 포함하고 있지 않습니다.
# 이 기능을 추가하려면 다음 함수들이 필요합니다:


def delete_opensearch_document(document_id: str):
    """OpenSearch에서 특정 ID의 문서를 삭제합니다."""
    try:
        os_client.delete(index=RAG_WORKS_CONTENT_INDEX_NAME, id=document_id)
        print(
            f"Document {document_id} deleted from OpenSearch index {RAG_WORKS_CONTENT_INDEX_NAME}."
        )
    except NotFoundError:
        print(
            f"Document {document_id} not found in OpenSearch index {RAG_WORKS_CONTENT_INDEX_NAME} for deletion."
        )
    except Exception as e:
        print(f"Error deleting document {document_id} from OpenSearch: {e}")


def update_opensearch_document_for_character(db: Session, character_id: int):
    """RDB의 Character 변경 사항을 OpenSearch에 반영(업데이트 또는 재인덱싱)합니다."""
    character = (
        db.query(Character).filter(Character.character_id == character_id).first()
    )
    if character and character.character_settings:
        text_to_embed = f"캐릭터명: {character.character_name}\n설정: {character.character_settings}"
        embedding = embedder.encode([text_to_embed])[0].tolist()
        doc_id = f"char_{character.character_id}"
        document_source = {
            "works_id": character.works_id,
            "content_type": "character",
            "original_db_id": character.character_id,
            "character_name": character.character_name,
            "text_content": text_to_embed,
            "embedding_vector": embedding,
        }
        try:
            os_client.index(
                index=RAG_WORKS_CONTENT_INDEX_NAME,
                id=doc_id,
                body=document_source,
                refresh=True,
            )
            print(f"Character document {doc_id} updated in OpenSearch.")
        except Exception as e:
            print(f"Error updating character document {doc_id} in OpenSearch: {e}")
    elif character and not character.character_settings:  # 설정이 비워진 경우 삭제 고려
        delete_opensearch_document(f"char_{character.character_id}")


def update_opensearch_document_for_world(db: Session, world_id: int):
    """RDB의 World 변경 사항을 OpenSearch에 반영(업데이트 또는 재인덱싱)합니다."""
    world = db.query(World).filter(World.worlds_id == world_id).first()
    if world and world.worlds_content:
        embedding = embedder.encode([world.worlds_content])[0].tolist()
        doc_id = f"world_{world.worlds_id}"
        document_source = {
            "works_id": world.works_id,
            "content_type": "world",
            "original_db_id": world.worlds_id,
            "text_content": world.worlds_content,
            "embedding_vector": embedding,
        }
        try:
            os_client.index(
                index=RAG_WORKS_CONTENT_INDEX_NAME,
                id=doc_id,
                body=document_source,
                refresh=True,
            )
            print(f"World document {doc_id} updated in OpenSearch.")
        except Exception as e:
            print(f"Error updating world document {doc_id} in OpenSearch: {e}")
    elif world and not world.worlds_content:  # 내용이 비워진 경우 삭제 고려
        delete_opensearch_document(f"world_{world.worlds_id}")


# 위 update/delete 함수들은 SQLAlchemy의 이벤트 리스너나,
# Character/World 정보를 수정/삭제하는 CRUD 함수 내에서 호출되어야 합니다.
# 예를 들어, crud/characters.py의 update_character 함수 내에서
# update_opensearch_document_for_character(db, character_id)를 호출합니다.
# 마찬가지로 delete_character 함수 내에서는 delete_opensearch_document(f"char_{character_id}")를 호출합니다.
