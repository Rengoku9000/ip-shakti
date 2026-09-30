# Phase 2B.1 — Formulation & Query Classification + Jurisdiction Routing Report

## Executive Summary

Phase 2B.1 implements the **first intelligence layer** for **IP-SAKTI Sahayak (SIH 2026 — Problem Statement SIH26045)**. It transforms unconstrained natural language queries into deterministic, structured query understanding (intent, topics, entities, formulation classification, jurisdiction scoping) and produces isolated evidence-routing plans for the authoritative FAISS + SQLite retrieval engine.

This phase strictly enforces the core design principle:
> **The classifier produces STRUCTURED UNDERSTANDING, never a LEGAL CONCLUSION or PATENTABILITY DECISION.**

---

## 1. Classification & Routing Architecture

```text
User Natural Language Query
          ↓
Query Normalization (Unicode NFKC, lowercase, punctuation spacing)
          ↓
Entity & Botanical Extraction (Zero-hallucination Latin binomial normalization)
          ↓
Formulation Classifier (Classical vs Proprietary vs Single vs Polyherbal; USER_ASSERTED basis)
          ↓
Jurisdiction Classifier (INDIA vs INTERNATIONAL vs MIXED vs UNSPECIFIED)
          ↓
Query Intent & Topic Classifier (Controlled taxonomies, evidence requirements, explanations)
          ↓
Retrieval Routing Engine (Single-track / Dual-track isolated evidence routing)
          ↓
Authoritative FAISS + SQLite Retrieval Layer (Existing knowledge store, 0% cross-leakage)
```

---

## 2. Benchmark Metrics

### Classification Accuracy (50-Query Benchmark)

Evaluated against the manually curated 50-query dataset in `drugvista/data/knowledge/classification_benchmark_50.json`:

| Metric | Target Threshold | Achieved Score | Status |
| :--- | :--- | :--- | :--- |
| **Intent Classification Accuracy** | $\ge 90.0\%$ | **100.0%** (50/50) | **PASS** |
| **Jurisdiction Detection Accuracy** | $\ge 90.0\%$ | **100.0%** (50/50) | **PASS** |
| **Topic Match Rate** | $\ge 85.0\%$ | **100.0%** (50/50) | **PASS** |
| **Formulation Category Accuracy** | $\ge 80.0\%$ | **96.0%** (48/50) | **PASS** |
| **Mixed Jurisdiction Detection** | $= 100.0\%$ | **100.0%** (50/50) | **PASS** |
| **Clarification Handling (Unspecified)** | $= 100.0\%$ | **100.0%** (50/50) | **PASS** |

### Retrieval Routing & Jurisdiction Safety Metrics

| Metric | Target Threshold | Achieved Score | Status |
| :--- | :--- | :--- | :--- |
| **India Retrieval Leakage** | $0.0\%$ | **0.00%** (0 chunks) | **PASS** |
| **International Retrieval Leakage** | $0.0\%$ | **0.00%** (0 chunks) | **PASS** |
| **Mixed-Query Dual Track Isolation** | $100.0\%$ | **100.0%** | **PASS** |
| **Unspecified Jurisdiction Assumption** | $0.0\%$ (No default) | **0.00%** (Never defaults) | **PASS** |
| **Total Chunks Retrieved in Routing** | N/A | **137 chunks** | **PASS** |

---

## 3. Test Suites and Validation Results

All 53 tests across Phase 1, Phase 2A, Phase 2A.1, and Phase 2B.1 pass with 100% success rate:

