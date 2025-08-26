import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { WorkflowApproval, ApprovalRequest } from '../models/workflow.model';

@Injectable({
  providedIn: 'root'
})
export class WorkflowService {
  private apiUrl = `${environment.apiUrl}/workflow`;

  constructor(private http: HttpClient) {}

  getPendingApprovals(): Observable<WorkflowApproval[]> {
    return this.http.get<WorkflowApproval[]>(`${this.apiUrl}/approvals`);
  }

  submitForApproval(jobId: number, request: ApprovalRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/approvals/${jobId}/submit`, request);
  }

  approveJob(approvalId: number, comments?: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/approvals/${approvalId}/approve`, { comments });
  }

  rejectJob(approvalId: number, comments: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/approvals/${approvalId}/reject`, { comments });
  }
}
