import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class IngestionService {
  private apiUrl = `${environment.apiUrl}/ingestion`;

  constructor(private http: HttpClient) {}

  ingestApiData(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/api`, data);
  }

  ingestSwiftMessage(data: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/swift`, data);
  }

  uploadBatchFile(file: File, sourceId?: number): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (sourceId) {
      formData.append('source_id', sourceId.toString());
    }
    return this.http.post(`${this.apiUrl}/batch`, formData);
  }

  getIngestionStatus(jobId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/status/${jobId}`);
  }
}
