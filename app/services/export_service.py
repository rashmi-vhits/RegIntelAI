from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.config import settings
from app.models.report import AnalysisReport
from app.services.comparison_service import compare_reports
from app.services.review_service import build_recommendation
from app.utils.storage import ensure_directories


def build_officer_packet(report: AnalysisReport, comparison_report: AnalysisReport | None = None) -> dict[str, Any]:
    form_fields = ((report.entities or {}).get("form_fields") or {}) if isinstance(report.entities, dict) else {}
    summary = report.summary or {}
    review_packet = summary.get("review_packet", {})
    anonymization = summary.get("anonymization", {})

    comparison_result = compare_reports(comparison_report, report) if comparison_report is not None else None
    recommendation = build_recommendation(form_fields, report.completeness or {}, report.classification or {}, comparison_result)

    packet = {
        "case_header": {
            "case_id": review_packet.get("case_id", form_fields.get("pt_id", report.id)),
            "source_format": _format_source_format(report.document_type),
            "report_type": review_packet.get("report_type", form_fields.get("type_of_report", "Unknown")),
            "severity": _format_severity(report.classification.get("label", "unknown")),
            "priority": recommendation.get("priority", "Medium"),
            "review_status": recommendation.get("status", "Ready for medical review"),
            "date_processed": _utc_now(),
        },
        "executive_summary": {
            "narrative_summary": summary.get("case_overview", ""),
            "drug_or_device": _clean_intervention(form_fields.get("intervention_type", "Unknown")),
            "event_summary": form_fields.get("adverse_event_terms", "Unknown"),
        },
        "completeness_assessment": {
            "score": report.completeness.get("score"),
            "missing_required_fields": report.completeness.get("missing_fields", []),
            "missing_recommended_fields": report.completeness.get("recommended_missing_fields", []),
        },
        "privacy_redaction_findings": {
            "pii_detected": anonymization.get("matched_patterns", review_packet.get("pii_findings", [])),
            "redaction_applied": bool(report.anonymized_text),
        },
        "severity_classification": {
            "label": _format_severity(report.classification.get("label")),
            "basis": report.classification.get("triggered_rules", []),
            "evidence": summary.get("evidence_snippet", summary.get("narrative_excerpt", "")),
        },
        "recommendation": recommendation,
        "version_comparison": comparison_result,
    }
    return packet


def export_packet_json(report: AnalysisReport, comparison_report: AnalysisReport | None = None) -> tuple[dict[str, Any], str]:
    packet = build_officer_packet(report, comparison_report)
    return packet, f"report_{report.id}_officer_packet.json"


def export_packet_pdf(report: AnalysisReport, comparison_report: AnalysisReport | None = None) -> tuple[str, str]:
    ensure_directories()
    packet = build_officer_packet(report, comparison_report)
    output_path = Path(settings.export_dir) / f"report_{report.id}_officer_packet.pdf"
    _render_pdf(packet, output_path)
    return str(output_path), output_path.name


def _render_pdf(packet: dict[str, Any], output_path: Path) -> None:
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("PacketTitle", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16, spaceAfter=10)
    section = ParagraphStyle("PacketSection", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, textColor=colors.HexColor("#243746"), spaceAfter=6)
    bullet = ParagraphStyle("PacketBullet", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=12, leftIndent=12)
    body = styles["BodyText"]
    body.fontName = "Helvetica"
    body.fontSize = 9
    body.leading = 12

    story = [
        Paragraph("RegIntel AI Officer Review Packet", title),
        Paragraph(_header_line(packet["case_header"]), body),
        Spacer(1, 8),
    ]

    story.extend(_section_block("Executive Summary", packet["executive_summary"], body, section))
    story.extend(_section_block("Completeness Assessment", packet["completeness_assessment"], body, section))
    story.extend(_section_block("Privacy / Redaction Findings", packet["privacy_redaction_findings"], body, section))
    story.extend(_section_block("Severity Classification", packet["severity_classification"], body, section))
    story.extend(_recommendation_block(packet["recommendation"], body, bullet, section))

    if packet.get("version_comparison"):
        comparison = packet["version_comparison"]
        story.append(Paragraph("Version Comparison", section))
        story.append(Paragraph(comparison.get("summary_banner", "No comparison summary"), body))
        story.append(Spacer(1, 6))
        table_data = [["Field", "Previous Value", "Updated Value", "Impact"]]
        for item in comparison.get("changed_fields", []):
            table_data.append([item["label"], item["old"], item["new"], item["impact"]])
        if len(table_data) > 1:
            table = Table(table_data, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6edf3")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#243746")),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b7c5d3")),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            story.append(table)
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Officer Comparison Summary:</b>", body))
        story.append(Spacer(1, 3))
        story.append(Paragraph(comparison.get("officer_summary", {}).get("officer_summary", ""), body))

    doc.build(story)


def _section_block(title: str, payload: dict[str, Any], body: ParagraphStyle, section: ParagraphStyle) -> list:
    block = [Paragraph(title, section)]
    for key, value in payload.items():
        if value in (None, "", []):
            continue
        if isinstance(value, list):
            value_text = "; ".join(_display_value(item) for item in value)
        else:
            value_text = _display_value(value)
        block.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {value_text}", body))
        block.append(Spacer(1, 4))
    return block


def _recommendation_block(payload: dict[str, Any], body: ParagraphStyle, bullet: ParagraphStyle, section: ParagraphStyle) -> list:
    block = [Paragraph("Recommendation", section)]
    for key in ("status", "priority", "action"):
        value = payload.get(key)
        if value:
            block.append(Paragraph(f"<b>{key.replace('_', ' ').title()}:</b> {_display_value(value)}", body))
            block.append(Spacer(1, 4))

    basis = payload.get("basis", [])
    if basis:
        block.append(Paragraph("<b>Basis:</b>", body))
        block.append(Spacer(1, 3))
        for item in basis:
            block.append(Paragraph(f"• {_display_value(item)}", bullet))
            block.append(Spacer(1, 2))
    return block


def _header_line(header: dict[str, Any]) -> str:
    return (
        f"Case ID: {header['case_id']} | Source Format: {header['source_format']} | "
        f"Report Type: {header['report_type']} | Severity: {header['severity']} | "
        f"Priority: {header['priority']} | Review Status: {header['review_status']} | "
        f"Date Processed: {header['date_processed']}"
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _format_source_format(document_type: str) -> str:
    mapping = {
        "txt": "Text Submission",
        "pdf": "PDF Submission",
        "docx": "Word Submission",
    }
    return mapping.get(str(document_type).lower(), str(document_type).upper())


def _format_severity(value: Any) -> str:
    text = str(value or "Unknown").strip()
    parts = [part.strip() for part in text.split("-") if part.strip()]
    if not parts:
        return "Unknown"
    return " - ".join(part[:1].upper() + part[1:] for part in parts)


def _clean_intervention(value: str) -> str:
    first_line = str(value or "Unknown").split("\n")[0].strip()
    first_line = first_line.replace("Medication:", "").replace("Device:", "").strip()
    return first_line or "Unknown"


def _display_value(value: Any) -> str:
    if isinstance(value, str) and value:
        return _format_severity(value) if value == value.lower() and " - " in value else value
    return str(value)
