from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class RepositoryTests(unittest.TestCase):
    def test_json_files_parse(self):
        for path in ROOT.rglob("*.json"):
            if ".git" not in path.parts:
                with self.subTest(path=path.relative_to(ROOT)):
                    json.loads(path.read_text(encoding="utf-8"))

    def test_versions_are_synchronized(self):
        expected = read_json("package.json")["version"]
        versions = {
            read_json("plugin.json")["version"],
            read_json(".plugin/plugin.json")["version"],
            read_json(".cursor-plugin/plugin.json")["version"],
            read_json(".claude-plugin/plugin.json")["version"],
            read_json(".codex-plugin/plugin.json")["version"],
            read_json(".claude-plugin/marketplace.json")["metadata"]["version"],
            read_json("skills/modellix/skill.json")["version"],
        }
        skill_text = (ROOT / "skills/modellix/SKILL.md").read_text(encoding="utf-8")
        versions.add(
            re.search(
                r'(?m)^  version:\s*["\']?([^"\'\s]+)["\']?$', skill_text
            ).group(1)
        )
        self.assertEqual(versions, {expected})

    def test_agent_plugins_1_0_core_layout(self):
        manifest = read_json("plugin.json")
        mcp = read_json("mcp.json")
        self.assertEqual(
            manifest["$schema"],
            "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        )
        self.assertEqual(
            set(manifest)
            - {
                "$schema",
                "name",
                "version",
                "description",
                "author",
                "homepage",
                "repository",
                "license",
                "keywords",
                "extensions",
            },
            set(),
        )
        self.assertEqual(
            mcp["$schema"],
            "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
        )
        self.assertEqual(set(mcp), {"$schema", "mcpServers"})
        docs_server = mcp["mcpServers"]["modellix-docs"]
        self.assertEqual(docs_server["type"], "streamable-http")
        self.assertTrue(docs_server["url"].startswith("https://"))
        self.assertTrue((ROOT / "skills/modellix/SKILL.md").is_file())

    def test_agent_skill_frontmatter_uses_standard_fields(self):
        text = (ROOT / "skills/modellix/SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        top_level = {
            line.split(":", 1)[0]
            for line in frontmatter.splitlines()
            if line and not line[0].isspace()
        }
        self.assertEqual(
            top_level,
            {"name", "description", "license", "compatibility", "metadata"},
        )
        metadata_lines = [
            line.strip()
            for line in frontmatter.splitlines()
            if line.startswith("  ") and not line.startswith("    ")
        ]
        self.assertTrue(metadata_lines)
        self.assertTrue(all(": " in line for line in metadata_lines))

    def test_cursor_manifest_matches_official_surface(self):
        manifest = read_json(".cursor-plugin/plugin.json")
        allowed = {
            "name",
            "displayName",
            "description",
            "version",
            "minClientVersions",
            "author",
            "publisher",
            "homepage",
            "repository",
            "license",
            "logo",
            "keywords",
            "category",
            "tags",
            "commands",
            "agents",
            "skills",
            "rules",
            "hooks",
            "variables",
            "mcpServers",
        }
        self.assertEqual(set(manifest) - allowed, set())
        self.assertRegex(manifest["name"], r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")
        self.assertEqual(set(manifest["author"]) - {"name", "email"}, set())
        for field in ("logo", "commands", "skills", "rules", "hooks", "mcpServers"):
            path = ROOT / manifest[field]
            self.assertTrue(path.exists(), f"missing Cursor component path: {field}={path}")

    def test_all_plugin_identifiers_are_lowercase(self):
        for path in (
            "plugin.json",
            ".plugin/plugin.json",
            ".cursor-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
        ):
            name = read_json(path)["name"]
            with self.subTest(path=path):
                self.assertRegex(name, r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")

    def test_cursor_marketplace_entry_resolves(self):
        marketplace = read_json(".cursor-plugin/marketplace.json")
        self.assertEqual(marketplace["plugins"][0]["name"], "modellix")
        source = (ROOT / marketplace["plugins"][0]["source"]).resolve()
        self.assertEqual(source, ROOT.resolve())

    def test_commands_have_frontmatter_and_paid_guards(self):
        command_paths = sorted((ROOT / "commands").glob("*.md"))
        self.assertEqual({p.stem for p in command_paths}, {
            "audio", "doctor", "download", "image", "models", "tasks", "video"
        })
        for path in command_paths:
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            frontmatter = text.split("---", 2)[1]
            self.assertIn("description:", frontmatter)
            if path.stem in {"audio", "image", "video"}:
                self.assertIn("disable-model-invocation: true", frontmatter)

    def test_repository_does_not_ship_maintainer_agent_hooks(self):
        self.assertFalse((ROOT / ".cursor/hooks.json").exists())
        maintainer_hooks = ROOT / ".cursor/hooks"
        self.assertFalse(
            maintainer_hooks.exists() and any(path.is_file() for path in maintainer_hooks.rglob("*"))
        )
        active_hooks = (
            (ROOT / "hooks/hooks.json").read_text(encoding="utf-8")
            + (ROOT / "hooks/cursor-hooks.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("community", active_hooks)
        self.assertNotIn("git\\s+push", active_hooks)

    def test_task_result_schema_supports_cli_and_download(self):
        schema = read_json("skills/modellix/assets/output/task-result.schema.json")
        self.assertIn("download", schema["properties"])
        self.assertNotIn("required", schema["properties"]["raw"])

    def test_package_excludes_python_build_artifacts(self):
        package = read_json("package.json")
        files = package["files"]
        self.assertIn("plugin.json", files)
        self.assertIn("mcp.json", files)
        self.assertIn("!scripts/**/*.pyc", files)
        self.assertIn("!skills/**/*.pyc", files)
        self.assertIn("!scripts/**/__pycache__/**", files)
        self.assertIn("!skills/**/__pycache__/**", files)
        self.assertEqual(package["bin"]["modellix-plugin"], "scripts/install.mjs")
        self.assertEqual(package["publishConfig"]["access"], "public")
        self.assertEqual(
            package["publishConfig"]["registry"], "https://registry.npmjs.org/"
        )

    def test_relative_markdown_links_exist(self):
        pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
        for path in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.mdc")):
            if ".git" in path.parts:
                continue
            for target in pattern.findall(path.read_text(encoding="utf-8")):
                target = target.strip().split("#", 1)[0]
                if not target or "://" in target or target.startswith(("mailto:", "#")):
                    continue
                with self.subTest(path=path.relative_to(ROOT), target=target):
                    self.assertTrue((path.parent / target).exists())

    def test_no_common_secret_token_prefixes(self):
        patterns = (
            r"github_pat_[A-Za-z0-9_]{20,}",
            r"ghp_[A-Za-z0-9]{20,}",
            r"npm_[A-Za-z0-9]{20,}",
            r"AKIA[0-9A-Z]{16}",
            r"sk-[A-Za-z0-9]{20,}",
        )
        combined = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.parts
        )
        for pattern in patterns:
            self.assertIsNone(re.search(pattern, combined), pattern)

    def test_workflow_dependencies_are_not_floating(self):
        workflow = (ROOT / ".github/workflows/skill_update.yml").read_text(encoding="utf-8")
        self.assertNotRegex(workflow, r"uses:\s+[^\s]+@(main|master|v\d+)\s*$")


if __name__ == "__main__":
    unittest.main()
