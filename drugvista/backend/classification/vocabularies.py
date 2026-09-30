"""
Controlled Vocabularies and Taxonomies for IP-SAKTI Sahayak
Phase 2B.1 — Formulation & Query Classification + Jurisdiction Routing.

Defines standardized enums for intents, topics, formulation types,
entity types, and jurisdiction categorizations.
"""
from enum import Enum


class QueryIntent(str, Enum):
    """Controlled vocabulary of supported user query intents."""
    GENERAL_INFORMATION = "GENERAL_INFORMATION"
    FORMULATION_INFORMATION = "FORMULATION_INFORMATION"
    PATENTABILITY = "PATENTABILITY"
    TRADITIONAL_KNOWLEDGE = "TRADITIONAL_KNOWLEDGE"
    REGULATORY_COMPLIANCE = "REGULATORY_COMPLIANCE"
    PHARMACOPOEIA = "PHARMACOPOEIA"
    FORMULATION_CLASSIFICATION = "FORMULATION_CLASSIFICATION"
    ABS = "ABS"
    INTERNATIONAL_IP = "INTERNATIONAL_IP"
    SOURCE_LOOKUP = "SOURCE_LOOKUP"
    UNKNOWN = "UNKNOWN"


class Topic(str, Enum):
    """Subject matter topic tags for retrieval routing and context scoping."""
    PATENT_LAW = "PATENT_LAW"
    TRADEMARK = "TRADEMARK"
    TRADITIONAL_KNOWLEDGE = "TRADITIONAL_KNOWLEDGE"
    GENETIC_RESOURCES = "GENETIC_RESOURCES"
    BIOLOGICAL_RESOURCES = "BIOLOGICAL_RESOURCES"
    ABS = "ABS"
    AYURVEDA_REGULATION = "AYURVEDA_REGULATION"
    ASU_MEDICINE = "ASU_MEDICINE"
    PHARMACOPOEIA = "PHARMACOPOEIA"
    FORMULARY = "FORMULARY"
    LICENSING = "LICENSING"
    GMP = "GMP"
    INTERNATIONAL_TREATY = "INTERNATIONAL_TREATY"
    UNKNOWN = "UNKNOWN"


class FormulationType(str, Enum):
    """Classification of Ayurvedic/herbal drug formulations."""
    AYURVEDIC_FORMULATION = "AYURVEDIC_FORMULATION"
    CLASSICAL_FORMULATION = "CLASSICAL_FORMULATION"
    PROPRIETARY_FORMULATION = "PROPRIETARY_FORMULATION"
    SINGLE_DRUG = "SINGLE_DRUG"
    POLYHERBAL_FORMULATION = "POLYHERBAL_FORMULATION"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class FormulationBasis(str, Enum):
    """Evidentiary basis for the formulation classification."""
    USER_ASSERTED = "USER_ASSERTED"
    EVIDENCE_SUPPORTED = "EVIDENCE_SUPPORTED"
    UNKNOWN = "UNKNOWN"


class EntityType(str, Enum):
    """Types of extracted entities from queries."""
    BOTANICAL = "BOTANICAL"
    FORMULATION_FORM = "FORMULATION_FORM"
    STATUTE = "STATUTE"
    REGULATORY_BODY = "REGULATORY_BODY"
    TREATY = "TREATY"
    GENERAL = "GENERAL"


class JurisdictionChoice(str, Enum):
    """Strictly partitioned jurisdictions."""
    INDIA = "INDIA"
    INTERNATIONAL = "INTERNATIONAL"
    UNSPECIFIED = "UNSPECIFIED"
