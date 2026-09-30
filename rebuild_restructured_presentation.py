import os
import shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

SRC_PPT = r"c:\Projects\drugvista\IP-SAKTI_Sahayak_SIH2026.pptx"
DST_PPT = r"c:\Projects\drugvista\IP-SAKTI_Sahayak_SIH2026.pptx"

# Color Palette
NAVY_DARK = RGBColor(11, 37, 69)       # #0B2545
NAVY_MED = RGBColor(27, 54, 93)        # #1B365D
GREEN_DARK = RGBColor(11, 79, 52)      # #0B4F34
GREEN_LIGHT = RGBColor(230, 246, 238)  # #E6F6EE
AMBER = RGBColor(217, 119, 6)          # #D97706
AMBER_LIGHT = RGBColor(254, 243, 235)  # #FEF3EB
BLUE_ACCENT = RGBColor(37, 99, 235)    # #2563EB
BLUE_LIGHT = RGBColor(239, 246, 255)   # #EFF6FF
SLATE_DARK = RGBColor(15, 23, 42)      # #0F172A
SLATE_MUTED = RGBColor(71, 85, 105)    # #475569
SLATE_BORDER = RGBColor(226, 232, 240) # #E2E8F0
BG_CARD = RGBColor(248, 250, 252)      # #F8FAFC
BG_HERO = RGBColor(241, 245, 249)      # #F1F5F9
WHITE = RGBColor(255, 255, 255)

ICONS_DIR = r"c:\Projects\drugvista\extracted_assets\custom_icons"
ASSETS_DIR = r"c:\Projects\drugvista\extracted_assets"
BRAIN_DIR = r"C:\Users\kunal\.gemini\antigravity-ide\brain\8c54cd72-cb39-4129-8802-00113cda2b8a"
QR_DIR = r"c:\Projects\drugvista\extracted_assets\qrcodes"
UI_PATH = os.path.join(ASSETS_DIR, "ui_screenshot.jpg")

prs = Presentation(SRC_PPT)

def clear_interior_shapes(slide, framing_names):
    for s in list(slide.shapes):
        if s.name not in framing_names:
            el = s._element
            el.getparent().remove(el)

def add_card(slide, left, top, width, height, bg_color=WHITE, border_color=SLATE_BORDER, border_width=Pt(1)):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = border_width
    else:
        card.line.fill.background()
    return card

def add_badge(slide, left, top, width, height, text, bg_color, text_color=WHITE, font_size=Pt(10), bold=True):
    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    b.fill.solid()
    b.fill.fore_color.rgb = bg_color
    b.line.fill.background()
    tf = b.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = PP_ALIGN.CENTER
    p.font.size = font_size
    p.font.bold = bold
    p.font.color.rgb = text_color
    p.font.name = "Segoe UI"
    return b

def add_text_box(slide, left, top, width, height):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf

# ==============================================================================
# SLIDE 2: PROPOSED SOLUTION
# ==============================================================================
print("Redesigning Slide 2...")
slide2 = prs.slides[1]
clear_interior_shapes(slide2, {'Rectangle 8', 'Slide Number Placeholder 5', 'Footer Placeholder 6', 'Title 1', 'Oval 9', 'Picture 10'})

for s in slide2.shapes:
    if s.name == 'Title 1':
        s.text_frame.text = "PROPOSED SOLUTION"
        p = s.text_frame.paragraphs[0]
        p.font.name = "Segoe UI"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = NAVY_DARK

# Top Hero Proposition Banner
add_card(slide2, Inches(0.4), Inches(1.05), Inches(12.53), Inches(0.85), bg_color=BG_HERO, border_color=SLATE_BORDER)
tf = add_text_box(slide2, Inches(0.6), Inches(1.12), Inches(8.5), Inches(0.7))
p1 = tf.paragraphs[0]
p1.text = "A Grounded, Sovereign AI Copilot for Ayurvedic Intellectual Property"
p1.font.size = Pt(14)
p1.font.bold = True
p1.font.color.rgb = NAVY_DARK
p1.font.name = "Segoe UI"
p2 = tf.add_paragraph()
p2.text = "Deterministic legal synthesis resolving the trilemma of Ayurvedic Prior Art, Section 3(p) exclusions, and trilingual equity."
p2.font.size = Pt(10)
p2.font.color.rgb = SLATE_MUTED
p2.font.name = "Segoe UI"

add_badge(slide2, Inches(9.3), Inches(1.2), Inches(3.4), Inches(0.55), "Zero Cloud Dependency  •  Local CPU  •  SHA-256", GREEN_DARK, WHITE, font_size=Pt(9.5))

# 3 Solution Pillars
pillar_w = Inches(4.04)
pillar_gap = Inches(0.2)
pillar_y = Inches(2.05)
pillar_h = Inches(2.65)

# --- PILLAR 1 ---
x1 = Inches(0.4)
add_card(slide2, x1, pillar_y, pillar_w, pillar_h, bg_color=WHITE, border_color=SLATE_BORDER)
slide2.shapes.add_picture(os.path.join(ICONS_DIR, "icon_book_statute.png"), x1 + Inches(0.2), pillar_y + Inches(0.2), Inches(0.55), Inches(0.55))
tf = add_text_box(slide2, x1 + Inches(0.85), pillar_y + Inches(0.2), pillar_w - Inches(1.0), Inches(0.55))
p = tf.paragraphs[0]
p.text = "Authoritative Legal Ingestion"
p.font.size = Pt(12.5)
p.font.bold = True
p.font.color.rgb = NAVY_DARK
p2 = tf.add_paragraph()
p2.text = "Cryptographic integrity on primary statutes"
p2.font.size = Pt(9)
p2.font.color.rgb = AMBER

