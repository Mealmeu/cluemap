import type { StudentHistoryItem } from "../types/api";

interface StudentHistoryTableProps {
  items: StudentHistoryItem[];
}

export const StudentHistoryTable = ({ items }: StudentHistoryTableProps) => {
  if (!items.length) {
    return <div className="rounded-2xl bg-slate-50 p-6 text-sm text-slate-500">표시할 학생 제출 이력이 없습니다.</div>;
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">문제</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">상태</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">점수</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">분류</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">제출 시각</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {items.map((item) => (
            <tr key={item.submission_id}>
              <td className="px-4 py-3 text-sm text-slate-800">{item.problem_title}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{item.run_status}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{Math.round(item.score * 100)}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{item.category ?? "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-500">{new Date(item.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
