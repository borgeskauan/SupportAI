"""Semantic clustering module for grouping similar support records."""

import logging
from typing import Optional

from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import numpy as np

from backend.models import SupportRecord
from backend.models.cluster_group import ClusterGroup


logger = logging.getLogger(__name__)


def cluster_similar_records(
    records: list[SupportRecord],
    embeddings: dict[str, list[float]],
    min_cluster_size: int = 3,
    similarity_threshold: float = 0.70,
) -> list[ClusterGroup]:
    """
    Cluster support records by semantic similarity of their embeddings.

    Uses hierarchical clustering with cosine distance to group similar cases
    into issue families. Records with insufficient similarity (below threshold)
    form singleton clusters.

    Args:
        records: List of SupportRecord objects
        embeddings: Dict mapping record_id -> embedding vector
        min_cluster_size: Minimum records required to form a valid cluster (default: 3)
        similarity_threshold: Minimum cosine similarity to form a cluster (default: 0.70).
                            Range: 0-1 where 1 = identical, 0 = orthogonal

    Returns:
        List of ClusterGroup objects, only including clusters with >= min_cluster_size records

    Raises:
        ValueError: If records or embeddings are empty, or if dimensions mismatch
    """
    if not records:
        logger.warning("No records provided for clustering")
        return []

    if not embeddings:
        logger.warning("No embeddings provided for clustering")
        return []

    # Validate all records have embeddings
    record_ids = [r.id for r in records]
    missing = [rid for rid in record_ids if rid not in embeddings]
    if missing:
        logger.warning(f"Missing embeddings for {len(missing)} records, skipping clustering")
        return []

    logger.info(f"Clustering {len(records)} records with similarity_threshold={similarity_threshold}")

    # Convert embeddings to numpy array in same order as records
    vectors = np.array([embeddings[rid] for rid in record_ids], dtype=np.float32)

    # Handle single record case
    if len(vectors) == 1:
        logger.info("Only 1 record provided, returning singleton cluster")
        return [
            ClusterGroup(
                cluster_id="cluster_001",
                record_ids=record_ids,
                similarity_threshold=similarity_threshold,
                confidence_score=1.0,
                size=1,
            )
        ]

    try:
        # Compute pairwise cosine distances
        # pdist returns condensed distance matrix
        distances = pdist(vectors, metric="cosine")

        # Perform hierarchical clustering
        Z = linkage(distances, method="average")

        # Convert similarity threshold to distance threshold
        # similarity = 1 - cosine_distance
        distance_threshold = 1.0 - similarity_threshold

        # Cut the dendrogram at the distance threshold
        cluster_labels = fcluster(Z, distance_threshold, criterion="distance")

        logger.debug(f"Hierarchical clustering produced {len(np.unique(cluster_labels))} clusters")

        # Group records by cluster label
        clusters_dict = {}
        for record_id, label in zip(record_ids, cluster_labels):
            if label not in clusters_dict:
                clusters_dict[label] = []
            clusters_dict[label].append(record_id)

        # Build ClusterGroup objects, filtering by minimum size
        cluster_groups = []
        for cluster_idx, (label, ids) in enumerate(sorted(clusters_dict.items()), 1):
            cluster_size = len(ids)

            # Skip clusters smaller than minimum
            if cluster_size < min_cluster_size:
                logger.debug(
                    f"Skipping cluster with {cluster_size} records "
                    f"(below minimum {min_cluster_size})"
                )
                continue

            # Compute cluster confidence: average pairwise similarity within cluster
            if cluster_size > 1:
                # Get vectors for this cluster
                cluster_vectors = vectors[[record_ids.index(rid) for rid in ids]]
                # Compute pairwise distances within cluster
                cluster_distances = pdist(cluster_vectors, metric="cosine")
                # Convert to similarities
                cluster_similarities = 1.0 - cluster_distances
                confidence = float(np.mean(cluster_similarities))
            else:
                confidence = 1.0

            cluster = ClusterGroup(
                cluster_id=f"cluster_{cluster_idx:03d}",
                record_ids=ids,
                similarity_threshold=similarity_threshold,
                confidence_score=confidence,
                size=cluster_size,
            )
            cluster_groups.append(cluster)

        logger.info(
            f"Clustering complete: {len(cluster_groups)} clusters "
            f"with >= {min_cluster_size} records"
        )
        logger.info(f"  Cluster sizes: {[c.size for c in cluster_groups]}")

        return cluster_groups

    except Exception as e:
        logger.error(f"Error during clustering: {e}")
        raise
