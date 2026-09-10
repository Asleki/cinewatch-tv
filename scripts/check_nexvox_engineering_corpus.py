#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "nexvox" / "engineering"
REQUIRED = {
    "README.md",
    "DATASET_CARD.md",
    "authority/CineWatch_NexVox_Engineering_Knowledge_Authority_001.md",
    "policy/corpus-policy.yaml",
    "schemas/records.schema.yaml",
    "manifests/corpus-manifest.yaml",
    "manifests/sync-state.yaml",
    "narratives/engineering-history.md",
    "narratives/architecture-decisions.md",
    "narratives/failures-corrections-lessons.md",
    "narratives/engineering-methods.md",
    "narratives/glossary.md",
    "datasets/repository-files.csv",
    "datasets/repository-file-versions.csv",
    "datasets/commits.csv",
    "datasets/commit-changes.csv",
    "datasets/symbols.csv",
    "datasets/dependencies.csv",
    "datasets/milestones.csv",
    "datasets/artifacts.csv",
    "datasets/failure-correction-chains.csv",
    "datasets/qualifications.csv",
    "datasets/decisions.csv",
    "datasets/conversation-sources.csv",
    "datasets/source-reconciliations.csv",
    "datasets/knowledge-records.jsonl",
    "datasets/history-records.jsonl",
    "evals/engineering-knowledge-evals.yaml",
    "checksums.sha256",
}
GENERATED = {
    "DATASET_CARD.md",
    "manifests/corpus-manifest.yaml",
    "manifests/sync-state.yaml",
    "narratives/engineering-history.md",
    "narratives/architecture-decisions.md",
    "narratives/failures-corrections-lessons.md",
    "narratives/engineering-methods.md",
    "narratives/glossary.md",
    "datasets/repository-files.csv",
    "datasets/repository-file-versions.csv",
    "datasets/commits.csv",
    "datasets/commit-changes.csv",
    "datasets/symbols.csv",
    "datasets/dependencies.csv",
    "datasets/milestones.csv",
    "datasets/artifacts.csv",
    "datasets/failure-correction-chains.csv",
    "datasets/qualifications.csv",
    "datasets/decisions.csv",
    "datasets/source-reconciliations.csv",
    "datasets/knowledge-records.jsonl",
    "datasets/history-records.jsonl",
    "checksums.sha256",
}

ALLOWED_PROJECTION_PATHS = {f"nexvox/engineering/{rel}" for rel in GENERATED}


def projection_path_violations(paths: set[str]) -> list[str]:
    return sorted(path for path in paths if path not in ALLOWED_PROJECTION_PATHS)


def fail(msg: str) -> None:
    print(f"FAIL  {msg}", file=sys.stderr)
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS  {msg}")


