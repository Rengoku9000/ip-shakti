"""
Script to generate the polished 6-slide Smart India Hackathon 2026 Presentation
for SIH Problem Statement SIH26045: IP-SAKTI Sahayak.
Modeled directly on the provided SIH submission reference presentation format and style.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank slide

    # Paths to assets
    base_dir = r"c:\Projects\drugvista"
    assets_dir = os.path.join(base_dir, "extracted_assets")
    sih_logo_path = os.path.join(assets_dir, "sih_logo_clean.png")
    sih_bulb_path = os.path.join(assets_dir, "sih_bulb_clean.png")
    ui_screenshot_path = os.path.join(assets_dir, "ui_screenshot.jpg")
    qr_dir = os.path.join(assets_dir, "qrcodes")

    # Colors
    c_white = RGBColor(255, 255, 255)
    c_dark_green = RGBColor(15, 77, 50)       # #0F4D32
    c_primary_green = RGBColor(18, 107, 69)    # #126B45
    c_light_green = RGBColor(234, 244, 238)    # #EAF4EE
    c_navy = RGBColor(27, 54, 93)              # #1B365D
    c_text_dark = RGBColor(23, 33, 27)         # #17211B
    c_text_muted = RGBColor(82, 96, 87)        # #526057
    c_border = RGBColor(220, 229, 222)         # #DCE5DE
    c_badge_dark = RGBColor(30, 41, 59)        # Slate 800

    # Pillar Colors
    c_blue_pillar = RGBColor(29, 78, 137)
    c_blue_bg = RGBColor(241, 246, 254)
    c_orange_pillar = RGBColor(194, 94, 0)
    c_orange_bg = RGBColor(255, 248, 240)
    c_green_pillar = RGBColor(18, 107, 69)
    c_green_bg = RGBColor(240, 253, 244)
    c_purple_pillar = RGBColor(109, 40, 217)
    c_purple_bg = RGBColor(250, 245, 255)

    def add_header(slide, title_text, slide_num):
        # Top-left OUTLAWS pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(0.26), Inches(1.35), Inches(0.54))
        pill.fill.solid()
        pill.fill.fore_color.rgb = c_badge_dark
        pill.line.fill.background()
        tf = pill.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.text = "OUTLAWS"
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Arial"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = c_white

        # Slide Title
        tb = slide.shapes.add_textbox(Inches(1.9), Inches(0.24), Inches(9.1), Inches(0.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial"
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = c_navy

        # SIH 2026 Logo on top-right
        if os.path.exists(sih_logo_path):
            slide.shapes.add_picture(sih_logo_path, Inches(11.2), Inches(0.18), width=Inches(1.75))

        # Thin divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.4), Inches(0.88), Inches(12.533), Inches(0.015))
        line.fill.solid()
        line.fill.fore_color.rgb = c_border
        line.line.fill.background()

        # Footer
        ft = slide.shapes.add_textbox(Inches(4.5), Inches(7.15), Inches(4.333), Inches(0.3))
        p = ft.text_frame.paragraphs[0]
        p.text = "@SIH Idea submission- Template"
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Arial"
        p.font.size = Pt(9)
        p.font.color.rgb = c_text_muted

        fn = slide.shapes.add_textbox(Inches(12.2), Inches(7.15), Inches(0.8), Inches(0.3))
        p = fn.text_frame.paragraphs[0]
        p.text = str(slide_num)
        p.alignment = PP_ALIGN.RIGHT
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = c_navy

    # =========================================================================
    # SLIDE 1: COVER SLIDE
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)

    # Top Header: SMART INDIA HACKATHON 2026
    tb_top = slide1.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(10.0), Inches(0.8))
    p = tb_top.text_frame.paragraphs[0]
    p.text = "SMART INDIA HACKATHON 2026"
    p.font.name = "Arial"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = c_navy
    p.alignment = PP_ALIGN.CENTER

    # SIH Logo on top right
    if os.path.exists(sih_logo_path):
        slide1.shapes.add_picture(sih_logo_path, Inches(11.0), Inches(0.25), width=Inches(1.9))

    # Project Title (Underlined & Prominent)
    tb_title = slide1.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(10.0), Inches(0.8))
    p = tb_title.text_frame.paragraphs[0]
    p.text = "IP-SAKTI Sahayak"
    p.font.name = "Arial"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.underline = True
    p.font.color.rgb = c_dark_green
    p.alignment = PP_ALIGN.CENTER

    # Left content box with SIH details (Direct on clean canvas, exactly like reference)
    tb_details = slide1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(7.2), Inches(4.8))
    tf_d = tb_details.text_frame
    tf_d.word_wrap = True

    bullets = [
        ("Problem Statement ID – ", "SIH26045"),
        ("Problem Statement Title – ", "\nStudent Innovation – AI-Powered Assistant for Intellectual Property, Traditional Knowledge, and Regulatory Frameworks in Ayurveda."),
        ("Theme – ", "Disaster Management / MedTech / Ayush / LegalTech"),
        ("PS Category – ", "Software"),
        ("Team ID – ", "146711"),
        ("Team Name – ", "Outlaws")
    ]

    for i, (label, val) in enumerate(bullets):
        p = tf_d.add_paragraph() if i > 0 else tf_d.paragraphs[0]
        p.space_after = Pt(12)
        run1 = p.add_run()
        run1.text = "• " + label
        run1.font.bold = True
        run1.font.size = Pt(14)
        run1.font.color.rgb = c_text_dark
        run1.font.name = "Arial"

        run2 = p.add_run()
        run2.text = val
        run2.font.bold = (label != "Problem Statement Title – ")
        run2.font.size = Pt(14)
        run2.font.color.rgb = c_dark_green if label == "Problem Statement ID – " else c_text_dark
        run2.font.name = "Arial"

    # Right side: SIH Bulb Graphic
    if os.path.exists(sih_bulb_path):
        slide1.shapes.add_picture(sih_bulb_path, Inches(8.3), Inches(1.8), width=Inches(4.5))

    # =========================================================================
    # SLIDE 2: PROPOSED SOLUTION
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "IP-SAKTI Sahayak – Authoritative, Multilingual, Evidence-Grounded", 2)

    # Sub-heading
    tb_prop = slide2.shapes.add_textbox(Inches(0.4), Inches(0.92), Inches(4.0), Inches(0.35))
    p = tb_prop.text_frame.paragraphs[0]
    p.text = "◆ Proposed Solution"
    p.font.name = "Arial"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = c_navy

    pillars = [
        {
            "num": "1",
            "title": "DETERMINISTIC STATUTORY KNOWLEDGE",
            "bg": c_blue_bg,
            "border": c_blue_pillar,
            "items": [
                ("Primary Legislation Index", "Ingests 7 primary statutes: Patents Act 1970, Biological Diversity Act 2002/2023, Drugs & Cosmetics Act 1940."),
                ("Cryptographic Integrity", "SHA-256 cryptographic verification prevents phantom laws and LLM hallucination."),
                ("Canonical Section Anchors", "Direct citation binding to Sec 3(p), Sec 6 NBA, and Schedule 1 ASU classical texts.")
            ]
        },
        {
            "num": "2",
            "title": "DUAL-JURISDICTION ISOLATION",
            "bg": c_orange_bg,
            "border": c_orange_pillar,
            "items": [
                ("Zero Cross-Leakage", "Strict separation between Indian statutory regime and international treaties (WIPO GRATK 2024, Nagoya)."),
                ("Formulation-Aware Routing", "Distinguishes classical compound formulas from novel single-herb extracts automatically."),
                ("Multi-Stage Intelligence", "Pre-retrieval intent classification and jurisdictional boundaries prior to RAG search.")
            ]
        },
        {
            "num": "3",
            "title": "CITATION PROVENANCE & AUDIT",
            "bg": c_green_bg,
            "border": c_green_pillar,
            "items": [
                ("Epistemic Grounding", "Strict separation between explicit statutory facts and legal interpretation."),
                ("Full Traceability", "Every recommendation links to gazette authority, enactment date, and official portal URL."),
                ("Trust Enforcement", "Answers without verifiable statutory anchors are mathematically rejected.")
            ]
        },
        {
            "num": "4",
            "title": "TRILINGUAL ACCESS & TKDL SAFEGUARD",
            "bg": c_purple_bg,
            "border": c_purple_pillar,
            "items": [
                ("Native Trilingual Engine", "End-to-end question answering in English, Hindi (Devanagari), and Kannada."),
                ("Citation Immutability", "Statutory clauses and section numbers remain untranslated and legally pristine."),
                ("TKDL Defensive Compliance", "Strict non-disclosure protocol: safe abstention on restricted TKDL manuscripts.")
            ]
        }
    ]

    card_w = Inches(2.95)
    card_h = Inches(3.2)
    start_x = Inches(0.4)
    gap = Inches(0.24)
    top_y = Inches(1.3)

    for i, pil in enumerate(pillars):
        x = start_x + i * (card_w + gap)
        box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, top_y, card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = pil["bg"]
        box.line.color.rgb = pil["border"]
        box.line.width = Pt(1.5)

        hbar = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.08), top_y + Inches(0.08), card_w - Inches(0.16), Inches(0.48))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = pil["border"]
        hbar.line.fill.background()
        p = hbar.text_frame.paragraphs[0]
        p.text = f"{pil['num']}  {pil['title']}"
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Arial"
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = c_white

        tf_c = box.text_frame
        tf_c.word_wrap = True
        tf_c.margin_left = Inches(0.14)
        tf_c.margin_right = Inches(0.14)
        tf_c.margin_top = Inches(0.62)

        for j, (head, body) in enumerate(pil["items"]):
            p = tf_c.add_paragraph() if j > 0 else tf_c.paragraphs[0]
            p.space_after = Pt(6)
            r1 = p.add_run()
            r1.text = head + "\n"
            r1.font.bold = True
            r1.font.size = Pt(9.5)
            r1.font.color.rgb = c_text_dark
            r1.font.name = "Arial"

            r2 = p.add_run()
            r2.text = body
            r2.font.bold = False
            r2.font.size = Pt(8.5)
            r2.font.color.rgb = c_text_muted
            r2.font.name = "Arial"

    # Middle query workflow diagram bar
    diag_y = Inches(4.65)
    diag_box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), diag_y, Inches(12.533), Inches(1.35))
    diag_box.fill.solid()
    diag_box.fill.fore_color.rgb = c_white
    diag_box.line.color.rgb = c_border
    diag_box.line.width = Pt(1)

    steps = [
        ("Natural Language Query", "User asks in English, Hindi, or Kannada", "👤"),
        ("Query Understanding & Routing", "Intent, entities, formulation & jurisdiction classification", "⚙"),
        ("Dual Vector + Relational Store", "FAISS dense similarity + SQLite authority metadata", "🗄"),
        ("Epistemic Reasoner", "Evidence-bounded legal analysis with citation binding", "⚖"),
        ("Authoritative Trilingual Output", "Grounded response, key points & direct official URLs", "📑")
    ]

    step_w = Inches(2.3)
    step_gap = Inches(0.2)
    step_start_x = Inches(0.55)
    for k, (stitle, sdesc, sicon) in enumerate(steps):
        sx = step_start_x + k * (step_w + step_gap)
        sbox = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx, diag_y + Inches(0.12), step_w, Inches(1.1))
        sbox.fill.solid()
        sbox.fill.fore_color.rgb = c_light_green
        sbox.line.color.rgb = c_primary_green
        sbox.line.width = Pt(1)
        tf_s = sbox.text_frame
        tf_s.word_wrap = True
        tf_s.margin_left = Inches(0.08)
        tf_s.margin_right = Inches(0.08)
        tf_s.margin_top = Inches(0.08)

        p = tf_s.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = f"{sicon} {stitle}"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = c_dark_green

        p2 = tf_s.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = sdesc
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = c_text_muted

        if k < len(steps) - 1:
            arr = slide2.shapes.add_textbox(sx + step_w - Inches(0.05), diag_y + Inches(0.45), step_gap + Inches(0.1), Inches(0.4))
            pa = arr.text_frame.paragraphs[0]
            pa.text = "➔"
            pa.alignment = PP_ALIGN.CENTER
            pa.font.name = "Arial"
            pa.font.size = Pt(14)
            pa.font.bold = True
            pa.font.color.rgb = c_primary_green

    # Bottom Banner: PROOF, NOT PITCH
    proof_y = Inches(6.15)
    proof_box = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.4), proof_y, Inches(12.533), Inches(0.85))
    proof_box.fill.solid()
    proof_box.fill.fore_color.rgb = c_badge_dark
    proof_box.line.fill.background()

    tb_pr_title = slide2.shapes.add_textbox(Inches(0.5), proof_y + Inches(0.1), Inches(2.2), Inches(0.65))
    tf_pt = tb_pr_title.text_frame
    p = tf_pt.paragraphs[0]
    p.text = "PROOF, NOT PITCH"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = c_white
    p2 = tf_pt.add_paragraph()
    p2.text = "Validated prototype with real tests"
    p2.font.name = "Arial"
    p2.font.size = Pt(8.5)
    p2.font.color.rgb = RGBColor(148, 163, 184)

    proof_items = [
        ("98/98 Passing Tests", "Automated test suites across 4 phases"),
        ("Working Streamlit App", "Multi-screen UI, live citations, trilingual"),
        ("Sub-1.2s Response Time", "Deterministic retrieval on local CPU (no GPU)"),
        ("7 Canonical Statutes", "100% cryptographic SHA-256 provenance")
    ]
    p_w = Inches(2.4)
    p_start = Inches(2.8)
    for m, (mtitle, msub) in enumerate(proof_items):
        mx = p_start + m * (p_w + Inches(0.1))
        tb_m = slide2.shapes.add_textbox(mx, proof_y + Inches(0.1), p_w, Inches(0.65))
        tf_m = tb_m.text_frame
        p = tf_m.paragraphs[0]
        p.text = "✔ " + mtitle
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = RGBColor(52, 211, 153)
        p2 = tf_m.add_paragraph()
        p2.text = msub
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = RGBColor(203, 213, 225)

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "TECHNICAL APPROACH", 3)

    # Left Section: Ingestion & Verification Pipeline
    sec1_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(1.05), Inches(5.9), Inches(2.8))
    sec1_box.fill.solid()
    sec1_box.fill.fore_color.rgb = c_white
    sec1_box.line.color.rgb = c_border
    sec1_box.line.width = Pt(1)

    h1 = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.4), Inches(1.05), Inches(5.9), Inches(0.4))
    h1.fill.solid()
    h1.fill.fore_color.rgb = c_navy
    h1.line.fill.background()
    p = h1.text_frame.paragraphs[0]
    p.text = "  Knowledge Ingestion & Provenance Architecture"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = c_white

    flow_items = [
        ("1. Official Gazette / Treaty Source", "Verified portals: IP India, National Biodiversity Authority, WIPO, PCIM&H", c_blue_bg, c_blue_pillar),
        ("2. SHA-256 Manifest Verification", "Cryptographic hash check ensures zero altered or unverified text enters production", c_orange_bg, c_orange_pillar),
        ("3. Structure-Aware Legal Parser", "Dissects statutory chapters, sections, rules, proviso clauses & schedules", c_green_bg, c_green_pillar),
        ("4. Dual Vector + Relational Store", "FAISS (dense semantic vectors) + SQLite (relational provenance & authorities)", c_purple_bg, c_purple_pillar)
    ]
    f_y = Inches(1.52)
    for n, (ftitle, fdesc, fbg, fbrd) in enumerate(flow_items):
        fb = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.55), f_y + n * Inches(0.56), Inches(5.6), Inches(0.48))
        fb.fill.solid()
        fb.fill.fore_color.rgb = fbg
        fb.line.color.rgb = fbrd
        fb.line.width = Pt(1)
        tf_f = fb.text_frame
        tf_f.word_wrap = True
        tf_f.margin_left = Inches(0.12)
        tf_f.margin_top = Inches(0.04)
        p = tf_f.paragraphs[0]
        p.text = ftitle + ": "
        p.font.name = "Arial"
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = c_text_dark
        r = p.add_run()
        r.text = fdesc
        r.font.bold = False
        r.font.size = Pt(8)
        r.font.color.rgb = c_text_muted

    # Lower Left Section: 4-Layer System Architecture
    sec2_box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(4.0), Inches(5.9), Inches(2.95))
    sec2_box.fill.solid()
    sec2_box.fill.fore_color.rgb = c_white
    sec2_box.line.color.rgb = c_border
    sec2_box.line.width = Pt(1)

    h2 = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.4), Inches(4.0), Inches(5.9), Inches(0.4))
    h2.fill.solid()
    h2.fill.fore_color.rgb = c_dark_green
    h2.line.fill.background()
    p = h2.text_frame.paragraphs[0]
    p.text = "  System Architecture (Layered Decomposition)"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = c_white

    layers = [
        ("Layer 1: Presentation & UI", "Streamlit 1.37, custom professional CSS, responsive cards, trilingual toggle"),
        ("Layer 2: Routing & Intelligence", "FastAPI REST endpoints, Intent Classifier, Formulation Extractor, Epistemic Reasoner"),
        ("Layer 3: Vector & Provenance Engine", "FAISS Index (all-MiniLM-L6-v2), SQLite relational database with WAL journal mode"),
        ("Layer 4: Statutory Knowledge Corpus", "The Patents Act 1970, Biological Diversity Act 2002/23, DCA 1940, WIPO GRATK 2024")
    ]
    l_y = Inches(4.5)
    for l_idx, (ltitle, ldesc) in enumerate(layers):
        lb = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.55), l_y + l_idx * Inches(0.58), Inches(5.6), Inches(0.5))
        lb.fill.solid()
        lb.fill.fore_color.rgb = c_light_green
        lb.line.color.rgb = c_primary_green
        lb.line.width = Pt(1)
        tf_l = lb.text_frame
        tf_l.word_wrap = True
        tf_l.margin_left = Inches(0.12)
        tf_l.margin_top = Inches(0.04)
        p = tf_l.paragraphs[0]
        p.text = ltitle + "\n"
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = c_dark_green
        p2 = tf_l.add_paragraph()
        p2.text = ldesc
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = c_text_muted

    # Middle Section: TECH STACK
    tb_ts = slide3.shapes.add_textbox(Inches(6.5), Inches(0.95), Inches(3.5), Inches(0.35))
    p = tb_ts.text_frame.paragraphs[0]
    p.text = "◆ TECH STACK"
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = c_navy

    tech_stacks = [
        {
            "cat": "FRONTEND & APP SHELL",
            "desc": "Cross-platform responsive web UI, custom CSS design system, live multi-tab layout",
            "tags": ["Streamlit", "Python 3.11", "HTML5/CSS3", "BaseWeb"],
            "color": c_blue_pillar,
            "bg": c_blue_bg
        },
        {
            "cat": "CORE ENGINE & REASONING",
            "desc": "REST API service, evidence-bounded legal reasoning, epistemic uncertainty modeling",
            "tags": ["FastAPI", "Uvicorn", "Pydantic V2", "Epistemic Engine"],
            "color": c_orange_pillar,
            "bg": c_orange_bg
        },
        {
            "cat": "VECTOR RETRIEVAL & STORAGE",
            "desc": "Dense vector similarity indexing, ACID relational provenance, cryptographic audit",
            "tags": ["FAISS", "SQLite (WAL)", "SHA-256", "Citation Anchors"],
            "color": c_green_pillar,
            "bg": c_green_bg
        },
        {
            "cat": "LOCAL AI & MULTILINGUAL NLP",
            "desc": "Semantic dense embedding model, multi-script Devanagari & Kannada synthesis",
            "tags": ["all-MiniLM-L6-v2", "sentence-transformers", "Regex Parsers", "Indic NLP"],
            "color": c_purple_pillar,
            "bg": c_purple_bg
        }
    ]

    ts_y = Inches(1.3)
    ts_w = Inches(4.7)
    for t_idx, ts in enumerate(tech_stacks):
        box_t = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.5), ts_y + t_idx * Inches(1.4), ts_w, Inches(1.25))
        box_t.fill.solid()
        box_t.fill.fore_color.rgb = ts["bg"]
        box_t.line.color.rgb = ts["color"]
        box_t.line.width = Pt(1.5)

        tf_t = box_t.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = Inches(0.15)
        tf_t.margin_top = Inches(0.1)

        p = tf_t.paragraphs[0]
        p.text = ts["cat"]
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = ts["color"]

        p2 = tf_t.add_paragraph()
        p2.text = ts["desc"]
        p2.font.name = "Arial"
        p2.font.size = Pt(8.5)
        p2.font.color.rgb = c_text_muted

        p3 = tf_t.add_paragraph()
        p3.text = " • ".join(ts["tags"])
        p3.font.name = "Arial"
        p3.font.size = Pt(9.0)
        p3.font.bold = True
        p3.font.color.rgb = c_text_dark

    # Right Section: Dedicated QR Boxes (REPORT and SOURCE CODE)
    qr_github_path = os.path.join(qr_dir, "github.png")
    qr_report_path = os.path.join(qr_dir, "report.png")

    # Report Box
    rbox = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.45), Inches(1.3), Inches(1.48), Inches(2.65))
    rbox.fill.solid()
    rbox.fill.fore_color.rgb = c_white
    rbox.line.color.rgb = c_border
    rbox.line.width = Pt(1)

    r_hdr = slide3.shapes.add_textbox(Inches(11.45), Inches(1.35), Inches(1.48), Inches(0.35))
    p = r_hdr.text_frame.paragraphs[0]
    p.text = "REPORT"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = c_navy

    if os.path.exists(qr_report_path):
        slide3.shapes.add_picture(qr_report_path, Inches(11.59), Inches(1.72), width=Inches(1.2))

    tb_lbl1 = slide3.shapes.add_textbox(Inches(11.45), Inches(3.05), Inches(1.48), Inches(0.8))
    p = tb_lbl1.text_frame.paragraphs[0]
    p.text = "Scan to read\ndetailed audit\nand reports"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(8.0)
    p.font.color.rgb = c_text_muted

    # Source Code Box
    sbox = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(11.45), Inches(4.2), Inches(1.48), Inches(2.75))
    sbox.fill.solid()
    sbox.fill.fore_color.rgb = c_white
    sbox.line.color.rgb = c_border
    sbox.line.width = Pt(1)

    s_hdr = slide3.shapes.add_textbox(Inches(11.45), Inches(4.25), Inches(1.48), Inches(0.35))
    p = s_hdr.text_frame.paragraphs[0]
    p.text = "SOURCE CODE"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = c_dark_green

    if os.path.exists(qr_github_path):
        slide3.shapes.add_picture(qr_github_path, Inches(11.59), Inches(4.62), width=Inches(1.2))

    tb_lbl2 = slide3.shapes.add_textbox(Inches(11.45), Inches(5.95), Inches(1.48), Inches(0.8))
    p = tb_lbl2.text_frame.paragraphs[0]
    p.text = "Scan to view\nGitHub repository\nand tests"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(8.0)
    p.font.color.rgb = c_text_muted

    # =========================================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "FEASIBILITY AND VIABILITY", 4)

    # Sub banner across top
    top_stat = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(0.95), Inches(12.533), Inches(0.42))
    top_stat.fill.solid()
    top_stat.fill.fore_color.rgb = c_light_green
    top_stat.line.color.rgb = c_primary_green
    top_stat.line.width = Pt(1)
    p = top_stat.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "Local CPU Inference Engine  •  FastAPI Backend (Port 8000)  •  Streamlit Web UI (Port 8501)  •  SHA-256 Provenance Ledger"
    p.font.name = "Arial"
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = c_dark_green

    col_w = Inches(3.95)
    col_gap = Inches(0.34)
    y_start = Inches(1.48)
    col_h = Inches(4.35)

    # Column 1: VALIDATED TODAY
    c1 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), y_start, col_w, col_h)
    c1.fill.solid()
    c1.fill.fore_color.rgb = c_white
    c1.line.color.rgb = c_green_pillar
    c1.line.width = Pt(1.5)

    h_c1 = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.4), y_start, col_w, Inches(0.42))
    h_c1.fill.solid()
    h_c1.fill.fore_color.rgb = c_green_pillar
    h_c1.line.fill.background()
    p = h_c1.text_frame.paragraphs[0]
    p.text = "  ✔ VALIDATED TODAY"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = c_white

    v_items = [
        ("Sub-Second Deterministic Retrieval", "Latency <1.2s per complex query on standard commodity CPU."),
        ("7 Authoritative Primary Corpora", "Patents Act 1970, BDA 2002/23, DCA 1940, WIPO 2024, Nagoya, PCIM&H, TKDL."),
        ("Zero Cross-Jurisdiction Leakage", "Strict isolation ensures international treaties never contaminate Indian statutory analysis."),
        ("100% Citation Provenance", "Every legal finding links to exact section, gazette URL, and authority."),
        ("Native Trilingual Intelligence", "English, Hindi (Devanagari), and Kannada with citation immutability."),
        ("Safe Abstention Guardrail", "Zero risk of leaking confidential or non-public TKDL prior art."),
        ("98/98 Automated Tests Passing", "Comprehensive unit and integration regression test suite with 100% success.")
    ]
    tf_v = c1.text_frame
    tf_v.word_wrap = True
    tf_v.margin_left = Inches(0.18)
    tf_v.margin_right = Inches(0.18)
    tf_v.margin_top = Inches(0.5)

    for idx, (head, desc) in enumerate(v_items):
        p = tf_v.add_paragraph() if idx > 0 else tf_v.paragraphs[0]
        p.space_after = Pt(4)
        r1 = p.add_run()
        r1.text = "✔ " + head + ": "
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = c_dark_green
        r1.font.name = "Arial"

        r2 = p.add_run()
        r2.text = desc
        r2.font.bold = False
        r2.font.size = Pt(7.8)
        r2.font.color.rgb = c_text_muted
        r2.font.name = "Arial"

    # Column 2: KNOWN LIMITATIONS -> NEXT STEPS
    c2_x = Inches(0.4) + col_w + col_gap
    c2 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c2_x, y_start, col_w, col_h)
    c2.fill.solid()
    c2.fill.fore_color.rgb = c_white
    c2.line.color.rgb = c_orange_pillar
    c2.line.width = Pt(1.5)

    h_c2 = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, c2_x, y_start, col_w, Inches(0.42))
    h_c2.fill.solid()
    h_c2.fill.fore_color.rgb = c_orange_pillar
    h_c2.line.fill.background()
    p = h_c2.text_frame.paragraphs[0]
    p.text = "  ⚠ KNOWN LIMITATIONS ➔ NEXT STEPS"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = c_white

    lim_items = [
        ("Diverse State Biodiversity Rules", "➔ Next: Automated State-by-State ABS fee and benefit-sharing calculation engine."),
        ("High Court & IPAB Jurisprudence", "➔ Next: Ingest landmark patent disputes and revocation precedents (Neem, Turmeric)."),
        ("Fully Offline Field Deployment", "➔ Next: Deploy 4-bit quantized Small Language Models (Qwen-1.5B via llama.cpp) on edge."),
        ("Real-Time Patent Gazette Sync", "➔ Next: Direct API integration with Indian Patent Office (IPO) weekly published gazettes.")
    ]
    l_y_sub = y_start + Inches(0.52)
    for idx, (lim, next_step) in enumerate(lim_items):
        lbox = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c2_x + Inches(0.12), l_y_sub + idx * Inches(0.78), col_w - Inches(0.24), Inches(0.72))
        lbox.fill.solid()
        lbox.fill.fore_color.rgb = c_orange_bg
        lbox.line.color.rgb = c_orange_pillar
        lbox.line.width = Pt(1)
        tf_l = lbox.text_frame
        tf_l.word_wrap = True
        tf_l.margin_left = Inches(0.1)
        tf_l.margin_top = Inches(0.04)

        p = tf_l.paragraphs[0]
        p.text = "⚠ " + lim
        p.font.name = "Arial"
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = c_orange_pillar

        p2 = tf_l.add_paragraph()
        p2.text = next_step
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.bold = False
        p2.font.color.rgb = c_text_dark

    tb_tr = slide4.shapes.add_textbox(c2_x + Inches(0.12), y_start + Inches(3.72), col_w - Inches(0.24), Inches(0.55))
    p = tb_tr.text_frame.paragraphs[0]
    p.text = "🛡 We prioritize scientific rigor & transparency.\nEvery claim is verified by deterministic tests."
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(8.0)
    p.font.bold = True
    p.font.color.rgb = c_text_muted

    # Column 3: FIELD VIABILITY -> DEPLOYMENT PATH
    c3_x = c2_x + col_w + col_gap
    c3 = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c3_x, y_start, col_w, col_h)
    c3.fill.solid()
    c3.fill.fore_color.rgb = c_white
    c3.line.color.rgb = c_blue_pillar
    c3.line.width = Pt(1.5)

    h_c3 = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, c3_x, y_start, col_w, Inches(0.42))
    h_c3.fill.solid()
    h_c3.fill.fore_color.rgb = c_blue_pillar
    h_c3.line.fill.background()
    p = h_c3.text_frame.paragraphs[0]
    p.text = "  📊 FIELD VIABILITY ➔ DEPLOYMENT PATH"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = c_white

    deploy_steps = [
        ("1", "Prototype (Validated)", [
            "Streamlit Web + Desktop App",
            "FastAPI deterministic backend",
            "7 primary verified legal corpora",
            "Sub-1.2s local CPU retrieval",
            "98/98 unit & regression tests"
        ], c_blue_pillar),
        ("2", "Pilot (Field Testing)", [
            "Deploy across 5 Ayush universities",
            "Pilot with registered patent attorneys",
            "State Biodiversity Board feedback",
            "Real-world query latency benchmarks"
        ], c_orange_pillar),
        ("3", "National Rollout (Scale)", [
            "Integration with National Ayush Mission",
            "MSME IP facilitation cell support",
            "Multilingual rural reach (Hi, Kn, Ta, Te)",
            "Automated weekly gazette updates"
        ], c_green_pillar)
    ]

    d_y = y_start + Inches(0.5)
    for dnum, dtitle, dpoints, dcol in deploy_steps:
        dbox = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c3_x + Inches(0.12), d_y, col_w - Inches(0.24), Inches(1.15))
        dbox.fill.solid()
        dbox.fill.fore_color.rgb = c_white
        dbox.line.color.rgb = dcol
        dbox.line.width = Pt(1)

        npill = slide4.shapes.add_shape(MSO_SHAPE.OVAL, c3_x + Inches(0.18), d_y + Inches(0.08), Inches(0.3), Inches(0.3))
        npill.fill.solid()
        npill.fill.fore_color.rgb = dcol
        npill.line.fill.background()
        p = npill.text_frame.paragraphs[0]
        p.text = dnum
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Arial"
        p.font.size = Pt(9)
        p.font.bold = True
        p.font.color.rgb = c_white

        tb_dt = slide4.shapes.add_textbox(c3_x + Inches(0.55), d_y + Inches(0.05), col_w - Inches(0.7), Inches(0.3))
        p = tb_dt.text_frame.paragraphs[0]
        p.text = dtitle
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = dcol

        tb_db = slide4.shapes.add_textbox(c3_x + Inches(0.2), d_y + Inches(0.32), col_w - Inches(0.4), Inches(0.8))
        tf_db = tb_db.text_frame
        tf_db.word_wrap = True
        for b_idx, pt in enumerate(dpoints):
            p = tf_db.add_paragraph() if b_idx > 0 else tf_db.paragraphs[0]
            p.text = "• " + pt
            p.font.name = "Arial"
            p.font.size = Pt(7.5)
            p.font.color.rgb = c_text_muted

        d_y += Inches(1.25)

    # Bottom bar: WHY IT IS VIABLE
    why_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), Inches(6.0), Inches(12.533), Inches(0.95))
    why_box.fill.solid()
    why_box.fill.fore_color.rgb = c_white
    why_box.line.color.rgb = c_border
    why_box.line.width = Pt(1)

    why_reasons = [
        ("Commodity Hardware", "Runs purely on standard CPU laptops or servers without GPU dependency."),
        ("Zero Cloud Lock-in", "Local vector search and inference eliminate recurring third-party API expenses."),
        ("Modular & Decoupled", "FastAPI backend and Streamlit UI can scale independently across cloud or edge."),
        ("Strict Ethical Guardrails", "Honors TKDL non-disclosure guidelines; prevents biopiracy and data leakage.")
    ]
    w_w = Inches(3.0)
    for w_idx, (whead, wdesc) in enumerate(why_reasons):
        wx = Inches(0.55) + w_idx * Inches(3.08)
        tb_w = slide4.shapes.add_textbox(wx, Inches(6.05), w_w, Inches(0.85))
        tf_w = tb_w.text_frame
        tf_w.word_wrap = True
        p = tf_w.paragraphs[0]
        p.text = "💡 " + whead
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = c_dark_green

        p2 = tf_w.add_paragraph()
        p2.text = wdesc
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = c_text_muted

    # =========================================================================
    # SLIDE 5: IMPACT AND BENEFITS
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "IMPACT AND BENEFITS", 5)

    hub = slide5.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.66), Inches(2.2), Inches(2.0), Inches(2.0))
    hub.fill.solid()
    hub.fill.fore_color.rgb = c_light_green
    hub.line.color.rgb = c_primary_green
    hub.line.width = Pt(3)
    p = hub.text_frame.paragraphs[0]
    p.text = "IMPACT\n&\nBENEFITS"
    p.alignment = PP_ALIGN.CENTER
    p.font.name = "Arial"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = c_dark_green

    left_impacts = [
        ("1", "BIO-PIRACY PREVENTION", "Shields traditional medicine from wrongful patenting abroad by equipping Indian patent agents with instant prior art and statutory Section 3(p) defense."),
        ("2", "ACCELERATED AYUSH R&D", "Slashes prior art and regulatory clearance search time from 2–3 weeks to under 2 seconds for researchers and innovators."),
        ("3", "DATA SOVEREIGNTY & AUDIT", "Strictly adheres to CSIR-TKDL non-disclosure guidelines and NBA protocols, maintaining complete digital sovereignty."),
        ("4", "AUDITABLE LEGAL TRUST", "Deterministic citation anchors eliminate hallucinations in formal patent applications and regulatory clearance filings."),
        ("5", "COST-EFFECTIVE DEPLOYMENT", "Zero recurring GPU cloud expense; runs on commodity servers, laptops, and institutional private networks.")
    ]

    ly = Inches(1.05)
    for num, ititle, idesc in left_impacts:
        box_i = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), ly, Inches(5.0), Inches(0.92))
        box_i.fill.solid()
        box_i.fill.fore_color.rgb = c_white
        box_i.line.color.rgb = c_border
        box_i.line.width = Pt(1)

        np = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), ly + Inches(0.12), Inches(0.35), Inches(0.35))
        np.fill.solid()
        np.fill.fore_color.rgb = c_dark_green
        np.line.fill.background()
        p = np.text_frame.paragraphs[0]
        p.text = num
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = c_white

        tb = slide5.shapes.add_textbox(Inches(0.95), ly + Inches(0.04), Inches(4.35), Inches(0.85))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = ititle
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = c_navy

        p2 = tf.add_paragraph()
        p2.text = idesc
        p2.font.name = "Arial"
        p2.font.size = Pt(7.8)
        p2.font.color.rgb = c_text_muted

        ly += Inches(0.98)

    right_beneficiaries = [
        ("1", "AYUSH RESEARCHERS & ACADEMIA", "Instantly evaluate novelty vs Section 3(p) exclusions for novel herbal formulations and clinical abstracts."),
        ("2", "PATENT ATTORNEYS & AGENTS", "Rapid prior-art discovery, statutory defense drafting, and compliance verification across international treaties."),
        ("3", "HERBAL MSMEs & STARTUPS", "Clear guidance on Drugs & Cosmetics Act licensing, Ayurvedic Pharmacopoeia compliance, and NBA approvals."),
        ("4", "TRADITIONAL HEALERS & FARMERS", "Native-language access in Hindi & Kannada protects local agricultural biodiversity and community IP rights."),
        ("5", "REGULATORY BODIES (NBA / CDSCO)", "Standardized evidence evaluation framework for ASU commercial applications and benefit-sharing.")
    ]

    ry = Inches(1.05)
    for num, btitle, bdesc in right_beneficiaries:
        box_b = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.93), ry, Inches(5.0), Inches(0.92))
        box_b.fill.solid()
        box_b.fill.fore_color.rgb = c_white
        box_b.line.color.rgb = c_border
        box_b.line.width = Pt(1)

        np = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.03), ry + Inches(0.12), Inches(0.35), Inches(0.35))
        np.fill.solid()
        np.fill.fore_color.rgb = c_primary_green
        np.line.fill.background()
        p = np.text_frame.paragraphs[0]
        p.text = num
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = c_white

        tb = slide5.shapes.add_textbox(Inches(8.48), ry + Inches(0.04), Inches(4.35), Inches(0.85))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = btitle
        p.font.name = "Arial"
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = c_dark_green

        p2 = tf.add_paragraph()
        p2.text = bdesc
        p2.font.name = "Arial"
        p2.font.size = Pt(7.8)
        p2.font.color.rgb = c_text_muted

        ry += Inches(0.98)

    val_y = Inches(6.05)
    val_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), val_y, Inches(12.533), Inches(0.95))
    val_box.fill.solid()
    val_box.fill.fore_color.rgb = c_badge_dark
    val_box.line.fill.background()

    tb_vr = slide5.shapes.add_textbox(Inches(0.5), val_y + Inches(0.12), Inches(2.2), Inches(0.7))
    tf_vr = tb_vr.text_frame
    p = tf_vr.paragraphs[0]
    p.text = "VALIDATED RESULTS"
    p.font.name = "Arial"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = c_white
    p2 = tf_vr.add_paragraph()
    p2.text = "Measured on Working Prototype"
    p2.font.name = "Arial"
    p2.font.size = Pt(8.0)
    p2.font.color.rgb = RGBColor(148, 163, 184)

    results_data = [
        ("< 1.2 s", "Local Retrieval Latency"),
        ("CPU-Only", "No Dedicated GPU Required"),
        ("98 / 98", "Automated Tests Passing"),
        ("7 Sources", "Authoritative Statutes Ingested"),
        ("100% Auditable", "Deterministic Section Provenance")
    ]
    r_w = Inches(1.95)
    for r_idx, (rval, rlbl) in enumerate(results_data):
        rx = Inches(2.8) + r_idx * Inches(1.92)
        tb_r = slide5.shapes.add_textbox(rx, val_y + Inches(0.1), r_w, Inches(0.75))
        tf_r = tb_r.text_frame
        p = tf_r.paragraphs[0]
        p.text = rval
        p.font.name = "Arial"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = RGBColor(52, 211, 153)
        p2 = tf_r.add_paragraph()
        p2.text = rlbl
        p2.font.name = "Arial"
        p2.font.size = Pt(8.0)
        p2.font.color.rgb = RGBColor(226, 232, 240)

    # =========================================================================
    # SLIDE 6: RESEARCH & REFERENCES
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "RESEARCH & REFERENCES", 6)

    ref_categories = [
        {
            "num": "1",
            "title": "PRIMARY STATUTES & LEGAL FRAMEWORKS",
            "border": c_blue_pillar,
            "qr": "ipindia",
            "items": [
                ("The Patents Act, 1970 (Sec 2, 3(p), 10)", "ipindia.gov.in/writereaddata/Portal/IPOAct"),
                ("The Biological Diversity Act, 2002 & 2023", "nbaindia.org/content/25/19/1/act.html"),
                ("Drugs and Cosmetics Act, 1940 (ASU Framework)", "ayush.gov.in/docs/drugs-and-cosmetics-act-1940.pdf")
            ]
        },
        {
            "num": "2",
            "title": "MULTILATERAL TREATIES & AGREEMENTS",
            "border": c_orange_pillar,
            "qr": "wipo",
            "items": [
                ("WIPO GRATK Treaty (Diplomatic Act, May 2024)", "wipo.int/edocs/mdocs/tk/en/gratk_dc/gratk_dc_7.pdf"),
                ("Nagoya Protocol on Access & Benefit-Sharing", "cbd.int/abs/text/default.shtml")
            ]
        },
        {
            "num": "3",
            "title": "AYUSH & TRADITIONAL KNOWLEDGE REPOSITORIES",
            "border": c_green_pillar,
            "qr": "pcimh",
            "items": [
                ("PCIM&H Pharmacopoeial Standards & Guidance", "pcimh.gov.in"),
                ("CSIR-TKDL Defensive Prior Art Mandate", "tkdl.res.in/tkdl/langdefault/common/Abouttkdl.asp")
            ]
        },
        {
            "num": "4",
            "title": "CORE SOFTWARE & AI TECHNOLOGIES",
            "border": c_purple_pillar,
            "qr": "github",
            "items": [
                ("IP-SAKTI Sahayak GitHub Repository", "github.com/Rengoku9000/Drugvista"),
                ("FAISS Vector Index (Facebook AI)", "github.com/facebookresearch/faiss"),
                ("sentence-transformers (all-MiniLM-L6-v2)", "huggingface.co/sentence-transformers")
            ]
        }
    ]

    ref_y = Inches(1.02)
    ref_w = Inches(6.8)
    for cat in ref_categories:
        c_box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.4), ref_y, ref_w, Inches(1.36))
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = c_white
        c_box.line.color.rgb = cat["border"]
        c_box.line.width = Pt(1.5)

        htag = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.48), ref_y + Inches(0.06), Inches(3.8), Inches(0.28))
        htag.fill.solid()
        htag.fill.fore_color.rgb = cat["border"]
        htag.line.fill.background()
        p = htag.text_frame.paragraphs[0]
        p.text = f"{cat['num']}  {cat['title']}"
        p.font.name = "Arial"
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = c_white

        # QR Code image on right of card
        qr_file = os.path.join(qr_dir, f"{cat['qr']}.png")
        if os.path.exists(qr_file):
            slide6.shapes.add_picture(qr_file, Inches(6.2), ref_y + Inches(0.18), width=Inches(0.9))

        tf_it = c_box.text_frame
        tf_it.word_wrap = True
        tf_it.margin_left = Inches(0.12)
        tf_it.margin_right = Inches(1.1)
        tf_it.margin_top = Inches(0.38)

        for it_idx, (it_title, it_url) in enumerate(cat["items"]):
            p = tf_it.add_paragraph() if it_idx > 0 else tf_it.paragraphs[0]
            p.space_after = Pt(2)
            r1 = p.add_run()
            r1.text = "• " + it_title + ": "
            r1.font.bold = True
            r1.font.size = Pt(8.0)
            r1.font.color.rgb = c_text_dark
            r1.font.name = "Arial"

            r2 = p.add_run()
            r2.text = it_url
            r2.font.bold = False
            r2.font.size = Pt(7.5)
            r2.font.color.rgb = c_blue_pillar
            r2.font.name = "Arial"

        ref_y += Inches(1.44)

    # Right Column: UI DESIGN - WORKING PROTOTYPE (Using user-attached UI screenshot)
    ui_x = Inches(7.4)
    ui_y = Inches(1.02)
    ui_w = Inches(5.533)
    ui_h = Inches(5.95)

    ui_panel = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, ui_x, ui_y, ui_w, ui_h)
    ui_panel.fill.solid()
    ui_panel.fill.fore_color.rgb = c_white
    ui_panel.line.color.rgb = c_border
    ui_panel.line.width = Pt(1.5)

    ui_hdr = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, ui_x, ui_y, ui_w, Inches(0.38))
    ui_hdr.fill.solid()
    ui_hdr.fill.fore_color.rgb = c_dark_green
    ui_hdr.line.fill.background()
    p = ui_hdr.text_frame.paragraphs[0]
    p.text = "  UI Design — IP-SAKTI Sahayak Working Prototype"
    p.font.name = "Arial"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = c_white

    # Embed User-Attached UI Image
    if os.path.exists(ui_screenshot_path):
        slide6.shapes.add_picture(ui_screenshot_path, ui_x + Inches(0.12), ui_y + Inches(0.48), width=ui_w - Inches(0.24))

    tb_cap = slide6.shapes.add_textbox(ui_x + Inches(0.12), ui_y + Inches(4.35), ui_w - Inches(0.24), Inches(1.5))
    tf_cap = tb_cap.text_frame
    tf_cap.word_wrap = True

    p = tf_cap.paragraphs[0]
    p.text = "Working Prototype Capabilities Illustrated:"
    p.font.name = "Arial"
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = c_navy

    caps = [
        "1. Home Portal: Quick access to Ask Assistant, Ayurveda & TK, and IP & Legal frameworks.",
        "2. Query Understanding: Auto-detected intent, topic, formulation type, and jurisdiction badges.",
        "3. Authoritative Sources: Direct citation cards linking to Patents Act 1970, TKDL, and Pharmacopoeia.",
        "4. Trilingual Translation: Native Devanagari Hindi and Kannada synthesis with citation immutability."
    ]
    for c in caps:
        p = tf_cap.add_paragraph()
        p.text = "• " + c
        p.font.name = "Arial"
        p.font.size = Pt(8.0)
        p.font.color.rgb = c_text_muted

    # Save presentation
    output_path = os.path.join(base_dir, "IP-SAKTI_Sahayak_SIH2026.pptx")
    prs.save(output_path)
    print(f"Polished presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_presentation()
