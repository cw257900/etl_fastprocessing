import { Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  {
    path: 'login',
    loadComponent: () => import('./components/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register',
    loadComponent: () => import('./components/register/register.component').then(m => m.RegisterComponent)
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'data-sources',
    loadComponent: () => import('./components/data-sources/data-sources.component').then(m => m.DataSourcesComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'ingestion',
    loadComponent: () => import('./components/ingestion/ingestion.component').then(m => m.IngestionComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'processing',
    loadComponent: () => import('./components/processing/processing.component').then(m => m.ProcessingComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'workflow',
    loadComponent: () => import('./components/workflow/workflow.component').then(m => m.WorkflowComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'lineage',
    loadComponent: () => import('./components/lineage/lineage.component').then(m => m.LineageComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'exceptions',
    loadComponent: () => import('./components/exceptions/exceptions.component').then(m => m.ExceptionsComponent),
    canActivate: [AuthGuard]
  },
  { path: '**', redirectTo: '/dashboard' }
];
