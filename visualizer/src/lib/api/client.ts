import { auth } from '$lib/stores/auth.store';
import { toastStore as toast } from '$lib/stores/toast.store';
import { get } from 'svelte/store';

const BASE_URL = 'http://localhost:8000';

type RequestMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

class ApiClient {
  private async request<T>(
    endpoint: string,
    method: RequestMethod,
    options: RequestOptions = {}
  ): Promise<T> {
    const { params, headers, ...customConfig } = options;

    // Build URL with query params
    const url = new URL(`${BASE_URL}${endpoint}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, value);
        }
      });
    }

    // Get token
    const { token } = get(auth);

    const isFormData = options.body instanceof FormData || options.body instanceof URLSearchParams;

    const config: RequestInit = {
      method,
      headers: {
        ...(!isFormData ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(headers as Record<string, string>),
      },
      ...customConfig,
    };

    try {
      const response = await fetch(url.toString(), config);

      if (!response.ok) {
        // Handle 401 Unauthorized
        if (response.status === 401) {
          auth.logout();
          toast.error('Session expired. Please login again.');
          throw new Error('Unauthorized');
        }

        // Try to parse error message from backend
        let errorMessage = 'An error occurred';
        try {
          const errorData = await response.json();
          // Handle FastAPI validation errors (array of errors)
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map((e: any) => e.msg).join(', ');
          } else {
            errorMessage = errorData.detail || errorData.message || errorMessage;
          }
        } catch {
          errorMessage = response.statusText;
        }

        throw new Error(errorMessage);
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return {} as T;
      }

      return await response.json();
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      // Don't toast for 401 as we handled it above
      if (message !== 'Unauthorized') {
        toast.error(message);
      }
      throw error;
    }
  }

  get<T>(endpoint: string, options?: RequestOptions) {
    return this.request<T>(endpoint, 'GET', options);
  }

  post<T>(endpoint: string, body?: any, options?: RequestOptions) {
    const isFormData = body instanceof FormData || body instanceof URLSearchParams;
    return this.request<T>(endpoint, 'POST', {
      ...options,
      body: isFormData ? body : JSON.stringify(body),
    });
  }

  put<T>(endpoint: string, body?: any, options?: RequestOptions) {
    const isFormData = body instanceof FormData || body instanceof URLSearchParams;
    return this.request<T>(endpoint, 'PUT', {
      ...options,
      body: isFormData ? body : JSON.stringify(body),
    });
  }

  delete<T>(endpoint: string, options?: RequestOptions) {
    return this.request<T>(endpoint, 'DELETE', options);
  }

  patch<T>(endpoint: string, body?: any, options?: RequestOptions) {
    const isFormData = body instanceof FormData || body instanceof URLSearchParams;
    return this.request<T>(endpoint, 'PATCH', {
      ...options,
      body: isFormData ? body : JSON.stringify(body),
    });
  }
}

export const api = new ApiClient();
