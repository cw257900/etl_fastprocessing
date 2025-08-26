export interface DataSource {
  id: number;
  name: string;
  description?: string;
  source_type: 'API' | 'SWIFT' | 'BATCH';
  connection_config?: any;
  schema_config?: any;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateDataSourceRequest {
  name: string;
  description?: string;
  source_type: 'API' | 'SWIFT' | 'BATCH';
  connection_config?: any;
  schema_config?: any;
}
