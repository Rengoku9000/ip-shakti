# DrugVista → IP-SAKTI Sahayak
# Phase 2C — Multilingual Text Intelligence Report

## 1. Executive Summary

Phase 2C implements **Multilingual Text Intelligence** for IP-SAKTI Sahayak (SIH 2026 Problem Statement SIH26045). Expanding beyond English text processing, the system now provides end-to-end support for **English**, **Hindi (Devanagari)**, and **Kannada** queries and responses while preserving **100% citation provenance, statutory section immutability, jurisdiction isolation, and epistemic uncertainty**.

### Core Operational Principles
1. **Evidence Ground Truth**: Authoritative legal and regulatory evidence is never machine-translated prior to reasoning. Legal reasoning operates exclusively over canonical, verified statutory chunks.
2. **Language ≠ Jurisdiction**: Query language never determines or alters the jurisdiction of applicable law. A Hindi query may inquire into international treaties, and an English query may inquire into Indian patent law.
3. **Citation Immutability Mandate**: Citation anchors (`Patents Act 1970 — Section 3(p)`), source IDs, chunk IDs, legal statuses, and URLs remain strictly immutable during translation and localization.
4. **Epistemic Modesty**: Probabilistic qualifications (*"may be relevant"*, *"cannot determine"*, *"insufficient evidence"*) and negative statutory exclusions are preserved without being converted into definitive legal guarantees.
5. **Local-First & Offline Resilience**: Deterministic local dictionaries and phrase preservation ensure full functionality without external translation APIs or network dependencies.

---

## 2. Architecture Diagram

```
                ┌───────────────────────────┐
                │   User Query (EN/HI/KN)   │
                └─────────────┬─────────────┘
                              ↓
                ┌───────────────────────────┐
                │  Language Detection (2C)  │
                │  - Unicode Script Block   │
                │  - Confidence & Dominance │
                └─────────────┬─────────────┘
                              ↓
                ┌───────────────────────────┐
                │ Query Normalization (2C)  │
                │  - Verbatim Statutory Re  │
                │  - Botanical/Herb Terms   │
                │  - Canonical English Rep  │
                └─────────────┬─────────────┘
                              ↓
                ┌───────────────────────────┐
                │   Classification (2B.1)   │
                │   - Intent & Topic Match  │
                │   - Jurisdiction Signals  │
                └─────────────┬─────────────┘
                              ↓
                ┌───────────────────────────┐
                │ Multi-Track Routing (2B.1)│
                │   - Isolated Jur Tracks   │
                └─────────────┬─────────────┘
                              ↓
                ┌───────────────────────────┐
                │  Authoritative Retrieval  │
                │  - FAISS + SQLite DB (2A) │
                │  - Exact Anchor Boost     │
                └─────────────┬─────────────┘
                              ↓
                ┌───────────────────────────┐
                │ Evidence Reasoning (2B.2) │
                │  - Source Fact Separation │
                │  - Epistemic Guardrails   │
                └─────────────┬─────────────┘
                              ↓
                ┌───────────────────────────┐
                │   Answer Localizer (2C)   │
                │  - Citation Immutability  │
                │  - Modality Preservation  │
                └─────────────┬─────────────┘
                              ↓
                ┌───────────────────────────┐
                │   Cited Localized Answer  │
                │  - Immutable Citations    │
                │  - Preserved Jur & Status │
                └───────────────────────────┘
```

---

## 3. Evaluation Benchmark Results

The 30-case authoritative multilingual benchmark (`drugvista/data/knowledge/multilingual_benchmark_30.json`) spanning 10 English, 10 Hindi, and 10 Kannada cases was evaluated across all architectural dimensions:

