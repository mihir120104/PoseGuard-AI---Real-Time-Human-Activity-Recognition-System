"""
report_generator.py
Generates a professional PDF report for the HAR AI Platform.
Usage: from report_generator import generate_pdf_report
"""

import io
import os
import numpy as np
import pandas as pd
from datetime import datetime
from collections import Counter

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus import Image as RLImage

# ── Color palette ──
DARK       = colors.HexColor("#0d1117")
CARD       = colors.HexColor("#161b27")
BORDER     = colors.HexColor("#21283a")
GREEN      = colors.HexColor("#22c55e")
TEAL       = colors.HexColor("#14b8a6")
AMBER      = colors.HexColor("#f59e0b")
RED        = colors.HexColor("#ef4444")
MUTED      = colors.HexColor("#5c6478")
LIGHT_TEXT = colors.HexColor("#c8cdd8")
WHITE      = colors.white
PAGE_W, PAGE_H = A4
MARGIN = 18 * mm


def _styles():
    base = getSampleStyleSheet()
    def S(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    return {
        "title":    S("title",    fontSize=26, textColor=WHITE,      leading=32, spaceAfter=4,  fontName="Helvetica-Bold"),
        "subtitle": S("subtitle", fontSize=11, textColor=MUTED,      leading=16, spaceAfter=16, fontName="Helvetica"),
        "h1":       S("h1",       fontSize=13, textColor=TEAL,       leading=18, spaceAfter=6,  spaceBefore=14, fontName="Helvetica-Bold"),
        "h2":       S("h2",       fontSize=10, textColor=MUTED,      leading=14, spaceAfter=4,  spaceBefore=8,  fontName="Helvetica-Bold"),
        "body":     S("body",     fontSize=9,  textColor=LIGHT_TEXT, leading=14, spaceAfter=4,  fontName="Helvetica"),
        "small":    S("small",    fontSize=8,  textColor=MUTED,      leading=12, spaceAfter=2,  fontName="Helvetica"),
        "mono":     S("mono",     fontSize=9,  textColor=GREEN,      leading=14,                fontName="Courier-Bold"),
        "center":   S("center",   fontSize=9,  textColor=LIGHT_TEXT, leading=14, alignment=TA_CENTER, fontName="Helvetica"),
        "alert":    S("alert",    fontSize=9,  textColor=RED,        leading=14, fontName="Helvetica-Bold"),
        "kpi_val":  S("kpi_val",  fontSize=18, textColor=GREEN,      leading=22, alignment=TA_CENTER, fontName="Helvetica-Bold"),
        "kpi_lbl":  S("kpi_lbl",  fontSize=7,  textColor=MUTED,      leading=10, alignment=TA_CENTER, fontName="Helvetica"),
    }


def _kpi_table(data):
    """data = list of (label, value, color_hex)"""
    st = _styles()
    cells = []
    for label, value, color in data:
        val_style = ParagraphStyle("kv", parent=st["kpi_val"],
                                   textColor=colors.HexColor(color))
        cells.append([
            Paragraph(value, val_style),
            Paragraph(label, st["kpi_lbl"]),
        ])
    col_w = (PAGE_W - 2 * MARGIN) / len(cells)
    tdata = [
        [c[0] for c in cells],
        [c[1] for c in cells],
    ]
    t = Table(tdata, colWidths=[col_w] * len(cells))
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), CARD),
        ("BOX",         (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID",   (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING",  (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _section_rule(story, styles, title):
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Paragraph(title, styles["h1"]))


def _df_table(df, col_widths=None, header_bg=CARD, row_bg1=DARK, row_bg2=CARD):
    """Render a DataFrame as a styled ReportLab Table."""
    st = _styles()
    head_style = ParagraphStyle("th", parent=st["small"],
                                textColor=TEAL, fontName="Helvetica-Bold")
    cell_style  = st["small"]

    data = [[Paragraph(str(c), head_style) for c in df.columns]]
    for _, row in df.iterrows():
        data.append([Paragraph(str(v), cell_style) for v in row.values])

    if col_widths is None:
        w = (PAGE_W - 2 * MARGIN) / len(df.columns)
        col_widths = [w] * len(df.columns)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND",    (0, 0), (-1, 0),  header_bg),
        ("BACKGROUND",    (0, 1), (-1, -1), row_bg1),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [row_bg1, row_bg2]),
        ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    t.setStyle(TableStyle(style))
    return t


def _background_canvas(canvas, doc):
    """Full-page dark background + header bar + footer."""
    canvas.saveState()
    # Page background
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Top accent bar
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 6, PAGE_W, 6, fill=1, stroke=0)
    # Footer
    canvas.setFillColor(BORDER)
    canvas.rect(0, 0, PAGE_W, 10 * mm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, 4 * mm,
                      f"HAR AI Platform  ·  Confidential  ·  Generated {datetime.now().strftime('%d %b %Y %H:%M')}")
    canvas.drawRightString(PAGE_W - MARGIN, 4 * mm, f"Page {doc.page}")
    canvas.restoreState()


