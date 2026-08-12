#!/usr/bin/env node

import { constants as fsConstants } from "node:fs";
import {
  access,
  chmod,
  copyFile,
  mkdir,
  readdir,
  readFile,
  rename,
  rm,
  stat,
} from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const PACKAGE_NAME = "@modellix/modellix-plugin";
const PLUGIN_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SUPPORTED_HOSTS = new Set(["cursor", "portable"]);
const INCLUDED_NAMES = new Set([
  ".agents",
  ".claude-plugin",
  ".codex-plugin",
  ".cursor-plugin",
  ".mcp.json",
  ".opencode",
  ".pi",
  ".plugin",
  "CHANGELOG.md",
  "LICENSE",
  "README.md",
  "SECURITY.md",
  "assets",
  "commands",
  "hooks",
  "mcp.json",
  "openclaw.plugin.json",
  "package.json",
  "plugin.json",
  "rules",
  "scripts",
  "skills",
]);

function usage() {
  return `Install the Modellix Agent Plugin from its npm package.

Usage:
  modellix-plugin install --host cursor [--force] [--dry-run]
  modellix-plugin install --host portable --target <directory> [--force] [--dry-run]

Hosts:
  cursor    Install into ~/.cursor/plugins/local/modellix.
  portable  Materialize the complete Agent Plugins bundle at --target.

Options:
  --host <host>      Required: cursor or portable.
  --target <path>    Override the destination. Required for portable installs.
  --force            Replace an existing destination after moving it to a backup.
  --dry-run          Validate and print the destination without changing files.
  -h, --help         Show this help.
  -v, --version      Print the package version.
`;
}

function fail(message) {
  process.stderr.write(`modellix-plugin: ${message}\n`);
  process.exitCode = 1;
}

function parseArgs(argv) {
  const args = [...argv];
  const options = { command: null, dryRun: false, force: false, host: null, target: null };

  while (args.length) {
    const arg = args.shift();
    if (arg === "-h" || arg === "--help") {
      options.help = true;
    } else if (arg === "-v" || arg === "--version") {
      options.version = true;
    } else if (arg === "--dry-run") {
      options.dryRun = true;
    } else if (arg === "--force") {
      options.force = true;
    } else if (arg === "--host" || arg === "--target") {
      const value = args.shift();
      if (!value || value.startsWith("-")) {
        throw new Error(`${arg} requires a value`);
      }
      options[arg.slice(2)] = value;
    } else if (arg.startsWith("--host=")) {
      options.host = arg.slice("--host=".length);
    } else if (arg.startsWith("--target=")) {
      options.target = arg.slice("--target=".length);
    } else if (!options.command) {
      options.command = arg;
    } else {
      throw new Error(`unexpected argument: ${arg}`);
    }
  }

  return options;
}

async function exists(candidate) {
  try {
    await access(candidate, fsConstants.F_OK);
    return true;
  } catch {
    return false;
  }
}

function normalized(candidate) {
  const resolved = path.resolve(candidate);
  return process.platform === "win32" ? resolved.toLowerCase() : resolved;
}

function contains(parent, child) {
  const relative = path.relative(normalized(parent), normalized(child));
  return relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative));
}

function validateDestination(target) {
  const resolved = path.resolve(target);
  const home = path.resolve(os.homedir());
  const root = path.parse(resolved).root;

  if (normalized(resolved) === normalized(home) || normalized(resolved) === normalized(root)) {
    throw new Error("refusing to install over the home directory or filesystem root");
  }
  if (contains(PLUGIN_ROOT, resolved) || contains(resolved, PLUGIN_ROOT)) {
    throw new Error("source and destination must not contain one another");
  }
  return resolved;
}

function destinationFor(options) {
  if (options.target) return validateDestination(options.target);
  if (options.host === "cursor") {
    return validateDestination(path.join(os.homedir(), ".cursor", "plugins", "local", "modellix"));
  }
  throw new Error("--target is required for --host portable");
}

