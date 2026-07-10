import { useState } from "react";
import { Sun, Moon, Monitor, Check } from "lucide-react";
import {
  getStoredTheme,
  setStoredTheme,
  applyTheme,
  getStoredDefaultTopK,
  setStoredDefaultTopK,
} from "../lib/preferences.js";

const THEME_OPTIONS = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
];

export default function SettingsPanel() {
  const [theme, setTheme] = useState(getStoredTheme);
  const [topK, setTopK] = useState(getStoredDefaultTopK);
  const [saved, setSaved] = useState(false);

  function chooseTheme(value) {
    setTheme(value);
    setStoredTheme(value);
    applyTheme(value);
  }

  function saveTopK() {
    const clamped = Math.min(50, Math.max(1, Number(topK) || 5));
    setTopK(clamped);
    setStoredDefaultTopK(clamped);
    setSaved(true);
    setTimeout(() => setSaved(false), 1800);
  }

  return (
    <section className="panel">
      <header className="panel-header">
        <h1>Settings</h1>
        <p>Only controls that actually do something live here - nothing decorative.</p>
      </header>

      <div className="settings-stack">
        <div className="settings-card">
          <h2 className="settings-card-title">Appearance</h2>
          <p className="settings-card-desc">Choose how Campus Genius looks on this device.</p>
          <div className="theme-options">
            {THEME_OPTIONS.map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                type="button"
                className={`theme-option ${theme === value ? "is-active" : ""}`}
                onClick={() => chooseTheme(value)}
                aria-pressed={theme === value}
              >
                <Icon size={18} strokeWidth={2} />
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="settings-card">
          <h2 className="settings-card-title">Retrieval defaults</h2>
          <p className="settings-card-desc">
            Sets the starting Top K value on the Ask and Search forms. You can still change it
            per question - this just saves you resetting it every time.
          </p>
          <div className="settings-field">
            <div className="settings-field-row">
              <label htmlFor="settings-top-k">Default passages retrieved (Top K)</label>
              <span className="settings-field-value">k = {topK}</span>
            </div>
            <input
              id="settings-top-k"
              className="settings-range"
              type="range"
              min={1}
              max={20}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
            />
            <p className="settings-hint">More passages give broader context but slower answers.</p>
            <div className="settings-save-row">
              <button type="button" className="primary-button" onClick={saveTopK}>
                Save default
              </button>
              {saved && (
                <span className="settings-saved-note">
                  <Check size={13} strokeWidth={2.5} style={{ verticalAlign: "-2px" }} /> Saved
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="settings-not-supported">
          Model selection, answer temperature, hybrid search, answer language, and account
          controls aren't wired to a real backend yet, so they're left out rather than shown as
          non-functional UI.
        </div>
      </div>
    </section>
  );
}
