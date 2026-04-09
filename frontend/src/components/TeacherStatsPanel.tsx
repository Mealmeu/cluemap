import type { TeacherProblemInsights, TeacherProblemStats } from "../types/api";

interface TeacherStatsPanelProps {
  stats: TeacherProblemStats;
  insights: TeacherProblemInsights;
  onSelectStudent?: (studentId: number) => void;
}

export const TeacherStatsPanel = ({ stats, insights, onSelectStudent }: TeacherStatsPanelProps) => {
  return (
    <section className="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
      <div className="card p-6">
        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl bg-slate-50 p-4">
            <p className="text-sm text-slate-500">총 제출</p>
            <p className="mt-2 text-2xl font-bold text-slate-900">{stats.total_submissions}</p>
          </div>
          <div className="rounded-2xl bg-emerald-50 p-4">
            <p className="text-sm text-emerald-700">통과</p>
            <p className="mt-2 text-2xl font-bold text-emerald-900">{stats.passed_submissions}</p>
          </div>
          <div className="rounded-2xl bg-red-50 p-4">
            <p className="text-sm text-red-700">실패</p>
            <p className="mt-2 text-2xl font-bold text-red-900">{stats.failed_submissions}</p>
          </div>
          <div className="rounded-2xl bg-blue-50 p-4">
            <p className="text-sm text-blue-700">평균 점수</p>
            <p className="mt-2 text-2xl font-bold text-blue-900">{Math.round(stats.average_score * 100)}</p>
          </div>
        </div>

        <div className="mt-6">
          <h3 className="text-sm font-semibold text-slate-800">반복 실패 학생</h3>
          <div className="mt-3 space-y-3">
            {stats.repeated_failures.length ? (
              stats.repeated_failures.map((student) => (
                <button
                  className="flex w-full items-center justify-between rounded-2xl border border-slate-200 px-4 py-3 text-left transition hover:border-blue-300 hover:bg-blue-50"
                  key={student.student_id}
                  onClick={() => onSelectStudent?.(student.student_id)}
                  type="button"
                >
                  <div>
                    <p className="font-medium text-slate-900">{student.email}</p>
                    <p className="text-sm text-slate-500">최근 제출 {student.latest_submission_at ?? "-"}</p>
                  </div>
                  <span className="rounded-full bg-red-100 px-3 py-1 text-sm font-medium text-red-700">
                    실패 {student.failure_count}회
                  </span>
                </button>
              ))
            ) : (
              <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">반복 실패 학생이 없습니다.</div>
            )}
          </div>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold text-slate-900">수업 보완 인사이트</h3>
        <p className="mt-3 text-sm leading-6 text-slate-600">{insights.summary}</p>

        <div className="mt-5">
          <h4 className="text-sm font-semibold text-slate-800">집중 포인트</h4>
          <ul className="mt-3 space-y-2 text-sm text-slate-600">
            {insights.focus_points.length ? (
              insights.focus_points.map((item) => <li key={item}>{item}</li>)
            ) : (
              <li>아직 요약할 포인트가 없습니다.</li>
            )}
          </ul>
        </div>

        <div className="mt-5">
          <h4 className="text-sm font-semibold text-slate-800">추천 복습 개념</h4>
          <div className="mt-3 flex flex-wrap gap-2">
            {insights.review_topics.length ? (
              insights.review_topics.map((topic) => (
                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700" key={topic}>
                  {topic}
                </span>
              ))
            ) : (
              <span className="text-sm text-slate-500">아직 없습니다.</span>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};
