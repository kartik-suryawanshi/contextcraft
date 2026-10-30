from abc import ABC, abstractmethod
from typing import List
import hashlib
import math


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        pass


class DeterministicEmbeddingProvider(BaseEmbeddingProvider):
    """Generates deterministic pseudo-embeddings for testing and local operation without external APIs."""

    def __init__(self, dimensions: int = 16):
        self.dimensions = dimensions

    def embed_text(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimensions

        # Hash chunks of the text to deterministic floats
        tokens = text.lower().split()
        vector = [0.0] * self.dimensions
        for idx, token in enumerate(tokens):
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            for d in range(self.dimensions):
                val = ((h >> (d * 4)) & 0xFF) / 255.0 - 0.5
                vector[d] += val

        # Normalize to unit length
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 1e-6:
            vector = [round(x / norm, 4) for x in vector]
        return vector

    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        return max(0.0, min(1.0, (dot + 1.0) / 2.0))
