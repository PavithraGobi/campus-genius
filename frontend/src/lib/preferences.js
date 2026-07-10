/**
 * Client-side-only preferences. Nothing here talks to the backend -
 * there's no settings/auth endpoint to persist to, so these are the two
 * controls that are honestly real without one:
 *
 * - theme: purely a frontend concern (which CSS tokens apply).
 * - defaultTopK: pre-fills the `top_k` field already sent to
 *   /answer/ask and /retrieval/search - it doesn't invent a new
 *   backend parameter, just remembers the user's preferred starting
 *   value instead of always resetting to 5.
 */

const THEME_KEY = "campus-genius:theme";
const TOP_K_KEY = "campus-genius:default-top-k";

export function getStoredTheme() {
  try {
    return localStorage.getItem(THEME_KEY) || "system";
  } catch {
    return "system";
  }
}

export function setStoredTheme(theme) {
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch {
    /* localStorage unavailable - theme just won't persist */
  }
}

function resolveTheme(theme) {
  if (theme === "system") {
    return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return theme;
}

export function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", resolveTheme(theme));
}

export function getStoredDefaultTopK() {
  try {
    const n = Number(localStorage.getItem(TOP_K_KEY));
    return Number.isFinite(n) && n >= 1 && n <= 50 ? n : 5;
  } catch {
    return 5;
  }
}

export function setStoredDefaultTopK(value) {
  try {
    localStorage.setItem(TOP_K_KEY, String(value));
  } catch {
    /* localStorage unavailable - default just won't persist */
  }
}
