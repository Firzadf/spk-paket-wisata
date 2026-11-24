# DESIGN.md — Modern Technical Product & UI/UX Constitution

Your aesthetic benchmark is **Stripe, Linear, Vercel, and Cloudflare Docs** — NOT generic Web3/SaaS AI templates. Every visual and UX decision optimizes for **clarity, speed, verifiability, and zero-friction interaction**.

---

## 1. Anti-Slop Rules (STRICTLY BANNED)

- **No AI-slop color tropes:** No neon purple/pink/cyan glowing radial gradients, no rainbow gradient text (`bg-gradient-to-r from-purple-500 to-pink-500`), no floating blurred neon orbs.
- **No glassmorphism abuse:** No heavy `backdrop-blur-xl` cards stacked over noisy backgrounds. Use solid surfaces with crisp `1px` borders.
- **No buzzword copy:** Banned words: *"Revolutionary"*, *"Next-Gen"*, *"Seamless"*, *"Unlock the power of"*, *"Empowering"*, *"Game-changing"*, *"Decentralized future"*. Write concrete, verifiable facts.
- **No decorative filler:** Never place generic 3-column icon cards with vague marketing blurbs when a real data table, live telemetry, code diff, or interactive sandbox communicates faster.
- **No wallet-wall or auth-wall on entry:** First-time visitors must be able to inspect, simulate, or test the core product within **10 seconds** without connecting a wallet, signing up, or installing anything.

---

## 2. Visual System & Tokens

Pick **ONE** mode per project (do not muddy Light and Dark):

### Mode A — Light Editorial (Docs, Protocols, Finance, Legal, Escrow)
- Canvas: `#FAFAFA` / `#FFFFFF` | Card Surface: `#FFFFFF` (`1px solid #E5E7EB`) | Subtle Surface: `#F4F4F5`
- Text: Primary `#09090B`, Secondary `#52525B`, Muted `#71717A`
- Primary Accent (Pick 1): Deep Ink `#18181B`, Cobalt `#2563EB`, or Forest `#059669`
- Semantic Status:
  - Pass / Live / Verified: `#16A34A` (bg `#F0FDF4`, border `#BBF7D0`)
  - Warning / Simulated / Diff: `#D97706` (bg `#FFFBEB`, border `#FDE68A`)
  - Error / Regression / Revert: `#DC2626` (bg `#FEF2F2`, border `#FECACA`)

### Mode B — Dark Telemetry (Infra, Bridges, Security, DevTools)
- Canvas: `#0A0A0C` | Card Surface: `#111114` (`1px solid #232329`) | Elevated: `#18181D`
- Text: Primary `#F4F4F5`, Secondary `#A1A1AA`, Muted `#71717A`
- Single Accent: `#3B82F6` or `#10B981` or `#F59E0B` (< 5% viewport area).

### Typography & Geometry
- **Headings & UI:** `Inter` or `Geist Sans` (`letter-spacing: -0.025em` on H1/H2).
- **Numbers, Hashes, Code, Badges:** `JetBrains Mono` / `Geist Mono` with `font-variant-numeric: tabular-nums` on **every** number, price, block height, timer, and table cell.
- **Borders & Radius:** Hairline `1px solid` borders instead of heavy drop shadows (`shadow-xl` banned except modals). Radius: `6px` (`rounded-md`) or `8px` (`rounded-lg`) for cards/buttons, `4px` for badges. No `rounded-3xl` bubbles.

---

## 3. Winning Page Architecture (Proof-First Flow)

1. **Minimal Header (<= 56px):** Wordmark left, 3–5 concise nav links, 1 primary CTA.
2. **Hero = Concrete Claim + Live Interactive Surface:**
   - Eyebrow badge with real status (`LIVE ON TESTNET · BLOCK #282559`).
   - H1 stating concrete outcome in <= 2 lines.
   - Right column (or immediate below-fold): **live interactive product surface** (replay, clickable simulator, terminal diff) usable with zero login/wallet.
3. **Quantified Problem / Benchmark:** Before/after comparison using real measured numbers.
4. **How It Works (3 Deterministic Steps):** Numbered `01`, `02`, `03` with real payload/code/state transitions.
5. **Interactive Lab / Sandbox:** Let users trigger edge cases, failure modes, or scenarios and inspect deterministic results.
6. **Verifiable Proof & Receipts:** Real explorer links, contract addresses, test counts, or downloadable JSON evidence.
7. **Honesty / Threat Model / Scope Boundary:** Explicitly separate *Live vs Simulated* and *Trusted vs Trustless*. Tag every panel (`LIVE`, `SIMULATED`, `READ-ONLY`).

---

## 4. Frontend Engineering Standards

- **SSR / Static First:** Landing, docs, and proof pages MUST render semantic HTML on first load. Never ship a blank CSR-only shell for public pages.
- **Recorded Replay Fallback:** When displaying live RPC/API telemetry, bundle a real recorded snapshot as initial state so first paint is instantly alive, then upgrade smoothly to live polling/WS. Never show infinite spinners.
- **Copy-Friendly Technical UI:** Truncate hashes cleanly (`0x58bb…8bc2`) in monospace with 1-click copy and explorer link.
