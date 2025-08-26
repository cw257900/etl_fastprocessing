import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterModule } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatSidenavModule,
    MatListModule
  ],
  template: `
    <mat-sidenav-container class="sidenav-container">
      <mat-sidenav #drawer class="sidenav" fixedInViewport="true">
        <mat-toolbar>Menu</mat-toolbar>
        <mat-nav-list>
          <a mat-list-item routerLink="/dashboard" routerLinkActive="active">
            <mat-icon>dashboard</mat-icon>
            <span>Dashboard</span>
          </a>
          <a mat-list-item routerLink="/data-sources" routerLinkActive="active">
            <mat-icon>storage</mat-icon>
            <span>Data Sources</span>
          </a>
          <a mat-list-item routerLink="/ingestion" routerLinkActive="active">
            <mat-icon>cloud_upload</mat-icon>
            <span>Data Ingestion</span>
          </a>
          <a mat-list-item routerLink="/processing" routerLinkActive="active">
            <mat-icon>settings</mat-icon>
            <span>Processing Jobs</span>
          </a>
          <a mat-list-item routerLink="/workflow" routerLinkActive="active">
            <mat-icon>approval</mat-icon>
            <span>Workflow</span>
          </a>
          <a mat-list-item routerLink="/lineage" routerLinkActive="active">
            <mat-icon>account_tree</mat-icon>
            <span>Data Lineage</span>
          </a>
          <a mat-list-item routerLink="/exceptions" routerLinkActive="active">
            <mat-icon>error</mat-icon>
            <span>Exceptions</span>
          </a>
        </mat-nav-list>
      </mat-sidenav>

      <mat-sidenav-content>
        <mat-toolbar color="primary">
          <button
            type="button"
            aria-label="Toggle sidenav"
            mat-icon-button
            (click)="drawer.toggle()">
            <mat-icon aria-label="Side nav toggle icon">menu</mat-icon>
          </button>
          <span>ETL Fast Processing</span>
          <span class="spacer"></span>
          <button mat-button *ngIf="authService.isAuthenticated()" (click)="logout()">
            <mat-icon>logout</mat-icon>
            Logout
          </button>
          <button mat-button *ngIf="!authService.isAuthenticated()" routerLink="/login">
            <mat-icon>login</mat-icon>
            Login
          </button>
        </mat-toolbar>
        
        <div class="content">
          <router-outlet></router-outlet>
        </div>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `,
  styles: [`
    .sidenav-container {
      height: 100%;
    }

    .sidenav {
      width: 250px;
    }

    .sidenav .mat-toolbar {
      background: inherit;
    }

    .mat-toolbar.mat-primary {
      position: sticky;
      top: 0;
      z-index: 1;
    }

    .spacer {
      flex: 1 1 auto;
    }

    .content {
      padding: 20px;
      min-height: calc(100vh - 64px);
    }

    .active {
      background-color: rgba(0, 0, 0, 0.04);
    }
  `]
})
export class AppComponent {
  constructor(public authService: AuthService) {}

  logout() {
    this.authService.logout();
  }
}
