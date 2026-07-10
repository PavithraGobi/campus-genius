# Campus Genius — Frontend Design System

This documents the rules the current UI follows, so future changes stay
consistent instead of drifting toward generic AI-dashboard defaults.

## Concept

A library index-card / marginalia system. The product's entire value
proposition is "trust this answer because here is exactly where it came
from" — every design decision should reinforce that, not decorate around
it.

## Tokens

All color, type, spacing, and elevation values live in
`src/styles/tokens.css`. **New components should reference these
variables, not hardcode hex codes or arbitrary rem values.** If a token
you need doesn't exist yet, add it there with a comment explaining its
purpose, rather than inlining a one-off value in a component stylesheet.

## The signature accent: citation yellow (`--highlight`)

This is the one accent color in the whole system, and it is reserved
**exclusively** for grounded-citation moments:
- Source-card similarity scores
- Cited spans (`[1]`, `[2]`, etc.) inside a generated answer
- The active sidebar tab's left accent bar (the one always-visible piece
  of "you are looking at grounded output" chrome)

It must **never** be used as:
- A general brand color, button fill, or link color
- Decoration on something unrelated to a retrieved/cited passage
- A "success" or "highlight" color for unrelated UI (use `--ok` /
  `--processing` instead)

If you're reaching for `--highlight` and what you're styling isn't tied
to a retrieved source, stop and use `--ink` or `--processing` instead.

## What to avoid

- Generic AI-dashboard tropes: cream + terracotta serif hero, neon
  gradients, glassmorphism, big-number-with-small-label hero blocks.
- Decoration for its own sake — every structural device (dividers,
  mono-caps section labels, card perforation lines) should encode
  something true about the content, not just look busy.
- Raw error strings with no recovery path. Every error state must pair a
  plain-language message with a hint about what to do next, and a retry
  action where the failure is retryable (see `ErrorState.jsx`).
- Spinners for loading. Prefer calm, static skeletons that mirror the
  shape of the incoming content (see `AnswerSkeleton.jsx`) so the layout
  doesn't jump.

## Component patterns to reuse

- **Empty state** (`.empty-panel-state`): shown before a user has
  submitted anything in a panel. Should say what will appear and how to
  trigger it — an invitation to act, not a blank void.
- **Loading state** (`AnswerSkeleton.jsx` / `.skeleton-block`): shown
  while a request is in flight. Mirrors the real result layout.
- **Error state** (`ErrorState.jsx`): message + contextual hint (derived
  from the error type/status) + retry button that replays the last
  submitted request.
- **Section label** (`.section-label`): small mono-caps label above a
  logical group (a form section, a results group). Used for hierarchy,
  not decoration.

## Type scale

All font sizes live in `tokens.css` as `--text-2xs` through `--text-2xl`,
plus `--leading-*` for line-height. New components should reach for one
of these instead of an arbitrary rem value, so hierarchy stays
predictable as screens are added.

## Layout

- Sidebar is a fixed-width nav; the active tab gets the yellow accent
  bar (see above) plus a filled dark background — no other tab state
  uses color beyond hover's neutral background shift. Each tab also
  carries a live count grounded in real document state (Library: total
  documents; Ask/Search: documents actually `ready` to query) — not a
  decorative badge.
- The dog-ear fold on `.source-card` is echoed at two other scales: the
  sidebar brand mark and the answer text block. This is the one
  structural motif tying nav → answer → source together as "the same
  kind of paper," so don't add a fourth variant without a reason tied to
  provenance.
- Main content area always opens with the `StatusStrip` (API health +
  document readiness + last upload), so the user's trust signals are
  visible before they even look at a panel.
- Panels cap at `900px` max-width for readability; source/result grids
  use `auto-fill, minmax(240px, 1fr)` so they reflow naturally rather
  than needing manual breakpoints.

## Constraints that don't change

- No backend files, endpoints, or response fields are ever modified from
  the frontend side. Every field rendered in a component must map to an
  actual field on `DocumentResponse`, `AnswerResponse`, or
  `RetrievedChunk` (see `backend/app/models/`).
- Prefer small, targeted changes over rewrites. If a redesign pass only
  needs to touch 2–3 files to fix a real problem, don't touch the rest.