bullets1 = [
    ("Primary Statutes Ingestion: ", "Direct parsing of The Patents Act 1970, Biological Diversity Act 2002/2023, and Drugs & Cosmetics Act 1940."),
    ("SHA-256 Checksums: ", "Prevents LLM hallucinations or phantom citations; strictly grounded in official Gazette provisions."),
    ("Pharmacopoeial Binding: ", "Links classical Ayurvedic formulations directly to official Ayurvedic Pharmacopoeia (API) monographs.")
]
tf_b1 = add_text_box(slide2, x1 + Inches(0.2), pillar_y + Inches(0.85), pillar_w - Inches(0.4), Inches(1.7))
for i, (b_title, b_desc) in enumerate(bullets1):
    p = tf_b1.paragraphs[0] if i == 0 else tf_b1.add_paragraph()
    if i > 0: p.space_before = Pt(4)
    run1 = p.add_run()
    run1.text = "• " + b_title
    run1.font.bold = True
    run1.font.size = Pt(9.5)
    run1.font.color.rgb = SLATE_DARK
    run2 = p.add_run()
    run2.text = b_desc
    run2.font.size = Pt(9)
    run2.font.color.rgb = SLATE_MUTED

# --- PILLAR 2 ---
x2 = x1 + pillar_w + pillar_gap
add_card(slide2, x2, pillar_y, pillar_w, pillar_h, bg_color=WHITE, border_color=SLATE_BORDER)
slide2.shapes.add_picture(os.path.join(ICONS_DIR, "icon_shield.png"), x2 + Inches(0.2), pillar_y + Inches(0.2), Inches(0.55), Inches(0.55))
tf = add_text_box(slide2, x2 + Inches(0.85), pillar_y + Inches(0.2), pillar_w - Inches(1.0), Inches(0.55))
p = tf.paragraphs[0]
p.text = "Dual-Jurisdiction Reasoner"
p.font.size = Pt(12.5)
p.font.bold = True
p.font.color.rgb = NAVY_DARK
p2 = tf.add_paragraph()
p2.text = "Zero cross-leakage between jurisdictions"
p2.font.size = Pt(9)
p2.font.color.rgb = GREEN_DARK

bullets2 = [
    ("Strict Legal Isolation: ", "Enforces clean boundaries between Indian sovereign law (Patents Act, BDA) and international treaties (WIPO, PCT, Nagoya)."),
    ("Formulation vs Extract: ", "Distinguishes classical polyherbal ASU remedies from novel single-herb chemical extractions."),
    ("TKDL Defensive Shield: ", "Strict non-disclosure compliance; safe abstention on confidential Ayurvedic manuscripts.")
]
tf_b2 = add_text_box(slide2, x2 + Inches(0.2), pillar_y + Inches(0.85), pillar_w - Inches(0.4), Inches(1.7))
for i, (b_title, b_desc) in enumerate(bullets2):
    p = tf_b2.paragraphs[0] if i == 0 else tf_b2.add_paragraph()
    if i > 0: p.space_before = Pt(4)
    run1 = p.add_run()
    run1.text = "• " + b_title
    run1.font.bold = True
    run1.font.size = Pt(9.5)
    run1.font.color.rgb = SLATE_DARK
    run2 = p.add_run()
    run2.text = b_desc
    run2.font.size = Pt(9)
    run2.font.color.rgb = SLATE_MUTED

# --- PILLAR 3 ---
x3 = x2 + pillar_w + pillar_gap
add_card(slide2, x3, pillar_y, pillar_w, pillar_h, bg_color=WHITE, border_color=SLATE_BORDER)
slide2.shapes.add_picture(os.path.join(ICONS_DIR, "icon_multilingual.png"), x3 + Inches(0.2), pillar_y + Inches(0.2), Inches(0.55), Inches(0.55))
tf = add_text_box(slide2, x3 + Inches(0.85), pillar_y + Inches(0.2), pillar_w - Inches(1.0), Inches(0.55))
p = tf.paragraphs[0]
p.text = "Provenance & Trilingual Delivery"
p.font.size = Pt(12.5)
p.font.bold = True
p.font.color.rgb = NAVY_DARK
p2 = tf.add_paragraph()
p2.text = "Courtroom-grade audit & Indic equity"
p2.font.size = Pt(9)
p2.font.color.rgb = BLUE_ACCENT

bullets3 = [
    ("Deterministic Citations: ", "Every output includes verifiable enactment dates, section numbers, gazette links, and official URLs."),
    ("Native Trilingual Engine: ", "End-to-end guidance in English, Hindi (Devanagari), and Kannada with preserved statutory clauses."),
    ("Citation Immutability: ", "Legal citations (e.g. Sec 3(p), Sec 6 NBA) remain untranslated and legally pristine across all languages.")
]
tf_b3 = add_text_box(slide2, x3 + Inches(0.2), pillar_y + Inches(0.85), pillar_w - Inches(0.4), Inches(1.7))
for i, (b_title, b_desc) in enumerate(bullets3):
    p = tf_b3.paragraphs[0] if i == 0 else tf_b3.add_paragraph()
    if i > 0: p.space_before = Pt(4)
    run1 = p.add_run()
    run1.text = "• " + b_title
    run1.font.bold = True
    run1.font.size = Pt(9.5)
    run1.font.color.rgb = SLATE_DARK
    run2 = p.add_run()
    run2.text = b_desc
    run2.font.size = Pt(9)
    run2.font.color.rgb = SLATE_MUTED

# Bottom End-to-End Decision Pipeline
pipe_y = Inches(4.85)
pipe_h = Inches(1.15)
add_card(slide2, Inches(0.4), pipe_y, Inches(12.53), pipe_h, bg_color=WHITE, border_color=SLATE_BORDER)

