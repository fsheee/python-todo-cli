import { api } from './api';
import { User, RegisterInput, LoginInput, AuthResponse } from '@/types';

export async function signIn(
  email: string,
  password: string
): Promise<AuthResponse> {
  const data: LoginInput = { email, password };
  return api.login(data);
}

export async function signUp(data: RegisterInput): Promise<AuthResponse> {
  return api.register(data);
}

export async function signOut(): Promise<void> {
  return api.logout();
}

export async function getSession(): Promise<User | null> {
  return api.getSession();
}

export function getToken(): string | null {
  return api.getToken();
}

export function setToken(token: string | null): void {
  api.setToken(token);
}

export function isAuthenticated(): boolean {
  return !!api.getToken();
}
