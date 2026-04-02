/**
 * Frontend Status Type
 */
export type DraftStatus = 'Draft' | 'Reviewed' | 'Rejected';

/**
 * Frontend FAQ Draft Model (normalized from backend)
 */
export interface FaqDraft {
  id: string; // Changed from number to string (faq_id from backend)
  title: string;
  intent: string;
  family: string;
  status: DraftStatus;
  confidence: number;
  caseCount: number;
  updated: string;
}

/**
 * Frontend Evidence Item (derived from backend supporting_evidence)
 */
export interface EvidenceItem {
  id: string;
  source: string;
  summary: string;
  timeAgo: string;
}

/**
 * Frontend FAQ Detail Model (normalized from backend)
 */
export interface FaqDetail {
  id: string; // Changed from number to string
  intent: string;
  updated: string;
  family: string;
  status: DraftStatus;
  reviewNeeded: boolean;
  title: string;
  confidence: number;
  caseCount: number;
  problemStatement: string;
  causeExplanation: string;
  steps: string[];
  edgeCases: string[];
  contactSupport: string;
  evidence: EvidenceItem[];
}

export type FaqDetailUpdate = Pick<
  FaqDetail,
  'title' | 'intent' | 'problemStatement' | 'causeExplanation' | 'steps' | 'edgeCases' | 'contactSupport'
>;

/**
 * Backend Response Types (from /faqs endpoint)
 */

export interface BackendSupportingEvidence {
  case_id: string;
  source_type: string;
  summary: string;
  created_at: string; // ISO datetime
}

export interface BackendFaqContent {
  title: string;
  problem_statement: string;
  cause_explanation: string;
  step_by_step_fix: string[];
  edge_cases: string[];
  when_to_contact_support: string;
}

export interface BackendFaqDraft {
  faq_id: string;
  issue_family_label: string;
  status: 'draft' | 'reviewed' | 'rejected';
  review_needed: boolean;
  confidence_score: number;
  supporting_case_ids: string[];
  supporting_case_count: number;
  supporting_evidence: BackendSupportingEvidence[];
  faq: BackendFaqContent;
}

export interface BackendFaqListResponse {
  total: number;
  faqs: BackendFaqDraft[];
}

/**
 * Mapping Functions
 */

/**
 * Convert backend FaqStatus to frontend DraftStatus
 */
export function mapStatus(status: string): DraftStatus {
  switch (status.toLowerCase()) {
    case 'draft':
      return 'Draft';
    case 'reviewed':
      return 'Reviewed';
    case 'rejected':
      return 'Rejected';
    default:
      return 'Draft';
  }
}

/**
 * Generate relative time string from ISO datetime
 */
export function getTimeAgo(isoDatetime: string): string {
  try {
    const date = new Date(isoDatetime);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);

    if (diffSecs < 60) return 'just now';
    if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m ago`;
    if (diffSecs < 86400) return `${Math.floor(diffSecs / 3600)}h ago`;
    if (diffSecs < 604800) return `${Math.floor(diffSecs / 86400)}d ago`;
    return `${Math.floor(diffSecs / 604800)}w ago`;
  } catch {
    return 'unknown';
  }
}

/**
 * Convert backend FAQDraft to frontend FaqDraft
 */
export function mapBackendToFaqDraft(backend: BackendFaqDraft): FaqDraft {
  return {
    id: backend.faq_id,
    title: backend.faq.title,
    intent: backend.issue_family_label,
    family: backend.issue_family_label,
    status: mapStatus(backend.status),
    confidence: backend.confidence_score,
    caseCount: backend.supporting_case_count,
    updated: backend.supporting_evidence[0]?.created_at || new Date().toISOString(),
  };
}

/**
 * Convert backend FaqDraft to frontend FaqDetail
 */
export function mapBackendToFaqDetail(backend: BackendFaqDraft): FaqDetail {
  const evidence: EvidenceItem[] = backend.supporting_evidence.map((ev) => ({
    id: ev.case_id,
    source: ev.source_type,
    summary: ev.summary,
    timeAgo: getTimeAgo(ev.created_at),
  }));

  return {
    id: backend.faq_id,
    title: backend.faq.title,
    intent: backend.issue_family_label,
    updated: backend.supporting_evidence[0]?.created_at || new Date().toISOString(),
    family: backend.issue_family_label,
    status: mapStatus(backend.status),
    reviewNeeded: backend.review_needed,
    confidence: backend.confidence_score,
    caseCount: backend.supporting_case_count,
    problemStatement: backend.faq.problem_statement,
    causeExplanation: backend.faq.cause_explanation,
    steps: backend.faq.step_by_step_fix,
    edgeCases: backend.faq.edge_cases,
    contactSupport: backend.faq.when_to_contact_support,
    evidence,
  };
}
