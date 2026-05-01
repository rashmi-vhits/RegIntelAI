export type UploadedFileResponse = {
  report_id: number;
  filename: string;
  document_type: string;
  status: string;
};

export type ReportResponse = {
  id: number;
  original_filename: string;
  document_type: string;
  status: string;
  extracted_text: string;
  anonymized_text: string;
  sections: Array<{ heading: string; content: string }>;
  entities: Record<string, unknown>;
  summary: Record<string, unknown>;
  completeness: {
    is_complete: boolean;
    score: number;
    missing_fields: string[];
    recommended_missing_fields?: string[];
    findings?: Array<{ rule_id: string; severity: string; message: string }>;
    review_recommendation?: string;
  };
  classification: {
    label: string;
    confidence: number;
    triggered_rules: string[];
    explanation: string;
  };
  comparison_snapshot: Record<string, unknown>;
  audit_log: Array<Record<string, unknown>>;
  created_at: string;
  updated_at: string;
};

export type ReviewPacket = {
  case_id: string;
  severity: string;
  report_type: string;
  missing_fields: string[];
  recommended_missing_fields?: string[];
  pii_findings: string[];
  recommendation: {
    status: string;
    priority: string;
    action: string;
    basis: string[];
  };
  signoff_present: boolean;
};

export type CompareResult = {
  has_changes: boolean;
  change_count: number;
  summary_banner: string;
  changed_fields: Array<{
    field: string;
    label: string;
    old: string;
    new: string;
    impact: string;
  }>;
  entity_deltas: Record<string, unknown>;
  officer_summary: {
    summary_banner: string;
    officer_summary: string;
    model_provider?: string;
  };
};

export type CompareResponse = {
  source_report_id: number;
  target_report_id: number;
  result: CompareResult;
};
