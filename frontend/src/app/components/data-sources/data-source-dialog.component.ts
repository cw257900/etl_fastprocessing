import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { DataSourceService } from '../../services/data-source.service';
import { DataSource } from '../../models/data-source.model';

@Component({
  selector: 'app-data-source-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule
  ],
  template: `
    <h2 mat-dialog-title>{{ data.mode === 'create' ? 'Create' : 'Edit' }} Data Source</h2>
    
    <mat-dialog-content>
      <form [formGroup]="dataSourceForm">
        <mat-form-field class="full-width">
          <mat-label>Name</mat-label>
          <input matInput formControlName="name" required>
        </mat-form-field>

        <mat-form-field class="full-width">
          <mat-label>Description</mat-label>
          <textarea matInput formControlName="description" rows="3"></textarea>
        </mat-form-field>

        <mat-form-field class="full-width">
          <mat-label>Source Type</mat-label>
          <mat-select formControlName="source_type" required>
            <mat-option value="API">API</mat-option>
            <mat-option value="SWIFT">Swift Messages</mat-option>
            <mat-option value="BATCH">Batch Files</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field class="full-width" *ngIf="dataSourceForm.get('source_type')?.value === 'API'">
          <mat-label>API Endpoint</mat-label>
          <input matInput formControlName="api_endpoint">
        </mat-form-field>

        <mat-form-field class="full-width" *ngIf="dataSourceForm.get('source_type')?.value === 'SWIFT'">
          <mat-label>Swift Network</mat-label>
          <input matInput formControlName="swift_network">
        </mat-form-field>
      </form>
    </mat-dialog-content>

    <mat-dialog-actions>
      <button mat-button (click)="onCancel()">Cancel</button>
      <button mat-raised-button color="primary" 
              [disabled]="dataSourceForm.invalid || isLoading"
              (click)="onSave()">
        {{ data.mode === 'create' ? 'Create' : 'Update' }}
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .full-width {
      width: 100%;
      margin-bottom: 15px;
    }
  `]
})
export class DataSourceDialogComponent {
  dataSourceForm: FormGroup;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private dataSourceService: DataSourceService,
    private dialogRef: MatDialogRef<DataSourceDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { mode: 'create' | 'edit', dataSource?: DataSource }
  ) {
    this.dataSourceForm = this.fb.group({
      name: [data.dataSource?.name || '', Validators.required],
      description: [data.dataSource?.description || ''],
      source_type: [data.dataSource?.source_type || '', Validators.required],
      api_endpoint: [''],
      swift_network: ['']
    });
  }

  onSave(): void {
    if (this.dataSourceForm.valid) {
      this.isLoading = true;
      const formValue = this.dataSourceForm.value;
      
      const connectionConfig: any = {};
      if (formValue.api_endpoint) {
        connectionConfig.endpoint = formValue.api_endpoint;
      }
      if (formValue.swift_network) {
        connectionConfig.network = formValue.swift_network;
      }

      const dataSourceData = {
        name: formValue.name,
        description: formValue.description,
        source_type: formValue.source_type,
        connection_config: connectionConfig
      };

      const operation = this.data.mode === 'create' 
        ? this.dataSourceService.createDataSource(dataSourceData)
        : this.dataSourceService.updateDataSource(this.data.dataSource!.id, dataSourceData);

      operation.subscribe({
        next: () => {
          this.isLoading = false;
          this.dialogRef.close(true);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error saving data source:', error);
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }
}
