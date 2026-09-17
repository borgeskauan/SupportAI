"""The deterministic demo must exercise real grouping and FAQ generation."""

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from backend.core.embeddings import format_for_embedding
from backend.core.faq_generation import FAQGenerationService
from backend.models import IssueFamily, SupportRecord
from backend.providers.mock_llm import MockLLM
from backend.providers.mock_provider import MockEmbeddingProvider
from backend.startup import (
    build_issue_families,
    generate_embeddings_and_cluster,
    generate_labels_for_clusters,
)


@pytest.fixture
def records():
    fixture = Path(__file__).parents[1] / "demo" / "scenario.json"
    return [SupportRecord.model_validate(r) for r in json.loads(fixture.read_text())["records"]]


@pytest.mark.parametrize("dimension", [16, 768])
def test_receipt_vectors_are_repeatable_distinct_and_similar(records, dimension):
    provider = MockEmbeddingProvider(dimension=dimension)
    texts = [format_for_embedding(r) for r in records]
    vectors = np.array(provider.embed_batch(texts))
    assert vectors.shape == (6, dimension)
    assert np.isfinite(vectors).all()
    assert provider.embed_batch(texts) == vectors.tolist()
    normalized = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    similarity = normalized @ normalized.T
    receipt_pairs = similarity[:3, :3][np.triu_indices(3, k=1)]
    assert np.all(receipt_pairs > 0.90)
    assert np.all(receipt_pairs < 0.99)  # Not identical vectors or rounded 100% confidence.
    assert np.max(similarity[:3, 3:]) < 0.70  # Unrelated cases must not join the demo.


def test_receipts_group_together_and_unrelated_cases_stay_out(records):
    settings = SimpleNamespace(CLUSTERING_SIMILARITY_THRESHOLD=0.90, CLUSTERING_MIN_CLUSTER_SIZE=3)
    _, clusters = generate_embeddings_and_cluster(records, MockEmbeddingProvider(), settings)
    assert len(clusters) == 1
    assert set(clusters[0].record_ids) == {"receipt_01", "receipt_02", "receipt_03"}
    labeled = generate_labels_for_clusters(clusters, records, MockLLM())
    family = build_issue_families(labeled, records)[0]
    assert family.issue_family_label == "Missing receipt after successful payment"
    draft = FAQGenerationService(MockLLM()).generate_faq_draft(family)
    assert draft.faq.title == "My payment went through. Where is my receipt?"


@pytest.fixture
def family(records):
    return IssueFamily(
        issue_family_label="Missing receipt after successful payment",
        supporting_case_ids=[r.id for r in records[:3]],
        confidence_score=0.95,
        records=records[:3],
    )


def test_real_pipeline_generates_receipt_answer_with_distinct_evidence(family):
    assert family.issue_family_label == "Missing receipt after successful payment"
    draft = FAQGenerationService(MockLLM()).generate_faq_draft(family)
    assert draft.faq.title == "My payment went through. Where is my receipt?"
    assert len({e.summary for e in draft.supporting_evidence}) == 3
    assert {e.source_type for e in draft.supporting_evidence} == {"ticket", "chat_log", "escalation"}
    answer = " ".join(draft.faq.step_by_step_fix).lower()
    for evidence in ["spam", "order reference", "payment", "delay", "email address", "resend"]:
        assert evidence in answer
    assert "not a reason to repeat a confirmed payment" in " ".join(draft.faq.edge_cases)
    assert "refresh" not in answer
    assert "minutes" not in answer
    assert 0.90 < draft.confidence_score < 0.99


def test_changed_resolution_does_not_get_scripted_answer(family):
    family.records[0].resolution_text = "The payment failed and no receipt was issued."
    draft = FAQGenerationService(MockLLM()).generate_faq_draft(family)
    assert draft.faq.title != "My payment went through. Where is my receipt?"


@pytest.mark.parametrize("separator", ["\n", "\\n"])
def test_multiline_resolution_cannot_hide_conflicting_evidence(family, separator):
    family.records[0].resolution_text += separator + "Correction: payment actually failed and no receipt exists."
    draft = FAQGenerationService(MockLLM()).generate_faq_draft(family)
    assert draft.faq.title != "My payment went through. Where is my receipt?"


@pytest.mark.parametrize("separator", ["\n", "\\n"])
def test_multiline_extra_case_cannot_be_ignored(family, records, separator):
    unrelated = records[3].model_copy(deep=True)
    unrelated.case_summary += separator + "The customer was unable to sign in."
    family.records.append(unrelated)
    draft = FAQGenerationService(MockLLM()).generate_faq_draft(family)
    assert draft.faq.title != "My payment went through. Where is my receipt?"


def test_multiline_summary_does_not_get_receipt_label(records):
    from backend.core.labeling import LABEL_GENERATION_PROMPT

    records[0].case_summary += "\nCorrection: the payment failed."
    summaries = "\n".join(f"{i}. {record.case_summary}" for i, record in enumerate(records[:3], 1))
    assert MockLLM().generate(LABEL_GENERATION_PROMPT.format(cluster_summaries=summaries)) != "Missing receipt after successful payment"


def test_extra_unrelated_case_does_not_get_scripted_answer(family, records):
    family.records.append(records[3])
    draft = FAQGenerationService(MockLLM()).generate_faq_draft(family)
    assert draft.faq.title != "My payment went through. Where is my receipt?"


def test_partial_receipt_evidence_uses_fallback(family):
    family.records.pop()
    draft = FAQGenerationService(MockLLM()).generate_faq_draft(family)
    assert draft.faq.title != "My payment went through. Where is my receipt?"


def test_receipt_answer_does_not_depend_on_case_order(family):
    family.records.reverse()
    draft = FAQGenerationService(MockLLM()).generate_faq_draft(family)
    assert draft.faq.title == "My payment went through. Where is my receipt?"


def test_demo_workspace_preserves_user_configuration_and_data(tmp_path):
    from backend.demo.__main__ import prepare_demo

    source = tmp_path / "source"
    source.mkdir()
    (source / "data").mkdir()
    (source / "data" / "user.json").write_text('[{"id":"user-data"}]')
    (source / ".env").write_text("LLM_PROVIDER=gemini\nGEMINI_API_KEY=synthetic-test-secret\n")
    (source / "main.py").write_text("# application source\n")
    destination = tmp_path / "demo"
    prepare_demo(source, destination)

    assert not (destination / "backend" / ".env").exists()
    assert not (destination / "backend" / "data" / "user.json").exists()
    copied = json.loads((destination / "backend" / "data" / "demo.json").read_text())
    assert len(copied) == 6
    assert len({r["case_summary"] for r in copied}) == 6
    assert (source / "data" / "user.json").read_text() == '[{"id":"user-data"}]'
    assert "synthetic-test-secret" in (source / ".env").read_text()
    assert (destination / "backend" / "main.py").read_text() == "# application source\n"
    with pytest.raises(FileExistsError):
        prepare_demo(source, destination)  # Never merge into an existing workspace.


def test_unknown_inputs_keep_generic_mock_behavior():
    provider = MockEmbeddingProvider(dimension=16)
    assert provider.embed("") == [0.0] * 16
    assert provider.embed("password reset") != provider.embed("delivery tracking")
    assert MockLLM().generate("1. Password reset link expired") != "Missing receipt after successful payment"
    assert MockLLM().generate("No numbered cases") == "Support Issues"
