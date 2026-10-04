import os
import base64
import subprocess

PROJECT_DIR = r"c:\Projects\drugvista"
ASSETS_DIR = os.path.join(PROJECT_DIR, "presentation", "assets")
QR_DIR = os.path.join(ASSETS_DIR, "qrcodes")
ICONS_DIR = os.path.join(ASSETS_DIR, "custom_icons")

HTML_OUTPUT = os.path.join(PROJECT_DIR, "submission", "SIH2026_PROJECT_REPORT_OUTLAWS.html")
PDF_OUTPUT = os.path.join(PROJECT_DIR, "submission", "SIH2026_PROJECT_REPORT_OUTLAWS.pdf")

def img_to_base64(path):
    if os.path.exists(path):
        ext = os.path.splitext(path)[1].lower().replace(".", "")
        if ext == "jpg": ext = "jpeg"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/{ext};base64,{b64}"
    return ""

sih_logo_b64 = img_to_base64(os.path.join(ASSETS_DIR, "sih_logo_clean.png"))
ui_screenshot_b64 = img_to_base64(os.path.join(ASSETS_DIR, "ui_screenshot.jpg"))
qr_github_b64 = img_to_base64(os.path.join(QR_DIR, "qr_github.png"))
qr_report_b64 = img_to_base64(os.path.join(QR_DIR, "qr_report.png"))
qr_ipindia_b64 = img_to_base64(os.path.join(QR_DIR, "qr_ipindia.png"))
qr_nba_b64 = img_to_base64(os.path.join(QR_DIR, "qr_nba.png"))
qr_ayush_b64 = img_to_base64(os.path.join(QR_DIR, "qr_ayush.png"))
qr_wipo_b64 = img_to_base64(os.path.join(QR_DIR, "qr_wipo.png"))