steps = [
    ("1. USER QUERY", "Natural language input\n(EN / HI / KN)", GREEN_DARK),
    ("2. INTENT & JURISDICTION", "Classifies ASU vs Novel,\nIndia vs International", NAVY_MED),
    ("3. DUAL RETRIEVAL", "FAISS Vector Search +\nSQLite Relational WAL", BLUE_ACCENT),
    ("4. EPISTEMIC VALIDATOR", "Cross-checks statutes;\nRejects unanchored claims", AMBER),
    ("5. AUDIT-LOCKED OUTPUT", "Grounded answer with\nverifiable gazette links", GREEN_DARK)
]
step_w = Inches(2.3)
step_gap = Inches(0.18)
start_x = Inches(0.55)

for idx, (stitle, ssub, scolor) in enumerate(steps):
    sx = start_x + idx * (step_w + step_gap)
    add_card(slide2, sx, pipe_y + Inches(0.12), step_w, Inches(0.9), bg_color=BG_CARD, border_color=SLATE_BORDER)
    add_badge(slide2, sx, pipe_y + Inches(0.12), step_w, Inches(0.28), stitle, scolor, WHITE, font_size=Pt(8.5))
    tf_s = add_text_box(slide2, sx + Inches(0.08), pipe_y + Inches(0.42), step_w - Inches(0.16), Inches(0.55))
    p = tf_s.paragraphs[0]
    p.text = ssub
    p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(8.5)
    p.font.color.rgb = SLATE_DARK
    
    if idx < 4:
        arrow_x = sx + step_w + Inches(0.03)
        tf_a = add_text_box(slide2, arrow_x, pipe_y + Inches(0.38), step_gap - Inches(0.06), Inches(0.3))
        p = tf_a.paragraphs[0]
        p.text = "➔"
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = SLATE_MUTED

# Bottom Verification Badge
add_card(slide2, Inches(0.4), Inches(6.05), Inches(12.53), Inches(0.28), bg_color=GREEN_DARK, border_color=None)
tf_trust = add_text_box(slide2, Inches(0.5), Inches(6.06), Inches(12.33), Inches(0.25))
p = tf_trust.paragraphs[0]
p.text = "VERIFIED CAPABILITY: 98/98 automated tests passing  |  Runs on standard laptop CPU (<1.2s latency)  |  Zero cloud dependency"
p.alignment = PP_ALIGN.CENTER
p.font.size = Pt(9)
p.font.bold = True
p.font.color.rgb = WHITE

# ==============================================================================
# SLIDE 3: TECHNICAL APPROACH & ARCHITECTURE
# ==============================================================================
print("Redesigning Slide 3...")
slide3 = prs.slides[2]
clear_interior_shapes(slide3, {'Rectangle 9', 'Slide Number Placeholder 5', 'Footer Placeholder 6', 'Title 1', 'Oval 4', 'Picture 11'})

for s in slide3.shapes:
    if s.name == 'Title 1':
        s.text_frame.text = "TECHNICAL APPROACH & ARCHITECTURE"
        p = s.text_frame.paragraphs[0]
        p.font.name = "Segoe UI"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = NAVY_DARK

# Left Side (55%): 4-Tier Software Architecture Diagram
arch_w = Inches(6.9)
arch_x = Inches(0.4)
arch_y = Inches(1.1)
arch_h = Inches(5.15)
add_card(slide3, arch_x, arch_y, arch_w, arch_h, bg_color=WHITE, border_color=SLATE_BORDER)

tf = add_text_box(slide3, arch_x + Inches(0.3), arch_y + Inches(0.15), arch_w - Inches(0.6), Inches(0.4))
p = tf.paragraphs[0]
p.text = "End-to-End Grounded AI Architecture"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = NAVY_DARK

layers = [
    ("LAYER 1: PRESENTATION & USER EXPERIENCE", 
     "Streamlit Web Application  •  Custom High-Contrast CSS  •  Responsive Viewport",
     "Trilingual Query Input (EN/HI/KN)  |  Citation Inspector Drawer  |  Statutory Card Badges",
     GREEN_LIGHT, GREEN_DARK),
    
    ("LAYER 2: REST API & EPISTEMIC REASONING", 
     "FastAPI Core Service  •  Pydantic V2 Models  •  Strict Boundary Enforcement",
     "Query Intent Classifier  |  Formulation vs Extract Router  |  Epistemic Legal Reasoner",
     BLUE_LIGHT, BLUE_ACCENT),
    
    ("LAYER 3: DUAL RETRIEVAL & INDEXING ENGINE", 
     "Dense Vector Store + Relational Storage  •  SHA-256 Checksum Validation",
     "FAISS Index (all-MiniLM-L6-v2 Embeddings)  |  SQLite (WAL Mode)  |  Canonical Section Anchors",
     AMBER_LIGHT, AMBER),
    
    ("LAYER 4: AUTHORITATIVE STATUTORY CORPUS & GUARDRAILS", 
     "Indian Sovereign Law & Traditional Knowledge  •  Zero Phantom Hallucinations",
     "The Patents Act 1970 (Sec 3(p))  |  Biological Diversity Act 2002/23  |  D&C Act 1940  |  TKDL Shield",
     BG_HERO, NAVY_DARK)
]

layer_y = arch_y + Inches(0.6)
layer_h = Inches(0.95)
layer_gap = Inches(0.18)

