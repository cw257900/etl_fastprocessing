import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { WorkflowService } from '../../services/workflow.service';
import { WorkflowApproval } from '../../models/workflow.model';

@Component({
  selector: 'app-workflow',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatSnackBarModule
  ],
  template: `
    <div class="workflow-container">
      <h1>Workflow Approvals</h1>

      <mat-card>
        <mat-card-content>
          <table mat-table [dataSource]="approvals" class="full-width">
            <ng-container matColumnDef="job_id">
              <th mat-header-cell *matHeaderCellDef>Job ID</th>
              <td mat-cell *matCellDef="let approval">{{ approval.job_id }}</td>
            </ng-container>

            <ng-container matColumnDef="type">
              <th mat-header-cell *matHeaderCellDef>Type</th>
              <td mat-cell *matCellDef="let approval">
                <mat-chip>{{ approval.approval_type }}</mat-chip>
              </td>
            </ng-container>

            <ng-container matColumnDef="state">
              <th mat-header-cell *matHeaderCellDef>State</th>
              <td mat-cell *matCellDef="let approval">
                <mat-chip [class]="'state-' + approval.state.toLowerCase()">
                  {{ approval.state }}
                </mat-chip>
              </td>
            </ng-container>

            <ng-container matColumnDef="submitted">
              <th mat-header-cell *matHeaderCellDef>Submitted</th>
              <td mat-cell *matCellDef="let approval">
                {{ approval.submitted_at | date:'short' }}
              </td>
            </ng-container>

            <ng-container matColumnDef="comments">
              <th mat-header-cell *matHeaderCellDef>Comments</th>
              <td mat-cell *matCellDef="let approval">
                {{ approval.comments || 'No comments' }}
              </td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef>Actions</th>
              <td mat-cell *matCellDef="let approval">
                <button mat-raised-button color="primary" 
                        (click)="approveJob(approval.id)"
                        [disabled]="approval.state !== 'PENDING'">
                  Approve
                </button>
                <button mat-raised-button color="warn" 
                        (click)="rejectJob(approval.id)"
                        [disabled]="approval.state !== 'PENDING'">
                  Reject
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
    .workflow-container {
      padding: 20px;
    }

    .state-pending { background-color: #ff9800; color: white; }
    .state-approved { background-color: #4caf50; color: white; }
    .state-rejected { background-color: #f44336; color: white; }
    .state-cancelled { background-color: #9e9e9e; color: white; }

    button {
      margin-right: 10px;
    }
  `]
})
export class WorkflowComponent implements OnInit {
  approvals: WorkflowApproval[] = [];
  displayedColumns = ['job_id', 'type', 'state', 'submitted', 'comments', 'actions'];

  constructor(
    private workflowService: WorkflowService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadApprovals();
  }

  loadApprovals(): void {
    this.workflowService.getPendingApprovals().subscribe({
      next: (approvals) => {
        this.approvals = approvals;
      }
    });
  }

  approveJob(approvalId: number): void {
    const comments = prompt('Enter approval comments (optional):');
    
    this.workflowService.approveJob(approvalId, comments || undefined).subscribe({
      next: () => {
        this.snackBar.open('Job approved successfully', 'Close', { duration: 3000 });
        this.loadApprovals();
      },
      error: (error) => {
        this.snackBar.open('Error approving job', 'Close', { duration: 3000 });
      }
    });
  }

  rejectJob(approvalId: number): void {
    const comments = prompt('Enter rejection reason:');
    
    if (comments) {
      this.workflowService.rejectJob(approvalId, comments).subscribe({
        next: () => {
          this.snackBar.open('Job rejected', 'Close', { duration: 3000 });
          this.loadApprovals();
        },
        error: (error) => {
          this.snackBar.open('Error rejecting job', 'Close', { duration: 3000 });
        }
      });
    }
  }
}
