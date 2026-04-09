import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { AnalysisResultCard } from "../components/AnalysisResultCard";
import { SubmissionResultCard } from "../components/SubmissionResultCard";
import { getSubmission, getSubmissionAnalysis } from "../services/submissions";

export const SubmissionResultPage = () => {
  const params = useParams();
  const submissionId = Number(params.submissionId);

  const submissionQuery = useQuery({
    queryKey: ["submission", submissionId],
    queryFn: () => getSubmission(submissionId),
    enabled: Number.isFinite(submissionId)
  });

  const analysisQuery = useQuery({
    queryKey: ["submission", submissionId, "analysis"],
    queryFn: () => getSubmissionAnalysis(submissionId),
    enabled: Number.isFinite(submissionId)
  });

  const submission = submissionQuery.data;
  const analysis = analysisQuery.data ?? submission?.analysis_result ?? null;

  if (submissionQuery.isLoading) {
    return <main className="mx-auto max-w-6xl px-4 py-10">제출 결과를 불러오는 중입니다...</main>;
  }

  if (submissionQuery.isError || !submission) {
    return (
      <main className="mx-auto max-w-6xl px-4 py-10">
        <div className="card p-6 text-sm text-red-700">제출 결과를 불러오지 못했습니다.</div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link className="text-sm font-semibold text-blue-700" to={`/problems/${submission.problem_id}`}>
          ← 문제로 돌아가기
        </Link>
        <span className="text-sm text-slate-500">제출 #{submission.id}</span>
      </div>

      <SubmissionResultCard submission={submission} />

      {analysis ? (
        <AnalysisResultCard analysis={analysis} />
      ) : (
        <div className="card p-6 text-sm text-slate-500">분석 결과를 아직 불러오지 못했습니다.</div>
      )}

      <div className="card p-6">
        <h2 className="text-lg font-semibold text-slate-900">재제출 안내</h2>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          위 힌트를 참고해 코드를 수정한 뒤 다시 제출할 수 있습니다. 제출 버튼은 분석이 끝나기 전까지 비활성화됩니다.
        </p>
      </div>
    </main>
  );
};