for l_idx, (ltitle, lsub, ldesc, lbg, lcol) in enumerate(layers):
    ly = layer_y + l_idx * (layer_h + layer_gap)
    add_card(slide3, arch_x + Inches(0.25), ly, arch_w - Inches(0.5), layer_h, bg_color=lbg, border_color=lcol, border_width=Pt(1.2))
    
    tf_l = add_text_box(slide3, arch_x + Inches(0.4), ly + Inches(0.08), arch_w - Inches(0.8), Inches(0.8))
    p1 = tf_l.paragraphs[0]
    p1.text = ltitle
    p1.font.size = Pt(9.5)
    p1.font.bold = True
    p1.font.color.rgb = lcol
    
    p2 = tf_l.add_paragraph()
    p2.text = lsub
    p2.font.size = Pt(8.5)
    p2.font.bold = True
    p2.font.color.rgb = SLATE_DARK
    
    p3 = tf_l.add_paragraph()
    p3.text = ldesc
    p3.font.size = Pt(8)
    p3.font.color.rgb = SLATE_MUTED

# Right Side (45%): Tech Stack Cards + Empirical Benchmarks
right_x = Inches(7.5)
right_w = Inches(5.43)

# Top Right: Technology Stack
add_card(slide3, right_x, arch_y, right_w, Inches(2.55), bg_color=WHITE, border_color=SLATE_BORDER)
tf = add_text_box(slide3, right_x + Inches(0.25), arch_y + Inches(0.12), right_w - Inches(0.5), Inches(0.35))
p = tf.paragraphs[0]
p.text = "Core Technology Stack"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = NAVY_DARK

tech_cards = [
    ("FRONTEND & APP SHELL", "Streamlit, Python 3.11, Custom CSS", "Responsive design, multi-tab drawer, instant Indic font rendering (Nirmala UI)."),
    ("BACKEND & REASONING", "FastAPI, Pydantic V2, Uvicorn", "Modular microservice, schema validation, deterministic fallback logic."),
    ("VECTOR & STORAGE", "FAISS CPU, SQLite WAL, SHA-256", "Sub-second dense vector indexing, ACID-compliant relational provenance logging."),
    ("LOCAL AI & INDIC NLP", "Sentence-Transformers, all-MiniLM", "Lightweight 384-d semantic embedding models running 100% on commodity CPU.")
]

tcard_y = arch_y + Inches(0.48)
tcard_h = Inches(0.45)
for t_idx, (ttitle, ttech, tdesc) in enumerate(tech_cards):
    ty = tcard_y + t_idx * Inches(0.5)
    add_card(slide3, right_x + Inches(0.2), ty, right_w - Inches(0.4), tcard_h, bg_color=BG_CARD, border_color=SLATE_BORDER)
    tf_t = add_text_box(slide3, right_x + Inches(0.3), ty + Inches(0.04), right_w - Inches(0.6), Inches(0.4))
    p = tf_t.paragraphs[0]
    run1 = p.add_run()
    run1.text = ttitle + ": "
    run1.font.bold = True
    run1.font.size = Pt(8.5)
    run1.font.color.rgb = NAVY_MED
    run2 = p.add_run()
    run2.text = ttech
    run2.font.bold = True
    run2.font.size = Pt(8.5)
    run2.font.color.rgb = GREEN_DARK
    
    p2 = tf_t.add_paragraph()
    p2.text = tdesc
    p2.font.size = Pt(7.5)
    p2.font.color.rgb = SLATE_MUTED

# Bottom Right: Empirical Benchmarks & QR Codes
bench_y = arch_y + Inches(2.7)
bench_h = Inches(2.45)
add_card(slide3, right_x, bench_y, right_w, bench_h, bg_color=WHITE, border_color=SLATE_BORDER)

tf = add_text_box(slide3, right_x + Inches(0.25), bench_y + Inches(0.12), right_w - Inches(0.5), Inches(0.35))
p = tf.paragraphs[0]
p.text = "Empirical Validation & Reproducibility"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = NAVY_DARK

# 3 Metric Cards
m_w = Inches(1.58)
m_gap = Inches(0.12)
m_y = bench_y + Inches(0.48)
metrics = [
    ("< 1.2s", "Retrieval Latency", "Per complex query on standard local CPU"),
    ("650 MB", "RAM Footprint", "Ultra-lean, runs on basic laptops without GPU"),
    ("98 / 98", "Automated Tests", "100% test pass rate across all legal rules")
]
for idx, (mval, mlabel, msub) in enumerate(metrics):
    mx = right_x + Inches(0.2) + idx * (m_w + m_gap)
    add_card(slide3, mx, m_y, m_w, Inches(0.85), bg_color=BG_HERO, border_color=SLATE_BORDER)
    tf_m = add_text_box(slide3, mx, m_y + Inches(0.06), m_w, Inches(0.75))
    p1 = tf_m.paragraphs[0]
    p1.text = mval
    p1.alignment = PP_ALIGN.CENTER
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = GREEN_DARK
    p2 = tf_m.add_paragraph()
    p2.text = mlabel
    p2.alignment = PP_ALIGN.CENTER
    p2.font.size = Pt(8)
    p2.font.bold = True
    p2.font.color.rgb = NAVY_DARK
    p3 = tf_m.add_paragraph()
    p3.text = msub
    p3.alignment = PP_ALIGN.CENTER
    p3.font.size = Pt(6.5)
    p3.font.color.rgb = SLATE_MUTED

# QR Codes
qr_y = bench_y + Inches(1.45)
qr_path1 = os.path.join(QR_DIR, "qr_github.png")
qr_path2 = os.path.join(QR_DIR, "qr_report.png")
if os.path.exists(qr_path1):
    slide3.shapes.add_picture(qr_path1, right_x + Inches(0.4), qr_y, Inches(0.82), Inches(0.82))
    tf_qr1 = add_text_box(slide3, right_x + Inches(1.3), qr_y + Inches(0.12), Inches(1.8), Inches(0.6))
    p = tf_qr1.paragraphs[0]
    p.text = "GitHub Repository"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p2 = tf_qr1.add_paragraph()
    p2.text = "Source Code & Tests"
    p2.font.size = Pt(8)
    p2.font.color.rgb = BLUE_ACCENT

