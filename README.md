# freestyle-pods

Disposable Claude Code environments on [Freestyle](https://www.freestyle.sh) VMs.
One **base** snapshot per repo, one **pod** (VM) per task, credentials held at
the network edge so they never enter a VM.

```
                 bake (once per repo)                 up / fanout (per task, ~1 s)
 git repo ──► builder VM ──► clone, setup ──► snapshot base-<repo> ──┬──► pod-a   (branch pods/a)
                                                                     ├──► pod-b   (branch pods/b)
                                                                     └──► pod-c   (branch pods/c)
 ANTHROPIC_API_KEY / PODS_GITHUB_TOKEN ──► Freestyle edge rule ──► injected on the way out
```

It replaces `git worktree` for agent work: each task gets its own machine, with
its own ports, Docker, databases and processes, started from a snapshot with
dependencies already installed instead of reinstalling them per worktree.

## Why this fits Freestyle

| Freestyle capability | How pods use it |
|---|---|
| Memory and disk snapshots, about 1 s boot | `bake` once, `up` any number of pods from it |
| Copies from one snapshot | `fanout -n 3`: same prompt, three attempts, keep the best diff |
| Pause keeps memory and bills only disk | idle pods pause after 15 min; `resume` in under 1 s, mid-task |
| Files readable while paused | `logs` and `ls` read run state without waking the VM |
| Egress rules that inject secrets at the edge | the Anthropic and GitHub credentials never touch the guest or a snapshot |
| Per-VM budgets and time limits | each pod: 4 h compute cap, deleted after 7 days |
| Claude Code preinstalled on the Ubuntu images | no install step; `bake` only pre-answers onboarding |

## Quickstart

Requires Node 22.18+ (runs the TypeScript directly, no build step).

```bash
npm install
cp .env.example .env            # FREESTYLE_API_KEY, ANTHROPIC_API_KEY, optional PODS_GITHUB_TOKEN

bin/pods bake app --repo https://github.com/you/app --setup "npm ci"
bin/pods up fix-login --base app
bin/pods run fix-login "Fix the login redirect bug and add a test" 
bin/pods logs fix-login -f
bin/pods diff fix-login > fix-login.patch      # or: bin/pods push fix-login
bin/pods down fix-login
```

Try three approaches at once:

```bash
bin/pods fanout cache --base app -n 3 "Add a response cache to the API client"
bin/pods ls
bin/pods diff cache-2
bin/pods down cache-1 cache-3
```

## Commands

| Command | What it does |
|---|---|
| `bake <base> --repo <url> [--ref <branch>] [--setup "<cmd>"] [--size sm\|md\|lg]` | Builder VM, clone into `/work`, run setup (no time limit), seed `~/.claude.json`, snapshot as `base-<base>`, delete builder. Re-baking replaces the old snapshot. |
| `up <task> --base <base> [--offline]` | Start `pod-<task>` from the base on a new branch `pods/<task>`. `--offline` gives no internet except the edge-injected endpoints. |
| `run <task> "<prompt>" [--model <id>] [--wait]` | `claude -p --dangerously-skip-permissions`, detached in the VM, so it outlives both this CLI and the 5-minute exec limit. |
| `fanout <task> --base <base> -n <N> "<prompt>"` | `up` and `run` for `<task>-1` … `<task>-N` in parallel. |
| `ls` / `bases` | Pods (VM state, run state, size, minutes run) and baked snapshots. |
| `logs <task> [-f]` | Claude's stream condensed to messages, tool calls, retries and the final result with its cost. |
| `diff <task>` | All changes since `up`, committed or not. |
| `push <task>` | Commit and push `pods/<task>` to `origin` (needs `PODS_GITHUB_TOKEN`). |
| `exec <task> -- <cmd>` | Run a command in `/work`. |
| `pause` / `resume <task>` | Freeze with memory kept, then continue where it left off. |
| `down <task...>` / `down --all`, `unbake <base>` | Delete pods or a base. |

Sizes: `sm` = 2 vCPU / 4 GiB (default), `md` = 4 / 8, `lg` = 8 / 16 (Hobby plan or higher).

## Security model

- **Anthropic key:** an inline egress rule on each pod overwrites `x-api-key` on
  `POST api.anthropic.com/v1/messages`. The guest runs Claude Code with a
  placeholder key. The rule is deleted with the VM.
- **GitHub:** only when `PODS_GITHUB_TOKEN` is set, a rule adds `Authorization`
  for `github.com` (private clones, `push`). It deliberately does not read
  `GITHUB_TOKEN`, so an ambient, broadly scoped token is never forwarded. Use a
  fine-grained token limited to the repos you bake.
- Snapshots hold code and dependencies only, never credentials.
- Every process in a pod can use the edge credentials. The isolation boundary
  is the VM, not the agent.

## Costs (list prices, Oct 2026)

| | `sm` (2 vCPU / 4 GiB) | `md` (4 / 8) |
|---|---|---|
| Running | about $0.13 / h | about $0.27 / h |
| Paused | about $1 / month | about $2 / month |

Free plan: 10 running VMs at once, at most 4 vCPU / 8 GiB each, 200 vCPU-hours
included each month. A 20-minute agent run on `sm` costs about $0.05 plus
Anthropic usage.

## Caveats

- The Anthropic rule covers `POST /v1/messages`, which is what headless
  `claude -p` uses. The edge path was verified to reach Anthropic, but not yet
  with a real key. If your Claude Code version also needs another endpoint, add
  a rule for it in `src/lib.ts`.
- `fanout` uses one Anthropic key for every pod, so parallel runs share your
  rate limit.
- Freestyle runs Linux only, so macOS and iOS builds are out of scope.

## Layout

```
bin/pods        entry point (loads .env)
src/pods.ts     CLI commands
src/lib.ts      Freestyle helpers: exec, detached jobs, edge secret rules, lookup
```
