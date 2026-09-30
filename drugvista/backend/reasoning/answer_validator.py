"""
Answer Validator and Unsupported Claim Detector for IP-SAKTI Sahayak
Phase 2B.2 — Evidence-Based Reasoning & Cited Answer Generation.

Scrutinizes all generated claims against retrieved evidence chunks before final response formatting.
Detects and filters unsupported statutory references, fabricated citations, cross-jurisdiction
leakage, and definitive legal verdicts.
Ensures Unsupported Claim Rate = 0.0% on authoritative knowledge.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from .evidence_model import Claim, ClaimType, EvidenceItem


@dataclass
class ValidationReport:
    """Detailed audit report of generated claims against authoritative evidence."""
    total_claims: int
    validated_claims: int
    unsupported_claims: List[Claim] = field(default_factory=list)
    unsupported_claim_rate: float = 0.0
    citation_accuracy: float = 100.0
    forbidden_verdicts_caught: int = 0
    jurisdiction_mismatches_caught: int = 0
    status_mismatches_caught: int = 0
    passed: bool = True


class AnswerValidator:
    """
    Validates that every claim made in the reasoning output has concrete,
    traceable grounding in the retrieved authoritative evidence chunks.
    """

    def __init__(self):
        # Forbidden definitive legal advice patterns (Section 20)
        self.forbidden_verdict_patterns = [
            re.compile(r"\b(will\s+be\s+granted|guaranteed\s+to\s+pass|definitely\s+patentable|you\s+are\s+legally\s+compliant|patent\s+will\s+be\s+rejected|guaranteed\s+approval)\b", re.IGNORECASE),
            re.compile(r"\b(i\s+advise\s+you\s+to|legal\s+verdict\s+is|final\s+legal\s+determination)\b", re.IGNORECASE)
        ]

        # Specific provision citation pattern (e.g., Section 3(p), Article 5, Rule 161)
        self.provision_pattern = re.compile(
            r"\b(section\s+\d+[\(\)\w]*|article\s+\d+[\(\)\w]*|rule\s+\d+[\(\)\w]*|schedule\s+[a-z]+)\b",
            re.IGNORECASE
        )

    def validate_claims(
        self,
        claims: List[Claim],
        evidence_items: List[EvidenceItem],
        target_jurisdiction: Optional[str] = None
    ) -> Tuple[List[Claim], ValidationReport]:
        """
        Validates claims against the evidence pool. Filters out unsupported claims
        and qualifies ambiguous statements.
        """
        if not claims:
            return [], ValidationReport(
                total_claims=0,
                validated_claims=0,
                unsupported_claim_rate=0.0,
                citation_accuracy=100.0,
                passed=True
            )

        evidence_by_id = {item.chunk_id: item for item in evidence_items}
        evidence_by_anchor = {item.citation_anchor.lower(): item for item in evidence_items}

        validated: List[Claim] = []
        unsupported: List[Claim] = []
        forbidden_caught = 0
        jur_mismatches = 0
        status_mismatches = 0
        citation_matches = 0

        for claim in claims:
            is_valid = True
            claim_text = claim.text

            # 1. Evidence Grounding Check (Does supporting evidence exist in pool?)
            has_grounding = False
            matched_items: List[EvidenceItem] = []

            for ref in claim.supporting_evidence:
                if ref in evidence_by_id:
                    has_grounding = True
                    matched_items.append(evidence_by_id[ref])
                elif ref.lower() in evidence_by_anchor:
                    has_grounding = True
                    matched_items.append(evidence_by_anchor[ref.lower()])

            if not has_grounding:
                is_valid = False
                unsupported.append(claim)
                continue

            # 2. Citation Accuracy Check (Are cited anchors genuinely present?)
            claim_citations_valid = True
            for cit in claim.citations:
                if cit.lower() in evidence_by_anchor or any(cit in item.citation_anchor for item in matched_items):
                    citation_matches += 1
                else:
                    claim_citations_valid = False
                    is_valid = False

            if not claim_citations_valid:
                unsupported.append(claim)
                continue

            # 3. Statutory Provision Verification (No hallucinated section numbers)
            mentioned_provisions = self.provision_pattern.findall(claim_text)
            for prov in mentioned_provisions:
                prov_norm = prov.lower().replace(" ", "")
                # Provision must appear in at least one matched evidence item text, label, or anchor
                prov_found_in_evidence = any(
                    prov_norm in item.text.lower().replace(" ", "") or
                    prov_norm in item.citation_anchor.lower().replace(" ", "")
                    for item in matched_items
                )
                if not prov_found_in_evidence:
                    # Hallucinated provision number!
                    is_valid = False
                    unsupported.append(claim)
                    break

            if not is_valid:
                continue

            # 4. Forbidden Legal Verdict Check (Section 20)
            has_forbidden_verdict = any(p.search(claim_text) for p in self.forbidden_verdict_patterns)
            if has_forbidden_verdict:
                forbidden_caught += 1
                # Qualify claim instead of asserting definitive legal advice
                qualified_text = self._qualify_forbidden_claim(claim_text)
                claim.text = qualified_text
                claim.type = ClaimType.INTERPRETATION.value
                claim.qualification = "Qualified: Regulatory decisions depend on statutory examination by the competent authority."

            # 5. Jurisdiction Consistency Check
            if target_jurisdiction and target_jurisdiction != "UNSPECIFIED":
                # Ensure claim jurisdiction aligns with matched items
                for item in matched_items:
                    if target_jurisdiction in {"INDIA", "INTERNATIONAL"} and item.jurisdiction != target_jurisdiction:
                        jur_mismatches += 1
                        is_valid = False
                        break

            if not is_valid:
                unsupported.append(claim)
                continue

            # 6. Legal Status Check (Treaty not in force or Historical)
            for item in matched_items:
                if item.legal_status in {"ADOPTED", "NOT_IN_FORCE"}:
                    if "binding indian law" in claim_text.lower() or "in force in india" in claim_text.lower():
                        status_mismatches += 1
                        claim.text = claim_text.replace("binding Indian law", "an adopted international treaty (not yet in force)")
                        claim.qualification = "Adopted international treaty provision; not in force as binding domestic law."
                elif "HISTORICAL" in (item.verification_status or "").upper():
                    if "current law" in claim_text.lower() or "currently applicable" in claim_text.lower():
                        status_mismatches += 1
                        claim.text = claim_text.replace("current law", "historical legal framework (superseded)")
                        claim.qualification = "Historical source; superseded by subsequent legislation."

            validated.append(claim)

        total = len(claims)
        unsupported_count = len(unsupported)
        unsupported_rate = (unsupported_count / total * 100) if total > 0 else 0.0
        cit_acc = (citation_matches / max(len(claims), 1) * 100) if total > 0 else 100.0

        report = ValidationReport(
            total_claims=total,
            validated_claims=len(validated),
            unsupported_claims=unsupported,
            unsupported_claim_rate=round(unsupported_rate, 2),
            citation_accuracy=round(min(100.0, cit_acc), 2),
            forbidden_verdicts_caught=forbidden_caught,
            jurisdiction_mismatches_caught=jur_mismatches,
            status_mismatches_caught=status_mismatches,
            passed=(unsupported_count == 0)
        )

        return validated, report

    def _qualify_forbidden_claim(self, text: str) -> str:
        """Replace absolute legal advice with evidence-based statutory relevance."""
        text = re.sub(
            r"\b(will\s+be\s+granted|guaranteed\s+to\s+pass|definitely\s+patentable)\b",
            "may be eligible for consideration subject to statutory examination",
            text,
            flags=re.IGNORECASE
        )
        text = re.sub(
            r"\b(you\s+are\s+legally\s+compliant)\b",
            "the provided parameters align with relevant regulatory provisions",
            text,
            flags=re.IGNORECASE
        )
        text = re.sub(
            r"\b(patent\s+will\s+be\s+rejected)\b",
            "the application may face statutory objections under the cited provisions",
            text,
            flags=re.IGNORECASE
        )
        return text


# Singleton validator
answer_validator = AnswerValidator()
