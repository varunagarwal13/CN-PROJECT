"""
Comprehensive Viva Prep Guide & PDF Generator for NetMirage.
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
    HRFlowable
)
from reportlab.pdfgen import canvas

# Import structured data
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from viva_data import (
    METADATA,
    SECTION_1_QUESTIONS,
    SECTION_2_QUESTIONS,
    END_TO_END_STEPS,
    CHEAT_SHEET_ROWS
)

WORKSPACE_ROOT = r"c:\Users\varun\Projects\cn project"
OUTPUT_PDF = os.path.join(WORKSPACE_ROOT, "NetMirage_Viva_Guide.pdf")
OUTPUT_MD = os.path.join(WORKSPACE_ROOT, "docs", "VIVA_PREP_GUIDE.md")

# ---------------------------------------------------------
# 1. MARKDOWN GENERATION
# ---------------------------------------------------------
def generate_markdown():
    print(f"Generating Markdown guide at: {OUTPUT_MD}")
    md = []
    md.append(f"# NetMirage: Comprehensive Lab Viva & Technical Defense Guide")
    md.append(f"**Course**: {METADATA['course_code']} — {METADATA['course_title']} ({METADATA['assessment_type']})  ")
    md.append(f"**Institution**: {METADATA['institution']}  ")
    md.append(f"**Department**: {METADATA['department']}  ")
    md.append(f"**Faculty Guide**: {METADATA['faculty_guide']}  ")
    md.append(f"**Project**: {METADATA['project_title']}  ")
    md.append(f"**Candidates**:\n")
    for c in METADATA['candidates']:
        md.append(f"- **{c['name']}** (`{c['reg_no']}`)")
    md.append("\n---\n")

    md.append("## Executive Summary & Examination Alignment\n")
    md.append("This technical viva preparation guide establishes a 100% rigorous, bidirectional mapping between the **BACSE203 Computer Networks Lab Syllabus** (Modules 1–6 and Indicative Experiments) and the **NetMirage Cyber-Range Architecture** (`app_build/`).\n")
    md.append("Every question is structured in an intuitive, examiner-focused 3-part answer format:\n")
    md.append("1. **Simple Explanation (In Plain English)**: A crisp 2-sentence intuitive explanation free of heavy jargon.\n")
    md.append("2. **Detailed Technical Breakdown**: Rigorous networking theory, packet headers, bit flags, handshakes, subnet math, and RFC protocols.\n")
    md.append("3. **Where It Is in NetMirage (`file_path` & function)**: Exact code location in `app_build/` to open and show the professor on screen.\n")
    md.append("\n---\n")

    # Section 1
    md.append(f"## SECTION 1: SYLLABUS-MAPPED NETWORKING QUESTIONS ({len(SECTION_1_QUESTIONS)} Questions)\n")
    for q in SECTION_1_QUESTIONS:
        md.append(f"### Q{q['id']}: {q['title']}\n")
        md.append(f"**Syllabus Topic**: `{q['module']}`\n\n")
        md.append(f"> **Simple Explanation (In Plain English)**:  \n> {q['simple']}\n\n")
        md.append(f"**Detailed Technical Breakdown**:  \n{q['technical']}\n\n")
        md.append(f"**Where It Is in NetMirage (`file_path` & function)**:  \n- **File & Function**: `{q['where']}`\n\n")
        md.append("---\n")

    # Section 2
    md.append(f"\n## SECTION 2: PROJECT ARCHITECTURE & SECURITY DEFENSE QUESTIONS ({len(SECTION_2_QUESTIONS)} Questions)\n")
    for q in SECTION_2_QUESTIONS:
        md.append(f"### Q{q['id']}: {q['title']}\n")
        md.append(f"**Focus Area**: `{q['module']}`\n\n")
        md.append(f"> **Simple Explanation (In Plain English)**:  \n> {q['simple']}\n\n")
        md.append(f"**Detailed Technical Breakdown**:  \n{q['technical']}\n\n")
        md.append(f"**Where It Is in NetMirage (`file_path` & function)**:  \n- **File & Function**: `{q['where']}`\n\n")
        md.append("---\n")

    # Section 3
    md.append(f"\n## SECTION 3: END-TO-END EXECUTION FLOW WALKTHROUGH ({len(END_TO_END_STEPS)} Steps)\n")
    md.append("A complete 18-step sequential trace from the instant the operator clicks `START RUN` on the tactile dashboard to live WebSocket event delivery:\n\n")
    for s in END_TO_END_STEPS:
        md.append(f"### Step {s['step']}: {s['name']}\n")
        md.append(f"- **Primary Component**: `{s['component']}`\n")
        md.append(f"- **Trigger / Action**: {s['action']}\n")
        md.append(f"- **Technical Operation**: {s['detail']}\n\n")

    md.append("---\n")

    # Section 4
    md.append("\n## SECTION 4: QUICK CODE-NAVIGATION CHEAT SHEET TABLE\n")
    md.append("| Candidate | Topic Examiner Asks About | Exact File Path to Open | Function / Class Name | What to Point Out on Screen |\n")
    md.append("| :--- | :--- | :--- | :--- | :--- |\n")
    for r in CHEAT_SHEET_ROWS:
        md.append(f"| **{r.get('candidate', 'Team')}** | **{r['topic']}** | `{r['file']}` | `{r['function']}` | {r['point_out']} |\n")

    md_content = "\n".join(md)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Markdown guide written successfully ({len(md_content)} bytes).")

# ---------------------------------------------------------
# 2. PDF GENERATION VIA REPORTLAB
# ---------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#4B5563"))

        # Top running header
        self.drawString(36, 756, "BACSE203 P: Computer Networks Lab | NetMirage Viva Defense Guide")
        self.drawRightString(576, 756, "VIT Vellore | Dr. Sudha M")
        self.setStrokeColor(colors.HexColor("#009B4D"))
        self.setLineWidth(1)
        self.line(36, 750, 576, 750)

        # Bottom running footer
        self.setStrokeColor(colors.HexColor("#D1D5DB"))
        self.setLineWidth(0.5)
        self.line(36, 42, 576, 42)
        self.setFont("Helvetica", 7.5)
        self.drawString(36, 30, "Confidential - Academic Lab Assessment & Project Defense | Candidates: A. Panda, A. Parmar, M. Patel, V. Agarwal")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 30, page_str)
        self.restoreState()


def build_pdf():
    print(f"Generating PDF study guide at: {OUTPUT_PDF}")
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54
    )

    base_styles = getSampleStyleSheet()

    # Custom typography styles
    style_cover_title = ParagraphStyle(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#111827"),
        alignment=1
    )
    style_cover_sub = ParagraphStyle(
        "CoverSub",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#009B4D"),
        alignment=1
    )
    style_cover_meta = ParagraphStyle(
        "CoverMeta",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#374151"),
        alignment=1
    )
    style_sec_header = ParagraphStyle(
        "SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.white,
        spaceBefore=0,
        spaceAfter=0
    )
    style_q_title = ParagraphStyle(
        "QuestionTitle",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#111827"),
        keepWithNext=True
    )
    style_q_tag = ParagraphStyle(
        "QuestionTag",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#009B4D"),
        keepWithNext=True
    )
    style_box_header_simple = ParagraphStyle(
        "BoxHeaderSimple",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#047857"),
        spaceAfter=2
    )
    style_box_text_simple = ParagraphStyle(
        "BoxTextSimple",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#064E3B")
    )
    style_tech_header = ParagraphStyle(
        "TechHeader",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#374151"),
        spaceBefore=3,
        spaceAfter=2,
        keepWithNext=True
    )
    style_tech_text = ParagraphStyle(
        "TechText",
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.8,
        textColor=colors.HexColor("#1F2937")
    )
    style_code_header = ParagraphStyle(
        "CodeHeader",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=2
    )
    style_code_text = ParagraphStyle(
        "CodeText",
        fontName="Courier",
        fontSize=7.2,
        leading=9.5,
        textColor=colors.HexColor("#0F172A")
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
        leading=9.2,
        textColor=colors.HexColor("#1F2937")
    )
    style_table_code = ParagraphStyle(
        "TableCode",
        fontName="Courier",
        fontSize=6.8,
        leading=8.8,
        textColor=colors.HexColor("#111827")
    )

    story = []

    # ---------------------------------------------------------
    # COVER / HEADER CARD
    # ---------------------------------------------------------
    header_data = [
        [
            Paragraph(f"<b>VELLORE INSTITUTE OF TECHNOLOGY (VIT) VELLORE</b>", style_cover_sub),
        ],
        [
            Paragraph(f"<b>{METADATA['course_code']} -- {METADATA['course_title']} ({METADATA['assessment_type']})</b>", style_cover_title),
        ],
        [
            Paragraph(f"<b>PROJECT TITLE</b>: {METADATA['project_title']}", style_cover_meta),
        ],
        [
            Paragraph(f"<b>FACULTY GUIDE</b>: {METADATA['faculty_guide']} | <b>SCHOOL</b>: {METADATA['department']}", style_cover_meta),
        ],
        [
            Paragraph(f"<b>CANDIDATES</b>: Abhisumat Panda (25BYB0202) | Atharva Parmar (25BYB0180) | Manas Patel (25BYB0190) | Varun Agarwal (25BYB0186)", style_cover_meta),
        ]
    ]

    header_table = Table(header_data, colWidths=[540])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FAF5E9")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#009B4D")),
        ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.HexColor("#D1D5DB")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # Helper function for rendering section banners
    def render_section_banner(title_text):
        banner_data = [[Paragraph(f"<b>{title_text}</b>", style_sec_header)]]
        banner_table = Table(banner_data, colWidths=[540])
        banner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#111827")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#009B4D")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        return banner_table

    # Helper function for rendering 3-part question card
    def render_question_card(q):
        card_story = []

        # Title & Module Tag
        card_story.append(Paragraph(f"<b>TOPIC FOCUS:</b> {q['module'].upper()}", style_q_tag))
        card_story.append(Paragraph(f"<b>Q{q['id']}: {q['title']}</b>", style_q_title))
        card_story.append(Spacer(1, 3))

        # Box 1: Simple Explanation (Plain English)
        box1_content = [
            [Paragraph("<b>SIMPLE EXPLANATION (IN PLAIN ENGLISH):</b>", style_box_header_simple)],
            [Paragraph(q['simple'], style_box_text_simple)]
        ]
        box1_table = Table(box1_content, colWidths=[536])
        box1_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#86EFAC")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        card_story.append(box1_table)
        card_story.append(Spacer(1, 4))

        # Section 2: Detailed Technical Breakdown
        tech_lines = q['technical'].split("\n")
        card_story.append(Paragraph("<b>DETAILED TECHNICAL BREAKDOWN:</b>", style_tech_header))
        for line in tech_lines:
            if line.strip():
                card_story.append(Paragraph(line.strip(), style_tech_text))
                card_story.append(Spacer(1, 1.5))
        card_story.append(Spacer(1, 3))

        # Box 3: Where It Is in NetMirage (Code Reference)
        box3_content = [
            [Paragraph("<b>WHERE IT IS IN NETMIRAGE (CODE & FUNCTION REFERENCE):</b>", style_code_header)],
            [Paragraph(f"<b>Path & Logic</b>: {q['where']}", style_code_text)]
        ]
        box3_table = Table(box3_content, colWidths=[536])
        box3_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        card_story.append(box3_table)
        card_story.append(Spacer(1, 6))

        # Thin separator rule
        card_story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E5E7EB"), spaceAfter=6))

        return card_story

    # ---------------------------------------------------------
    # SECTION 1: SYLLABUS-MAPPED QUESTIONS
    # ---------------------------------------------------------
    story.append(render_section_banner(f"SECTION 1: SYLLABUS-MAPPED NETWORKING QUESTIONS ({len(SECTION_1_QUESTIONS)} QUESTIONS)"))
    story.append(Spacer(1, 8))

    for q in SECTION_1_QUESTIONS:
        flowables = render_question_card(q)
        for fl in flowables:
            story.append(fl)

    # ---------------------------------------------------------
    # SECTION 2: PROJECT ARCHITECTURE & SECURITY DEFENSE
    # ---------------------------------------------------------
    story.append(PageBreak())
    story.append(render_section_banner(f"SECTION 2: PROJECT ARCHITECTURE & SECURITY DEFENSE QUESTIONS ({len(SECTION_2_QUESTIONS)} QUESTIONS)"))
    story.append(Spacer(1, 8))

    for q in SECTION_2_QUESTIONS:
        flowables = render_question_card(q)
        for fl in flowables:
            story.append(fl)

    # ---------------------------------------------------------
    # SECTION 3: END-TO-END EXECUTION FLOW WALKTHROUGH
    # ---------------------------------------------------------
    story.append(PageBreak())
    story.append(render_section_banner(f"SECTION 3: END-TO-END EXECUTION FLOW WALKTHROUGH ({len(END_TO_END_STEPS)} STEPS)"))
    story.append(Spacer(1, 8))

    step_intro = Paragraph(
        "<b>Architectural Lifecycle</b>: The following 18-step sequential sequence traces an entire adversarial emulation run from the instant the operator initiates testing on the physical dashboard to final containment:",
        style_tech_text
    )
    story.append(step_intro)
    story.append(Spacer(1, 6))

    for s in END_TO_END_STEPS:
        step_box_data = [
            [
                Paragraph(f"<b>STEP {s['step']}: {s['name'].upper()}</b>", style_box_header_simple),
                Paragraph(f"<b>Component:</b> <font name='Courier'>{s['component']}</font>", style_q_tag)
            ],
            [
                Paragraph(f"<b>Trigger / Action:</b> {s['action']}", style_tech_text),
                Paragraph(f"<b>Operation:</b> {s['detail']}", style_tech_text)
            ]
        ]
        step_table = Table(step_box_data, colWidths=[200, 336])
        step_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FAF5E9")),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#111827")),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor("#D1D5DB")),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(step_table)
        story.append(Spacer(1, 4))

    # ---------------------------------------------------------
    # SECTION 4: QUICK CODE-NAVIGATION CHEAT SHEET TABLE
    # ---------------------------------------------------------
    story.append(PageBreak())
    story.append(render_section_banner("SECTION 4: QUICK CODE-NAVIGATION CHEAT SHEET TABLE"))
    story.append(Spacer(1, 8))

    cheat_intro = Paragraph(
        "<b>Candidate Defense Matrix</b>: Quick-reference index mapping each candidate to their core subsystem responsibilities, exact files, function names, and screen talking points during examiner cross-questioning.",
        style_tech_text
    )
    story.append(cheat_intro)
    story.append(Spacer(1, 6))

    cheat_table_data = [
        [
            Paragraph("<b>Candidate</b>", style_table_header),
            Paragraph("<b>Topic Examiner Asks About</b>", style_table_header),
            Paragraph("<b>Exact File Path to Open</b>", style_table_header),
            Paragraph("<b>Function / Class</b>", style_table_header),
            Paragraph("<b>What to Point Out on Screen</b>", style_table_header)
        ]
    ]

    for r in CHEAT_SHEET_ROWS:
        cheat_table_data.append([
            Paragraph(f"<b>{r.get('candidate', 'Team')}</b>", style_table_cell),
            Paragraph(f"<b>{r['topic']}</b>", style_table_cell),
            Paragraph(f"<font name='Courier'>{r['file']}</font>", style_table_code),
            Paragraph(f"<font name='Courier'>{r['function']}</font>", style_table_code),
            Paragraph(r['point_out'], style_table_cell)
        ])

    cheat_table = Table(cheat_table_data, colWidths=[90, 105, 115, 95, 135])
    cheat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#111827")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#111827")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(cheat_table)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully compiled at: {OUTPUT_PDF}")


if __name__ == "__main__":
    generate_markdown()
    build_pdf()
    print("All tasks completed successfully!")
