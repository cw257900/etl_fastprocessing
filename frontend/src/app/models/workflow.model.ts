export interface WorkflowApproval {
  id: number;
  job_id: number;
  approval_type: 'DATA_PROMOTION' | 'SCHEMA_CHANGE' | 'JOB_EXECUTION';
  state: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCELLED';
  submitted_by: number;
  approved_by?: number;
  comments?: string;
  submitted_at: string;
  approved_at?: string;
}

export interface ApprovalRequest {
  approval_type: 'DATA_PROMOTION' | 'SCHEMA_CHANGE' | 'JOB_EXECUTION';
  comments?: string;
}
