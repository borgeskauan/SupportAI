"""Label generation for clustered issue families."""

import logging
from typing import TYPE_CHECKING

from backend.models.cluster_group import ClusterGroup

if TYPE_CHECKING:
    from backend.core.llm_protocol import LLM
    from backend.models import SupportRecord


logger = logging.getLogger(__name__)


LABEL_GENERATION_PROMPT = """You are generating a short internal label for a cluster of repeated solved support issues.

Write one concise issue-family label:
- 4 to 8 words
- clear and human-readable
- describe the shared customer problem
- do not mention case IDs
- do not use quotes
- return only the label

Cluster summaries:
{cluster_summaries}"""


def generate_cluster_labels(
    clusters: list[ClusterGroup],
    records: dict[str, "SupportRecord"],
    llm_provider: "LLM",
) -> list[ClusterGroup]:
    """
    Generate human-readable labels for clusters using an LLM provider.

    Args:
        clusters: List of ClusterGroup objects
        records: Dict mapping record_id -> SupportRecord
        llm_provider: LLM provider instance (mock, Gemini, etc.)

    Returns:
        List of ClusterGroup objects with label field populated

    Raises:
        ValueError: If clusters or records are empty
    """
    if not clusters:
        logger.warning("No clusters provided for label generation")
        return []

    if not records:
        logger.warning("No records provided for label generation")
        return []

    logger.info(f"Generating labels for {len(clusters)} clusters...")

    labeled_clusters = []

    for cluster in clusters:
        try:
            # Get records in this cluster
            cluster_records = []
            for rid in cluster.record_ids:
                if rid in records:
                    cluster_records.append(records[rid])
                else:
                    logger.warning(f"Record {rid} not found in records dict, skipping")

            if not cluster_records:
                logger.warning(f"Cluster {cluster.cluster_id} has no valid records, using fallback label")
                cluster.label = f"Issue Family {cluster.cluster_id}"
                labeled_clusters.append(cluster)
                continue

            # Build cluster summary for prompt
            summaries = "\n".join(
                f"{i+1}. {record.case_summary}"
                for i, record in enumerate(cluster_records)
            )

            # Build full prompt
            prompt = LABEL_GENERATION_PROMPT.format(cluster_summaries=summaries)

            # Call LLM provider
            label = llm_provider.generate(prompt)

            # Validate and store label
            if label:
                cluster.label = label
                logger.debug(f"Generated label for {cluster.cluster_id}: '{label}'")
            else:
                logger.warning(f"Empty label generated for {cluster.cluster_id}, using fallback")
                cluster.label = f"Issue Family {cluster.cluster_id}"

            labeled_clusters.append(cluster)

        except Exception as e:
            logger.error(f"Error generating label for cluster {cluster.cluster_id}: {e}")
            cluster.label = f"Issue Family {cluster.cluster_id}"
            labeled_clusters.append(cluster)

    logger.info(f"Label generation complete: {len(labeled_clusters)} clusters labeled")
    return labeled_clusters
