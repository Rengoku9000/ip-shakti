# DrugVista → IP-SAKTI Sahayak
# Phase 2B.2 — Evidence-Based Reasoning & Cited Answer Generation Report

## 1. Executive Summary

Phase 2B.2 completes the authoritative intelligence layer for IP-SAKTI Sahayak (SIH 2026 Problem Statement SIH26045). Building on the deterministic knowledge corpus (Phase 2A), source integrity audit (Phase 2A.1), and formulation/query classification and routing (Phase 2B.1), this phase implements **evidence-bounded reasoning over authoritative legal and regulatory provisions**.

The core operational principle is **NO EVIDENCE → NO CLAIM**:
* The reasoning engine strictly bounds all generated claims to retrieved, verified statutory and regulatory text.
* Source facts (`SOURCE_FACT`) are programmatically segregated from interpretations (`INTERPRETATION`).
* Every substantive factual claim is mapped to verified citation anchors originating from SQLite provenance metadata.
* Unsupported claims, hallucinated statutory sections, and definitive legal guarantees are systematically detected and eliminated.
* Safe abstention (`INSUFFICIENT_EVIDENCE`), clarification handling (`CLARIFICATION_REQUIRED`), and escalation (`HUMAN_REVIEW_RECOMMENDED`) protect users from misguidance.
* Both online LLM provider reasoning and deterministic offline fallback modes operate with zero cross-jurisdiction leakage.

---

## 2. End-to-End Reasoning Architecture

```
User Question
      ↓
[Query & Formulation Classification]  (Phase 2B.1)
  - Intent detection (100%)
  - Jurisdiction detection (100%)
  - Topic matching (100%)
  - Formulation context & user-assertion flagging
      ↓
[Multi-Track Retrieval Routing]       (Phase 2B.1)
  - Isolated tracks: INDIA vs INTERNATIONAL
  - Domain and authority prioritization
      ↓
[Authoritative Retrieval]             (Phase 2A / 2A.1)
  - FAISS similarity + SQLite provenance metadata
  - Exact provision anchor boost (+0.25)
      ↓
[Evidence Model & Pre-Abstention Audit] (Phase 2B.2)
  - EvidenceItem encapsulation
  - TKDL confidential access check
  - Unspecified jurisdiction clarification check
      ↓
[Evidence Sufficiency Evaluation]     (Phase 2B.2)
  - Primary vs Secondary authority auditing
  - In-force vs adopted/historical legal status audit
  - Multi-track jurisdiction isolation check
      ↓
[Structured Reasoning Engine]          (Phase 2B.2)
  - Direct evidence vs inferred conclusions
  - Formulation verification (USER_ASSERTED vs EVIDENCE_SUPPORTED)
  - Deterministic offline fallback / Schema-constrained online provider
      ↓
[Answer Validation & Guardrails]      (Phase 2B.2)
  - Hallucinated provision audit (Regex vs Retrieved anchors)
  - Citation provenance verification
  - Forbidden definitive legal verdict qualification
  - Unsupported claim elimination (Target: 0% Unsupported Claim Rate)
      ↓
[Cited Structured Response]           (Phase 2B.2)
  - Controlled status: EVIDENCE_SUPPORTED | PARTIALLY_SUPPORTED |
                       INSUFFICIENT_EVIDENCE | CLARIFICATION_REQUIRED |
                       HUMAN_REVIEW_RECOMMENDED
  - Deterministic citations & source links
```

---

## 3. Evaluation Benchmark Results

The 30-case authoritative reasoning benchmark (`drugvista/data/knowledge/reasoning_benchmark_30.json`) spanning 10 Patent/IP cases, 10 Ayurveda Regulatory cases, 5 ABS cases, and 5 International cases was executed across all evaluation dimensions:

| Metric | Target | Result | Status |
| :--- | :--- | :--- | :--- |
| **Reasoning Status Accuracy** | $\ge 90.0\%$ | **100.0%** (30/30) | **PASSED** |
| **Required Citation Anchor Hit Rate** | $\ge 90.0\%$ | **100.0%** (30/30) | **PASSED** |
| **Total Substantive Claims Audited** | - | **300 claims** | - |
| **Unsupported Claim Rate** | **0.00%** | **0.00%** (0 unsupported) | **PASSED** |
| **Forbidden Legal Verdict Violations** | **0** | **0 violations** | **PASSED** |
| **Jurisdiction Isolation Rate** | **100.0%** | **100.0%** (0 leakage) | **PASSED** |
| **Clarification Handling Accuracy** | $\ge 95.0\%$ | **100.0%** | **PASSED** |
| **Abstention Accuracy** | $\ge 95.0\%$ | **100.0%** | **PASSED** |

### Cumulative Regression Suite