if os.path.exists(qr_path2):
    slide3.shapes.add_picture(qr_path2, right_x + Inches(3.1), qr_y, Inches(0.82), Inches(0.82))
    tf_qr2 = add_text_box(slide3, right_x + Inches(4.0), qr_y + Inches(0.12), Inches(1.3), Inches(0.6))
    p = tf_qr2.paragraphs[0]
    p.text = "Technical Report"
    p.font.size = Pt(9)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    p2 = tf_qr2.add_paragraph()
    p2.text = "Documentation"
    p2.font.size = Pt(8)
    p2.font.color.rgb = GREEN_DARK

# ==============================================================================
# SLIDE 4: FEASIBILITY AND VIABILITY (Restructured: 3 Feasibility Cards + Prototype UI Snapshot + Roadmap)
# ==============================================================================
print("Redesigning Slide 4...")
slide4 = prs.slides[3]
clear_interior_shapes(slide4, {'Rectangle 9', 'Slide Number Placeholder 5', 'Footer Placeholder 6', 'Title 1', 'Oval 2', 'Picture 10'})

for s in slide4.shapes:
    if s.name == 'Title 1':
        s.text_frame.text = "FEASIBILITY, VIABILITY & ROADMAP"
        p = s.text_frame.paragraphs[0]
        p.font.name = "Segoe UI"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = NAVY_DARK

# 1. Top Section: 3 Feasibility Cards
top_y = Inches(1.05)
top_h = Inches(1.6)
top_w = Inches(4.04)
top_gap = Inches(0.2)

feasibility_cards = [
    ("Technical Feasibility", "icon_cpu.png", GREEN_DARK, [
        ("Commodity CPU Inference: ", "Runs completely locally on standard i5/Ryzen laptops without discrete GPUs."),
        ("Sub-1.2s Latency: ", "Optimized FAISS vector index provides instant query triage and citation lookup."),
        ("Offline Independence: ", "Operates with zero cloud connectivity; immune to internet outages.")
    ]),
    ("Operational & Market Viability", "icon_leaf.png", AMBER, [
        ("Zero Recurring API Costs: ", "Eliminates high per-token proprietary LLM API costs for cash-constrained MSMEs."),
        ("Designed for Ayush Domain: ", "Custom workflows built specifically for Vaidyas, patent attorneys, and researchers."),
        ("Non-Technical Interface: ", "Intuitive web application with zero command-line or coding knowledge required.")
    ]),
    ("Regulatory & Sovereign Feasibility", "icon_shield.png", BLUE_ACCENT, [
        ("CSIR-TKDL Confidentiality: ", "Strict adherence to traditional knowledge non-disclosure agreements."),
        ("Indian Data Sovereignty: ", "Sensitive Ayurvedic formulas and patents never leave institutional boundaries."),
        ("100% Deterministic Evidence: ", "Every claim backed by official Gazette enactment dates and section anchors.")
    ])
]

for idx, (ftitle, ficon, fcol, fbullets) in enumerate(feasibility_cards):
    fx = Inches(0.4) + idx * (top_w + top_gap)
    add_card(slide4, fx, top_y, top_w, top_h, bg_color=WHITE, border_color=SLATE_BORDER)
    slide4.shapes.add_picture(os.path.join(ICONS_DIR, ficon), fx + Inches(0.18), top_y + Inches(0.15), Inches(0.45), Inches(0.45))
    tf = add_text_box(slide4, fx + Inches(0.72), top_y + Inches(0.15), top_w - Inches(0.85), Inches(0.4))
    p = tf.paragraphs[0]
    p.text = ftitle
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = fcol
    
    tf_b = add_text_box(slide4, fx + Inches(0.18), top_y + Inches(0.58), top_w - Inches(0.36), Inches(0.95))
    for b_idx, (b_title, b_desc) in enumerate(fbullets):
        p = tf_b.paragraphs[0] if b_idx == 0 else tf_b.add_paragraph()
        if b_idx > 0: p.space_before = Pt(2)
        run1 = p.add_run()
        run1.text = "• " + b_title
        run1.font.bold = True
        run1.font.size = Pt(8.5)
        run1.font.color.rgb = SLATE_DARK
        run2 = p.add_run()
        run2.text = b_desc
        run2.font.size = Pt(8)
        run2.font.color.rgb = SLATE_MUTED

# 2. Middle Section: Live Working Prototype Snapshot & Validation Scorecard
mid_y = Inches(2.8)
mid_h = Inches(1.8)

# Left: Prototype Snapshot
proto_w = Inches(5.8)
add_card(slide4, Inches(0.4), mid_y, proto_w, mid_h, bg_color=WHITE, border_color=SLATE_BORDER)
if os.path.exists(UI_PATH):
    slide4.shapes.add_picture(UI_PATH, Inches(0.55), mid_y + Inches(0.15), Inches(2.35), Inches(1.5))

tf_p = add_text_box(slide4, Inches(3.05), mid_y + Inches(0.15), Inches(3.0), Inches(1.5))
p = tf_p.paragraphs[0]
p.text = "Validated Working Prototype"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = NAVY_DARK

features = [
    "Full-featured Streamlit user interface",
    "Section 3(p) prior art triage & evaluation",
    "Interactive primary legal source citations",
    "Instant English, Hindi, and Kannada answers"
]
for f in features:
    p = tf_p.add_paragraph()
    p.text = "✓ " + f
    p.font.size = Pt(8.5)
    p.font.color.rgb = GREEN_DARK

