import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { DataSourceService } from '../../services/data-source.service';
import { DataSource } from '../../models/data-source.model';
import { DataSourceDialogComponent } from './data-source-dialog.component';

@Component({
  selector: 'app-data-sources',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatChipsModule,
    MatDialogModule
  ],
  template: `
    <div class="data-sources-container">
      <div class="header">
        <h1>Data Sources</h1>
        <button mat-raised-button color="primary" (click)="openCreateDialog()">
          <mat-icon>add</mat-icon>
          Add Data Source
        </button>
      </div>

      <mat-card>
        <mat-card-content>
          <table mat-table [dataSource]="dataSources" class="full-width">
            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef>Name</th>
              <td mat-cell *matCellDef="let source">{{ source.name }}</td>
            </ng-container>

            <ng-container matColumnDef="type">
              <th mat-header-cell *matHeaderCellDef>Type</th>
              <td mat-cell *matCellDef="let source">
                <mat-chip [class]="'type-' + source.source_type.toLowerCase()">
                  {{ source.source_type }}
                </mat-chip>
              </td>
            </ng-container>

            <ng-container matColumnDef="status">
              <th mat-header-cell *matHeaderCellDef>Status</th>
              <td mat-cell *matCellDef="let source">
                <mat-chip [class]="source.is_active ? 'active' : 'inactive'">
                  {{ source.is_active ? 'Active' : 'Inactive' }}
                </mat-chip>
              </td>
            </ng-container>

            <ng-container matColumnDef="created">
              <th mat-header-cell *matHeaderCellDef>Created</th>
              <td mat-cell *matCellDef="let source">
                {{ source.created_at | date:'short' }}
              </td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef>Actions</th>
              <td mat-cell *matCellDef="let source">
                <button mat-icon-button (click)="editDataSource(source)">
                  <mat-icon>edit</mat-icon>
                </button>
                <button mat-icon-button color="warn" (click)="deleteDataSource(source.id)">
                  <mat-icon>delete</mat-icon>
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
    .data-sources-container {
      padding: 20px;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .type-api { background-color: #2196f3; color: white; }
    .type-swift { background-color: #ff9800; color: white; }
    .type-batch { background-color: #4caf50; color: white; }
    
    .active { background-color: #4caf50; color: white; }
    .inactive { background-color: #9e9e9e; color: white; }
  `]
})
export class DataSourcesComponent implements OnInit {
  dataSources: DataSource[] = [];
  displayedColumns = ['name', 'type', 'status', 'created', 'actions'];

  constructor(
    private dataSourceService: DataSourceService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.loadDataSources();
  }

  loadDataSources(): void {
    this.dataSourceService.getDataSources().subscribe({
      next: (sources) => {
        this.dataSources = sources;
      },
      error: (error) => {
        console.error('Error loading data sources:', error);
      }
    });
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(DataSourceDialogComponent, {
      width: '500px',
      data: { mode: 'create' }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadDataSources();
      }
    });
  }

  editDataSource(source: DataSource): void {
    const dialogRef = this.dialog.open(DataSourceDialogComponent, {
      width: '500px',
      data: { mode: 'edit', dataSource: source }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.loadDataSources();
      }
    });
  }

  deleteDataSource(id: number): void {
    if (confirm('Are you sure you want to delete this data source?')) {
      this.dataSourceService.deleteDataSource(id).subscribe({
        next: () => {
          this.loadDataSources();
        },
        error: (error) => {
          console.error('Error deleting data source:', error);
        }
      });
    }
  }
}
