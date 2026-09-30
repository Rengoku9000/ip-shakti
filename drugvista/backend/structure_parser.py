"""
Structure-Aware Legal & Regulatory Parser for DrugVista / IP-SAKTI Sahayak
Extracts hierarchical document sections, generates deterministic citation anchors,
and produces structure-bounded chunks with strict legal provenance.
"""
import re
import uuid
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from models import DocumentSection, ChunkMetadata, DocumentMetadata, SectionType, AuthorityLevel, Jurisdiction
from document_chunker import DocumentChunker


@dataclass
class ParsedLegalDocument:
    metadata: Dict[str, Any]
    sections: List[DocumentSection]
    section_contents: Dict[str, str]  # section_id -> text content
    clean_full_text: str


class StructureAwareParser:
    """
    Parses structured statutes, treaties, rules, and guidance documents.
    Preserves exact section markers and builds deterministic citation anchors.
    """
    SECTION_MARKER_REGEX = re.compile(r'\[SECTION:\s*([^\]]+)\]', re.IGNORECASE)
    NATURAL_HEADER_REGEX = re.compile(
        r'^(?:\[SECTION:\s*([^\]]+)\]|((?:Section|Article|Rule|Clause|Schedule|The\s+First\s+Schedule)\s+[0-9A-Za-z\(\)\-]+(?:\s*[-–—:]\s*[^\n]+)?))',
        re.MULTILINE | re.IGNORECASE
    )
    METADATA_BLOCK_REGEX = re.compile(r'=== SOURCE METADATA ===(.*?)=== END METADATA ===', re.DOTALL)

    @staticmethod
    def generate_citation_anchor(title: str, section: Any) -> str:
        """Deterministic citation anchor generator: '{Title} — {Section/Article/Rule}'"""
        label = getattr(section, "section_label", str(section))
        return f"{title} — {label}"

    def parse_text(
        self,
        raw_text: str = "",
        document_id: str = "doc_default",
        text: Optional[str] = None,
        doc_title: Optional[str] = None,
        **kwargs
    ) -> ParsedLegalDocument:
        """Parse text containing metadata header and structural section markers or natural headers"""
        effective_text = text if text is not None else raw_text
        metadata = {}
        if doc_title:
            metadata["title"] = doc_title
        for k, v in kwargs.items():
            metadata[k] = v

        body_text = effective_text

        # Extract metadata block if present
        meta_match = self.METADATA_BLOCK_REGEX.search(effective_text)
        if meta_match:
            meta_str = meta_match.group(1).strip()
            for line in meta_str.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    metadata[k.strip().lower()] = v.strip()
            body_text = effective_text[meta_match.end():].strip()

        # Split into sections based on [SECTION: ...] markers first, then fallback to natural headers
        matches = list(self.SECTION_MARKER_REGEX.finditer(body_text))
        is_natural = False
        if not matches:
            matches = list(self.NATURAL_HEADER_REGEX.finditer(body_text))
            is_natural = True

        sections: List[DocumentSection] = []
        section_contents: Dict[str, str] = {}
        
        if not matches:
            # Fallback: treat entire body as a single general section
            sec_id = f"{document_id}_sec_general"
            sec = DocumentSection(
                id=sec_id,
                document_id=document_id,
                parent_id=None,
                section_type=SectionType.SECTION.value,
                section_label="General Provisions",
                section_title=metadata.get("title", "General Provisions"),
                sequence=0
            )
            sections.append(sec)
            section_contents[sec_id] = body_text
            return ParsedLegalDocument(
                metadata=metadata,
                sections=sections,
                section_contents=section_contents,
                clean_full_text=body_text
            )

        clean_parts = []
        for i, match in enumerate(matches):
            raw_label = (match.group(1) or match.group(2) or "").strip()
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(body_text)
            sec_content = body_text[start_pos:end_pos].strip()

            sec_id = f"{document_id}_sec_{i+1}"
            sec_type, sec_title = self._infer_section_type_and_title(raw_label, sec_content)

            sec = DocumentSection(
                id=sec_id,
                document_id=document_id,
                parent_id=None,
                section_type=sec_type,
                section_label=raw_label,
                section_title=sec_title,
                sequence=i + 1
            )
            sections.append(sec)
            section_contents[sec_id] = sec_content
            clean_parts.append(f"[{raw_label}]\n{sec_content}")

        return ParsedLegalDocument(
            metadata=metadata,
            sections=sections,
            section_contents=section_contents,
            clean_full_text="\n\n".join(clean_parts)
        )

    def create_structured_chunks(
        self,
        parsed_doc: ParsedLegalDocument,
        document_id: str,
        chunk_size: int = 600,
        chunk_overlap: int = 100
    ) -> List[ChunkMetadata]:
        """
        Create chunks respecting legal section boundaries.
        Each chunk is tagged with its section_id and a deterministic citation anchor.
        """
        chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        all_chunks: List[ChunkMetadata] = []
        global_chunk_idx = 0

        short_title = parsed_doc.metadata.get("short_title") or parsed_doc.metadata.get("title", "Statute")
        authority_level = parsed_doc.metadata.get("authority_level", AuthorityLevel.PRIMARY.value)
        jurisdiction = parsed_doc.metadata.get("jurisdiction", Jurisdiction.INDIA.value)

        for sec in parsed_doc.sections:
            content = parsed_doc.section_contents.get(sec.id, "")
            if not content:
                continue

            # Deterministic Citation Anchor: e.g. "Patents Act 1970 — Section 3(p)"
            citation_anchor = f"{short_title} — {sec.section_label}"

            # Chunk within section boundary
            sec_chunks = chunker.chunk_text(
                text=content,
                document_id=document_id,
                extra_metadata={
                    "section_id": sec.id,
                    "section_label": sec.section_label,
                    "section_type": sec.section_type,
                    "citation_anchor": citation_anchor,
                    "authority_level": authority_level,
                    "jurisdiction": jurisdiction,
                    "short_title": short_title
                }
            )

            for sc in sec_chunks:
                sc.id = f"{document_id}_chunk_{global_chunk_idx}"
                sc.chunk_index = global_chunk_idx
                sc.section_id = sec.id
                sc.citation_anchor = citation_anchor
                sc.authority_level = authority_level
                sc.jurisdiction = jurisdiction
                all_chunks.append(sc)
                global_chunk_idx += 1

        return all_chunks

    @staticmethod
    def _infer_section_type_and_title(raw_label: str, content: str) -> Tuple[str, Optional[str]]:
        """Determine SectionType and extract heading title from first line"""
        label_lower = raw_label.lower()
        if "article" in label_lower:
            sec_type = SectionType.ARTICLE.value
        elif "rule" in label_lower:
            sec_type = SectionType.RULE.value
        elif "schedule" in label_lower:
            sec_type = SectionType.SCHEDULE.value
        elif "chapter" in label_lower:
            sec_type = SectionType.CHAPTER.value
        elif "verse" in label_lower:
            sec_type = SectionType.VERSE.value
        elif "clause" in label_lower:
            sec_type = SectionType.CLAUSE.value
        else:
            sec_type = SectionType.SECTION.value

        # Extract title from the first line if formatted as "Section X - Title:"
        first_line = content.splitlines()[0] if content else ""
        title = None
        if " - " in first_line:
            parts = first_line.split(" - ", 1)
            title = parts[1].split(":")[0].strip()
        elif ":" in first_line and len(first_line.split(":")[0]) < 60:
            title = first_line.split(":")[0].strip()
        return sec_type, title


# Singleton instance
structure_parser = StructureAwareParser()
