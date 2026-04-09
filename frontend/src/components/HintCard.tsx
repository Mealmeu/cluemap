interface HintCardProps {
  title: string;
  content: string;
}

export const HintCard = ({ title, content }: HintCardProps) => {
  return (
    <article className="rounded-2xl border border-blue-100 bg-blue-50 p-4">
      <h3 className="text-sm font-semibold text-blue-900">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-blue-900/80">{content}</p>
    </article>
  );
};
