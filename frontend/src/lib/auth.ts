const ACCESS_TOKEN_KEY = "access";
const REFRESH_TOKEN_KEY = "refresh";

const isBrowser = typeof window !== "undefined";

function readToken(key: string): string | null {
  if (!isBrowser) {
    return null;
  }

  return window.localStorage.getItem(key);
}

function writeToken(key: string, value: string | null): void {
  if (!isBrowser) {
    return;
  }

  if (value) {
    window.localStorage.setItem(key, value);
    return;
  }

  window.localStorage.removeItem(key);
}

export function setToken(accessToken: string, refreshToken?: string | null): void {
  writeToken(ACCESS_TOKEN_KEY, accessToken);

  if (refreshToken !== undefined) {
    writeToken(REFRESH_TOKEN_KEY, refreshToken);
  }
}

export function getToken(): string | null {
  return readToken(ACCESS_TOKEN_KEY);
}

export function removeToken(): void {
  writeToken(ACCESS_TOKEN_KEY, null);
  writeToken(REFRESH_TOKEN_KEY, null);
}

export function isLoggedIn(): boolean {
  return Boolean(getToken());
}

export function getRefreshToken(): string | null {
  return readToken(REFRESH_TOKEN_KEY);
}

export function setRefreshToken(refreshToken: string | null): void {
  writeToken(REFRESH_TOKEN_KEY, refreshToken);
}

export function getAuthTokens(): {
  access: string | null;
  refresh: string | null;
} {
  return {
    access: getToken(),
    refresh: getRefreshToken(),
  };
}
