import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ETLService {
  private apiUrl = `${environment.apiUrl}/etl-config`;

  constructor(private http: HttpClient) {}

  getConfigSchemas(): Observable<any> {
    return this.http.get(`${this.apiUrl}/schemas`);
  }

  getConfigSchema(schemaType: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/schemas/${schemaType}`);
  }

  updateConfigSchema(schemaType: string, schemaData: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/schemas/${schemaType}`, schemaData);
  }

  convertETLData(file: File, inputSchema: string = 'input_schema', outputSchema: string = 'output_schema', processingRules: string = 'processing_rules'): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('input_schema', inputSchema);
    formData.append('output_schema', outputSchema);
    formData.append('processing_rules', processingRules);
    return this.http.post(`${this.apiUrl}/convert`, formData);
  }

  getETLJobStatus(jobId: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/processing/jobs/${jobId}`);
  }
}