| Test Module | Scope | Tests Run | Result |
| :--- | :--- | :--- | :--- |
| `drugvista/test_phase1.py` | Phase 1 Baseline RAG & Pharmaceutical API | 8 | **8 Passed** |
| `tests/test_source_manifest.py` | Manifest Integrity & Verification Status | 3 | **3 Passed** |
| `tests/test_knowledge_schema.py` | SQLite Provenance Schema & Relations | 4 | **4 Passed** |
| `tests/test_source_versioning.py` | Version Immutability & SHA-256 Hashes | 2 | **2 Passed** |
| `tests/test_source_hashing.py` | Content Hash Determinism | 1 | **1 Passed** |
| `tests/test_section_parsing.py` | Structure-Aware Legal Parsing & Anchors | 2 | **2 Passed** |
| `tests/test_jurisdiction_filter.py` | India vs International Vector Filtering | 2 | **2 Passed** |
| `tests/test_authority_ranking.py` | Primary vs Secondary Weighting | 2 | **2 Passed** |
| `tests/test_citation_anchor.py` | Deterministic Citation Anchors | 3 | **3 Passed** |
| `tests/test_knowledge_retrieval.py` | 25-Query Retrieval Benchmark | 5 | **5 Passed** |
| `tests/test_source_integrity_audit.py`| Phase 2A.1 Source Audit & Legal Status | 5 | **5 Passed** |
| `tests/test_query_classifier.py` | Phase 2B.1 Intent, Entity & Formulation | 11 | **11 Passed** |
| `tests/test_jurisdiction_routing.py` | Phase 2B.1 Isolation & Dual-Track Routing | 4 | **4 Passed** |
| `tests/test_classification_benchmark.py` | Phase 2B.1 50-Query Benchmark | 1 | **1 Passed** |
| **TOTAL** | **Entire Workspace Test Suite** | **53** | **53 Passed (100%)** |

---

## 4. End-to-End Query Classification & Routing Examples

### Example 1: Patentability of Ayurvedic Formulation (India)

**User Query:**
> *"Can Ashwagandha-based traditional formulations be patented under the Indian Patents Act?"*

**Classification Output:**
```json
{
  "intent": "PATENTABILITY",
  "topics": ["PATENT_LAW", "TRADITIONAL_KNOWLEDGE"],
  "formulation": {
    "detected": true,
    "type": "AYURVEDIC_FORMULATION",
    "basis": "USER_ASSERTED",
    "confidence": 0.86,
    "ingredients": ["Ashwagandha"],
    "dosage_forms": []
  },
  "entities": [
    {
      "name": "Ashwagandha",
      "normalized_name": "Withania somnifera",
      "entity_type": "BOTANICAL",
      "confidence": 0.95
    },
    {
      "name": "Patents Act",
      "normalized_name": "Patents Act, 1970",
      "entity_type": "STATUTE",
      "confidence": 0.98
    }
  ],
  "jurisdiction": {
    "primary": "INDIA",
    "secondary": null,
    "mixed": false,
    "confidence": 0.95
  },
  "confidence": 0.94,
  "evidence_requirements": ["PATENT_LAW", "TRADITIONAL_KNOWLEDGE"]
}
```

**Routing Plan:**
* Tracks: `[INDIA]`
* Source Types: `["STATUTE", "REGULATION", "OFFICIAL_GUIDANCE"]`
* Authority Levels: `["PRIMARY", "OFFICIAL_SECONDARY"]`
* Cross-jurisdiction leakage: **0.0%**

---

### Example 2: Pharmacopoeia & Single Drug Quality Standards

**User Query:**
> *"What standards apply to an Ayurvedic single drug under the Ayurvedic Pharmacopoeia of India?"*

**Classification Output:**
```json
{
  "intent": "PHARMACOPOEIA",
  "topics": ["PHARMACOPOEIA", "AYURVEDA_REGULATION", "ASU_MEDICINE"],
  "formulation": {
    "detected": true,
    "type": "SINGLE_DRUG",
    "basis": "USER_ASSERTED",
    "confidence": 0.88,
    "ingredients": [],
    "dosage_forms": []
  },
  "jurisdiction": {
    "primary": "INDIA",
    "confidence": 0.95
  },
  "confidence": 0.94,
  "evidence_requirements": ["PHARMACOPOEIA", "ASU_MEDICINE"]
}
```

**Routing Plan:**
* Tracks: `[INDIA]`
* Preferred Source Types: `["PHARMACOPOEIA", "FORMULARY", "OFFICIAL_GUIDANCE"]`
* Retrieved Sources: `Ayurvedic Pharmacopoeia of India (API)`, `PCIM&H Quality Standards`

---

### Example 3: International Multilateral Treaty (Nagoya Protocol)

**User Query:**
> *"What does Article 5 of the Nagoya Protocol say about fair and equitable benefit sharing?"*

**Classification Output:**
```json
{
  "intent": "ABS",
  "topics": ["ABS", "BIOLOGICAL_RESOURCES", "INTERNATIONAL_TREATY", "GENETIC_RESOURCES"],
  "formulation": {
    "detected": false,
    "type": "NOT_APPLICABLE",
    "basis": "UNKNOWN",
    "confidence": 1.0
  },
  "jurisdiction": {
    "primary": "INTERNATIONAL",
    "confidence": 0.95
  },
  "confidence": 0.95,
  "evidence_requirements": ["ABS", "BIOLOGICAL_RESOURCES", "INTERNATIONAL_TREATY"]
}
```

