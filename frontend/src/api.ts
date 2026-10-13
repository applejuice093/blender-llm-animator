/**
 * Shared API helpers for the studios.
 *
 * The backend URL is read from the VITE_API_URL env var at build/dev time
 * (see frontend/.env.example) and falls back to the default uvicorn port.
 */
export const API_URL: string = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/+$/, '');

type ValidationIssue = { loc?: (string | number)[]; msg?: string };

/** Turn a FastAPI error `detail` (string or 422 issue list) into readable text. */
export function formatApiError(detail: unknown, fallback = 'Request failed'): string {
  if (typeof detail === 'string' && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const parts = (detail as ValidationIssue[]).map((issue) => {
      const field = issue.loc?.filter((p) => p !== 'body').join('.') ?? '';
      return field ? `${field}: ${issue.msg ?? 'invalid'}` : issue.msg ?? 'invalid';
    });
    if (parts.length) return parts.join('; ');
  }
  return fallback;
}

/** POST JSON and return the parsed body, throwing a readable Error on non-2xx. */
export async function postJson<T = any>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return parseResponse<T>(response);
}

/** GET JSON and return the parsed body, throwing a readable Error on non-2xx. */
export async function getJson<T = any>(path: string): Promise<T> {
  return parseResponse<T>(await fetch(`${API_URL}${path}`));
}

async function parseResponse<T>(response: Response): Promise<T> {
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(formatApiError(data?.detail, `HTTP ${response.status}`));
  }
  return data as T;
}
