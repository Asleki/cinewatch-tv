#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tomllib
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("NEXVOX_ENGINEERING_OUT", str(ROOT / "nexvox" / "engineering"))).resolve()
GENERATOR_VERSION = "1.0.0"
SCHEMA_VERSION = "1.0"

GENERATED_PREFIXES = (
    "nexvox/engineering/datasets/",
    "nexvox/engineering/manifests/",
    "nexvox/engineering/narratives/",
)
GENERATED_EXACT = {
    "nexvox/engineering/DATASET_CARD.md",
    "nexvox/engineering/checksums.sha256",
}

REFERENCE_ONLY_EXACT = {
    "package-lock.json",
    "apps/web/next-env.d.ts",
    "packages/contracts/src/generated/openapi.d.ts",
    "packages/contracts/openapi/cinewatch-v1.openapi.json",
    "docs/progress/CineWatch_TV_Engineering_Chronicle.md",
    "docs/progress/dashboard/progress-data.json",
    "docs/blueprints/CineWatch_Tv_V1_Blueprint_001.pdf",
}
REVIEW_REQUIRED_EXACT = {
    "docs/governance/CineWatch_TV_V1_API_Content_Rights_Qualification_Register_001.md",
    "docs/architecture/CineWatch_TV_V1_Competitive_Design_Intelligence_001.md",
}

TEXT_SUFFIXES = {
    ".md", ".py", ".ts", ".tsx", ".js", ".json", ".jsonl", ".css", ".html",
    ".toml", ".yml", ".yaml", ".sh", ".sql", ".txt", ".example", ".nvmrc", ".mjs", ".ini", ".mako",
    ".npmrc", ".editorconfig", ".gitattributes", ".gitignore",
}

@dataclass(frozen=True)
class FileEntry:
    path: str
    mode: str
    blob_sha: str
    size: int


def run_git(*args: str, text: bool = True, check: bool = True) -> str | bytes:
    cp = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )
    return cp.stdout


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def classify(path: str) -> tuple[str, str]:
    if path in REVIEW_REQUIRED_EXACT:
        return "TRAINING_REVIEW_REQUIRED", "contains external/provider research or rights evidence requiring record-level review"
    if path in REFERENCE_ONLY_EXACT or path.endswith("/.gitkeep") or path.endswith(".gitkeep"):
        return "REFERENCE_ONLY", "canonical/reference/generated artifact retained for provenance but excluded from training text"
    if path.startswith(GENERATED_PREFIXES) or path in GENERATED_EXACT:
        return "REFERENCE_ONLY", "NexVox generated projection excluded to prevent recursive training duplication"
    return "TRAINING_ELIGIBLE", "CineWatch-owned source, test, governance, or engineering documentation"


def authority_domain(path: str) -> str:
    if path == "CINEWATCH_ENGINEERING_WORKFLOW.md":
        return "engineering_workflow"
    if path.startswith("docs/blueprints/"):
        return "product_blueprint"
    if path.startswith("docs/governance/"):
        return "governance"
    if path.startswith("docs/architecture/decisions/"):
        return "architecture_decision"
    if path.startswith("docs/architecture/"):
        return "architecture"
    if path.startswith("docs/progress/activity/"):
        return "engineering_history"
    if path.startswith("docs/progress/"):
        return "engineering_projection"
    if path.startswith("services/api/database/migrations/") or path.endswith(".sql"):
        return "database_migration"
    if path.startswith("services/api/"):
        return "backend"
    if path.startswith("apps/web/"):
        return "frontend"
    if path.startswith("packages/contracts/"):
        return "contracts"
    if path.startswith("tests/"):
        return "tests"
    if path.startswith("scripts/"):
        return "engineering_tooling"
    if path.startswith(".github/"):
        return "ci_supply_chain"
    if path.startswith("nexvox/engineering/authority/"):
        return "nexvox_authority"
    if path.startswith("nexvox/engineering/policy/"):
        return "nexvox_policy"
    if path.startswith("nexvox/engineering/schemas/"):
        return "nexvox_schema"
    return "repository_foundation"


def source_role(path: str) -> str:
    if path == "CINEWATCH_ENGINEERING_WORKFLOW.md":
        return "LOCKED_AUTHORITY"
    if path.startswith("docs/blueprints/") and path.endswith(".md"):
        return "APPROVED_BLUEPRINT"
    if path.startswith("docs/architecture/decisions/"):
        return "ADR"
    if path.startswith("docs/architecture/"):
        return "ARCHITECTURE_AUTHORITY"
    if path.startswith("docs/governance/"):
        return "GOVERNANCE_AUTHORITY"
    if path == "docs/progress/activity/engineering-events.jsonl":
        return "APPEND_ONLY_LEDGER"
    if path.startswith("docs/progress/"):
        return "GENERATED_PROJECTION"
    if path.startswith("tests/"):
        return "TEST"
    if path.startswith("scripts/"):
        return "ENGINEERING_TOOL"
    if path.endswith((".py", ".ts", ".tsx", ".js", ".css", ".html", ".sql", ".sh")):
        return "SOURCE_CODE"
    return "REPOSITORY_SOURCE"


def language(path: str) -> str:
    name = Path(path).name
    suffix = Path(path).suffix.lower()
    return {
        ".py": "Python", ".ts": "TypeScript", ".tsx": "TSX", ".js": "JavaScript",
        ".css": "CSS", ".html": "HTML", ".md": "Markdown", ".json": "JSON",
        ".jsonl": "JSONL", ".toml": "TOML", ".yml": "YAML", ".yaml": "YAML",
        ".sh": "Shell", ".sql": "SQL", ".mjs": "JavaScript", ".ini": "INI", ".mako": "Mako", ".pdf": "PDF", ".txt": "Text",
    }.get(suffix, "Config" if name.startswith(".") or suffix == "" else suffix.lstrip(".").upper())


def is_text_path(path: str) -> bool:
    if path.endswith(".pdf"):
        return False
    suffix = Path(path).suffix.lower()
    return suffix in TEXT_SUFFIXES or Path(path).name.startswith(".") or suffix == ""


