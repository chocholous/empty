#!/usr/bin/env node
// pods — disposable Claude Code environments on Freestyle VMs.
// One snapshot per repo ("base"), one VM per task ("pod"), secrets held at the edge.
import { parseArgs } from "node:util";
import {
  BASE_PREFIX, POD_DIR, POD_PREFIX, SIZES, WORKDIR, type Size,
  baseSlug, destroy, die, exitCode, firewall, fs, log, pod, podSlug, pods, q, readLog,
  secretRules, sh, snapshotBySlug, spawn, wait, writeFile,
} from "./lib.ts";

const USAGE = `pods — Claude Code pods on Freestyle VMs

  pods bake <base> --repo <git-url> [--ref main] [--setup "<cmd>"] [--size sm|md|lg]
      Build a snapshot: clone, run setup, pre-answer Claude Code onboarding.
  pods up <task> --base <base> [--offline]       Start a pod from a base, on branch pods/<task>.
  pods run <task> "<prompt>" [--model <id>] [--wait]
      Run Claude Code headless in the pod (detached; survives this process).
  pods fanout <task> --base <base> -n <N> "<prompt>" [--model <id>]
      N pods from the same snapshot, same prompt: <task>-1 … <task>-N.
  pods ls                                        Pods, their state and last run.
  pods bases                                     Baked snapshots.
  pods logs <task> [-f]                          Claude's progress (readable while paused).
  pods diff <task>                               Everything the agent changed since up.
  pods push <task>                               Commit and push pods/<task> (needs PODS_GITHUB_TOKEN).
  pods exec <task> -- <cmd>                      Run a command in /work.
  pods pause|resume <task>                       Pause keeps memory and bills only disk.
  pods down <task...> | --all                    Delete pods.
  pods unbake <base>                             Delete a base snapshot.

Env: FREESTYLE_API_KEY (required), ANTHROPIC_API_KEY, PODS_GITHUB_TOKEN — both injected
at the Freestyle edge, never written into a VM or snapshot.`;

const { positionals, values: o } = parseArgs({
  allowPositionals: true,
  options: {
    repo: { type: "string" },
    ref: { type: "string" },
    setup: { type: "string" },
    size: { type: "string", default: "sm" },
    base: { type: "string" },
    model: { type: "string" },
    n: { type: "string", short: "n", default: "3" },
    offline: { type: "boolean", default: false },
    wait: { type: "boolean", default: false },
    follow: { type: "boolean", short: "f", default: false },
    all: { type: "boolean", default: false },
    help: { type: "boolean", short: "h", default: false },
  },
});
const [cmd, ...args] = positionals;

if (!process.env.FREESTYLE_API_KEY && cmd && !o.help) die("FREESTYLE_API_KEY is not set (put it in .env)");

// Claude Code reads its config from here; seeding it skips the first-run wizard
// and the per-directory trust prompt.
const claudeJson = JSON.stringify({
  hasCompletedOnboarding: true,
  theme: "dark",
  projects: { [WORKDIR]: { hasTrustDialogAccepted: true } },
});

async function bake(name: string) {
  if (!o.repo) die("--repo is required");
  const size = o.size as Size;
  if (!SIZES[size]) die(`--size must be one of ${Object.keys(SIZES).join(", ")}`);

  log(`builder from ${SIZES[size]}`);
  const { vm, vmId } = await fs.vms.create({
    snapshotId: SIZES[size],
    firewall: firewall(true),
    tls: { rules: secretRules().filter((r) => r.domain === "github.com") },
    metadata: { pods: "builder", base: name },
    ttlSeconds: 3600,
  });
  try {
    log(`clone ${o.repo}`);
    await sh(vm, `sudo install -d -o ubuntu -g ubuntu ${WORKDIR}
      git clone ${o.ref ? `--branch ${q(o.ref)}` : ""} ${q(o.repo)} ${WORKDIR}
      git -C ${WORKDIR} config user.name "pods"
      git -C ${WORKDIR} config user.email "pods@users.noreply.github.com"`, 300_000);
    await writeFile(vm, "/home/ubuntu/.claude.json", claudeJson);

    if (o.setup) {
      log(`setup: ${o.setup}`);
      await spawn(vm, "setup", `cd ${WORKDIR} && ${o.setup}`);
      const code = await wait(vm, "setup");
      if (code !== 0) die(`setup exited ${code}\n${(await readLog(vm, "setup")).slice(-4000)}`);
    }
    await sh(vm, `rm -rf ${POD_DIR}; git -C ${WORKDIR} status --short | head -5`);

    const slug = baseSlug(name);
    const old = await snapshotBySlug(slug);
    log("snapshot");
    const { snapshotId } = await vm.snapshot({ displayName: `${name} @ ${o.ref ?? "default"}` });
    if (old) await fs.vms.snapshots.delete(old.id);
    await fs.vms.snapshots.update(snapshotId, { slug });
    console.log(`${slug}  ${snapshotId}`);
  } finally {
    await destroy(vmId);
  }
}

