import type { CompareResponse, ReportResponse } from "../types";

export const mockReport: ReportResponse = {
  id: 6,
  original_filename: "sae_case_006_incomplete.txt",
  document_type: "txt",
  status: "analyzed",
  extracted_text:
    "Patient Name: Rohan Kulkarni\nPhone: 9345612780\nEmail: rohan.kulkarni38@example.com\nAddress: Hyderabad, Telangana\nAdverse Event Term(s): Severe gastrointestinal bleeding, dizziness",
  anonymized_text:
    "Patient Name: [REDACTED_PATIENT_NAME]\nPhone: [REDACTED_PHONE]\nEmail: [REDACTED_EMAIL]\nAddress: [REDACTED_ADDRESS]\nAdverse Event Term(s): Severe gastrointestinal bleeding, dizziness",
  sections: [
    {
      heading: "General",
      content: "Incomplete SAE submission used for UI demo."
    }
  ],
  entities: {
    form_fields: {
      pt_id: "PT-88412",
      patient_name: "Rohan Kulkarni",
      intervention_type: "Medication: GLX-17",
      adverse_event_terms: "Severe gastrointestinal bleeding, dizziness",
      type_of_report: "Initial"
    }
  },
  summary: {
    case_overview: "Case involves an incomplete hospitalization report linked to GLX-17.",
    narrative_excerpt:
      "The participant required urgent stabilization and transfusion support after repeated episodes of bleeding.",
    review_packet: {
      case_id: "PT-88412",
      severity: "hospitalization - prolonged",
      report_type: "Initial",
      missing_fields: [
        "sae_onset_date",
        "relationship_of_event_to_intervention",
        "signature_of_principal_investigator",
        "date"
      ],
      recommended_missing_fields: ["sae_stop_date", "outcome_of_serious_adverse_event"],
      pii_findings: ["patient_name", "phone", "email", "address"],
      recommendation: {
        status: "Needs follow-up clarification",
        priority: "Medium",
        action: "Hold for follow-up clarification. Submission is not review-ready due to missing required information.",
        basis: [
          "Missing mandatory field: sae onset date",
          "Missing mandatory field: relationship of event to intervention",
          "Missing mandatory field: signature of principal investigator",
          "Serious event category: Hospitalization - prolonged"
        ]
      },
      signoff_present: false
    },
    anonymization: {
      matched_patterns: ["patient_name", "phone", "email", "address"]
    }
  },
  completeness: {
    is_complete: false,
    score: 36,
    missing_fields: [
      "sae_onset_date",
      "relationship_of_event_to_intervention",
      "signature_of_principal_investigator",
      "date"
    ],
    recommended_missing_fields: ["sae_stop_date", "outcome_of_serious_adverse_event"],
    findings: [
      {
        rule_id: "SAE-001",
        severity: "high",
        message: "Onset date should be present Missing: sae_onset_date."
      },
      {
        rule_id: "SAE-005",
        severity: "high",
        message: "Investigator sign-off required before submission Missing: signature_of_principal_investigator, date."
      }
    ],
    review_recommendation: "manual_review"
  },
  classification: {
    label: "hospitalization - prolonged",
    confidence: 0.93,
    triggered_rules: ["Used declared SAE category from source form."],
    explanation: "Rule-first severity classification using form category with keyword fallback."
  },
  comparison_snapshot: {},
  audit_log: [],
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

export const mockCompareResponse: CompareResponse = {
  source_report_id: 1,
  target_report_id: 2,
  result: {
    has_changes: true,
    change_count: 5,
    summary_banner: "5 material changes detected",
    changed_fields: [
      {
        field: "sae_onset_date",
        label: "Onset Date",
        old: "12/Mar/2025",
        new: "11/Mar/2025",
        impact: "Timeline changed"
      },
      {
        field: "sae_stop_date",
        label: "Stop Date",
        old: "18/Mar/2025",
        new: "20/Mar/2025",
        impact: "Resolution window updated"
      },
      {
        field: "relationship_of_event_to_intervention",
        label: "Relationship",
        old: "Possible",
        new: "Probable",
        impact: "Causality strengthened"
      },
      {
        field: "outcome_of_serious_adverse_event",
        label: "Outcome",
        old: "Missing",
        new: "Recovering; liver enzymes trending downward at discharge.",
        impact: "Follow-up clarity improved"
      },
      {
        field: "type_of_report",
        label: "Report Type",
        old: "Initial",
        new: "Follow-up",
        impact: "Submission stage advanced"
      }
    ],
    entity_deltas: {},
    officer_summary: {
      summary_banner: "5 material changes detected",
      officer_summary:
        "The revised report advances the case from initial submission to follow-up, strengthens causality from Possible to Probable, and adds outcome plus laboratory detail that improves clinical review context.",
      model_provider: "ollama"
    }
  }
};
