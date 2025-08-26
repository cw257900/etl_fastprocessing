import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatTabsModule } from '@angular/material/tabs';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ExceptionService } from '../../services/exception.service';
import { DataException } from '../../models/exception.model';

@Component({
  selector: 'app-exceptions',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatTabsModule,
    MatSnackBarModule
  ],
  template: `
    <div class="exceptions-container">
      <h1>Data Exceptions</h1>

      <mat-card>
        <mat-card-content>
          <mat-tab-group (selectedTabChange)="onTabChange($event)">
            <mat-tab label="Unresolved">
              <div class="tab-content">
                <table mat-table [dataSource]="unresolvedExceptions" class="full-width">
                  <ng-container matColumnDef="severity">
                    <th mat-header-cell *matHeaderCellDef>Severity</th>
                    <td mat-cell *matCellDef="let exception">
                      <mat-chip [class]="'severity-chip ' + exception.severity.toLowerCase()">
                        {{ exception.severity }}
                      </mat-chip>
                    </td>
                  </ng-container>

                  <ng-container matColumnDef="type">
                    <th mat-header-cell *matHeaderCellDef>Type</th>
                    <td mat-cell *matCellDef="let exception">{{ exception.exception_type }}</td>
                  </ng-container>

                  <ng-container matColumnDef="message">
                    <th mat-header-cell *matHeaderCellDef>Message</th>
                    <td mat-cell *matCellDef="let exception">
                      <div class="message-cell">{{ exception.message }}</div>
                    </td>
                  </ng-container>

                  <ng-container matColumnDef="job_id">
                    <th mat-header-cell *matHeaderCellDef>Job ID</th>
                    <td mat-cell *matCellDef="let exception">{{ exception.job_id || 'N/A' }}</td>
                  </ng-container>

                  <ng-container matColumnDef="timestamp">
                    <th mat-header-cell *matHeaderCellDef>Timestamp</th>
                    <td mat-cell *matCellDef="let exception">
                      {{ exception.timestamp | date:'short' }}
                    </td>
                  </ng-container>

                  <ng-container matColumnDef="actions">
                    <th mat-header-cell *matHeaderCellDef>Actions</th>
                    <td mat-cell *matCellDef="let exception">
                      <button mat-raised-button color="primary" 
                              (click)="resolveException(exception.id)">
                        Resolve
                      </button>
                    </td>
                  </ng-container>

                  <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
                  <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
                </table>
              </div>
            </mat-tab>

            <mat-tab label="Resolved">
              <div class="tab-content">
                <table mat-table [dataSource]="resolvedExceptions" class="full-width">
                  <ng-container matColumnDef="severity">
                    <th mat-header-cell *matHeaderCellDef>Severity</th>
                    <td mat-cell *matCellDef="let exception">
                      <mat-chip [class]="'severity-chip ' + exception.severity.toLowerCase()">
                        {{ exception.severity }}
                      </mat-chip>
                    </td>
                  </ng-container>

                  <ng-container matColumnDef="type">
                    <th mat-header-cell *matHeaderCellDef>Type</th>
                    <td mat-cell *matCellDef="let exception">{{ exception.exception_type }}</td>
                  </ng-container>

                  <ng-container matColumnDef="message">
                    <th mat-header-cell *matHeaderCellDef>Message</th>
                    <td mat-cell *matCellDef="let exception">
                      <div class="message-cell">{{ exception.message }}</div>
                    </td>
                  </ng-container>

                  <ng-container matColumnDef="resolved_at">
                    <th mat-header-cell *matHeaderCellDef>Resolved At</th>
                    <td mat-cell *matCellDef="let exception">
                      {{ exception.resolved_at | date:'short' }}
                    </td>
                  </ng-container>

                  <ng-container matColumnDef="resolution_notes">
                    <th mat-header-cell *matHeaderCellDef>Resolution Notes</th>
                    <td mat-cell *matCellDef="let exception">
                      <div class="message-cell">{{ exception.resolution_notes || 'No notes' }}</div>
                    </td>
                  </ng-container>

                  <tr mat-header-row *matHeaderRowDef="resolvedDisplayedColumns"></tr>
                  <tr mat-row *matRowDef="let row; columns: resolvedDisplayedColumns;"></tr>
                </table>
              </div>
            </mat-tab>
          </mat-tab-group>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .exceptions-container {
      padding: 20px;
    }

    .tab-content {
      padding: 20px 0;
    }

    .message-cell {
      max-width: 300px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .severity-chip.low { background-color: #4caf50; color: white; }
    .severity-chip.medium { background-color: #ff9800; color: white; }
    .severity-chip.high { background-color: #ff5722; color: white; }
    .severity-chip.critical { background-color: #f44336; color: white; }
  `]
})
export class ExceptionsComponent implements OnInit {
  unresolvedExceptions: DataException[] = [];
  resolvedExceptions: DataException[] = [];
  displayedColumns = ['severity', 'type', 'message', 'job_id', 'timestamp', 'actions'];
  resolvedDisplayedColumns = ['severity', 'type', 'message', 'resolved_at', 'resolution_notes'];

  constructor(
    private exceptionService: ExceptionService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadUnresolvedExceptions();
  }

  onTabChange(event: any): void {
    if (event.index === 0) {
      this.loadUnresolvedExceptions();
    } else {
      this.loadResolvedExceptions();
    }
  }

  loadUnresolvedExceptions(): void {
    this.exceptionService.getExceptions(false).subscribe({
      next: (exceptions) => {
        this.unresolvedExceptions = exceptions;
      }
    });
  }

  loadResolvedExceptions(): void {
    this.exceptionService.getExceptions(true).subscribe({
      next: (exceptions) => {
        this.resolvedExceptions = exceptions;
      }
    });
  }

  resolveException(exceptionId: number): void {
    const resolutionNotes = prompt('Enter resolution notes:');
    
    if (resolutionNotes) {
      this.exceptionService.resolveException(exceptionId, { resolution_notes: resolutionNotes }).subscribe({
        next: () => {
          this.snackBar.open('Exception resolved successfully', 'Close', { duration: 3000 });
          this.loadUnresolvedExceptions();
        },
        error: (error) => {
          this.snackBar.open('Error resolving exception', 'Close', { duration: 3000 });
        }
      });
    }
  }
}
