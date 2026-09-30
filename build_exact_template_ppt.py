"""
Master build script for IP-SAKTI Sahayak (SIH2026).
100% preserves the reference PowerPoint presentation template, layout, fonts, and geometry,
while replacing ALL previous project content and images (SecureMesh/LoRa/Raspberry Pis)
with authentic IP-SAKTI Sahayak assets (Ayurvedic research, Indian legal frameworks, UI prototype, etc.).
"""

import os
import qrcode
from pptx import Presentation
from pptx.util import Pt

def replace_picture_blob(shape, image_path):
    if not os.path.exists(image_path):
        print(f"Warning: image path {image_path} does not exist!")
        return
    rId = shape._element.blip_rId
    img_part = shape.part.related_part(rId)
    with open(image_path, "rb") as f:
        img_part._blob = f.read()

def main():
    src_pptx = r"C:\Projects\Secure mesh\docs\PPT\SecureMesh.pptx"
    out_pptx = r"C:\Projects\drugvista\IP-SAKTI_Sahayak_SIH2026.pptx"
    
    # Asset directories
    assets_dir = r"c:\Projects\drugvista\extracted_assets\new_slide_assets"
    qr_dir = r"c:\Projects\drugvista\extracted_assets\qrcodes"
    ui_screenshot = r"c:\Projects\drugvista\extracted_assets\ui_screenshot.jpg"
    brain_dir = r"C:\Users\kunal\.gemini\antigravity-ide\brain\8c54cd72-cb39-4129-8802-00113cda2b8a"

    os.makedirs(qr_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    # 1. Generate QR codes
    urls = {
        "github": "https://github.com/Rengoku9000/Drugvista",
        "report": "https://github.com/Rengoku9000/Drugvista/tree/main/docs",
        "ipindia": "https://ipindia.gov.in/writereaddata/Portal/IPOAct",
        "wipo": "https://www.wipo.int/edocs/mdocs/tk/en/gratk_dc/gratk_dc_7.pdf",
        "nba": "http://nbaindia.org/content/25/19/1/act.html",
        "ayush": "https://ayush.gov.in/docs/drugs-and-cosmetics-act-1940.pdf",
        "pcimh": "https://pcimh.gov.in",
        "tkdl": "https://www.tkdl.res.in/tkdl/langdefault/common/Abouttkdl.asp",
        "faiss": "https://github.com/facebookresearch/faiss",
        "hf": "https://huggingface.co/sentence-transformers"
    }
    for name, url in urls.items():
        q_img = qrcode.make(url)
        q_img.save(os.path.join(qr_dir, f"{name}.png"))

    prs = Presentation(src_pptx)

    # Helper: update oval badge on any slide to IP-SAKTI
    for slide_idx, s in enumerate(prs.slides):
        for sh in s.shapes:
            if "Oval" in sh.name and sh.has_text_frame:
                for p in sh.text_frame.paragraphs:
                    for r in p.runs:
                        if "OUTLAWS" in r.text:
                            r.text = "IP-SAKTI"

    # =========================================================================
    # SLIDE 1: Title & Overview
    # =========================================================================
    s1 = prs.slides[0]
    for sh in s1.shapes:
        if sh.name == "Subtitle 3":
            tf = sh.text_frame
            for p in tf.paragraphs:
                for r in p.runs:
                    if "SecureMesh" in r.text:
                        r.text = "IP-SAKTI Sahayak"
        elif sh.name == "TextBox 9":
            tf = sh.text_frame
            if len(tf.paragraphs) > 0 and len(tf.paragraphs[0].runs) > 1:
                tf.paragraphs[0].runs[1].text = " – SIH26045"
            if len(tf.paragraphs) > 1 and len(tf.paragraphs[1].runs) > 2:
                tf.paragraphs[1].runs[1].text = " – "
                tf.paragraphs[1].runs[2].text = "Student Innovation – AI-Powered Assistant for Intellectual Property, Traditional Knowledge, and Regulatory Frameworks in Ayurveda."
            if len(tf.paragraphs) > 2 and len(tf.paragraphs[2].runs) > 1:
                tf.paragraphs[2].runs[1].text = " – MedTech / Ayush / LegalTech"
            if len(tf.paragraphs) > 3 and len(tf.paragraphs[3].runs) > 1:
                tf.paragraphs[3].runs[1].text = " – Software"
            if len(tf.paragraphs) > 5 and len(tf.paragraphs[5].runs) > 1:
                tf.paragraphs[5].runs[1].text = " – IP-SAKTI Team"

    # =========================================================================
    # SLIDE 2: Proposed Solution
    # =========================================================================
    s2 = prs.slides[1]
    for sh in s2.shapes:
        if sh.name == "Title 1":
            sh.text_frame.paragraphs[0].runs[0].text = "IP-SAKTI Sahayak – Grounded, Multilingual AI"
        elif sh.name == "Text 6":
            sh.text_frame.paragraphs[0].runs[0].text = "DETERMINISTIC KNOWLEDGE"
        elif sh.name == "Text 10":
            sh.text_frame.paragraphs[0].runs[0].text = "Primary Statutes"
            sh.text_frame.paragraphs[1].runs[0].text = "Ingests Patents Act 1970, Biodiversity Act 2002/23, Drugs & Cosmetics Act 1940."
        elif sh.name == "Text 11":
            sh.text_frame.paragraphs[0].runs[0].text = "Cryptographic Integrity"
            sh.text_frame.paragraphs[1].runs[0].text = "SHA-256 verification prevents phantom laws and LLM hallucination."
        elif sh.name == "Text 12":
            sh.text_frame.paragraphs[0].runs[0].text = "Canonical Section Anchors"
            sh.text_frame.paragraphs[1].runs[0].text = "Direct citation binding to Sec 3(p), Sec 6 NBA, and Schedule 1 ASU classical texts."
        elif sh.name == "Image 4":
            print("Replacing Slide 2 Image 4 (Col 1 Diagram)...")
            replace_picture_blob(sh, os.path.join(assets_dir, "diag_col1_deterministic.png"))

        elif sh.name == "Text 17":
            sh.text_frame.paragraphs[0].runs[0].text = "DUAL-JURISDICTION ISOLATION"
        elif sh.name == "Text 21":
            sh.text_frame.paragraphs[0].runs[0].text = "Zero Cross-Leakage"
            if len(sh.text_frame.paragraphs[1].runs) > 1:
                sh.text_frame.paragraphs[1].runs[0].text = "Strict separation between Indian law "
                sh.text_frame.paragraphs[1].runs[1].text = "and international treaties."
            else:
                sh.text_frame.paragraphs[1].runs[0].text = "Strict separation between Indian law and international treaties."
        elif sh.name == "Text 22":
            sh.text_frame.paragraphs[0].runs[0].text = "Formulation Routing"
            sh.text_frame.paragraphs[1].runs[0].text = "Distinguishes classical compound formulas from novel single-herb extracts."
        elif sh.name == "Text 23":
            sh.text_frame.paragraphs[0].runs[0].text = "Multi-Stage Intelligence"
            sh.text_frame.paragraphs[1].runs[0].text = "Pre-retrieval intent classification and jurisdictional boundaries."
        elif sh.name == "Image 8":
            print("Replacing Slide 2 Image 8 (Col 2 Diagram)...")
            replace_picture_blob(sh, os.path.join(assets_dir, "diag_col2_dual_jurisdiction.png"))

        elif sh.name == "Text 28":
            sh.text_frame.paragraphs[0].runs[0].text = "CITATION PROVENANCE & AUDIT"
        elif sh.name == "Text 32":
            sh.text_frame.paragraphs[0].runs[0].text = "Epistemic Grounding"
            sh.text_frame.paragraphs[1].runs[0].text = "Strict separation between explicit statutory facts and legal interpretation."
        elif sh.name == "Text 33":
            sh.text_frame.paragraphs[0].runs[0].text = "Full Traceability"
            sh.text_frame.paragraphs[1].runs[0].text = "Every recommendation links to gazette authority, enactment date, and official URL."
        elif sh.name == "Text 34":
            sh.text_frame.paragraphs[0].runs[0].text = "Trust Enforcement"
            sh.text_frame.paragraphs[1].runs[0].text = "Answers without verifiable statutory anchors are mathematically rejected."
        elif sh.name == "Image 12":
            print("Replacing Slide 2 Image 12 (Col 3 Diagram)...")
            replace_picture_blob(sh, os.path.join(assets_dir, "diag_col3_citation_provenance.png"))

        elif sh.name == "Text 39":
            sh.text_frame.paragraphs[0].runs[0].text = "TRILINGUAL & DEFENSIVE SAFEGUARD"
        elif sh.name == "Text 43":
            sh.text_frame.paragraphs[0].runs[0].text = "Native Trilingual Engine"
            sh.text_frame.paragraphs[1].runs[0].text = "End-to-end question answering in English, Hindi (Devanagari), and Kannada."
        elif sh.name == "Text 44":
            sh.text_frame.paragraphs[0].runs[0].text = "Citation Immutability"
            sh.text_frame.paragraphs[1].runs[0].text = "Statutory clauses and section numbers remain untranslated and legally pristine."
        elif sh.name == "Text 45":
            sh.text_frame.paragraphs[0].runs[0].text = "TKDL Defensive Compliance"
            sh.text_frame.paragraphs[1].runs[0].text = "Strict non-disclosure protocol: safe abstention on restricted TKDL manuscripts."
        elif sh.name == "Image 16":
            print("Replacing Slide 2 Image 16 (Col 4 Diagram)...")
            replace_picture_blob(sh, os.path.join(assets_dir, "diag_col4_trilingual_safeguard.png"))

        elif sh.name == "Text 49":
            sh.text_frame.paragraphs[0].runs[0].text = "Automated Tests"
            sh.text_frame.paragraphs[1].runs[0].text = "98/98 unit tests passing"
        elif sh.name == "Text 50":
            sh.text_frame.paragraphs[0].runs[0].text = "Working Streamlit Web App"
            sh.text_frame.paragraphs[1].runs[0].text = "UI, live citation cards, trilingual"
        elif sh.name == "Text 51":
            sh.text_frame.paragraphs[0].runs[0].text = "Core Milestone Complete"
            sh.text_frame.paragraphs[1].runs[0].text = "Phase 2C Complete"
        elif sh.name == "Text 52":
            sh.text_frame.paragraphs[0].runs[0].text = "Runs on Commodity Hardware"
            if len(sh.text_frame.paragraphs[1].runs) > 1:
                sh.text_frame.paragraphs[1].runs[0].text = "Local Laptop"
                sh.text_frame.paragraphs[1].runs[1].text = " / CPU-only (No GPU required)"
            else:
                sh.text_frame.paragraphs[1].runs[0].text = "Local Laptop / CPU-only (No GPU required)"
        elif sh.name == "Text 57":
            sh.text_frame.paragraphs[0].runs[0].text = "github.com/Rengoku9000/Drugvista"
            sh.text_frame.paragraphs[0].runs[0].font.size = Pt(14)

    # =========================================================================
    # SLIDE 3: Technical Approach
    # =========================================================================
    s3 = prs.slides[2]
    for sh in s3.shapes:
        if sh.name == "Image 0":
            print("Replacing Slide 3 Image 0 (Knowledge Ingestion)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "ayurveda_manuscript_ai_1790785918790.jpg"))
        elif sh.name == "Text 1":
            sh.text_frame.paragraphs[0].runs[0].text = "Knowledge Ingestion & Parsing"
        elif sh.name == "Text 3":
            sh.text_frame.paragraphs[0].runs[0].text = "Structure-aware parsing of ASU texts,"
            sh.text_frame.paragraphs[1].runs[0].text = "pharmacopoeias & legal gazettes"
        
        elif sh.name == "Image 1":
            print("Replacing Slide 3 Image 1 (Dual Store Graph)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "ayush_dual_store_graph_1790785951914.jpg"))
        elif sh.name == "Text 5":
            sh.text_frame.paragraphs[0].runs[0].text = "Dual-Store Knowledge Graph"
        elif sh.name == "Text 7":
            sh.text_frame.paragraphs[0].runs[0].text = "User Query"
            sh.text_frame.paragraphs[1].runs[0].text = "(Natural Language)"
        elif sh.name == "Text 9":
            sh.text_frame.paragraphs[0].runs[0].text = "Legal Routing"
            sh.text_frame.paragraphs[1].runs[0].text = "(Intent & Jurisdictions)"
        elif sh.name == "Text 11":
            sh.text_frame.paragraphs[0].runs[0].text = "Dual Index"
            sh.text_frame.paragraphs[1].runs[0].text = "(FAISS + SQLite)"
        elif sh.name == "Text 13":
            sh.text_frame.paragraphs[0].runs[0].text = "Trilingual Output"
            sh.text_frame.paragraphs[1].runs[0].text = "(Evidence-Bounded)"

        elif sh.name == "Image 2":
            print("Replacing Slide 3 Image 2 (Legal & Botanicals Background)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "ayurvedic_herbs_statutes_1790785982523.jpg"))
        elif sh.name == "Text 15":
            sh.text_frame.paragraphs[0].runs[0].text = "Authoritative Statutory Corpus & Botanical Standards"
        elif sh.name == "Text 17":
            sh.text_frame.paragraphs[0].runs[0].text = "Patents Act, 1970"
            sh.text_frame.paragraphs[1].runs[0].text = "Section 3(p) TK exclusions"
            sh.text_frame.paragraphs[2].runs[0].text = "(IP India Ingestion)"
        elif sh.name == "Text 19":
            sh.text_frame.paragraphs[0].runs[0].text = "Biodiversity Act"
            sh.text_frame.paragraphs[1].runs[0].text = "NBA Prior Approval"
            sh.text_frame.paragraphs[2].runs[0].text = "(2023 Amendment rules)"
        elif sh.name == "Text 21":
            sh.text_frame.paragraphs[0].runs[0].text = "D&C Act, 1940"
            sh.text_frame.paragraphs[1].runs[0].text = "ASU Rules 1945"
            sh.text_frame.paragraphs[2].runs[0].text = "(Schedule 1 standards)"
        elif sh.name == "Text 23":
            sh.text_frame.paragraphs[0].runs[0].text = "WIPO Treaty"
            sh.text_frame.paragraphs[1].runs[0].text = "GRATK (2024)"
            sh.text_frame.paragraphs[2].runs[0].text = "Mandatory patent disclosure"
        elif sh.name == "Text 25":
            if len(sh.text_frame.paragraphs[0].runs) > 2:
                sh.text_frame.paragraphs[0].runs[0].text = "CSIR-TKDL & PCIM&H ("
                sh.text_frame.paragraphs[0].runs[1].text = "Verified"
                sh.text_frame.paragraphs[0].runs[2].text = ")"
            else:
                sh.text_frame.paragraphs[0].runs[0].text = "CSIR-TKDL & PCIM&H (Verified)"
            sh.text_frame.paragraphs[1].runs[0].text = "Defensive prior art guidelines & ASU pharmacopoeial standards"

        elif sh.name == "Text 30":
            sh.text_frame.paragraphs[0].runs[0].text = "FRONTEND & APP SHELL"
            sh.text_frame.paragraphs[1].runs[0].text = "Cross-platform responsive web UI, custom CSS design system"
        elif sh.name == "Text 31":
            sh.text_frame.paragraphs[0].runs[0].text = "Streamlit"
        elif sh.name == "Text 32":
            sh.text_frame.paragraphs[0].runs[0].text = "Python 3.11"
        elif sh.name == "Text 33":
            sh.text_frame.paragraphs[0].runs[0].text = "HTML5/CSS3"
        elif sh.name == "Text 34":
            sh.text_frame.paragraphs[0].runs[0].text = "BaseWeb"
        elif sh.name == "Text 37":
            sh.text_frame.paragraphs[0].runs[0].text = "APPLICATION & REASONING"
            sh.text_frame.paragraphs[1].runs[0].text = "Deterministic legal logic, epistemic bounding and REST service"
        elif sh.name == "Text 38":
            sh.text_frame.paragraphs[0].runs[0].text = "FastAPI"
        elif sh.name == "Text 39":
            sh.text_frame.paragraphs[0].runs[0].text = "Pydantic V2"
        elif sh.name == "Text 42":
            sh.text_frame.paragraphs[0].runs[0].text = "RETRIEVAL & STORAGE"
            sh.text_frame.paragraphs[1].runs[0].text = "Dense semantic indexing, relational provenance and SHA-256 audit"
        elif sh.name == "Text 43":
            sh.text_frame.paragraphs[0].runs[0].text = "FAISS"
        elif sh.name == "Text 44":
            sh.text_frame.paragraphs[0].runs[0].text = "SQLite (WAL)"
        elif sh.name == "Text 45":
            sh.text_frame.paragraphs[0].runs[0].text = "SHA-256"
        elif sh.name == "Text 46":
            sh.text_frame.paragraphs[0].runs[0].text = "Anchors"
        elif sh.name == "Text 49":
            sh.text_frame.paragraphs[0].runs[0].text = "LOCAL AI & NLP"
            sh.text_frame.paragraphs[1].runs[0].text = "Embedding models and trilingual Indic text generation"
        elif sh.name == "Text 50":
            sh.text_frame.paragraphs[0].runs[0].text = "all-MiniLM"
        elif sh.name == "Text 51":
            sh.text_frame.paragraphs[0].runs[0].text = "Sentence-Trans"
        elif sh.name == "Text 52":
            sh.text_frame.paragraphs[0].runs[0].text = "Indic NLP"
        elif sh.name == "Text 53":
            sh.text_frame.paragraphs[0].runs[0].text = "Regex Parser"

        elif sh.name == "Text 57":
            sh.text_frame.paragraphs[0].runs[0].text = "Presentation Layer"
        elif sh.name == "Text 59":
            sh.text_frame.paragraphs[0].runs[0].text = "Application Layer"
        elif sh.name == "Text 61":
            sh.text_frame.paragraphs[0].runs[0].text = "Storage & Data Layer"
        elif sh.name == "Text 62":
            sh.text_frame.paragraphs[0].runs[0].text = "Streamlit Web App"
        elif sh.name == "Text 63":
            sh.text_frame.paragraphs[0].runs[0].text = "Custom CSS System"
        elif sh.name == "Text 64":
            sh.text_frame.paragraphs[0].runs[0].text = "Trilingual Tabs"
        elif sh.name == "Text 65":
            sh.text_frame.paragraphs[0].runs[0].text = "Citations Panel"
        elif sh.name == "Text 66":
            sh.text_frame.paragraphs[0].runs[0].text = "FastAPI Core Service"
        elif sh.name == "Text 67":
            sh.text_frame.paragraphs[0].runs[0].text = "Intent & Formulation Router"
        elif sh.name == "Text 68":
            sh.text_frame.paragraphs[0].runs[0].text = "Epistemic Reasoner Engine"
        elif sh.name == "Text 69":
            sh.text_frame.paragraphs[0].runs[0].text = "Citation Anchor Validator"
        elif sh.name == "Text 72":
            sh.text_frame.paragraphs[0].runs[0].text = "FAISS Index"
        elif sh.name == "Text 73":
            sh.text_frame.paragraphs[0].runs[0].text = "SQLite (WAL)"
        elif sh.name == "Text 74":
            sh.text_frame.paragraphs[0].runs[0].text = "7 Statutes (SHA-256)"

        elif sh.name == "Image 78":
            replace_picture_blob(sh, os.path.join(qr_dir, "report.png"))
        elif sh.name == "Image 81":
            replace_picture_blob(sh, os.path.join(qr_dir, "github.png"))

    # =========================================================================
    # SLIDE 4: Feasibility and Viability (EXACT SHAPE NAMES!)
    # =========================================================================
    s4 = prs.slides[3]
    for sh in s4.shapes:
        if sh.name == "Text 1":
            sh.text_frame.paragraphs[0].runs[0].text = "Client / UI Node"
            sh.text_frame.paragraphs[1].runs[0].text = "Streamlit Web App (Port 8501)"
        elif sh.name == "Text 3":
            sh.text_frame.paragraphs[0].runs[0].text = "IP-SAKTI REST Core"
            sh.text_frame.paragraphs[1].runs[0].text = "FastAPI + Epistemic Engine (Port 8000)"
        elif sh.name == "Text 5":
            sh.text_frame.paragraphs[0].runs[0].text = "Local Vector Engine"
            sh.text_frame.paragraphs[1].runs[0].text = "FAISS Dense Index + SQLite WAL"
        elif sh.name == "Image 2":
            print("Replacing Slide 4 Image 2 (Vector Engine Icon)...")
            replace_picture_blob(sh, os.path.join(assets_dir, "vector_engine_icon.png"))

        elif sh.name == "Text 16":
            sh.text_frame.paragraphs[0].runs[0].text = "Sub-Second Retrieval"
            sh.text_frame.paragraphs[1].runs[0].text = "Latency <1.2s per complex query on CPU"
        elif sh.name == "Text 18":
            sh.text_frame.paragraphs[0].runs[0].text = "7 Primary Statutes"
            sh.text_frame.paragraphs[1].runs[0].text = "Patents Act, BDA, DCA, WIPO, Nagoya, PCIM&H, TKDL"
        elif sh.name == "Text 20":
            sh.text_frame.paragraphs[0].runs[0].text = "Deterministic Provenance"
            sh.text_frame.paragraphs[1].runs[0].text = "Every clause traced to Act, Section, and official URL"
        elif sh.name == "Text 22":
            sh.text_frame.paragraphs[0].runs[0].text = "Zero-Leakage Routing"
            sh.text_frame.paragraphs[1].runs[0].text = "Strict isolation between India and International treaties"
        elif sh.name == "Text 24":
            sh.text_frame.paragraphs[0].runs[0].text = "Trilingual Intelligence"
            sh.text_frame.paragraphs[1].runs[0].text = "English, Hindi, and Kannada with citation immutability"

        elif sh.name == "Text 26":
            sh.text_frame.paragraphs[0].runs[0].text = "< 1.2 s / query"
            sh.text_frame.paragraphs[1].runs[0].text = "Local AI analysis time"
        elif sh.name == "Text 28":
            sh.text_frame.paragraphs[0].runs[0].text = "CPU-only"
            sh.text_frame.paragraphs[1].runs[0].text = "No GPU required"
        elif sh.name == "Text 30":
            sh.text_frame.paragraphs[0].runs[0].text = "Validated on Laptop & Local CPU"
            sh.text_frame.paragraphs[1].runs[0].text = "Runs on commodity hardware with 98/98 tests passing"

        elif sh.name == "Text 38":
            sh.text_frame.paragraphs[0].runs[0].text = "Diverse State Biodiversity"
            sh.text_frame.paragraphs[1].runs[0].text = "Rules"
        elif sh.name == "Text 39":
            sh.text_frame.paragraphs[0].runs[0].text = "State-by-State automated ABS fee"
            sh.text_frame.paragraphs[1].runs[0].text = "and benefit-sharing calculation engine"
        elif sh.name == "Text 41":
            sh.text_frame.paragraphs[0].runs[0].text = "High Court & IPAB Precedents"
            sh.text_frame.paragraphs[1].runs[0].text = "not yet fully indexed"
        elif sh.name == "Text 42":
            sh.text_frame.paragraphs[0].runs[0].text = "Ingest landmark patent revocation"
            sh.text_frame.paragraphs[1].runs[0].text = "rulings (e.g. Neem, Turmeric cases)"
        elif sh.name == "Text 44":
            sh.text_frame.paragraphs[0].runs[0].text = "Edge SLM Deployment"
            sh.text_frame.paragraphs[1].runs[0].text = "for fully offline usage"
        elif sh.name == "Text 45":
            sh.text_frame.paragraphs[0].runs[0].text = "Deploy 4-bit quantized SLMs"
            sh.text_frame.paragraphs[1].runs[0].text = "(Qwen-1.5B via llama.cpp) on device"
        elif sh.name == "Text 47":
            sh.text_frame.paragraphs[0].runs[0].text = "Live Patent Office Gazette"
            sh.text_frame.paragraphs[1].runs[0].text = "synchronization"
        elif sh.name == "Text 48":
            sh.text_frame.paragraphs[0].runs[0].text = "Direct API integration with IPO"
            sh.text_frame.paragraphs[1].runs[0].text = "weekly published official gazettes"
        elif sh.name == "Text 50":
            sh.text_frame.paragraphs[0].runs[0].text = "We prioritize scientific rigor & transparency."
            sh.text_frame.paragraphs[1].runs[0].text = "Every claim is verified by deterministic tests."

        elif sh.name == "Image 29":
            print("Replacing Slide 4 Image 29 (Prototype Thumbnail)...")
            replace_picture_blob(sh, os.path.join(assets_dir, "ui_thumb_square.jpg"))
        elif sh.name == "Image 30":
            print("Replacing Slide 4 Image 30 (AYUSH Lab Pilot)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "ayush_lab_collaboration_1790786018530.jpg"))
        elif sh.name == "Image 31":
            print("Replacing Slide 4 Image 31 (India Digital Grid)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "india_ayush_digital_grid_1790786055717.jpg"))

        elif sh.name == "Text 58":
            lines = [
                "Streamlit Web App",
                "FastAPI backend",
                "7 primary legal corpora",
                "Sub-1.2s local retrieval",
                "98/98 unit & regression tests"
            ]
            for l_idx, line in enumerate(lines):
                if l_idx < len(sh.text_frame.paragraphs):
                    sh.text_frame.paragraphs[l_idx].runs[0].text = line
        elif sh.name == "Text 63":
            lines = [
                "Deploy across 5 Ayush universities",
                "Pilot with registered patent attorneys",
                "State Biodiversity Board feedback",
                "Latency & accuracy benchmarks"
            ]
            for l_idx, line in enumerate(lines):
                if l_idx < len(sh.text_frame.paragraphs):
                    sh.text_frame.paragraphs[l_idx].runs[0].text = line
        elif sh.name == "Text 68":
            lines = [
                "Integration with National Ayush Mission",
                "MSME IP facilitation cell support",
                "Multilingual rural reach (Hi, Kn, Ta, Te)",
                "Automated weekly gazette updates"
            ]
            for l_idx, line in enumerate(lines):
                if l_idx < len(sh.text_frame.paragraphs):
                    sh.text_frame.paragraphs[l_idx].runs[0].text = line

        elif sh.name == "Text 72":
            sh.text_frame.paragraphs[0].runs[0].text = "Uses commodity CPU hardware"
        elif sh.name == "Text 73":
            sh.text_frame.paragraphs[0].runs[0].text = "Works without cloud dependency"
        elif sh.name == "Text 74":
            sh.text_frame.paragraphs[0].runs[0].text = "Modular & decoupled architecture"
        elif sh.name == "Text 75":
            sh.text_frame.paragraphs[0].runs[0].text = "Strict TKDL confidentiality compliance"

    # =========================================================================
    # SLIDE 5: Impact and Benefits
    # =========================================================================
    s5 = prs.slides[4]
    for sh in s5.shapes:
        # Left 5 Images
        if sh.name == "Image 0":
            print("Replacing Slide 5 Image 0 (Bio-Piracy)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "bio_piracy_shield_1790786174590.jpg"))
        elif sh.name == "Text 38":
            sh.text_frame.paragraphs[0].runs[0].text = "BIO-PIRACY PREVENTION"
        elif sh.name == "Text 40":
            sh.text_frame.paragraphs[0].runs[0].text = "Shields traditional medicine from wrongful patenting abroad by equipping Indian patent agents with instant prior art and statutory Section 3(p) defense."

        elif sh.name == "Image 2":
            print("Replacing Slide 5 Image 2 (Accelerated R&D)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "ayush_rd_lab_1790786214487.jpg"))
        elif sh.name == "Text 45":
            sh.text_frame.paragraphs[0].runs[0].text = "ACCELERATED AYUSH R&D"
        elif sh.name == "Text 47":
            sh.text_frame.paragraphs[0].runs[0].text = "Slashes prior art and regulatory clearance search time from 2–3 weeks to under 2 seconds for researchers and innovators."

        elif sh.name == "Image 4":
            print("Replacing Slide 5 Image 4 (Data Sovereignty)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "data_sovereignty_server_1790786262756.jpg"))
        elif sh.name == "Text 52":
            sh.text_frame.paragraphs[0].runs[0].text = "DATA SOVEREIGNTY & AUDIT"
        elif sh.name == "Text 54":
            sh.text_frame.paragraphs[0].runs[0].text = "Strictly adheres to CSIR-TKDL non-disclosure guidelines and NBA protocols, maintaining complete digital sovereignty."
            if len(sh.text_frame.paragraphs[0].runs) > 1:
                sh.text_frame.paragraphs[0].runs[1].text = ""

        elif sh.name == "Image 6":
            print("Replacing Slide 5 Image 6 (Auditable Legal Trust)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "auditable_legal_trust_1790786313373.jpg"))
        elif sh.name == "Text 59":
            sh.text_frame.paragraphs[0].runs[0].text = "AUDITABLE LEGAL TRUST"
        elif sh.name == "Text 61":
            sh.text_frame.paragraphs[0].runs[0].text = "Deterministic citation anchors eliminate hallucinations in formal patent applications and regulatory clearance filings."

        elif sh.name == "Image 8":
            print("Replacing Slide 5 Image 8 (Affordable Deployment)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "affordable_laptop_cpu_1790786351271.jpg"))
        elif sh.name == "Text 66":
            sh.text_frame.paragraphs[0].runs[0].text = "AFFORDABLE DEPLOYMENT"
        elif sh.name == "Text 68":
            sh.text_frame.paragraphs[0].runs[0].text = "Zero recurring GPU cloud expense; runs on commodity servers, laptops, and institutional private networks."

        # Right 5 Images
        elif sh.name == "Image 10":
            print("Replacing Slide 5 Image 10 (Ayush Researchers)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "ayush_researcher_portrait_1790786385872.jpg"))
        elif sh.name == "Text 73":
            sh.text_frame.paragraphs[0].runs[0].text = "AYUSH RESEARCHERS"
        elif sh.name == "Text 75":
            sh.text_frame.paragraphs[0].runs[0].text = "Instantly evaluate novelty vs Section 3(p) exclusions for novel herbal formulations and clinical abstracts."

        elif sh.name == "Image 12":
            print("Replacing Slide 5 Image 12 (Patent Attorneys)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "patent_attorney_portrait_1790786426288.jpg"))
        elif sh.name == "Text 80":
            sh.text_frame.paragraphs[0].runs[0].text = "PATENT ATTORNEYS"
        elif sh.name == "Text 82":
            sh.text_frame.paragraphs[0].runs[0].text = "Rapid prior-art discovery, statutory defense drafting, and compliance verification across international treaties."

        elif sh.name == "Image 14":
            print("Replacing Slide 5 Image 14 (Herbal MSMEs)...")
            replace_picture_blob(sh, os.path.join(brain_dir, "herbal_msme_portrait_1790786471782.jpg"))
        elif sh.name == "Text 87":
            sh.text_frame.paragraphs[0].runs[0].text = "HERBAL MSMEs"
        elif sh.name == "Text 89":
            sh.text_frame.paragraphs[0].runs[0].text = "Clear guidance on Drugs & Cosmetics Act licensing, Ayurvedic Pharmacopoeia compliance, and NBA approvals."

        elif sh.name == "Image 16":
            print("Replacing Slide 5 Image 16 (Traditional Healers)...")
            replace_picture_blob(sh, os.path.join(assets_dir, "healer_square.jpg"))
        elif sh.name == "Text 94":
            sh.text_frame.paragraphs[0].runs[0].text = "TRADITIONAL HEALERS"
        elif sh.name == "Text 96":
            sh.text_frame.paragraphs[0].runs[0].text = "Native-language access in Hindi & Kannada protects local agricultural biodiversity and community IP rights."

        elif sh.name == "Image 18":
            print("Slide 5 Image 18 (Regulatory Bodies / Secretariat Dome preserved)...")
        elif sh.name == "Text 101":
            sh.text_frame.paragraphs[0].runs[0].text = "REGULATORY BODIES"
        elif sh.name == "Text 103":
            sh.text_frame.paragraphs[0].runs[0].text = "Standardized evidence evaluation framework for ASU commercial applications and benefit-sharing."

        # Strategic value pillars (01 - 05)
        elif sh.name == "Text 106":
            if len(sh.text_frame.paragraphs[0].runs) > 1:
                sh.text_frame.paragraphs[0].runs[0].text = "01  "
                sh.text_frame.paragraphs[0].runs[1].text = "INTERNET-INDEPENDENT"
            sh.text_frame.paragraphs[1].runs[0].text = "Statutory search, evidence retrieval and local analysis continue without cloud dependency."
        elif sh.name == "Text 108":
            if len(sh.text_frame.paragraphs[0].runs) > 1:
                sh.text_frame.paragraphs[0].runs[0].text = "02  "
                sh.text_frame.paragraphs[0].runs[1].text = "SECURITY & CONFIDENTIALITY"
            sh.text_frame.paragraphs[1].runs[0].text = "Sensitive queries remain local; strict non-disclosure guardrails on proprietary TKDL data."
        elif sh.name == "Text 110":
            if len(sh.text_frame.paragraphs[0].runs) > 1:
                sh.text_frame.paragraphs[0].runs[0].text = "03  "
                sh.text_frame.paragraphs[0].runs[1].text = "SUB-SECOND TRIAGE"
            sh.text_frame.paragraphs[1].runs[0].text = "Analyzes complex patentability and regulatory queries in <1.2 seconds on commodity CPU."
        elif sh.name == "Text 112":
            if len(sh.text_frame.paragraphs[0].runs) > 1:
                sh.text_frame.paragraphs[0].runs[0].text = "04  "
                sh.text_frame.paragraphs[0].runs[1].text = "AUDITABLE CITATIONS"
            sh.text_frame.paragraphs[1].runs[0].text = "Every clause traced to official gazette enactment, section number, and primary source URL."
        elif sh.name == "Text 114":
            if len(sh.text_frame.paragraphs[0].runs) > 1:
                sh.text_frame.paragraphs[0].runs[0].text = "05  "
                sh.text_frame.paragraphs[0].runs[1].text = "TRILINGUAL EQUITY"
            sh.text_frame.paragraphs[1].runs[0].text = "Empowers grassroots Ayurvedic practitioners with native Devanagari Hindi and Kannada answers."

        elif sh.name == "Text 118":
            sh.text_frame.paragraphs[0].runs[0].text = "< 1.2 s"
            sh.text_frame.paragraphs[1].runs[0].text = "Local retrieval"
            sh.text_frame.paragraphs[2].runs[0].text = "latency per query"
        elif sh.name == "Text 119":
            sh.text_frame.paragraphs[0].runs[0].text = "CPU-only"
            sh.text_frame.paragraphs[1].runs[0].text = "Runs on commodity"
            sh.text_frame.paragraphs[2].runs[0].text = "hardware (no GPU)"
        elif sh.name == "Text 120":
            sh.text_frame.paragraphs[0].runs[0].text = "98 / 98"
            sh.text_frame.paragraphs[1].runs[0].text = "Automated tests"
            sh.text_frame.paragraphs[2].runs[0].text = "passing (100% pass)"
        elif sh.name == "Text 121":
            sh.text_frame.paragraphs[0].runs[0].text = "7 Sources"
            sh.text_frame.paragraphs[1].runs[0].text = "Authoritative legal"
            sh.text_frame.paragraphs[2].runs[0].text = "statutes ingested"
        elif sh.name == "Text 122":
            sh.text_frame.paragraphs[0].runs[0].text = "100% Auditable"
            sh.text_frame.paragraphs[1].runs[0].text = "Deterministic section"
            sh.text_frame.paragraphs[2].runs[0].text = "provenance anchors"

    # =========================================================================
    # SLIDE 6: Research & References (EXACT SHAPE NAMES!)
    # =========================================================================
    s6 = prs.slides[5]
    for sh in s6.shapes:
        if sh.name == "Subtitle":
            sh.text_frame.paragraphs[0].runs[0].text = "Key technical references used in the IP-SAKTI Sahayak implementation"
        elif sh.name == "Text 3":
            sh.text_frame.paragraphs[0].runs[0].text = "PRIMARY STATUTES & LEGAL FRAMEWORKS"
        elif sh.name == "Text 6":
            sh.text_frame.paragraphs[0].runs[0].text = "The Patents Act, 1970"
            sh.text_frame.paragraphs[1].runs[0].text = "Section 3(p) exclusions, Section 10 disclosures and ASU amendments."
        elif sh.name == "Text 8":
            sh.text_frame.paragraphs[0].runs[0].text = "ipindia.gov.in/writereaddata/Portal/IPOAct"
        elif sh.name == "Image 1":
            replace_picture_blob(sh, os.path.join(qr_dir, "ipindia.png"))

        elif sh.name == "Text 11":
            sh.text_frame.paragraphs[0].runs[0].text = "The Biological Diversity Act, 2002 & 2023"
            sh.text_frame.paragraphs[1].runs[0].text = "NBA prior approvals, Section 6, and Access & Benefit-Sharing rules."
        elif sh.name == "Text 13":
            sh.text_frame.paragraphs[0].runs[0].text = "nbaindia.org/content/25/19/1/act.html"
        elif sh.name == "Image 3":
            replace_picture_blob(sh, os.path.join(qr_dir, "nba.png"))

        elif sh.name == "Text 16":
            sh.text_frame.paragraphs[0].runs[0].text = "Drugs & Cosmetics Act, 1940 (ASU Framework)"
            sh.text_frame.paragraphs[1].runs[0].text = "First Schedule classical formularies and Ayurvedic manufacturing standards."
        elif sh.name == "Text 18":
            sh.text_frame.paragraphs[0].runs[0].text = "ayush.gov.in/docs/drugs-and-cosmetics-act-1940.pdf"
        elif sh.name == "Image 5":
            replace_picture_blob(sh, os.path.join(qr_dir, "ayush.png"))

        elif sh.name == "Text 22":
            sh.text_frame.paragraphs[0].runs[0].text = "MULTILATERAL TREATIES & AGREEMENTS"
        elif sh.name == "Text 25":
            sh.text_frame.paragraphs[0].runs[0].text = "WIPO GRATK Treaty (2024)"
            sh.text_frame.paragraphs[1].runs[0].text = "International patent disclosure standard for genetic resources and TK."
        elif sh.name == "Text 27":
            sh.text_frame.paragraphs[0].runs[0].text = "wipo.int/edocs/mdocs/tk/en/gratk_dc/gratk_dc_7.pdf"
        elif sh.name == "Image 7":
            replace_picture_blob(sh, os.path.join(qr_dir, "wipo.png"))

        elif sh.name == "Text 30":
            sh.text_frame.paragraphs[0].runs[0].text = "Nagoya Protocol (ABS)"
            sh.text_frame.paragraphs[1].runs[0].text = "CBD multilateral framework for fair and equitable benefit-sharing."
        elif sh.name == "Text 32":
            sh.text_frame.paragraphs[0].runs[0].text = "cbd.int/abs/text/default.shtml"

        elif sh.name == "Text 35":
            sh.text_frame.paragraphs[0].runs[0].text = "IP-SAKTI Sahayak GitHub Repository"
            sh.text_frame.paragraphs[1].runs[0].text = "Source code, test suites, and deterministic legal reasoning implementation."
        elif sh.name == "Text 37":
            sh.text_frame.paragraphs[0].runs[0].text = "github.com/Rengoku9000/Drugvista"
        elif sh.name == "Image 11":
            replace_picture_blob(sh, os.path.join(qr_dir, "github.png"))

        elif sh.name == "Text 41":
            sh.text_frame.paragraphs[0].runs[0].text = "AYUSH & TRADITIONAL KNOWLEDGE REPOSITORIES"
        elif sh.name == "Text 44":
            sh.text_frame.paragraphs[0].runs[0].text = "PCIM&H Standards"
            sh.text_frame.paragraphs[1].runs[0].text = "Pharmacopoeial monographs & quality standards for ASU medicines."
        elif sh.name == "Text 46":
            sh.text_frame.paragraphs[0].runs[0].text = "pcimh.gov.in"
        elif sh.name == "Image 13":
            replace_picture_blob(sh, os.path.join(qr_dir, "pcimh.png"))

        elif sh.name == "Text 49":
            sh.text_frame.paragraphs[0].runs[0].text = "CSIR-TKDL Advisory"
            sh.text_frame.paragraphs[1].runs[0].text = "Defensive prior art guidelines and confidential protection protocols."
        elif sh.name == "Text 51":
            sh.text_frame.paragraphs[0].runs[0].text = "tkdl.res.in/tkdl/langdefault/common/Abouttkdl.asp"
        elif sh.name == "Image 15":
            replace_picture_blob(sh, os.path.join(qr_dir, "tkdl.png"))

        elif sh.name == "Text 55":
            sh.text_frame.paragraphs[0].runs[0].text = "CORE SOFTWARE & AI TECHNOLOGIES"
        elif sh.name == "Text 58":
            sh.text_frame.paragraphs[0].runs[0].text = "FAISS Vector Index (Facebook AI)"
            sh.text_frame.paragraphs[1].runs[0].text = "Dense similarity search engine for high-speed sub-second retrieval."
        elif sh.name == "Text 60":
            sh.text_frame.paragraphs[0].runs[0].text = "github.com/facebookresearch/faiss"
        elif sh.name == "Image 17":
            replace_picture_blob(sh, os.path.join(qr_dir, "faiss.png"))

        elif sh.name == "Text 63":
            sh.text_frame.paragraphs[0].runs[0].text = "sentence-transformers (all-MiniLM-L6-v2)"
            sh.text_frame.paragraphs[1].runs[0].text = "Lightweight semantic embedding model running entirely on local CPU."
        elif sh.name == "Text 65":
            sh.text_frame.paragraphs[0].runs[0].text = "huggingface.co/sentence-transformers"
        elif sh.name == "Image 19":
            replace_picture_blob(sh, os.path.join(qr_dir, "hf.png"))

        elif sh.name == "Text 66":
            sh.text_frame.paragraphs[0].runs[0].text = "UI Design — IP-SAKTI Sahayak Working Prototype"
        elif sh.name == "Image 20":
            print("Replacing Image 20 with attached UI screenshot...")
            replace_picture_blob(sh, ui_screenshot)
        elif sh.name == "Text 69":
            sh.text_frame.paragraphs[0].runs[0].text = "IP-SAKTI Sahayak working prototype"
            sh.text_frame.paragraphs[1].runs[0].text = "Query analysis, grounded legal answers, and multilingual translation."

    prs.save(out_pptx)
    print(f"Successfully updated original template and saved to {out_pptx}!")

if __name__ == "__main__":
    main()
