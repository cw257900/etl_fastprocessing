import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIconModule } from '@angular/material/icon';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-lineage',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatExpansionModule,
    MatIconModule
  ],
  template: `
    <div class="lineage-container">
      <h1>Data Lineage</h1>

      <mat-card>
        <mat-card-content>
          <form [formGroup]="searchForm" (ngSubmit)="searchLineage()">
            <mat-form-field class="full-width">
              <mat-label>Job ID</mat-label>
              <input matInput formControlName="jobId" type="number" required>
            </mat-form-field>
            
            <button mat-raised-button color="primary" type="submit" 
                    [disabled]="searchForm.invalid || isLoading">
              Search Lineage
            </button>
          </form>
        </mat-card-content>
      </mat-card>

      <mat-card *ngIf="lineageData">
        <mat-card-header>
          <mat-card-title>Data Lineage for Job {{ lineageData.job_id }}</mat-card-title>
        </mat-card-header>
        
        <mat-card-content>
          <div class="lineage-summary">
            <p><strong>Total Events:</strong> {{ lineageData.total_events }}</p>
            <p><strong>Transformations:</strong> {{ lineageData.transformations?.length || 0 }}</p>
          </div>

          <mat-accordion>
            <mat-expansion-panel *ngFor="let event of lineageData.events; let i = index">
              <mat-expansion-panel-header>
                <mat-panel-title>
                  <mat-icon>{{ getEventIcon(event.event_type) }}</mat-icon>
                  {{ event.event_type | titlecase }}
                </mat-panel-title>
                <mat-panel-description>
                  {{ event.timestamp | date:'medium' }}
                </mat-panel-description>
              </mat-expansion-panel-header>
              
              <div class="event-details">
                <h4>Metadata:</h4>
                <pre>{{ event.metadata | json }}</pre>
                
                <div *ngIf="event.input_schema">
                  <h4>Input Schema:</h4>
                  <pre>{{ event.input_schema | json }}</pre>
                </div>
                
                <div *ngIf="event.output_schema">
                  <h4>Output Schema:</h4>
                  <pre>{{ event.output_schema | json }}</pre>
                </div>
                
                <div *ngIf="event.transformation_details">
                  <h4>Transformation Details:</h4>
                  <pre>{{ event.transformation_details | json }}</pre>
                </div>
              </div>
            </mat-expansion-panel>
          </mat-accordion>

          <div class="data-flow" *ngIf="lineageData.data_flow">
            <h3>Data Flow Timeline</h3>
            <div class="flow-step" *ngFor="let step of lineageData.data_flow">
              <div class="step-number">{{ step.step }}</div>
              <div class="step-content">
                <strong>{{ step.event_type | titlecase }}</strong>
                <p>{{ step.description }}</p>
                <small>{{ step.timestamp | date:'medium' }}</small>
              </div>
            </div>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .lineage-container {
      padding: 20px;
    }

    .full-width {
      width: 100%;
      margin-bottom: 15px;
    }

    .lineage-summary {
      background-color: #f5f5f5;
      padding: 15px;
      border-radius: 4px;
      margin-bottom: 20px;
    }

    .event-details {
      padding: 15px 0;
    }

    .event-details h4 {
      margin: 15px 0 5px 0;
      color: #1976d2;
    }

    .event-details pre {
      background-color: #f5f5f5;
      padding: 10px;
      border-radius: 4px;
      overflow-x: auto;
      font-size: 12px;
    }

    .data-flow {
      margin-top: 30px;
    }

    .flow-step {
      display: flex;
      align-items: flex-start;
      margin: 15px 0;
      padding: 15px;
      border-left: 3px solid #1976d2;
      background-color: #f9f9f9;
    }

    .step-number {
      background-color: #1976d2;
      color: white;
      border-radius: 50%;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 15px;
      font-weight: bold;
    }

    .step-content {
      flex: 1;
    }

    .step-content p {
      margin: 5px 0;
      color: #666;
    }

    .step-content small {
      color: #999;
    }

    mat-expansion-panel-header mat-icon {
      margin-right: 10px;
    }
  `]
})
export class LineageComponent implements OnInit {
  searchForm: FormGroup;
  lineageData: any = null;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient
  ) {
    this.searchForm = this.fb.group({
      jobId: ['']
    });
  }

  ngOnInit(): void {}

  searchLineage(): void {
    if (this.searchForm.valid) {
      this.isLoading = true;
      const jobId = this.searchForm.value.jobId;
      
      this.http.get(`${environment.apiUrl}/lineage/trace/${jobId}`).subscribe({
        next: (response: any) => {
          this.isLoading = false;
          this.lineageData = response.trace;
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error fetching lineage:', error);
        }
      });
    }
  }

  getEventIcon(eventType: string): string {
    switch (eventType) {
      case 'ingestion': return 'cloud_upload';
      case 'transformation': return 'transform';
      case 'output': return 'cloud_download';
      case 'approval_submitted': return 'send';
      case 'approval_approved': return 'check_circle';
      case 'approval_rejected': return 'cancel';
      default: return 'event';
    }
  }
}
