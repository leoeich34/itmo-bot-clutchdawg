# app/rag/vector_db.py

import faiss
import numpy as np

class VectorDB:
    def __init__(self, dimension=768):
        self.dimension = dimension
        self.index = faiss.IndexIVFFlat(faiss.IndexFlatIP(self.dimension), self.dimension, 100, faiss.METRIC_INNER_PRODUCT)
        self.texts = []
        self.embed_model = SentenceTransformer('all-MiniLM-L12-v2')
        self.index.train(np.random.random((1000, self.dimension)).astype('float32'))  # Тренировка индекса

    def add_texts(self, texts: List[str]):
        embeddings = self.embed_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        self.index.add(embeddings)
        self.texts.extend(texts)

    def query(self, query_embedding: np.ndarray, top_k=5) -> List[Dict]:
        if self.index.ntotal == 0:
            return []
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.texts):
                results.append({
                    "text": self.texts[idx],
                    "score": float(dist)
                })
        return results