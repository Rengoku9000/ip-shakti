"""
Formulation Classifier for IP-SAKTI Sahayak
Phase 2B.1 — Formulation & Query Classification + Jurisdiction Routing.

Classifies Ayurvedic/herbal formulations into controlled categories
(AYURVEDIC_FORMULATION, CLASSICAL_FORMULATION, PROPRIETARY_FORMULATION,
SINGLE_DRUG, POLYHERBAL_FORMULATION, UNKNOWN, NOT_APPLICABLE).
Carefully distinguishes evidentiary basis: USER_ASSERTED vs EVIDENCE_SUPPORTED vs UNKNOWN.
Never outputs legal fact or authoritative validity without external evidence.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict

import config
from .vocabularies import FormulationType, FormulationBasis, EntityType
from .entity_extractor import Entity, normalize_query, FORMULATION_SIGNALS


@dataclass
class FormulationClassification:
    """Structured representation of formulation classification."""
    detected: bool
    type: str = FormulationType.NOT_APPLICABLE.value
    basis: str = FormulationBasis.UNKNOWN.value
    confidence: float = 0.0
    ingredients: List[str] = field(default_factory=list)
    dosage_forms: List[str] = field(default_factory=list)
    explanation: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FormulationClassifier:
    """
    Deterministic rule-based formulation classifier evaluating botanical counts,
    explicit user assertions, classical/modern dosage signals, and proprietary indicators.
    """

    def __init__(self, confidence_threshold: Optional[float] = None):
        self.threshold = confidence_threshold or config.FORMULATION_CONFIDENCE_THRESHOLD

        # Explicit user-assertion regexes
        self.classical_assertion = re.compile(
            r"\b(classical\s+formulations?|classical\s+ayurvedic|shastric|authoritative\s+text\s+formulations?)\b",
            re.IGNORECASE
        )
        self.proprietary_assertion = re.compile(
            r"\b(proprietary\s+formulations?|patent\s+or\s+proprietary|patent\s+and\s+proprietary|proprietary\s+ayurvedic|proprietary\s+medicines?|modern\s+formulations?|novel\s+formulations?|branded\s+formulations?)\b",
            re.IGNORECASE
        )
        self.traditional_ayush_assertion = re.compile(
            r"\b(traditional\s+formulations?|ayurvedic\s+formulations?|herbal\s+formulations?|asu\s+formulations?|ayush\s+formulations?|herbal\s+medicines?|ayurvedic\s+medicines?|herbal\s+preparations?|ayurvedic\s+drugs?|herbal\s+powders?)\b",
            re.IGNORECASE
        )
        self.single_drug_assertion = re.compile(
            r"\b(single\s+drugs?|single\s+herbs?|single\s+ingredients?|monoplant|isolated\s+extracts?|single\s+botanical)\b",
            re.IGNORECASE
        )
        self.polyherbal_assertion = re.compile(
            r"\b(polyherbal|multi\s+herbs?|combination\s+of\s+herbs|multi\s+ingredients?|multiple\s+herbs?)\b",
            re.IGNORECASE
        )

        # Well-known classical polyherbal names
        self.classical_compounds = {
            "triphala", "trikatu", "chyawanprash", "avipattikar", "sitopaladi",
            "hingwashtak", "talishadi", "mahasudarshan", "yograj guggulu",
            "kaishore guggulu", "dashamoolarishta", "ashokarishta", "drakshasava"
        }

    def classify(self, query: str, entities: List[Entity]) -> FormulationClassification:
        """
        Classifies the formulation mentioned or implied in the query.
        """
        norm_query = normalize_query(query)
        explanations: List[str] = []

        # 1. Filter botanical ingredients and dosage forms
        botanicals = [e.name for e in entities if e.entity_type == EntityType.BOTANICAL.value]
        dosage_forms = [e.name for e in entities if e.entity_type == EntityType.FORMULATION_FORM.value]

        # Check if any classical compound name is directly in query
        matched_classical_compounds = [
            c for c in self.classical_compounds
            if re.search(rf"\b{re.escape(c)}\b", norm_query)
        ]

        has_formulation_signal = len(dosage_forms) > 0
        has_ingredients = len(botanicals) > 0 or len(matched_classical_compounds) > 0
        has_classical_assertion = bool(self.classical_assertion.search(norm_query))
        has_proprietary_assertion = bool(self.proprietary_assertion.search(norm_query))
        has_traditional_assertion = bool(self.traditional_ayush_assertion.search(norm_query))
        has_single_assertion = bool(self.single_drug_assertion.search(norm_query))
        has_polyherbal_assertion = bool(self.polyherbal_assertion.search(norm_query))

        # Check for non-formulation / administrative or irrelevant query
        if not (has_ingredients or has_formulation_signal or has_traditional_assertion or
                has_classical_assertion or has_proprietary_assertion or has_single_assertion or
                has_polyherbal_assertion):
            return FormulationClassification(
                detected=False,
                type=FormulationType.NOT_APPLICABLE.value,
                basis=FormulationBasis.UNKNOWN.value,
                confidence=1.0,
                ingredients=[],
                dosage_forms=[],
                explanation=["No formulation, dosage form, or botanical ingredient detected in query."]
            )

        # 2. Priority classification based on explicit evidence / assertions

        # A. Classical formulation
        if has_classical_assertion or len(matched_classical_compounds) > 0:
            comp_note = f" (named classical compound: {', '.join(matched_classical_compounds)})" if matched_classical_compounds else ""
            explanations.append(f"User query asserts or names classical Ayurvedic formulation{comp_note}.")
            return FormulationClassification(
                detected=True,
                type=FormulationType.CLASSICAL_FORMULATION.value,
                basis=FormulationBasis.USER_ASSERTED.value,
                confidence=0.88,
                ingredients=botanicals,
                dosage_forms=dosage_forms,
                explanation=explanations
            )

        # B. Proprietary formulation
        if has_proprietary_assertion:
            explanations.append("User query asserts patent or proprietary medicine / formulation.")
            return FormulationClassification(
                detected=True,
                type=FormulationType.PROPRIETARY_FORMULATION.value,
                basis=FormulationBasis.USER_ASSERTED.value,
                confidence=0.90,
                ingredients=botanicals,
                dosage_forms=dosage_forms,
                explanation=explanations
            )

        # C. Polyherbal Formulation
        if has_polyherbal_assertion or len(botanicals) >= 2:
            explanations.append(f"Multiple botanical ingredients or polyherbal assertion detected: {', '.join(botanicals)}.")
            return FormulationClassification(
                detected=True,
                type=FormulationType.POLYHERBAL_FORMULATION.value,
                basis=FormulationBasis.USER_ASSERTED.value,
                confidence=0.88,
                ingredients=botanicals,
                dosage_forms=dosage_forms,
                explanation=explanations
            )

        # D. Traditional / General Ayurvedic formulation
        if has_traditional_assertion:
            explanations.append("User query asserts traditional Ayurvedic/herbal formulation.")
            return FormulationClassification(
                detected=True,
                type=FormulationType.AYURVEDIC_FORMULATION.value,
                basis=FormulationBasis.USER_ASSERTED.value,
                confidence=0.86,
                ingredients=botanicals,
                dosage_forms=dosage_forms,
                explanation=explanations
            )

        # E. Single Drug (explicit assertion, or single botanical with no composite formulation assertion)
        if has_single_assertion or len(botanicals) == 1:
            # If accompanied by a classical dosage form (e.g. churna), it is an Ayurvedic formulation
            if has_formulation_signal and any(f in {"churna", "churnas", "kwatha", "kashaya", "asava", "arishta", "vati", "taila", "ghrita"} for f in dosage_forms):
                explanations.append(f"Single botanical '{botanicals[0]}' in classical dosage form '{dosage_forms[0]}'.")
                return FormulationClassification(
                    detected=True,
                    type=FormulationType.AYURVEDIC_FORMULATION.value,
                    basis=FormulationBasis.USER_ASSERTED.value,
                    confidence=0.85,
                    ingredients=botanicals,
                    dosage_forms=dosage_forms,
                    explanation=explanations
                )
            else:
                bot_name = botanicals[0] if botanicals else "unspecified"
                explanations.append(f"Query specifies single botanical drug/ingredient: '{bot_name}'.")
                return FormulationClassification(
                    detected=True,
                    type=FormulationType.SINGLE_DRUG.value,
                    basis=FormulationBasis.USER_ASSERTED.value,
                    confidence=0.88,
                    ingredients=botanicals,
                    dosage_forms=dosage_forms,
                    explanation=explanations
                )

        # F. Dosage form signal only
        if has_formulation_signal:
            explanations.append(f"Generic formulation dosage signal detected: {', '.join(dosage_forms)}.")
            return FormulationClassification(
                detected=True,
                type=FormulationType.AYURVEDIC_FORMULATION.value,
                basis=FormulationBasis.USER_ASSERTED.value,
                confidence=0.75,
                ingredients=botanicals,
                dosage_forms=dosage_forms,
                explanation=explanations
            )

        # G. Ambiguous or unknown
        return FormulationClassification(
            detected=True,
            type=FormulationType.UNKNOWN.value,
            basis=FormulationBasis.UNKNOWN.value,
            confidence=0.30,
            ingredients=botanicals,
            dosage_forms=dosage_forms,
            explanation=["Formulation detected but category is ambiguous or lacks distinguishing signals."]
        )


# Singleton classifier
formulation_classifier = FormulationClassifier()
