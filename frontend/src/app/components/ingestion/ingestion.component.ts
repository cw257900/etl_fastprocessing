import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatTabsModule } from '@angular/material/tabs';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { IngestionService } from '../../services/ingestion.service';
import { DataSourceService } from '../../services/data-source.service';
import { DataSource } from '../../models/data-source.model';

@Component({
  selector: 'app-ingestion',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatTabsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatSnackBarModule
  ],
  template: `
    <div class="ingestion-container">
      <h1>Data Ingestion</h1>

      <mat-card>
        <mat-card-content>
          <mat-tab-group>
            <mat-tab label="API Data">
              <div class="tab-content">
                <form [formGroup]="apiForm" (ngSubmit)="submitApiData()">
                  <mat-form-field class="full-width">
                    <mat-label>Data Source</mat-label>
                    <mat-select formControlName="source_id" required>
                      <mat-option *ngFor="let source of apiDataSources" [value]="source.id">
                        {{ source.name }}
                      </mat-option>
                    </mat-select>
                  </mat-form-field>

                  <mat-form-field class="full-width">
                    <mat-label>JSON Data</mat-label>
                    <textarea matInput formControlName="data" rows="10" 
                              placeholder='{"key": "value", "array": [1, 2, 3]}'></textarea>
                  </mat-form-field>

                  <button mat-raised-button color="primary" type="submit" 
                          [disabled]="apiForm.invalid || isLoading">
                    <mat-spinner diameter="20" *ngIf="isLoading"></mat-spinner>
                    Submit API Data
                  </button>
                </form>
              </div>
            </mat-tab>

            <mat-tab label="Swift Messages">
              <div class="tab-content">
                <form [formGroup]="swiftForm" (ngSubmit)="submitSwiftMessage()">
                  <mat-form-field class="full-width">
                    <mat-label>Message Type</mat-label>
                    <mat-select formControlName="message_type" required>
                      <mat-option value="MT103">MT103 - Single Customer Credit Transfer</mat-option>
                      <mat-option value="MT202">MT202 - General Financial Institution Transfer</mat-option>
                      <mat-option value="MT940">MT940 - Customer Statement Message</mat-option>
                      <mat-option value="MT950">MT950 - Statement Message</mat-option>
                    </mat-select>
                  </mat-form-field>

                  <mat-form-field class="full-width">
                    <mat-label>Sender</mat-label>
                    <input matInput formControlName="sender" required>
                  </mat-form-field>

                  <mat-form-field class="full-width">
                    <mat-label>Receiver</mat-label>
                    <input matInput formControlName="receiver" required>
                  </mat-form-field>

                  <mat-form-field class="full-width">
                    <mat-label>Message Content</mat-label>
                    <textarea matInput formControlName="message_content" rows="10" 
                              placeholder=":20:REFERENCE&#10;:32A:YYMMDDCCCAMOUNT&#10;:50K:ORDERING CUSTOMER&#10;:59:BENEFICIARY"></textarea>
                  </mat-form-field>

                  <button mat-raised-button color="primary" type="submit" 
                          [disabled]="swiftForm.invalid || isLoading">
                    <mat-spinner diameter="20" *ngIf="isLoading"></mat-spinner>
                    Submit Swift Message
                  </button>
                </form>
              </div>
            </mat-tab>

            <mat-tab label="Batch Upload">
              <div class="tab-content">
                <form [formGroup]="batchForm" (ngSubmit)="submitBatchFile()">
                  <mat-form-field class="full-width">
                    <mat-label>Data Source (Optional)</mat-label>
                    <mat-select formControlName="source_id">
                      <mat-option value="">None</mat-option>
                      <mat-option *ngFor="let source of batchDataSources" [value]="source.id">
                        {{ source.name }}
                      </mat-option>
                    </mat-select>
                  </mat-form-field>

                  <div class="file-upload">
                    <input type="file" #fileInput (change)="onFileSelected($event)" 
                           accept=".csv,.json,.xlsx,.xls" style="display: none;">
                    <button mat-stroked-button type="button" (click)="fileInput.click()">
                      Choose File
                    </button>
                    <span class="file-name" *ngIf="selectedFile">{{ selectedFile.name }}</span>
                  </div>

                  <div class="file-info" *ngIf="selectedFile">
                    <p>File: {{ selectedFile.name }}</p>
                    <p>Size: {{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB</p>
                    <p>Type: {{ selectedFile.type }}</p>
                  </div>

                  <button mat-raised-button color="primary" type="submit" 
                          [disabled]="!selectedFile || isLoading">
                    <mat-spinner diameter="20" *ngIf="isLoading"></mat-spinner>
                    Upload File
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
    .ingestion-container {
      padding: 20px;
    }

    .tab-content {
      padding: 20px 0;
    }

    .full-width {
      width: 100%;
      margin-bottom: 15px;
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
  `]
})
export class IngestionComponent {
  apiForm: FormGroup;
  swiftForm: FormGroup;
  batchForm: FormGroup;
  