# Right: Empirical Validation Metrics
eval_x = Inches(6.4)
eval_w = Inches(6.53)
add_card(slide4, eval_x, mid_y, eval_w, mid_h, bg_color=BG_HERO, border_color=SLATE_BORDER)

tf_e = add_text_box(slide4, eval_x + Inches(0.3), mid_y + Inches(0.15), eval_w - Inches(0.6), Inches(0.35))
p = tf_e.paragraphs[0]
p.text = "Empirical Validation Highlights"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = NAVY_DARK

v_metrics = [
    ("7 Primary Statutes", "Patents Act 1970, Biodiversity Act 2002/23, D&C Act 1940, WIPO, Nagoya, PCIM&H, TKDL."),
    ("98 / 98 Automated Tests", "100% deterministic test pass rate across jurisdiction routing, citation extraction, and Indic translation."),
    ("< 1.2s Local CPU Speed", "Average response latency measured on standard non-GPU commodity hardware over 250 test queries.")
]
tf_vb = add_text_box(slide4, eval_x + Inches(0.3), mid_y + Inches(0.5), eval_w - Inches(0.6), Inches(1.2))
for idx, (m_head, m_body) in enumerate(v_metrics):
    p = tf_vb.paragraphs[0] if idx == 0 else tf_vb.add_paragraph()
    if idx > 0: p.space_before = Pt(3)
    run1 = p.add_run()
    run1.text = "• " + m_head + ": "
    run1.font.bold = True
    run1.font.size = Pt(9)
    run1.font.color.rgb = NAVY_MED
    run2 = p.add_run()
    run2.text = m_body
    run2.font.size = Pt(8.5)
    run2.font.color.rgb = SLATE_MUTED

# 3. Bottom Section: Scalability Roadmap
road_y = Inches(4.75)
road_h = Inches(1.5)
road_w = Inches(12.53)
add_card(slide4, Inches(0.4), road_y, road_w, road_h, bg_color=WHITE, border_color=SLATE_BORDER)

tf = add_text_box(slide4, Inches(0.6), road_y + Inches(0.1), Inches(12.0), Inches(0.3))
p = tf.paragraphs[0]
p.text = "Scalability & Deployment Roadmap"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = NAVY_DARK

phases = [
    ("PHASE 1: WORKING PROTOTYPE (CURRENT)", "SIH 2026 Milestone", 
     "• Validated FastAPI backend & Streamlit UI\n• 7 primary statutory corpuses indexed\n• Sub-1.2s local retrieval & 98/98 tests passing\n• Native Trilingual UI (English, Hindi, Kannada)", GREEN_DARK, GREEN_LIGHT),
    
    ("PHASE 2: INSTITUTIONAL PILOT", "Q3 - Q4 2026", 
     "• Deployment across 5 Ayush research universities\n• Formal feedback with registered patent attorneys\n• State Biodiversity Board ABS fee calculator\n• Accuracy & latency stress-testing at scale", NAVY_MED, BLUE_LIGHT),
    
    ("PHASE 3: NATIONAL SCALE & EXPANSION", "2027 & Beyond", 
     "• Direct integration with National Ayush Mission\n• Automated IPO weekly gazette synchronization\n• Quantized edge SLMs (4-bit Qwen on-device)\n• Expansion to Tamil, Telugu, and Marathi", AMBER, AMBER_LIGHT)
]

phase_w = Inches(3.85)
phase_gap = Inches(0.24)
for p_idx, (p_title, p_time, p_desc, p_col, p_bg) in enumerate(phases):
    px = Inches(0.65) + p_idx * (phase_w + phase_gap)
    py = road_y + Inches(0.38)
    add_card(slide4, px, py, phase_w, Inches(1.02), bg_color=p_bg, border_color=p_col, border_width=Pt(1.2))
    
    tf_phase = add_text_box(slide4, px + Inches(0.12), py + Inches(0.06), phase_w - Inches(0.24), Inches(0.92))
    p1 = tf_phase.paragraphs[0]
    p1.text = p_title
    p1.font.size = Pt(8.5)
    p1.font.bold = True
    p1.font.color.rgb = p_col
    
    p2 = tf_phase.add_paragraph()
    p2.text = p_time
    p2.font.size = Pt(7.5)
    p2.font.bold = True
    p2.font.color.rgb = SLATE_DARK
    
    p3 = tf_phase.add_paragraph()
    p3.text = p_desc
    p3.font.size = Pt(7.5)
    p3.font.color.rgb = SLATE_MUTED

# ==============================================================================
# SLIDE 5: IMPACT AND BENEFITS
# ==============================================================================
print("Redesigning Slide 5...")
slide5 = prs.slides[4]
clear_interior_shapes(slide5, {'Rectangle 9', 'Slide Number Placeholder 5', 'Footer Placeholder 6', 'Title 1', 'Oval 2', 'Picture 10'})

for s in slide5.shapes:
    if s.name == 'Title 1':
        s.text_frame.text = "IMPACT, BENEFITS & STAKEHOLDERS"
        p = s.text_frame.paragraphs[0]
        p.font.name = "Segoe UI"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = NAVY_DARK

# Top Section: 3 Impact Pillars
impact_y = Inches(1.05)
impact_h = Inches(1.95)
impact_w = Inches(4.04)
impact_gap = Inches(0.2)

