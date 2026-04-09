import { create } from "zustand";

import type { User } from "../types/api";

type AuthStatus = "loading" | "authenticated" | "guest";

interface AuthState {
  accessToken: string | null;
  user: User | null;
  status: AuthStatus;
  setSession: (accessToken: string, user: User) => void;
  clearSession: () => void;
  setStatus: (status: AuthStatus) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  status: "loading",
  setSession: (accessToken, user) =>
    set({
      accessToken,
      user,
      status: "authenticated"
    }),
  clearSession: () =>
    set({
      accessToken: null,
      user: null,
      status: "guest"
    }),
  setStatus: (status) => set({ status })
}));
