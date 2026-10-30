from abc import ABC, abstractmethod
from typing import List, Dict, Any
import re


class BaseRetrievalProvider(ABC):
    @abstractmethod
    def calculate_relevance(self, query: str, document_text: str, topic: str = "") -> float:
        pass


class LexicalRetrievalProvider(BaseRetrievalProvider):
    """Calculates normalized lexical relevance score between query and fact text/topic."""

    def __init__(self):
        # Stopwords to filter out trivial words
        self.stopwords = {
            "the", "is", "at", "which", "on", "a", "an", "and", "or", "to", "in",
            "of", "for", "with", "as", "by", "from", "its", "was", "be", "this",
            "that", "it", "are", "were"
        }

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r"\w+", text.lower())
        return [w for w in words if w not in self.stopwords and len(w) > 1]

    def calculate_relevance(self, query: str, document_text: str, topic: str = "") -> float:
        if not query or not document_text:
            return 0.1

        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            return 0.2

        doc_tokens = set(self._tokenize(f"{topic} {document_text}"))
        if not doc_tokens:
            return 0.1

        # Token overlap / Jaccard
        intersection = query_tokens.intersection(doc_tokens)
        overlap_score = len(intersection) / len(query_tokens)

        # Topic boost
        topic_tokens = set(self._tokenize(topic))
        topic_overlap = len(query_tokens.intersection(topic_tokens))
        topic_boost = 0.2 if topic_overlap > 0 else 0.0

        # Exact substring boost
        substring_boost = 0.2 if topic.lower() in query.lower() else 0.0

        total_score = overlap_score * 0.6 + topic_boost + substring_boost
        # Base floor score of 0.1 so candidate isn't zeroed out completely
        return round(max(0.05, min(1.0, total_score)), 3)
