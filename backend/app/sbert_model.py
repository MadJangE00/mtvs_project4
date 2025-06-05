# from sentence_transformers import SentenceTransformer

# # 임베딩 모델
# class SBERTEmbedder:
#     def __init__(self, model_name: str = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"):
#         self.model = SentenceTransformer(model_name)

#     def encode(self, texts):
#         return self.model.encode(texts, show_progress_bar=True)
# app/sbert_model.py
from sentence_transformers import SentenceTransformer
from functools import lru_cache
from . import config  # Assuming config.py is in the 'app' directory

# It's good practice to define constants if they are specific to a model family
# snunlp/KR-SBERT-V40K-klueNLI-augSTS has 768 dimensions.
# If your EMBEDDING_MODEL_NAME changes to a model with a different dimension,
# this constant would also need to change.
# Consider adding EMBEDDING_DIMENSION to your config.py if it can vary.
SBERT_EMBEDDING_DIMENSION = 768


class SBERTEmbedder:
    def __init__(self):
        # Use the model name from config, fallback to a default if not in config
        # (though your config.py provides a default for EMBEDDING_MODEL_NAME)
        model_name_to_load = config.EMBEDDING_MODEL_NAME
        self.model = SentenceTransformer(model_name_to_load)
        print(f"SBERT Embedder initialized with model: {model_name_to_load}")

    def encode(
        self, texts, show_progress_bar=False
    ):  # Default show_progress_bar to False for server use
        return self.model.encode(texts, show_progress_bar=show_progress_bar)


@lru_cache()  # Cache the embedder instance
def get_embedder():
    return SBERTEmbedder()
