import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DataException, ExceptionResolution } from '../models/exception.model';

@Injectable({
  providedIn: 'root'
})
export class ExceptionService {
  private apiUrl = `${environment.apiUrl}/exceptions`;

  constructor(private http: HttpClient) {}

  getExceptions(resolved?: boolean): Observable<DataException[]> {
    const params = resolved !== undefined ? { resolved: resolved.toString() } : {};
    return this.http.get<DataException[]>(this.apiUrl, { params });
  }

  getException(id: number): Observable<DataException> {
    return this.http.get<DataException>(`${this.apiUrl}/${id}`);
  }

  resolveException(id: number, resolution: ExceptionResolution): Observable<any> {
    return this.http.post(`${this.apiUrl}/${id}/resolve`, resolution);
  }

  getJobExceptions(jobId: number): Observable<DataException[]> {
    return this.http.get<DataException[]>(`${this.apiUrl}/job/${jobId}`);
  }
}
