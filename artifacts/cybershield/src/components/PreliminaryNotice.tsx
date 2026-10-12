type PreliminaryNoticeProps = {
  className?: string;
};

export function PreliminaryNotice({ className = '' }: PreliminaryNoticeProps) {
  return (
    <aside
      role="note"
      aria-label="Assessment limitation"
      className={`rounded-lg border border-amber-300/20 bg-amber-300/[.05] p-3 text-xs leading-5 text-amber-100/90 ${className}`}
    >
      Automated preliminary assessment—not a guarantee, confirmed threat, or
      professional security audit. A low-risk result is not proof of safety.
    </aside>
  );
}
