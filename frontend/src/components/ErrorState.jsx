import { ApiError } from "../api/client.js";

/**
 * Turns a raw error into a message + an actionable hint, plus a retry
 * button. Never just prints the raw string with nothing the user can do
 * about it.
 */
function hintFor(err) {
  if (err instanceof ApiError) {
    if (err.status === 503) {
      return "The answer model may not be reachable. Confirm Ollama is running and the model is pulled, then try again.";
    }
    if (err.status === 400) {
      return "The request was rejected - check the question and document selection, then try again.";
    }
    return "The backend returned an error. Try again, or check the backend terminal for details.";
  }
  return "Couldn't reach the backend API. Confirm it's running and the address in .env is correct.";
}

export default function ErrorState({ error, onRetry }) {
  return (
    <div className="error-state">
      <div className="error-state-message">{error.message}</div>
      <div className="error-state-hint">{hintFor(error)}</div>
      {onRetry && (
        <button className="ghost-button error-state-retry" onClick={onRetry} type="button">
          Try again
        </button>
      )}
    </div>
  );
}