impact_cards = [
    ("Bio-Piracy Defense & Sovereignty", 
     os.path.join(BRAIN_DIR, "bio_piracy_shield_1790786174590.jpg"),
     "Shields Indian traditional knowledge from wrongful international patenting by equipping patent agents with instant prior art and Section 3(p) defense."),
    
    ("Accelerated Ayush R&D", 
     os.path.join(BRAIN_DIR, "ayush_rd_lab_1790786214487.jpg"),
     "Slashes prior art and regulatory clearance search time from 2–3 weeks to under 2 seconds, accelerating Ayurvedic drug discovery and IP filing."),
    
    ("Grassroots Language Equity", 
     os.path.join(BRAIN_DIR, "auditable_legal_trust_1790786313373.jpg"),
     "Democratizes complex intellectual property frameworks for traditional healers, farmers, and MSMEs through native Hindi and Kannada guidance.")
]

for idx, (ititle, iphoto, idesc) in enumerate(impact_cards):
    ix = Inches(0.4) + idx * (impact_w + impact_gap)
    add_card(slide5, ix, impact_y, impact_w, impact_h, bg_color=WHITE, border_color=SLATE_BORDER)
    if os.path.exists(iphoto):
        slide5.shapes.add_picture(iphoto, ix + Inches(0.15), impact_y + Inches(0.15), Inches(1.3), Inches(1.0))
    
    tf = add_text_box(slide5, ix + Inches(1.55), impact_y + Inches(0.15), impact_w - Inches(1.7), Inches(1.0))
    p1 = tf.paragraphs[0]
    p1.text = ititle
    p1.font.size = Pt(11)
    p1.font.bold = True
    p1.font.color.rgb = NAVY_DARK
    
    tf_desc = add_text_box(slide5, ix + Inches(0.15), impact_y + Inches(1.22), impact_w - Inches(0.3), Inches(0.65))
    p = tf_desc.paragraphs[0]
    p.text = idesc
    p.font.size = Pt(8.5)
    p.font.color.rgb = SLATE_MUTED

# Middle Section: 4 Stakeholder Beneficiaries
stake_y = Inches(3.15)
stake_h = Inches(2.05)
stake_w = Inches(3.0)
stake_gap = Inches(0.17)

stakeholders = [
    ("Ayush Researchers", 
     os.path.join(BRAIN_DIR, "ayush_researcher_portrait_1790786385872.jpg"),
     "Evaluate Novelty Instantly",
     "Screen novel botanical compounds against Section 3(p) exclusions and scientific literature before investing in clinical trials."),
    
    ("Patent Attorneys", 
     os.path.join(BRAIN_DIR, "patent_attorney_portrait_1790786426288.jpg"),
     "Courtroom-Grade Citations",
     "Rapid prior-art discovery, statutory defense drafting, and compliance verification across international patent treaties."),
    
    ("Herbal MSMEs", 
     os.path.join(BRAIN_DIR, "herbal_msme_portrait_1790786471782.jpg"),
     "Streamlined ASU Compliance",
     "Clear guidance on Drugs & Cosmetics Act licensing, Ayurvedic Pharmacopoeia standards, and State Biodiversity Board approvals."),
    
    ("Traditional Healers", 
     os.path.join(ASSETS_DIR, "new_slide_assets", "healer_square.jpg"),
     "Community IP Protection",
     "Native-language access in Hindi & Kannada protects local agricultural biodiversity and community intellectual property rights.")
]

for idx, (sname, sphoto, sval, sdesc) in enumerate(stakeholders):
    sx = Inches(0.4) + idx * (stake_w + stake_gap)
    add_card(slide5, sx, stake_y, stake_w, stake_h, bg_color=WHITE, border_color=SLATE_BORDER)
    if os.path.exists(sphoto):
        slide5.shapes.add_picture(sphoto, sx + Inches(0.15), stake_y + Inches(0.15), Inches(0.9), Inches(0.9))
    
    tf = add_text_box(slide5, sx + Inches(1.15), stake_y + Inches(0.15), stake_w - Inches(1.25), Inches(0.9))
    p1 = tf.paragraphs[0]
    p1.text = sname
    p1.font.size = Pt(10.5)
    p1.font.bold = True
    p1.font.color.rgb = NAVY_DARK
    
    p2 = tf.add_paragraph()
    p2.text = sval
    p2.font.size = Pt(8.5)
    p2.font.bold = True
    p2.font.color.rgb = GREEN_DARK
    
    tf_d = add_text_box(slide5, sx + Inches(0.15), stake_y + Inches(1.12), stake_w - Inches(0.3), Inches(0.85))
    p = tf_d.paragraphs[0]
    p.text = sdesc
    p.font.size = Pt(8)
    p.font.color.rgb = SLATE_MUTED

# Bottom Section: 5 Strategic Advantages
adv_y = Inches(5.35)
adv_h = Inches(0.85)
add_card(slide5, Inches(0.4), adv_y, Inches(12.53), adv_h, bg_color=BG_HERO, border_color=SLATE_BORDER)

advantages = [
    ("100% Offline-Capable", "Zero reliance on external cloud servers"),
    ("Zero Recurring GPU Cost", "Runs on standard commodity laptop CPU"),
    ("Deterministic Citations", "Directly anchored to official Gazettes"),
    ("Cross-Statute Synthesis", "Harmonizes Patents Act, BDA & D&C Act"),
    ("Trilingual Equity", "Native English, Hindi, and Kannada answers")
]

adv_w = Inches(2.35)
adv_gap = Inches(0.15)
for idx, (ahead, asub) in enumerate(advantages):
    ax = Inches(0.55) + idx * (adv_w + adv_gap)
    tf_a = add_text_box(slide5, ax, adv_y + Inches(0.12), adv_w, Inches(0.65))
    p1 = tf_a.paragraphs[0]
    p1.text = "✓ " + ahead
    p1.font.size = Pt(9.5)
    p1.font.bold = True
    p1.font.color.rgb = NAVY_DARK
    p2 = tf_a.add_paragraph()
    p2.text = asub
    p2.font.size = Pt(8)
    p2.font.color.rgb = SLATE_MUTED

