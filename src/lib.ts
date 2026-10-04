import { Freestyle, type CreateTlsRuleOptions, type Vm, type VmData } from "freestyle";

export const WORKDIR = "/work";
export const POD_DIR = "/home/ubuntu/.pod";
export const BASE_PREFIX = "base-";
export const POD_PREFIX = "pod-";

export const SIZES = {
  sm: "freestyle/ubuntu-sm", // 2 vCPU / 4 GiB / 16 GB
  md: "freestyle/ubuntu", //    4 vCPU / 8 GiB / 32 GB
  lg: "freestyle/ubuntu-lg", // 8 vCPU / 16 GiB / 64 GB (Hobby+)
} as const;
export type Size = keyof typeof SIZES;

// Created on first use so `pods --help` works without an API key.
let client: Freestyle | undefined;
export const fs = new Proxy({} as Freestyle, { get: (_, key) => Reflect.get((client ??= new Freestyle()), key) });

export function die(message: string): never {
  console.error(`error: ${message}`);
  process.exit(1);
}

export function log(message: string) {
  console.error(`· ${message}`);
}

/** Single-quote a string for bash. */
export const q = (s: string) => `'${s.replace(/'/g, `'\\''`)}'`;

const b64 = (s: string) => Buffer.from(s, "utf8").toString("base64");

/** Run a bash script as the `ubuntu` user; throws on a non-zero exit. */
export async function sh(vm: Vm, script: string, timeoutMs = 120_000): Promise<string> {
  const r = await vm.exec({ command: "bash -s", stdin: b64(`set -euo pipefail\n${script}`), timeoutMs });
  if (r.statusCode !== 0) {
    throw new Error(`exit ${r.statusCode}\n${(r.stderr || r.stdout || "").trim()}`);
  }
  return (r.stdout ?? "").trimEnd();
}

/** Write a file in the guest as `ubuntu` (vm.fs writes as root). */
export async function writeFile(vm: Vm, path: string, content: string, mode = "644") {
  const dir = path.slice(0, path.lastIndexOf("/")) || "/";
  await sh(vm, `mkdir -p ${q(dir)}\nbase64 -d > ${q(path)} <<'EOF'\n${b64(content)}\nEOF\nchmod ${mode} ${q(path)}`);
}

/**
 * Start a script detached from the exec call, which is capped at 5 minutes.
 * Output goes to `$POD_DIR/<name>.log`, the exit code to `$POD_DIR/<name>.exit`.
 */
export async function spawn(vm: Vm, name: string, script: string) {
  const file = `${POD_DIR}/${name}.sh`;
  await writeFile(vm, file, `#!/usr/bin/env bash\nset -uo pipefail\n${script}\n`, "755");
  await sh(
    vm,
    `rm -f ${POD_DIR}/${name}.exit
     setsid nohup bash -c '${file} > ${POD_DIR}/${name}.log 2>&1; echo $? > ${POD_DIR}/${name}.exit' >/dev/null 2>&1 < /dev/null &`,
  );
}

/** Exit code of a spawned script, or null while it is still running. Works on paused VMs. */
export async function exitCode(vm: Vm, name: string): Promise<number | null> {
  try {
    return Number((await vm.fs.readTextFile(`${POD_DIR}/${name}.exit`)).trim());
  } catch {
    return null;
  }
}

export async function wait(vm: Vm, name: string, pollMs = 3000): Promise<number> {
  for (;;) {
    const code = await exitCode(vm, name);
    if (code !== null) return code;
    await new Promise((r) => setTimeout(r, pollMs));
  }
}

export async function readLog(vm: Vm, name: string): Promise<string> {
  try {
    return await vm.fs.readTextFile(`${POD_DIR}/${name}.log`);
  } catch {
    return "";
  }
}

/**
 * Egress rules that hold credentials at the Freestyle edge. The guest only ever
 * sees placeholders; the edge overwrites the auth header on the way out.
 * Inline rules (no source identity) belong to the VM being created.
 */
export function secretRules(): CreateTlsRuleOptions[] {
  const rules: CreateTlsRuleOptions[] = [];
  const anthropic = process.env.ANTHROPIC_API_KEY?.trim();
  if (anthropic) {
    rules.push({
      action: "allow",
      domain: "api.anthropic.com",
      source: {},
      destination: { public: true },
      match: { method: ["POST"], path: { exact: "/v1/messages" } },
      transform: [{ headers: { "x-api-key": anthropic } }],
    });
  }
  // Deliberately not GITHUB_TOKEN: ambient CI/gh tokens are often broad-scoped.
  const github = process.env.PODS_GITHUB_TOKEN?.trim();
  if (github) {
    const basic = Buffer.from(`x-access-token:${github}`).toString("base64");
    rules.push({
      action: "allow",
      domain: "github.com",
      source: {},
      destination: { public: true },
      transform: [{ headers: { authorization: `Basic ${basic}` } }],
    });
  }
  return rules;
}

export function firewall(internet: boolean) {
  return { rules: internet ? [{ action: "allow" as const, source: {}, destination: { public: true as const } }] : [] };
}

/** Delete and confirm. A delete issued right after a snapshot can be dropped, so retry. */
export async function destroy(vmIdOrSlug: string) {
  for (let attempt = 0; attempt < 10; attempt++) {
    await fs.vms.delete(vmIdOrSlug).catch(() => {});
    await new Promise((r) => setTimeout(r, 1500));
    if (!(await fs.vms.get(vmIdOrSlug).then(() => true, () => false))) return;
  }
  throw new Error(`could not delete ${vmIdOrSlug}; remove it with \`freestyle vm delete ${vmIdOrSlug}\``);
}

export const podSlug =(task: string) => `${POD_PREFIX}${task}`;
export const baseSlug = (name: string) => `${BASE_PREFIX}${name}`;

export async function pods(): Promise<VmData[]> {
  const { vms } = await fs.vms.list({ limit: 200 });
  return vms.filter((v) => v.metadata?.pods === "1");
}

export async function pod(task: string): Promise<{ vm: Vm; data: VmData }> {
  const data = await fs.vms.get(podSlug(task)).catch(() => die(`no pod "${task}" (see \`pods ls\`)`));
  return { vm: fs.vms.ref(data.id), data };
}

export async function snapshotBySlug(slug: string) {
  const { snapshots } = await fs.vms.snapshots.list({ limit: 200 });
  return snapshots.find((s) => s.slug === slug);
}
