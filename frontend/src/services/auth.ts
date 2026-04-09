import { apiClient, applyAuthResponse, clearAuthSession, refreshAuthSession } from "./api/client";
import type { AuthResponse, MessageResponse, User } from "../types/api";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload extends LoginPayload {
  role: "student" | "teacher";
}

export const register = async (payload: RegisterPayload) => {
  const { data } = await apiClient.post<AuthResponse>("/api/auth/register", payload);
  return applyAuthResponse(data);
};

export const login = async (payload: LoginPayload) => {
  const { data } = await apiClient.post<AuthResponse>("/api/auth/login", payload);
  return applyAuthResponse(data);
};

export const logout = async () => {
  const { data } = await apiClient.post<MessageResponse>("/api/auth/logout");
  clearAuthSession();
  return data;
};

export const refresh = async () => refreshAuthSession();

export const getMe = async () => {
  const { data } = await apiClient.get<User>("/api/auth/me");
  return data;
};