def generate_pdf_report(df: pd.DataFrame) -> bytes:
    """
    Generate a full PDF report from the activity history DataFrame.
    df must have columns: ID, Activity, Confidence, Time
    Returns bytes of the PDF.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN + 8, bottomMargin=14 * mm,
    )

    styles = _styles()
    story  = []

    # ── COVER / HEADER ──
    story.append(Spacer(1, 10))
    story.append(Paragraph("HAR AI Platform", styles["title"]))
    story.append(Paragraph("Human Activity Recognition — Activity Analysis Report", styles["subtitle"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%A, %d %B %Y at %H:%M:%S')}  ·  "
        f"Records: {len(df)}  ·  Model: CNN + BiLSTM + Attention  ·  F1: 99.61%",
        styles["small"]
    ))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=TEAL))

    # ── MODEL METRICS (if available) ──
    metrics = {}
    if os.path.exists("metrics.txt"):
        try:
            with open("metrics.txt") as f:
                for line in f:
                    k, v = line.strip().split(":")
                    metrics[k.strip()] = float(v.strip())
        except:
            pass

    if metrics:
        _section_rule(story, styles, "Model Performance")
        kpi_data = [
            ("Accuracy",    f"{metrics.get('Accuracy',0)*100:.2f}%",    "#22c55e"),
            ("Weighted F1", f"{metrics.get('F1',0)*100:.2f}%",          "#14b8a6"),
            ("Macro F1",    f"{metrics.get('F1_macro',0)*100:.2f}%",    "#14b8a6"),
            ("Top-2 Acc",   f"{metrics.get('Top2_accuracy',0)*100:.2f}%","#f59e0b"),
            ("Avg Confidence", f"{metrics.get('Avg_confidence',0)*100:.1f}%","#f59e0b"),
        ]
        story.append(_kpi_table(kpi_data))

    # ── DATASET SUMMARY ──
    _section_rule(story, styles, "Dataset Summary")

    df_work = df.copy()
    df_work["Time"] = pd.to_datetime(df_work["Time"])
    df_work = df_work.sort_values("Time")

    summary_data = [
        ("Total Records",     str(len(df_work)),                               "#22c55e"),
        ("Unique Activities", str(df_work["Activity"].nunique()),               "#14b8a6"),
        ("Avg Confidence",    f"{df_work['Confidence'].mean()*100:.1f}%",       "#f59e0b"),
        ("Date Range",        f"{df_work['Time'].min().strftime('%d/%m/%y')} – {df_work['Time'].max().strftime('%d/%m/%y')}", "#c8cdd8"),
    ]
    story.append(_kpi_table(summary_data))

    # ── ACTIVITY DISTRIBUTION ──
    _section_rule(story, styles, "Activity Distribution")
    counts = df_work["Activity"].value_counts().reset_index()
    counts.columns = ["Activity", "Count"]
    counts["% of Total"] = (counts["Count"] / len(df_work) * 100).round(1).astype(str) + "%"
    counts["Avg Confidence"] = counts["Activity"].apply(
        lambda a: f"{df_work[df_work['Activity']==a]['Confidence'].mean()*100:.1f}%"
    )

    w_total = PAGE_W - 2 * MARGIN
    story.append(_df_table(counts, col_widths=[w_total*0.4, w_total*0.15, w_total*0.2, w_total*0.25]))

    # ── RISK ACTIVITY CHECK ──
    RISK = ["fighting", "Fighting", "falling"]
    risk_df = df_work[df_work["Activity"].isin(RISK)]
    if not risk_df.empty:
        _section_rule(story, styles, "Risk Activity Alert")
        story.append(Paragraph(
            f"WARNING: {len(risk_df)} risk activity records detected "
            f"({', '.join(risk_df['Activity'].unique())}). "
            f"Latest occurrence: {risk_df['Time'].max().strftime('%d %b %Y %H:%M:%S')}",
            styles["alert"]
        ))
        story.append(Spacer(1, 6))
        risk_show = risk_df[["Time","Activity","Confidence"]].copy()
        risk_show["Time"] = risk_show["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
        risk_show["Confidence"] = (risk_show["Confidence"]*100).round(1).astype(str) + "%"
        risk_show = risk_show.head(20)
        story.append(_df_table(risk_show, col_widths=[w_total*0.45, w_total*0.3, w_total*0.25]))

    # ── CONFIDENCE ANALYSIS ──
    _section_rule(story, styles, "Confidence Analysis")
    thresholds = [(0.0,0.5),(0.5,0.65),(0.65,0.75),(0.75,0.85),(0.85,0.95),(0.95,1.01)]
    bucket_rows = []
    for lo, hi in thresholds:
        mask = (df_work["Confidence"] >= lo) & (df_work["Confidence"] < hi)
        n    = mask.sum()
        if n > 0:
            bucket_rows.append({
                "Confidence Range": f"{lo:.0%} – {min(hi,1.0):.0%}",
                "Count": str(n),
                "% of Records": f"{n/len(df_work)*100:.1f}%",
                "Avg Confidence": f"{df_work[mask]['Confidence'].mean()*100:.1f}%",
            })
    if bucket_rows:
        bdf = pd.DataFrame(bucket_rows)
        story.append(_df_table(bdf, col_widths=[w_total*0.3, w_total*0.15, w_total*0.25, w_total*0.3]))

    # ── TIME ANALYSIS ──
    _section_rule(story, styles, "Temporal Analysis")
    df_work["Hour"]    = df_work["Time"].dt.hour
    df_work["Weekday"] = df_work["Time"].dt.day_name()

    hourly = df_work.groupby("Hour").size().reset_index(name="Count")
    hourly["Hour"] = hourly["Hour"].astype(str) + ":00"
    peak_hour = hourly.loc[hourly["Count"].idxmax(), "Hour"]
    story.append(Paragraph(
        f"Peak activity hour: {peak_hour}  ·  "
        f"Most common activity: {df_work['Activity'].mode()[0]}  ·  "
        f"High-confidence records (>85%): {(df_work['Confidence']>0.85).sum()} "
        f"({(df_work['Confidence']>0.85).sum()/len(df_work)*100:.1f}%)",
        styles["body"]
    ))
    story.append(Spacer(1, 6))

    # Per-activity stats table
    act_stats = []
    for act in df_work["Activity"].unique():
        sub = df_work[df_work["Activity"] == act]
        act_stats.append({
            "Activity": act,
            "Count": str(len(sub)),
            "Min Conf": f"{sub['Confidence'].min()*100:.1f}%",
            "Max Conf": f"{sub['Confidence'].max()*100:.1f}%",
            "Avg Conf": f"{sub['Confidence'].mean()*100:.1f}%",
            "Std Conf": f"{sub['Confidence'].std()*100:.1f}%",
        })
    adf = pd.DataFrame(act_stats).sort_values("Count", ascending=False)
    cw  = [w_total*0.25, w_total*0.1, w_total*0.15, w_total*0.15, w_total*0.175, w_total*0.175]
    story.append(_df_table(adf, col_widths=cw))

    # ── PAGE BREAK → FULL ACTIVITY LOG ──
    story.append(PageBreak())

    story.append(Paragraph("Complete Activity Log", styles["h1"]))
    story.append(Paragraph(
        f"All {len(df_work)} records sorted by time (most recent first).",
        styles["small"]
    ))
    story.append(Spacer(1, 6))

    log = df_work[["Time","Activity","Confidence"]].copy()
    log = log.sort_values("Time", ascending=False)
    log["Time"]       = log["Time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    log["Confidence"] = (log["Confidence"]*100).round(1).astype(str) + "%"

    # Split into chunks so table doesn't overflow badly
    CHUNK = 50
    for i in range(0, len(log), CHUNK):
        chunk = log.iloc[i:i+CHUNK]
        story.append(_df_table(chunk, col_widths=[w_total*0.5, w_total*0.3, w_total*0.2]))
        if i + CHUNK < len(log):
            story.append(Spacer(1, 4))

    # ── FOOTER NOTE ──
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "This report was auto-generated by HAR AI Platform. "
        "Model: CNN + BiLSTM + Attention · Architecture: 7-class pose-based activity recognition. "
        "Trained on 2568 augmented samples with 5-fold cross-validation. "
        "Test set F1: 99.61% · Test accuracy: 99.61%.",
        styles["small"]
    ))

    doc.build(story, onFirstPage=_background_canvas, onLaterPages=_background_canvas)
    buf.seek(0)
    return buf.read()