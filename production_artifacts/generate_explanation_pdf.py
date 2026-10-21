"""
NetMirage: Comprehensive Project Explanation & Code Walkthrough PDF and Markdown Generator.
Course: BACSE203 P - Computer Networks Lab (Innovative Lab Assessment ELA 1.0)
Institution: Vellore Institute of Technology (VIT), Vellore
Faculty Guide: Dr. Sudha M, Professor, School of Computer Science and Engineering
Candidates:
  - Abhisumat Panda (25BYB0202)
  - Atharva Parmar (25BYB0180)
  - Manas Patel (25BYB0190)
  - Varun Agarwal (25BYB0186)
"""

import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
    Preformatted
)
from reportlab.pdfgen import canvas

# Ensure relative import works
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from explanation_data import (
    METADATA,
    CHAPTER_1,
    CHAPTER_2,
    CHAPTER_3,
    CHAPTER_4,
    CHAPTER_5,
    CHAPTER_6,
    CHAPTER_7
)

WORKSPACE_ROOT = r"c:\Users\varun\Projects\cn project"
OUTPUT_PDF = os.path.join(WORKSPACE_ROOT, "NetMirage_Project_Explanation.pdf")
OUTPUT_MD = os.path.join(WORKSPACE_ROOT, "docs", "PROJECT_EXPLANATION.md")


