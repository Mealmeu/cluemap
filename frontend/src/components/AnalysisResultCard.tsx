import type { AnalysisResult } from "../types/api";
import { HintCard } from "./HintCard";
import { ReviewTopicsCard } from "./ReviewTopicsCard";

interface AnalysisResultCardProps {
  analysis: AnalysisResult;
}

export const AnalysisResultCard = ({ analysis }: AnalysisResultCardProps) => {
  return (
    <section className="card space-y-5 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-blue-700">AI 오답 분석</p>
          <h2 className="mt-1 text-xl font-semibold text-slate-900">{analysis.category}</h2>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
          신뢰도 {Math.round(analysis.confidence * 100)}%
        </span>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <article className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <h3 className="text-sm font-semibold text-slate-800">현재 이해 상태</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">{analysis.student_state}</p>
        </article>
        <article className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <h3 className="text-sm font-semibold text-slate-800">왜 틀렸는지</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">{analysis.why_wrong}</p>
        </article>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <HintCard content={analysis.hint_level_1} title="힌트 1단계" />
        <HintCard content={analysis.hint_level_2} title="힌트 2단계" />
      </div>

      <ReviewTopicsCard topics={analysis.review_topics} />
    </section>
  );
};
