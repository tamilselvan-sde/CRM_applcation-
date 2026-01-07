import logging
import os
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger(__name__)

PDF_STORAGE_PATH = "/app/invoices"


def ensure_pdf_directory() -> None:
    if not os.path.exists(PDF_STORAGE_PATH):
        os.makedirs(PDF_STORAGE_PATH)
        logger.info(f"Created PDF storage directory: {PDF_STORAGE_PATH}")


def generate_invoice_pdf(
    invoice_number: str,
    customer_name: str,
    customer_email: str,
    customer_address: Optional[str],
    issue_date: datetime,
    due_date: Optional[datetime],
    items: list,
    subtotal: Decimal,
    tax_rate: Decimal,
    tax_amount: Decimal,
    total: Decimal,
    notes: Optional[str] = None,
) -> bytes:
    logger.info(f"Generating PDF for invoice: {invoice_number}")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1976D2"),
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1976D2"),
        spaceBefore=15,
        spaceAfter=10,
    )

    normal_style = ParagraphStyle(
        "Normal",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=5,
    )

    elements = []

    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Spacer(1, 10))

    invoice_info = [
        ["Invoice Number:", invoice_number],
        ["Issue Date:", issue_date.strftime("%B %d, %Y")],
        ["Due Date:", due_date.strftime("%B %d, %Y") if due_date else "N/A"],
    ]

    info_table = Table(invoice_info, colWidths=[1.5 * inch, 3 * inch])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1976D2")),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Bill To:", heading_style))
    elements.append(Paragraph(f"<b>{customer_name}</b>", normal_style))
    elements.append(Paragraph(customer_email, normal_style))
    if customer_address:
        for line in customer_address.split("\n"):
            elements.append(Paragraph(line, normal_style))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Items", heading_style))

    table_data = [["Description", "Qty", "Unit Price", "Subtotal"]]
    for item in items:
        description = item.get("description") or item.get("product_name", "Item")
        quantity = item.get("quantity", 1)
        unit_price = item.get("unit_price", 0)
        item_subtotal = item.get("subtotal", 0)
        table_data.append([
            description,
            str(quantity),
            f"${float(unit_price):,.2f}",
            f"${float(item_subtotal):,.2f}",
        ])

    items_table = Table(
        table_data,
        colWidths=[3.5 * inch, 0.75 * inch, 1.25 * inch, 1.25 * inch],
    )
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1976D2")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))

    totals_data = [
        ["Subtotal:", f"${float(subtotal):,.2f}"],
        [f"Tax ({float(tax_rate)}%):", f"${float(tax_amount):,.2f}"],
        ["Total:", f"${float(total):,.2f}"],
    ]

    totals_table = Table(totals_data, colWidths=[5.25 * inch, 1.5 * inch])
    totals_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("FONTSIZE", (0, -1), (-1, -1), 14),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.HexColor("#1976D2")),
        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#1976D2")),
    ]))
    elements.append(totals_table)

    if notes:
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Notes", heading_style))
        elements.append(Paragraph(notes, normal_style))

    elements.append(Spacer(1, 40))
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.gray,
        alignment=1,
    )
    elements.append(Paragraph("Thank you for your business!", footer_style))
    elements.append(Paragraph(
        f"Generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}",
        footer_style
    ))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    logger.info(f"PDF generated successfully for invoice: {invoice_number}")
    return pdf_bytes


def save_invoice_pdf(invoice_number: str, pdf_bytes: bytes) -> str:
    ensure_pdf_directory()
    filename = f"invoice_{invoice_number}.pdf"
    filepath = os.path.join(PDF_STORAGE_PATH, filename)

    with open(filepath, "wb") as f:
        f.write(pdf_bytes)

    logger.info(f"PDF saved to: {filepath}")
    return filepath


def get_invoice_pdf_path(invoice_number: str) -> Optional[str]:
    filename = f"invoice_{invoice_number}.pdf"
    filepath = os.path.join(PDF_STORAGE_PATH, filename)

    if os.path.exists(filepath):
        return filepath
    return None