async function up(task: string, base: string) {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(task)) die("task names are lowercase letters, digits and dashes");
  if (!secretRules().some((r) => r.domain === "api.anthropic.com")) log("ANTHROPIC_API_KEY not set: Claude will not authenticate");
  const { vm, vmId } = await fs.vms.create({
    snapshotId: baseSlug(base),
    slug: podSlug(task),
    firewall: firewall(!o.offline),
    tls: { rules: secretRules() },
    metadata: { pods: "1", task, base },
    idleTimeoutSeconds: 900, //       pause after 15 idle minutes; paused = disk-only billing
    maxRunTotalSeconds: 4 * 3600, //  hard compute budget per pod
    ttlSeconds: 7 * 24 * 3600, //     garbage-collect forgotten pods after a week
  });
  const sha = await sh(vm, `cd ${WORKDIR} && git checkout -q -b pods/${task} && git rev-parse HEAD`);
  await writeFile(vm, `${POD_DIR}/base-sha`, sha);
  console.log(`${podSlug(task)}  ${vmId}  pods/${task} @ ${sha.slice(0, 8)}`);
}

async function run(task: string, prompt: string) {
  const { vm } = await pod(task);
  if ((await exitCode(vm, "claude")) === null && (await readLog(vm, "claude"))) die(`a run is already in progress in ${task}`);
  await writeFile(vm, `${POD_DIR}/prompt.md`, prompt);
  // The key below is a placeholder: the edge rule swaps in the real one.
  await spawn(vm, "claude", `cd ${WORKDIR}
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
export ANTHROPIC_API_KEY=sk-ant-placeholder-replaced-at-the-edge
claude -p "$(cat ${POD_DIR}/prompt.md)" --dangerously-skip-permissions \\
  --output-format stream-json --verbose ${o.model ? `--model ${q(o.model)}` : ""} < /dev/null`);
  log(`started in ${task}; follow with: pods logs ${task} -f`);
  if (o.wait) {
    const code = await wait(vm, "claude", 5000);
    await logs(task, false);
    process.exitCode = code;
  }
}

/** Condense Claude's stream-json into one line per step. */
function render(raw: string): string {
  const out: string[] = [];
  for (const line of raw.split("\n")) {
    if (!line.trim()) continue;
    let e: any;
    try { e = JSON.parse(line); } catch { out.push(line); continue; }
    if (e.type === "assistant") {
      for (const c of e.message?.content ?? []) {
        if (c.type === "text" && c.text.trim()) out.push(`💬 ${c.text.trim()}`);
        if (c.type === "tool_use") out.push(`🔧 ${c.name} ${JSON.stringify(c.input).slice(0, 160)}`);
      }
    } else if (e.type === "system" && e.subtype === "api_retry") {
      out.push(`⏳ API retry ${e.attempt}/${e.max_retries} (${e.error_status} ${e.error})`);
    } else if (e.type === "result") {
      out.push(`${e.is_error ? "❌ error" : "✅ " + e.subtype} · ${e.num_turns ?? "?"} turns · $${(e.total_cost_usd ?? 0).toFixed(3)} · ${Math.round((e.duration_ms ?? 0) / 1000)}s`);
      if (e.result) out.push(e.result);
    }
  }
  return out.join("\n");
}

async function logs(task: string, follow: boolean) {
  const { vm } = await pod(task);
  let shown = 0;
  for (;;) {
    const text = render(await readLog(vm, "claude"));
    if (text.length > shown) process.stdout.write(text.slice(shown) + "\n");
    shown = text.length + 1;
    if (!follow || (await exitCode(vm, "claude")) !== null) return;
    await new Promise((r) => setTimeout(r, 4000));
  }
}

async function diff(task: string) {
  const { vm } = await pod(task);
  process.stdout.write(await sh(vm, `cd ${WORKDIR} && git add -A && git diff --cached $(cat ${POD_DIR}/base-sha)`) + "\n");
}

