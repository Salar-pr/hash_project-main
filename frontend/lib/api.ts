import { clearAuth, getAccess, getRefresh, updateAccess } from "./auth";

export const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api").replace(/\/$/, "");

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, body: unknown) {
    super(extractError(body) || `API Error ${status}`);
    this.status = status;
    this.body = body;
  }
}

function extractError(body: unknown): string {
  if (!body || typeof body !== "object") return "";
  const b = body as Record<string, unknown>;
  if (typeof b.detail === "string") return b.detail;
  if (typeof b.message === "string") return b.message;
  const first = Object.values(b)[0];
  if (Array.isArray(first) && typeof first[0] === "string") return first[0];
  if (typeof first === "string") return first;
  return "";
}

async function parseResponse(res: Response) {
  const contentType = res.headers.get("content-type") || "";
  if (res.status === 204) return null;
  if (contentType.includes("application/json")) return res.json();
  return res.text();
}

type ApiOptions = RequestInit & { auth?: boolean; retry?: boolean };

export async function apiFetch<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { auth = true, retry = true, headers, ...rest } = options;
  const url = path.startsWith("http") ? path : `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const finalHeaders = new Headers(headers);

  if (!finalHeaders.has("Content-Type") && rest.body && !(rest.body instanceof FormData)) {
    finalHeaders.set("Content-Type", "application/json");
  }

  if (auth) {
    const access = getAccess();
    if (access) finalHeaders.set("Authorization", `Bearer ${access}`);
  }

  const res = await fetch(url, { ...rest, headers: finalHeaders });
  const body = await parseResponse(res);

  if (res.status === 401 && auth && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return apiFetch<T>(path, { ...options, retry: false });
  }

  if (!res.ok) throw new ApiError(res.status, body);
  return body as T;
}

export async function refreshAccessToken() {
  const refresh = getRefresh();
  if (!refresh) return false;
  try {
    const data = await apiFetch<{ access: string }>("/auth/jwt/refresh/", {
      method: "POST",
      auth: false,
      retry: false,
      body: JSON.stringify({ refresh })
    });
    updateAccess(data.access);
    return true;
  } catch {
    clearAuth();
    return false;
  }
}

export function query(params: Record<string, string | number | null | undefined>) {
  const sp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && String(v) !== "") sp.set(k, String(v));
  });
  const qs = sp.toString();
  return qs ? `?${qs}` : "";
}
