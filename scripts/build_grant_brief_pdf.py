#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


NAVY = colors.HexColor("#10243E")
DEEP = colors.HexColor("#091725")
TEAL = colors.HexColor("#19B5A5")
CYAN = colors.HexColor("#73D8D0")
AMBER = colors.HexColor("#FFB547")
INK = colors.HexColor("#172536")
MUTED = colors.HexColor("#5D6B79")
PALE = colors.HexColor("#EEF5F6")
LINE = colors.HexColor("#D7E2E7")
WHITE = colors.white


def register_fonts() -> tuple[str, str]:
    regular_candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    bold_candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    regular = next((Path(path) for path in regular_candidates if Path(path).exists()), None)
    bold = next((Path(path) for path in bold_candidates if Path(path).exists()), None)
    if regular and bold:
        pdfmetrics.registerFont(TTFont("GrantSans", str(regular)))
        pdfmetrics.registerFont(TTFont("GrantSans-Bold", str(bold)))
        return "GrantSans", "GrantSans-Bold"
    return "Helvetica", "Helvetica-Bold"


REGULAR, BOLD = register_fonts()


class AccuracyChart(Flowable):
    def __init__(self, width: float, height: float = 57 * mm):
        super().__init__()
        self.width = width
        self.height = height
        self.data = [
            ("Transformers BF16", 96.875, 84.2557, 99.4462, TEAL),
            ("GGUF BF16", 93.75, 79.8529, 98.2689, colors.HexColor("#4087A8")),
            ("GGUF Q8_0", 96.875, 84.2557, 99.4462, colors.HexColor("#3768B0")),
            ("GGUF Q4_K_M", 87.5, 71.9317, 95.0299, AMBER),
        ]

    def draw(self) -> None:
        canvas = self.canv
        label_width = 98
        plot_left = label_width + 10
        plot_right = self.width - 42
        plot_width = plot_right - plot_left
        y_top = self.height - 24
        row_gap = 30

        canvas.setFont(REGULAR, 7.5)
        canvas.setFillColor(MUTED)
        for tick in (0, 25, 50, 75, 100):
            x = plot_left + plot_width * tick / 100
            canvas.setStrokeColor(LINE)
            canvas.setLineWidth(0.5)
            canvas.line(x, 10, x, self.height - 12)
            canvas.drawCentredString(x, self.height - 8, str(tick))

        for index, (label, value, lower, upper, color) in enumerate(self.data):
            y = y_top - index * row_gap
            canvas.setFillColor(INK)
            canvas.setFont(BOLD, 8.5)
            canvas.drawRightString(label_width, y - 2, label)

            canvas.setFillColor(colors.HexColor("#E7EEF1"))
            canvas.roundRect(plot_left, y - 7, plot_width, 11, 4, fill=1, stroke=0)
            canvas.setFillColor(color)
            canvas.roundRect(
                plot_left,
                y - 7,
                plot_width * value / 100,
                11,
                4,
                fill=1,
                stroke=0,
            )

            low_x = plot_left + plot_width * lower / 100
            high_x = plot_left + plot_width * upper / 100
            canvas.setStrokeColor(INK)
            canvas.setLineWidth(1)
            canvas.line(low_x, y - 12, high_x, y - 12)
            canvas.line(low_x, y - 15, low_x, y - 9)
            canvas.line(high_x, y - 15, high_x, y - 9)
            canvas.setFillColor(INK)
            canvas.setFont(BOLD, 8)
            canvas.drawString(plot_right + 7, y - 3, f"{value:.1f}%")

        canvas.setFillColor(MUTED)
        canvas.setFont(REGULAR, 7.5)
        canvas.drawString(plot_left, 0, "Bars: exact-match rate. Whiskers: Wilson 95% confidence interval.")


