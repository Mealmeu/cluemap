import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import type { CategoryCount } from "../types/api";

interface MisconceptionChartProps {
  data: CategoryCount[];
}

const colors = ["#1d4ed8", "#0f766e", "#f59e0b", "#dc2626", "#7c3aed", "#475569"];

export const MisconceptionChart = ({ data }: MisconceptionChartProps) => {
  if (!data.length) {
    return <div className="rounded-2xl bg-slate-50 p-6 text-sm text-slate-500">집계된 오답 유형이 아직 없습니다.</div>;
  }

  return (
    <div className="h-72">
      <ResponsiveContainer height="100%" width="100%">
        <PieChart>
          <Pie cx="50%" cy="50%" data={data} dataKey="count" innerRadius={60} outerRadius={100} nameKey="category">
            {data.map((entry, index) => (
              <Cell fill={colors[index % colors.length]} key={entry.category} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
