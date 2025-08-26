export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: 'ADMIN' | 'DATA_ENGINEER' | 'ANALYST' | 'VIEWER';
  is_active: boolean;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role?: 'ADMIN' | 'DATA_ENGINEER' | 'ANALYST' | 'VIEWER';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}