def git_blob(commit: str, path: str) -> bytes:
    return run_git("show", f"{commit}:{path}", text=False)  # type: ignore[return-value]


def decode_text(data: bytes) -> str | None:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def list_tree(commit: str) -> list[FileEntry]:
    raw = run_git("ls-tree", "-r", "-l", commit)
    out: list[FileEntry] = []
    for line in str(raw).splitlines():
        m = re.match(r"^(\d+)\s+blob\s+([0-9a-f]{40})\s+(\d+)\t(.+)$", line)
        if not m:
            continue
        out.append(FileEntry(m.group(4), m.group(1), m.group(2), int(m.group(3))))
    return out


def commit_list(source_commit: str) -> list[str]:
    return [x for x in str(run_git("rev-list", "--reverse", source_commit)).splitlines() if x]


def commit_meta(commit: str) -> dict[str, str]:
    fmt = "%H%x1f%P%x1f%aI%x1f%cI%x1f%an%x1f%ae%x1f%s%x1f%B"
    parts = str(run_git("show", "-s", f"--format={fmt}", commit)).rstrip("\n").split("\x1f", 7)
    while len(parts) < 8:
        parts.append("")
    return {
        "commit": parts[0], "parents": parts[1], "author_at": parts[2], "committer_at": parts[3],
        "author_name": parts[4], "author_email": parts[5], "subject": parts[6], "body": parts[7].strip(),
    }


def commit_numstat(commit: str) -> list[dict[str, object]]:
    raw = str(run_git("show", "--format=", "--numstat", "--find-renames", commit))
    rows = []
    for line in raw.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        a, d, path = parts
        rows.append({"path": path, "additions": None if a == "-" else int(a), "deletions": None if d == "-" else int(d)})
    return rows


def changed_statuses(commit: str) -> list[tuple[str, str, str]]:
    # status, old_path, new_path
    raw = str(run_git("diff-tree", "--root", "--no-commit-id", "--name-status", "-r", "-M", commit))
    result = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            result.append((parts[0], parts[1], parts[1]))
        elif len(parts) >= 3:
            result.append((parts[0], parts[1], parts[2]))
    return result


def csv_write(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})


