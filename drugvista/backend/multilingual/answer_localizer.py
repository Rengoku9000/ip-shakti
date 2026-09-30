"""
Answer Localizer for DrugVista / IP-SAKTI Sahayak
Localizes generated reasoning results into the requested target language
(Hindi or Kannada) while preserving immutable citation provenance,
statutory section identifiers, and machine-readable reasoning status.
"""
import copy
import logging
from typing import Dict, Any, Tuple
try:
    from reasoning.evidence_model import (
        StructuredReasoningResult,
        Claim,
        EvidenceItem
    )
    from models import CitationSource
except ImportError:
    from ..reasoning.evidence_model import (
        StructuredReasoningResult,
        Claim,
        EvidenceItem
    )
    from ..models import CitationSource
from .language_policy import SupportedLanguage
from .translation_service import translation_service

logger = logging.getLogger(__name__)


class AnswerLocalizer:
    """
    Safely localizes reasoning outputs into Hindi or Kannada.
    Enforces citation anchor and legal status immutability.
    """

    def localize(
        self,
        reasoning: StructuredReasoningResult,
        target_language: str
    ) -> Tuple[StructuredReasoningResult, Dict[str, Any]]:
        """
        Produce a localized copy of the structured reasoning result.
        Does not mutate the original canonical object.
        """
        tgt = (target_language or SupportedLanguage.ENGLISH.value).upper()

        localization_meta = {
            "requested_language": tgt,
            "answer_language": tgt if tgt in {SupportedLanguage.HINDI.value, SupportedLanguage.KANNADA.value} else SupportedLanguage.ENGLISH.value,
            "translation_used": False
        }

        # If target language is English or unsupported, return canonical reasoning as-is
        if tgt == SupportedLanguage.ENGLISH.value or tgt not in {
            SupportedLanguage.HINDI.value, SupportedLanguage.KANNADA.value
        }:
            return reasoning, localization_meta

        localization_meta["translation_used"] = True

        # Deep copy to ensure canonical objects remain unmodified
        loc_res = copy.deepcopy(reasoning)

        # 1. Localize Summary
        if loc_res.summary:
            loc_res.summary = translation_service.translate(
                loc_res.summary,
                source_language="ENGLISH",
                target_language=tgt
            )

        # 2. Localize Source Facts (preserve exact citation anchors and chunk references)
        loc_facts = []
        for fact in loc_res.source_facts:
            loc_text = translation_service.translate(
                fact.text,
                source_language="ENGLISH",
                target_language=tgt
            )
            loc_qual = translation_service.translate(
                fact.qualification,
                source_language="ENGLISH",
                target_language=tgt
            ) if fact.qualification else None

            loc_facts.append(
                Claim(
                    text=loc_text,
                    type=fact.type,
                    support_nature=fact.support_nature,
                    citations=list(fact.citations),
                    supporting_evidence=list(fact.supporting_evidence),
                    jurisdiction=fact.jurisdiction,
                    legal_status=fact.legal_status,
                    qualification=loc_qual
                )
            )
        loc_res.source_facts = loc_facts

        # 3. Localize Interpretations (preserve exact citations and qualification)
        loc_interps = []
        for interp in loc_res.interpretations:
            loc_text = translation_service.translate(
                interp.text,
                source_language="ENGLISH",
                target_language=tgt
            )
            loc_qual = translation_service.translate(
                interp.qualification,
                source_language="ENGLISH",
                target_language=tgt
            ) if interp.qualification else None

            loc_interps.append(
                Claim(
                    text=loc_text,
                    type=interp.type,
                    support_nature=interp.support_nature,
                    citations=list(interp.citations),
                    supporting_evidence=list(interp.supporting_evidence),
                    jurisdiction=interp.jurisdiction,
                    legal_status=interp.legal_status,
                    qualification=loc_qual
                )
            )
        loc_res.interpretations = loc_interps

        # 4. Localize Uncertainties & Clarification Needs
        loc_res.uncertainties = [
            translation_service.translate(u, "ENGLISH", tgt)
            for u in loc_res.uncertainties
        ]
        loc_res.clarification_needed = [
            translation_service.translate(c, "ENGLISH", tgt)
            for c in loc_res.clarification_needed
        ]

        # 5. IMMUTABILITY VERIFICATION:
        # Verify that citation anchors, source_ids, jurisdictions, and legal_status were NOT altered
        for orig_e, loc_e in zip(reasoning.evidence_items, loc_res.evidence_items):
            assert orig_e.citation_anchor == loc_e.citation_anchor, "Citation anchor mutation detected!"
            assert orig_e.source_id == loc_e.source_id, "Source ID mutation detected!"
            assert orig_e.jurisdiction == loc_e.jurisdiction, "Jurisdiction mutation detected!"
            assert orig_e.legal_status == loc_e.legal_status, "Legal status mutation detected!"

        for orig_c, loc_c in zip(reasoning.citations, loc_res.citations):
            assert orig_c.citation_anchor == loc_c.citation_anchor, "Citation source anchor mutation detected!"
            assert orig_c.source_id == loc_c.source_id, "Citation source ID mutation detected!"

        # Machine-readable status remains identical (e.g. EVIDENCE_SUPPORTED)
        loc_res.status = reasoning.status
        loc_res.human_review = reasoning.human_review
        loc_res.sufficiency = reasoning.sufficiency

        logger.info(f"Answer successfully localized to {tgt} (status: {loc_res.status})")
        return loc_res, localization_meta


# Singleton localizer
answer_localizer = AnswerLocalizer()
