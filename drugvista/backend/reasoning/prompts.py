"""
Reasoning Prompts and Offline Synthesis Templates for IP-SAKTI Sahayak
Phase 2B.2 — Evidence-Based Reasoning & Cited Answer Generation.

Provides structured system rules for LLM generation and deterministic,
zero-hallucination offline reasoning synthesis when running in offline mode.
"""
import json
from typing import List, Dict, Any, Optional

from classification import QueryClassification
from .evidence_model import EvidenceItem, Claim, ClaimType, ReasoningStatus, SufficiencyState


SYSTEM_REASONING_PROMPT = """You are IP-SAKTI Sahayak, an authoritative, source-cited assistant for Intellectual Property and regulatory guidance in Ayurveda.

SYSTEM RULES (STRICT COMPLIANCE MANDATORY):
1. Use ONLY the supplied retrieved evidence. Do NOT rely on prior legal knowledge outside the provided chunks.
2. Do NOT invent laws, sections, rules, dates, case law, treaties, or citations.
3. Do NOT treat user assertions as legal facts. Mark unverified user assertions as requiring verification.
4. Internally distinguish SOURCE FACTS (directly stated in source) from MODEL INTERPRETATION (reasoning applied to user case).
5. Respect legal jurisdiction strictly. Never blend Indian law and International treaties into a single rule.
6. Respect source legal status. An ADOPTED treaty not in force must NOT be described as binding current domestic law.
7. State uncertainty explicitly whenever statutory coverage is incomplete.
8. Abstain safely when evidence is insufficient. Never fabricate conclusions to be helpful.
9. NEVER claim to have searched confidential TKDL formulation databases. Confidential TKDL records are non-public.
10. Do NOT provide definitive legal advice or guarantees (e.g., "Your patent will be granted"). Use evidence-based phrasing: "The retrieved provision indicates that...".

Output MUST strictly follow the JSON schema provided.
"""


def format_evidence_context(evidence_items: List[EvidenceItem]) -> str:
    """Format structured evidence items for the prompt."""
    if not evidence_items:
        return "No authoritative evidence retrieved."

    blocks = []
    for i, item in enumerate(evidence_items, 1):
        status_note = f" [Status: {item.legal_status}]" if item.legal_status != "IN_FORCE" else ""
        blocks.append(
            f"--- EVIDENCE ITEM [{i}] ---\n"
            f"Citation Anchor: {item.citation_anchor}\n"
            f"Source ID: {item.source_id} (Version: {item.source_version_id})\n"
            f"Authority: {item.authority} (Level: {item.authority_level})\n"
            f"Jurisdiction: {item.jurisdiction}{status_note}\n"
            f"URL: {item.source_url}\n"
            f"Content:\n{item.text}\n"
        )
    return "\n".join(blocks)


def build_offline_summary(
    classification: QueryClassification,
    source_facts: List[Claim],
    interpretations: List[Claim],
    sufficiency_state: str,
    target_jurisdiction: str
) -> str:
    """
    Deterministic synthesis for offline mode preserving evidence-based reasoning
    without LLM hallucinations.
    """
    if not source_facts:
        return "Insufficient authoritative evidence retrieved to formulate a verified regulatory explanation."

    intent = classification.intent
    topics_str = ", ".join(classification.topics)
    primary_anchor = source_facts[0].citations[0] if source_facts[0].citations else "authoritative source"

    summary_lines = [
        f"Based on authoritative {target_jurisdiction} regulatory evidence, this inquiry regarding {intent.lower().replace('_', ' ')} "
        f"is governed primarily by {primary_anchor}."
    ]

    if len(source_facts) > 1:
        secondary_anchor = source_facts[1].citations[0] if source_facts[1].citations else "secondary provisions"
        summary_lines.append(
            f"Additionally, {secondary_anchor} provides relevant statutory parameters concerning {topics_str.lower().replace('_', ' ')}."
        )

    if classification.formulation.detected:
        f_type = classification.formulation.type.lower().replace('_', ' ')
        summary_lines.append(
            f"The formulation context indicates a {f_type} (user-asserted), which requires verification against pharmacopoeial monographs."
        )

    summary_lines.append(
        "Formal determination of patentability, biological diversity approval, or manufacturing licensing is exercised solely by the competent statutory authorities."
    )

    return " ".join(summary_lines)
