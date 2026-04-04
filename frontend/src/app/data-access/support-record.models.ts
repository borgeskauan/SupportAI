export interface SupportRecord {
  id: string;
  sourceType: string;
  createdAt: string;
  status: string;
  caseSummary: string;
  resolutionText: string;
  customerMessage: string;
  productArea: string;
  tags: string[];
  severity: string;
  sentiment: string;
}

export interface SupportRecordListResponse {
  total: number;
  records: SupportRecord[];
}

export interface BackendSupportRecord {
  id: string;
  source_type: string;
  created_at: string;
  status: string;
  case_summary: string;
  resolution_text: string;
  customer_message: string;
  product_area: string;
  tags: string[];
  severity: string;
  sentiment: string;
}

export interface BackendSupportRecordListResponse {
  total: number;
  records: BackendSupportRecord[];
}

export function mapBackendToSupportRecord(backend: BackendSupportRecord): SupportRecord {
  return {
    id: backend.id,
    sourceType: backend.source_type,
    createdAt: backend.created_at,
    status: backend.status,
    caseSummary: backend.case_summary,
    resolutionText: backend.resolution_text,
    customerMessage: backend.customer_message,
    productArea: backend.product_area,
    tags: backend.tags,
    severity: backend.severity,
    sentiment: backend.sentiment,
  };
}

export function localizeSupportRecordStatus(status: string): string {
  switch (status.toLowerCase()) {
    case 'resolved':
      return $localize`:@@record_status_resolved:Resolved`;
    case 'open':
      return $localize`:@@record_status_open:Open`;
    case 'pending':
      return $localize`:@@record_status_pending:Pending`;
    default:
      return formatToken(status);
  }
}

export function localizeSupportRecordSource(sourceType: string): string {
  switch (sourceType.toLowerCase()) {
    case 'ticket':
      return $localize`:@@record_source_ticket:Ticket`;
    case 'chat':
      return $localize`:@@record_source_chat:Chat`;
    case 'email':
      return $localize`:@@record_source_email:Email`;
    default:
      return formatToken(sourceType);
  }
}

export function localizeSupportRecordSeverity(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'low':
      return $localize`:@@record_severity_low:Low`;
    case 'medium':
      return $localize`:@@record_severity_medium:Medium`;
    case 'high':
      return $localize`:@@record_severity_high:High`;
    case 'critical':
      return $localize`:@@record_severity_critical:Critical`;
    default:
      return formatToken(severity);
  }
}

export function localizeSupportRecordSentiment(sentiment: string): string {
  switch (sentiment.toLowerCase()) {
    case 'frustrated':
      return $localize`:@@record_sentiment_frustrated:Frustrated`;
    case 'neutral':
      return $localize`:@@record_sentiment_neutral:Neutral`;
    case 'satisfied':
      return $localize`:@@record_sentiment_satisfied:Satisfied`;
    case 'confused':
      return $localize`:@@record_sentiment_confused:Confused`;
    case 'urgent':
      return $localize`:@@record_sentiment_urgent:Urgent`;
    default:
      return formatToken(sentiment);
  }
}

function formatToken(value: string): string {
  return value
    .split(/[_\s-]+/)
    .filter((token) => token.length > 0)
    .map((token) => token.charAt(0).toUpperCase() + token.slice(1))
    .join(' ');
}
