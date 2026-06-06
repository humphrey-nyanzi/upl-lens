type EmptyStateProps = {
  actionHref?: string;
  actionLabel?: string;
  message: string;
  title?: string;
};

export function EmptyState({ actionHref, actionLabel, message, title }: EmptyStateProps) {
  if (!title && !actionHref) return <p className="empty-state">{message}</p>;

  return (
    <section className="empty-state intelligence-empty-state">
      {title ? <h2>{title}</h2> : null}
      <p>{message}</p>
      {actionHref && actionLabel ? (
        <a className="text-button dark" href={actionHref}>
          {actionLabel}
        </a>
      ) : null}
    </section>
  );
}

export type IntelligenceEmptyStateProps = EmptyStateProps;

export function IntelligenceEmptyState(props: IntelligenceEmptyStateProps) {
  return <EmptyState {...props} />;
}
