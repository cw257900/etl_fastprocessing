import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatStepperModule } from '@angular/material/stepper';
import { MatIconModule } from '@angular/material/icon';
import { ETLService } from '../../services/etl.service';
import { ProcessingService } from '../../services/processing.service';

@Component({
  selector: 'app-etl-converter',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatStepperModule,
    MatIconModule
  ],
  template: `
    <div class="etl-converter-container">
      <h1>ETL Data Converter</h1>

      <mat-card>
        <mat-card-content>
          <mat-stepper [linear]="true" #stepper>
            <mat-step [stepControl]="fileForm" label="Upload File">
              <form [formGroup]="fileForm">
                <div class="file-upload-section">
                  <h3>Select Data File</h3>
                  <div class="file-upload">
                    <input type="file" #fileInput (change)="onFileSelected($event)" 
                           accept=".dat,.csv,.xlsx,.xls" style="display: none;">
                    <button mat-stroked-button type="button" (click)="fileInput.click()">
                      <mat-icon>cloud_upload</mat-icon>
                      Choose File
                    </button>
                    <span class="file-name" *ngIf="selectedFile">{{ selectedFile.name }}</span>
                  </div>

                  <div class="file-info" *ngIf="selectedFile">
                    <p><strong>File:</strong> {{ selectedFile.name }}</p>
                    <p><strong>Size:</strong> {{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB</p>
                    <p><strong>Type:</strong> {{ selectedFile.type || getFileExtension(selectedFile.name) }}</p>
                  </div>
                </div>

                <div class="stepper-buttons">
                  <button mat-raised-button color="primary" matStepperNext 
                          [disabled]="!selectedFile">Next</button>
                </div>
              </form>
            </mat-step>

            <mat-step [stepControl]="configForm" label="Configure ETL">
              <form [formGroup]="configForm">
                <mat-form-field class="full-width">
                  <mat-label>Input Schema</mat-label>
                  <mat-select formControlName="inputSchema" required>
                    <mat-option value="input_schema">Default Input Schema</mat-option>
                  </mat-select>
                </mat-form-field>

                <mat-form-field class="full-width">
                  <mat-label>Output Schema</mat-label>
                  <mat-select formControlName="outputSchema" required>
                    <mat-option value="output_schema">FLEX PP Balance Output</mat-option>
                  </mat-select>
                </mat-form-field>

                <mat-form-field class="full-width">
                  <mat-label>Processing Rules</mat-label>
                  <mat-select formControlName="processingRules" required>
                    <mat-option value="processing_rules">Default Processing Rules</mat-option>
                  </mat-select>
                </mat-form-field>

                <div class="stepper-buttons">
                  <button mat-button matStepperPrevious>Back</button>
                  <button mat-raised-button color="primary" matStepperNext 
                          [disabled]="configForm.invalid">Next</button>
                </div>
              </form>
            </mat-step>

            <mat-step label="Process & Monitor">
              <div class="processing-section">
                <div *ngIf="!conversionStarted" class="conversion-summary">
                  <h3>Conversion Summary</h3>
                  <p><strong>File:</strong> {{ selectedFile?.name }}</p>
                  <p><strong>Input Schema:</strong> {{ configForm.value.inputSchema }}</p>
                  <p><strong>Output Schema:</strong> {{ configForm.value.outputSchema }}</p>
                  <p><strong>Processing Rules:</strong> {{ configForm.value.processingRules }}</p>
                  
                  <button mat-raised-button color="primary" (click)="startConversion()" 
                          [disabled]="isProcessing">
                    <mat-icon>play_arrow</mat-icon>
                    Start ETL Conversion
                  </button>
                </div>

                <div *ngIf="conversionStarted" class="conversion-status">
                  <div *ngIf="isProcessing" class="processing-indicator">
                    <mat-spinner diameter="40"></mat-spinner>
                    <p>Processing ETL conversion...</p>
                    <p>Job ID: {{ currentJobId }}</p>
                  </div>

                  <div *ngIf="conversionResult && !isProcessing" class="conversion-result">
                    <div class="result-success" *ngIf="conversionResult.status === 'success'">
                      <mat-icon color="primary">check_circle</mat-icon>
                      <h3>Conversion Completed Successfully!</h3>
                      <p><strong>Records Processed:</strong> {{ conversionResult.records_processed }}</p>
                      <p><strong>Output File:</strong> {{ conversionResult.output_file }}</p>
                      <button mat-raised-button color="accent" (click)="downloadResult()">
                        <mat-icon>download</mat-icon>
                        Download Result
                      </button>
                    </div>

                    <div class="result-error" *ngIf="conversionResult.status === 'error'">
                      <mat-icon color="warn">error</mat-icon>
                      <h3>Conversion Failed</h3>
                      <p>{{ conversionResult.error }}</p>
                    </div>
                  </div>
                </div>

                <div class="stepper-buttons">
                  <button mat-button matStepperPrevious [disabled]="isProcessing">Back</button>
                  <button mat-raised-button color="primary" (click)="resetConverter()" 
                          *ngIf="conversionResult && !isProcessing">
                    <mat-icon>refresh</mat-icon>
                    Convert Another File
                  </button>
                </div>
              </div>
            </mat-step>
          </mat-stepper>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .etl-converter-container {
      padding: 20px;
    }

    .file-upload-section {
      margin: 20px 0;
    }

    .file-upload {
      margin: 15px 0;
      display: flex;
      align-items: center;
      gap: 15px;
    }

    .file-name {
      color: #666;
      font-style: italic;
    }

    .file-info {
      background-color: #f5f5f5;
      padding: 15px;
      border-radius: 4px;
      margin: 15px 0;
    }

    .file-info p {
      margin: 5px 0;
    }

    .full-width {
      width: 100%;
      margin-bottom: 15px;
    }

    .stepper-buttons {
      margin-top: 20px;
      display: flex;
      gap: 10px;
    }

    .processing-section {
      padding: 20px 0;
    }

    .conversion-summary {
      background-color: #f9f9f9;
      padding: 20px;
      border-radius: 4px;
      margin-bottom: 20px;
    }

    .processing-indicator {
      text-align: center;
      padding: 40px;
    }

    .processing-indicator mat-spinner {
      margin: 0 auto 20px;
    }

    .conversion-result {
      text-align: center;
      padding: 20px;
    }

    .result-success {
      color: #4caf50;
    }

    .result-error {
      color: #f44336;
    }

    .result-success mat-icon,
    .result-error mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
      margin-bottom: 10px;
    }
  `]
})
export class ETLConverterComponent {
  fileForm: FormGroup;
  configForm: FormGroup;
  selectedFile: File | null = null;
  isProcessing = false;
  conversionStarted = false;
  conversionResult: any = null;
  currentJobId: number | null = null;

