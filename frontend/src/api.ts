const API_BASE = import.meta.env.VITE_API_BASE_URL?.trim() || 'http://localhost:8000';

const TOKEN_KEY = 'slm_access_token';

/** Persist the JWT access token from a login response. */
export function setAuthToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

/** Remove the stored JWT token (logout). */
export function clearAuthToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

/** Return the stored JWT token, or null if not logged in. */
export function getAuthToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

function resolveApiUrl(path: string): string {
  if (!path.startsWith('/')) {
    return `${API_BASE || ''}/${path}`;
  }

  if (API_BASE) {
    return `${API_BASE.replace(/\/$/, '')}${path}`;
  }

  return path;
}

export async function apiCall<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || undefined);
  if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(resolveApiUrl(path), {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorText = await response.text();
    let message = errorText || `Request failed (${response.status})`;
    try {
      const parsed = JSON.parse(errorText);
      if (typeof parsed.detail === 'string') message = parsed.detail;
      else if (Array.isArray(parsed.detail)) message = parsed.detail.map((item: { msg?: string }) => item.msg || 'Invalid request').join(', ');
    } catch {
      // Keep the raw response when the server does not return JSON.
    }

    if (response.status === 401) {
      clearAuthToken();
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}