class PhaseTimeline(Flowable):
    def __init__(self, width: float, height: float = 50 * mm):
        super().__init__()
        self.width = width
        self.height = height
        self.phases = [
            ("Public proof", 1, 2, TEAL),
            ("Evaluator hardening", 3, 5, colors.HexColor("#4087A8")),
            ("Quantization matrix", 6, 8, colors.HexColor("#3768B0")),
            ("Devices + attacks", 9, 11, AMBER),
            ("Evidence receipt", 12, 13, colors.HexColor("#8C6AC4")),
            ("Review + release", 14, 16, colors.HexColor("#596979")),
        ]

    def draw(self) -> None:
        canvas = self.canv
        left = 105
        right = self.width - 8
        plot_width = right - left
        row_gap = 24
        y_top = self.height - 22

        canvas.setFont(REGULAR, 7)
        canvas.setFillColor(MUTED)
        for week in range(1, 17):
            x = left + plot_width * (week - 0.5) / 16
            canvas.drawCentredString(x, self.height - 8, str(week))

        for index, (label, start, end, color) in enumerate(self.phases):
            y = y_top - index * row_gap
            canvas.setFillColor(INK)
            canvas.setFont(BOLD, 8)
            canvas.drawRightString(left - 8, y, label)
            x = left + plot_width * (start - 1) / 16
            width = plot_width * (end - start + 1) / 16
            canvas.setFillColor(color)
            canvas.roundRect(x, y - 6, width, 10, 3, fill=1, stroke=0)


