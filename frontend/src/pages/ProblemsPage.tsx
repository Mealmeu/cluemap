import { Link } from "react-router-dom";

import { ProblemList } from "../components/ProblemList";
import { useProblemsQuery } from "../hooks/useProblems";
import { useAuthStore } from "../store/auth-store";

export const ProblemsPage = () => {
  const { data, isLoading, isError, error } = useProblemsQuery();
  const user = useAuthStore((state) => state.user);

  return (
    <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
      <section className="mb-8 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-blue-700">문제 목록</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">학습 복구를 위한 Python 입문 문제</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            문제를 선택하면 starter code, 이전 제출 흐름, AI 오답 분석까지 이어서 확인할 수 있습니다.
          </p>
        </div>
        {user?.role === "teacher" ? (
          <div className="flex gap-3">
            <Link className="button-secondary" to="/teacher/problems">
              문제 관리
            </Link>
            <Link className="button-primary" to="/teacher/dashboard">
              교사 대시보드
            </Link>
          </div>
        ) : null}
      </section>

      {isLoading ? <div className="card p-6 text-sm text-slate-500">문제 목록을 불러오는 중입니다...</div> : null}
      {isError ? (
        <div className="card p-6 text-sm text-red-700">
          문제 목록을 불러오지 못했습니다. {(error as Error).message}
        </div>
      ) : null}
      {!isLoading && !isError && data?.length === 0 ? (
        <div className="card p-6 text-sm text-slate-500">등록된 문제가 없습니다.</div>
      ) : null}
      {data?.length ? <ProblemList problems={data} /> : null}
    </main>
  );
};