  dataSources: DataSource[] = [];
  selectedFile: File | null = null;
  isLoading = false;

  constructor(
    private fb: FormBuilder,
    private ingestionService: IngestionService,
    private dataSourceService: DataSourceService,
    private snackBar: MatSnackBar
  ) {
    this.apiForm = this.fb.group({
      source_id: ['', Validators.required],
      data: ['', Validators.required]
    });

    this.swiftForm = this.fb.group({
      message_type: ['', Validators.required],
      sender: ['', Validators.required],
      receiver: ['', Validators.required],
      message_content: ['', Validators.required]
    });

    this.batchForm = this.fb.group({
      source_id: ['']
    });

    this.loadDataSources();
  }

  get apiDataSources() {
    return this.dataSources.filter(ds => ds.source_type === 'API');
  }

  get batchDataSources() {
    return this.dataSources.filter(ds => ds.source_type === 'BATCH');
  }

  loadDataSources(): void {
    this.dataSourceService.getDataSources().subscribe({
      next: (sources) => {
        this.dataSources = sources;
      }
    });
  }

  submitApiData(): void {
    if (this.apiForm.valid) {
      this.isLoading = true;
      const formValue = this.apiForm.value;
      
      try {
        const data = JSON.parse(formValue.data);
        const request = {
          source_id: formValue.source_id,
          data: data
        };

        this.ingestionService.ingestApiData(request).subscribe({
          next: (response) => {
            this.isLoading = false;
            this.snackBar.open('API data submitted successfully!', 'Close', { duration: 3000 });
            this.apiForm.reset();
          },
          error: (error) => {
            this.isLoading = false;
            this.snackBar.open('Error submitting API data', 'Close', { duration: 3000 });
          }
        });
      } catch (e) {
        this.isLoading = false;
        this.snackBar.open('Invalid JSON format', 'Close', { duration: 3000 });
      }
    }
  }

  submitSwiftMessage(): void {
    if (this.swiftForm.valid) {
      this.isLoading = true;
      
      this.ingestionService.ingestSwiftMessage(this.swiftForm.value).subscribe({
        next: (response) => {
          this.isLoading = false;
          this.snackBar.open('Swift message submitted successfully!', 'Close', { duration: 3000 });
          this.swiftForm.reset();
        },
        error: (error) => {
          this.isLoading = false;
          this.snackBar.open('Error submitting Swift message', 'Close', { duration: 3000 });
        }
      });
    }
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
    }
  }

  submitBatchFile(): void {
    if (this.selectedFile) {
      this.isLoading = true;
      const sourceId = this.batchForm.value.source_id || undefined;
      
      this.ingestionService.uploadBatchFile(this.selectedFile, sourceId).subscribe({
        next: (response) => {
          this.isLoading = false;
          this.snackBar.open('File uploaded successfully!', 'Close', { duration: 3000 });
          this.selectedFile = null;
          this.batchForm.reset();
        },
        error: (error) => {
          this.isLoading = false;
          this.snackBar.open('Error uploading file', 'Close', { duration: 3000 });
        }
      });
    }
  }
}
