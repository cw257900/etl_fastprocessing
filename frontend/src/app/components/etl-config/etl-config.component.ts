import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ETLService } from '../../services/etl.service';

@Component({
  selector: 'app-etl-config',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatTabsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSnackBarModule,
    MatProgressSpinnerModule
  ],
  template: `
    <div class="etl-config-container">
      <h1>ETL Configuration Management</h1>

      <mat-card>
        <mat-card-content>
          <mat-tab-group>
            <mat-tab label="Input Schema">
              <div class="tab-content">
                <form [formGroup]="inputSchemaForm" (ngSubmit)="updateInputSchema()">
                  <mat-form-field class="full-width">
                    <mat-label>Input Schema Configuration</mat-label>
                    <textarea matInput formControlName="schema" rows="20" 
                              placeholder="JSON configuration for input schema"></textarea>
                  </mat-form-field>
                  <button mat-raised-button color="primary" type="submit" 
                          [disabled]="inputSchemaForm.invalid || isLoading">
                    <mat-spinner diameter="20" *ngIf="isLoading"></mat-spinner>
                    Update Input Schema
                  </button>
                </form>
              </div>
            </mat-tab>

            <mat-tab label="Output Schema">
              <div class="tab-content">
                <form [formGroup]="outputSchemaForm" (ngSubmit)="updateOutputSchema()">
                  <mat-form-field class="full-width">
                    <mat-label>Output Schema Configuration</mat-label>
                    <textarea matInput formControlName="schema" rows="20" 
                              placeholder="JSON configuration for output schema"></textarea>
                  </mat-form-field>
                  <button mat-raised-button color="primary" type="submit" 
                          [disabled]="outputSchemaForm.invalid || isLoading">
                    <mat-spinner diameter="20" *ngIf="isLoading"></mat-spinner>
                    Update Output Schema
                  </button>
                </form>
              </div>
            </mat-tab>

            <mat-tab label="Processing Rules">
              <div class="tab-content">
                <form [formGroup]="processingRulesForm" (ngSubmit)="updateProcessingRules()">
                  <mat-form-field class="full-width">
                    <mat-label>Processing Rules Configuration</mat-label>
                    <textarea matInput formControlName="schema" rows="20" 
                              placeholder="JSON configuration for processing rules"></textarea>
                  </mat-form-field>
                  <button mat-raised-button color="primary" type="submit" 
                          [disabled]="processingRulesForm.invalid || isLoading">
                    <mat-spinner diameter="20" *ngIf="isLoading"></mat-spinner>
                    Update Processing Rules
                  </button>
                </form>
              </div>
            </mat-tab>
          </mat-tab-group>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .etl-config-container {
      padding: 20px;
    }

    .tab-content {
      padding: 20px 0;
    }

    .full-width {
      width: 100%;
      margin-bottom: 15px;
    }
  `]
})
export class ETLConfigComponent implements OnInit {
  inputSchemaForm: FormGroup;
  outputSchemaForm: FormGroup;
  processingRulesForm: FormGroup;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private etlService: ETLService,
    private snackBar: MatSnackBar
  ) {
    this.inputSchemaForm = this.fb.group({
      schema: ['']
    });

    this.outputSchemaForm = this.fb.group({
      schema: ['']
    });

    this.processingRulesForm = this.fb.group({
      schema: ['']
    });
  }

  ngOnInit(): void {
    this.loadSchemas();
  }

  loadSchemas(): void {
    this.etlService.getConfigSchema('input_schema').subscribe({
      next: (schema) => {
        this.inputSchemaForm.patchValue({
          schema: JSON.stringify(schema, null, 2)
        });
      }
    });

    this.etlService.getConfigSchema('output_schema').subscribe({
      next: (schema) => {
        this.outputSchemaForm.patchValue({
          schema: JSON.stringify(schema, null, 2)
        });
      }
    });

    this.etlService.getConfigSchema('processing_rules').subscribe({
      next: (schema) => {
        this.processingRulesForm.patchValue({
          schema: JSON.stringify(schema, null, 2)
        });
      }
    });
  }

  updateInputSchema(): void {
    if (this.inputSchemaForm.valid) {
      this.isLoading = true;
      try {
        const schemaData = JSON.parse(this.inputSchemaForm.value.schema);
        this.etlService.updateConfigSchema('input_schema', schemaData).subscribe({
          next: () => {
            this.isLoading = false;
            this.snackBar.open('Input schema updated successfully!', 'Close', { duration: 3000 });
          },
          error: () => {
            this.isLoading = false;
            this.snackBar.open('Error updating input schema', 'Close', { duration: 3000 });
          }
        });
      } catch (e) {
        this.isLoading = false;
        this.snackBar.open('Invalid JSON format', 'Close', { duration: 3000 });
      }
    }
  }

  updateOutputSchema(): void {
    if (this.outputSchemaForm.valid) {
      this.isLoading = true;
      try {
        const schemaData = JSON.parse(this.outputSchemaForm.value.schema);
        this.etlService.updateConfigSchema('output_schema', schemaData).subscribe({
          next: () => {
            this.isLoading = false;
            this.snackBar.open('Output schema updated successfully!', 'Close', { duration: 3000 });
          },
          error: () => {
            this.isLoading = false;
            this.snackBar.open('Error updating output schema', 'Close', { duration: 3000 });
          }
        });
      } catch (e) {
        this.isLoading = false;
        this.snackBar.open('Invalid JSON format', 'Close', { duration: 3000 });
      }
    }
  }

  updateProcessingRules(): void {
    if (this.processingRulesForm.valid) {
      this.isLoading = true;
      try {
        const schemaData = JSON.parse(this.processingRulesForm.value.schema);
        this.etlService.updateConfigSchema('processing_rules', schemaData).subscribe({
          next: () => {
            this.isLoading = false;
            this.snackBar.open('Processing rules updated successfully!', 'Close', { duration: 3000 });
          },
          error: () => {
            this.isLoading = false;
            this.snackBar.open('Error updating processing rules', 'Close', { duration: 3000 });
          }
        });
      } catch (e) {
        this.isLoading = false;
        this.snackBar.open('Invalid JSON format', 'Close', { duration: 3000 });
      }
    }
  }
}
