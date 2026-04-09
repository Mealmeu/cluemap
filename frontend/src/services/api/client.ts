import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";

import { useAuthStore } from "../../store/auth-store";
import type { AuthResponse } from "../../types/api";

declare module "axios" {
  interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "";

export const apiClient = axios.create({
  baseURL,
  withCredentials: true
});

const refreshClient = axios.create({
  baseURL,
  withCredentials: true
});

let initialized = false;
let refreshPromise: Promise<AuthResponse> | null = null;

const getCsrfToken = () => {
  if (typeof document === "undefined") {
    return null;
  }
  const cookie = document.cookie
    .split("; ")
    .find((item) => item.startsWith("cluemap_csrf_token="));
  return cookie ? decodeURIComponent(cookie.split("=")[1] ?? "") : null;
};

const attachSecurityHeaders = (config: InternalAxiosRequestConfig) => {
  const accessToken = useAuthStore.getState().accessToken;
  if (accessToken) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  const method = (config.method ?? "get").toLowerCase();
  if (["post", "put", "patch", "delete"].includes(method)) {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers = config.headers ?? {};
      config.headers["X-CSRF-Token"] = csrfToken;
    }
  }
  return config;
};

export const applyAuthResponse = (response: AuthResponse) => {
  useAuthStore.getState().setSession(response.access_token, response.user);
  return response;
};

export const clearAuthSession = () => {
  useAuthStore.getState().clearSession();
};

export const refreshAuthSession = async () => {
  const { data } = await refreshClient.post<AuthResponse>("/api/auth/refresh");
  return applyAuthResponse(data);
};

const shouldSkipRefresh = (config?: InternalAxiosRequestConfig) => {
  const url = config?.url ?? "";
  return ["/api/auth/login", "/api/auth/register", "/api/auth/refresh", "/api/auth/logout"].some((item) =>
    url.includes(item)
  );
};

export const setupApiInterceptors = () => {
  if (initialized) {
    return;
  }

  apiClient.interceptors.request.use(attachSecurityHeaders);
  refreshClient.interceptors.request.use(attachSecurityHeaders);

  apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config;
      if (!originalRequest || originalRequest._retry || shouldSkipRefresh(originalRequest)) {
        return Promise.reject(error);
      }

      if (error.response?.status !== 401) {
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      try {
        refreshPromise = refreshPromise ?? refreshAuthSession().finally(() => {
          refreshPromise = null;
        });
        const refreshed = await refreshPromise;
        originalRequest.headers = originalRequest.headers ?? {};
        originalRequest.headers.Authorization = `Bearer ${refreshed.access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        clearAuthSession();
        return Promise.reject(refreshError);
      }
    }
  );

  initialized = true;
};