# -------------------------------------------------------------------------------------------------
# 1. MARKDOWN GENERATION
# -------------------------------------------------------------------------------------------------
def generate_markdown():
    print(f"[1/3] Generating Markdown Guide at: {OUTPUT_MD}")
    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    md = []

    # Title & Metadata
    md.append(f"# {METADATA['project_title']}")
    md.append(f"## {METADATA['document_title']}\n")
    md.append(f"**Course**: {METADATA['course_code']} — {METADATA['course_title']} ({METADATA['assessment_type']})  ")
    md.append(f"**Institution**: {METADATA['institution']}  ")
    md.append(f"**Department**: {METADATA['department']}  ")
    md.append(f"**Faculty Guide**: {METADATA['faculty_guide']}  \n")
    md.append("### Project Development & Research Team\n")
    md.append("| Candidate Name | Registration No. | Engineering Subsystem Focus |")
    md.append("| :--- | :--- | :--- |")
    for member in METADATA['team']:
        md.append(f"| **{member['name']}** | `{member['reg_no']}` | {member['role']} |")
    md.append("\n---\n")

    md.append("## Executive Summary\n")
    md.append(
        "This architectural guide and codebase walkthrough provides a comprehensive, dual-layer explanation "
        "of the **NetMirage Defensive Cyber-Range Platform**. Every subsystem is analyzed through three mandatory lenses:\n"
        "1. **What It Is (In Simple English)**: Plain, intuitive explanations using relatable analogies for non-specialists.\n"
        "2. **How It Works Under the Hood (Technical Deep Dive)**: Rigorous engineering, packet structures, networking protocols, state machines, and RFC specifications.\n"
        "3. **Exact Codebase Location (`file_path` + key functions)**: Exact files, classes, and function calls inside `<WORKSPACE_ROOT>/app_build/` to inspect on screen.\n"
    )
    md.append("\n---\n")

    # Chapter 1
    md.append(f"## {CHAPTER_1['title']}\n")
    md.append(f"{CHAPTER_1['intro']}\n\n")
    for sec in CHAPTER_1['sections']:
        md.append(f"### {sec['id']}: {sec['title']}\n")
        md.append(f"#### 1. What It Is (In Simple English)\n> {sec['simple']}\n\n")
        md.append(f"#### 2. How It Works Under the Hood (Technical Deep Dive)\n{sec['technical']}\n\n")
        md.append(f"#### 3. Exact Codebase Location\n- **File & Logic**: `{sec['where']}`\n\n")
        md.append("---\n")

    # Chapter 2
    md.append(f"\n## {CHAPTER_2['title']}\n")
    md.append(f"{CHAPTER_2['intro']}\n\n")
    for step in CHAPTER_2['steps']:
        md.append(f"### Stage {step['step']}: {step['name']}\n")
        md.append(f"#### 1. What It Is (In Simple English)\n> {step['simple']}\n\n")
        md.append(f"#### 2. How It Works Under the Hood (Technical Deep Dive)\n{step['technical']}\n\n")
        md.append(f"#### 3. Exact Codebase Location\n- **File & Logic**: `{step['where']}`\n\n")
        md.append("---\n")

    # Chapter 3
    md.append(f"\n## {CHAPTER_3['title']}\n")
    md.append(f"{CHAPTER_3['intro']}\n\n")
    for topic in CHAPTER_3['topics']:
        md.append(f"### {topic['id']}: {topic['title']}\n")
        md.append(f"#### 1. What It Is (In Simple English)\n> {topic['simple']}\n\n")
        md.append(f"#### 2. How It Works Under the Hood (Technical Deep Dive)\n{topic['technical']}\n\n")
        md.append(f"#### 3. Exact Codebase Location\n- **File & Logic**: `{topic['where']}`\n\n")
        md.append("---\n")

    # Chapter 4
    md.append(f"\n## {CHAPTER_4['title']}\n")
    md.append(f"{CHAPTER_4['intro']}\n\n")
    for mod in CHAPTER_4['modules']:
        md.append(f"### File: `{mod['file']}` — {mod['title']}\n")
        md.append(f"#### 1. What It Is (In Simple English)\n> {mod['simple']}\n\n")
        md.append(f"#### 2. How It Works Under the Hood (Technical Deep Dive)\n{mod['technical']}\n\n")
        md.append(f"#### 3. Exact Functions & Exports\n- **Exported Symbols**: `{mod['functions']}`\n\n")
        md.append("---\n")

    # Chapter 5
    md.append(f"\n## {CHAPTER_5['title']}\n")
    md.append(f"{CHAPTER_5['intro']}\n\n")
    md.append("### 5.1 Universal Event Envelope Contract\n")
    md.append("Every message distributed across WebSockets and persisted to SQLite conforms to this schema:\n")
    md.append("```json\n" + CHAPTER_5['envelope_example'] + "\n```\n")
    md.append("\n**Line-by-Line Attribute Breakdown:**\n")
    md.append("| Key | Type | Technical Purpose & Constraints |")
    md.append("| :--- | :--- | :--- |")
    for k, t, p in CHAPTER_5['envelope_explanation']:
        md.append(f"| `{k}` | `{t}` | {p} |")
    md.append("\n")

    md.append("### 5.2 Action Broker Execution Result Contract\n")
    md.append("The structured return payload from every allowlisted operation:\n")
    md.append("```json\n" + CHAPTER_5['broker_example'] + "\n```\n")
    md.append("\n**Line-by-Line Attribute Breakdown:**\n")
    md.append("| Key | Type | Technical Purpose & Constraints |")
    md.append("| :--- | :--- | :--- |")
    for k, t, p in CHAPTER_5['broker_explanation']:
        md.append(f"| `{k}` | `{t}` | {p} |")
    md.append("\n")

    md.append("### 5.3 The 6 Immutable Database Tables\n")
    md.append("| Table Name | Primary Key | Key Columns | Forensic Purpose |")
    md.append("| :--- | :--- | :--- | :--- |")
    for tb in CHAPTER_5['tables']:
        md.append(f"| `{tb['name']}` | `{tb['pk']}` | `{tb['columns']}` | {tb['purpose']} |")
    md.append("\n---\n")

    # Chapter 6
    md.append(f"\n## {CHAPTER_6['title']}\n")
    md.append(f"{CHAPTER_6['intro']}\n\n")
    md.append("### 6.1 Platform Launch Instructions\n")
    md.append(f"Single-command launch via PowerShell:\n```powershell\n{CHAPTER_6['startup_script_ps1']}\n```\n\n")
    md.append("Manual multi-terminal startup sequence:\n")
    for step_title, cmd in CHAPTER_6['manual_commands']:
        md.append(f"- **{step_title}**:\n  ```bash\n  {cmd}\n  ```")
    md.append("\n")

    md.append("### 6.2 Faculty Demonstration Playbook (Screen Walkthrough)\n")
    md.append("| Timestamp | Demonstration Action | Examiner Narration & What to Point Out |")
    md.append("| :--- | :--- | :--- |")
    for ts, act, narr in CHAPTER_6['demo_script']:
        md.append(f"| **{ts}** | {act} | {narr} |")
    md.append("\n")

    md.append("### 6.3 Automated Test Suite Verification\n")
    md.append(f"{CHAPTER_6['tests_summary']}\n")
    md.append(f"```bash\n{CHAPTER_6['test_command']}\n```\n\n")
    md.append("| Test Module | Tests | Verified Subsystems & Guardrails |")
    md.append("| :--- | :--- | :--- |")
    for mod, count, desc in CHAPTER_6['test_table']:
        md.append(f"| `{mod}` | **{count}** | {desc} |")
    md.append("\n---\n")

    # Chapter 7
    md.append(f"\n## {CHAPTER_7['title']}\n")
    md.append(f"{CHAPTER_7['intro']}\n\n")
    md.append("### 7.1 Non-Negotiable Security Invariants\n")
    for inv_title, inv_desc in CHAPTER_7['security_invariants']:
        md.append(f"- **{inv_title}**: {inv_desc}")
    md.append("\n")

    md.append("### 7.2 Fault Tolerance & Failure Modes\n")
    for fail_title, fail_desc in CHAPTER_7['failure_modes']:
        md.append(f"- **{fail_title}**: {fail_desc}")
    md.append("\n")

    md.append("### 7.3 Candidate Defense & Cross-Questioning Guide\n")
    for cand in CHAPTER_7['candidate_defense']:
        md.append(f"#### {cand['name']} (`{cand['reg_no']}`) — {cand['focus']}\n")
        md.append(f"- **Primary Files**: `{cand['files']}`\n")
        md.append(f"- **Viva Defense Point**: {cand['defense_topic']}\n\n")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Markdown guide successfully written ({len(md)} lines).")


