const LABELS = {
  pending: "Pending",
  processing: "Processing",
  ready: "Ready",
  failed: "Failed",
};

export default function StatusBadge({ status }) {
  return <span className={`status-badge status-badge-${status}`}>{LABELS[status] || status}</span>;
}
