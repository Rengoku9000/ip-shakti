"""
Multi-Format Document Loader and Normalizer for DrugVista
Supports TXT, PDF, DOCX, CSV, and JSON formats.
"""
import os
import csv
import json
import hashlib
from io import StringIO, BytesIO
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path


def normalize_text(text: str) -> str:
    """Normalize newlines and clean whitespace consistently"""
    if not text:
        return ""
    # Standardize Windows / Unix newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip leading/trailing whitespace
    return text.strip()


def compute_sha256(text: str) -> str:
    """Compute SHA-256 hash of normalized text for deterministic deduplication"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class DocumentLoader:
    ALLOWED_EXTENSIONS = {'.txt', '.csv', '.json', '.pdf', '.docx'}

    @classmethod
    def load_from_bytes(cls, content: bytes, filename: str, doc_type: str = "document", description: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parse in-memory file bytes into one or more normalized document records.
        Structured formats like CSV can yield multiple records.
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file format '{ext}'. Allowed: {', '.join(cls.ALLOWED_EXTENSIONS)}")

        results: List[Dict[str, Any]] = []

        if ext == '.pdf':
            text = cls._extract_pdf(content)
            norm = normalize_text(text)
            if len(norm) >= 10:
                results.append({
                    "filename": filename,
                    "content": norm,
                    "content_hash": compute_sha256(norm),
                    "source_type": doc_type,
                    "title": filename,
                    "description": description or f"PDF document: {filename}"
                })

        elif ext == '.docx':
            text = cls._extract_docx(content)
            norm = normalize_text(text)
            if len(norm) >= 10:
                results.append({
                    "filename": filename,
                    "content": norm,
                    "content_hash": compute_sha256(norm),
                    "source_type": doc_type,
                    "title": filename,
                    "description": description or f"DOCX document: {filename}"
                })

        elif ext == '.csv':
            # Each valid row becomes a document record
            text_content = content.decode('utf-8', errors='replace')
            reader = csv.DictReader(StringIO(text_content))
            for i, row in enumerate(reader):
                row_text = "\n".join([f"{k}: {v}" for k, v in row.items() if v])
                norm = normalize_text(row_text)
                if len(norm) >= 10:
                    row_name = f"{filename}_row_{i+1}"
                    results.append({
                        "filename": row_name,
                        "content": norm,
                        "content_hash": compute_sha256(norm),
                        "source_type": doc_type,
                        "title": f"{filename} (Row {i+1})",
                        "description": description or f"CSV row {i+1} from {filename}"
                    })

        elif ext == '.json':
            text_content = content.decode('utf-8', errors='replace')
            data = json.loads(text_content)
            if isinstance(data, list):
                for i, item in enumerate(data):
                    item_text = "\n".join([f"{k}: {v}" for k, v in item.items()]) if isinstance(item, dict) else str(item)
                    norm = normalize_text(item_text)
                    if len(norm) >= 10:
                        results.append({
                            "filename": f"{filename}_item_{i+1}",
                            "content": norm,
                            "content_hash": compute_sha256(norm),
                            "source_type": doc_type,
                            "title": f"{filename} (Item {i+1})",
                            "description": description or f"JSON record {i+1} from {filename}"
                        })
            else:
                item_text = "\n".join([f"{k}: {v}" for k, v in data.items()]) if isinstance(data, dict) else str(data)
                norm = normalize_text(item_text)
                if len(norm) >= 10:
                    results.append({
                        "filename": filename,
                        "content": norm,
                        "content_hash": compute_sha256(norm),
                        "source_type": doc_type,
                        "title": filename,
                        "description": description or f"JSON document: {filename}"
                    })

        else:
            # Plain text
            text_content = content.decode('utf-8', errors='replace')
            norm = normalize_text(text_content)
            if len(norm) >= 10:
                results.append({
                    "filename": filename,
                    "content": norm,
                    "content_hash": compute_sha256(norm),
                    "source_type": doc_type,
                    "title": filename,
                    "description": description or f"Text document: {filename}"
                })

        return results

    @classmethod
    def load_from_file(cls, file_path: Path, doc_type: str = "document") -> List[Dict[str, Any]]:
        """Load document from a local file path"""
        path = Path(file_path)
        with open(path, "rb") as f:
            content = f.read()
        return cls.load_from_bytes(content, filename=path.name, doc_type=doc_type)

    @staticmethod
    def _extract_pdf(content: bytes) -> str:
        import PyPDF2
        reader = PyPDF2.PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    @staticmethod
    def _extract_docx(content: bytes) -> str:
        from docx import Document
        doc = Document(BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
