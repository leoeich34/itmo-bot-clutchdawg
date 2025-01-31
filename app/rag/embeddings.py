# embeddings.py
from sentence_transformers import SentenceTransformer

class EmbeddingsModel:
    """
    Пример работы с моделью для получения эмбеддингов.
    Можно использовать 'all-MiniLM-L6-v2' или другую подходящую.
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def get_embeddings(self, texts: list) -> list:
        """
        Возвращает список эмбеддингов для списка текстов.
        Каждый эмбеддинг — это вектор float.
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings