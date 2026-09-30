# IP-SAKTI Sahayak — Phase 2A Knowledge Corpus

## Overview
This directory contains the curated, version-tracked, and cryptographically verified legal and regulatory knowledge corpus for **SIH 2026 Problem Statement SIH26045: IP-SAKTI Sahayak** (Ayurveda Intellectual Property & Regulatory Assistant).

Following the core principle:
```text
SOURCE AUTHORITY > CORPUS SIZE
```
All documents in this knowledge base originate exclusively from official government portals, statutory gazettes, multilateral treaty secretariats, and official standards bodies. No unverified third-party blogs, scraped repositories, or LLM-generated summaries are included.

---

## Controlled Vocabularies & Taxonomies

### 1. Source Types (`SourceType`)
- `STATUTE`: Primary legislative acts enacted by Parliament.
- `RULE`: Statutory rules framed under legislative delegated authority.
- `REGULATION`: Subordinate regulatory notices and statutory guidelines.
- `TREATY`: Multilateral international conventions and diplomatic conference treaties.
- `PHARMACOPOEIA`: Official statutory monographs defining purity, identity, and strength.
- `FORMULARY`: Authoritative recipe formularies for classical compound formulations.
- `OFFICIAL_GUIDANCE`: Ministry and pharmacopoeial commission advisory publications.
- `REGISTRY`: Official public register notices.
- `CASE_LAW`: Judicial decisions and appellate rulings.
- `CLASSICAL_TEXT`: Ancient treatises recognized under the First Schedule of the Drugs and Cosmetics Act.
- `GOVERNMENT_PUBLICATION`: Official gazettes and public policy frameworks.

### 2. Authority Levels (`AuthorityLevel`)
- `PRIMARY`: Actual legal and statutory authority (Acts, Rules, Treaties, Gazette notifications). Given high retrieval prioritization (+0.08 authority score weighting).
- `OFFICIAL_SECONDARY`: Government and ministry explanatory/guidance materials (PCIM&H guidelines, CSIR TKDL public advisories). Given medium retrieval prioritization (+0.04 authority score weighting).
- `REFERENCE`: Supporting commentary, academic citations, or non-binding explanatory material (no authority boost).

### 3. Jurisdictions (`Jurisdiction`)
- `INDIA`: National legal regime applicable within the territory of India.
- `INTERNATIONAL`: Multilateral international treaties, conventions, and global IP frameworks.
*Note: Cross-jurisdiction leakage is strictly prohibited by retrieval filtering.*

### 4. Verification Statuses (`VerificationStatus`)
- `verified`: Source file exists, cryptographic SHA-256 hash matches manifest, and provenance is validated. Only `verified` sources enter the production vector index.
- `unverified`: Source identified but pending formal verification.
- `superseded`: Historical version preserved for auditability but superseded by an amendment.
- `rejected`: Source failed verification or was deemed non-authoritative.

---

## Authoritative Corpus Sources

