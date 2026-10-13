# Next.js

Checked 2026-10-13: `create-next-app` 16.4.0 — Next 16.4.0, React 19.3.0 —
with pnpm 11.

## Scaffold

Read by `/work-bootstrap:new`.

```bash
pnpm dlx create-next-app@latest . --use-pnpm --skip-install --disable-git --yes <options>
```

- **Every option is passed.** `--yes` fills a missing one from the preferences
  an earlier run saved on this machine, and only then from the defaults — two
  machines, two different projects.
- **The owner's questions**, 16.4.0 defaults marked:
  - linter — `--eslint` (default) or `--biome`;
  - `--src-dir` — default off;
  - `--import-alias` — default `@/*`;
  - `--react-compiler` — default off;
  - `--cache-components` — **on by default, and `--help` does not say so.**
    No recommendation from here: it decides how every page renders, and with
    it `await params` is runtime data. On, it also writes
    `partialPrefetching: true` into `next.config`;
  - `--agent-feedback` — on under `--yes`: writes
    `experimental.agentFeedback: true` into `next.config`, and agents prepare
    anonymised feedback about Next for the owner's review.

  TypeScript, Tailwind, the App Router and `AGENTS.md` are defaults nobody
  has needed to ask about; each takes `--no-<flag>`, as do the options
  above.
- **The folder's name becomes the package name**, so npm's naming rules
  apply: no capitals, no spaces.
- **The folder may hold** `.claude`, `.git`, `.gitignore`, `.gitlab-ci.yml`,
  `.idea`, `.vscode`, `.zed`, `LICENSE`, `docs` and the like. Anything else —
  `AGENTS.md`, `CLAUDE.md`, `README.md` among them — and the generator
  refuses with "could conflict". It never deletes anything. This is why
  `new` runs before `setup`, never after.
- **The generator's git stays off.** Without `--disable-git` it commits
  "Initial commit from Create Next App" itself.
- **Pins.** The generator writes `packageManager: pnpm@<version>` and
  `pnpm-workspace.yaml` with `allowBuilds` for its own build scripts; neither
  is written twice. Add `.nvmrc` with the Node version the owner confirms —
  the running one by default — and
  `pnpm pkg set engines.node=">=<major> <<major+1>"`. Then `pnpm install`:
  it writes the lockfile and must finish without `ERR_PNPM_IGNORED_BUILDS`.

## For the harness

Read by `/work-bootstrap:setup`.

- **The generator writes `AGENTS.md`**, holding a block between
  `<!-- BEGIN:nextjs-agent-rules -->` and `<!-- END:nextjs-agent-rules -->`;
  `CLAUDE.md` is left to `setup`. Write around the block, never remove it:
  `next dev`, run by an agent, writes it back — appended at the end —
  whenever it is missing
  (`node_modules/next/dist/server/lib/generate-agent-files.js`).
- **`middleware.ts` is gone.** Next 16 renamed it: the file is `proxy.ts`,
  beside `app/`, and exports `proxy`. `AGENTS.md` says so once — older
  material teaches the old name.
- **With Cache Components, `params` is not free.** `await params` is runtime
  data; with locales, the locale comes from `next/root-params`, not from the
  `params` prop. `AGENTS.md` says so once.
- **`allowBuilds`.** `AGENTS.md` §2 carries the line from `templates.md` that
  a dependency with a build script needs an entry.
- **The type-check is `next typegen && tsc --noEmit`.** The generated
  `layout.tsx` uses the global `LayoutProps`, which exists only after type
  generation, and `next-env.d.ts` is ignored: `tsc` alone fails on a clean
  checkout.