| Component | Test Suite | Tests Passed |
| :--- | :--- | :--- |
| **Phase 1** | Architecture, Hashing, Chunking, Provenance, FAISS, Domain | **8 / 8** |
| **Phase 2A / 2A.1** | Corpus Integrity, Source Versioning, Anchor Provenance | **19 / 19** |
| **Phase 2B.1** | Formulation & Query Classification, Jurisdiction Routing | **26 / 26** |
| **Phase 2B.2** | Evidence Model, Sufficiency, Claim Mapping, Citations, Guardrails, Benchmark | **27 / 27** |
| **Total Test Suite** | Full discovery (`tests/` + `drugvista/`) | **80 / 80 (100%)** |

---

## 4. Key Architectural Implementations

### 4.1 Controlled Answer Types (`ReasoningStatus`)
The system outputs strictly bounded evidence states:
1. `EVIDENCE_SUPPORTED`: Strong/adequate verified evidence directly answers the query.
2. `PARTIALLY_SUPPORTED`: Partial evidence available; key statutory facets require qualification.
3. `INSUFFICIENT_EVIDENCE`: Corpus lacks relevant verified provisions or authority is weak.
4. `CLARIFICATION_REQUIRED`: Query lacks critical legal parameters (e.g., unspecified jurisdiction).
5. `HUMAN_REVIEW_RECOMMENDED`: Triggered on confidential records requests (TKDL), material statutory conflicts, or requests for definitive legal opinions.

### 4.2 Structured Evidence Model (`EvidenceItem`)
Extends `RetrievedChunk` without textual duplication, carrying:
* `chunk_id`, `source_id`, `source_version_id`
* `title`, `authority`, `authority_level` (`PRIMARY`, `OFFICIAL_SECONDARY`, `REFERENCE`)
* `jurisdiction` (`INDIA`, `INTERNATIONAL`)
* `legal_status` (`IN_FORCE`, `AMENDED`, `ADOPTED_NOT_IN_FORCE`, `REPEALED`)
* `verification_status` (`OFFICIAL_VERIFIED`, `VERIFIED_HISTORICAL`, `UNVERIFIED`)
* `citation_anchor`, `source_url`, `retrieval_score`, `relevance_reason`

### 4.3 Direct Fact vs Inferred Interpretation (`ClaimMapper`)
Every claim generated contains a strict classification:
* `SOURCE_FACT`: Verbatim or deterministic extraction from retrieved statutory text, citing exact chunk IDs and anchor labels.
* `INTERPRETATION`: Domain reasoning contextualizing the statutory requirement to the query, explicitly accompanied by qualification statements ("Based on the retrieved provision, this may require...").

### 4.4 Answer Validation & Unsupported Claim Elimination (`AnswerValidator`)
Before returning responses to clients:
1. **Hallucination Detection**: Extracts all section, rule, article, and schedule citations in generated text using regex; flags and rejects any provision not present in the retrieved chunk metadata.
2. **Provenance Verification**: Verifies that every `supporting_evidence` ID corresponds to an actual retrieved chunk.
3. **Forbidden Ruling Stripping**: Automatically qualifies definitive assertions ("patent will be granted", "you are legally compliant") into objective evidence observations.

### 4.5 Pre-Retrieval Guardrails & Abstention (`AbstentionGuard`)
* **TKDL Confidentiality (Section 30)**: Requests seeking confidential TKDL database searches are intercepted with `HUMAN_REVIEW_RECOMMENDED` and safe abstention, clarifying that confidential prior art records are non-public.
* **Missing Jurisdiction (Section 18)**: Queries on jurisdiction-specific legal rules omitting geographic scope are halted with `CLARIFICATION_REQUIRED`.
* **Definitive Legal Guarantee Guard (Section 20)**: Intercepts requests for conclusive legal certifications.

### 4.6 Dual-Mode Execution (LLM & Deterministic Offline)
* **Online Mode**: Employs `SYSTEM_REASONING_PROMPT` containing 10 strict system rules for structured JSON generation.
* **Offline Fallback Mode**: Generates deterministic, fully cited statutory summaries directly from SQLite metadata and retrieved chunks with zero hallucination.

---

## 5. End-to-End Exemplar Outputs

### Example 1: Supported Patent Query (Section 3(p) Traditional Knowledge)
* **Query**: `"Can an Ayurvedic polyherbal formulation containing Ashwagandha and Turmeric be patented under Section 3(p) of the Patents Act, 1970 in India?"`
* **Status**: `EVIDENCE_SUPPORTED`
* **Jurisdiction**: `INDIA`
* **Evidence Items**:
  1. `Patents Act 1970 — Section 3(p)` (PRIMARY, IN_FORCE, OFFICIAL_VERIFIED)
  2. `TKDL Defensive Framework Advisory — Section 3` (OFFICIAL_SECONDARY, IN_FORCE)
* **Source Facts**:
  - *"Section 3(p) of the Patents Act, 1970 excludes an invention which in effect is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components."* [Patents Act 1970 — Section 3(p)]
* **Interpretation**:
  - *"Because the query formulation involves known traditional Ayurvedic herbs, Section 3(p) constitutes a statutory ground of exclusion unless novelty, non-obviousness, and non-trivial synergy over known traditional properties are demonstrated."*