# -------------------------------------------------------------------------------------------------
# 2. REPORTLAB NUMBERED CANVAS (RUNNING HEADERS & FOOTERS)
# -------------------------------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(page_count)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # Page 1: Skip running header
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#D8CCA8"))
            self.setLineWidth(0.5)
            self.line(36, 756, 576, 756)
            self.setFont("Helvetica-Bold", 7)
            self.setFillColor(colors.HexColor("#009B4D"))
            self.drawString(36, 760, "NETMIRAGE: DEFENSIVE CYBER-RANGE ARCHITECTURE & CODEBASE GUIDE")
            self.setFont("Helvetica", 7)
            self.setFillColor(colors.HexColor("#6B7280"))
            self.drawRightString(576, 760, "BACSE203 P Computer Networks Lab | VIT Vellore")

        # Running Footer (All pages)
        self.setStrokeColor(colors.HexColor("#D8CCA8"))
        self.setLineWidth(0.5)
        self.line(36, 40, 576, 40)
        self.setFont("Helvetica", 7)
        self.setFillColor(colors.HexColor("#4B5563"))
        self.drawString(36, 28, "Candidates: A. Panda (25BYB0202), A. Parmar (25BYB0180), M. Patel (25BYB0190), V. Agarwal (25BYB0186)")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica-Bold", 7)
        self.setFillColor(colors.HexColor("#111827"))
        self.drawRightString(576, 28, page_str)
        self.restoreState()