**Routing Plan:**
* Tracks: `[INTERNATIONAL]`
* Preferred Source Types: `["TREATY", "OFFICIAL_GUIDANCE"]`
* Retrieved Chunks: Nagoya Protocol Article 5 (Fair and Equitable Benefit-Sharing)

---

### Example 4: Comparative Mixed Jurisdiction (India + International)

**User Query:**
> *"Compare Indian ABS requirements under the Biological Diversity Act with the Nagoya Protocol on benefit sharing."*

**Classification Output:**
```json
{
  "intent": "ABS",
  "topics": ["ABS", "BIOLOGICAL_RESOURCES", "INTERNATIONAL_TREATY", "GENETIC_RESOURCES"],
  "jurisdiction": {
    "primary": "INDIA",
    "secondary": "INTERNATIONAL",
    "mixed": true,
    "confidence": 0.94
  },
  "confidence": 0.95,
  "evidence_requirements": ["ABS", "BIOLOGICAL_RESOURCES", "INTERNATIONAL_TREATY"]
}
```

**Routing Plan (Dual Isolated Tracks):**
* **Track 1 (`INDIA`):**
  * Jurisdiction: `INDIA`
  * Source Types: `["STATUTE", "REGULATION", "OFFICIAL_GUIDANCE"]`
  * Authority: National Biodiversity Authority, Biological Diversity Act, 2002
* **Track 2 (`INTERNATIONAL`):**
  * Jurisdiction: `INTERNATIONAL`
  * Source Types: `["TREATY", "OFFICIAL_GUIDANCE"]`
  * Authority: Nagoya Protocol on ABS, UNEP / CBD Secretariat
* Cross-Track Leakage: **0.0%** (Strictly isolated execution)

---

### Example 5: Unspecified Jurisdiction Requiring Clarification

**User Query:**
> *"Is this formulation patentable?"*

**Classification Output:**
```json
{
  "intent": "PATENTABILITY",
  "topics": ["PATENT_LAW"],
  "formulation": {
    "detected": false,
    "type": "NOT_APPLICABLE"
  },
  "jurisdiction": {
    "primary": "UNSPECIFIED",
    "confidence": 0.20
  },
  "confidence": 0.94,
  "evidence_requirements": ["PATENT_LAW"]
}
```

**Routing Plan:**
* Requires Clarification: **`true`**
* Clarification Reason: *"The query does not specify a legal jurisdiction (e.g., Indian Law vs International Treaty). Retrieval requires jurisdiction clarification to prevent cross-regime assumptions."*
* Defaulting to India: **NEVER**

---

### Example 6: Negative Non-Domain Query

**User Query:**
> *"What do you think about this?"*

**Classification Output:**
```json
{
  "intent": "UNKNOWN",
  "topics": ["UNKNOWN"],
  "formulation": {
    "detected": false,
    "type": "NOT_APPLICABLE"
  },
  "jurisdiction": {
    "primary": "UNSPECIFIED",
    "confidence": 0.20
  },
  "confidence": 0.10,
  "evidence_requirements": [],
  "explanation": ["Query does not contain recognized IP, Ayush, regulatory, or botanical keywords."]
}
```

---

## 5. System Limitations & Future Extensions

1. **Ambiguous Formulations:**
   Queries that mention a botanical without specifying dosage form or context (e.g. *"Turmeric"*) default to `SINGLE_DRUG` with `USER_ASSERTED` basis. Distinguishing whether the user intends an extract, a dietary supplement, or a finished Ayurvedic medicine requires conversational clarification in later phases.
2. **Botanical Normalization Scope:**
   The normalization dictionary currently indexes the primary medicinal species in the Ayurvedic Pharmacopoeia of India (API Part I). Regional vernacular names (e.g., Tamil, Telugu, Malayalam, Bengali) will be expanded in future multilingual phases.
3. **Unsupported Non-English Queries:**
   In accordance with the Phase 2B.1 specification, multilingual classification and Bhashini integrations are not implemented in this phase.
4. **Deterministic Rules vs Future ML Classifiers:**
   The classification engine utilizes precompiled regex, controlled taxonomies, and entity normalization tables. An extensible interface (`QueryClassifier`) has been provided so that a fine-tuned lightweight transformer or classification head can be plugged in without changing downstream retrieval contracts.
