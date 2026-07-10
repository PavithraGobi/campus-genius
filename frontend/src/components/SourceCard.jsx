export default function SourceCard({ chunk, index, documentLabel, highlighted }) {
  const score = Math.round(chunk.similarity_score * 100);
  return (
    <article
      id={`source-${chunk.chunk_id}`}
      className={`source-card${highlighted ? " is-highlighted" : ""}`}
      style={{ "--stagger": index }}
    >
      <div className="source-card-fold" aria-hidden="true" />
      <div className="source-card-perforation" aria-hidden="true" />
      <div className="source-card-head">
        <span className="source-card-page">p. {chunk.page_number}</span>
        <span className="source-card-score">{score}% match</span>
      </div>
      <p className="source-card-text">{chunk.chunk_text}</p>
      <div className="source-card-foot">
        <span>{documentLabel || chunk.document_id}</span>
        <span>chunk #{chunk.chunk_index}</span>
      </div>
    </article>
  );
}