| Metric | Target | Result | Status |
| :--- | :--- | :--- | :--- |
| **Language Detection Accuracy** | $\ge 95.0\%$ | **100.0%** (30/30) | **PASSED** |
| **Intent Classification Accuracy** | $\ge 90.0\%$ | **100.0%** (30/30) | **PASSED** |
| **Jurisdiction Detection Accuracy** | $\ge 90.0\%$ | **100.0%** (30/30) | **PASSED** |
| **Reasoning Status Accuracy** | $\ge 90.0\%$ | **100.0%** (30/30) | **PASSED** |
| **Required Citation Anchor Hit Rate** | $\ge 90.0\%$ | **100.0%** (30/30) | **PASSED** |
| **Total Substantive Claims Audited** | - | **240 claims** | - |
| **Unsupported Claim Rate** | **0.00%** | **0.00%** (0 unsupported) | **PASSED** |
| **Forbidden Legal Verdict Violations** | **0** | **0 violations** | **PASSED** |
| **Citation Anchor Mutations** | **0** | **0 mutations** | **PASSED** |
| **Jurisdiction Mutations** | **0** | **0 mutations** | **PASSED** |
| **Legal Status Mutations** | **0** | **0 mutations** | **PASSED** |

### Cumulative Regression Suite

| Component | Test Suite | Tests Passed |
| :--- | :--- | :--- |
| **Phase 1** | Architecture, Hashing, Chunking, Provenance, FAISS | **8 / 8** |
| **Phase 2A / 2A.1** | Corpus Integrity, Source Versioning, Anchor Provenance | **19 / 19** |
| **Phase 2B.1** | Formulation & Query Classification, Jurisdiction Routing | **26 / 26** |
| **Phase 2B.2** | Evidence-Based Reasoning, Claim Support, Abstention | **27 / 27** |
| **Phase 2C** | Language Detection, Normalization, Citations, Uncertainty, Benchmark | **26 / 26** |
| **Total Test Suite** | Full discovery (`tests/` + `drugvista/`) | **106 / 106 (100%)** |

---

## 4. Key Architectural Implementations

### 4.1 Controlled Language Taxonomy (`language_policy.py`)
- Supported languages: `ENGLISH`, `HINDI`, `KANNADA`, `MIXED`, `UNKNOWN`.
- Scripts supported: `LATIN`, `DEVANAGARI`, `KANNADA`, `MIXED`, `UNKNOWN`.
- Extensible design allowing future Indian languages (Tamil, Telugu, Marathi, Bengali, Malayalam, Gujarati, etc.) without altering the core pipeline.

### 4.2 Deterministic Language Detection (`language_detector.py`)
- Analyzes Unicode code point frequency:
  - Devanagari block (`U+0900` to `U+097F`)
  - Kannada block (`U+0C80` to `U+0CFF`)
  - Latin alphabetic range (`A-Z`, `a-z`)
- Employs dominance weighting: alphanumeric section labels like `158-B` or `33EEB` do not falsely classify an otherwise pure Hindi/Kannada sentence as mixed.
- Detects transliterated text (Hinglish / Kanglish) and flags unsupported scripts (Cyrillic, Arabic, CJK) safely.

### 4.3 Controlled Domain Terminology (`terminology.py`)
- Maps common Ayurvedic formulation forms (Churna, Vati, Kwatha, Asava, Taila, Ghrita, Bhasma) across English, Hindi, and Kannada.
- Maps botanical and herbal ingredients (Ashwagandha -> *Withania somnifera*, Turmeric -> *Curcuma longa*, Guduchi -> *Tinospora cordifolia*).
- Regex-preserves statutory provisions verbatim: `Section 3(p)`, `धारा 3(p)`, `ಕಲಂ 3(p)`, `Rule 158-B`, `ನಿಯಮ 158-B`, `Article 5`, `Schedule T`, `First Schedule`.

### 4.4 Semantic Query Normalization (`query_normalizer.py`)
- Preserves the user's original query text untouched.
- Translates interrogatives, grammatical connectors, and domain concepts into a canonical English representation.
- Injects explicit statutory provision identifiers and jurisdiction anchors into the retrieval text.

