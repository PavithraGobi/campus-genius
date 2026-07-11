# Phase 7 — Viva Question Generation — frontend patch (v2)

## How to apply
Copy into your local `campus-genius/frontend/` checkout, same relative paths:

- src/components/VivaPanel.jsx  -> NEW file
- src/api/client.js              -> REPLACE (only addition: generateViva() at the end)
- src/components/Sidebar.jsx     -> REPLACE (only addition: "viva" tab entry + HelpCircle icon import)
- src/App.jsx                    -> REPLACE (only addition: VivaPanel import + tab render line)
- src/styles/index.css           -> REPLACE (bugfix, unrelated to viva - see below)

## Bonus fix included: fold-echo motif CSS
While checking that VivaPanel matches your theme, found that SourceCard.jsx renders
`.source-card-fold` and `.source-card-perforation` divs (used on Search tab results),
but there was NO matching CSS anywhere in the stylesheet - those divs were rendering
as empty/invisible. Added the missing rules (dog-ear corner fold + perforated left
edge), using only existing design tokens (--surface, --border) - no new colors
introduced. This affects the Search tab too, not just Viva - it's a pre-existing gap,
not something the viva work caused.

VivaPanel's cards now include the same fold/perforation divs so Viva results look
identical to Search results.

## Verified
`npm run build` succeeds with zero errors after all changes (Vite v5.4.21, 1606
modules transformed).

## Test after applying
1. Make sure the Phase 7 backend patch (phase7-viva-backend.zip) is applied and running first.
2. npm run dev
3. Check the Search tab first - source cards should now show a small folded corner
   (top-right) and a dashed perforation line (left edge) that weren't visible before.
4. New "Viva" tab appears in the sidebar between Search and Library.
5. Pick a ready document, set question count, click Generate.
6. Check: question cards match the same folded-corner/perforation look as Search
   results, difficulty badge shows, page references look right, "Regenerate" works,
   and an unknown/empty document shows the insufficient-context banner instead of
   a crash.
