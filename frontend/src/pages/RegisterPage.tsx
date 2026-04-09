import { AxiosError } from "axios";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { AuthForm } from "../components/AuthForm";
import { useAuth } from "../hooks/useAuth";
import type { RegisterFormValues } from "../schemas/auth";
import { useAuthStore } from "../store/auth-store";

export const RegisterPage = () => {
  const navigate = useNavigate();
  const { registerMutation } = useAuth();
  const user = useAuthStore((state) => state.user);
  const status = useAuthStore((state) => state.status);

  if (status === "authenticated" && user) {
    return <Navigate replace to={user.role === "teacher" ? "/teacher/dashboard" : "/problems"} />;
  }

  const errorMessage =
    (registerMutation.error as AxiosError<{ detail?: string }> | null)?.response?.data?.detail ?? undefined;

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="mx-auto w-full max-w-md">
        <AuthForm
          errorMessage={errorMessage}
          isPending={registerMutation.isPending}
          mode="register"
          onSubmit={(values) =>
            registerMutation.mutate(values as RegisterFormValues, {
              onSuccess: (response) => {
                navigate(response.user.role === "teacher" ? "/teacher/dashboard" : "/problems");
              }
            })
          }
        />
        <p className="mt-4 text-center text-sm text-slate-600">
          이미 계정이 있다면{" "}
          <Link className="font-semibold text-blue-700" to="/login">
            로그인
          </Link>
        </p>
      </div>
    </main>
  );
};