# -------------------------------------------------------------------------------------------------
# 3. PDF BUILD PIPELINE
# -------------------------------------------------------------------------------------------------
def build_pdf():
    print(f"[2/3] Compiling Publication-Grade PDF at: {OUTPUT_PDF}")
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Brand Palette
    C_IVORY = colors.HexColor("#FAF5E9")
    C_GREEN = colors.HexColor("#009B4D")
    C_TANGERINE = colors.HexColor("#FFCC00")
    C_CHARCOAL = colors.HexColor("#111827")
    C_BORDER = colors.HexColor("#D8CCA8")

    # Typography styles
    style_cover_title = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=C_CHARCOAL,
        alignment=1
    )
    style_cover_sub = ParagraphStyle(
        "CoverSub",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=C_GREEN,
        alignment=1
    )
    style_cover_meta = ParagraphStyle(
        "CoverMeta",
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#374151"),
        alignment=1
    )
    style_sec_banner = ParagraphStyle(
        "SectionBanner",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.white
    )
    style_item_title = ParagraphStyle(
        "ItemTitle",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=C_CHARCOAL,
        keepWithNext=True
    )
    style_box_header_simple = ParagraphStyle(
        "BoxHeaderSimple",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#065F46"),
        spaceAfter=1.5
    )
    style_box_text_simple = ParagraphStyle(
        "BoxTextSimple",
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor("#064E3B")
    )
    style_tech_header = ParagraphStyle(
        "TechHeader",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#374151"),
        spaceBefore=2.5,
        spaceAfter=1.5,
        keepWithNext=True
    )
    style_tech_text = ParagraphStyle(
        "TechText",
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor("#1F2937")
    )
    style_box_header_code = ParagraphStyle(
        "BoxHeaderCode",
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9,
        textColor=colors.HexColor("#334155"),
        spaceAfter=1.5
    )
    style_box_text_code = ParagraphStyle(
        "BoxTextCode",
        fontName="Courier-Bold",
        fontSize=7.2,
        leading=9.5,
        textColor=colors.HexColor("#0F172A")
    )
    style_code_block = ParagraphStyle(
        "CodeBlock",
        fontName="Courier",
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor("#111827")
    )
    style_table_header = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white
    )
    style_table_cell = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=7.2,
        leading=9.5,
        textColor=C_CHARCOAL
    )
    style_table_code = ParagraphStyle(
        "TableCode",
        fontName="Courier",
        fontSize=6.8,
        leading=9,
        textColor=C_CHARCOAL
    )

    def render_section_banner(title_text, bg_hex="#111827"):
        p = Paragraph(f"<b>{title_text.upper()}</b>", style_sec_banner)
        t = Table([[p]], colWidths=[540])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_hex)),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return t

    def render_dual_layer_card(title, simple, technical, code_ref):
        story_chunk = []
        # Title
        story_chunk.append(Paragraph(f"<b>{title}</b>", style_item_title))
        story_chunk.append(Spacer(1, 2))

        # Box 1: Simple Explanation (Plain English)
        box1_content = [
            [Paragraph("<b>WHAT IT IS (IN SIMPLE ENGLISH):</b>", style_box_header_simple)],
            [Paragraph(simple, style_box_text_simple)]
        ]
        box1 = Table(box1_content, colWidths=[540])
        box1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#86EFAC")),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story_chunk.append(box1)
        story_chunk.append(Spacer(1, 3))

        # Section 2: Technical Deep Dive
        story_chunk.append(Paragraph("<b>HOW IT WORKS UNDER THE HOOD (TECHNICAL DEEP DIVE):</b>", style_tech_header))
        tech_lines = technical.split("\n")
        for line in tech_lines:
            if line.strip():
                story_chunk.append(Paragraph(line.strip(), style_tech_text))
                story_chunk.append(Spacer(1, 1))
        story_chunk.append(Spacer(1, 2.5))

        # Box 3: Code Location
        box3_content = [
            [Paragraph("<b>EXACT CODEBASE LOCATION (FILE PATH & KEY FUNCTIONS):</b>", style_box_header_code)],
            [Paragraph(code_ref, style_box_text_code)]
        ]
        box3 = Table(box3_content, colWidths=[540])
        box3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story_chunk.append(box3)
        story_chunk.append(Spacer(1, 5))
        story_chunk.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB"), spaceAfter=5))
        return story_chunk

    story = []

    # ---------------------------------------------------------------------------------------------
    # COVER / HEADER BANNER
    # ---------------------------------------------------------------------------------------------
    cover_box = [
        [Paragraph(f"<b>{METADATA['project_title'].upper()}</b>", style_cover_title)],
        [Paragraph("<b>COMPREHENSIVE ARCHITECTURE GUIDE, CODE WALKTHROUGH & DEFENSE PLAYBOOK</b>", style_cover_sub)],
        [Paragraph(
            f"<b>Course:</b> {METADATA['course_code']} — {METADATA['course_title']} ({METADATA['assessment_type']}) &nbsp;|&nbsp; "
            f"<b>Institution:</b> {METADATA['institution']}<br/>"
            f"<b>Faculty Guide:</b> {METADATA['faculty_guide']}<br/>"
            f"<b>Team:</b> Abhisumat Panda (25BYB0202), Atharva Parmar (25BYB0180), Manas Patel (25BYB0190), Varun Agarwal (25BYB0186)",
            style_cover_meta
        )]
    ]
    cover_table = Table(cover_box, colWidths=[540])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_IVORY),
        ('BOX', (0, 0), (-1, -1), 1.25, C_CHARCOAL),
        ('LINEBELOW', (0, 0), (-1, 0), 0.75, C_GREEN),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------------------------------------------
    # CHAPTER 1: THE BIG PICTURE
    # ---------------------------------------------------------------------------------------------
    story.append(render_section_banner(CHAPTER_1['title'], bg_hex="#111827"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>{CHAPTER_1['intro']}</i>", style_tech_text))
    story.append(Spacer(1, 5))

    for sec in CHAPTER_1['sections']:
        for fl in render_dual_layer_card(f"{sec['id']}: {sec['title']}", sec['simple'], sec['technical'], sec['where']):
            story.append(fl)

    # ---------------------------------------------------------------------------------------------
    # CHAPTER 2: END-TO-END LIFECYCLE
    # ---------------------------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(render_section_banner(CHAPTER_2['title'], bg_hex="#009B4D"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>{CHAPTER_2['intro']}</i>", style_tech_text))
    story.append(Spacer(1, 5))

    for step in CHAPTER_2['steps']:
        title = f"STAGE {step['step']}: {step['name'].upper()}"
        for fl in render_dual_layer_card(title, step['simple'], step['technical'], step['where']):
            story.append(fl)

    # ---------------------------------------------------------------------------------------------
    # CHAPTER 3: COMPUTER NETWORKS CONCEPTS
    # ---------------------------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(render_section_banner(CHAPTER_3['title'], bg_hex="#111827"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>{CHAPTER_3['intro']}</i>", style_tech_text))
    story.append(Spacer(1, 5))

    for topic in CHAPTER_3['topics']:
        for fl in render_dual_layer_card(f"{topic['id']}: {topic['title']}", topic['simple'], topic['technical'], topic['where']):
            story.append(fl)

    # ---------------------------------------------------------------------------------------------
    # CHAPTER 4: CODEBASE TOUR
    # ---------------------------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(render_section_banner(CHAPTER_4['title'], bg_hex="#009B4D"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>{CHAPTER_4['intro']}</i>", style_tech_text))
    story.append(Spacer(1, 5))

    for mod in CHAPTER_4['modules']:
        title = f"{mod['file']} — {mod['title']}"
        code_ref = f"Exports: {mod['functions']}"
        for fl in render_dual_layer_card(title, mod['simple'], mod['technical'], code_ref):
            story.append(fl)

    # ---------------------------------------------------------------------------------------------
    # CHAPTER 5: DATA CONTRACTS & SCHEMAS
    # ---------------------------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(render_section_banner(CHAPTER_5['title'], bg_hex="#111827"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>{CHAPTER_5['intro']}</i>", style_tech_text))
    story.append(Spacer(1, 5))

    story.append(Paragraph("<b>5.1 UNIVERSAL EVENT ENVELOPE JSON SCHEMA</b>", style_item_title))
    story.append(Spacer(1, 2))
    story.append(Preformatted(CHAPTER_5['envelope_example'], style_code_block))
    story.append(Spacer(1, 4))

    env_table_data = [[
        Paragraph("<b>Key</b>", style_table_header),
        Paragraph("<b>Type</b>", style_table_header),
        Paragraph("<b>Technical Purpose & Constraints</b>", style_table_header)
    ]]
    for k, t, p in CHAPTER_5['envelope_explanation']:
        env_table_data.append([
            Paragraph(f"<b>{k}</b>", style_table_code),
            Paragraph(t, style_table_cell),
            Paragraph(p, style_table_cell)
        ])
    env_table = Table(env_table_data, colWidths=[90, 95, 355])
    env_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_CHARCOAL),
        ('BOX', (0, 0), (-1, -1), 0.75, C_CHARCOAL),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(env_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>5.2 ACTION BROKER RESULT JSON SCHEMA</b>", style_item_title))
    story.append(Spacer(1, 2))
    story.append(Preformatted(CHAPTER_5['broker_example'], style_code_block))
    story.append(Spacer(1, 4))

    broker_table_data = [[
        Paragraph("<b>Key</b>", style_table_header),
        Paragraph("<b>Type</b>", style_table_header),
        Paragraph("<b>Technical Purpose & Constraints</b>", style_table_header)
    ]]
    for k, t, p in CHAPTER_5['broker_explanation']:
        broker_table_data.append([
            Paragraph(f"<b>{k}</b>", style_table_code),
            Paragraph(t, style_table_cell),
            Paragraph(p, style_table_cell)
        ])
    broker_table = Table(broker_table_data, colWidths=[90, 95, 355])
    broker_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_CHARCOAL),
        ('BOX', (0, 0), (-1, -1), 0.75, C_CHARCOAL),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(broker_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>5.3 THE 6 IMMUTABLE DATABASE TABLES</b>", style_item_title))
    story.append(Spacer(1, 2))
    db_table_data = [[
        Paragraph("<b>Table Name</b>", style_table_header),
        Paragraph("<b>Primary Key</b>", style_table_header),
        Paragraph("<b>Columns</b>", style_table_header),
        Paragraph("<b>Forensic Purpose</b>", style_table_header)
    ]]
    for tb in CHAPTER_5['tables']:
        db_table_data.append([
            Paragraph(f"<b>{tb['name']}</b>", style_table_code),
            Paragraph(tb['pk'], style_table_cell),
            Paragraph(tb['columns'], style_table_code),
            Paragraph(tb['purpose'], style_table_cell)
        ])
    db_table = Table(db_table_data, colWidths=[80, 80, 175, 205])
    db_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_CHARCOAL),
        ('BOX', (0, 0), (-1, -1), 0.75, C_CHARCOAL),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(db_table)

    # ---------------------------------------------------------------------------------------------
    # CHAPTER 6: HOW TO RUN, DEMO & TEST
    # ---------------------------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(render_section_banner(CHAPTER_6['title'], bg_hex="#009B4D"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>{CHAPTER_6['intro']}</i>", style_tech_text))
    story.append(Spacer(1, 5))

    story.append(Paragraph("<b>6.1 PLATFORM STARTUP COMMANDS</b>", style_item_title))
    story.append(Spacer(1, 2))
    story.append(Paragraph(f"<b>Single-Command PowerShell Launcher:</b>", style_tech_header))
    story.append(Preformatted(CHAPTER_6['startup_script_ps1'], style_code_block))
    story.append(Spacer(1, 3))

    cmd_table_data = [[
        Paragraph("<b>Startup Step</b>", style_table_header),
        Paragraph("<b>Exact Command Execution</b>", style_table_header)
    ]]
    for s_title, cmd in CHAPTER_6['manual_commands']:
        cmd_table_data.append([
            Paragraph(f"<b>{s_title}</b>", style_table_cell),
            Paragraph(cmd, style_table_code)
        ])
    cmd_table = Table(cmd_table_data, colWidths=[140, 400])
    cmd_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_CHARCOAL),
        ('BOX', (0, 0), (-1, -1), 0.75, C_CHARCOAL),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(cmd_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>6.2 FACULTY DEMONSTRATION PLAYBOOK</b>", style_item_title))
    story.append(Spacer(1, 2))
    demo_table_data = [[
        Paragraph("<b>Time</b>", style_table_header),
        Paragraph("<b>Demonstration Action</b>", style_table_header),
        Paragraph("<b>What to Say & Point Out on Screen</b>", style_table_header)
    ]]
    for ts, act, narr in CHAPTER_6['demo_script']:
        demo_table_data.append([
            Paragraph(f"<b>{ts}</b>", style_table_code),
            Paragraph(f"<b>{act}</b>", style_table_cell),
            Paragraph(narr, style_table_cell)
        ])
    demo_table = Table(demo_table_data, colWidths=[75, 140, 325])
    demo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_CHARCOAL),
        ('BOX', (0, 0), (-1, -1), 0.75, C_CHARCOAL),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(demo_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>6.3 AUTOMATED TEST SUITE (24 VERIFIED TESTS)</b>", style_item_title))
    story.append(Spacer(1, 2))
    story.append(Preformatted(CHAPTER_6['test_command'], style_code_block))
    story.append(Spacer(1, 3))
    test_table_data = [[
        Paragraph("<b>Test Module</b>", style_table_header),
        Paragraph("<b>Tests</b>", style_table_header),
        Paragraph("<b>Verified Subsystems & Safety Boundaries</b>", style_table_header)
    ]]
    for t_mod, t_cnt, t_desc in CHAPTER_6['test_table']:
        test_table_data.append([
            Paragraph(f"<b>{t_mod}</b>", style_table_code),
            Paragraph(f"<b>{t_cnt}</b>", style_table_cell),
            Paragraph(t_desc, style_table_cell)
        ])
    test_table = Table(test_table_data, colWidths=[150, 60, 330])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_CHARCOAL),
        ('BOX', (0, 0), (-1, -1), 0.75, C_CHARCOAL),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(test_table)

    # ---------------------------------------------------------------------------------------------
    # CHAPTER 7: SECURITY INVARIANTS, FAILURE MODES & VIVA DEFENSE
    # ---------------------------------------------------------------------------------------------
    story.append(PageBreak())
    story.append(render_section_banner(CHAPTER_7['title'], bg_hex="#111827"))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<i>{CHAPTER_7['intro']}</i>", style_tech_text))
    story.append(Spacer(1, 5))

    story.append(Paragraph("<b>7.1 NON-NEGOTIABLE SECURITY INVARIANTS</b>", style_item_title))
    for inv_title, inv_desc in CHAPTER_7['security_invariants']:
        p = Paragraph(f"• <b>{inv_title}</b>: {inv_desc}", style_tech_text)
        story.append(p)
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>7.2 SYSTEM FAULT TOLERANCE & FAILURE MODES</b>", style_item_title))
    for fail_title, fail_desc in CHAPTER_7['failure_modes']:
        p = Paragraph(f"• <b>{fail_title}</b>: {fail_desc}", style_tech_text)
        story.append(p)
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>7.3 CANDIDATE DEFENSE MATRIX (EXAMINER CROSS-QUESTIONING)</b>", style_item_title))
    story.append(Spacer(1, 2))
    cand_table_data = [[
        Paragraph("<b>Candidate Name</b>", style_table_header),
        Paragraph("<b>Subsystem Focus</b>", style_table_header),
        Paragraph("<b>Core Files to Open</b>", style_table_header),
        Paragraph("<b>Technical Defense Point for Examiner</b>", style_table_header)
    ]]
    for cand in CHAPTER_7['candidate_defense']:
        cand_table_data.append([
            Paragraph(f"<b>{cand['name']}</b><br/><font size='6' color='#6B7280'>({cand['reg_no']})</font>", style_table_cell),
            Paragraph(cand['focus'], style_table_cell),
            Paragraph(cand['files'], style_table_code),
            Paragraph(cand['defense_topic'], style_table_cell)
        ])
    cand_table = Table(cand_table_data, colWidths=[100, 110, 130, 200])
    cand_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_CHARCOAL),
        ('BOX', (0, 0), (-1, -1), 0.75, C_CHARCOAL),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(cand_table)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully compiled at: {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_markdown()
    build_pdf()
    print("NetMirage Project Explanation and Code Walkthrough generated successfully!")
