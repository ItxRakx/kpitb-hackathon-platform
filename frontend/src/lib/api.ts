import { getAccessToken, clearTokens } from "./auth";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export interface RequestOptions extends Omit<RequestInit, "body" | "headers"> {
  body?: unknown;
  headers?: Record<string, string>;
  redirectOn401?: boolean;
}

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, data: unknown) {
    super(`API request failed with status ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

function buildUrl(path: string): string {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  const normalizedBase = BASE_URL.endsWith("/") ? BASE_URL.slice(0, -1) : BASE_URL;
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

function isFormData(body: unknown): body is FormData {
  return typeof FormData !== "undefined" && body instanceof FormData;
}

async function handleResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");

  let data: unknown = null;
  try {
    data = isJson ? await response.json() : await response.text();
  } catch {
    // Keep the empty fallback when a response body cannot be parsed.
  }

  if (!response.ok) {
    if (response.status === 401) {
      clearTokens();
      if (typeof window !== "undefined") {
        const currentPath = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/login?redirect=${currentPath}`;
      }
    }
    throw new ApiError(response.status, data);
  }

  return data as T;
}

export async function apiFetch<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const {
    body,
    headers: customHeaders = {},
    redirectOn401 = true,
    ...rest
  } = options;

  const headers: Record<string, string> = { ...customHeaders };

  if (body !== undefined && !isFormData(body) && !(body instanceof Blob)) {
    if (!("Content-Type" in headers) && !("content-type" in headers)) {
      headers["Content-Type"] = "application/json";
    }
  }

  const token = getAccessToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const init: RequestInit = {
    ...rest,
    headers,
  };

  if (body !== undefined) {
    if (isFormData(body) || body instanceof Blob) {
      init.body = body as BodyInit;
    } else {
      init.body = JSON.stringify(body);
    }
  }

  const response = await fetch(buildUrl(path), init);

  if (response.status === 401 && !redirectOn401) {
    clearTokens();
    const contentType = response.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");
    let data: unknown = null;
    try {
      data = isJson ? await response.json() : await response.text();
    } catch {
      // Keep the empty fallback when a response body cannot be parsed.
    }
    throw new ApiError(401, data);
  }

  return handleResponse<T>(response);
}

export const api = {
  get: <T>(path: string, options?: RequestOptions) =>
    apiFetch<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    apiFetch<T>(path, { ...options, method: "POST", body }),
  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    apiFetch<T>(path, { ...options, method: "PUT", body }),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    apiFetch<T>(path, { ...options, method: "PATCH", body }),
  delete: <T>(path: string, options?: RequestOptions) =>
    apiFetch<T>(path, { ...options, method: "DELETE" }),
};

export default api;