icon_shield_b64 = img_to_base64(os.path.join(ICONS_DIR, "icon_shield.png"))
icon_leaf_b64 = img_to_base64(os.path.join(ICONS_DIR, "icon_leaf.png"))
icon_book_b64 = img_to_base64(os.path.join(ICONS_DIR, "icon_book_statute.png"))
icon_cpu_b64 = img_to_base64(os.path.join(ICONS_DIR, "icon_cpu.png"))
icon_multi_b64 = img_to_base64(os.path.join(ICONS_DIR, "icon_multilingual.png"))

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SIH 2026 Project Report - Team OUTLAWS - IP-SAKTI Sahayak</title>
<style>
  @page {{
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {{
      content: counter(page);
    }}
  }}

  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}

  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1E293B;
    background-color: #FFFFFF;
    line-height: 1.55;
    font-size: 10.5pt;
    margin: 0;
    padding: 0;
  }}

  /* Page Break Helpers */
  .page-break {{
    page-break-before: always;
  }}
  .avoid-break {{
    page-break-inside: avoid;
  }}

  /* Typography */
  h1, h2, h3, h4 {{
    color: #0B2545;
    font-family: 'Segoe UI', -apple-system, sans-serif;
    font-weight: 700;
    margin-top: 1.4em;
    margin-bottom: 0.5em;
    line-height: 1.25;
  }}

  h1 {{ font-size: 20pt; border-bottom: 2.5px solid #0B2545; padding-bottom: 6px; }}
  h2 {{ font-size: 14pt; border-left: 4.5px solid #059669; padding-left: 10px; margin-top: 1.8em; }}
  h3 {{ font-size: 11.5pt; color: #1B365D; margin-top: 1.2em; }}
  h4 {{ font-size: 10.5pt; color: #334155; margin-top: 1em; }}

  p, li {{
    font-size: 10pt;
    color: #334155;
    line-height: 1.55;
  }}

  strong {{
    color: #0F172A;
  }}

  /* Header & Footer styling */
  .doc-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1.5px solid #CBD5E1;
    padding-bottom: 8px;
    margin-bottom: 18px;
    font-size: 8.5pt;
    color: #64748B;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .doc-footer {{
    margin-top: 25px;
    border-top: 1px solid #E2E8F0;
    padding-top: 8px;
    display: flex;
    justify-content: space-between;
    font-size: 8pt;
    color: #94A3B8;
  }}

  /* Cover Page */
  .cover-container {{
    min-height: 92vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 10px 0;
  }}

  .cover-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 15px;
  }}

  .cover-badge {{
    background: #0B4F34;
    color: #FFFFFF;
    font-size: 9pt;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 20px;
    display: inline-block;
    letter-spacing: 0.5px;
  }}

  .cover-team-badge {{
    background: #1B365D;
    color: #FFFFFF;
    font-size: 12pt;
    font-weight: 800;
    padding: 8px 20px;
    border-radius: 8px;
    display: inline-block;
    letter-spacing: 1px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }}

  .cover-hero {{
    margin: 40px 0;
  }}

  .cover-title {{
    font-size: 26pt;
    font-weight: 900;
    color: #0B2545;
    line-height: 1.15;
    margin-bottom: 12px;
  }}

  .cover-subtitle {{
    font-size: 13pt;
    color: #475569;
    font-weight: 500;
    line-height: 1.45;
    margin-bottom: 25px;
    border-left: 4px solid #D97706;
    padding-left: 14px;
  }}

  .cover-pills {{
    display: flex;
    gap: 10px;
    margin-bottom: 30px;
    flex-wrap: wrap;
  }}

  .cover-pill {{
    background: #F1F5F9;
    border: 1px solid #CBD5E1;
    color: #0F172A;
    font-size: 8.5pt;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 6px;
  }}

  .cover-pill.green {{ background: #E6F6EE; border-color: #A7F3D0; color: #065F46; }}
  .cover-pill.blue {{ background: #EFF6FF; border-color: #BFDBFE; color: #1E40AF; }}
  .cover-pill.amber {{ background: #FEF3EB; border-color: #FDE68A; color: #92400E; }}

  /* Meta Table */
  table.meta-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 9.5pt;
  }}

  table.meta-table th, table.meta-table td {{
    padding: 10px 14px;
    border: 1px solid #E2E8F0;
    text-align: left;
  }}

  table.meta-table th {{
    background-color: #0B2545;
    color: #FFFFFF;
    width: 28%;
    font-weight: 600;
  }}

  table.meta-table td {{
    background-color: #F8FAFC;
    color: #1E293B;
  }}

  /* Data & Comparison Tables */
  table.data-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 8.8pt;
  }}

  table.data-table th {{
    background: #1B365D;
    color: #FFFFFF;
    font-weight: 600;
    padding: 8px 10px;
    border: 1px solid #CBD5E1;
    text-align: left;
  }}

  table.data-table td {{
    padding: 7px 10px;
    border: 1px solid #E2E8F0;
    vertical-align: middle;
  }}

  table.data-table tr:nth-child(even) {{
    background-color: #F8FAFC;
  }}

  /* Callout Boxes */
  .callout {{
    background: #F8FAFC;
    border-left: 4px solid #0B2545;
    padding: 12px 16px;
    margin: 16px 0;
    border-radius: 0 6px 6px 0;
    border-top: 1px solid #E2E8F0;
    border-right: 1px solid #E2E8F0;
    border-bottom: 1px solid #E2E8F0;
  }}

  .callout.green {{
    background: #F0FDF4;
    border-left-color: #059669;
    border-color: #BBF7D0;
  }}

  .callout.amber {{
    background: #FFFBEB;
    border-left-color: #D97706;
    border-color: #FDE68A;
  }}

  .callout.blue {{
    background: #EFF6FF;
    border-left-color: #2563EB;
    border-color: #BFDBFE;
  }}

  .callout h4 {{
    margin-top: 0;
    margin-bottom: 4px;
  }}

  /* Metric Grid */
  .metric-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 18px 0;
  }}

  .metric-card {{
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 12px;
    text-align: center;
  }}

  .metric-card.highlight {{
    background: #E6F6EE;
    border-color: #10B981;
  }}

  .metric-val {{
    font-size: 16pt;
    font-weight: 800;
    color: #0B4F34;
    line-height: 1.1;
  }}

  .metric-title {{
    font-size: 8pt;
    font-weight: 700;
    color: #0B2545;
    margin-top: 4px;
    text-transform: uppercase;
  }}

  .metric-sub {{
    font-size: 7.5pt;
    color: #64748B;
    margin-top: 2px;
  }}

  /* Badges */
  .badge-pass {{
    background: #D1FAE5;
    color: #065F46;
    font-weight: 700;
    font-size: 7.5pt;
    padding: 2px 7px;
    border-radius: 4px;
    display: inline-block;
  }}

  .badge-primary {{
    background: #DBEAFE;
    color: #1E40AF;
    font-weight: 700;
    font-size: 7.5pt;
    padding: 2px 7px;
    border-radius: 4px;
    display: inline-block;
  }}

  /* Layer Box */
  .layer-box {{
    background: #FFFFFF;
    border: 1.2px solid #E2E8F0;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 14px;
  }}

  .layer-tag {{
    font-weight: 800;
    font-size: 8.5pt;
    padding: 6px 10px;
    border-radius: 4px;
    min-width: 140px;
    text-align: center;
  }}

  .layer-tag.l1 {{ background: #E6F6EE; color: #0B4F34; }}
  .layer-tag.l2 {{ background: #EFF6FF; color: #1E40AF; }}
  .layer-tag.l3 {{ background: #FEF3EB; color: #B45309; }}
  .layer-tag.l4 {{ background: #F1F5F9; color: #0F172A; }}

  /* UI Image Showcase */
  .ui-showcase {{
    text-align: center;
    margin: 18px 0;
    border: 1.5px solid #CBD5E1;
    border-radius: 8px;
    overflow: hidden;
    background: #0F172A;
    padding: 6px;
  }}

  .ui-showcase img {{
    width: 100%;
    max-height: 380px;
    object-fit: contain;
    border-radius: 4px;
  }}

  .ui-caption {{
    font-size: 8.5pt;
    color: #94A3B8;
    margin-top: 6px;
    padding-bottom: 4px;
  }}

  /* QR Box */
  .qr-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 16px 0;
  }}

  .qr-item {{
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 10px;
    text-align: center;
    background: #F8FAFC;
  }}

  .qr-item img {{
    width: 65px;
    height: 65px;
    margin-bottom: 6px;
  }}

  .qr-title {{
    font-size: 8pt;
    font-weight: 700;
    color: #0B2545;
  }}

  .qr-link {{
    font-size: 7pt;
    color: #2563EB;
    word-break: break-all;
  }}
</style>
</head>
<body>

<!-- ========================================================================= -->
<!-- COVER PAGE -->
<!-- ========================================================================= -->
<div class="cover-container">
  <div class="cover-top">
    <div>
      {f'<img src="{sih_logo_b64}" style="height: 65px;" alt="Smart India Hackathon Logo">' if sih_logo_b64 else '<span style="font-size: 16pt; font-weight: 800; color: #0B2545;">SMART INDIA HACKATHON 2026</span>'}
    </div>
    <div style="text-align: right;">
      <div class="cover-team-badge">TEAM: OUTLAWS</div>
      <div style="font-size: 8.5pt; color: #64748B; margin-top: 4px; font-weight: 600;">TEAM ID: 146711</div>
    </div>
  </div>

  <div class="cover-hero">
    <div class="cover-badge">SIH 2026 OFFICIAL SUBMISSION REPORT</div>
    <div class="cover-title" style="margin-top: 15px;">IP-SAKTI Sahayak</div>
    <div class="cover-subtitle">
      A Grounded, Sovereign AI Copilot for Ayurvedic Intellectual Property, Prior Art Triage, and Regulatory Frameworks
    </div>

    <div class="cover-pills">
      <div class="cover-pill green">✓ 100% Offline CPU Execution</div>
      <div class="cover-pill blue">✓ Zero Cloud API Costs</div>
      <div class="cover-pill amber">✓ SHA-256 Provenance Immutability</div>
      <div class="cover-pill green">✓ Native Trilingual (EN / HI / KN)</div>
      <div class="cover-pill blue">✓ 106 / 106 Automated Tests Passing</div>
    </div>

    <table class="meta-table">
      <tr>
        <th>Problem Statement ID</th>
        <td><strong>SIH26045</strong></td>
      </tr>
      <tr>
        <th>Problem Statement Title</th>
        <td>Student Innovation – AI-Powered Assistant for Intellectual Property, Traditional Knowledge, and Regulatory Frameworks in Ayurveda</td>
      </tr>
      <tr>
        <th>Theme & Category</th>
        <td><strong>MedTech / Ayush / LegalTech</strong> &nbsp;|&nbsp; <strong>Software</strong></td>
      </tr>
      <tr>
        <th>Team Name & Team ID</th>
        <td><strong>OUTLAWS</strong> &nbsp;(Team ID: <strong>146711</strong>)</td>
      </tr>
      <tr>
        <th>Target Ministries / Bodies</th>
        <td>Ministry of Ayush, Intellectual Property India (CGPDTM), National Biodiversity Authority (NBA), CSIR-TKDL</td>
      </tr>
      <tr>
        <th>Readiness Level</th>
        <td><strong>TRL-6 (Fully validated working prototype with 106 automated tests)</strong></td>
      </tr>
      <tr>
        <th>GitHub Repository</th>
        <td><a href="https://github.com/Rengoku9000/Drugvista" style="color:#2563EB; text-decoration:none;">github.com/Rengoku9000/Drugvista</a></td>
      </tr>
    </table>
  </div>

  <div class="doc-footer">
    <div>Smart India Hackathon 2026 &bull; Idea & Prototype Submission</div>
    <div>Confidential &bull; Team OUTLAWS</div>
  </div>
</div>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- SECTION 1: EXECUTIVE SUMMARY -->
<!-- ========================================================================= -->
<div class="doc-header">
  <div>IP-SAKTI Sahayak &bull; Problem Statement SIH26045</div>
  <div>Team OUTLAWS &bull; Team ID: 146711</div>
</div>

<h1>1. Executive Summary & Core Value Proposition</h1>

<p>
Ayurvedic intellectual property represents a critical intersection of national biological sovereignty, classical cultural heritage, and modern pharmaceutical biotechnology. Historically, Indian traditional medicine has been uniquely vulnerable to biopiracy and wrongful international patent grants (evidenced by landmark international disputes involving Turmeric, Neem, and Basmati) because patent examiners and domestic researchers lack fast, authoritative, and linguistically accessible prior art discovery tools.
</p>

<p>
Domestically, innovators face an intricate statutory labyrinth: navigating <strong>Section 3(p) exclusions</strong> under the Patents Act 1970, mandatory <strong>Access and Benefit Sharing (ABS) compliance</strong> under Section 6 of the Biological Diversity Act (BDA 2002/2023), and <strong>ASU manufacturing licensing</strong> under Chapter IV-A of the Drugs and Cosmetics Act 1940.
</p>

<p>
<strong>IP-SAKTI Sahayak</strong>, engineered by <strong>Team OUTLAWS</strong>, is an offline-first, sovereign AI co-pilot built specifically to eliminate this Ayush IP Trilemma. Rejecting the non-deterministic hallucination risks of generic commercial LLMs, IP-SAKTI Sahayak enforces the unyielding operational doctrine: <strong>"No Evidence &rarr; No Claim"</strong>.
</p>

<div class="metric-grid">
  <div class="metric-card highlight">
    <div class="metric-val">106 / 106</div>
    <div class="metric-title">Automated Tests</div>
    <div class="metric-sub">100% pass across 30 suites</div>
  </div>
  <div class="metric-card">
    <div class="metric-val">&lt; 1.20 s</div>
    <div class="metric-title">Response Latency</div>
    <div class="metric-sub">Standard non-GPU laptop CPU</div>
  </div>
  <div class="metric-card highlight">
    <div class="metric-val">0.00%</div>
    <div class="metric-title">Jurisdiction Leak</div>
    <div class="metric-sub">Strict India vs Intl firewall</div>
  </div>
  <div class="metric-card">
    <div class="metric-val">~650 MB</div>
    <div class="metric-title">RAM Footprint</div>
    <div class="metric-sub">Zero discrete GPU required</div>
  </div>
</div>

<div class="callout green">
  <h4 style="color: #065F46; margin-bottom: 4px;">Core Architectural Distinctions:</h4>
  <ul style="margin: 4px 0 0 16px; padding: 0; font-size: 9.5pt;">
    <li><strong>Deterministic Gazette Citations:</strong> Every legal output links to an official Gazette section, enactment date, and government URL.</li>
    <li><strong>Formulation vs Extract Router:</strong> Differentiates classical polyherbal remedies from novel chemical extractions.</li>
    <li><strong>Native Trilingual Indic Delivery:</strong> Full support for English, Hindi, and Kannada with immutable legal citation anchors.</li>
    <li><strong>Sovereign Privacy:</strong> 100% local CPU execution ensures proprietary formulations never leave institutional premises.</li>
  </ul>
</div>

<!-- ========================================================================= -->
<!-- SECTION 2: THE AYUSH IP TRILEMMA -->
<!-- ========================================================================= -->
<h2>2. Problem Context & The Ayush IP Trilemma</h2>

<div class="callout amber">
  <h4 style="color: #92400E;">The Core Crisis in Traditional Knowledge Protection</h4>
  Traditional Ayurvedic formulations face systemic friction across patent examination, biodiversity regulation, and linguistic accessibility. Generic generative AI models worsen the crisis by hallucinating fictitious statutes and leaking confidential formulations to overseas clouds.
</div>

<table class="data-table">
  <thead>
    <tr>
      <th style="width: 25%;">Dimension</th>
      <th style="width: 38%;">The Statutory Friction / Vulnerability</th>
      <th style="width: 37%;">IP-SAKTI Sahayak Resolution</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>1. Patents Act Sec 3(p) & Prior Art</strong></td>
      <td>Section 3(p) bars patenting of traditional knowledge or aggregations (Sec 3(e)). Innovators waste years attempting to patent non-patentable classical recipes, while legitimate novel formulations are abandoned.</td>
      <td><strong>Automated Prior Art Triage:</strong> Evaluates classical texts and pharmacopoeias, instantly flagging Section 3(p) bars while identifying patentable novel extracts.</td>
    </tr>
    <tr>
      <td><strong>2. Biodiversity (BDA) & ABS Approvals</strong></td>
      <td>Section 6 of Biological Diversity Act mandates prior NBA approval before applying for IPR on Indian biological resources. Failure results in severe criminal penalties and patent revocation.</td>
      <td><strong>Compliance Route Guidance:</strong> Classifies whether the applicant is subject to mandatory NBA prior approval or State Biodiversity Board intimation.</td>
    </tr>
    <tr>
      <td><strong>3. Drugs & Cosmetics Act (ASU)</strong></td>
      <td>Chapter IV-A & Rule 158-B require distinct proof of effectiveness for Classical ASU vs Patent/Proprietary ASU medicines, confusing small herbal manufacturers.</td>
      <td><strong>Regulatory Pathway Mapping:</strong> Directly maps formulations to First Schedule authoritative texts, Rule 158-B criteria, and PCIM&H standards.</td>
    </tr>
    <tr>
      <td><strong>4. Linguistic Divide & Biopiracy</strong></td>
      <td>80%+ Vaidyas and MSMEs operate in regional languages (Hindi, Kannada), cut off from complex English-only patent databases.</td>
      <td><strong>Native Indic Intelligence:</strong> High-fidelity reasoning in Hindi and Kannada with immutable, untranslated legal citation anchors.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- SECTION 3: SYSTEM ARCHITECTURE -->
<!-- ========================================================================= -->
<div class="doc-header">
  <div>IP-SAKTI Sahayak &bull; Problem Statement SIH26045</div>
  <div>Team OUTLAWS &bull; Team ID: 146711</div>
</div>

<h1>3. System Architecture & Technical Approach</h1>

<p>
IP-SAKTI Sahayak is designed as a modular, decoupled 4-tier architecture engineered for ultra-fast local inference, strict deterministic guardrails, and cryptographic provenance tracking.
</p>

<div class="avoid-break">
  <div class="layer-box">
    <div class="layer-tag l1">LAYER 1: PRESENTATION</div>
    <div>
      <strong>Streamlit High-Contrast Reactive Web Interface</strong><br>
      <span style="font-size: 9pt; color: #475569;">Trilingual query input (EN/HI/KN) &bull; Citation Inspector Drawer &bull; Color-coded Epistemic Status Badges &bull; Official Gazette URL Linkers</span>
    </div>
  </div>

  <div class="layer-box">
    <div class="layer-tag l2">LAYER 2: REASONING & API</div>
    <div>
      <strong>FastAPI Microservices & Epistemic Reasoner</strong><br>
      <span style="font-size: 9pt; color: #475569;">Unicode Script Language Detector &bull; Botanical Entity Normalizer &bull; Dual-Track Jurisdiction Router &bull; 5-State Epistemic Reasoner</span>
    </div>
  </div>

  <div class="layer-box">
    <div class="layer-tag l3">LAYER 3: RETRIEVAL & DB</div>
    <div>
      <strong>FAISS CPU Dense Vector Index + SQLite WAL Provenance</strong><br>
      <span style="font-size: 9pt; color: #475569;">384-dimensional all-MiniLM-L6-v2 embeddings &bull; Sub-1.2s similarity retrieval &bull; Dynamic Authority Level Scoring (+0.08 PRIMARY bonus, +0.25 Anchor match bonus)</span>
    </div>
  </div>

  <div class="layer-box">
    <div class="layer-tag l4">LAYER 4: STATUTORY CORPUS</div>
    <div>
      <strong>Cryptographically Verified Sovereign Legal Knowledge Base</strong><br>
      <span style="font-size: 9pt; color: #475569;">7 Primary Statutes backed by SHA-256 Checksums &bull; Regex-based Citation Locker &bull; Forbidden Verdict Filter &bull; TKDL Defensive Shield</span>
    </div>
  </div>
</div>

<h2>3.1 End-to-End Decision Pipeline Flow</h2>
<div class="callout blue">
  <div style="font-family: monospace; font-size: 8.8pt; line-height: 1.4; color: #0F172A;">
    [User Natural Language Query (EN/HI/KN)]<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&darr; (Phase 2C: Unicode Script Block Frequency Detection & Verbatim Section Regex Shield)<br>
    [Language Detection & Canonical Normalization]<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&darr; (Phase 2B.1: Latin Binomial Extraction & ASU Classical vs Novel Formulation Triage)<br>
    [Intent, Entity & Formulation Classifier]<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&darr; (Phase 2B.1: Strict Legal Firewall &mdash; 0.00% Cross-Leakage Enforcement)<br>
    [Dual-Track Isolated Jurisdiction Router (Track A: India | Track B: International)]<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&darr; (Phase 2A: FAISS Dense Vector + SQLite WAL Relational Schema)<br>
    [Authoritative Retrieval & Scoring Boost (Primary +0.08, Exact Anchor +0.25)]<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&darr; (Phase 2B.2: Strict "No Evidence &rarr; No Claim" State Machine)<br>
    [Epistemic Reasoner & Answer Validation Guardrails]<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&darr; (Phase 2C: Immutable Citation Masking & Target Language Localization)<br>
    [Cited, Verifiable Trilingual Structured Response with Official Gazette URLs]
  </div>
</div>

<h2>3.2 Working Prototype UI Showcase</h2>
<p>
The working application features a responsive, non-technical user experience enabling seamless legal triage for researchers, patent attorneys, and traditional Vaidyas:
</p>

<div class="ui-showcase">
  {f'<img src="{ui_screenshot_b64}" alt="IP-SAKTI Sahayak Working Prototype UI">' if ui_screenshot_b64 else '<div style="color:white; padding: 40px;">[Streamlit Working Prototype Screenshot]</div>'}
  <div class="ui-caption">Figure 1: IP-SAKTI Sahayak Live Streamlit UI &mdash; Query Triage, Interactive Citation Inspector Drawer, and Verifiable Statutory Gazette Anchors</div>
</div>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- SECTION 4: MASTER KNOWLEDGE CORPUS AUDIT -->
<!-- ========================================================================= -->
<div class="doc-header">
  <div>IP-SAKTI Sahayak &bull; Problem Statement SIH26045</div>
  <div>Team OUTLAWS &bull; Team ID: 146711</div>
</div>

<h1>4. Master Knowledge Base & Source Integrity Audit</h1>

<p>
A core vulnerability in legal and regulatory AI is "silent knowledge drift" or hallucinated statutory provisions. To establish courtroom-grade reliability, Team OUTLAWS executed an exhaustive source audit verifying all 7 production knowledge corpuses against official government gazettes:
</p>

<table class="data-table">
  <thead>
    <tr>
      <th style="width: 20%;">Statute / Corpus</th>
      <th style="width: 25%;">Official Issuing Authority</th>
      <th style="width: 20%;">Official Source Portal</th>
      <th style="width: 12%;">Authority</th>
      <th style="width: 11%;">Status</th>
      <th style="width: 12%;">Verification</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>The Patents Act, 1970</strong><br><span style="font-size:7.5pt; color:#64748B;">Act 39 of 1970 (Consolidated 2024)</span></td>
      <td>Intellectual Property India, Min. of Commerce & Industry</td>
      <td><a href="https://ipindia.gov.in" style="color:#2563EB;">ipindia.gov.in</a></td>
      <td><span class="badge-primary">PRIMARY</span></td>
      <td><code>IN_FORCE</code></td>
      <td><span class="badge-pass">VERIFIED</span></td>
    </tr>
    <tr>
      <td><strong>The Biological Diversity Act, 2002 & 2023</strong><br><span style="font-size:7.5pt; color:#64748B;">Act 18 of 2003 with 2023 Amendment</span></td>
      <td>National Biodiversity Authority (NBA), MoEFCC</td>
      <td><a href="https://indiacode.nic.in" style="color:#2563EB;">indiacode.nic.in</a></td>
      <td><span class="badge-primary">PRIMARY</span></td>
      <td><code>IN_FORCE</code></td>
      <td><span class="badge-pass">VERIFIED</span></td>
    </tr>
    <tr>
      <td><strong>Drugs & Cosmetics Act, 1940 & Rules 1945</strong><br><span style="font-size:7.5pt; color:#64748B;">Chapter IV-A & Rules Part XVI-A</span></td>
      <td>Ministry of Ayush / CDSCO, Govt of India</td>
      <td><a href="https://ayush.gov.in" style="color:#2563EB;">ayush.gov.in</a></td>
      <td><span class="badge-primary">PRIMARY</span></td>
      <td><code>IN_FORCE</code></td>
      <td><span class="badge-pass">VERIFIED</span></td>
    </tr>
    <tr>
      <td><strong>WIPO GRATK Treaty, 2024</strong><br><span style="font-size:7.5pt; color:#64748B;">Genetic Resources & Associated TK</span></td>
      <td>World Intellectual Property Organization (WIPO)</td>
      <td><a href="https://wipo.int" style="color:#2563EB;">wipo.int</a></td>
      <td><span class="badge-primary">PRIMARY</span></td>
      <td><code>ADOPTED</code></td>
      <td><span class="badge-pass">VERIFIED</span></td>
    </tr>
    <tr>
      <td><strong>Nagoya Protocol on ABS</strong><br><span style="font-size:7.5pt; color:#64748B;">UNEP/CBD/COP/DEC/X/1</span></td>
      <td>Convention on Biological Diversity (CBD) Secretariat</td>
      <td><a href="https://cbd.int" style="color:#2563EB;">cbd.int</a></td>
      <td><span class="badge-primary">PRIMARY</span></td>
      <td><code>IN_FORCE</code></td>
      <td><span class="badge-pass">VERIFIED</span></td>
    </tr>
    <tr>
      <td><strong>Ayush Pharmacopoeial Standards</strong><br><span style="font-size:7.5pt; color:#64748B;">PCIM&H Regulatory Standards 2021</span></td>
      <td>Pharmacopoeia Commission for Indian Medicine & Homoeopathy</td>
      <td><a href="https://pcimh.gov.in" style="color:#2563EB;">pcimh.gov.in</a></td>
      <td><span style="background:#E2E8F0; color:#334155; font-size:7.5pt; padding:2px 6px; border-radius:4px; font-weight:700;">SECONDARY</span></td>
      <td><code>IN_FORCE</code></td>
      <td><span class="badge-pass">VERIFIED</span></td>
    </tr>
    <tr>
      <td><strong>TKDL Defensive Scope Advisory</strong><br><span style="font-size:7.5pt; color:#64748B;">Public Defensive Prior Art Framework</span></td>
      <td>CSIR & Ministry of Ayush, Govt of India</td>
      <td><a href="https://tkdl.res.in" style="color:#2563EB;">tkdl.res.in</a></td>
      <td><span style="background:#E2E8F0; color:#334155; font-size:7.5pt; padding:2px 6px; border-radius:4px; font-weight:700;">SECONDARY</span></td>
      <td><code>IN_FORCE</code></td>
      <td><span class="badge-pass">VERIFIED</span></td>
    </tr>
  </tbody>
</table>

<div class="callout amber">
  <h4 style="color:#92400E;">Key Statutory Distinctions Enforced by IP-SAKTI Sahayak:</h4>
  <p style="margin: 0; font-size: 9pt;">
    <strong>1. WIPO GRATK Treaty Status:</strong> Correctly modeled as <code>ADOPTED</code> but <code>NOT_IN_FORCE</code> (pending deposit of 15 ratifications under Article 17). It is never falsely applied as domestic Indian legislation.<br>
    <strong>2. Biological Diversity (Amendment) Act 2023:</strong> Distinguishes codified exemptions between registered AYUSH practitioners and commercial manufacturers regarding State Biodiversity Board (SBB) intimations.<br>
    <strong>3. TKDL Defensive Non-Disclosure:</strong> Adheres strictly to CSIR guidelines; guides users on public prior art without breaching confidential classical manuscripts.
  </p>
</div>

<!-- ========================================================================= -->
<!-- SECTION 5: EMPIRICAL BENCHMARKS -->
<!-- ========================================================================= -->
<h2>5. Empirical Benchmarks & Validation Results</h2>

<p>
The system's intelligence, routing, and language capabilities were validated against three comprehensive benchmark suites:
</p>

<table class="data-table">
  <thead>
    <tr>
      <th>Benchmark Dimension</th>
      <th>Test Scope</th>
      <th>Key Metrics Evaluated</th>
      <th>Achieved Score</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Phase 2B.1: Classification & Routing</strong></td>
      <td>50-Query Curated Dataset</td>
      <td>Intent Accuracy &bull; Jurisdiction Accuracy &bull; Leakage Rate</td>
      <td><strong>100% Intent, 100% Jur, 0.00% Leak</strong></td>
      <td><span class="badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td><strong>Phase 2B.2: Evidence Reasoning</strong></td>
      <td>30-Case Authoritative Benchmark</td>
      <td>Status Accuracy &bull; Anchor Hit Rate &bull; Unsupported Claims</td>
      <td><strong>100% Status, 0.00% Unsupported</strong></td>
      <td><span class="badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td><strong>Phase 2C: Trilingual Text Intelligence</strong></td>
      <td>30 Cases (10 EN, 10 HI, 10 KN)</td>
      <td>Language Detect &bull; Citation Anchor Immutability</td>
      <td><strong>100% Detect, 0 Anchor Mutations</strong></td>
      <td><span class="badge-pass">PASS</span></td>
    </tr>
    <tr>
      <td><strong>Full Automated Regression Suite</strong></td>
      <td>30 Python Test Modules</td>
      <td>Total Automated Tests Passing</td>
      <td><strong>106 / 106 Tests (100%) in 9.7s</strong></td>
      <td><span class="badge-pass">PASS</span></td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- SECTION 6: FEASIBILITY & ROADMAP -->
<!-- ========================================================================= -->
<div class="doc-header">
  <div>IP-SAKTI Sahayak &bull; Problem Statement SIH26045</div>
  <div>Team OUTLAWS &bull; Team ID: 146711</div>
</div>

<h1>6. Feasibility, Scalability & Phased Roadmap</h1>

<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-val">TRL-6</div>
    <div class="metric-title">Maturity Level</div>
    <div class="metric-sub">Verified working prototype</div>
  </div>
  <div class="metric-card highlight">
    <div class="metric-val">&#8377;0.00</div>
    <div class="metric-title">Recurring API Cost</div>
    <div class="metric-sub">Zero proprietary token fees</div>
  </div>
  <div class="metric-card">
    <div class="metric-val">Docker</div>
    <div class="metric-title">Deployability</div>
    <div class="metric-sub">One-click containerization</div>
  </div>
  <div class="metric-card highlight">
    <div class="metric-val">100%</div>
    <div class="metric-title">Offline Ready</div>
    <div class="metric-sub">Functions in remote Ayush clinics</div>
  </div>
</div>

<h2>6.1 Scalability & Deployment Roadmap</h2>
<table class="data-table">
  <thead>
    <tr>
      <th style="width: 25%;">Phase</th>
      <th style="width: 18%;">Timeline</th>
      <th style="width: 57%;">Target Milestones & Deliverables</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Phase 1: Working Prototype</strong><br><span class="badge-pass">CURRENT MILESTONE</span></td>
      <td>SIH 2026</td>
      <td>
        &bull; 7 primary statutory corpuses indexed with SHA-256 validation.<br>
        &bull; Full-featured FastAPI backend & responsive Streamlit web UI.<br>
        &bull; Sub-1.2s local CPU retrieval; 106/106 automated tests passing.<br>
        &bull; Native Trilingual delivery in English, Hindi, and Kannada.
      </td>
    </tr>
    <tr>
      <td><strong>Phase 2: Institutional Pilot</strong></td>
      <td>Q3 &ndash; Q4 2026</td>
      <td>
        &bull; Deployment across 5 Ayush research universities & state institutes.<br>
        &bull; Direct feedback loop with registered patent attorneys and Vaidyas.<br>
        &bull; Automated State Biodiversity Board (SBB) ABS fee calculation module.<br>
        &bull; Expansion of individual botanical monograph index (PCIM&H Vol 1&ndash;10).
      </td>
    </tr>
    <tr>
      <td><strong>Phase 3: National Scale</strong></td>
      <td>2027 & Beyond</td>
      <td>
        &bull; Direct integration with National Ayush Mission & Indian Patent Office.<br>
        &bull; Automated weekly IPO Gazette publication webhooks.<br>
        &bull; Quantized edge SLMs (4-bit Qwen on-device models for field tablets).<br>
        &bull; Language expansion to Tamil, Telugu, Marathi, and Bengali.
      </td>
    </tr>
  </tbody>
</table>

<!-- ========================================================================= -->
<!-- SECTION 7: STAKEHOLDER BENEFICIARIES -->
<!-- ========================================================================= -->
<h2>7. Stakeholder Beneficiaries & Impact Matrix</h2>

<table class="data-table">
  <thead>
    <tr>
      <th style="width: 22%;">Beneficiary Group</th>
      <th style="width: 38%;">Core Operational Pain Point</th>
      <th style="width: 40%;">Direct Value Delivered by IP-SAKTI Sahayak</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Ayush Researchers</strong></td>
      <td>Weeks spent manually searching classical texts to verify if a plant recipe infringes Section 3(p) prior art.</td>
      <td><strong>Cuts prior-art screening from 3 weeks to &lt; 2 seconds</strong>, identifying patentable novel extracts vs classical recipes.</td>
    </tr>
    <tr>
      <td><strong>Patent Attorneys</strong></td>
      <td>Risk of hallucinated case law or outdated gazette citations in patent applications.</td>
      <td><strong>Courtroom-grade citations</strong> directly anchored to official Gazettes with verified enactment dates.</td>
    </tr>
    <tr>
      <td><strong>Herbal MSMEs & Startups</strong></td>
      <td>Costly application rejections due to lack of Rule 158-B proof or BDA Section 6 approvals.</td>
      <td><strong>Step-by-step regulatory guidance</strong> detailing ASU licensing categories and State Biodiversity Board intimations.</td>
    </tr>
    <tr>
      <td><strong>Traditional Healers & Vaidyas</strong></td>
      <td>Disenfranchised by complex English-only patent gazettes and digital databases.</td>
      <td><strong>Democratizes legal access</strong> through native Hindi and Kannada guidance explaining community IP rights.</td>
    </tr>
    <tr>
      <td><strong>Regulatory Bodies (IPO / NBA)</strong></td>
      <td>Burdened by massive backlogs of non-patentable traditional knowledge patent filings.</td>
      <td><strong>Pre-screens patent filings</strong>, filtering out frivolous traditional knowledge claims prior to official submission.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<!-- ========================================================================= -->
<!-- SECTION 8: REFERENCES & QR CODES -->
<!-- ========================================================================= -->
<div class="doc-header">
  <div>IP-SAKTI Sahayak &bull; Problem Statement SIH26045</div>
  <div>Team OUTLAWS &bull; Team ID: 146711</div>
</div>

<h1>8. Statutory References, Digital Verification & QR Codes</h1>

<p>
All legal provisions and project repositories referenced throughout this report can be verified via official portals:
</p>

<div class="qr-grid">
  <div class="qr-item">
    {f'<img src="{qr_github_b64}" alt="GitHub QR">' if qr_github_b64 else ''}
    <div class="qr-title">GitHub Repository</div>
    <div class="qr-link">github.com/Rengoku9000/Drugvista</div>
  </div>
  <div class="qr-item">
    {f'<img src="{qr_ipindia_b64}" alt="IP India QR">' if qr_ipindia_b64 else ''}
    <div class="qr-title">Patents Act (IP India)</div>
    <div class="qr-link">ipindia.gov.in</div>
  </div>
  <div class="qr-item">
    {f'<img src="{qr_nba_b64}" alt="NBA QR">' if qr_nba_b64 else ''}
    <div class="qr-title">NBA Biological Diversity</div>
    <div class="qr-link">nbaindia.org</div>
  </div>
  <div class="qr-item">
    {f'<img src="{qr_ayush_b64}" alt="Ayush QR">' if qr_ayush_b64 else ''}
    <div class="qr-title">Ministry of Ayush</div>
    <div class="qr-link">ayush.gov.in</div>
  </div>
  <div class="qr-item">
    {f'<img src="{qr_wipo_b64}" alt="WIPO QR">' if qr_wipo_b64 else ''}
    <div class="qr-title">WIPO GRATK Treaty</div>
    <div class="qr-link">wipo.int</div>
  </div>
  <div class="qr-item">
    {f'<img src="{qr_report_b64}" alt="Report QR">' if qr_report_b64 else ''}
    <div class="qr-title">Technical Audit Report</div>
    <div class="qr-link">Full Verification Specs</div>
  </div>
</div>

<h2>9. Formal Submission Declaration</h2>

<div class="callout green">
  <h4 style="color:#065F46;">DECLARATION BY TEAM OUTLAWS:</h4>
  <p style="font-size: 9.5pt; margin-bottom: 0;">
    We hereby declare that the project <strong>IP-SAKTI Sahayak</strong> submitted for <strong>Smart India Hackathon 2026</strong> under <strong>Problem Statement SIH26045</strong> represents our original architectural engineering, implementation, and empirical evaluation. The solution is fully operational, verified against 106 automated unit and regression tests, and stands ready for institutional deployment.
  </p>
</div>

<table class="meta-table" style="margin-top: 25px;">
  <tr>
    <th>Hackathon</th>
    <td><strong>Smart India Hackathon 2026 (SIH 2026)</strong></td>
  </tr>
  <tr>
    <th>Problem Statement</th>
    <td><strong>SIH26045 &bull; Student Innovation &bull; Software &bull; MedTech / Ayush / LegalTech</strong></td>
  </tr>
  <tr>
    <th>Team Name & ID</th>
    <td><strong>OUTLAWS &bull; Team ID: 146711</strong></td>
  </tr>
  <tr>
    <th>Official Codebase</th>
    <td><a href="https://github.com/Rengoku9000/Drugvista" style="color: #2563EB;">https://github.com/Rengoku9000/Drugvista</a></td>
  </tr>
</table>

<div class="doc-footer" style="margin-top: 40px;">
  <div>Smart India Hackathon 2026 &bull; Official Project Report &bull; Team OUTLAWS</div>
  <div>Generated: September 2026 &bull; TRL-6 Production Prototype</div>
</div>

</body>
</html>
"""

with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML Report written to: {HTML_OUTPUT}")

chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
file_url = "file:///" + HTML_OUTPUT.replace("\\", "/")

cmd = [
    chrome,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_OUTPUT}",
    file_url
]

print("Executing Chrome headless PDF conversion...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)

if os.path.exists(PDF_OUTPUT):
    size_kb = os.path.getsize(PDF_OUTPUT) / 1024
    print(f"SUCCESS: Generated PDF Report at: {PDF_OUTPUT} ({size_kb:.1f} KB)")
else:
    print("FAILED to create PDF output. Stderr:", res.stderr)
