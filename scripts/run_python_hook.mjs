#!/usr/bin/env node

/** Cross-platform launcher for the optional Python hook implementations. */

import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HOOKS = new Set([
  "modellix_run_guard",
  "modellix_task_watch",
  "modellix_stop_reminder",
]);

function failOpen(message) {
  process.stderr.write(`[modellix-hook] ${message}\n`);
  process.stdout.write("{}\n");
  process.exit(0);
}

const hookName = process.argv[2] || "";
if (!HOOKS.has(hookName)) {
  failOpen("unknown hook name; skipped");
}

let input;
try {
  input = readFileSync(0);
} catch {
  failOpen("could not read hook input; skipped");
}

const scriptPath = join(dirname(fileURLToPath(import.meta.url)), `${hookName}.py`);
const candidates =
  process.platform === "win32"
    ? [
        ["py", ["-3"]],
        ["python", []],
        ["python3", []],
      ]
    : [
        ["python3", []],
        ["python", []],
      ];

for (const [command, prefix] of candidates) {
  const probe = spawnSync(command, [...prefix, "--version"], {
    encoding: "utf8",
    timeout: 3_000,
    windowsHide: true,
  });
  if (probe.error?.code === "ENOENT") {
    continue;
  }
  const version = `${probe.stdout || ""}${probe.stderr || ""}`.trim();
  if (probe.status !== 0 || !/^Python 3(?:\.|\s|$)/i.test(version)) {
    continue;
  }
  const result = spawnSync(command, [...prefix, scriptPath], {
    input,
    encoding: "utf8",
    timeout: 9_000,
    windowsHide: true,
  });
  if (result.status === 0) {
    process.stdout.write(result.stdout || "{}\n");
    process.exit(0);
  }
  failOpen(`${hookName} failed; skipped`);
}

failOpen("Python 3 was not found; optional hook skipped");