def run_git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def flat_yaml(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if not m:
            continue
        value = m.group(2).strip()
        if value.startswith('"') and value.endswith('"'):
            value = json.loads(value)
        result[m.group(1)] = value
    return result


def main() -> int:
    if not CORPUS.is_dir():
        fail("nexvox/engineering directory is missing")
    actual = {p.relative_to(CORPUS).as_posix() for p in CORPUS.rglob("*") if p.is_file()}
    missing = sorted(REQUIRED - actual)
    unexpected = sorted(actual - REQUIRED)
    if missing:
        fail("missing corpus files: " + ", ".join(missing))
    if unexpected:
        fail("unexpected corpus files: " + ", ".join(unexpected))
    ok("exact 29-file NexVox corpus layout")

    sync = flat_yaml(CORPUS / "manifests" / "sync-state.yaml")
    source = sync.get("source_commit", "")
    if not re.fullmatch(r"[0-9a-f]{40}", source):
        fail("sync-state source_commit is not a full SHA")
    subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{source}^{{commit}}"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    head = run_git("rev-parse", "HEAD").strip()
    body = run_git("show", "-s", "--format=%B", "HEAD")
    if head == source:
        ok("corpus projects current HEAD source commit")
    else:
        if not re.search(r"(?mi)^NexVox-Projection:\s*true\s*$", body):
            fail(f"corpus is stale: source {source[:7]} does not equal HEAD {head[:7]} and HEAD is not a NexVox projection commit")
        m = re.search(r"(?mi)^NexVox-Source-Commit:\s*([0-9a-f]{40})\s*$", body)
        parent = run_git("rev-parse", "HEAD^").strip()
        if not m or m.group(1) != source or parent != source:
            fail("projection commit trailers/parent do not match sync-state source_commit")
        ok("projection commit binds exactly to preceding source commit")

        changed_paths = {
            line.strip()
            for line in run_git("diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").splitlines()
            if line.strip()
        }
        if not changed_paths:
            fail("projection commit contains no changed files")
        violations = projection_path_violations(changed_paths)
        if violations:
            fail("projection commit changes non-generator-owned paths: " + ", ".join(violations))
        ok("projection commit changes only generator-owned corpus paths")

    checksum_lines = (CORPUS / "checksums.sha256").read_text(encoding="utf-8").splitlines()
    seen = set()
    for line in checksum_lines:
        m = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not m:
            fail(f"invalid checksum line: {line}")
        expected, rel = m.groups()
        path = CORPUS / rel
        if not path.is_file():
            fail(f"checksum references missing file: {rel}")
        if sha256(path.read_bytes()) != expected:
            fail(f"checksum mismatch: {rel}")
        seen.add(rel)
    should = REQUIRED - {"checksums.sha256"}
    if seen != should:
        fail("checksums do not cover exactly the 28 non-checksum corpus files")
    ok("SHA-256 corpus integrity")

    for rel in ("datasets/knowledge-records.jsonl", "datasets/history-records.jsonl"):
        count = 0
        with (CORPUS / rel).open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    fail(f"invalid JSONL {rel}:{lineno}: {exc}")
                content = obj.get("content", "")
                if sha256(content.encode("utf-8")) != obj.get("content_sha256"):
                    fail(f"content hash mismatch {rel}:{lineno}")
                if obj.get("training_eligibility") in {"REFERENCE_ONLY", "TRAINING_PROHIBITED"}:
                    fail(f"non-training content emitted into {rel}:{lineno}")
                count += 1
        if count == 0:
            fail(f"empty JSONL dataset: {rel}")
        ok(f"{rel} record hashes and eligibility")

    with (CORPUS / "datasets" / "conversation-sources.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        fail("conversation-sources.csv is empty")
    for row in rows:
        if row.get("verbatim") == "false" and row.get("human_validation") != "complete" and row.get("training_eligibility") != "TRAINING_REVIEW_REQUIRED":
            fail(f"unvalidated transformed conversation source must remain review-required: {row.get('source_id')}")
    ok("conversation provenance and human-validation gate")

    # Obvious credential-value patterns; names such as AWS_SECRET_ACCESS_KEY are allowed in policy text.
    secret_patterns = [
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ]
    for rel in REQUIRED:
        path = CORPUS / rel
        if path.suffix.lower() in {".md", ".yaml", ".csv", ".jsonl", ".sha256"} or path.name == "README.md":
            text = path.read_text(encoding="utf-8")
            for pattern in secret_patterns:
                if pattern.search(text):
                    fail(f"credential-like value detected in corpus: {rel}")
    ok("corpus secret-value exclusion")

    # Deterministic regeneration into a temporary projection.
    with tempfile.TemporaryDirectory(prefix="cwtv-nexvox-check-") as td:
        temp = Path(td) / "engineering"
        shutil.copytree(CORPUS, temp)
        env = dict(os.environ)
        env["NEXVOX_ENGINEERING_OUT"] = str(temp)
        cp = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_nexvox_engineering_corpus.py"), "--source-commit", source],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        if cp.returncode != 0:
            fail("deterministic regeneration failed: " + cp.stderr.strip())
        for rel in sorted(REQUIRED):
            a = CORPUS / rel
            b = temp / rel
            if a.read_bytes() != b.read_bytes():
                fail(f"generated corpus drift: {rel}")
    ok("deterministic NexVox corpus projection")
    ok("CWTV NexVox engineering knowledge foundation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
