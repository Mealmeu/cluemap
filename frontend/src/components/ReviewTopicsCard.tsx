interface ReviewTopicsCardProps {
  topics: string[];
}

export const ReviewTopicsCard = ({ topics }: ReviewTopicsCardProps) => {
  return (
    <article className="rounded-2xl border border-emerald-100 bg-emerald-50 p-4">
      <h3 className="text-sm font-semibold text-emerald-900">복습 개념</h3>
      <div className="mt-3 flex flex-wrap gap-2">
        {topics.length ? (
          topics.map((topic) => (
            <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-emerald-800" key={topic}>
              {topic}
            </span>
          ))
        ) : (
          <span className="text-sm text-emerald-800">추천 복습 개념이 아직 없습니다.</span>
        )}
      </div>
    </article>
  );
};