async function push(task: string) {
  if (!process.env.PODS_GITHUB_TOKEN) die("PODS_GITHUB_TOKEN is not set");
  const { vm } = await pod(task);
  console.log(await sh(vm, `cd ${WORKDIR}
    git add -A
    git diff --cached --quiet || git commit -q -m "pods: ${task}" -m "$(head -c 2000 ${POD_DIR}/prompt.md 2>/dev/null || true)"
    git push -q -u origin pods/${task} 2>&1
    echo "pushed pods/${task} @ $(git rev-parse --short HEAD)"`, 300_000));
}

async function ls() {
  const list = await pods();
  if (!list.length) return console.log("no pods");
  for (const v of list) {
    const vm = fs.vms.ref(v.id);
    const code = await exitCode(vm, "claude");
    const started = code !== null || (await readLog(vm, "claude")) !== "";
    const runState = !started ? "idle" : code === null ? "running" : code === 0 ? "done" : `failed(${code})`;
    const r = v.resources;
    console.log([
      (v.slug ?? v.id).replace(POD_PREFIX, "").padEnd(20), v.state.padEnd(8), runState.padEnd(10),
      `base=${v.metadata.base}`.padEnd(20), `${r.cpu}cpu/${Math.round(r.memory / 1024)}G`,
      `${Math.round((v.totalRunSeconds ?? 0) / 60)}min`,
    ].join("  "));
  }
}

async function bases() {
  const { snapshots } = await fs.vms.snapshots.list({ limit: 200 });
  const mine = snapshots.filter((s) => s.slug?.startsWith(BASE_PREFIX));
  if (!mine.length) return console.log("no bases");
  for (const s of mine) console.log(`${s.slug!.replace(BASE_PREFIX, "").padEnd(20)}  ${s.id}  ${s.displayName ?? ""}  ${s.createdAt}`);
}

async function main() {
  const need = (n: number, what: string) => { if (args.length < n) die(`usage: pods ${cmd} ${what}`); };
  switch (cmd) {
    case "bake": need(1, "<base> --repo <url>"); return bake(args[0]);
    case "up": need(1, "<task> --base <base>"); if (!o.base) die("--base is required"); return up(args[0], o.base);
    case "run": need(2, '<task> "<prompt>"'); return run(args[0], args.slice(1).join(" "));
    case "fanout": {
      need(2, '<task> --base <base> -n <N> "<prompt>"');
      if (!o.base) die("--base is required");
      const n = Number(o.n);
      const tasks = Array.from({ length: n }, (_, i) => `${args[0]}-${i + 1}`);
      await Promise.all(tasks.map((t) => up(t, o.base!)));
      await Promise.all(tasks.map((t) => run(t, args.slice(1).join(" "))));
      return;
    }
    case "ls": return ls();
    case "bases": return bases();
    case "logs": need(1, "<task>"); return logs(args[0], o.follow);
    case "diff": need(1, "<task>"); return diff(args[0]);
    case "push": need(1, "<task>"); return push(args[0]);
    case "exec": {
      need(2, "<task> -- <cmd>");
      const { vm } = await pod(args[0]);
      const r = await vm.exec({ command: `cd ${WORKDIR} && ${args.slice(1).join(" ")}`, timeoutMs: 300_000 });
      process.stdout.write(r.stdout ?? ""); process.stderr.write(r.stderr ?? "");
      process.exitCode = r.statusCode ?? 1;
      return;
    }
    case "pause": need(1, "<task>"); await (await pod(args[0])).vm.pause(); return log(`paused ${args[0]}`);
    case "resume": need(1, "<task>"); await (await pod(args[0])).vm.start(); return log(`resumed ${args[0]}`);
    case "down": {
      const targets = o.all ? (await pods()).map((v) => v.metadata.task) : args;
      if (!targets.length) die("usage: pods down <task...> | --all");
      await Promise.all(targets.map(async (t) => { await destroy(podSlug(t)); log(`deleted ${t}`); }));
      return;
    }
    case "unbake": {
      need(1, "<base>");
      const s = await snapshotBySlug(baseSlug(args[0]));
      if (!s) die(`no base "${args[0]}"`);
      await fs.vms.snapshots.delete(s.id);
      return log(`deleted base ${args[0]}`);
    }
    default: console.log(USAGE); if (cmd && !o.help) process.exitCode = 1;
  }
}

main().catch((e) => die(e instanceof Error ? e.message : String(e)));
