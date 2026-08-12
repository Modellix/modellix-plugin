import assert from "node:assert/strict";
import { mkdir, mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const installer = path.join(root, "scripts", "install.mjs");

function run(args) {
  return spawnSync(process.execPath, [installer, ...args], {
    cwd: root,
    encoding: "utf8",
  });
}

test("installer requires an explicit host", () => {
  const result = run(["install"]);
  assert.equal(result.status, 1);
  assert.match(result.stderr, /--host is required/u);
});

test("portable dry run does not create the target", async () => {
  const temporary = await mkdtemp(path.join(os.tmpdir(), "modellix-plugin-test-"));
  const target = path.join(temporary, "bundle");
  try {
    const result = run(["install", "--host", "portable", "--target", target, "--dry-run"]);
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /Would install @modellix\/modellix-plugin@/u);
    await assert.rejects(readFile(path.join(target, "plugin.json")));
  } finally {
    await rm(temporary, { force: true, recursive: true });
  }
});

test("portable install materializes the complete plugin without repository files", async () => {
  const temporary = await mkdtemp(path.join(os.tmpdir(), "modellix-plugin-test-"));
  const target = path.join(temporary, "bundle");
  try {
    const result = run(["install", "--host", "portable", "--target", target]);
    assert.equal(result.status, 0, result.stderr);
    const portableManifest = JSON.parse(await readFile(path.join(target, "plugin.json"), "utf8"));
    const packageManifest = JSON.parse(await readFile(path.join(target, "package.json"), "utf8"));
    assert.equal(portableManifest.name, "modellix");
    assert.equal(packageManifest.name, "@modellix/modellix-plugin");
    await readFile(path.join(target, "skills", "modellix", "SKILL.md"), "utf8");
    await assert.rejects(readFile(path.join(target, "tests", "test_repository.py")));
    await assert.rejects(readFile(path.join(target, ".github", "workflows", "skill_update.yml")));
    await assert.rejects(readFile(path.join(target, "AGENTS.md")));
    await assert.rejects(readFile(path.join(target, ".gitignore")));
  } finally {
    await rm(temporary, { force: true, recursive: true });
  }
});

test("force update preserves the previous destination as a backup", async () => {
  const temporary = await mkdtemp(path.join(os.tmpdir(), "modellix-plugin-test-"));
  const target = path.join(temporary, "bundle");
  try {
    await mkdir(target);
    await writeFile(path.join(target, "user-marker.txt"), "keep me\n", "utf8");
    const result = run(["install", "--host", "portable", "--target", target, "--force"]);
    assert.equal(result.status, 0, result.stderr);
    const backupName = (await readdir(temporary)).find((entry) => entry.startsWith("bundle.backup-"));
    assert.ok(backupName, "expected a timestamped backup directory");
    assert.equal(
      await readFile(path.join(temporary, backupName, "user-marker.txt"), "utf8"),
      "keep me\n",
    );
    await readFile(path.join(target, "plugin.json"), "utf8");
  } finally {
    await rm(temporary, { force: true, recursive: true });
  }
});
