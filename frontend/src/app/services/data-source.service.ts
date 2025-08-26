import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DataSource, CreateDataSourceRequest } from '../models/data-source.model';

@Injectable({
  providedIn: 'root'
})
export class DataSourceService {
  private apiUrl = `${environment.apiUrl}/data-sources`;

  constructor(private http: HttpClient) {}

  getDataSources(): Observable<DataSource[]> {
    return this.http.get<DataSource[]>(this.apiUrl);
  }

  getDataSource(id: number): Observable<DataSource> {
    return this.http.get<DataSource>(`${this.apiUrl}/${id}`);
  }

  createDataSource(dataSource: CreateDataSourceRequest): Observable<DataSource> {
    return this.http.post<DataSource>(this.apiUrl, dataSource);
  }

  updateDataSource(id: number, dataSource: Partial<DataSource>): Observable<DataSource> {
    return this.http.put<DataSource>(`${this.apiUrl}/${id}`, dataSource);
  }

  deleteDataSource(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
