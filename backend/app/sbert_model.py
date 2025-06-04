from sentence_transformers import SentenceTransformer

# 임베딩 모델
class SBERTEmbedder:
    def __init__(self, model_name: str = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        return self.model.encode(texts, show_progress_bar=True)