  constructor(
    private fb: FormBuilder,
    private etlService: ETLService,
    private processingService: ProcessingService,
    private snackBar: MatSnackBar
  ) {
    this.fileForm = this.fb.group({
      file: ['', Validators.required]
    });

    this.configForm = this.fb.group({
      inputSchema: ['input_schema', Validators.required],
      outputSchema: ['output_schema', Validators.required],
      processingRules: ['processing_rules', Validators.required]
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.fileForm.patchValue({ file: file.name });
    }
  }

  getFileExtension(filename: string): string {
    return filename.split('.').pop()?.toUpperCase() || 'Unknown';
  }

  startConversion(): void {
    if (this.selectedFile && this.configForm.valid) {
      this.isProcessing = true;
      this.conversionStarted = true;
      
      const formValue = this.configForm.value;
      
      this.etlService.convertETLData(
        this.selectedFile,
        formValue.inputSchema,
        formValue.outputSchema,
        formValue.processingRules
      ).subscribe({
        next: (response) => {
          this.currentJobId = response.job_id;
          this.monitorJobProgress(response.job_id);
        },
        error: (error) => {
          this.isProcessing = false;
          this.conversionResult = {
            status: 'error',
            error: error.error?.detail || 'Conversion failed'
          };
          this.snackBar.open('ETL conversion failed', 'Close', { duration: 3000 });
        }
      });
    }
  }

  monitorJobProgress(jobId: number): void {
    const checkStatus = () => {
      this.etlService.getETLJobStatus(jobId).subscribe({
        next: (job) => {
          if (job.status === 'COMPLETED') {
            this.isProcessing = false;
            this.conversionResult = {
              status: 'success',
              records_processed: job.output_data?.records_processed || 0,
              output_file: job.output_data?.output_file || 'converted_output.csv'
            };
            this.snackBar.open('ETL conversion completed successfully!', 'Close', { duration: 3000 });
          } else if (job.status === 'FAILED') {
            this.isProcessing = false;
            this.conversionResult = {
              status: 'error',
              error: job.error_message || 'Conversion failed'
            };
            this.snackBar.open('ETL conversion failed', 'Close', { duration: 3000 });
          } else if (job.status === 'RUNNING' || job.status === 'PENDING') {
            setTimeout(checkStatus, 2000);
          }
        },
        error: () => {
          this.isProcessing = false;
          this.conversionResult = {
            status: 'error',
            error: 'Failed to monitor job progress'
          };
        }
      });
    };
    
    setTimeout(checkStatus, 1000);
  }

  downloadResult(): void {
    this.snackBar.open('Download functionality would be implemented here', 'Close', { duration: 3000 });
  }

  resetConverter(): void {
    this.selectedFile = null;
    this.conversionStarted = false;
    this.conversionResult = null;
    this.currentJobId = null;
    this.isProcessing = false;
    this.fileForm.reset();
    this.configForm.patchValue({
      inputSchema: 'input_schema',
      outputSchema: 'output_schema',
      processingRules: 'processing_rules'
    });
  }
}
