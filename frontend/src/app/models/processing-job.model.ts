export interface ProcessingJob {
  id: number;
  name: string;
  description?: string;
  source_id?: number;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  started_at?: string;
  completed_at?: string;
  created_at: string;
  transformation_rules?: any;
  error_message?: string;
}

export interface TransformationRule {
  rule_type: string;
  parameters: any;
  description?: string;
}
