import logging
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_EMBEDDINGS_PATH = REPO_ROOT / "data" / "corpus_embeddings.npz"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

CONTEXT_TOKEN_BUDGET = 4000

CHARS_PER_TOKEN = 4


@lru_cache(maxsize=1)
def _get_embedding_model() -> SentenceTransformer:
    """Lazy-load the sentence embedding model."""
    logger.info(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@lru_cache(maxsize=1)
def _get_reranker_model() -> CrossEncoder:
    """Lazy-load the cross-encoder reranking model."""
    logger.info(f"Loading reranker model: {RERANKER_MODEL_NAME}")
    return CrossEncoder(RERANKER_MODEL_NAME)


@lru_cache(maxsize=1)
def _load_corpus() -> Tuple[np.ndarray, List[str]]:
    """
    Load the precomputed corpus embeddings and the corresponding text
    passages. The .npz file contains two arrays: 'embeddings' (n x d)
    and 'passages' (n,).
    """
    if not CORPUS_EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(
            f"Corpus embeddings file not found at {CORPUS_EMBEDDINGS_PATH}. "
            "The full reference corpus is not redistributed with this "
            "release; a small representative subset is shipped to support "
            "the demo. See README for details."
        )
    data = np.load(CORPUS_EMBEDDINGS_PATH, allow_pickle=True)
    embeddings = data["embeddings"]
    passages = data["passages"].tolist()
    logger.info(f"Loaded corpus: {len(passages)} passages, "
                f"embedding dim = {embeddings.shape[1]}")
    return embeddings, passages

def retrieve(
    query: str,
    top_k: int = 50,
    top_k_after_rerank: int = 8,
    max_tokens: int = CONTEXT_TOKEN_BUDGET,
) -> str:
    embedding_model = _get_embedding_model()
    reranker_model = _get_reranker_model()
    corpus_embeddings, corpus_passages = _load_corpus()

    query_embedding = embedding_model.encode(
        query, normalize_embeddings=True, show_progress_bar=False
    )
    similarities = corpus_embeddings @ query_embedding  # cosine since normalized
    top_k_indices = np.argpartition(-similarities, top_k)[:top_k]
    top_k_indices = top_k_indices[np.argsort(-similarities[top_k_indices])]
    candidate_passages = [corpus_passages[i] for i in top_k_indices]

    pairs = [(query, passage) for passage in candidate_passages]
    rerank_scores = reranker_model.predict(pairs, show_progress_bar=False)
    rerank_order = np.argsort(-rerank_scores)[:top_k_after_rerank]
    reranked_passages = [candidate_passages[i] for i in rerank_order]
  
    context = _assemble_context(reranked_passages, max_tokens)

    return context

def _assemble_context(passages: List[str], max_tokens: int) -> str:
    """
    Concatenate passages in order, truncating to the token budget.

    Passages are joined by blank lines. The function does not perform
    exact tokenisation; the character-per-token heuristic is sufficient
    to keep the resulting context well within the LLM's input window
    while preserving the rerank order.
    """
    max_chars = max_tokens * CHARS_PER_TOKEN
    parts: List[str] = []
    running_chars = 0
    for passage in passages:
        if running_chars + len(passage) > max_chars:
            break
        parts.append(passage)
        running_chars += len(passage) + 2  # +2 for the joining "\n\n"
    return "\n\n".join(parts)
