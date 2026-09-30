"""
Boundary-Aware Document Chunker for DrugVista
Splits documents deterministically into overlapping chunks while tracking
exact character offsets, chunk ordering, and boundary semantics.
"""
import re
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import config
from models import ChunkMetadata


class DocumentChunker:
    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP
        if self.chunk_overlap >= self.chunk_size:
            self.chunk_overlap = max(0, self.chunk_size // 4)

    def chunk_text(self, text: str, document_id: str, extra_metadata: Optional[Dict[str, Any]] = None) -> List[ChunkMetadata]:
        """
        Split text into overlapping chunks respecting paragraph and sentence boundaries.
        Returns a list of ChunkMetadata instances with accurate start/end character offsets.
        """
        extra_meta = extra_metadata or {}
        text_len = len(text)
        if text_len == 0:
            return []

        # If text is shorter than chunk size, return single chunk
        if text_len <= self.chunk_size:
            chunk_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            return [
                ChunkMetadata(
                    id=f"{document_id}_chunk_0",
                    document_id=document_id,
                    chunk_index=0,
                    content=text,
                    start_offset=0,
                    end_offset=text_len,
                    token_count=max(1, len(text.split())),
                    content_hash=chunk_hash,
                    metadata=extra_meta
                )
            ]

        chunks: List[ChunkMetadata] = []
        start = 0
        chunk_index = 0

        while start < text_len:
            # Determine preliminary end
            tentative_end = min(start + self.chunk_size, text_len)
            
            if tentative_end == text_len:
                actual_end = text_len
            else:
                # Seek a natural break point (paragraph > sentence > space)
                # Look backwards from tentative_end down to start + (chunk_size // 2)
                min_boundary = start + max(1, self.chunk_size // 2)
                window = text[min_boundary:tentative_end]
                
                # Priority 1: Double newline (paragraph boundary)
                p_idx = window.rfind("\n\n")
                if p_idx != -1:
                    actual_end = min_boundary + p_idx + 2
                else:
                    # Priority 2: Sentence boundary (. ! ? followed by space or newline)
                    sentence_matches = list(re.finditer(r'[\.\!\?]\s', window))
                    if sentence_matches:
                        last_match = sentence_matches[-1]
                        actual_end = min_boundary + last_match.end()
                    else:
                        # Priority 3: Single newline
                        nl_idx = window.rfind("\n")
                        if nl_idx != -1:
                            actual_end = min_boundary + nl_idx + 1
                        else:
                            # Priority 4: Word boundary (space)
                            space_idx = window.rfind(" ")
                            if space_idx != -1:
                                actual_end = min_boundary + space_idx + 1
                            else:
                                # Hard cut if no natural boundary found
                                actual_end = tentative_end

            chunk_text_slice = text[start:actual_end]
            clean_text = chunk_text_slice.strip()
            
            if len(clean_text) > 0:
                # Calculate offsets relative to original text
                trimmed_start = start + chunk_text_slice.find(clean_text)
                trimmed_end = trimmed_start + len(clean_text)
                chunk_hash = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
                
                chunks.append(
                    ChunkMetadata(
                        id=f"{document_id}_chunk_{chunk_index}",
                        document_id=document_id,
                        chunk_index=chunk_index,
                        content=clean_text,
                        start_offset=trimmed_start,
                        end_offset=trimmed_end,
                        token_count=max(1, len(clean_text.split())),
                        content_hash=chunk_hash,
                        metadata=extra_meta
                    )
                )
                chunk_index += 1

            if actual_end >= text_len:
                break
                
            # Slide forward by chunk_size - overlap
            start = max(start + 1, actual_end - self.chunk_overlap)

        return chunks
