import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormArray, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { ProcessingService } from '../../services/processing.service';
import { ProcessingJob } from '../../models/processing-job.model';

@Component({
  selector: 'app-transformation-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <h2 mat-dialog-title>Apply Transformation Rules</h2>
    
    <mat-dialog-content>
      <p><strong>Job:</strong> {{ data.job.name }}</p>
      
      <form [formGroup]="transformationForm">
        <div formArrayName="rules">
          <div *ngFor="let rule of rulesArray.controls; let i = index" 
               [formGroupName]="i" class="rule-group">
            <mat-form-field>
              <mat-label>Rule Type</mat-label>
              <mat-select formControlName="rule_type" required>
                <mat-option value="remove_duplicates">Remove Duplicates</mat-option>
                <mat-option value="handle_nulls">Handle Nulls</mat-option>
                <mat-option value="normalize_text">Normalize Text</mat-option>
                <mat-option value="validate_data_types">Validate Data Types</mat-option>
                <mat-option value="filter_rows">Filter Rows</mat-option>
                <mat-option value="aggregate_data">Aggregate Data</mat-option>
              </mat-select>
            </mat-form-field>

            <mat-form-field>
              <mat-label>Description</mat-label>
              <input matInput formControlName="description">
            </mat-form-field>

            <mat-form-field>
              <mat-label>Parameters (JSON)</mat-label>
              <textarea matInput formControlName="parameters" rows="3" 
                        placeholder='{"key": "value"}'></textarea>
            </mat-form-field>

            <button mat-icon-button color="warn" (click)="removeRule(i)" type="button">
              <mat-icon>delete</mat-icon>
            </button>
          </div>
        </div>

        <button mat-button type="button" (click)="addRule()">
          <mat-icon>add</mat-icon>
          Add Rule
        </button>
      </form>
    </mat-dialog-content>

    <mat-dialog-actions>
      <button mat-button (click)="onCancel()">Cancel</button>
      <button mat-raised-button color="primary" 
              [disabled]="transformationForm.invalid || isLoading"
              (click)="onApply()">
        Apply Transformations
      </button>
    </mat-dialog-actions>
  `,
  styles: [`
    .rule-group {
      border: 1px solid #ddd;
      padding: 15px;
      margin: 10px 0;
      border-radius: 4px;
      position: relative;
    }

    .rule-group button[mat-icon-button] {
      position: absolute;
      top: 10px;
      right: 10px;
    }

    mat-form-field {
      width: 100%;
      margin-bottom: 10px;
    }
  `]
})
export class TransformationDialogComponent {
  transformationForm: FormGroup;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private processingService: ProcessingService,
    private dialogRef: MatDialogRef<TransformationDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { job: ProcessingJob }
  ) {
    this.transformationForm = this.fb.group({
      rules: this.fb.array([])
    });

    this.addRule();
  }

  get rulesArray(): FormArray {
    return this.transformationForm.get('rules') as FormArray;
  }

  addRule(): void {
    const ruleGroup = this.fb.group({
      rule_type: ['', Validators.required],
      description: [''],
      parameters: ['{}', Validators.required]
    });
    this.rulesArray.push(ruleGroup);
  }

  removeRule(index: number): void {
    this.rulesArray.removeAt(index);
  }

  onApply(): void {
    if (this.transformationForm.valid) {
      this.isLoading = true;
      
      const rules = this.rulesArray.value.map((rule: any) => ({
        rule_type: rule.rule_type,
        description: rule.description,
        parameters: JSON.parse(rule.parameters)
      }));

      this.processingService.applyTransformationRules(this.data.job.id, rules).subscribe({
        next: () => {
          this.isLoading = false;
          this.dialogRef.close(true);
        },
        error: (error) => {
          this.isLoading = false;
          console.error('Error applying transformations:', error);
        }
      });
    }
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }
}
