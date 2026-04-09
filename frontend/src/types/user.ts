export interface User {
  id: number;
  email: string;
  display_name: string;
  role: 'admin' | 'contributor';
  is_blocked: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterData {
  email: string;
  password: string;
  display_name: string;
}

export interface LoginData {
  email: string;
  password: string;
}
