import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RouterModule } from '@angular/router';
import { ProcessingService } from '../../services/processing.service';
import { ExceptionService } from '../../services/exception.service';
import { WorkflowService } from '../../services/workflow.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatIconModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    RouterModule
  ],
  template: `
    <div class="dashboard-container">
      <h1>ETL Dashboard</h1>
      
      <div class="stats-grid">
        <mat-card class="stat-card">
          <mat-card-header>
            <mat-icon>work</mat-icon>
            <mat-card-title>Processing Jobs</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-number">{{ jobStats.total || 0 }}</div>
            <div class="stat-details">
              <span class="running">{{ jobStats.running || 0 }} Running</span>
              <span class="failed">{{ jobStats.failed || 0 }} Failed</span>
            </div>
          </mat-card-content>
          <mat-card-actions>
            <button mat-button routerLink="/processing">View All</button>
          </mat-card-actions>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-header>
            <mat-icon>error</mat-icon>
            <mat-card-title>Exceptions</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-number">{{ exceptionStats.total || 0 }}</div>
            <div class="stat-details">
              <span class="unresolved">{{ exceptionStats.unresolved || 0 }} Unresolved</span>
              <span class="critical">{{ exceptionStats.critical || 0 }} Critical</span>
            </div>
          </mat-card-content>
          <mat-card-actions>
            <button mat-button routerLink="/exceptions">View All</button>
          </mat-card-actions>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-header>
            <mat-icon>approval</mat-icon>
            <mat-card-title>Pending Approvals</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-number">{{ approvalStats.pending || 0 }}</div>
            <div class="stat-details">
              <span>Awaiting Review</span>
            </div>
          </mat-card-content>
          <mat-card-actions>
            <button mat-button routerLink="/workflow">Review</button>
          </mat-card-actions>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-header>
            <mat-icon>storage</mat-icon>
            <mat-card-title>Data Sources</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-number">{{ dataSourceStats.total || 0 }}</div>
            <div class="stat-details">
              <span class="active">{{ dataSourceStats.active || 0 }} Active</span>
            </div>
          </mat-card-content>
          <mat-card-actions>
            <button mat-button routerLink="/data-sources">Manage</button>
          </mat-card-actions>
        </mat-card>
      </div>

      <div class="quick-actions">
        <h2>Quick Actions</h2>
        <div class="action-buttons">
          <button mat-raised-button color="primary" routerLink="/data-sources">
            <mat-icon>add</mat-icon>
            Add Data Source
          </button>
          <button mat-raised-button color="accent" routerLink="/ingestion">
            <mat-icon>cloud_upload</mat-icon>
            Upload Data
          </button>
          <button mat-raised-button routerLink="/lineage">
            <mat-icon>account_tree</mat-icon>
            View Lineage
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container {
      padding: 20px;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin: 20px 0;
    }

    .stat-card {
      text-align: center;
    }

    .stat-card mat-card-header {
      justify-content: center;
      align-items: center;
      gap: 10px;
    }

    .stat-number {
      font-size: 2.5em;
      font-weight: bold;
      color: #1976d2;
    }

    .stat-details {
      display: flex;
      justify-content: space-around;
      margin-top: 10px;
      font-size: 0.9em;
    }

    .running { color: #2196f3; }
    .failed { color: #f44336; }
    .unresolved { color: #ff9800; }
    .critical { color: #f44336; }
    .active { color: #4caf50; }

    .quick-actions {
      margin-top: 40px;
    }

    .action-buttons {
      display: flex;
      gap: 15px;
      flex-wrap: wrap;
      margin-top: 15px;
    }

    .action-buttons button {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  `]
})
export class DashboardComponent implements OnInit {
  jobStats: any = {};
  exceptionStats: any = {};
  approvalStats: any = {};
  dataSourceStats: any = {};
  isLoading = true;

  constructor(
    private processingService: ProcessingService,
    private exceptionService: ExceptionService,
    private workflowService: WorkflowService
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  private loadDashboardData(): void {
    this.processingService.getProcessingJobs().subscribe({
      next: (jobs) => {
        this.jobStats = {
          total: jobs.length,
          running: jobs.filter(j => j.status === 'RUNNING').length,
          failed: jobs.filter(j => j.status === 'FAILED').length
        };
      }
    });

    this.exceptionService.getExceptions().subscribe({
      next: (exceptions) => {
        this.exceptionStats = {
          total: exceptions.length,
          unresolved: exceptions.filter(e => !e.resolved).length,
          critical: exceptions.filter(e => e.severity === 'CRITICAL').length
        };
      }
    });

    this.workflowService.getPendingApprovals().subscribe({
      next: (approvals) => {
        this.approvalStats = {
          pending: approvals.filter(a => a.state === 'PENDING').length
        };
      }
    });

    this.dataSourceStats = { total: 0, active: 0 };
    this.isLoading = false;
  }
}