# ==============================================================================
# SLIDE 6: RESEARCH, REFERENCES & PROTOTYPE
# ==============================================================================
print("Redesigning Slide 6...")
slide6 = prs.slides[5]
clear_interior_shapes(slide6, {'Rectangle 9', 'Slide Number Placeholder 5', 'Footer Placeholder 6', 'Title 1', 'Oval 2', 'Picture 11'})

for s in slide6.shapes:
    if s.name == 'Title 1':
        s.text_frame.text = "RESEARCH, REFERENCES & PROTOTYPE"
        p = s.text_frame.paragraphs[0]
        p.font.name = "Segoe UI"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = NAVY_DARK

# Left Side (52%): Authoritative Domain Frameworks
left_w = Inches(6.5)
left_x = Inches(0.4)
ref_y = Inches(1.1)

ref_sections = [
    ("1. Indian Sovereign Statutes & Regulatory Authorities", [
        ("The Patents Act, 1970 (Sec 3(p) & 10)", "ipindia.gov.in", "qr_ipindia.png"),
        ("The Biological Diversity Act, 2002 & 2023", "nbaindia.org", "qr_nba.png"),
        ("Drugs & Cosmetics Act, 1940 (ASU Rules)", "ayush.gov.in", "qr_ayush.png")
    ]),
    ("2. Multilateral Treaties & Traditional Knowledge", [
        ("WIPO GRATK Treaty (2024 Mandatory Disclosure)", "wipo.int", "qr_wipo.png"),
        ("Nagoya Protocol on Access & Benefit-Sharing", "cbd.int", "qr_nagoya.png"),
        ("PCIM&H Standards & CSIR-TKDL Guidelines", "pcimh.gov.in", "qr_pcimh.png")
    ]),
    ("3. Open-Source AI Stack & Project Repository", [
        ("FAISS Dense Vector Index & Sentence-Transformers", "huggingface.co", "qr_hf.png"),
        ("IP-SAKTI Sahayak GitHub Repository", "github.com/Rengoku9000/Drugvista", "qr_github.png")
    ])
]

curr_y = ref_y
for s_title, s_items in ref_sections:
    card_h = Inches(0.4) + len(s_items) * Inches(0.48)
    add_card(slide6, left_x, curr_y, left_w, card_h, bg_color=WHITE, border_color=SLATE_BORDER)
    
    tf = add_text_box(slide6, left_x + Inches(0.2), curr_y + Inches(0.08), left_w - Inches(0.4), Inches(0.3))
    p = tf.paragraphs[0]
    p.text = s_title
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = NAVY_DARK
    
    item_y = curr_y + Inches(0.38)
    for iname, iurl, iqr in s_items:
        qr_p = os.path.join(QR_DIR, iqr)
        if os.path.exists(qr_p):
            slide6.shapes.add_picture(qr_p, left_x + Inches(0.2), item_y, Inches(0.38), Inches(0.38))
        
        tf_item = add_text_box(slide6, left_x + Inches(0.68), item_y, left_w - Inches(0.8), Inches(0.38))
        p = tf_item.paragraphs[0]
        run1 = p.add_run()
        run1.text = iname + " — "
        run1.font.bold = True
        run1.font.size = Pt(8.5)
        run1.font.color.rgb = SLATE_DARK
        run2 = p.add_run()
        run2.text = iurl
        run2.font.size = Pt(8)
        run2.font.color.rgb = BLUE_ACCENT
        
        item_y += Inches(0.46)
        
    curr_y += card_h + Inches(0.12)

# Right Side (48%): Live Working Prototype Showcase
right_x = Inches(7.1)
right_w = Inches(5.83)
add_card(slide6, right_x, ref_y, right_w, Inches(5.1), bg_color=WHITE, border_color=SLATE_BORDER)

tf_rt = add_text_box(slide6, right_x + Inches(0.25), ref_y + Inches(0.12), right_w - Inches(0.5), Inches(0.35))
p = tf_rt.paragraphs[0]
p.text = "Working Prototype UI — Live Verification"
p.font.size = Pt(13)
p.font.bold = True
p.font.color.rgb = NAVY_DARK

if os.path.exists(UI_PATH):
    slide6.shapes.add_picture(UI_PATH, right_x + Inches(0.25), ref_y + Inches(0.48), Inches(5.33), Inches(3.3))

spec_y = ref_y + Inches(3.88)
add_card(slide6, right_x + Inches(0.25), spec_y, Inches(5.33), Inches(1.12), bg_color=BG_HERO, border_color=SLATE_BORDER)

tf_spec = add_text_box(slide6, right_x + Inches(0.4), spec_y + Inches(0.08), Inches(5.03), Inches(0.95))
p = tf_spec.paragraphs[0]
p.text = "Prototype Specifications & Operational Guarantees:"
p.font.size = Pt(9.5)
p.font.bold = True
p.font.color.rgb = NAVY_DARK

specs = [
    "• Streamlit reactive frontend with instant trilingual tab switching",
    "• Deterministic citation drawer linking directly to Gazette enactments",
    "• Sub-1.2 second response latency on local commodity CPU (Zero GPU needed)",
    "• 98/98 unit and regression tests passing with full test automation"
]
for s in specs:
    p = tf_spec.add_paragraph()
    p.text = s
    p.font.size = Pt(8)
    p.font.color.rgb = SLATE_MUTED

# Save presentation
prs.save(DST_PPT)
print(f"Redesigned presentation successfully saved to: {DST_PPT}")
