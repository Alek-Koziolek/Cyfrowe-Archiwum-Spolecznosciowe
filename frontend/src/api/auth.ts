import api from './client';
import type {
  LoginData,
  RegisterData,
  TokenResponse,
  User,
} from '../types/user';

export async function register(data: RegisterData): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>('/auth/register', data);
  return response.data;
}

export async function login(data: LoginData): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>('/auth/login', data);
  return response.data;
}

export async function getMe(): Promise<User> {
  const response = await api.get<User>('/auth/me');
  return response.data;
}

export async function refreshToken(
  refresh_token: string,
): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>('/auth/refresh', null, {
    params: { refresh_token },
  });
  return response.data;
}
