import { AxiosError } from "axios";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { AuthForm } from "../components/AuthForm";
import { useAuth } from "../hooks/useAuth";
import type { LoginFormValues } from "../schemas/auth";
import { useAuthStore } from "../store/auth-store";

export const LoginPage = () => {
  const navigate = useNavigate();
  const { loginMutation } = useAuth();
  const user = useAuthStore((state) => state.user);
  const status = useAuthStore((state) => state.status);

  if (status === "authenticated" && user) {
    return <Navigate replace to={user.role === "teacher" ? "/teacher/dashboard" : "/problems"} />;
  }

  const errorMessage =
    (loginMutation.error as AxiosError<{ detail?: string }> | null)?.response?.data?.detail ?? undefined;

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="grid w-full max-w-5xl gap-10 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="hidden rounded-[32px] bg-slate-950 p-10 text-white lg:block">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-blue-300">ClueMap</p>
          <h1 className="mt-6 text-4xl font-bold leading-tight">오답을 단서로 바꾸는 Python 학습 복구 시스템</h1>
          <p className="mt-6 text-base leading-8 text-slate-300">
            학생은 단계별 힌트와 복습 포인트를 받고, 교사는 문제별 오답 유형과 반복 실패 흐름을 한눈에 볼 수 있습니다.
          </p>
        </section>

        <div className="mx-auto w-full max-w-md">
          <AuthForm
            errorMessage={errorMessage}
            isPending={loginMutation.isPending}
            mode="login"
            onSubmit={(values) =>
              loginMutation.mutate(values as LoginFormValues, {
                onSuccess: (response) => {
                  navigate(response.user.role === "teacher" ? "/teacher/dashboard" : "/problems");
                }
              })
            }
          />
          <p className="mt-4 text-center text-sm text-slate-600">
            계정이 없다면{" "}
            <Link className="font-semibold text-blue-700" to="/register">
              회원가입
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
};
