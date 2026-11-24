---
name: ui-craft
description: Build modern, developer-grade UI/UX following DESIGN.md with zero AI slop, SSR-first rendering, and replay fallbacks.
---

# Skill: Modern Technical UI/UX Craft

## When to Trigger
- Creating or editing any page, layout, component, dashboard, chart, or interactive demo.

## Execution Protocol
1. **Enforce `DESIGN.md` Tokens:**
   - Commit to either **Light Editorial** or **Dark Telemetry**.
   - Apply `font-mono tabular-nums` to all numbers, metrics, prices, timestamps, and hashes.
   - Use `1px` hairline borders and restrained radius (`6px`/`8px`). Strip all neon gradients, glow orbs, and buzzwords.
2. **Zero-Friction Proof Above the Fold:**
   - Ensure the hero contains a real interactive preview, diff, simulator, or live replay that works **without wallet connection or signup**.
3. **Resilient Data Pattern (Recorded Replay + Live Upgrade):**
   - Initialize telemetry components with a real recorded snapshot (`initialData`) so SSR/first paint renders immediately with real numbers.
   - Hydrate/poll live endpoints asynchronously; if live fetch fails or times out, stay on the recorded replay and show an honest `REPLAY` / `OFFLINE` status pill.
4. **4-State Completeness:**
   - Verify `loading` (layout-matched skeleton), `empty` (clear CTA), `error` (actionable retry), and `data` states exist for every async view.
