from __future__ import annotations

import json
import os
import re
import subprocess
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
            read_json("skills/modellix-design/skill.json")["version"],
        }
        skill_text = (ROOT / "skills/modellix-design/SKILL.md").read_text(encoding="utf-8")
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
        docs_server = mcp["mcpServers"]["Modellix Docs Search"]
        self.assertEqual(docs_server["type"], "streamable-http")
        self.assertEqual(docs_server["url"], "https://docs.modellix.ai/mcp")
        self.assertNotIn("headers", docs_server)
        self.assertTrue((ROOT / "skills/modellix-design/SKILL.md").is_file())
        self.assertEqual(
            read_json("skills/modellix-design/skill.json")["name"], "modellix-design"
        )
        self.assertTrue(
            (ROOT / "skills/modellix-ffmpeg/SKILL.md").is_file()
        )
        self.assertEqual(
            read_json("skills/modellix-ffmpeg/skill.json")["name"],
            "modellix-ffmpeg",
        )
        self.assertTrue((ROOT / "skills/modellix-moviepy/SKILL.md").is_file())
        self.assertEqual(
            read_json("skills/modellix-moviepy/skill.json")["name"],
            "modellix-moviepy",
        )
        self.assertTrue(
            (ROOT / "skills/modellix-image-prompt-engineering/SKILL.md").is_file()
        )
        self.assertEqual(
            read_json("skills/modellix-image-prompt-engineering/skill.json")["name"],
            "modellix-image-prompt-engineering",
        )
        self.assertTrue((ROOT / "skills/modellix-social-card/SKILL.md").is_file())
        self.assertEqual(
            read_json("skills/modellix-social-card/skill.json")["name"],
            "modellix-social-card",
        )
        self.assertTrue((ROOT / "skills/modellix-infographic/SKILL.md").is_file())
        self.assertEqual(
            read_json("skills/modellix-infographic/skill.json")["name"],
            "modellix-infographic",
        )
        self.assertTrue((ROOT / "skills/modellix-ecomm-ugc-video/SKILL.md").is_file())
        self.assertEqual(
            read_json("skills/modellix-ecomm-ugc-video/skill.json")["name"],
            "modellix-ecomm-ugc-video",
        )
        self.assertTrue((ROOT / "skills/modellix-cover-image/SKILL.md").is_file())
        self.assertEqual(
            read_json("skills/modellix-cover-image/skill.json")["name"],
            "modellix-cover-image",
        )
        self.assertTrue((ROOT / "skills/modellix-comic/SKILL.md").is_file())
        self.assertEqual(
            read_json("skills/modellix-comic/skill.json")["name"],
            "modellix-comic",
        )
        self.assertTrue((ROOT / "skills/modellix-article-illustrator/SKILL.md").is_file())
        self.assertEqual(
            read_json("skills/modellix-article-illustrator/skill.json")["name"],
            "modellix-article-illustrator",
        )

    def test_mcp_servers_are_named_and_unauthenticated(self):
        expected = {
            "Modellix Docs Search": "https://docs.modellix.ai/mcp",
            "Modellix Media Generation": "https://tool.modellix.ai/mcp/media",
            "Modellix Web Tools": "https://tool.modellix.ai/mcp",
        }
        for path, transport in (("mcp.json", "streamable-http"), (".mcp.json", "http")):
            mcp = read_json(path)
            servers = mcp["mcpServers"]
            with self.subTest(path=path):
                self.assertEqual(set(servers), set(expected))
                self.assertNotIn("modellix-docs", servers)
                blob = json.dumps(mcp)
                self.assertNotIn("Authorization", blob)
                self.assertNotIn("X-Mdlx-User-Id", blob)
                for name, url in expected.items():
                    self.assertEqual(servers[name]["type"], transport)
                    self.assertEqual(servers[name]["url"], url)
                    self.assertNotIn("headers", servers[name])

    def test_agent_skill_frontmatter_uses_standard_fields(self):
        skill_dirs = sorted(path.parent for path in (ROOT / "skills").glob("*/SKILL.md"))
        self.assertEqual(
            {path.name for path in skill_dirs},
            {
                "modellix-design",
                "modellix-image-prompt-engineering",
                "modellix-ffmpeg",
                "modellix-moviepy",
                "modellix-social-card",
                "modellix-infographic",
                "modellix-ecomm-ugc-video",
                "modellix-cover-image",
                "modellix-comic",
                "modellix-article-illustrator",
            },
        )
        for skill_dir in skill_dirs:
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            frontmatter = text.split("---", 2)[1]
            top_level = {
                line.split(":", 1)[0]
                for line in frontmatter.splitlines()
                if line and not line[0].isspace()
            }
            with self.subTest(skill=skill_dir.name):
                self.assertEqual(
                    top_level,
                    {"name", "description", "license", "compatibility", "metadata"},
                )
                self.assertRegex(
                    frontmatter, rf"(?m)^name:\s*{re.escape(skill_dir.name)}\s*$"
                )
                metadata_lines = [
                    line.strip()
                    for line in frontmatter.splitlines()
                    if line.startswith("  ") and not line.startswith("    ")
                ]
                self.assertTrue(metadata_lines)
                self.assertTrue(all(": " in line for line in metadata_lines))

    def test_prompt_skill_is_prompt_only_and_credential_free(self):
        skill_dir = ROOT / "skills/modellix-image-prompt-engineering"
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        metadata = read_json("skills/modellix-image-prompt-engineering/skill.json")
        self.assertNotIn("modellix-cli", text)
        self.assertNotIn("MODELLIX_API_KEY", text)
        self.assertTrue(
            {"primaryCredential", "primaryEnv", "requiredEnv", "env"}.isdisjoint(metadata)
        )
        self.assertIn("modellix-design", text)
        self.assertIn("Do not recommend a model", text)
        self.assertNotIn("google/nano-banana-2-lite", text)
        self.assertNotIn("google/nano-banana-2-lite-edit", text)

    def test_social_card_skill_is_prompt_only_and_credential_free(self):
        text = (ROOT / "skills/modellix-social-card/SKILL.md").read_text(encoding="utf-8")
        metadata = read_json("skills/modellix-social-card/skill.json")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertTrue(
            {"primaryCredential", "primaryEnv", "requiredEnv", "env"}.isdisjoint(metadata)
        )
        self.assertNotIn("MODELLIX_API_KEY", text)
        self.assertNotIn("modellix-cli", text)
        self.assertIn("Do not recommend a model", text)
        self.assertIn("modellix-design", text)

    def test_infographic_skill_is_prompt_only_and_credential_free(self):
        text = (ROOT / "skills/modellix-infographic/SKILL.md").read_text(encoding="utf-8")
        metadata = read_json("skills/modellix-infographic/skill.json")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertTrue(
            {"primaryCredential", "primaryEnv", "requiredEnv", "env"}.isdisjoint(metadata)
        )
        self.assertNotIn("MODELLIX_API_KEY", text)
        self.assertNotIn("modellix-cli", text)
        self.assertIn("Do not recommend a model", text)
        self.assertIn("modellix-design", text)

    def test_ecomm_ugc_video_skill_is_prompt_only_and_credential_free(self):
        text = (ROOT / "skills/modellix-ecomm-ugc-video/SKILL.md").read_text(encoding="utf-8")
        metadata = read_json("skills/modellix-ecomm-ugc-video/skill.json")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertTrue(
            {"primaryCredential", "primaryEnv", "requiredEnv", "env"}.isdisjoint(metadata)
        )
        self.assertNotIn("MODELLIX_API_KEY", text)
        self.assertNotIn("modellix-cli", text)
        self.assertIn("Do not recommend a model", text)
        self.assertIn("modellix-design", text)
        self.assertIn("modellix-ffmpeg", text)

    def test_cover_image_skill_is_prompt_only_and_credential_free(self):
        text = (ROOT / "skills/modellix-cover-image/SKILL.md").read_text(encoding="utf-8")
        metadata = read_json("skills/modellix-cover-image/skill.json")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertTrue(
            {"primaryCredential", "primaryEnv", "requiredEnv", "env"}.isdisjoint(metadata)
        )
        self.assertNotIn("MODELLIX_API_KEY", text)
        self.assertNotIn("modellix-cli", text)
        self.assertIn("Do not recommend a model", text)
        self.assertIn("modellix-design", text)

    def test_comic_skill_is_prompt_only_and_credential_free(self):
        text = (ROOT / "skills/modellix-comic/SKILL.md").read_text(encoding="utf-8")
        metadata = read_json("skills/modellix-comic/skill.json")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertTrue(
            {"primaryCredential", "primaryEnv", "requiredEnv", "env"}.isdisjoint(metadata)
        )
        self.assertNotIn("MODELLIX_API_KEY", text)
        self.assertNotIn("modellix-cli", text)
        self.assertIn("Do not recommend a model", text)
        self.assertIn("modellix-design", text)

    def test_article_illustrator_skill_is_prompt_only_and_credential_free(self):
        text = (ROOT / "skills/modellix-article-illustrator/SKILL.md").read_text(encoding="utf-8")
        metadata = read_json("skills/modellix-article-illustrator/skill.json")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertTrue(
            {"primaryCredential", "primaryEnv", "requiredEnv", "env"}.isdisjoint(metadata)
        )
        self.assertNotIn("MODELLIX_API_KEY", text)
        self.assertNotIn("modellix-cli", text)
        self.assertIn("Do not recommend a model", text)
        self.assertIn("modellix-design", text)

    def test_ffmpeg_skill_is_local_and_credential_free(self):
        text = (ROOT / "skills/modellix-ffmpeg/SKILL.md").read_text(encoding="utf-8")
        metadata = read_json("skills/modellix-ffmpeg/skill.json")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertTrue(
            {"primaryCredential", "primaryEnv", "requiredEnv", "env"}.isdisjoint(metadata)
        )
        self.assertNotIn("MODELLIX_API_KEY", text)
        self.assertNotIn("modellix-cli", text)
        self.assertIn("check_ffmpeg.py --json", text)
        self.assertIn("wait", text)
        self.assertIn("modellix-design", text)
        self.assertIn("modellix-moviepy", text)

    def test_moviepy_skill_is_local_and_credential_free(self):
        text = (ROOT / "skills/modellix-moviepy/SKILL.md").read_text(encoding="utf-8")
        metadata = read_json("skills/modellix-moviepy/skill.json")
        self.assertEqual(metadata["version"], "1.0.0")
        self.assertTrue(
            {"primaryCredential", "primaryEnv", "requiredEnv", "env"}.isdisjoint(metadata)
        )
        self.assertNotIn("MODELLIX_API_KEY", text)
        self.assertNotIn("modellix-cli", text)
        self.assertIn("check_moviepy.py --json", text)
        self.assertIn("wait", text)
        self.assertIn("modellix-design", text)
        self.assertIn("modellix-ffmpeg", text)
        self.assertIn("TextClip", text)

    def test_host_skill_symlinks_target_canonical_trees(self):
        for host in (".opencode", ".pi"):
            for skill_name in (
                "modellix-design",
                "modellix-image-prompt-engineering",
                "modellix-ffmpeg",
                "modellix-moviepy",
                "modellix-social-card",
                "modellix-infographic",
                "modellix-ecomm-ugc-video",
                "modellix-cover-image",
                "modellix-comic",
                "modellix-article-illustrator",
            ):
                path = ROOT / host / "skills" / skill_name
                with self.subTest(host=host, skill=skill_name):
                    if os.name == "nt" and not path.is_symlink():
                        # Git for Windows can materialize mode-120000 entries as
                        # link text when the account cannot create symlinks.
                        relative = path.relative_to(ROOT).as_posix()
                        indexed = subprocess.check_output(["git", "ls-files", "--stage", "--", relative], cwd=ROOT, text=True)
                        self.assertTrue(indexed.startswith("120000 "))
                        self.assertEqual(path.read_text(encoding="utf-8").strip(), f"../../skills/{skill_name}")
                        continue
                    self.assertTrue(path.is_symlink())
                    self.assertEqual(path.resolve(), (ROOT / "skills" / skill_name).resolve())

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
            "audio", "article-illustrator", "comic", "cover-image", "doctor", "download", "ecomm-ugc-video", "image", "infographic", "models", "prompt", "social-card", "tasks", "video"
        })
        for path in command_paths:
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            frontmatter = text.split("---", 2)[1]
            self.assertIn("description:", frontmatter)
            if path.stem in {"audio", "article-illustrator", "comic", "cover-image", "ecomm-ugc-video", "image", "infographic", "prompt", "social-card", "video"}:
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

    def test_skill_documents_model_get_schema(self):
        skill = (ROOT / "skills/modellix-design/SKILL.md").read_text(encoding="utf-8")
        playbook = (ROOT / "skills/modellix-design/references/cli-playbook.md").read_text(
            encoding="utf-8"
        )
        models_command = (ROOT / "commands/models.md").read_text(encoding="utf-8")
        self.assertIn("model get-schema", skill)
        self.assertIn("model get-schema", playbook)
        self.assertIn("model get-schema", models_command)

    def test_task_result_schema_supports_cli_and_download(self):
        schema = read_json("skills/modellix-design/assets/output/task-result.schema.json")
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
