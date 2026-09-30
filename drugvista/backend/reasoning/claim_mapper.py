"""
Claim Mapper and Evidence Chain Generator for IP-SAKTI Sahayak
Phase 2B.2 — Evidence-Based Reasoning & Cited Answer Generation.

Extracts structured claims from authoritative evidence chunks, rigorously
distinguishes SOURCE_FACT from INTERPRETATION, and tracks DIRECT vs INFERRED
evidence connections in an inspectable evidence chain.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from classification import QueryClassification
from .evidence_model import (
    Claim,
    ClaimType,
    SupportNature,
    EvidenceItem,
    EvidenceChainItem,
    ReasoningStatus
)


class ClaimMapper:
    """
    Constructs deterministic, evidence-bound claims from retrieved authoritative chunks
    and builds explicit, inspectable evidence chains.
    """

    def map_claims(
        self,
        query: str,
        classification: QueryClassification,
        evidence_items: List[EvidenceItem]
    ) -> Tuple[List[Claim], List[Claim], List[EvidenceChainItem]]:
        """
        Extracts source facts and interpretations from retrieved evidence items.
        Returns: (source_facts, interpretations, evidence_chain).
        """
        source_facts: List[Claim] = []
        interpretations: List[Claim] = []
        evidence_chain: List[EvidenceChainItem] = []

        if not evidence_items:
            return source_facts, interpretations, evidence_chain

        for item in evidence_items:
            chunk_content = item.text.strip()
            anchor = item.citation_anchor
            chunk_id = item.chunk_id
            jur = item.jurisdiction
            status = item.legal_status

            # Extract key sentences or summary clause from chunk for SOURCE_FACT
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", chunk_content) if len(s.strip()) > 20]
            if not sentences:
                sentences = [chunk_content[:200]]

            # Primary source fact directly supported by retrieved text
            fact_text = f"According to {anchor}, {sentences[0]}"
            # Ensure proper qualification if treaty is not in force or historical
            qualification = None
            if status in {"ADOPTED", "NOT_IN_FORCE"}:
                qualification = "Adopted international treaty provision; not yet entered into force as binding domestic law."
            elif "HISTORICAL" in (item.verification_status or "").upper():
                qualification = "Historical statutory record; superseded or historical version."

            fact_claim = Claim(
                text=fact_text,
                supporting_evidence=[chunk_id],
                type=ClaimType.SOURCE_FACT.value,
                support_nature=SupportNature.DIRECT.value,
                citations=[anchor],
                jurisdiction=jur,
                legal_status=status,
                qualification=qualification
            )
            source_facts.append(fact_claim)

            # Inferred interpretation applying the source fact to the user's specific context
            interp_text = self._build_interpretation(classification, item, sentences[0])
            interp_claim = Claim(
                text=interp_text,
                supporting_evidence=[chunk_id],
                type=ClaimType.INTERPRETATION.value,
                support_nature=SupportNature.INFERRED.value,
                citations=[anchor],
                jurisdiction=jur,
                legal_status=status,
                qualification=qualification
            )
            interpretations.append(interp_claim)

            # Build inspectable evidence chain entry
            chain_item = EvidenceChainItem(
                claim=fact_text,
                evidence=[{
                    "chunk_id": chunk_id,
                    "citation_anchor": anchor,
                    "support": "direct",
                    "jurisdiction": jur,
                    "authority": item.authority,
                    "legal_status": status
                }],
                interpretation=interp_text,
                support_level=ReasoningStatus.EVIDENCE_SUPPORTED.value
            )
            evidence_chain.append(chain_item)

        return source_facts, interpretations, evidence_chain

    def _build_interpretation(
        self,
        classification: QueryClassification,
        item: EvidenceItem,
        source_sentence: str
    ) -> str:
        """
        Formulates a careful, non-verdict interpretation connecting the source
        to the user's query context.
        """
        formulation_type = classification.formulation.type
        ingredients = classification.formulation.ingredients
        jur = item.jurisdiction

        subject_parts = []
        if ingredients:
            subject_parts.append(f"ingredients such as {', '.join(ingredients)}")
        if formulation_type not in {"NOT_APPLICABLE", "UNKNOWN"}:
            subject_parts.append(f"a formulation categorized as {formulation_type.lower().replace('_', ' ')}")

        subject_desc = f" ({' involving '.join(subject_parts)})" if subject_parts else ""

        if jur == "INDIA":
            return (
                f"Under Indian law, the provisions of {item.citation_anchor} indicate that inquiries "
                f"concerning this subject matter{subject_desc} are governed by the statutory requirements "
                f"specified above, which patent examiners or regulatory authorities evaluate on a case-by-case basis."
            )
        elif jur == "INTERNATIONAL":
            status_note = " (as an adopted multilateral instrument)" if item.legal_status in {"ADOPTED", "NOT_IN_FORCE"} else ""
            return (
                f"At the international level, {item.citation_anchor}{status_note} establishes multilateral standards "
                f"relevant to genetic resources and traditional knowledge{subject_desc}, requiring compliance with "
                f"applicable sovereign disclosure and benefit-sharing principles."
            )
        else:
            return (
                f"Based on {item.citation_anchor}, this provision is relevant to analyzing the regulatory "
                f"parameters surrounding the user's inquiry{subject_desc}."
            )


# Singleton mapper
claim_mapper = ClaimMapper()