def make_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle(
            "cover_kicker",
            parent=sample["Normal"],
            fontName=BOLD,
            fontSize=10,
            leading=13,
            textColor=CYAN,
            spaceAfter=8,
        ),
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=sample["Title"],
            fontName=BOLD,
            fontSize=31,
            leading=34,
            textColor=WHITE,
            alignment=TA_LEFT,
            spaceAfter=14,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            parent=sample["Normal"],
            fontName=REGULAR,
            fontSize=14,
            leading=20,
            textColor=colors.HexColor("#DDEAF0"),
            spaceAfter=20,
        ),
        "cover_small": ParagraphStyle(
            "cover_small",
            parent=sample["Normal"],
            fontName=REGULAR,
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#B9CBD4"),
        ),
        "title": ParagraphStyle(
            "title",
            parent=sample["Heading1"],
            fontName=BOLD,
            fontSize=21,
            leading=25,
            textColor=NAVY,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=sample["Heading2"],
            fontName=BOLD,
            fontSize=12.5,
            leading=16,
            textColor=NAVY,
            spaceBefore=7,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "body",
            parent=sample["BodyText"],
            fontName=REGULAR,
            fontSize=9.3,
            leading=13.5,
            textColor=INK,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "small",
            parent=sample["BodyText"],
            fontName=REGULAR,
            fontSize=7.8,
            leading=10.5,
            textColor=MUTED,
            spaceAfter=3,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=sample["BodyText"],
            fontName=REGULAR,
            fontSize=9,
            leading=13,
            textColor=INK,
            leftIndent=12,
            firstLineIndent=-7,
            bulletIndent=0,
            spaceAfter=4,
        ),
        "callout": ParagraphStyle(
            "callout",
            parent=sample["BodyText"],
            fontName=BOLD,
            fontSize=10.2,
            leading=14,
            textColor=NAVY,
        ),
        "table": ParagraphStyle(
            "table",
            parent=sample["BodyText"],
            fontName=REGULAR,
            fontSize=7.7,
            leading=10,
            textColor=INK,
        ),
        "table_bold": ParagraphStyle(
            "table_bold",
            parent=sample["BodyText"],
            fontName=BOLD,
            fontSize=7.7,
            leading=10,
            textColor=INK,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            parent=sample["BodyText"],
            fontName=BOLD,
            fontSize=7.7,
            leading=10,
            textColor=WHITE,
        ),
        "center_small": ParagraphStyle(
            "center_small",
            parent=sample["BodyText"],
            fontName=REGULAR,
            fontSize=7.8,
            leading=10,
            alignment=TA_CENTER,
            textColor=MUTED,
        ),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def bullet(text: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(f"<bullet>&bull;</bullet>{text}", styles["bullet"])


def card(text: str, style: ParagraphStyle, background: colors.Color = PALE) -> Table:
    table = Table([[p(text, style)]], colWidths=[170 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 11),
                ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def metric_cards(styles: dict[str, ParagraphStyle]) -> Table:
    items = [
        ("31/32", "BF16 + Q8_0 exact match"),
        ("0/256", "Decoy matches in each condition"),
        ("0.99 GB", "Q4_K_M artifact"),
    ]
    cells = []
    for value, label in items:
        cells.append(
            p(
                f'<font name="{BOLD}" size="19" color="#73D8D0">{value}</font><br/>'
                f'<font name="{REGULAR}" size="8" color="#DDEAF0">{label}</font>',
                styles["cover_small"],
            )
        )
    table = Table([cells], colWidths=[55 * mm] * 3, rowHeights=[28 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#163653")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#31526C")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#31526C")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def results_table(styles: dict[str, ParagraphStyle]) -> Table:
    rows = [
        ["Condition", "Size", "Exact", "Rate", "Wilson 95% CI"],
        ["Transformers BF16", "3.09 GB", "31/32", "96.88%", "84.26%-99.45%"],
        ["GGUF BF16", "3.09 GB", "30/32", "93.75%", "79.85%-98.27%"],
        ["GGUF Q8_0", "1.65 GB", "31/32", "96.88%", "84.26%-99.45%"],
        ["GGUF Q4_K_M", "0.99 GB", "28/32", "87.50%", "71.93%-95.03%"],
    ]
    styled = []
    for row_index, row in enumerate(rows):
        row_style = styles["table_header"] if row_index == 0 else styles["table"]
        styled.append([p(cell, row_style) for cell in row])
    table = Table(styled, colWidths=[48 * mm, 23 * mm, 21 * mm, 23 * mm, 38 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def budget_table(styles: dict[str, ParagraphStyle]) -> Table:
    rows = [
        ("Research and engineering", "$25,000", "Harness, devices, report"),
        ("Reproducible compute", "$7,000", "Six checkpoints + reruns"),
        ("Physical test devices", "$5,000", "Two Android classes"),
        ("Independent review", "$5,000", "Security + statistical methods"),
        ("Documentation + release", "$3,000", "Guides, demo, community"),
        ("Hosting + CI", "$2,000", "Artifacts and runners"),
        ("Contingency", "$3,000", "Failed runs and format changes"),
        ("Total", "$50,000", "16-week public build"),
    ]
    data = [[p("Category", styles["table_header"]), p("Amount", styles["table_header"]), p("Purpose", styles["table_header"])]]
    for category, amount, purpose in rows:
        row_style = styles["table_bold"] if category == "Total" else styles["table"]
        data.append([p(category, row_style), p(amount, row_style), p(purpose, row_style)])
    table = Table(data, colWidths=[58 * mm, 28 * mm, 76 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [WHITE, PALE]),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DCEFED")),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def assurance_table(styles: dict[str, ParagraphStyle]) -> Table:
    rows = [
        ("L0", "Self-declared", "Signed artifact and policy hashes", "No proof the hashed model ran"),
        ("L1", "Device-attested", "Hardware-backed receipt key", "Still trusts user-space measurement"),
        ("L2", "Measured load", "Trusted model/runtime measurement", "Requires platform or OEM integration"),
        ("L3", "Protected execution", "Attested inference or proof", "Out of scope for first grant"),
    ]
    data = [[p(value, styles["table_header"]) for value in ("Level", "Identity", "Adds", "Honest boundary")]]
    for row in rows:
        data.append([p(value, styles["table"] if index else styles["table_bold"]) for index, value in enumerate(row)])
    table = Table(data, colWidths=[14 * mm, 34 * mm, 56 * mm, 58 * mm], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
                ("GRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def page_background(canvas, doc) -> None:
    page = canvas.getPageNumber()
    width, height = A4
    canvas.saveState()
    if page == 1:
        canvas.setFillColor(DEEP)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.rect(0, height - 9 * mm, width, 9 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor("#15344E"))
        canvas.circle(width + 5 * mm, 35 * mm, 70 * mm, fill=1, stroke=0)
    else:
        canvas.setFillColor(WHITE)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        canvas.setStrokeColor(TEAL)
        canvas.setLineWidth(2)
        canvas.line(20 * mm, height - 17 * mm, 42 * mm, height - 17 * mm)
        canvas.setFont(BOLD, 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(20 * mm, height - 13 * mm, "EDGEOML / SENTIENT GRANT BRIEF")
        canvas.setFont(REGULAR, 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(width - 20 * mm, 12 * mm, f"{page - 1} / 4")
        canvas.drawString(20 * mm, 12 * mm, "Preliminary pilot - not an upstream OML reproduction")
    canvas.restoreState()


def build_pdf(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    width, height = A4
    frame = Frame(20 * mm, 18 * mm, width - 40 * mm, height - 36 * mm, id="main")
    template = PageTemplate(id="all", frames=[frame], onPage=page_background)
    doc = BaseDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="EdgeOML - Sentient Open Source AGI Grant Brief",
        author="EdgeOML",
        subject="On-device OML fingerprint robustness benchmark and evidence receipts",
    )
    doc.addPageTemplates([template])

    story = []

    # Cover
    story.extend(
        [
            Spacer(1, 36 * mm),
            p("OPEN SOURCE AGI GRANT / $50,000 / 16 WEEKS", styles["cover_kicker"]),
            p("EdgeOML", styles["cover_title"]),
            p(
                "Measuring whether model fingerprints survive conversion, quantization, "
                "and deployment on hardware people actually own.",
                styles["cover_subtitle"],
            ),
            Spacer(1, 7 * mm),
            metric_cards(styles),
            Spacer(1, 13 * mm),
            p(
                '<font name="%s" color="#FFB547">Thesis.</font> Open models become truly accessible '
                "when they run locally. Their identity evidence must survive the same deployment "
                "pipeline." % BOLD,
                ParagraphStyle(
                    "cover_thesis",
                    parent=styles["cover_subtitle"],
                    fontSize=12,
                    leading=17,
                ),
            ),
            Spacer(1, 12 * mm),
            p(
                "Technical demo complete on Apple M4 / 16 GiB<br/>"
                "Public repository: github.com/hex-aragon/edgeoml<br/>"
                "Prepared 03 September 2026",
                styles["cover_small"],
            ),
            PageBreak(),
        ]
    )

    # Page 2
    story.extend(
        [
            p("1. The missing deployment evidence", styles["title"]),
            p(
                "Sentient's public OML implementation establishes a key-response model "
                "fingerprinting workflow. Real on-device deployment then changes format, runtime, "
                "prompt handling, and numeric precision. Today, a failed fingerprint check cannot "
                "cleanly identify which transformation caused the failure.",
                styles["body"],
            ),
            Spacer(1, 2 * mm),
            card(
                "<b>Core question</b><br/>Does an OML-fingerprinted open model remain identifiable "
                "after HF-to-GGUF conversion and practical 8/6/5/4/3/2-bit quantization on laptops "
                "and phones?",
                styles["callout"],
            ),
            Spacer(1, 5 * mm),
            p("The controlled comparison", styles["h2"]),
            Table(
                [
                    [p("HF BF16", styles["table_bold"]), p("->", styles["center_small"]), p("GGUF BF16", styles["table_bold"]), p("Isolates conversion, runtime, and template effects", styles["table"])],
                    [p("GGUF BF16", styles["table_bold"]), p("->", styles["center_small"]), p("GGUF Q4", styles["table_bold"]), p("Isolates quantization effects", styles["table"])],
                ],
                colWidths=[30 * mm, 12 * mm, 34 * mm, 88 * mm],
                style=TableStyle(
                    [
                        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [PALE, WHITE]),
                        ("GRID", (0, 0), (-1, -1), 0.6, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (1, 0), (1, -1), "CENTER"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                ),
            ),
            Spacer(1, 5 * mm),
            p("Why this fits Sentient", styles["h2"]),
            bullet("<b>Personal on-device AI:</b> evaluates models on inexpensive consumer hardware.", styles),
            bullet("<b>Proof that a model is what it claims:</b> measures lineage separately from artifact identity.", styles),
            bullet("<b>Agent identity:</b> binds model, runtime, policy, tools, request, and response in an evidence receipt.", styles),
            bullet("<b>Privacy by default:</b> supports local inference while documenting what is and is not attested.", styles),
            Spacer(1, 4 * mm),
            p("Claims we deliberately avoid", styles["h2"]),
            bullet("A signed model hash is not proof that those weights performed the inference.", styles),
            bullet("A fingerprint is not unremovable; we will publish removal cost versus utility damage.", styles),
            bullet("OML does not make payment unbreakable on a fully user-controlled offline device.", styles),
            PageBreak(),
        ]
    )

    # Page 3
    story.extend(
        [
            p("2. A real pre-grant pilot", styles["title"]),
            p(
                "We completed the minimum technical gate on an Apple M4 with 16 GiB unified "
                "memory. A pinned Apache-2.0 Qwen2.5 1.5B model received 32 synthetic one-token "
                "key-response fingerprints through rank-16 LoRA, was fused, converted to GGUF "
                "BF16, and quantized to Q8_0 and Q4_K_M.",
                styles["body"],
            ),
            AccuracyChart(170 * mm),
            Spacer(1, 2 * mm),
            results_table(styles),
            Spacer(1, 5 * mm),
            Table(
                [
                    [p('<font color="#19B5A5"><b>0 / 256</b></font><br/>Assigned decoy matches in every deployment condition<br/><font size="7">Wilson 95% upper bound: 1.48%</font>', styles["body"]),
                     p('<font color="#19B5A5"><b>0 / 32</b></font><br/>Original-model accidental matches<br/><font size="7">Wilson 95% upper bound: 10.72%</font>', styles["body"])],
                ],
                colWidths=[84 * mm, 84 * mm],
                style=TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), PALE),
                        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]
                ),
            ),
            Spacer(1, 4 * mm),
            p("Reproducibility evidence", styles["h2"]),
            bullet("1,184 raw JSONL prediction records and generated Wilson intervals.", styles),
            bullet("Pinned model, llama.cpp, OML audit revision, package versions, seed, and commands.", styles),
            bullet("SHA-256 verification for base, adapter, fused, BF16, Q8_0, and Q4_K_M artifacts.", styles),
            bullet("The failed 640-update checkpoint (7/32) is retained rather than hidden.", styles),
            p(
                "Boundary: this is an OML-style MLX LoRA feasibility run, not a reproduction of "
                "Sentient's full OML fine-tuning method. The funded work closes that gap.",
                ParagraphStyle("boundary", parent=styles["small"], textColor=colors.HexColor("#8A5A16")),
            ),
            PageBreak(),
        ]
    )

    # Page 4
    story.extend(
        [
            p("3. What $50,000 unlocks", styles["title"]),
            p(
                "The pilot answers whether the idea is technically credible. The grant funds the "
                "replication, device diversity, removal attacks, and independent scrutiny required "
                "to turn one result into public infrastructure.",
                styles["body"],
            ),
            PhaseTimeline(170 * mm),
            Spacer(1, 3 * mm),
            p("16-week acceptance targets", styles["h2"]),
            bullet("Two Apache-2.0 model families x three seeds x full practical quantization matrix.", styles),
            bullet("144 primary inference cells, each with a manifest, hash, raw records, and result or documented failure.", styles),
            bullet("Apple reference hardware plus mid-range and flagship Android device measurements.", styles),
            bullet("Repeated quantization and fine-tuning removal experiments with utility-damage curves.", styles),
            bullet("L0 receipt schema and Android L1 device-attested prototype, with independent review.", styles),
            Spacer(1, 4 * mm),
            p("Budget", styles["h2"]),
            budget_table(styles),
            Spacer(1, 4 * mm),
            card(
                "If Sentient provides compute credits, cash compute savings will be redirected to "
                "more negative controls, a third low-cost Android device, and additional independent review.",
                styles["body"],
                colors.HexColor("#FFF5E4"),
            ),
            PageBreak(),
        ]
    )

    # Page 5
    story.extend(
        [
            p("4. Trust framework and path to adoption", styles["title"]),
            p(
                "EdgeOML keeps model lineage, artifact identity, agent identity, and execution "
                "integrity separate. One signature cannot honestly answer all four questions.",
                styles["body"],
            ),
            assurance_table(styles),
            Spacer(1, 4 * mm),
            p("Commercial validation after the grant", styles["h2"]),
            p(
                "A privacy-first shopping agent will keep preferences, budgets, purchase history, "
                "and risk rules on-device. Recommendation receipts can disclose the model and "
                "quantization, policy version, offers considered, affiliate commission, selected "
                "item, and whether user constraints were satisfied. Commission neutrality becomes "
                "a measurable product trust metric, not a marketing promise.",
                styles["body"],
            ),
            card(
                "<b>Capital path</b><br/>$50k open-source grant -> OML deployment evidence -> "
                "OEM/TEE measured-load research -> on-device shopping pilot -> investment track "
                "with usage, savings, conversion, and bias metrics.",
                styles["callout"],
            ),
            Spacer(1, 5 * mm),
            p("Immediate submission status", styles["h2"]),
            bullet("Technical pilot and local evidence package: complete.", styles),
            bullet("Public repository and stable demo URL: github.com/hex-aragon/edgeoml.", styles),
            bullet("Application request: Open Source AGI Grant Track, $50,000, 16 weeks.", styles),
            Spacer(1, 5 * mm),
            p("Primary sources", styles["h2"]),
            p(
                '<link href="https://sentient.foundation/grants" color="#3768B0">sentient.foundation/grants</link> - program scope<br/>'
                '<link href="https://github.com/sentient-agi/OML-1.0-Fingerprinting" color="#3768B0">github.com/sentient-agi/OML-1.0-Fingerprinting</link> - public OML implementation<br/>'
                '<link href="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct" color="#3768B0">huggingface.co/Qwen/Qwen2.5-1.5B-Instruct</link> - Apache-2.0 base model<br/>'
                '<link href="https://github.com/ml-explore/mlx-lm" color="#3768B0">github.com/ml-explore/mlx-lm</link> - Apple Silicon LoRA runtime<br/>'
                '<link href="https://github.com/ggml-org/llama.cpp" color="#3768B0">github.com/ggml-org/llama.cpp</link> - GGUF conversion and quantization',
                styles["small"],
            ),
            Spacer(1, 4 * mm),
            p(
                "EdgeOML is designed to publish useful evidence whether fingerprints survive Q4 "
                "or fail at a reproducible boundary.",
                ParagraphStyle(
                    "closing",
                    parent=styles["callout"],
                    fontSize=12,
                    leading=16,
                    textColor=TEAL,
                ),
            ),
        ]
    )

    doc.build(story)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="output/pdf/edgeoml-sentient-grant-brief.pdf",
    )
    args = parser.parse_args()
    build_pdf(Path(args.output))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