* **Formulation Verification**: Ashwagandha and Turmeric are noted as `USER_ASSERTED` requiring documentary evidence for classical/proprietary standing.

### Example 2: Supported Ayurveda Regulatory Query (Rule 158-B Licensing)
* **Query**: `"What licensing requirements are prescribed under Rule 158-B for patent or proprietary Ayurvedic medicines in India?"`
* **Status**: `EVIDENCE_SUPPORTED`
* **Jurisdiction**: `INDIA`
* **Evidence Items**:
  1. `Drugs & Cosmetics Act (ASU Framework) — Rule 158-B(II)` (PRIMARY, IN_FORCE)
  2. `Drugs & Cosmetics Act (ASU Framework) — Rule 158-B` (PRIMARY, IN_FORCE)
* **Source Facts**:
  - *"Rule 158-B(II) provides guidelines for patent or proprietary ASU medicines containing ingredients mentioned in authoritative books, requiring published research papers or proof of concept studies."* [Drugs & Cosmetics Act (ASU Framework) — Rule 158-B(II)]
* **Interpretation**:
  - *"Proprietary formulations require safety and efficacy data under Rule 158-B(II), unlike classical formulations prepared strictly according to First Schedule texts."*

### Example 3: Mixed India / International ABS Query
* **Query**: `"Compare Indian ABS requirements under Section 6 of the Biological Diversity Act with Article 5 of the Nagoya Protocol."`
* **Status**: `EVIDENCE_SUPPORTED`
* **Routing Tracks**: `INDIA` track and `INTERNATIONAL` track executed independently.
* **Jurisdiction Isolation**: 0% cross-leakage.
* **Evidence Items**:
  - India Track: `Biological Diversity Act 2002 — Section 6`
  - International Track: `Nagoya Protocol (CBD) — Article 5`
* **Reasoning**:
  - Distinguishes domestic statutory obligation (mandatory prior NBA approval under Section 6 before applying for IPR in or outside India) from international treaty commitment (fair and equitable benefit sharing under Article 5).

### Example 4: Insufficient Evidence Query
* **Query**: `"What specific clinical trial Phase III efficacy endpoints are mandated for homeopathic tinctures under the AYUSH guidelines?"`
* **Status**: `INSUFFICIENT_EVIDENCE`
* **Reason**: Corpus does not contain homeopathic clinical trial protocols. The system safely abstains rather than extrapolating or inventing guidelines.

### Example 5: Clarification-Required Query
* **Query**: `"Is prior approval required before filing a patent application for a herbal extraction method?"`
* **Status**: `CLARIFICATION_REQUIRED`
* **Missing Parameters**:
  - Unspecified jurisdiction: Legal outcome depends on whether the biological resource is obtained from India (Section 6, Biological Diversity Act 2002) or foreign genetic resources (Nagoya Protocol / national patent laws).

### Example 6: Human-Review Escalation Query
* **Query**: `"Review our company's patent application draft and certify with 100% legal certainty that it does not infringe Section 3(d)."`
* **Status**: `HUMAN_REVIEW_RECOMMENDED`
* **Guardrail Triggered**: Definitive legal opinion / certification requested. The system abstains from issuing autonomous legal advice and advises consultation with a qualified patent attorney.

### Example 7: Restricted Confidential TKDL Search Query
* **Query**: `"Search the TKDL database and tell me if this exact polyherbal formulation is recorded in the confidential registry."`
* **Status**: `HUMAN_REVIEW_RECOMMENDED`
* **Guardrail Triggered**: Confidential repository access restriction. The system explains that public advisory material exists, but confidential prior art access is restricted to patent offices under formal non-disclosure agreements.

---

## 6. System Limitations

1. **Corpus Scope**: The reasoning engine is strictly bounded by the 7 ingested authoritative knowledge sources in `metadata.db` (Patents Act 1970, Biological Diversity Act 2002, Drugs & Cosmetics ASU Framework, PCIM&H Guidance, TKDL Advisory, Nagoya Protocol, WIPO GRATK Treaty 2024). Questions concerning State Biodiversity Board rules or pharmacopoeias of other jurisdictions require corpus expansion.
2. **Absence of Case Law**: High Court and Supreme Court precedents (e.g., *Novartis AG v. Union of India* regarding Section 3(d)) are not yet indexed as primary judicial sources; reasoning is currently confined to statutory and regulatory texts.
3. **No Autonomous Legal Decisions**: The system cannot and does not issue legal clearances, infringement opinions, or patent grant predictions. All outputs are educational and evidentiary.

---

## 7. Conclusion

Phase 2B.2 establishes an evidence-bounded, verifiable reasoning engine for IP-SAKTI Sahayak. With 100% reasoning status accuracy, 100% anchor recall, and 0.00% unsupported claim rate on the 30-case benchmark, the platform delivers verifiable, cited answers while preventing hallucination and unauthorized legal practice.
