import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";

import { CodeEditorPanel } from "../components/CodeEditorPanel";
import { ProblemDetailCard } from "../components/ProblemDetailCard";
import { useProblemQuery } from "../hooks/useProblems";
import { createSubmission, getMyProblemSubmissions } from "../services/submissions";

export const ProblemDetailPage = () => {
  const navigate = useNavigate();
  const params = useParams();
  const problemId = Number(params.problemId);
  const [code, setCode] = useState("");
  const { data: problem, isLoading, isError, error } = useProblemQuery(problemId, Number.isFinite(problemId));
  const submissionsQuery = useQuery({
    queryKey: ["submissions", "me", problemId],
    queryFn: () => getMyProblemSubmissions(problemId),
    enabled: Number.isFinite(problemId)
  });
  const latestSubmission = submissionsQuery.data?.[0] ?? null;

  useEffect(() => {
    if (!problem) {
      return;
    }
    setCode(latestSubmission?.code ?? problem.starter_code);
  }, [latestSubmission?.code, problem]);

  const submissionMutation = useMutation({
    mutationFn: createSubmission,
    onSuccess: (submission) => {
      navigate(`/submissions/${submission.id}`);
    }
  });

  if (isLoading) {
    return <main className="mx-auto max-w-7xl px-4 py-10">문제를 불러오는 중입니다...</main>;
  }

  if (isError || !problem) {
    return (
      <main className="mx-auto max-w-7xl px-4 py-10">
        <div className="card p-6 text-sm text-red-700">문제를 불러오지 못했습니다. {(error as Error)?.message}</div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-7xl space-y-6 px-4 py-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link className="text-sm font-semibold text-blue-700" to="/problems">
          ← 문제 목록으로
        </Link>
        {latestSubmission ? (
          <div className="rounded-full bg-blue-50 px-4 py-2 text-sm text-blue-700">
            최근 제출 {Math.round(latestSubmission.score * 100)}점
          </div>
        ) : null}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_1.1fr]">
        <ProblemDetailCard latestSubmission={latestSubmission} problem={problem} />
        <CodeEditorPanel
          code={code}
          isSubmitting={submissionMutation.isPending}
          onChange={setCode}
          onSubmit={() => submissionMutation.mutate({ problem_id: problem.id, code })}
        />
      </div>

      {submissionMutation.isError ? (
        <div className="card p-6 text-sm text-red-700">제출에 실패했습니다. 다시 시도해 주세요.</div>
      ) : null}

      <section className="card p-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">이전 제출 흐름</h2>
          <span className="text-sm text-slate-500">{submissionsQuery.data?.length ?? 0}건</span>
        </div>
        {submissionsQuery.isLoading ? <p className="mt-4 text-sm text-slate-500">이전 제출을 불러오는 중입니다...</p> : null}
        {submissionsQuery.data?.length ? (
          <div className="mt-4 space-y-3">
            {submissionsQuery.data.slice(0, 5).map((submission) => (
              <Link
                className="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3 transition hover:border-blue-300 hover:bg-blue-50"
                key={submission.id}
                to={`/submissions/${submission.id}`}
              >
                <div>
                  <p className="font-medium text-slate-900">
                    제출 #{submission.id} · {submission.analysis_result?.category ?? submission.run_status}
                  </p>
                  <p className="text-sm text-slate-500">{new Date(submission.created_at).toLocaleString()}</p>
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
                  {Math.round(submission.score * 100)}점
                </span>
              </Link>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-slate-500">아직 제출 이력이 없습니다.</p>
        )}
      </section>
    </main>
  );
};
