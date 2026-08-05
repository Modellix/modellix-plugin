#!/usr/bin/env node

/** Run the stdlib unittest suite with the available Python 3 command. */

import { spawnSync } from "node:child_process";

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
  const result = spawnSync(
    command,
    [...prefix, "-m", "unittest", "discover", "-s", "tests", "-v"],
    { stdio: "inherit", windowsHide: true },
  );
  process.exit(result.status ?? 1);
}

process.stderr.write("Python 3 is required to run the repository tests.\n");
process.exit(1);