| Source ID | Document Title | Issuing Authority | Type | Level | Jurisdiction | Version / Date | SHA-256 Checksum (Truncated) | Status | Official Source URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `patents_act_1970` | The Patents Act, 1970 (Sec 2, 3, 10) | Intellectual Property India, Ministry of Commerce & Industry | STATUTE | PRIMARY | INDIA | Act 39 of 1970 (amended up to 2024 Rules) | `dafb2393a3cc...` | `verified` | [ipindia.gov.in](https://ipindia.gov.in/writereaddata/Portal/IPOAct/1_31_1_patent-act-1970-11march2015.pdf) |
| `biological_diversity_act_2002` | The Biological Diversity Act, 2002 | National Biodiversity Authority (NBA), MoEFCC | STATUTE | PRIMARY | INDIA | Act 18 of 2003 (with 2023 Amendment) | `ddf1ead0506b...` | `verified` | [nbaindia.org](http://nbaindia.org/content/25/19/1/act.html) |
| `drugs_cosmetics_act_asu_framework` | Drugs and Cosmetics Act, 1940 & Rules 1945 (ASU) | Ministry of Ayush / CDSCO, Govt of India | STATUTE | PRIMARY | INDIA | Act 23 of 1940 & Rules 1945 (as amended) | `27904db54eb9...` | `verified` | [ayush.gov.in](https://ayush.gov.in/docs/drugs-and-cosmetics-act-1940.pdf) |
| `wipo_gratk_treaty_2024` | WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge | World Intellectual Property Organization (WIPO) | TREATY | PRIMARY | INTERNATIONAL | Final Diplomatic Act (May 24, 2024) | `971876888c93...` | `verified` | [wipo.int](https://www.wipo.int/edocs/mdocs/tk/en/gratk_dc/gratk_dc_7.pdf) |
| `nagoya_protocol_abs` | Nagoya Protocol on Access and Benefit-Sharing | Secretariat of the Convention on Biological Diversity (CBD) | TREATY | PRIMARY | INTERNATIONAL | COP 10 Decision X/1 (Oct 29, 2010) | `71ba275d15e6...` | `verified` | [cbd.int](https://www.cbd.int/abs/text/default.shtml) |
| `ayush_pharmacopoeial_standards_guidance` | PCIM&H Pharmacopoeial Standards & Quality Guidance | Pharmacopoeia Commission for Indian Medicine & Homoeopathy | OFFICIAL_GUIDANCE | OFFICIAL_SECONDARY | INDIA | PCIM&H Guidance Reference 2021 | `cc95eb9d0399...` | `verified` | [pcimh.gov.in](https://pcimh.gov.in/) |
| `tkdl_public_scope_and_defensive_prior_art_advisory` | TKDL Defensive Prior Art Framework Advisory | CSIR & Ministry of Ayush, Govt of India | GOVERNMENT_PUBLICATION | OFFICIAL_SECONDARY | INDIA | CSIR-TKDL Public Reference 2022 | `2b7e5623b2cd...` | `verified` | [tkdl.res.in](https://www.tkdl.res.in/tkdl/langdefault/common/Abouttkdl.asp) |

---

## TKDL Defensive Prior Art & Confidentiality Guardrail

### Crucial Architectural Constraint
The **Traditional Knowledge Digital Library (TKDL)** is a confidential, non-public database accessible only to approved international patent examiners under bilateral non-disclosure access agreements. 
- In accordance with SIH26045 guidelines, **no restricted or non-public TKDL transcripts are scraped, duplicated, simulated, or redistributed.**
- The corpus retains public policy documents detailing TKDL's defensive protection mandate, IPC Traditional Knowledge Resource Classification (TKRC), and bilateral patent treaty structures.
- **Safe Abstention Protocol:** If any user query requests proprietary or confidential internal TKDL database entries, the assistant must safely abstain and escalate to formal CSIR-TKDL / registered patent agent channels.

---

## Directory Structure

```text
drugvista/data/knowledge/
├── manifests/
│   └── sources.json             # Machine-readable source manifest with cryptographic hashes
├── raw/                         # Verified, immutable raw text documents with structural markers
│   ├── patents_act_1970_sec3_sec10.txt
│   ├── biological_diversity_act_2002.txt
│   ├── drugs_cosmetics_act_asu_framework.txt
│   ├── wipo_gratk_treaty_2024.txt
│   ├── nagoya_protocol_abs.txt
│   ├── ayush_pharmacopoeial_standards_guidance.txt
│   └── tkdl_public_scope_and_defensive_prior_art_advisory.txt
├── evaluation_dataset.json      # 25 ground-truth evaluation queries with verified anchor mappings
└── README.md                    # This documentation file
```

---

## Known Corpus Limitations
1. **Scope Boundary:** Phase 2A deliberately focuses on core patentability exclusions (Section 3(p), 3(e), 3(d), 10(4)), ABS authorizations (Sections 3, 4, 6, 7, 21), ASU regulatory definitions (Section 33EEB, Rule 158-B, Schedule I), and landmark multilateral treaties (WIPO GRATK 2024, Nagoya Protocol). Full judicial case law volumes and regional state biodiversity board rules will be expanded in subsequent phases.
2. **Classical Text Representation:** Individual verses of Charaka Samhita and Sushruta Samhita are currently referenced via their statutory recognition under Schedule I of the Drugs & Cosmetics Act. Direct Sanskrit verse-level structural parsing is reserved for the classical corpus expansion phase.
