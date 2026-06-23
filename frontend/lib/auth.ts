import type { AuthBundle, User } from "./types";

const ACCESS_KEY = "hr_access";
const REFRESH_KEY = "hr_refresh";
const TOKEN_KEY = "hr_token";
const USER_KEY = "hr_user";

export function saveAuth(bundle: AuthBundle) {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_KEY, bundle.access);
  localStorage.setItem(REFRESH_KEY, bundle.refresh);
  localStorage.setItem(TOKEN_KEY, bundle.token);
  localStorage.setItem(USER_KEY, JSON.stringify(bundle.user));
}

export function updateAccess(access: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_KEY, access);
}

export function updateUser(user: User) {
  if (typeof window === "undefined") return;
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearAuth() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function getAccess() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefresh() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function isAuthed() {
  return Boolean(getAccess() || getToken());
}
