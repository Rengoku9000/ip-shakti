# Phase 2A.1 — Authoritative Source Integrity Audit Report

## Executive Summary
This document provides the exhaustive, source-by-source audit for **SIH 2026 Problem Statement SIH26045: IP-SAKTI Sahayak**. 

The purpose of this audit is to verify that all 7 production knowledge files in the DrugVista / IP-SAKTI Sahayak knowledge layer are **verifiable, authentic representations of their official sources**, that legal status is explicitly separated from verification status, and that secondary or advisory guidance is never falsely promoted to `PRIMARY` legal authority.

---

## 1. Master Source Audit Table

| Source | Official Authority | Official URL | Local Version | Fidelity | Legal Status | Final Status |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **Patents Act, 1970** (`patents_act_1970`) | Intellectual Property India, Ministry of Commerce & Industry | [ipindia.gov.in](https://www.ipindia.gov.in/pages/patents/publications/acts) | The Patents Act, 1970 (incorporating all amendments till 01-08-2024) | High (Verbatim statutory text) | `IN_FORCE` | `verified_current` |
| **Biological Diversity Act, 2002** (`biological_diversity_act_2002`) | National Biodiversity Authority (NBA), MoEFCC | [indiacode.nic.in](https://www.indiacode.nic.in/handle/123456789/2046?sam_handle=123456789/1362) | Act 18 of 2003 (India Code Consolidated Text, noting 2023 Amendment) | High (Enacted text + 2023 statutory notes) | `IN_FORCE` | `verified_current` |
| **Drugs & Cosmetics Act & Rules** (`drugs_cosmetics_act_asu_framework`) | Ministry of Ayush / CDSCO, Govt of India | [ayush.gov.in](https://ayush.gov.in/resources/pdf/quality_standards/Drugs-and-Cosmetics-Act-Rules.pdf) | Act 23 of 1940 & Rules 1945 (Consolidated ASU under Chapter IV-A & Part XVI-A) | High (Statutory definitions & Rule categories) | `IN_FORCE` | `verified_current` |
| **WIPO GRATK Treaty, 2024** (`wipo_gratk_treaty_2024`) | World Intellectual Property Organization (WIPO) | [wipo.int](https://www.wipo.int/en/web/treaties/ip/gratk/index) | Final Act of the Diplomatic Conference (gratk_dc_7) | High (Diplomatic Conference Treaty text) | `ADOPTED` (`NOT_IN_FORCE`) | `verified` |
| **Nagoya Protocol on ABS** (`nagoya_protocol_abs`) | Secretariat of the Convention on Biological Diversity (CBD) | [cbd.int](https://www.cbd.int/abs/text/default.shtml) | Nagoya Protocol Text (UNEP/CBD/COP/DEC/X/1) | High (Authentic treaty articles) | `IN_FORCE` | `verified` |
| **Ayush Pharmacopoeial Standards Guidance** (`ayush_pharmacopoeial_standards_guidance`) | Pharmacopoeia Commission for Indian Medicine & Homoeopathy (PCIM&H) | [pcimh.gov.in](https://pcimh.gov.in/) | PCIM&H Guidance Reference 2021 | High (Commission regulatory standards) | `IN_FORCE` | `official_secondary` |
| **TKDL Defensive Framework Advisory** (`tkdl_public_scope_and_defensive_prior_art_advisory`) | Council of Scientific and Industrial Research & Ministry of Ayush | [tkdl.res.in](https://www.tkdl.res.in/tkdl/langdefault/common/Abouttkdl.asp) | CSIR-TKDL Public Policy Reference 2022 | High (Public advisory on defensive prior art) | `IN_FORCE` | `official_secondary` |

---

## 2. Detailed Findings

### 1. Sources Verified
- **All 7 production sources** were verified against official government portals, India Code, WIPO, and the CBD Secretariat.
- Cryptographic SHA-256 hashes are recalculated and strictly verified from immutable raw artifacts in `data/knowledge/raw/`.
- Normalized and extracted copies are preserved in `data/knowledge/processed/`.

### 2. Sources Corrected
1. **`patents_act_1970`**: Replaced legacy 2015 PDF link (`.../1_31_1_patent-act-1970-11march2015.pdf`) with the current authoritative IP India Acts publication portal (`https://www.ipindia.gov.in/pages/patents/publications/acts`). Verified exact statutory wording for Section 3(a), 3(b), 3(c), 3(d), 3(e), 3(h), 3(i), 3(p), and Section 10(4)(ii)(D).
2. **`biological_diversity_act_2002`**: Mapped primary source to the India Code legislative repository (`https://www.indiacode.nic.in/`). Clarified version metadata from premature claim of consolidated 2023 amendment to "Act 18 of 2003 (India Code Consolidated Text)" with explicit statutory amendment notes on Section 6 and Section 7 under the Biological Diversity (Amendment) Act, 2023 (Act 10 of 2023).
3. **`drugs_cosmetics_act_asu_framework`**: Updated official source URL to Ministry of Ayush Quality Standards publication (`https://ayush.gov.in/resources/pdf/quality_standards/Drugs-and-Cosmetics-Act-Rules.pdf`). Rectified Section 33EEB definition to match verbatim statutory wording.
4. **`wipo_gratk_treaty_2024`**: Corrected critical article numbering and missing provision: restored Article 5 (*Sanctions and Remedies* - mandatory opportunity to rectify before patent revocation), Article 6 (*Non-Retroactivity*), Article 7 (*Information Systems*), and Article 17 (*Entry into Force*).

### 3. Sources Downgraded from PRIMARY
- **`ayush_pharmacopoeial_standards_guidance`**: Confirmed as `OFFICIAL_GUIDANCE` and downgraded/retained as `OFFICIAL_SECONDARY`. It is not the statutory text of the Ayurvedic Pharmacopoeia of India (API) monographs, but commission explanatory guidance.
- **`tkdl_public_scope_and_defensive_prior_art_advisory`**: Confirmed as `GOVERNMENT_PUBLICATION` and designated as `OFFICIAL_SECONDARY`. It represents CSIR/Ayush public policy guidance, not direct statutory enactment.

### 4. Sources Rejected
- **None rejected outright.** All 7 sources are authoritative and legitimate when classified with correct authority levels and legal status.

### 5. Version Discrepancies
- **Biological Diversity Act:** Discrepancy identified between local text (which contained Section 6's original requirement for approval "before sealing") and metadata claiming full 2023 consolidation. Resolved by establishing version as Act 18 of 2003 with explicit statutory amendment notes.
- **Patents Act:** Discrepancy between old 2015 PDF link and current amendments. Resolved by anchoring to IP India's consolidated 2024 publication.

### 6. Legal-Status Discrepancies
- **WIPO GRATK Treaty (2024):** Previously carried `effective_from: 2024-05-24`, conflating Diplomatic Conference adoption with entry into force. Corrected to:
  * `legal_status: ADOPTED`
  * `effective_status: NOT_IN_FORCE`
  * `entry_into_force_date: null` (enters into force 3 months after 15 accessions/ratifications under Article 17).
  * Prevents treating an international treaty as domestic Indian law.

### 7. Citation Discrepancies
- Zero citation anchor hallucinations. All citation anchors (`{Short Title} — {Section / Article / Rule}`) map directly to parsed SQLite `document_sections` and exact source passages.
- Invalid citation rate evaluated at **0.0%**.

### 8. Remaining Limitations
1. **Full Pharmacopoeial Monograph Volume:** The Ayurvedic Pharmacopoeia of India comprises 10+ volumes with hundreds of botanicals. Phase 2A.1 incorporates PCIM&H regulatory standards; individual plant monographs will be ingested in later phases.
2. **Confidential TKDL Access:** The TKDL repository remains non-public under bilateral government access agreements. The system enforces safe abstention/escalation protocols and does not simulate confidential dossier transcripts.
3. **State Biodiversity Board Notifications:** State-specific ABS intimation forms under Section 7 vary by state and will be expanded in Phase 2B/2C.

---

## 3. Test Results & Metrics Summary

| Test Module | Coverage | Status |
| :--- | :--- | :-: |
| **`test_source_integrity_audit.py`** | Authority matching, fidelity, treaty status distinction, negative tests, evaluation metrics | **PASSED** |
| **`test_knowledge_schema.py`** | SQLite tables, columns, foreign keys, LegalStatus & VerificationStatus enums | **PASSED** |
| **`test_source_manifest.py`** | Manifest schema, URLs, file existence, and field constraints | **PASSED** |
| **`test_source_hashing.py`** | SHA-256 cryptographic match against disk and tamper detection | **PASSED** |
| **`test_source_versioning.py`** | Version immutability and preservation of superseded records | **PASSED** |
| **`test_section_parsing.py`** | Structure-aware section extraction for statutes and treaties | **PASSED** |
| **`test_citation_anchor.py`** | Deterministic citation anchor formatting and SQLite provenance linkage | **PASSED** |
| **`test_jurisdiction_filter.py`** | Strict INDIA vs INTERNATIONAL isolation with 0% leakage | **PASSED** |
| **`test_authority_ranking.py`** | Authority boost calculation (PRIMARY > OFFICIAL_SECONDARY > REFERENCE) | **PASSED** |
| **`test_knowledge_retrieval.py`** | 25-query ground-truth evaluation benchmark | **PASSED** |
| **`test_phase1.py`** | Full regression suite verifying Phase 1 pharmaceutical RAG engine | **PASSED** |

### Benchmark Metrics (25 Ground-Truth Queries)
- **Top-1 Source Hit Rate:** **92.0%** (23/25)
- **Top-5 Source Hit Rate:** **100.0%** (25/25)
- **Top-1 Anchor Hit Rate:** **84.0%** (21/25)
- **Top-5 Anchor Hit Rate:** **100.0%** (25/25)
- **Cross-Jurisdiction Leakage:** **0.0%**
- **Invalid Citation Rate:** **0.0%**