def yaml_quote(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def write_simple_yaml(path: Path, mapping: dict[str, object]) -> None:
    lines: list[str] = []
    for k, v in mapping.items():
        if isinstance(v, dict):
            lines.append(f"{k}:")
            for k2, v2 in v.items():
                lines.append(f"  {k2}: {yaml_quote(v2)}")
        elif isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {yaml_quote(item)}")
        else:
            lines.append(f"{k}: {yaml_quote(v)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_events(source_commit: str) -> list[dict]:
    path = "docs/progress/activity/engineering-events.jsonl"
    try:
        text = git_blob(source_commit, path).decode("utf-8")
    except Exception:
        return []
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def detect_symbols(path: str, text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if path.endswith(".py"):
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return rows
        class Visitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node: ast.FunctionDef):
                rows.append({"path": path, "symbol": node.name, "kind": "function", "line": node.lineno})
                self.generic_visit(node)
            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
                rows.append({"path": path, "symbol": node.name, "kind": "async_function", "line": node.lineno})
                self.generic_visit(node)
            def visit_ClassDef(self, node: ast.ClassDef):
                rows.append({"path": path, "symbol": node.name, "kind": "class", "line": node.lineno})
                self.generic_visit(node)
        Visitor().visit(tree)
    elif path.endswith((".ts", ".tsx", ".js")):
        patterns = [
            (r"(?m)^\s*export\s+(?:default\s+)?function\s+([A-Za-z_$][\w$]*)", "function"),
            (r"(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", "function"),
            (r"(?m)^\s*export\s+(?:default\s+)?class\s+([A-Za-z_$][\w$]*)", "class"),
            (r"(?m)^\s*(?:export\s+)?interface\s+([A-Za-z_$][\w$]*)", "interface"),
            (r"(?m)^\s*(?:export\s+)?type\s+([A-Za-z_$][\w$]*)\s*=", "type"),
            (r"(?m)^\s*export\s+const\s+([A-Za-z_$][\w$]*)\s*=", "const"),
        ]
        seen = set()
        for pattern, kind in patterns:
            for m in re.finditer(pattern, text):
                key = (m.group(1), kind, text.count("\n", 0, m.start()) + 1)
                if key in seen:
                    continue
                seen.add(key)
                rows.append({"path": path, "symbol": m.group(1), "kind": kind, "line": key[2]})
    return rows


def dependency_rows(source_commit: str, text_by_path: dict[str, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    # package manifests
    for path, text in text_by_path.items():
        if Path(path).name == "package.json":
            try:
                obj = json.loads(text)
            except json.JSONDecodeError:
                continue
            for section in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies", "overrides"):
                deps = obj.get(section, {})
                if isinstance(deps, dict):
                    for dep, spec in sorted(deps.items()):
                        rows.append({"source_path": path, "dependency": dep, "dependency_kind": f"npm_{section}", "specifier": spec, "line": ""})
        if path.endswith("pyproject.toml"):
            try:
                obj = tomllib.loads(text)
            except tomllib.TOMLDecodeError:
                continue
            project = obj.get("project", {})
            for dep in project.get("dependencies", []) or []:
                rows.append({"source_path": path, "dependency": dep, "dependency_kind": "python_runtime", "specifier": dep, "line": ""})
            for group, deps in (project.get("optional-dependencies", {}) or {}).items():
                for dep in deps:
                    rows.append({"source_path": path, "dependency": dep, "dependency_kind": f"python_optional:{group}", "specifier": dep, "line": ""})
    # code imports
    for path, text in text_by_path.items():
        if path.endswith(".py"):
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        rows.append({"source_path": path, "dependency": alias.name, "dependency_kind": "python_import", "specifier": "", "line": node.lineno})
                elif isinstance(node, ast.ImportFrom):
                    mod = ("." * node.level) + (node.module or "")
                    rows.append({"source_path": path, "dependency": mod, "dependency_kind": "python_import_from", "specifier": "", "line": node.lineno})
        elif path.endswith((".ts", ".tsx", ".js")):
            for m in re.finditer(r"(?m)^\s*(?:import|export)\b[^\n]*?\bfrom\s+[\"']([^\"']+)[\"']", text):
                rows.append({"source_path": path, "dependency": m.group(1), "dependency_kind": "js_import", "specifier": "", "line": text.count("\n", 0, m.start()) + 1})
            for m in re.finditer(r"(?m)^\s*import\s+[\"']([^\"']+)[\"']", text):
                rows.append({"source_path": path, "dependency": m.group(1), "dependency_kind": "js_side_effect_import", "specifier": "", "line": text.count("\n", 0, m.start()) + 1})
        if path.startswith(".github/workflows/"):
            for m in re.finditer(r"(?m)^\s*uses:\s*([^\s#]+)", text):
                rows.append({"source_path": path, "dependency": m.group(1), "dependency_kind": "github_action", "specifier": m.group(1), "line": text.count("\n", 0, m.start()) + 1})
    # deterministic dedupe
    uniq = {}
    for r in rows:
        key = tuple(str(r[k]) for k in ("source_path", "dependency", "dependency_kind", "specifier", "line"))
        uniq[key] = r
    return [uniq[k] for k in sorted(uniq)]


def read_existing_conversation_rows() -> list[dict[str, object]]:
    path = OUT / "datasets" / "conversation-sources.csv"
    if path.exists():
        with path.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    return []


def default_conversation_rows() -> list[dict[str, object]]:
    seeds = [
        ("CWTV-CONV-000001", "2026-09-10", "current_conversation", "tmux workflow", "The CineWatch tmux map is nine windows and 6:git is Version Control only; 8:chronicle owns engineering history and dashboard governance."),
        ("CWTV-CONV-000002", "2026-09-10", "current_conversation", "frontend styling", "CineWatch uses semantic HTML and native CSS as primary design authority; Tailwind is permitted selectively when justified."),
        ("CWTV-CONV-000003", "2026-09-10", "current_conversation", "CSS-exclusive pages", "Complex cinematic, editorial, screenplay, gallery, responsive, animation, or accessibility-sensitive surfaces may remain CSS-exclusive."),
        ("CWTV-CONV-000004", "2026-09-10", "current_conversation", "competitive design", "The design research direction benchmarks streaming, music, production/screenwriting, and entertainment editorial products without cloning them."),
        ("CWTV-CONV-000005", "2026-09-10", "current_conversation", "V1.3.1", "CWTV.V1.3.1 began as Design System Evidence and Competitive Intelligence before implementation changes."),
        ("CWTV-CONV-000006", "2026-09-10", "current_conversation", "whitespace correction", "A staged diff whitespace gate rejected trailing Markdown whitespace; the files were normalized, rehashed, correction events appended, then restaged and committed."),
        ("CWTV-CONV-000007", "2026-09-10", "current_conversation", "NexVox objective", "The user requested an engineering knowledge/training layer so NexVox can learn how CineWatch was built, including errors, corrections, decisions, commits, tests, and engineering methods."),
        ("CWTV-CONV-000008", "2026-09-10", "current_conversation", "NexVox formats", "Requested corpus representations include Markdown, YAML, CSV where appropriate, and a local-only PDF; JSONL was added for append-friendly machine records."),
        ("CWTV-CONV-000009", "2026-09-10", "current_conversation", "Git provenance", "A Git bundle was provided so the engineering corpus can audit complete reachable history rather than only the current source ZIP."),
        ("CWTV-CONV-000010", "2026-09-10", "current_conversation", "training eligibility", "Inspection of all source does not imply training permission for all source; external/provider material requires review and generated projections should be deduplicated."),
        ("CWTV-CONV-000011", "2026-09-10", "current_conversation", "per-commit sync", "A normal engineering commit should be followed by a NexVox projection commit that records the exact source commit; projection commits do not recursively trigger another projection."),
        ("CWTV-CONV-000012", "2026-09-10", "current_conversation", "audit permission", "The user explicitly authorized completion of the NexVox Engineering Knowledge Authority, policy/schema, and measured datasets before resuming CWTV.V1.3.1 design work."),
    ]
    return [
        {
            "source_id": sid,
            "date": date,
            "source_kind": kind,
            "topic": topic,
            "availability": "retrieved_conversation_context",
            "verbatim": "false",
            "transformation": "normalized_engineering_fact",
            "human_validation": "pending",
            "training_eligibility": "TRAINING_REVIEW_REQUIRED",
            "summary": summary,
        }
        for sid, date, kind, topic, summary in seeds
    ]


def chunk_text(text: str, max_chars: int = 6000, max_lines: int = 80) -> list[tuple[int, int, str]]:
    lines = text.splitlines()
    chunks = []
    start = 0
    while start < len(lines):
        end = min(start + max_lines, len(lines))
        while end > start + 1 and len("\n".join(lines[start:end])) > max_chars:
            end -= 1
        if end == start:
            end = start + 1
        content = "\n".join(lines[start:end]).strip("\n")
        if content.strip():
            chunks.append((start + 1, end, content))
        start = end
    return chunks


def build(source_commit: str) -> dict[str, int]:
    source_commit = str(run_git("rev-parse", source_commit)).strip()
    commits = commit_list(source_commit)
    source_meta = commit_meta(source_commit)
    tree = list_tree(source_commit)

    OUT.mkdir(parents=True, exist_ok=True)
    datasets = OUT / "datasets"
    manifests = OUT / "manifests"
    narratives = OUT / "narratives"
    for d in (datasets, manifests, narratives):
        d.mkdir(parents=True, exist_ok=True)

    text_by_path: dict[str, str] = {}
    file_rows = []
    class_counts = Counter()
    class_bytes = Counter()
    lang_counts = Counter()
    current_lines = 0
    for entry in tree:
        data = git_blob(source_commit, entry.path)
        text = decode_text(data) if is_text_path(entry.path) else None
        lines = 0 if text is None else len(text.splitlines())
        if text is not None:
            text_by_path[entry.path] = text
            current_lines += lines
        elig, reason = classify(entry.path)
        class_counts[elig] += 1
        class_bytes[elig] += entry.size
        lang_counts[language(entry.path)] += 1
        file_rows.append({
            "path": entry.path,
            "mode": entry.mode,
            "blob_sha": entry.blob_sha,
            "sha256": sha256_bytes(data),
            "bytes": entry.size,
            "line_count": lines if text is not None else "",
            "language": language(entry.path),
            "authority_domain": authority_domain(entry.path),
            "source_role": source_role(entry.path),
            "training_eligibility": elig,
            "eligibility_reason": reason,
            "generated_projection": str(entry.path.startswith(GENERATED_PREFIXES) or entry.path in GENERATED_EXACT).lower(),
        })
    csv_write(datasets / "repository-files.csv", list(file_rows[0].keys()) if file_rows else [], file_rows)

    commit_rows = []
    commit_change_rows = []
    file_version_rows = []
    change_seq = 0
    version_seq = 0
    for idx, commit in enumerate(commits, start=1):
        meta = commit_meta(commit)
        numstats = {r["path"]: r for r in commit_numstat(commit)}
        statuses = changed_statuses(commit)
        total_add = sum((r["additions"] or 0) for r in numstats.values())
        total_del = sum((r["deletions"] or 0) for r in numstats.values())
        body = meta["body"]
        projection = bool(re.search(r"(?mi)^NexVox-Projection:\s*true\s*$", body))
        msrc = re.search(r"(?mi)^NexVox-Source-Commit:\s*([0-9a-f]{40})\s*$", body)
        commit_rows.append({
            "sequence": idx,
            "commit": commit,
            "parents": meta["parents"],
            "author_at": meta["author_at"],
            "committer_at": meta["committer_at"],
            "author_name": meta["author_name"],
            "subject": meta["subject"],
            "files_changed": len(statuses),
            "additions": total_add,
            "deletions": total_del,
            "is_nexvox_projection": str(projection).lower(),
            "nexvox_source_commit": msrc.group(1) if msrc else "",
        })
        for status, old_path, new_path in statuses:
            change_seq += 1
            stat = numstats.get(new_path) or numstats.get(old_path) or {}
            path = new_path
            elig, reason = classify(path)
            blob_sha = ""
            sha = ""
            size: object = ""
            lines: object = ""
            if not status.startswith("D"):
                try:
                    ls = str(run_git("ls-tree", "-l", commit, "--", path)).strip()
                    mm = re.match(r"^(\d+)\s+blob\s+([0-9a-f]{40})\s+(\d+)\t", ls)
                    if mm:
                        blob_sha = mm.group(2)
                        size = int(mm.group(3))
                        data = git_blob(commit, path)
                        sha = sha256_bytes(data)
                        txt = decode_text(data) if is_text_path(path) else None
                        lines = len(txt.splitlines()) if txt is not None else ""
                except subprocess.CalledProcessError:
                    pass
            commit_change_rows.append({
                "change_id": f"CWTV-GITCHG-{change_seq:06d}",
                "commit": commit,
                "status": status,
                "old_path": old_path if old_path != new_path else "",
                "path": new_path,
                "additions": stat.get("additions", ""),
                "deletions": stat.get("deletions", ""),
                "training_eligibility": elig,
            })
            version_seq += 1
            file_version_rows.append({
                "version_id": f"CWTV-FVER-{version_seq:06d}",
                "commit": commit,
                "commit_sequence": idx,
                "status": status,
                "path": path,
                "blob_sha": blob_sha,
                "sha256": sha,
                "bytes": size,
                "line_count": lines,
                "training_eligibility": elig,
                "eligibility_reason": reason,
            })
    csv_write(datasets / "commits.csv", list(commit_rows[0].keys()), commit_rows)
    csv_write(datasets / "commit-changes.csv", list(commit_change_rows[0].keys()), commit_change_rows)
    csv_write(datasets / "repository-file-versions.csv", list(file_version_rows[0].keys()), file_version_rows)

    symbol_rows = []
    sym_id = 0
    for path in sorted(text_by_path):
        for row in detect_symbols(path, text_by_path[path]):
            sym_id += 1
            elig, _ = classify(path)
            row = {"symbol_id": f"CWTV-SYM-{sym_id:06d}", **row, "training_eligibility": elig}
            symbol_rows.append(row)
    csv_write(datasets / "symbols.csv", ["symbol_id", "path", "symbol", "kind", "line", "training_eligibility"], symbol_rows)

    deps = dependency_rows(source_commit, text_by_path)
    dep_rows = []
    for i, r in enumerate(deps, start=1):
        dep_rows.append({"dependency_id": f"CWTV-DEP-{i:06d}", **r})
    csv_write(datasets / "dependencies.csv", ["dependency_id", "source_path", "dependency", "dependency_kind", "specifier", "line"], dep_rows)

    events = parse_events(source_commit)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for ev in events:
        grouped[ev.get("milestone", "")].append(ev)
    milestone_rows = []
    for milestone in sorted(grouped, key=lambda x: [int(y) if y.isdigit() else y for y in re.split(r"(\d+)", x)]):
        evs = grouped[milestone]
        started = next((e for e in evs if e.get("event_type") == "MILESTONE_STARTED"), None)
        qualified = next((e for e in reversed(evs) if e.get("event_type") == "MILESTONE_QUALIFIED" or e.get("result") == "QUALIFIED"), None)
        milestone_rows.append({
            "milestone": milestone,
            "event_count": len(evs),
            "started_event": started.get("event_id", "") if started else "",
            "started_at": started.get("occurred_at", "") if started else "",
            "latest_event": evs[-1].get("event_id", ""),
            "latest_event_type": evs[-1].get("event_type", ""),
            "qualified": str(bool(qualified)).lower(),
            "qualified_event": qualified.get("event_id", "") if qualified else "",
            "failed_events": sum(1 for e in evs if e.get("result") == "FAILED"),
            "correction_events": sum(1 for e in evs if "CORRECTION" in str(e.get("event_type", ""))),
            "duration_seconds_sum": sum(int(e.get("duration_seconds") or 0) for e in evs),
        })
    csv_write(datasets / "milestones.csv", list(milestone_rows[0].keys()) if milestone_rows else [], milestone_rows)

    artifact_rows = []
    for ev in events:
        art = ev.get("artifact")
        if art:
            artifact_rows.append({
                "event_id": ev.get("event_id", ""), "sequence": ev.get("sequence", ""), "milestone": ev.get("milestone", ""),
                "event_type": ev.get("event_type", ""), "artifact_name": art.get("name", ""), "artifact_sha256": art.get("sha256", ""),
                "occurred_at": ev.get("occurred_at", ""), "result": ev.get("result", ""), "summary": ev.get("summary", ""),
            })
    csv_write(datasets / "artifacts.csv", ["event_id", "sequence", "milestone", "event_type", "artifact_name", "artifact_sha256", "occurred_at", "result", "summary"], artifact_rows)

    # Failure/correction chains: preserve both explicit corrections and pass-based resolution.
    fc_rows = []
    chain_id = 0
    paired_corrections = set()
    for i, ev in enumerate(events):
        failure_type = str(ev.get("event_type", ""))
        if ev.get("result") != "FAILED" and "FAILED" not in failure_type:
            continue
        milestone = ev.get("milestone", "")
        wanted_correction = ev.get("correction")
        matching_pass_type = failure_type.replace("_FAILED", "_PASSED") if failure_type.endswith("_FAILED") else ""
        correction = None
        resolution = None
        for nxt in events[i + 1:]:
            if nxt.get("milestone") != milestone:
                continue
            nxt_type = str(nxt.get("event_type", ""))
            if matching_pass_type and nxt_type == matching_pass_type and nxt.get("result") != "FAILED":
                resolution = nxt
                break
            is_applied = nxt_type in {"CORRECTION_APPLIED", "CORRECTION_GENERATED"}
            if is_applied:
                if wanted_correction and nxt.get("correction") != wanted_correction:
                    continue
                correction = nxt
                paired_corrections.add(nxt.get("event_id"))
                # Explicit correction is the resolution mechanism; a later pass remains available in qualifications.csv.
                break
            if nxt_type == "MILESTONE_QUALIFIED" or nxt.get("result") == "QUALIFIED":
                break
        chain_id += 1
        fc_rows.append({
            "chain_id": f"CWTV-FC-{chain_id:05d}",
            "milestone": milestone,
            "failure_event": ev.get("event_id", ""),
            "failure_type": failure_type,
            "failure_summary": ev.get("summary", ""),
            "correction_event": correction.get("event_id", "") if correction else "",
            "correction_id": correction.get("correction", "") if correction else "",
            "correction_summary": correction.get("summary", "") if correction else "",
            "resolution_event": resolution.get("event_id", "") if resolution else (correction.get("event_id", "") if correction else ""),
            "resolution_type": resolution.get("event_type", "") if resolution else (correction.get("event_type", "") if correction else ""),
            "resolution_summary": resolution.get("summary", "") if resolution else (correction.get("summary", "") if correction else ""),
            "chain_state": "CORRECTED" if correction else ("RESOLVED_BY_PASS" if resolution else "UNPAIRED_FAILURE"),
        })
    # Preserve applied/generated corrections that have no FAILED ledger event paired to them.
    for ev in events:
        if ev.get("event_type") in {"CORRECTION_APPLIED", "CORRECTION_GENERATED"} and ev.get("event_id") not in paired_corrections:
            chain_id += 1
            fc_rows.append({
                "chain_id": f"CWTV-FC-{chain_id:05d}", "milestone": ev.get("milestone", ""), "failure_event": "",
                "failure_type": "", "failure_summary": "", "correction_event": ev.get("event_id", ""), "correction_id": ev.get("correction", ""),
                "correction_summary": ev.get("summary", ""), "resolution_event": ev.get("event_id", ""), "resolution_type": ev.get("event_type", ""),
                "resolution_summary": ev.get("summary", ""), "chain_state": "CORRECTION_WITHOUT_LEDGER_FAILURE",
            })
    csv_write(datasets / "failure-correction-chains.csv", ["chain_id", "milestone", "failure_event", "failure_type", "failure_summary", "correction_event", "correction_id", "correction_summary", "resolution_event", "resolution_type", "resolution_summary", "chain_state"], fc_rows)

    qual_rows = []
    for ev in events:
        et = str(ev.get("event_type", ""))
        if "QUALIFICATION" in et or et == "MILESTONE_QUALIFIED" or ev.get("result") == "QUALIFIED":
            qual_rows.append({
                "event_id": ev.get("event_id", ""), "sequence": ev.get("sequence", ""), "milestone": ev.get("milestone", ""),
                "event_type": et, "result": ev.get("result", ""), "occurred_at": ev.get("occurred_at", ""),
                "commit": ev.get("commit", ""), "summary": ev.get("summary", ""),
            })
    csv_write(datasets / "qualifications.csv", ["event_id", "sequence", "milestone", "event_type", "result", "occurred_at", "commit", "summary"], qual_rows)

    decision_rows = []
    adr_paths = sorted(p for p in text_by_path if p.startswith("docs/architecture/decisions/") and p.endswith(".md"))
    for idx, path in enumerate(adr_paths, start=1):
        text = text_by_path[path]
        title_m = re.search(r"(?m)^#\s+(.+)$", text)
        status_m = re.search(r"(?mi)^\*\*Status:\*\*\s*`?([^`\n]+)`?", text)
        dec_m = re.search(r"(?ms)^##\s+(?:Decision|Architecture decision)\s*$\n(.*?)(?=^##\s|\Z)", text)
        decision = re.sub(r"\s+", " ", dec_m.group(1).strip()) if dec_m else ""
        decision_rows.append({
            "decision_id": f"CWTV-ADR-{idx:04d}", "path": path, "title": title_m.group(1).strip() if title_m else Path(path).stem,
            "status": status_m.group(1).strip() if status_m else "", "decision_summary": decision[:1200],
            "source_commit": source_commit, "training_eligibility": classify(path)[0],
        })
    csv_write(datasets / "decisions.csv", ["decision_id", "path", "title", "status", "decision_summary", "source_commit", "training_eligibility"], decision_rows)

    conv_rows = read_existing_conversation_rows() or default_conversation_rows()
    csv_write(datasets / "conversation-sources.csv", ["source_id", "date", "source_kind", "topic", "availability", "verbatim", "transformation", "human_validation", "training_eligibility", "summary"], conv_rows)

    # Reconciliations: explicit evidence hierarchy findings.
    recon_rows = []
    def add_recon(kind: str, primary: str, conflicting: str, resolution: str, evidence: str):
        recon_rows.append({"reconciliation_id": f"CWTV-RECON-{len(recon_rows)+1:04d}", "kind": kind, "primary_source": primary, "secondary_or_conflicting_source": conflicting, "resolution": resolution, "evidence": evidence})
    readme = text_by_path.get("README.md", "")
    latest_milestone = events[-1].get("milestone", "") if events else ""
    m = re.search(r"Current milestone[^\n]*?`([^`]+)`", readme, re.I)
    if m and latest_milestone and m.group(1) != latest_milestone:
        add_recon("STALE_STATUS", "docs/progress/activity/engineering-events.jsonl", "README.md", f"Use ledger-derived active milestone {latest_milestone}; treat README value {m.group(1)} as stale descriptive text.", "latest append-only ledger event versus README current milestone")
    add_recon("GENERATED_DUPLICATION", "docs/progress/activity/engineering-events.jsonl", "docs/progress/CineWatch_TV_Engineering_Chronicle.md", "Ledger is canonical; Markdown Chronicle is a generated human projection and should not be duplicated in training chunks.", "repository chronicle generator architecture")
    add_recon("GENERATED_DUPLICATION", "docs/progress/activity/engineering-events.jsonl", "docs/progress/dashboard/progress-data.json", "Ledger is canonical; dashboard data is a generated projection.", "repository dashboard generator architecture")
    add_recon("GENERATED_CONTRACT", "backend FastAPI/Pydantic authority", "packages/contracts/openapi/cinewatch-v1.openapi.json", "Treat OpenAPI as governed projection and generated TypeScript declarations as downstream reference; do not weight all three equally.", "contract generation pipeline")
    add_recon("SIGNED_ATTESTATION", "docs/blueprints/CineWatch_Tv_V1_Blueprint_001.md", "docs/blueprints/CineWatch_Tv_V1_Blueprint_001.pdf", "Use Markdown for searchable substantive authority and PDF/hash as immutable signed attestation; preserve both provenance roles.", "signed blueprint governance")
    ledger_commits = {e.get("commit") for e in events if e.get("commit")}
    add_recon("PARTIAL_COVERAGE", "Git commit graph", "engineering-events.jsonl commit fields", f"Git proves {len(commits)} reachable commits while ledger directly references {len(ledger_commits)} unique commit SHAs; join both sources rather than treating ledger commit references as exhaustive Git history.", "bundle-complete Git graph versus event ledger")
    if any(e.get("event_id") in {"CWTV-EVT-000128", "CWTV-EVT-000129"} for e in events):
        add_recon("CONVERSATION_ONLY_FAILURE", "conversation/terminal evidence", "engineering-events.jsonl", "Preserve that the staged whitespace gate failed as conversation-derived evidence; do not invent a missing FAILED ledger event. Ledger records only the later correction events.", "CWTV-EVT-000128 and CWTV-EVT-000129")
    qualified_milestones = {r["milestone"] for r in milestone_rows if r["qualified"] == "true"}
    stale_arch_status = []
    for apath, atext in text_by_path.items():
        if not apath.startswith("docs/architecture/") or "/decisions/" in apath:
            continue
        mm = re.search(r"(?mi)^\*\*Milestone:\*\*\s*`?([^`\n]+)`?", atext)
        sm = re.search(r"(?mi)^\*\*Status:\*\*\s*`?([^`\n]+)`?", atext)
        if mm and sm and mm.group(1).strip() in qualified_milestones and "CANDIDATE" in sm.group(1).upper():
            stale_arch_status.append(f"{apath} ({sm.group(1).strip()})")
    if stale_arch_status:
        add_recon("STALE_DOCUMENT_STATUS", "docs/progress/activity/engineering-events.jsonl", "qualified architecture document headers", "Treat candidate-status headers as historical document text when the append-only ledger later proves the owning milestone qualified; do not rewrite signed/history evidence merely to make wording current.", "; ".join(stale_arch_status))
    add_recon("EXTERNAL_EVIDENCE", "CineWatch-owned conclusions", "provider/external research passages", "Keep externally sourced evidence review-required and extract CineWatch-owned decisions into separately attributable knowledge records.", "rights register and competitive design research")
    add_recon("LEGACY_PROVENANCE", "CineWatch V1 architecture", "legacy CineWatchStream", "Legacy product material is provenance/reference only unless explicitly reimplemented and qualified in V1.", "V1 design intelligence authority")
    add_recon("STATUS_VOCABULARY", "event_type plus result semantics", "individual historical event conventions", "Interpret event_type and result together; do not rewrite older valid event vocabulary to match newer conventions.", "append-only event schema and historical records")
    csv_write(datasets / "source-reconciliations.csv", ["reconciliation_id", "kind", "primary_source", "secondary_or_conflicting_source", "resolution", "evidence"], recon_rows)

    # Current knowledge chunks.
    knowledge_path = datasets / "knowledge-records.jsonl"
    knowledge_count = 0
    with knowledge_path.open("w", encoding="utf-8", newline="\n") as f:
        for path in sorted(text_by_path):
            elig, _ = classify(path)
            if elig == "REFERENCE_ONLY":
                continue
            text = text_by_path[path]
            for line_start, line_end, content in chunk_text(text):
                knowledge_count += 1
                rec = {
                    "schema_version": SCHEMA_VERSION,
                    "record_id": f"CWTV-KNOW-{knowledge_count:07d}",
                    "source_commit": source_commit,
                    "source_path": path,
                    "line_start": line_start,
                    "line_end": line_end,
                    "authority_domain": authority_domain(path),
                    "source_role": source_role(path),
                    "training_eligibility": elig,
                    "transformation": "line_chunk",
                    "content_sha256": sha256_text(content),
                    "content": content,
                }
                f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")

    # Historical patch records for every eligible/review changed file.
    history_path = datasets / "history-records.jsonl"
    history_count = 0
    with history_path.open("w", encoding="utf-8", newline="\n") as f:
        for idx, commit in enumerate(commits, start=1):
            meta = commit_meta(commit)
            parent = meta["parents"].split()[0] if meta["parents"] else ""
            for status, old_path, new_path in changed_statuses(commit):
                path = new_path
                elig, _ = classify(path)
                if elig == "REFERENCE_ONLY":
                    continue
                if parent:
                    patch = str(run_git("diff", "--no-ext-diff", "--unified=3", parent, commit, "--", path))
                else:
                    patch = str(run_git("show", "--format=", "--no-ext-diff", "--unified=3", commit, "--", path))
                if not patch.strip() and not status.startswith("D"):
                    data = git_blob(commit, path)
                    txt = decode_text(data)
                    patch = txt or ""
                history_count += 1
                rec = {
                    "schema_version": SCHEMA_VERSION,
                    "record_id": f"CWTV-HIST-{history_count:07d}",
                    "commit": commit,
                    "commit_sequence": idx,
                    "parent": parent or None,
                    "committer_at": meta["committer_at"],
                    "subject": meta["subject"],
                    "status": status,
                    "source_path": path,
                    "authority_domain": authority_domain(path),
                    "training_eligibility": elig,
                    "transformation": "git_patch",
                    "content_sha256": sha256_text(patch),
                    "content": patch,
                }
                f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")

    # Generated narratives.
    failures = [e for e in events if e.get("result") == "FAILED" or "FAILED" in str(e.get("event_type", ""))]
    correction_events = [e for e in events if e.get("event_type") in {"CORRECTION_GENERATED", "CORRECTION_APPLIED"}]
    correction_keys = {(e.get("milestone", ""), e.get("correction") or e.get("summary", "")) for e in correction_events}
    qualified = [r for r in milestone_rows if r["qualified"] == "true"]
    hist_lines = [
        "# CineWatch Engineering History", "", f"**Source commit:** `{source_commit}`", "",
        "This is a deterministic NexVox narrative projection. Git remains the canonical commit authority and `engineering-events.jsonl` remains the canonical engineering-activity ledger.", "",
        f"The source history contains **{len(commits)} reachable commits**, **{len(tree)} current tracked files**, and **{len(events)} engineering events**.", "",
        "## Commit sequence", "",
    ]
    for r in commit_rows:
        hist_lines.append(f"- `{str(r['commit'])[:7]}` - {r['subject']}")
    hist_lines += ["", "## Milestone state", ""]
    for r in milestone_rows:
        hist_lines.append(f"- `{r['milestone']}`: events={r['event_count']}, qualified={r['qualified']}, failures={r['failed_events']}, corrections={r['correction_events']}")
    (narratives / "engineering-history.md").write_text("\n".join(hist_lines) + "\n", encoding="utf-8")

    adr_lines = ["# CineWatch Architecture and Decisions", "", f"**Source commit:** `{source_commit}`", "", "This projection summarizes ADRs and architecture evidence; source documents remain authoritative.", ""]
    for r in decision_rows:
        adr_lines += [f"## {r['decision_id']} - {r['title']}", "", f"Source: `{r['path']}`", "", str(r['decision_summary']) or "Decision text is preserved in the source ADR.", ""]
    (narratives / "architecture-decisions.md").write_text("\n".join(adr_lines), encoding="utf-8")

    fc_lines = ["# CineWatch Failures, Corrections and Lessons", "", f"**Source commit:** `{source_commit}`", "", "Failures are preserved rather than rewritten away. A correction without a recorded FAILED ledger event remains explicitly marked as such.", ""]
    for r in fc_rows:
        fc_lines += [f"## {r['chain_id']} - {r['milestone']}", "", f"State: `{r['chain_state']}`", "", f"Failure: {r['failure_summary'] or 'No FAILED ledger event recorded.'}", "", f"Correction: {r['correction_summary'] or 'No paired correction recorded.'}", ""]
    (narratives / "failures-corrections-lessons.md").write_text("\n".join(fc_lines), encoding="utf-8")

    methods = f"""# CineWatch Engineering Methods\n\n**Source commit:** `{source_commit}`\n\n## Core method\n\nCineWatch engineering follows an inspect -> authority/scope -> smallest justified change -> focused validation -> broader qualification -> diff integrity -> Version Control -> remote CI -> chronicle/dashboard evidence path.\n\n## Evidence discipline\n\nGit is commit authority. The append-only engineering ledger is activity authority. Generated Chronicle/dashboard files are projections. Generated OpenAPI/type artifacts are downstream of canonical API authority. Unknown evidence is not upgraded by inference.\n\n## NexVox method\n\nNexVox records provenance and training eligibility for every source. Generated corpus files are excluded from recursive ingestion. A future projection commit must identify its exact source commit and must not recursively trigger another projection.\n"""
    (narratives / "engineering-methods.md").write_text(methods, encoding="utf-8")

    glossary = """# CineWatch Engineering Glossary\n\n- **Authority** - the source permitted to decide a fact within a defined domain.\n- **Projection** - deterministic human- or machine-readable output derived from a canonical source.\n- **Qualification** - evidence that a candidate passed the checks required for its scope.\n- **Chronicle** - generated Markdown view of the append-only engineering event ledger.\n- **Training eligible** - source content approved by policy for inclusion in a training/retrieval corpus.\n- **Training review required** - source content that must be reviewed at record level before training use.\n- **Reference only** - indexed for provenance but excluded from training text to avoid duplication, licensing risk, or generated noise.\n- **NexVox projection commit** - a commit whose purpose is to persist a corpus projection for an exact preceding source commit.\n- **Fail closed** - treat unknown permission as no permission until authority proves otherwise.\n- **Semantic HTML** - meaningful document structure rendered through React/Next.js rather than anonymous visual containers.\n- **CSS-first** - CineWatch design authority is expressed primarily through semantic HTML, design tokens, and native CSS; Tailwind remains optional.\n"""
    (narratives / "glossary.md").write_text(glossary, encoding="utf-8")

    # Dataset card and manifests.
    structured_files = sorted(p for p in datasets.iterdir() if p.is_file())
    dataset_card = f"""# CineWatch NexVox Engineering Dataset Card\n\n**Dataset ID:** `CWTV-NEXVOX-ENGINEERING-001`\n**Schema version:** `{SCHEMA_VERSION}`\n**Generator version:** `{GENERATOR_VERSION}`\n**Source commit:** `{source_commit}`\n**Source commit time:** `{source_meta['committer_at']}`\n**History complete to source commit:** `true`\n\n## Purpose\n\nTeach NexVox how CineWatch TV was engineered: architecture, implementation, commits, failures, corrections, tests, qualifications, design decisions, and engineering methods. This dataset is separate from future CineWatch user/search/recommendation training data.\n\n## Measured source\n\n- Reachable commits: **{len(commits)}**\n- Current tracked files: **{len(tree)}**\n- Current text lines: **{current_lines}**\n- Engineering events: **{len(events)}**\n- Qualified milestones: **{len(qualified)}**\n- Failed events: **{len(failures)}**\n- Recorded correction identities: **{len(correction_keys)}**\n- Symbols indexed: **{len(symbol_rows)}**\n- Dependencies/import edges indexed: **{len(dep_rows)}**\n- Current knowledge records: **{knowledge_count}**\n- Historical patch records: **{history_count}**\n\n## Current source classification\n\n- TRAINING_ELIGIBLE: **{class_counts['TRAINING_ELIGIBLE']} files / {class_bytes['TRAINING_ELIGIBLE']} bytes**\n- TRAINING_REVIEW_REQUIRED: **{class_counts['TRAINING_REVIEW_REQUIRED']} files / {class_bytes['TRAINING_REVIEW_REQUIRED']} bytes**\n- REFERENCE_ONLY: **{class_counts['REFERENCE_ONLY']} files / {class_bytes['REFERENCE_ONLY']} bytes**\n- TRAINING_PROHIBITED: **{class_counts['TRAINING_PROHIBITED']} files / {class_bytes['TRAINING_PROHIBITED']} bytes**\n\n## Training restriction\n\nInspection is not training permission. Records marked `TRAINING_REVIEW_REQUIRED`, `REFERENCE_ONLY`, or `TRAINING_PROHIBITED` must not be silently promoted into training data. Conversation summaries are transformed evidence and remain review-required until explicitly human-validated.\n"""
    (OUT / "DATASET_CARD.md").write_text(dataset_card, encoding="utf-8")

    dataset_sizes = {p.name: p.stat().st_size for p in structured_files}
    manifest = {
        "dataset_id": "CWTV-NEXVOX-ENGINEERING-001",
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "source_commit": source_commit,
        "source_commit_time": source_meta["committer_at"],
        "history_complete": True,
        "reachable_commits": len(commits),
        "current_tracked_files": len(tree),
        "current_text_lines": current_lines,
        "engineering_events": len(events),
        "knowledge_records": knowledge_count,
        "history_records": history_count,
        "dataset_files": len(structured_files),
        "dataset_bytes": sum(dataset_sizes.values()),
        "training_eligible_files": class_counts["TRAINING_ELIGIBLE"],
        "training_review_required_files": class_counts["TRAINING_REVIEW_REQUIRED"],
        "reference_only_files": class_counts["REFERENCE_ONLY"],
        "training_prohibited_files": class_counts["TRAINING_PROHIBITED"],
    }
    write_simple_yaml(manifests / "corpus-manifest.yaml", manifest)
    write_simple_yaml(manifests / "sync-state.yaml", {
        "dataset_id": "CWTV-NEXVOX-ENGINEERING-001",
        "schema_version": SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "source_commit": source_commit,
        "source_commit_time": source_meta["committer_at"],
        "source_history_complete": True,
        "projection_mode": "exact_git_commit",
        "projection_commit_required_after_source_commit": True,
        "projection_commit_recursion": "prohibited",
    })

    # Checksums cover every tracked corpus file except checksums itself.
    checksums_path = OUT / "checksums.sha256"
    all_files = sorted(p for p in OUT.rglob("*") if p.is_file() and p != checksums_path)
    lines = []
    for p in all_files:
        rel = p.relative_to(OUT).as_posix()
        lines.append(f"{sha256_bytes(p.read_bytes())}  {rel}")
    checksums_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "commits": len(commits), "files": len(tree), "events": len(events), "symbols": len(symbol_rows),
        "dependencies": len(dep_rows), "knowledge_records": knowledge_count, "history_records": history_count,
        "file_versions": len(file_version_rows), "commit_changes": len(commit_change_rows),
        "failures": len(failures), "corrections": len(correction_keys), "qualifications": len(qual_rows),
        "artifacts": len(artifact_rows), "reconciliations": len(recon_rows), "decisions": len(decision_rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the deterministic CineWatch NexVox engineering knowledge corpus.")
    parser.add_argument("--source-commit", default="HEAD", help="Exact Git commit/ref to project. Default: HEAD")
    args = parser.parse_args()
    try:
        stats = build(args.source_commit)
        print("PASS  built NexVox engineering corpus")
        for k, v in stats.items():
            print(f"PASS  {k}={v}")
        return 0
    except (OSError, subprocess.CalledProcessError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
