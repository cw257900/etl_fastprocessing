export interface DataException {
  id: number;
  job_id?: number;
  exception_type: string;
  message: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  metadata?: any;
  resolved: boolean;
  resolved_by?: number;
  resolution_notes?: string;
  timestamp: string;
  resolved_at?: string;
}

export interface ExceptionResolution {
  resolution_notes: string;
}
