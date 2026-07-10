/**
 * Calm, static loading placeholder shown while a request is in flight.
 * Deliberately not a spinner - it mirrors the shape of the result area
 * (answer block + a row of source cards) so the layout doesn't jump when
 * the real content arrives.
 */
export default function AnswerSkeleton() {
  return (
    <div className="answer-block" aria-live="polite" aria-busy="true">
      <div className="result-section">
        <span className="section-label">Answer</span>
        <div className="skeleton-block skeleton-text" />
      </div>
      <div className="result-section">
        <span className="section-label">Sources</span>
        <div className="source-grid">
          <div className="skeleton-block skeleton-card" />
          <div className="skeleton-block skeleton-card" />
          <div className="skeleton-block skeleton-card" />
        </div>
      </div>
    </div>
  );
}
