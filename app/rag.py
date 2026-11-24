import os
import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
EMBED_MODEL = "gemini-embedding-001"


class PolicyRAG:
    def __init__(self, filepath: str = "data/policies.txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        self.chunks = [text.strip() for text in raw_text.split("\n\n") if text.strip()]
        self.embeddings: list[list[float]] =self. _get_embeddings(self.chunks)

    def _get_embeddings(self, text: list[str]) -> list[float]:
        response = client.models.embed_content(
            model=EMBED_MODEL, 
            contents=text,
        )
        return [e.values for e in response.embeddings]


    @staticmethod
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        a = np.array(vec_a)
        b = np.array(vec_b)

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))

    def search(self, query: str, top_k: int = 2) -> list[dict]:
        query_vector = self._get_embeddings(query)[0]
        scored_results = []

        for chunk, vector in zip(self.chunks, self.embeddings):
            score = self._cosine_similarity(vector, query_vector)
            scored_results.append((score,chunk))

        scored_results.sort(key=lambda x : x[0], reverse=True)

        return [
            {
                "policy_excerpt": chunk,
                "similarity_score": round(score, 4),
            }
            for score, chunk in scored_results[:top_k]
        ]