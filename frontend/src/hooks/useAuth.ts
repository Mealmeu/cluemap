import { useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { getMe, login, logout, refresh, register } from "../services/auth";
import { useAuthStore } from "../store/auth-store";

export const useBootstrapAuth = () => {
  const status = useAuthStore((state) => state.status);
  const setSession = useAuthStore((state) => state.setSession);
  const clearSession = useAuthStore((state) => state.clearSession);

  useEffect(() => {
    if (status !== "loading") {
      return;
    }

    refresh()
      .then(async (response) => {
        setSession(response.access_token, response.user);
        return getMe();
      })
      .then((user) => {
        const token = useAuthStore.getState().accessToken;
        if (token) {
          setSession(token, user);
        }
      })
      .catch(() => {
        clearSession();
      });
  }, [clearSession, setSession, status]);
};

export const useAuth = () => {
  const queryClient = useQueryClient();

  const loginMutation = useMutation({
    mutationFn: login
  });

  const registerMutation = useMutation({
    mutationFn: register
  });

  const logoutMutation = useMutation({
    mutationFn: logout,
    onSettled: async () => {
      queryClient.clear();
    }
  });

  return {
    loginMutation,
    registerMutation,
    logoutMutation
  };
};
