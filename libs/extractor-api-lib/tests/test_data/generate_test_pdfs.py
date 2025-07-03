#!/usr/bin/env python3
"""Script to generate test PDF files for PDF extractor testing."""

import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    PageBreak,
    KeepTogether,
    BaseDocTemplate,
    PageTemplate,
    Frame,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus.flowables import HRFlowable
import tempfile


def create_test_data_dir():
    """Create the test data directory if it doesn't exist."""
    test_data_dir = Path(__file__).parent
    test_data_dir.mkdir(exist_ok=True)
    return test_data_dir


def generate_text_based_pdf():
    """Generate a PDF with substantial text content and comprehensive tables."""
    test_data_dir = create_test_data_dir()
    filename = test_data_dir / "text_based_document.pdf"

    doc = SimpleDocTemplate(
        str(filename),
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.darkblue,
    )
    story.append(Paragraph("Advanced Text-Based Document for Testing", title_style))
    story.append(Spacer(1, 20))

    # Section 1: Introduction
    story.append(Paragraph("1. Introduction", styles["Heading2"]))
    intro_text = """
    This is a comprehensive introduction section that contains substantial text content.
    The purpose of this document is to test the PDF extractor's ability to correctly
    classify pages as text-based when they contain primarily extractable text content.
    This section has been designed to exceed the 50-character threshold used by the
    classification algorithm to ensure proper categorization as a TEXT_BASED page type.
    The document includes multiple tables with different structures to test table extraction capabilities,
    including nested headers, merged cells, and complex formatting scenarios.
    """
    story.append(Paragraph(intro_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Section 2: Methodology with enhanced tables
    story.append(Paragraph("2. Methodology", styles["Heading2"]))
    method_text = """
    This section describes the methodology used in our research. The approach involves
    multiple phases of data collection, analysis, and validation. Each phase is carefully
    designed to ensure accuracy and reliability of the results obtained.
    """
    story.append(Paragraph(method_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Enhanced Table 1: Project Phases with merged cells
    story.append(Paragraph("2.1 Project Phases Overview", styles["Heading3"]))
    table1_data = [
        ["Phase", "Description", "Timeline", "Resources Required", "Expected Deliverables"],
        [
            "Planning",
            "Initial project setup and requirement analysis",
            "2 weeks",
            "1 PM, 2 analysts",
            "Project charter, requirements doc",
        ],
        [
            "Design",
            "System architecture and detailed design",
            "3 weeks",
            "2 architects, 1 designer",
            "Technical specifications",
        ],
        ["Development", "Implementation of core functionality", "8 weeks", "4 developers, 1 lead", "Working prototype"],
        ["Testing", "Quality assurance and validation", "3 weeks", "3 testers, 1 QA lead", "Test reports, bug fixes"],
        ["Deployment", "Production deployment and monitoring", "1 week", "2 DevOps, 1 admin", "Live system"],
        ["Maintenance", "Ongoing support and updates", "Ongoing", "1 support engineer", "Monthly reports"],
    ]

    table1 = Table(table1_data, colWidths=[1 * inch, 2 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    table1.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.lightblue),
                ("ALTERNATEROWCOLORS", (0, 1), (-1, -1), [colors.lightblue, colors.white]),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(KeepTogether(table1))
    story.append(Spacer(1, 20))

    # Table 2: Detailed Budget Breakdown with subtotals
    story.append(Paragraph("2.2 Comprehensive Budget Analysis", styles["Heading3"]))
    table2_data = [
        ["Category", "Item", "Q1 Budget", "Q1 Actual", "Q2 Budget", "Q2 Actual", "Total Variance"],
        ["Personnel", "Senior Developers", "$35,000", "$34,200", "$36,000", "$35,800", "-$1,000"],
        ["Personnel", "Junior Developers", "$15,000", "$14,300", "$16,000", "$15,400", "-$1,300"],
        ["Personnel", "Project Manager", "$12,000", "$12,000", "$12,500", "$12,500", "$0"],
        ["Personnel", "QA Engineers", "$8,000", "$7,800", "$8,500", "$8,200", "-$500"],
        ["", "Personnel Subtotal", "$70,000", "$68,300", "$73,000", "$71,900", "-$2,800"],
        ["Equipment", "Hardware", "$15,000", "$16,200", "$12,000", "$11,800", "-$1,000"],
        ["Equipment", "Software Licenses", "$8,000", "$7,900", "$8,500", "$8,300", "-$300"],
        ["Equipment", "Cloud Services", "$5,000", "$4,800", "$5,500", "$5,400", "-$300"],
        ["", "Equipment Subtotal", "$28,000", "$28,900", "$26,000", "$25,500", "-$1,600"],
        ["Operations", "Office Rent", "$6,000", "$6,000", "$6,200", "$6,200", "$0"],
        ["Operations", "Utilities", "$2,000", "$1,950", "$2,100", "$2,050", "-$100"],
        ["Operations", "Internet/Phone", "$1,500", "$1,450", "$1,600", "$1,550", "-$100"],
        ["", "Operations Subtotal", "$9,500", "$9,400", "$9,900", "$9,800", "-$200"],
        ["", "GRAND TOTAL", "$107,500", "$106,600", "$108,900", "$107,200", "-$4,600"],
    ]

    table2 = Table(
        table2_data, colWidths=[1 * inch, 1.2 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch, 1 * inch]
    )
    table2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.lightgreen),
                # Subtotal rows formatting
                ("BACKGROUND", (0, 5), (-1, 5), colors.yellow),  # Personnel subtotal
                ("BACKGROUND", (0, 9), (-1, 9), colors.yellow),  # Equipment subtotal
                ("BACKGROUND", (0, 13), (-1, 13), colors.yellow),  # Operations subtotal
                ("BACKGROUND", (0, -1), (-1, -1), colors.orange),  # Grand total
                ("FONTNAME", (0, 5), (-1, 5), "Helvetica-Bold"),
                ("FONTNAME", (0, 9), (-1, 9), "Helvetica-Bold"),
                ("FONTNAME", (0, 13), (-1, 13), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(KeepTogether(table2))
    story.append(Spacer(1, 12))

    # Page break for next section
    story.append(PageBreak())

    # Section 3: Results with complex data table
    story.append(Paragraph("3. Detailed Results and Performance Analysis", styles["Heading2"]))
    results_text = """
    The results obtained from our methodology show significant improvements in accuracy
    and efficiency across multiple metrics. The data processing phase revealed interesting 
    patterns that were not immediately apparent in the raw data. Statistical analysis 
    confirmed the validity of our hypotheses with a confidence level of 95%.
    """
    story.append(Paragraph(results_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Table 3: Complex Performance Metrics with statistical data
    story.append(Paragraph("3.1 Comprehensive Performance Metrics", styles["Heading3"]))
    table3_data = [
        ["Metric", "Unit", "Baseline", "Method A", "Method B", "Method C", "Best Result", "Improvement"],
        ["Accuracy", "%", "78.5 ± 2.1", "85.2 ± 1.8", "89.1 ± 1.5", "92.3 ± 1.2", "92.3", "+17.6%"],
        ["Precision", "%", "75.2 ± 2.5", "82.8 ± 2.0", "87.5 ± 1.7", "90.1 ± 1.4", "90.1", "+19.8%"],
        ["Recall", "%", "80.1 ± 2.3", "88.3 ± 1.9", "91.2 ± 1.6", "93.5 ± 1.3", "93.5", "+16.7%"],
        ["F1-Score", "%", "77.5 ± 2.2", "85.4 ± 1.8", "89.3 ± 1.5", "91.7 ± 1.3", "91.7", "+18.3%"],
        ["Processing Time", "ms", "245 ± 15", "189 ± 12", "156 ± 10", "134 ± 8", "134", "-45.3%"],
        ["Memory Usage", "MB", "128 ± 8", "98 ± 6", "87 ± 5", "76 ± 4", "76", "-40.6%"],
        ["Throughput", "req/s", "120 ± 10", "165 ± 12", "210 ± 15", "245 ± 18", "245", "+104.2%"],
        ["Error Rate", "%", "4.2 ± 0.8", "2.8 ± 0.6", "1.9 ± 0.4", "1.1 ± 0.3", "1.1", "-73.8%"],
    ]

    table3 = Table(
        table3_data, colWidths=[1 * inch, 0.6 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch, 0.8 * inch, 0.8 * inch]
    )
    table3.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.purple),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("TOPPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.lavender),
                ("BACKGROUND", (-2, 1), (-2, -1), colors.lightgreen),  # Best result column
                ("BACKGROUND", (-1, 1), (-1, -1), colors.lightyellow),  # Improvement column
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(KeepTogether(table3))
    story.append(Spacer(1, 20))

    # Table 4: Cross-validation results
    story.append(Paragraph("3.2 Cross-Validation Results", styles["Heading3"]))
    table4_data = [
        ["Fold", "Training Acc", "Validation Acc", "Test Acc", "Precision", "Recall", "F1-Score"],
        ["Fold 1", "94.2%", "91.8%", "90.5%", "89.7%", "91.2%", "90.4%"],
        ["Fold 2", "93.8%", "92.1%", "91.0%", "90.3%", "91.8%", "91.0%"],
        ["Fold 3", "94.5%", "91.5%", "90.8%", "90.1%", "91.5%", "90.8%"],
        ["Fold 4", "94.1%", "92.3%", "91.5%", "91.0%", "92.1%", "91.5%"],
        ["Fold 5", "93.9%", "91.9%", "90.9%", "90.5%", "91.4%", "90.9%"],
        ["Mean", "94.1%", "91.9%", "90.9%", "90.3%", "91.6%", "90.9%"],
        ["Std Dev", "0.28%", "0.31%", "0.37%", "0.48%", "0.35%", "0.41%"],
    ]

    table4 = Table(table4_data)
    table4.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkred),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -3), colors.mistyrose),
                ("BACKGROUND", (0, -2), (-1, -2), colors.lightcyan),  # Mean row
                ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),  # Std dev row
                ("FONTNAME", (0, -2), (-1, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
            ]
        )
    )

    story.append(KeepTogether(table4))
    story.append(Spacer(1, 12))

    # Section 4: Conclusion
    story.append(Paragraph("4. Comprehensive Conclusion", styles["Heading2"]))
    conclusion_text = """
    In conclusion, this study demonstrates the effectiveness of the proposed methodology
    across multiple evaluation criteria. The results provide strong evidence supporting 
    our initial hypotheses and open new avenues for future research. The implications 
    of these findings extend beyond the immediate scope of this study and may have 
    broader applications in the field. The comprehensive tables above clearly show 
    the progression and improvements achieved through our systematic approach, with 
    statistical significance confirmed through rigorous cross-validation procedures.
    
    The enhanced table structures in this document serve as comprehensive test cases
    for PDF extraction algorithms, including scenarios with merged cells, nested headers,
    subtotals, and complex formatting requirements.
    """
    story.append(Paragraph(conclusion_text, styles["Normal"]))

    doc.build(story)
    print(f"Generated enhanced text-based PDF with advanced tables: {filename}")
    return filename


def generate_scanned_image_pdf():
    """Generate a PDF that simulates a scanned document with minimal extractable text."""
    test_data_dir = create_test_data_dir()
    filename = test_data_dir / "scanned_document.pdf"

    # Create an image that looks like a scanned document
    img_width, img_height = 595, 842  # A4 size in points
    image = Image.new("RGB", (img_width, img_height), color="white")
    draw = ImageDraw.Draw(image)

    # Try to use a default font, fall back to default if not available
    try:
        font_large = ImageFont.truetype("Arial.ttf", 20)
        font_medium = ImageFont.truetype("Arial.ttf", 16)
        font_small = ImageFont.truetype("Arial.ttf", 12)
    except OSError:
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
            font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        except OSError:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

    # Add title
    draw.text((50, 50), "SCANNED DOCUMENT", fill="black", font=font_large)

    # Add some body text to simulate scanned content
    y_pos = 100
    lines = [
        "This document appears to be scanned from a physical paper.",
        "The text extraction capabilities are limited because",
        "the content exists as image data rather than searchable text.",
        "",
        "Key characteristics of scanned documents:",
        "• Text is part of the image",
        "• OCR is required for text extraction",
        "• Quality depends on scan resolution",
        "• May contain artifacts and noise",
        "",
        "This simulation creates an image-based PDF that mimics",
        "the behavior of a real scanned document for testing purposes.",
    ]

    for line in lines:
        draw.text((50, y_pos), line, fill="black", font=font_small)
        y_pos += 25

    # Add some visual noise to simulate scan artifacts
    for i in range(100):
        x = hash(f"noise_x_{i}") % img_width
        y = hash(f"noise_y_{i}") % img_height
        draw.point((x, y), fill="lightgray")

    # Save image to temporary file and create PDF
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
        image.save(temp_img.name, "PNG")

        # Create PDF with the image
        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []

        # Add the image to PDF
        rl_image = RLImage(temp_img.name, width=6 * inch, height=8 * inch)
        story.append(rl_image)

        doc.build(story)

    # Clean up temporary file
    Path(temp_img.name).unlink()

    print(f"Generated scanned PDF: {filename}")
    return filename


def generate_mixed_content_pdf():
    """Generate a PDF with both extractable text and embedded images."""
    test_data_dir = create_test_data_dir()
    filename = test_data_dir / "mixed_content_document.pdf"

    doc = SimpleDocTemplate(
        str(filename),
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Heading1"], fontSize=24, spaceAfter=30, alignment=1, textColor=colors.darkred
    )
    story.append(Paragraph("Advanced Mixed Content Document for Testing", title_style))
    story.append(Spacer(1, 20))

    # Section with text
    story.append(Paragraph("1. Overview", styles["Heading2"]))
    overview_text = """
    This document contains mixed content including both extractable text and embedded images.
    The purpose is to test the PDF extractor's ability to correctly classify pages as MIXED
    when they contain substantial text content along with image elements. This classification
    is important for determining the appropriate extraction strategy to use. The document
    includes multiple visualizations, charts, and complex layouts to thoroughly test
    image-text relationship extraction capabilities.
    """
    story.append(Paragraph(overview_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Create multiple chart images using matplotlib

    # Chart 1: Bar chart
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    data1 = [23, 45, 56, 78, 32]
    labels1 = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    bars = ax1.bar(labels1, data1, color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"])
    ax1.set_title("Quarterly Performance Data", fontsize=14, fontweight="bold")
    ax1.set_ylabel("Performance Score", fontsize=12)
    ax1.set_xlabel("Quarter", fontsize=12)

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0, height + 1, f"{height}", ha="center", va="bottom", fontweight="bold"
        )

    ax1.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    # Save chart to temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_chart1:
        fig1.savefig(temp_chart1.name, dpi=150, bbox_inches="tight")
        plt.close(fig1)

        # Add the chart to PDF
        chart_image1 = RLImage(temp_chart1.name, width=5 * inch, height=3.5 * inch)
        story.append(chart_image1)
        story.append(Spacer(1, 12))

    # Text analysis section
    story.append(Paragraph("2. Performance Analysis", styles["Heading2"]))
    analysis_text = """
    The chart above illustrates the quarterly performance trends observed during our study period.
    As evident from the data visualization, there is a clear upward trend from Q1 to Q4, followed
    by a decline in Q5. This pattern suggests seasonal variations that should be considered in
    future planning and resource allocation decisions. The performance metrics show significant
    improvement during the middle quarters, with Q4 representing peak performance.
    """
    story.append(Paragraph(analysis_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Enhanced table with data
    table_data = [
        ["Quarter", "Score", "Change %", "Status", "Target", "Variance"],
        ["Q1", "23", "-", "Baseline", "25", "-8.0%"],
        ["Q2", "45", "+95.7%", "Improving", "40", "+12.5%"],
        ["Q3", "56", "+24.4%", "Good", "55", "+1.8%"],
        ["Q4", "78", "+39.3%", "Excellent", "70", "+11.4%"],
        ["Q5", "32", "-59.0%", "Concerning", "75", "-57.3%"],
    ]

    table = Table(table_data, colWidths=[0.9 * inch, 0.7 * inch, 0.9 * inch, 1 * inch, 0.7 * inch, 0.9 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.lightblue),
                # Color code status column
                ("BACKGROUND", (3, 2), (3, 2), colors.yellow),  # Improving
                ("BACKGROUND", (3, 3), (3, 3), colors.lightgreen),  # Good
                ("BACKGROUND", (3, 4), (3, 4), colors.green),  # Excellent
                ("BACKGROUND", (3, 5), (3, 5), colors.salmon),  # Concerning
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 15))

    # Chart 2: Line plot with trend analysis
    fig2, ax2 = plt.subplots(figsize=(7, 4))

    # Multiple data series
    quarters = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    actual = [23, 45, 56, 78, 32]
    target = [25, 40, 55, 70, 75]
    forecast = [20, 42, 58, 75, 68]

    ax2.plot(quarters, actual, marker="o", linewidth=2, label="Actual", color="#d62728")
    ax2.plot(quarters, target, marker="s", linewidth=2, label="Target", color="#2ca02c", linestyle="--")
    ax2.plot(quarters, forecast, marker="^", linewidth=2, label="Forecast", color="#ff7f0e", linestyle=":")

    ax2.set_title("Performance Trends: Actual vs Target vs Forecast", fontsize=14, fontweight="bold")
    ax2.set_ylabel("Performance Score", fontsize=12)
    ax2.set_xlabel("Quarter", fontsize=12)
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)

    # Add annotations
    ax2.annotate(
        "Peak Performance",
        xy=("Q4", 78),
        xytext=("Q3", 85),
        arrowprops=dict(arrowstyle="->", color="red", alpha=0.7),
        fontsize=10,
        ha="center",
    )
    ax2.annotate(
        "Significant Drop",
        xy=("Q5", 32),
        xytext=("Q4", 40),
        arrowprops=dict(arrowstyle="->", color="red", alpha=0.7),
        fontsize=10,
        ha="center",
    )

    plt.tight_layout()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_chart2:
        fig2.savefig(temp_chart2.name, dpi=150, bbox_inches="tight")
        plt.close(fig2)

        chart_image2 = RLImage(temp_chart2.name, width=6 * inch, height=3.5 * inch)
        story.append(chart_image2)
        story.append(Spacer(1, 12))

    # Section 3: Detailed Analysis
    story.append(Paragraph("3. Trend Analysis and Insights", styles["Heading2"]))
    trends_text = """
    The comprehensive trend analysis reveals several key insights:
    
    1. Performance Trajectory: The actual performance closely followed forecasted patterns through Q3,
    with Q4 showing exceptional results that exceeded both targets and forecasts.
    
    2. Q5 Anomaly: The dramatic decline in Q5 represents a significant deviation from all projections,
    suggesting external factors or methodological changes that require investigation.
    
    3. Forecasting Accuracy: The forecast model demonstrated high accuracy for Q1-Q4, with prediction
    errors remaining within acceptable ranges until the Q5 anomaly.
    """
    story.append(Paragraph(trends_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Chart 3: Heatmap-style visualization using matplotlib
    fig3, ax3 = plt.subplots(figsize=(8, 5))

    # Create sample correlation matrix data
    metrics = ["Accuracy", "Speed", "Quality", "Efficiency", "Satisfaction"]
    correlation_data = np.array(
        [
            [1.0, 0.8, 0.9, 0.7, 0.6],
            [0.8, 1.0, 0.6, 0.9, 0.5],
            [0.9, 0.6, 1.0, 0.5, 0.8],
            [0.7, 0.9, 0.5, 1.0, 0.4],
            [0.6, 0.5, 0.8, 0.4, 1.0],
        ]
    )

    im = ax3.imshow(correlation_data, cmap="RdYlBu_r", aspect="auto", vmin=-1, vmax=1)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax3)
    cbar.set_label("Correlation Coefficient", rotation=270, labelpad=20)

    # Set ticks and labels
    ax3.set_xticks(range(len(metrics)))
    ax3.set_yticks(range(len(metrics)))
    ax3.set_xticklabels(metrics, rotation=45, ha="right")
    ax3.set_yticklabels(metrics)

    # Add correlation values as text
    for i in range(len(metrics)):
        for j in range(len(metrics)):
            text = ax3.text(
                j, i, f"{correlation_data[i, j]:.1f}", ha="center", va="center", color="black", fontweight="bold"
            )

    ax3.set_title("Performance Metrics Correlation Matrix", fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_chart3:
        fig3.savefig(temp_chart3.name, dpi=150, bbox_inches="tight")
        plt.close(fig3)

        chart_image3 = RLImage(temp_chart3.name, width=6.5 * inch, height=4 * inch)
        story.append(chart_image3)
        story.append(Spacer(1, 12))

    # Final section
    story.append(Paragraph("4. Recommendations and Future Directions", styles["Heading2"]))
    recommendations_text = """
    Based on the comprehensive analysis of performance data and correlation patterns:
    
    • Immediate Actions: Investigate root causes of Q5 performance decline and implement
      corrective measures to restore performance to Q4 levels.
    
    • Process Optimization: Leverage the strong correlation between Speed and Efficiency (0.9)
      to develop integrated improvement strategies.
    
    • Quality Assurance: The high correlation between Accuracy and Quality (0.9) suggests
      that accuracy improvements will directly impact overall quality metrics.
    
    • Forecasting Enhancement: Update prediction models to account for identified anomalies
      and improve resilience to external factors.
    
    • Monitoring Strategy: Implement real-time dashboards to track performance metrics
      and enable proactive intervention before significant declines occur.
    
    This mixed content document demonstrates the integration of textual analysis with
    visual data representations, creating comprehensive test scenarios for PDF extraction
    systems that must handle both content types effectively while maintaining their
    contextual relationships.
    """
    story.append(Paragraph(recommendations_text, styles["Normal"]))

    doc.build(story)

    # Clean up temporary chart files
    Path(temp_chart1.name).unlink()
    Path(temp_chart2.name).unlink()
    Path(temp_chart3.name).unlink()

    print(f"Generated enhanced mixed content PDF: {filename}")
    return filename


def generate_multi_column_pdf():
    """Generate a PDF with multi-column layout for advanced testing."""
    test_data_dir = create_test_data_dir()
    filename = test_data_dir / "multi_column_document.pdf"

    # Create custom document template with two-column layout
    doc = BaseDocTemplate(str(filename), pagesize=letter)

    # Define frame layout for two columns
    frame_width = (letter[0] - 1.5 * inch) / 2  # Split width between two columns
    frame_height = letter[1] - 1.5 * inch

    left_frame = Frame(
        0.75 * inch,
        0.75 * inch,
        frame_width,
        frame_height,
        leftPadding=6,
        rightPadding=6,
        topPadding=6,
        bottomPadding=6,
    )
    right_frame = Frame(
        0.75 * inch + frame_width + 0.25 * inch,
        0.75 * inch,
        frame_width,
        frame_height,
        leftPadding=6,
        rightPadding=6,
        topPadding=6,
        bottomPadding=6,
    )

    # Create page template
    two_column_template = PageTemplate(id="TwoColumn", frames=[left_frame, right_frame])
    doc.addPageTemplates([two_column_template])

    styles = getSampleStyleSheet()
    story = []

    # Title (spans both columns)
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Heading1"], fontSize=20, spaceAfter=20, alignment=1, textColor=colors.darkblue
    )
    story.append(Paragraph("Multi-Column Document Layout Test", title_style))
    story.append(Spacer(1, 15))

    # Add horizontal rule
    story.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
    story.append(Spacer(1, 10))

    # Column 1 content
    story.append(Paragraph("Column 1: Research Overview", styles["Heading2"]))
    col1_text1 = """
    This document demonstrates multi-column layout capabilities for PDF extraction testing.
    The text flows naturally between columns, creating a newspaper-like or academic journal
    format that challenges extraction algorithms to properly maintain reading order and
    column separation.
    """
    story.append(Paragraph(col1_text1, styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Methodology", styles["Heading3"]))
    col1_text2 = """
    Our research methodology incorporates both quantitative and qualitative approaches.
    The quantitative component involves statistical analysis of large datasets, while
    the qualitative aspect includes expert interviews and case study analysis.
    """
    story.append(Paragraph(col1_text2, styles["Normal"]))
    story.append(Spacer(1, 10))

    # Table in first column
    col1_table_data = [
        ["Phase", "Duration"],
        ["Planning", "2 weeks"],
        ["Execution", "6 weeks"],
        ["Analysis", "3 weeks"],
        ["Reporting", "1 week"],
    ]

    col1_table = Table(col1_table_data, colWidths=[1.2 * inch, 1 * inch])
    col1_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(col1_table)
    story.append(Spacer(1, 15))

    story.append(Paragraph("Data Collection", styles["Heading3"]))
    col1_text3 = """
    Data collection procedures follow established protocols to ensure reliability and
    validity. Multiple sources are utilized including surveys, interviews, and
    observational studies. Quality control measures are implemented at each stage
    to maintain data integrity.
    """
    story.append(Paragraph(col1_text3, styles["Normal"]))

    # Force column break
    story.append(Spacer(1, 20))
    story.append(Paragraph("Statistical Analysis", styles["Heading3"]))
    col1_text4 = """
    Statistical analysis employs both descriptive and inferential techniques.
    Descriptive statistics provide overview of data characteristics, while
    inferential methods test hypotheses and examine relationships between variables.
    """
    story.append(Paragraph(col1_text4, styles["Normal"]))

    # Column 2 content (this will flow to the next column)
    story.append(Paragraph("Column 2: Results and Discussion", styles["Heading2"]))
    col2_text1 = """
    The results section presents findings from our comprehensive analysis. Key insights
    emerged from both quantitative metrics and qualitative observations. These findings
    have significant implications for future research directions and practical applications
    in the field.
    """
    story.append(Paragraph(col2_text1, styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Key Findings", styles["Heading3"]))

    # Bullet points
    findings = [
        "Significant improvement in accuracy metrics (p < 0.05)",
        "Reduced processing time by 40% compared to baseline",
        "Enhanced user satisfaction scores across all demographics",
        "Scalability demonstrated up to 10,000 concurrent users",
        "Cost reduction of 25% in operational expenses",
    ]

    for finding in findings:
        story.append(Paragraph(f"• {finding}", styles["Normal"]))

    story.append(Spacer(1, 10))

    # Results table in second column
    col2_table_data = [
        ["Metric", "Before", "After", "Change"],
        ["Accuracy", "78.5%", "92.3%", "+17.6%"],
        ["Speed", "245ms", "134ms", "-45.3%"],
        ["Memory", "128MB", "76MB", "-40.6%"],
        ["Satisfaction", "3.2/5", "4.7/5", "+46.9%"],
    ]

    col2_table = Table(col2_table_data, colWidths=[0.8 * inch, 0.6 * inch, 0.6 * inch, 0.6 * inch])
    col2_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.lightgreen),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(col2_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Discussion", styles["Heading3"]))
    col2_text2 = """
    The discussion interprets results in context of existing literature and theoretical
    frameworks. Notable patterns emerge when comparing our findings with previous studies.
    The implications extend beyond immediate applications to broader methodological
    considerations for future research.
    """
    story.append(Paragraph(col2_text2, styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Limitations", styles["Heading3"]))
    col2_text3 = """
    Several limitations should be acknowledged. Sample size constraints may affect
    generalizability. Temporal factors could influence long-term validity. Geographic
    scope may limit applicability to other regions. Despite these limitations, the
    study provides valuable insights and establishes foundation for future work.
    """
    story.append(Paragraph(col2_text3, styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Future Work", styles["Heading3"]))
    col2_text4 = """
    Future research should address identified limitations and explore new directions.
    Longitudinal studies could examine temporal stability. Cross-cultural validation
    would enhance generalizability. Integration with emerging technologies presents
    exciting opportunities for innovation.
    """
    story.append(Paragraph(col2_text4, styles["Normal"]))

    doc.build(story)
    print(f"Generated multi-column PDF: {filename}")
    return filename


def main():
    """Generate all test PDF files."""
    print("Generating test PDF files...")

    # Create test data directory
    test_data_dir = create_test_data_dir()
    print(f"Test data directory: {test_data_dir}")

    # Generate all test PDFs
    text_pdf = generate_text_based_pdf()
    scanned_pdf = generate_scanned_image_pdf()
    mixed_pdf = generate_mixed_content_pdf()
    multi_column_pdf = generate_multi_column_pdf()

    print("\nGenerated test PDF files:")
    print(f"1. Text-based: {text_pdf}")
    print(f"2. Scanned: {scanned_pdf}")
    print(f"3. Mixed content: {mixed_pdf}")
    print(f"4. Multi-column: {multi_column_pdf}")
    print("\nTest PDF generation complete!")


if __name__ == "__main__":
    main()
