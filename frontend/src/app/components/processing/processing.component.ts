import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { ProcessingService } from '../../services/processing.service';
import { ProcessingJob } from '../../models/processing-job.model';
import { TransformationDialogComponent } from './transformation-dialog.component';

@Component({
  selector: 'app-processing',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDialogModule
  ],
  template: `
    <div class="processing-container">
      <h1>Processing Jobs</h1>

      <mat-card>
        <mat-card-content>
          <table mat-table [dataSource]="processingJobs" class="full-width">
            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef>Name</th>
              <td mat-cell *matCellDef="let job">{{ job.name }}</td>
            </ng-container>

            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef>Status</th>
              <td mat-cell *matCellDef="let job">
                <mat-chip [class]="'status-chip ' + job.status.toLowerCase()">
                  {{ job.status }}
                </mat-chip>
              </td>
            </ng-container>

            <ng-container matColumnDef="created">
              <th mat-header-cell *matHeaderCellDef>Created</th>
              <td mat-cell *matCellDef="let job">
                {{ job.created_at | date:'short' }}
              </td>
            </ng-container>

            <ng-container matColumnDef="started">
              <th mat-header-cell *matHeaderCellDef>Started</th>
              <td mat-cell *matCellDef="let job">
                {{ job.started_at | date:'short' }}
              </td>
            </ng-container>

            <ng-container matColumnDef="completed">
              <th mat-header-cell *matHeaderCellDef>Completed</th>
              <td mat-cell *matCellDef="let job">
                {{ job.completed_at | date:'short' }}
              </td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef>Actions</th>
              <td mat-cell *matCellDef="let job">
                <button mat-icon-button (click)="openTransformationDialog(job)" 
                        [disabled]="job.status === 'RUNNING'">
                  <mat-icon>settings</mat-icon>
                </button>
                <button mat-icon-button (click)="retryJob(job.id)" 
                        [disabled]="job.status !== 'FAILED'">
                  <mat-icon>refresh</mat-icon>
                </button>
                <button mat-icon-button (click)="viewJobDetails(job)">
                  <mat-icon>visibility</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
          </table>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .processing-container {
      padding: 20px;
    }
  `]
})
export class ProcessingComponent implements OnInit {
  processingJobs: ProcessingJob[] = [];
  displayedColumns = ['name', 'status', 'created', 'started', 'completed', 'actions'];

  constructor(
    private processingService: ProcessingService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadProcessingJobs();
  }

  loadProcessingJobs(): void {
    this.processingService.getProcessingJobs().subscribe({
      next: (jobs) => {
        this.processingJobs = jobs;
      }
    });
  }

  openTransformationDialog(job: ProcessingJob): void {
    const dialogRef = this.dialog.open(TransformationDialogComponent, {
      width: '600px',
      data: { job }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadProcessingJobs();
      }
    });
  }

  retryJob(jobId: number): void {
    this.processingService.retryJob(jobId).subscribe({
      next: () => {
        this.loadProcessingJobs();
      }
    });
  }

  viewJobDetails(job: ProcessingJob): void {
    console.log('Job details:', job);
  }
}
