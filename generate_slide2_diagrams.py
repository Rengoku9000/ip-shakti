import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_SEMIBOLD = r"C:\Windows\Fonts\segoeuisl.ttf"

def get_fonts(title_sz=36, text_sz=26, small_sz=20):
    return (
        ImageFont.truetype(FONT_BOLD, title_sz),
        ImageFont.truetype(FONT_BOLD, text_sz),
        ImageFont.truetype(FONT_REG, text_sz),
        ImageFont.truetype(FONT_REG, small_sz),
        ImageFont.truetype(FONT_BOLD, small_sz)
    )

def draw_rounded_card(d, xy, fill, outline=None, width=1, radius=18):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

# =============================================================================
# DIAGRAM 1: Deterministic Knowledge Pipeline
# =============================================================================
def make_diagram_1(out_path):
    im = Image.new("RGBA", (W, H), (247, 248, 245, 255))
    d = ImageDraw.Draw(im)
    f_title, f_h1, f_body, f_small, f_bsmall = get_fonts(38, 26, 21)

    # Outer container border
    draw_rounded_card(d, [15, 15, W-15, H-15], fill=(255, 255, 255), outline=(220, 229, 222), width=3, radius=24)

    # Top Header Banner
    draw_rounded_card(d, [40, 35, W-40, 115], fill=(234, 244, 238), outline=(18, 107, 69), width=2, radius=16)
    d.text((W//2, 75), "CANONICAL STATUTORY INGESTION", fill=(11, 79, 52), font=f_h1, anchor="mm")

    # 3 Statute Cards
    statutes = [
        ("The Patents Act, 1970", "Sec 3(p) TK Exclusions", (15, 77, 50)),
        ("Biodiversity Act 2002", "Sec 6 NBA Prior Approval", (18, 107, 69)),
        ("D&C Act, 1940 (ASU)", "Schedule 1 Formularies", (37, 99, 166))
    ]
    card_w = 460
    card_h = 160
    y_cards = 150
    for i, (title, sub, col) in enumerate(statutes):
        x = 60 + i * (card_w + 50)
        draw_rounded_card(d, [x, y_cards, x + card_w, y_cards + card_h], fill=(250, 252, 251), outline=col, width=3, radius=14)
        draw_rounded_card(d, [x + 20, y_cards + 15, x + card_w - 20, y_cards + 65], fill=col, radius=8)
        d.text((x + card_w//2, y_cards + 40), title, fill=(255, 255, 255), font=f_bsmall, anchor="mm")
        d.text((x + card_w//2, y_cards + 105), sub, fill=(23, 33, 27), font=f_body, anchor="mm")
        d.text((x + card_w//2, y_cards + 135), "Official Gazette Authority", fill=(82, 96, 87), font=f_small, anchor="mm")

    # Downward connecting flow
    d.line([(W//2, 320), (W//2, 380)], fill=(18, 107, 69), width=4)
    d.polygon([(W//2 - 12, 375), (W//2 + 12, 375), (W//2, 395)], fill=(18, 107, 69))

    # Middle Processing Box: Cryptographic Verification
    draw_rounded_card(d, [120, 400, W-120, 560], fill=(240, 245, 241), outline=(18, 107, 69), width=2, radius=16)
    d.text((W//2, 440), "Cryptographic Structure & Anchor Verification", fill=(11, 79, 52), font=f_h1, anchor="mm")
    d.text((W//2, 490), "SHA-256 Checksums • Clause Boundary Enforcement • Section Anchoring", fill=(82, 96, 87), font=f_body, anchor="mm")
    d.text((W//2, 530), "Guarantees zero phantom statutes or fabricated case law", fill=(18, 107, 69), font=f_bsmall, anchor="mm")

    # Downward connecting flow
    d.line([(W//2, 565), (W//2, 620)], fill=(18, 107, 69), width=4)
    d.polygon([(W//2 - 12, 615), (W//2 + 12, 615), (W//2, 635)], fill=(18, 107, 69))

    # Bottom Two Result Boxes: Local Grounded Store vs Cloud Rejection
    # Left box: Verified Local Store
    draw_rounded_card(d, [60, 645, W//2 - 25, 845], fill=(234, 244, 238), outline=(18, 107, 69), width=3, radius=16)
    d.text((60 + (W//2 - 25 - 60)//2, 695), "[OK] DETERMINISTIC LOCAL KNOWLEDGE", fill=(11, 79, 52), font=f_h1, anchor="mm")
    d.text((60 + (W//2 - 25 - 60)//2, 755), "FAISS Vector Index + SQLite Relational Store", fill=(23, 33, 27), font=f_body, anchor="mm")
    d.text((60 + (W//2 - 25 - 60)//2, 805), "Deterministic retrieval verified against Gazette text", fill=(82, 96, 87), font=f_small, anchor="mm")

    # Right box: Cloud Strikethrough
    draw_rounded_card(d, [W//2 + 25, 645, W - 60, 845], fill=(253, 242, 242), outline=(180, 35, 24), width=3, radius=16)
    d.text((W//2 + 25 + (W - 60 - (W//2 + 25))//2, 695), "[X] NO CLOUD HALLUCINATION", fill=(180, 35, 24), font=f_h1, anchor="mm")
    d.text((W//2 + 25 + (W - 60 - (W//2 + 25))//2, 755), "Zero external LLM API dependency for legal facts", fill=(23, 33, 27), font=f_body, anchor="mm")
    d.text((W//2 + 25 + (W - 60 - (W//2 + 25))//2, 805), "Mathematical rejection of unanchored answers", fill=(82, 96, 87), font=f_small, anchor="mm")

    im.convert("RGB").save(out_path, quality=95)
    print("Saved Diagram 1 to", out_path)

# =============================================================================
# DIAGRAM 2: Dual-Jurisdiction Isolation
# =============================================================================
def make_diagram_2(out_path):
    im = Image.new("RGBA", (W, H), (247, 248, 245, 255))
    d = ImageDraw.Draw(im)
    f_title, f_h1, f_body, f_small, f_bsmall = get_fonts(38, 26, 21)

    draw_rounded_card(d, [15, 15, W-15, H-15], fill=(255, 255, 255), outline=(220, 229, 222), width=3, radius=24)

    # Top Header Banner
    draw_rounded_card(d, [40, 35, W-40, 115], fill=(234, 244, 238), outline=(18, 107, 69), width=2, radius=16)
    d.text((W//2, 75), "DUAL-JURISDICTION ISOLATION ENGINE", fill=(11, 79, 52), font=f_h1, anchor="mm")

    # Column 1: Indian Sovereign Law (Left)
    col1_x1, col1_x2 = 60, W//2 - 60
    draw_rounded_card(d, [col1_x1, 145, col1_x2, 680], fill=(250, 252, 251), outline=(18, 107, 69), width=3, radius=16)
    draw_rounded_card(d, [col1_x1 + 20, 165, col1_x2 - 20, 230], fill=(11, 79, 52), radius=10)
    d.text(((col1_x1 + col1_x2)//2, 198), "INDIAN SOVEREIGN LAW", fill=(255, 255, 255), font=f_h1, anchor="mm")

    # Items inside Col 1
    items1 = [
        ("The Patents Act, 1970", "Sec 3(p) non-patentability of TK formulas"),
        ("Biological Diversity Act, 2002/23", "Sec 6 mandatory NBA prior approval & ABS"),
        ("Drugs & Cosmetics Act, 1940", "Rules 1945 ASU licensing & Schedule 1 texts"),
        ("Ayurvedic Pharmacopoeia (API)", "Monograph specifications & identity tests")
    ]
    for idx, (title, desc) in enumerate(items1):
        cy = 255 + idx * 100
        draw_rounded_card(d, [col1_x1 + 25, cy, col1_x2 - 25, cy + 85], fill=(234, 244, 238), outline=(18, 107, 69), width=1, radius=8)
        d.text((col1_x1 + 45, cy + 25), title, fill=(11, 79, 52), font=f_bsmall)
        d.text((col1_x1 + 45, cy + 55), desc, fill=(82, 96, 87), font=f_small)

    # Column 2: International Treaties (Right)
    col2_x1, col2_x2 = W//2 + 60, W - 60
    draw_rounded_card(d, [col2_x1, 145, col2_x2, 680], fill=(250, 252, 251), outline=(37, 99, 166), width=3, radius=16)
    draw_rounded_card(d, [col2_x1 + 20, 165, col2_x2 - 20, 230], fill=(37, 99, 166), radius=10)
    d.text(((col2_x1 + col2_x2)//2, 198), "INTERNATIONAL TREATIES", fill=(255, 255, 255), font=f_h1, anchor="mm")

    items2 = [
        ("WIPO GRATK Treaty (2024)", "Mandatory patent disclosure of genetic resources"),
        ("Nagoya Protocol (CBD)", "Fair & equitable benefit sharing access (ABS)"),
        ("Patent Cooperation Treaty (PCT)", "International prior art novelty search"),
        ("TKDL Defensive Guidance", "Prior art disclosure to USPTO/EPO/JPO")
    ]
    for idx, (title, desc) in enumerate(items2):
        cy = 255 + idx * 100
        draw_rounded_card(d, [col2_x1 + 25, cy, col2_x2 - 25, cy + 85], fill=(240, 247, 255), outline=(37, 99, 166), width=1, radius=8)
        d.text((col2_x1 + 45, cy + 25), title, fill=(37, 99, 166), font=f_bsmall)
        d.text((col2_x1 + 45, cy + 55), desc, fill=(82, 96, 87), font=f_small)

    # Center Boundary Barrier (Firewall)
    d.line([(W//2, 160), (W//2, 670)], fill=(166, 106, 0), width=4)
    draw_rounded_card(d, [W//2 - 50, 360, W//2 + 50, 460], fill=(255, 255, 255), outline=(166, 106, 0), width=3, radius=12)
    d.text((W//2, 400), "ZERO", fill=(166, 106, 0), font=f_bsmall, anchor="mm")
    d.text((W//2, 425), "LEAK", fill=(166, 106, 0), font=f_bsmall, anchor="mm")

    # Bottom Router Box
    draw_rounded_card(d, [120, 715, W - 120, 850], fill=(240, 245, 241), outline=(18, 107, 69), width=2, radius=16)
    d.text((W//2, 755), "Pre-Retrieval Formulation & Jurisdiction Router", fill=(11, 79, 52), font=f_h1, anchor="mm")
    d.text((W//2, 805), "Distinguishes classical compound remedies from novel extracts before executing legal search", fill=(82, 96, 87), font=f_body, anchor="mm")

    im.convert("RGB").save(out_path, quality=95)
    print("Saved Diagram 2 to", out_path)

# =============================================================================
# DIAGRAM 3: Citation Provenance & Legal Audit
# =============================================================================
def make_diagram_3(out_path):
    im = Image.new("RGBA", (W, H), (247, 248, 245, 255))
    d = ImageDraw.Draw(im)
    f_title, f_h1, f_body, f_small, f_bsmall = get_fonts(38, 26, 21)

    draw_rounded_card(d, [15, 15, W-15, H-15], fill=(255, 255, 255), outline=(220, 229, 222), width=3, radius=24)

    # Top Header Banner
    draw_rounded_card(d, [40, 35, W-40, 115], fill=(234, 244, 238), outline=(18, 107, 69), width=2, radius=16)
    d.text((W//2, 75), "CITATION PROVENANCE & AUDIT PIPELINE", fill=(11, 79, 52), font=f_h1, anchor="mm")

    # 3-Stage Pipeline Horizontal Flow
    stages = [
        ("STAGE 1: INPUT", "Legal Query Ingestion", "Extracts botanical names,\nintent, jurisdiction", 60, (18, 107, 69)),
        ("STAGE 2: RETRIEVAL", "Epistemic Reasoner", "Binds explicit statutory facts\nvs legal opinions", 560, (37, 99, 166)),
        ("STAGE 3: VERDICT", "Audit-Locked Answer", "Includes gazette URL, act date,\nand section anchors", 1060, (11, 79, 52))
    ]
    for title, h1, body, x, col in stages:
        draw_rounded_card(d, [x, 150, x + 480, 520], fill=(250, 252, 251), outline=col, width=3, radius=16)
        draw_rounded_card(d, [x + 20, 170, x + 460, 230], fill=col, radius=10)
        d.text((x + 240, 200), title, fill=(255, 255, 255), font=f_bsmall, anchor="mm")
        d.text((x + 240, 280), h1, fill=(23, 33, 27), font=f_h1, anchor="mm")
        
        # Text block
        lines = body.split("\n")
        d.text((x + 240, 350), lines[0], fill=(82, 96, 87), font=f_body, anchor="mm")
        if len(lines) > 1:
            d.text((x + 240, 385), lines[1], fill=(82, 96, 87), font=f_body, anchor="mm")
            
        draw_rounded_card(d, [x + 40, 440, x + 440, 490], fill=(234, 244, 238), outline=col, width=1, radius=8)
        d.text((x + 240, 465), "Verifiable Statutory Link", fill=col, font=f_small, anchor="mm")

    # Arrows between stages
    d.polygon([(525, 335), (555, 335), (540, 315)], fill=(18, 107, 69))
    d.polygon([(1025, 335), (1055, 335), (1040, 315)], fill=(18, 107, 69))
    d.line([(510, 335), (555, 335)], fill=(18, 107, 69), width=5)
    d.line([(1010, 335), (1055, 335)], fill=(18, 107, 69), width=5)

    # Bottom Trust Enforcement Banner
    draw_rounded_card(d, [60, 560, W - 60, 850], fill=(240, 245, 241), outline=(18, 107, 69), width=3, radius=16)
    d.text((W//2, 615), "MATHEMATICAL TRUST ENFORCEMENT", fill=(11, 79, 52), font=f_h1, anchor="mm")

    # 3 Badges at bottom
    badges = [
        ("Gazette Authority", "Every citation links to official gazette entry", 100),
        ("Epistemic Separation", "Strict division between law and inference", 580),
        ("Safe Abstention", "Rejects claims lacking statutory proof", 1060)
    ]
    for b_title, b_sub, bx in badges:
        draw_rounded_card(d, [bx, 670, bx + 440, 810], fill=(255, 255, 255), outline=(220, 229, 222), width=2, radius=12)
        d.text((bx + 220, 715), b_title, fill=(11, 79, 52), font=f_bsmall, anchor="mm")
        d.text((bx + 220, 765), b_sub, fill=(82, 96, 87), font=f_small, anchor="mm")

    im.convert("RGB").save(out_path, quality=95)
    print("Saved Diagram 3 to", out_path)

# =============================================================================
# DIAGRAM 4: Trilingual & Defensive Safeguard
# =============================================================================
def make_diagram_4(out_path):
    im = Image.new("RGBA", (W, H), (247, 248, 245, 255))
    d = ImageDraw.Draw(im)
    f_title, f_h1, f_body, f_small, f_bsmall = get_fonts(38, 26, 21)
    f_indic_bold = ImageFont.truetype(r"C:\Windows\Fonts\Nirmala.ttc", 23)
    f_indic_body = ImageFont.truetype(r"C:\Windows\Fonts\Nirmala.ttc", 19)

    draw_rounded_card(d, [15, 15, W-15, H-15], fill=(255, 255, 255), outline=(220, 229, 222), width=3, radius=24)

    # Top Header Banner
    draw_rounded_card(d, [40, 35, W-40, 115], fill=(234, 244, 238), outline=(18, 107, 69), width=2, radius=16)
    d.text((W//2, 75), "NATIVE TRILINGUAL & DEFENSIVE SAFEGUARD", fill=(11, 79, 52), font=f_h1, anchor="mm")

    # 3 Language Inputs
    langs = [
        ("English", "Official IPO & WIPO filings", 60, f_bsmall, f_small),
        ("हिंदी (Hindi)", "आयुष और पेटेंट कानून सहायता", 560, f_indic_bold, f_indic_body),
        ("ಕನ್ನಡ (Kannada)", "ಆಯುರ್ವೇದ ಪೇಟೆಂಟ್ ಮಾರ್ಗದರ್ಶನ", 1060, f_indic_bold, f_indic_body)
    ]
    for l_name, l_sub, lx, f_n, f_s in langs:
        draw_rounded_card(d, [lx, 150, lx + 480, 260], fill=(250, 252, 251), outline=(18, 107, 69), width=2, radius=14)
        draw_rounded_card(d, [lx + 20, 165, lx + 460, 210], fill=(18, 107, 69), radius=8)
        d.text((lx + 240, 187), l_name, fill=(255, 255, 255), font=f_n, anchor="mm")
        d.text((lx + 240, 235), l_sub, fill=(82, 96, 87), font=f_s, anchor="mm")

    # Downward connecting flow
    d.line([(W//2, 265), (W//2, 315)], fill=(18, 107, 69), width=4)
    d.polygon([(W//2 - 12, 310), (W//2 + 12, 310), (W//2, 330)], fill=(18, 107, 69))

    # Middle Processing Card: Indic NLP & Citation Immutability
    draw_rounded_card(d, [100, 335, W - 100, 525], fill=(240, 247, 255), outline=(37, 99, 166), width=2, radius=16)
    d.text((W//2, 380), "Indic Embedding & Citation Immutability Engine", fill=(37, 99, 166), font=f_h1, anchor="mm")
    d.text((W//2, 430), "Transfers natural language query while preserving legal terms untranslated", fill=(23, 33, 27), font=f_body, anchor="mm")
    d.text((W//2, 475), "Statutory section numbers (e.g., Sec 3(p), Sec 6 NBA) remain legally pristine", fill=(82, 96, 87), font=f_small, anchor="mm")

    # Downward connecting flow
    d.line([(W//2, 530), (W//2, 575)], fill=(18, 107, 69), width=4)
    d.polygon([(W//2 - 12, 570), (W//2 + 12, 570), (W//2, 590)], fill=(18, 107, 69))

    # Bottom Guardrail & Output
    draw_rounded_card(d, [60, 595, W - 60, 850], fill=(250, 252, 251), outline=(18, 107, 69), width=3, radius=16)
    
    # Left Box inside bottom: TKDL Non-Disclosure
    draw_rounded_card(d, [90, 625, W//2 - 20, 820], fill=(253, 242, 242), outline=(180, 35, 24), width=2, radius=12)
    d.text((90 + (W//2 - 20 - 90)//2, 670), "TKDL Defensive Guardrail", fill=(180, 35, 24), font=f_bsmall, anchor="mm")
    d.text((90 + (W//2 - 20 - 90)//2, 725), "Strict non-disclosure compliance protocol", fill=(23, 33, 27), font=f_body, anchor="mm")
    d.text((90 + (W//2 - 20 - 90)//2, 775), "Safe abstention on confidential TK manuscripts", fill=(82, 96, 87), font=f_small, anchor="mm")

    # Right Box inside bottom: Trilingual Response
    draw_rounded_card(d, [W//2 + 20, 625, W - 90, 820], fill=(234, 244, 238), outline=(18, 107, 69), width=2, radius=12)
    d.text((W//2 + 20 + (W - 90 - (W//2 + 20))//2, 670), "Grounded Trilingual Output", fill=(11, 79, 52), font=f_bsmall, anchor="mm")
    d.text((W//2 + 20 + (W - 90 - (W//2 + 20))//2, 725), "Natural fluency in chosen Indic language", fill=(23, 33, 27), font=f_body, anchor="mm")
    d.text((W//2 + 20 + (W - 90 - (W//2 + 20))//2, 775), "Interactive citation cards [1] [2] [3] in sidebar", fill=(82, 96, 87), font=f_small, anchor="mm")

    im.convert("RGB").save(out_path, quality=95)
    print("Saved Diagram 4 to", out_path)

if __name__ == "__main__":
    out_dir = r"c:\Projects\drugvista\extracted_assets\new_slide_assets"
    os.makedirs(out_dir, exist_ok=True)
    make_diagram_1(os.path.join(out_dir, "diag_col1_deterministic.png"))
    make_diagram_2(os.path.join(out_dir, "diag_col2_dual_jurisdiction.png"))
    make_diagram_3(os.path.join(out_dir, "diag_col3_citation_provenance.png"))
    make_diagram_4(os.path.join(out_dir, "diag_col4_trilingual_safeguard.png"))
