import axios, {
  AxiosError,
  AxiosHeaders,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";
import {
  getAuthTokens,
  getRefreshToken,
  getToken,
  removeToken,
  setRefreshToken,
  setToken,
} from "@/lib/auth";

const API_BASE_URL = "/api";

type RetryableRequestConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

let refreshRequest: Promise<string | null> | null = null;

export const getAccessToken = getToken;
export const getStoredTokens = getAuthTokens;
export const clearTokens = removeToken;

export function setTokens(tokens: {
  access?: string | null;
  refresh?: string | null;
}): void {
  if (tokens.access !== undefined) {
    if (!tokens.access) {
      removeToken();
      return;
    }

    if (tokens.refresh === undefined) {
      const currentRefresh = getRefreshToken();
      setToken(tokens.access, currentRefresh);
      return;
    }

    setToken(tokens.access, tokens.refresh);
    return;
  }

  if (tokens.refresh !== undefined) {
    setRefreshToken(tokens.refresh);
  }
}

function shouldSkipAuth(config?: InternalAxiosRequestConfig): boolean {
  const url = config?.url ?? "";
  return (
    url.includes("/token/") ||
    url.includes("/token/refresh/") ||
    url.includes("/logout/")
  );
}

function setAuthorizationHeader(
  config: InternalAxiosRequestConfig,
  token: string,
): InternalAxiosRequestConfig {
  const headers =
    config.headers instanceof AxiosHeaders
      ? config.headers
      : new AxiosHeaders(config.headers);

  headers.set("Authorization", `Bearer ${token}`);
  config.headers = headers;

  return config;
}

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();

  if (!refresh) {
    removeToken();
    return null;
  }

  if (!refreshRequest) {
    refreshRequest = axios
      .post<{ access: string }>(`${API_BASE_URL}/token/refresh/`, { refresh })
      .then((response) => {
        const nextAccessToken = response.data.access;
        setTokens({ access: nextAccessToken });
        return nextAccessToken;
      })
      .catch(() => {
        removeToken();
        return null;
      })
      .finally(() => {
        refreshRequest = null;
      });
  }

  return refreshRequest;
}

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const accessToken = getToken();

  if (!accessToken || shouldSkipAuth(config)) {
    return config;
  }

  return setAuthorizationHeader(config, accessToken);
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const responseStatus = error.response?.status;
    const originalRequest = error.config as RetryableRequestConfig | undefined;

    if (
      responseStatus !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      shouldSkipAuth(originalRequest)
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    const nextAccessToken = await refreshAccessToken();

    if (!nextAccessToken) {
      return Promise.reject(error);
    }

    return api.request(setAuthorizationHeader(originalRequest, nextAccessToken));
  },
);

export default api;
