import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ProcessingJob, TransformationRule } from '../models/processing-job.model';

@Injectable({
  providedIn: 'root'
})
export class ProcessingService {
  private apiUrl = `${environment.apiUrl}/processing`;

  constructor(private http: HttpClient) {}

  getProcessingJobs(): Observable<ProcessingJob[]> {
    return this.http.get<ProcessingJob[]>(`${this.apiUrl}/jobs`);
  }

  getProcessingJob(id: number): Observable<ProcessingJob> {
    return this.http.get<ProcessingJob>(`${this.apiUrl}/jobs/${id}`);
  }

  applyTransformationRules(jobId: number, rules: TransformationRule[]): Observable<any> {
    return this.http.post(`${this.apiUrl}/jobs/${jobId}/transform`, rules);
  }

  retryJob(jobId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/jobs/${jobId}/retry`, {});
  }
}
