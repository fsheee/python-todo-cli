import {
  User,
  Task,
  RegisterInput,
  LoginInput,
  AuthResponse,
  TaskCreateInput,
  TaskUpdateInput,
  TaskListResponse,
  ApiError,
} from '@/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    console.log('[API] setToken called:', token ? `${token.substring(0, 20)}...` : 'null');
    this.token = token;
    if (token) {
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', token);
        console.log('[API] Token stored in localStorage');
      }
    } else {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
        console.log('[API] Token removed from localStorage');
      }
    }
  }

  getToken(): string | null {
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('auth_token');
      console.log('[API] getToken - localStorage:', storedToken ? `${storedToken.substring(0, 20)}...` : 'null');
      console.log('[API] getToken - this.token:', this.token ? `${this.token.substring(0, 20)}...` : 'null');
      if (storedToken) {
        this.token = storedToken;
      }
    }
    console.log('[API] getToken returning:', this.token ? `${this.token.substring(0, 20)}...` : 'null');
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    console.log('[API] request to:', endpoint);
    console.log('[API] request - token present:', !!token);
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    };
    console.log('[API] request - Authorization header:', (headers as Record<string, string>)['Authorization'] ? 'present' : 'missing');

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let error: ApiError;
      try {
        error = await response.json();
      } catch {
        error = { detail: `HTTP ${response.status}: ${response.statusText}` };
      }
      throw error;
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  // Auth Methods
  async register(data: RegisterInput): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setToken(response.token);
    return response;
  }

  async login(data: LoginInput): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setToken(response.token);
    return response;
  }

  async logout(): Promise<void> {
    try {
      await this.request<void>('/api/auth/logout', {
        method: 'POST',
      });
    } finally {
      this.setToken(null);
    }
  }

  async getSession(): Promise<User | null> {
    try {
      const response = await this.request<{ user: User }>('/api/auth/session');
      return response.user;
    } catch {
      return null;
    }
  }

  // Task Methods
  async getTasks(userId: string): Promise<Task[]> {
    const response = await this.request<TaskListResponse>(
      `/api/${userId}/tasks`
    );
    return response.tasks;
  }

  async getTask(userId: string, taskId: string): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`);
  }

  async createTask(userId: string, data: TaskCreateInput): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTask(
    userId: string,
    taskId: string,
    data: TaskUpdateInput
  ): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteTask(userId: string, taskId: string): Promise<void> {
    return this.request<void>(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async toggleComplete(userId: string, taskId: string): Promise<Task> {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  }
}

export const api = new ApiClient();
