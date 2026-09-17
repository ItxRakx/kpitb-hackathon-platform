export interface ParticipantProfile {
  id: number;
  phone: string | null;
  institution: string | null;
  district: string | null;
  education_level: string | null;
  skills: string[];
  bio: string;
  portfolio_url: string | null;
  github_url: string | null;
  is_judge: boolean;
  is_verified: boolean;
  is_complete: boolean;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  profile: ParticipantProfile | null;
}

export interface TokenPair {
  access: string;
  refresh: string;
}

const ACCESS_TOKEN_KEY = "auth_access_token";
const REFRESH_TOKEN_KEY = "auth_refresh_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setTokens(tokens: TokenPair): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
  } catch {
    return;
  }
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  } catch {
    return;
  }
}

export function isAuthenticated(): boolean {
  return !!getAccessToken();
}
