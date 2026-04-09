import type { Submission } from "../types/api";

interface SubmissionResultCardProps {
  submission: Submission;
}

const statusLabel: Record<string, string> = {
  passed: "통과",
  failed: "실패",
  timeout: "시간 초과",
  runtime_error: "런타임 오류",
  syntax_error: "문법 오류",
  blocked: "실행 차단",
  running: "실행 중"
};

export const SubmissionResultCard = ({ submission }: SubmissionResultCardProps) => {
  return (
    <section className="card space-y-5 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-blue-700">제출 결과</p>
          <h2 className="mt-1 text-xl font-semibold text-slate-900">{statusLabel[submission.run_status] ?? submission.run_status}</h2>
        </div>
        <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
          {submission.passed_count}/{submission.total_count} 테스트 통과
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-2xl bg-slate-50 p-4">
          <p className="text-sm text-slate-500">점수</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">{Math.round(submission.score * 100)}</p>
        </div>
        <div className="rounded-2xl bg-slate-50 p-4">
          <p className="text-sm text-slate-500">실행 시간</p>
          <p className="mt-2 text-2xl font-bold text-slate-900">{submission.execution_time_ms ?? "-"}ms</p>
        </div>
        <div className="rounded-2xl bg-slate-50 p-4">
          <p className="text-sm text-slate-500">개선 여부</p>
          <p className="mt-2 text-lg font-semibold text-slate-900">
            {submission.improved === null ? "첫 제출" : submission.improved ? "이전보다 개선됨" : "추가 복구 필요"}
          </p>
        </div>
      </div>

      {submission.failure_summary.length ? (
        <div>
          <h3 className="text-sm font-semibold text-slate-800">실패 요약</h3>
          <div className="mt-3 space-y-3">
            {submission.failure_summary.map((item, index) => (
              <div className="rounded-2xl border border-red-100 bg-red-50 p-4 text-sm text-red-800" key={index}>
                <pre className="overflow-x-auto whitespace-pre-wrap">{JSON.stringify(item, null, 2)}</pre>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {submission.stderr_excerpt ? (
        <div className="rounded-2xl border border-red-100 bg-red-50 p-4 text-sm text-red-800">
          <h3 className="font-semibold">오류 메시지</h3>
          <pre className="mt-2 overflow-x-auto whitespace-pre-wrap">{submission.stderr_excerpt}</pre>
        </div>
      ) : null}
    </section>
  );
};
