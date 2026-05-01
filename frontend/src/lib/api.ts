import type { CompareResponse, ReportResponse, UploadedFileResponse } from "../types";
import { mockCompareResponse, mockReport } from "./mockData";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export async function uploadSubmission(file: File): Promise<UploadedFileResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    throw new Error("Upload failed.");
  }

  return response.json();
}

export async function analyzeCase(reportId: number): Promise<ReportResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ report_id: reportId })
  });

  if (!response.ok) {
    throw new Error("Analysis failed.");
  }

  return response.json();
}

export async function getReport(reportId: number): Promise<ReportResponse> {
  const response = await fetch(`${API_BASE_URL}/report/${reportId}`);
  if (!response.ok) {
    throw new Error("Fetching report failed.");
  }
  return response.json();
}

export async function compareReports(sourceReportId: number, targetReportId: number): Promise<CompareResponse> {
  const response = await fetch(`${API_BASE_URL}/compare`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ source_report_id: sourceReportId, target_report_id: targetReportId })
  });
  if (!response.ok) {
    throw new Error("Comparison failed.");
  }
  return response.json();
}

export function getMockReport(): ReportResponse {
  return mockReport;
}

export function getMockCompareResponse(): CompareResponse {
  return mockCompareResponse;
}

export function getExportUrls(reportId: number, compareToReportId?: number) {
  const suffix = compareToReportId ? `?compare_to_report_id=${compareToReportId}` : "";
  return {
    json: `${API_BASE_URL}/report/${reportId}/export/json${suffix}`,
    pdf: `${API_BASE_URL}/report/${reportId}/export/pdf${suffix}`
  };
}