### 4.5 Offline Deterministic Translation (`translation_service.py`)
- Built-in legal and regulatory phrasebooks for Hindi and Kannada.
- Implements citation masking: all citation brackets (e.g. `[1]`, `[Patents Act 1970 — Section 3(p)]`) are replaced with unique tokens during translation and restored verbatim post-translation.
- Prioritizes longer compound phrases to prevent sub-token fragmentation.

### 4.6 Answer Localizer & Invariance Enforcer (`answer_localizer.py`)
- Translates summaries, source facts, and interpretations into the requested target language.
- Re-asserts strict equality assertions on all `citation_anchor`, `source_id`, `jurisdiction`, and `legal_status` fields across canonical and localized outputs.
- Keeps machine-readable `ReasoningStatus` unchanged (`EVIDENCE_SUPPORTED`, `PARTIALLY_SUPPORTED`, `INSUFFICIENT_EVIDENCE`, `CLARIFICATION_REQUIRED`, `HUMAN_REVIEW_RECOMMENDED`).

---

## 5. End-to-End Exemplars Across Languages

### Example 1: English → English
* **Original Query**: `"Can an Ayurvedic polyherbal formulation containing Ashwagandha and Turmeric be patented under Section 3(p) of the Patents Act, 1970 in India?"`
* **Detected Language**: `ENGLISH` (Confidence: 1.0, Script: `LATIN`)
* **Normalized Query**: `"Can an Ayurvedic polyherbal formulation containing Ashwagandha and Turmeric be patented under Section 3(p) of the Patents Act, 1970 in India?"`
* **Classification**:
  - Intent: `PATENTABILITY`
  - Jurisdiction: `INDIA`
  - Topics: `PATENT_LAW`, `TRADITIONAL_KNOWLEDGE`
* **Retrieved Evidence**:
  - `Patents Act 1970 — Section 3(p)` (PRIMARY, IN_FORCE, OFFICIAL_VERIFIED)
* **Reasoning Status**: `EVIDENCE_SUPPORTED`
* **Final Answer**:
  - *Summary*: `"Section 3(p) of the Patents Act, 1970 excludes an invention which in effect is traditional knowledge or an aggregation of known properties of traditionally known components."`
  - *Source Fact*: `"Section 3(p) excludes traditional knowledge from patentability."` [Patents Act 1970 — Section 3(p)]
  - *Interpretation*: `"Because the formulation is based on traditionally known herbs, Section 3(p) may be relevant."` *(Note: Applicability depends on proof of synergy.)*
* **Citations**: `[1] Patents Act 1970 — Section 3(p)`

### Example 2: Hindi → Hindi
* **Original Query**: `"क्या भारत में अश्वगंधा और हल्दी से बने आयुर्वेदिक फॉर्मूलेशन को पेटेंट अधिनियम की धारा 3(p) के तहत पेटेंट कराया जा सकता है?"`
* **Detected Language**: `HINDI` (Confidence: 0.98, Script: `DEVANAGARI`)
* **Normalized Query**: `"Can Ashwagandha and Turmeric Ayurvedic formulation be patented under Patents Act under Section 3(p) in India?"`
* **Classification**:
  - Intent: `PATENTABILITY`
  - Jurisdiction: `INDIA`
  - Topics: `PATENT_LAW`, `TRADITIONAL_KNOWLEDGE`
* **Retrieved Evidence**:
  - `Patents Act 1970 — Section 3(p)` (PRIMARY, IN_FORCE, OFFICIAL_VERIFIED)
* **Reasoning Status**: `EVIDENCE_SUPPORTED`
* **Final Answer (Localized)**:
  - *Summary*: `"पेटेंट अधिनियम, 1970 की धारा 3(p) ऐसे आविष्कार को बाहर करती है जो वास्तव में पारंपरिक ज्ञान है।" [Patents Act 1970 — Section 3(p)]`
  - *Source Fact*: `"धारा 3(p) पारंपरिक ज्ञान को पेटेंट पात्रता से बाहर करती है।" [Patents Act 1970 — Section 3(p)]`
  - *Interpretation*: `"चूंकि यह फॉर्मूलेशन पारंपरिक रूप से ज्ञात जड़ी-बूटियों पर आधारित है, इसलिए धारा 3(p) प्रासंगिक हो सकता है।" [Patents Act 1970 — Section 3(p)]`
