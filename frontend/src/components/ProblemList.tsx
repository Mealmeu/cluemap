import { Link } from "react-router-dom";

import type { ProblemListItem } from "../types/api";

interface ProblemListProps {
  problems: ProblemListItem[];
}

export const ProblemList = ({ problems }: ProblemListProps) => {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {problems.map((problem) => (
        <article className="card flex h-full flex-col p-6" key={problem.id}>
          <div className="mb-4 flex items-start justify-between gap-3">
            <h2 className="text-lg font-semibold text-slate-900">{problem.title}</h2>
            <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">문제 {problem.id}</span>
          </div>
          <p className="flex-1 text-sm leading-6 text-slate-600">{problem.description}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {problem.concept_tags.map((tag) => (
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700" key={tag}>
                {tag}
              </span>
            ))}
          </div>
          <Link className="button-secondary mt-6 w-full" to={`/problems/${problem.id}`}>
            문제 풀기
          </Link>
        </article>
      ))}
    </div>
  );
};