function shouldCopy(source) {
  if (normalized(source) === normalized(PLUGIN_ROOT)) return true;
  const relative = path.relative(PLUGIN_ROOT, source);
  const parts = relative.split(path.sep);
  const first = parts[0];
  return (
    INCLUDED_NAMES.has(first)
    && !parts.includes("__pycache__")
    && !relative.endsWith(".pyc")
    && !relative.endsWith(".tgz")
  );
}

async function copyTree(source, destination) {
  if (!shouldCopy(source)) return;

  const sourceStat = await stat(source);
  if (sourceStat.isDirectory()) {
    await mkdir(destination, { recursive: true });
    for (const entry of await readdir(source)) {
      await copyTree(path.join(source, entry), path.join(destination, entry));
    }
    return;
  }
  if (!sourceStat.isFile()) {
    throw new Error(`unsupported package entry: ${path.relative(PLUGIN_ROOT, source)}`);
  }

  await copyFile(source, destination, fsConstants.COPYFILE_EXCL);
  if (process.platform !== "win32") await chmod(destination, sourceStat.mode & 0o777);
}

async function packageMetadata() {
  const manifest = JSON.parse(await readFile(path.join(PLUGIN_ROOT, "package.json"), "utf8"));
  if (manifest.name !== PACKAGE_NAME || !manifest.version) {
    throw new Error("package metadata is invalid");
  }
  for (const required of ["plugin.json", "mcp.json", "skills/modellix/SKILL.md"]) {
    if (!(await exists(path.join(PLUGIN_ROOT, ...required.split("/"))))) {
      throw new Error(`package is missing required plugin content: ${required}`);
    }
  }
  return manifest;
}

async function moveAside(target) {
  const stamp = new Date().toISOString().replaceAll(":", "-").replaceAll(".", "-");
  const backup = `${target}.backup-${stamp}`;
  await rename(target, backup);
  return backup;
}

async function install(options, manifest) {
  const target = destinationFor(options);
  const targetExists = await exists(target);

  if (targetExists && !options.force) {
    throw new Error(`destination already exists: ${target} (re-run with --force to update)`);
  }

  process.stdout.write(`${options.dryRun ? "Would install" : "Installing"} ${PACKAGE_NAME}@${manifest.version}\n`);
  process.stdout.write(`Host: ${options.host}\nDestination: ${target}\n`);
  if (options.dryRun) return;

  const parent = path.dirname(target);
  const staging = path.join(parent, `.modellix-install-${process.pid}-${Date.now()}`);
  let backup = null;
  await mkdir(parent, { recursive: true });

  try {
    await copyTree(PLUGIN_ROOT, staging);

    if (targetExists) backup = await moveAside(target);
    await rename(staging, target);
  } catch (error) {
    await rm(staging, { force: true, recursive: true });
    if (backup && !(await exists(target))) await rename(backup, target);
    throw error;
  }

  process.stdout.write(`Installed ${PACKAGE_NAME}@${manifest.version}.\n`);
  if (backup) process.stdout.write(`Previous install preserved at: ${backup}\n`);
  if (options.host === "cursor") {
    process.stdout.write("Reload the Cursor window, then confirm Modellix under Customize > Plugins.\n");
  } else {
    process.stdout.write("Point your Agent Plugins-compatible host at the destination shown above.\n");
  }
}

async function main() {
  let options;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (error) {
    fail(error.message);
    process.stderr.write(usage());
    return;
  }

  const manifest = await packageMetadata();
  if (options.version) {
    process.stdout.write(`${manifest.version}\n`);
    return;
  }
  if (options.help) {
    process.stdout.write(usage());
    return;
  }
  if (options.command !== "install") {
    fail("the install command is required");
    process.stderr.write(usage());
    return;
  }
  if (!options.host) {
    fail("--host is required; use cursor or portable");
    process.stderr.write(usage());
    return;
  }
  if (!SUPPORTED_HOSTS.has(options.host)) {
    fail(`unsupported host: ${options.host}`);
    process.stderr.write(usage());
    return;
  }

  try {
    await install(options, manifest);
  } catch (error) {
    fail(error.message);
  }
}

await main();
