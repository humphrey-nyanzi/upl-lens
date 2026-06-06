import { EmptyState, type IntelligenceEmptyStateProps } from "../common/EmptyState";

export type { IntelligenceEmptyStateProps };

export function InsightEmptyState(props: IntelligenceEmptyStateProps) {
  return <EmptyState {...props} />;
}
