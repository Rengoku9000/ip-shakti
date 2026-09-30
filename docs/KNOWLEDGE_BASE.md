# IP-SAKTI Sahayak — Knowledge Base & Citation Provenance Architecture (Phase 2A)

## 1. System Objective & Architecture

Phase 2A of the DrugVista → IP-SAKTI Sahayak evolution establishes a versioned, provenance-rich, and legally authoritative knowledge retrieval foundation.

In alignment with **SIH 2026 Problem Statement SIH26045**, every retrieved legal, regulatory, or technical passage is bound to an exact, deterministic citation anchor and traceable to its issuing authority, publication date, and official source URL without reliance on generative LLM guessing.

### Ingestion & Indexing Pipeline Flow
```text
Official Government / Treaty Source
              ↓
   Source Manifest Verification
   (SHA-256 cryptographic match)
              ↓
  Structure-Aware Legal Parser
  (Identifies Sections, Articles, Rules, Schedules)
              ↓
  Hierarchical Section Records (SQLite)
              ↓
  Structure-Bounded Chunking & Deterministic Anchors
  ("{Short Title} — {Section Label}")
              ↓
  Chunk & Provenance Records (SQLite)
              ↓
  Dense Vector Embeddings (all-MiniLM-L6-v2)
              ↓
  FAISS Vector Index (Persistent on disk)
```

---

## 2. Database Schema Extension (SQLite)

The Phase 1 storage foundation has been extended with relational tables that model authorities, versions, structural sections, and citation anchors without disturbing the baseline pharmaceutical document tables.

### `sources` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Unique identifier (e.g. `patents_act_1970`) |
| `name` | TEXT | NOT NULL | Official name of statute / treaty |
| `authority` | TEXT | NOT NULL | Issuing body (e.g. `Intellectual Property India`) |
| `source_type` | TEXT | NOT NULL | Controlled enum (`STATUTE`, `TREATY`, etc.) |
| `jurisdiction` | TEXT | NOT NULL | Controlled enum (`INDIA`, `INTERNATIONAL`) |
| `authority_level`| TEXT | NOT NULL | Controlled enum (`PRIMARY`, `OFFICIAL_SECONDARY`, `REFERENCE`) |
| `official_url` | TEXT | NOT NULL | Direct link to official government / gazette publication |
| `description` | TEXT | | Brief overview of subject matter |
| `created_at` | TEXT | NOT NULL | ISO timestamp |

### `source_versions` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Version record ID |
| `source_id` | TEXT | NOT NULL, FK(`sources.id`) | Foreign key linking to parent source |
| `version` | TEXT | NOT NULL | Version / amendment designation |
| `publication_date`| TEXT | | Official date of gazette enactment |
| `effective_from`| TEXT | | Date entering into force |
| `effective_until`| TEXT | | Null if current; date if superseded |
| `retrieved_at` | TEXT | NOT NULL | Ingestion timestamp |
| `content_hash` | TEXT | NOT NULL | 64-char SHA-256 hex digest of raw text |
| `local_path` | TEXT | | Relative path to verified raw source |
| `verification_status`| TEXT | NOT NULL | `verified`, `unverified`, `superseded`, `rejected` |

### `document_sections` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | PRIMARY KEY | Unique section ID (e.g. `patents_act_1970_sec_3p`) |
| `document_id` | TEXT | NOT NULL, FK(`documents.id`) | Link to parent ingested document |
| `parent_id` | TEXT | FK(`document_sections.id`) | Parent structural node (for nested chapters/sections) |
| `section_type` | TEXT | NOT NULL | `SECTION`, `ARTICLE`, `RULE`, `SCHEDULE`, etc. |
| `section_label`| TEXT | NOT NULL | Exact label (e.g. `Section 3(p)`, `Article 3`) |
| `section_title`| TEXT | | Descriptive title extracted from heading |
| `sequence` | INTEGER| NOT NULL | Natural ordinal sequence in source text |

### Extended Columns on `documents` & `chunks`
- `documents`: Added `source_id`, `source_version_id`, `authority_level`, `jurisdiction`.
- `chunks`: Added `section_id`, `citation_anchor`, `authority_level`, `jurisdiction`, `source_id`, `source_version_id`.

---

## 3. Strict Jurisdiction Isolation

SIH26045 demands distinct separation between the Indian regulatory regime and international IP mechanisms.

### Filtering Rules:
1. **INDIA Filter:** When `jurisdiction="INDIA"` is supplied to `Retriever.retrieve()`, all international treaties (`wipo_gratk_treaty_2024`, `nagoya_protocol_abs`) are strictly excluded.
2. **INTERNATIONAL Filter:** When `jurisdiction="INTERNATIONAL"` is supplied, all Indian domestic statutes (`patents_act_1970`, `biological_diversity_act_2002`, `drugs_cosmetics_act_asu_framework`) are strictly excluded.
3. **Cross-Jurisdiction Leakage:** Tested and verified at **0.0% leakage**.

---

## 4. Authority Level Re-ranking

A deterministic score boost prioritizes primary legal authority while preserving semantic relevance:

$$\text{Final Score} = \text{Cosine Similarity} + \text{Authority Bonus}$$

Where:
- `PRIMARY` authority bonus: $+0.08$
- `OFFICIAL_SECONDARY` authority bonus: $+0.04$
- `REFERENCE` authority bonus: $+0.00$

Results are capped at $1.0$ and re-sorted in descending order.

---

## 5. Exact Citation Anchor Generation

Citation anchors are generated deterministically by the `StructureAwareParser`:
```text
[Short Title] — [Section / Article / Rule Label]
```
### Real Examples:
1. **Statute:** `Patents Act 1970 — Section 3(p)`
2. **Treaty:** `WIPO GRATK Treaty 2024 — Article 3`
3. **Regulatory Rule:** `Drugs & Cosmetics Act (ASU Framework) — Rule 158-B`
4. **Classical Treaty Schedule:** `Drugs & Cosmetics Act (ASU Framework) — Schedule I`
5. **ABS Statute:** `Biological Diversity Act 2002 — Section 6`

Every anchor points back to an exact SQLite `document_section` and immutable source file with SHA-256 verification.

---

## 6. Safety & Abstention Guardrails

1. **No Unqualified Legal Advice:** In Phase 2A, the system never generates conclusionary statements like *"Your formulation is definitely patentable"*. It provides only verified statutory provisions and exact citations.
2. **TKDL Confidentiality & Safe Abstention:** The system explicitly guards against simulating non-public TKDL prior art search results. When encountering requests for non-public TKDL transcripts, it triggers safe abstention and escalation protocols.
