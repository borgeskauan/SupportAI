"""Similarity matrix computation for embeddings."""

import logging
import numpy as np
from scipy.spatial.distance import pdist, squareform


logger = logging.getLogger(__name__)


def compute_similarity_matrix(
    embeddings: dict[str, list[float]]
) -> tuple[list[str], np.ndarray]:
    """
    Compute pairwise cosine similarity matrix from embeddings.

    Args:
        embeddings: Dict mapping record_id -> embedding vector

    Returns:
        Tuple of (record_ids, similarity_matrix)
        - record_ids: List of record IDs in matrix order (for axis labels)
        - similarity_matrix: N×N numpy array where [i,j] = cosine_similarity(i,j)
                            Range: -1 to 1 (1 = identical, 0 = orthogonal, -1 = opposite)

    Raises:
        ValueError: If embeddings dict is empty or contains inconsistent dimensions
    """
    if not embeddings:
        raise ValueError("Embeddings dict cannot be empty")

    # Extract record IDs in consistent order
    record_ids = list(embeddings.keys())

    # Convert to numpy array
    vectors = np.array([embeddings[rid] for rid in record_ids], dtype=np.float32)

    if len(vectors) == 0:
        raise ValueError("No valid embeddings found")

    # Handle single vector case
    if len(vectors) == 1:
        return record_ids, np.array([[1.0]], dtype=np.float32)

    # Compute pairwise cosine distances (returns condensed distance matrix)
    distances = pdist(vectors, metric="cosine")

    # Convert condensed distance matrix to square matrix
    distance_matrix = squareform(distances)

    # Convert distances to similarities: similarity = 1 - cosine_distance
    similarity_matrix = 1.0 - distance_matrix

    logger.debug(
        f"Computed {len(record_ids)}×{len(record_ids)} similarity matrix "
        f"from {len(vectors)} embeddings"
    )

    return record_ids, similarity_matrix.astype(np.float32)
