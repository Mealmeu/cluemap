import { useEffect, useState } from "react";

import { MisconceptionChart } from "../components/MisconceptionChart";
import { StudentHistoryTable } from "../components/StudentHistoryTable";
import { TeacherStatsPanel } from "../components/TeacherStatsPanel";
import { useProblemsQuery } from "../hooks/useProblems";
import { useStudentHistoryQuery, useTeacherProblemInsightsQuery, useTeacherProblemStatsQuery } from "../hooks/useTeacher";

export const TeacherDashboardPage = () => {
  const { data: problems, isLoading: problemsLoading } = useProblemsQuery();
  const [selectedProblemId, setSelectedProblemId] = useState<number | null>(null);
  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);

  useEffect(() => {
    if (!selectedProblemId && problems?.length) {
      setSelectedProblemId(problems[0].id);
    }
  }, [problems, selectedProblemId]);

  const statsQuery = useTeacherProblemStatsQuery(selectedProblemId);
  const insightsQuery = useTeacherProblemInsightsQuery(selectedProblemId);
  const historyQuery = useStudentHistoryQuery(selectedStudentId);

  return (
    <main className="mx-auto max-w-7xl space-y-6 px-4 py-10">
      <section className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-blue-700">Teacher Dashboard</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">문제별 오답 유형과 수업 개선 포인트</h1>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            반복 실패 학생, 오답 유형 분포, AI 교사 요약을 한 화면에서 확인할 수 있습니다.
          </p>
        </div>
        <div className="card min-w-72 p-4">
          <label className="label-text" htmlFor="problem-select">
            문제 선택
          </label>
          <select
            className="input-base"
            id="problem-select"
            onChange={(event) => {
              setSelectedProblemId(Number(event.target.value));
              setSelectedStudentId(null);
            }}
            value={selectedProblemId ?? ""}
          >
            {problems?.map((problem) => (
              <option key={problem.id} value={problem.id}>
                {problem.title}
              </option>
            ))}
          </select>
        </div>
      </section>

      {problemsLoading ? <div className="card p-6 text-sm text-slate-500">문제 목록을 불러오는 중입니다...</div> : null}
      {!problemsLoading && !problems?.length ? <div className="card p-6 text-sm text-slate-500">문제가 없습니다.</div> : null}

      {statsQuery.data && insightsQuery.data ? (
        <>
          <TeacherStatsPanel insights={insightsQuery.data} onSelectStudent={setSelectedStudentId} stats={statsQuery.data} />
          <section className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-slate-900">오답 유형 분포</h2>
              <p className="mt-2 text-sm text-slate-600">문제별 misconception category 분포를 원형 차트로 확인합니다.</p>
              <div className="mt-4">
                <MisconceptionChart data={statsQuery.data.misconception_distribution} />
              </div>
            </div>

            <div className="card p-6">
              <h2 className="text-lg font-semibold text-slate-900">학생 제출 이력</h2>
              <p className="mt-2 text-sm text-slate-600">
                반복 실패 학생을 클릭하면 해당 학생의 누적 제출 이력을 확인할 수 있습니다.
              </p>
              <div className="mt-4">
                {selectedStudentId && historyQuery.data ? (
                  <StudentHistoryTable items={historyQuery.data.items} />
                ) : (
                  <div className="rounded-2xl bg-slate-50 p-6 text-sm text-slate-500">반복 실패 학생을 선택해 주세요.</div>
                )}
              </div>
            </div>
          </section>
        </>
      ) : null}

      {statsQuery.isError || insightsQuery.isError ? (
        <div className="card p-6 text-sm text-red-700">교사용 통계를 불러오지 못했습니다.</div>
      ) : null}
    </main>
  );
};