* **Citations**: `[1] Patents Act 1970 — Section 3(p)` (Immutable)

### Example 3: Kannada → Kannada
* **Original Query**: `"ಭಾರತದಲ್ಲಿ ಪೇಟೆಂಟ್ ಕಾಯ್ದೆಯ ಕಲಂ 3(p) ಅಡಿಯಲ್ಲಿ ಸಾಂಪ್ರದಾಯಿಕ ಜ್ಞಾನ ಆಧಾರಿತ ಅಶ್ವಗಂಧ ಚೂರ್ಣಕ್ಕೆ ಪೇಟೆಂಟ್ ಪಡೆಯಬಹುದೇ?"`
* **Detected Language**: `KANNADA` (Confidence: 0.98, Script: `KANNADA`)
* **Normalized Query**: `"Can traditional knowledge based Ashwagandha Churna be patented under Patents Act under Section 3(p) in India?"`
* **Classification**:
  - Intent: `PATENTABILITY`
  - Jurisdiction: `INDIA`
  - Topics: `PATENT_LAW`, `TRADITIONAL_KNOWLEDGE`
* **Retrieved Evidence**:
  - `Patents Act 1970 — Section 3(p)` (PRIMARY, IN_FORCE, OFFICIAL_VERIFIED)
* **Reasoning Status**: `EVIDENCE_SUPPORTED`
* **Final Answer (Localized)**:
  - *Summary*: `"ಪೇಟೆಂಟ್ ಕಾಯ್ದೆ, 1970 ರ ಕಲಂ 3(p) ಸಾಂಪ್ರದಾಯಿಕ ಜ್ಞಾನವಾಗಿರುವ ಆವಿಷ್ಕಾರಗಳನ್ನು ಹೊರಗಿಡುತ್ತದೆ." [Patents Act 1970 — Section 3(p)]`
  - *Source Fact*: `"ಕಲಂ 3(p) ಸಾಂಪ್ರದಾಯಿಕ ಜ್ಞಾನವನ್ನು ಪೇಟೆಂಟ್ ಅರ್ಹತೆಯಿಂದ ಹೊರಗಿಡುತ್ತದೆ." [Patents Act 1970 — Section 3(p)]`
  - *Interpretation*: `"ಈ ಸೂತ್ರೀಕರಣವು ಸಾಂಪ್ರದಾಯಿಕ ಗಿಡಮೂಲಿಕೆಗಳನ್ನು ಆಧರಿಸಿರುವುದರಿಂದ, ಕಲಂ 3(p) ಸಂಬಂಧಿತವಾಗಿರಬಹುದು." [Patents Act 1970 — Section 3(p)]`
* **Citations**: `[1] Patents Act 1970 — Section 3(p)` (Immutable)

---

## 6. System Limitations

1. **Text Only**: Voice, speech-to-text, and audio responses are intentionally out of scope for Phase 2C.
2. **Supported Languages**: Primary deterministic support covers English, Hindi, and Kannada. Extended scheduled Indian languages (Tamil, Telugu, Marathi, Bengali, etc.) require vocabulary expansion.
3. **No Autonomous Legal Decisions**: The system explains statutory grounds of patentability exclusions and regulatory requirements; it does not issue autonomous legal rulings or guarantees.

---

## 7. Conclusion

Phase 2C successfully introduces multilingual text intelligence into IP-SAKTI Sahayak without compromising legal rigor or evidence provenance. With 100% language detection accuracy, 100% intent classification, 100% anchor recall, and 0.00% unsupported claim rate on the 30-case benchmark, the platform delivers verifiable, localized legal and regulatory guidance across English, Hindi, and Kannada.
