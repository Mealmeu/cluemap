import type { Problem, Submission } from "../types/api";

interface ProblemDetailCardProps {
  problem: Problem;
  latestSubmission?: Submission | null;
}

export const ProblemDetailCard = ({ problem, latestSubmission }: ProblemDetailCardProps) => {
  return (
    <section className="card space-y-5 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-blue-700">Python 입문 문제</p>
          <h1 className="mt-2 text-2xl font-bold text-slate-900">{problem.title}</h1>
        </div>
        {latestSubmission ? (
          <div className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
            최근 제출 점수 {Math.round(latestSubmission.score * 100)}점
          </div>
        ) : null}
      </div>

      <div>
        <h2 className="text-sm font-semibold text-slate-800">문제 설명</h2>
        <p className="mt-2 whitespace-pre-line text-sm leading-7 text-slate-600">{problem.description}</p>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-slate-800">복구 포인트</h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {problem.misconception_taxonomy.map((item) => (
            <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700" key={item}>
              {item}
            </span>
          ))}
        </div>
      </div>

      <div className="rounded-2xl bg-slate-950 p-4 text-sm text-slate-100">
        <p className="mb-2 font-semibold text-slate-200">Starter Code</p>
        <pre className="overflow-x-auto whitespace-pre-wrap">{problem.starter_code}</pre>
      </div>
    </section>
  );
};
