from __future__ import annotations

import importlib.util
import subprocess
import unittest
from pathlib import Path


class NexVoxEngineeringCorpusQualificationTest(unittest.TestCase):
    def test_nexvox_engineering_corpus_contract(self) -> None:
        root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            ["python", "scripts/check_nexvox_engineering_corpus.py"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_projection_commit_rejects_non_generated_paths(self) -> None:
        root = Path(__file__).resolve().parents[2]
        checker_path = root / "scripts" / "check_nexvox_engineering_corpus.py"
        spec = importlib.util.spec_from_file_location("cwtv_nexvox_checker", checker_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        valid = {
            "nexvox/engineering/datasets/commits.csv",
            "nexvox/engineering/manifests/sync-state.yaml",
        }
        self.assertEqual(module.projection_path_violations(valid), [])

        malformed = valid | {
            "docs/architecture/CineWatch_TV_V1_Brand_and_Streaming_Signature_Authority_001.md",
            "docs/progress/activity/engineering-events.jsonl",
        }
        self.assertEqual(
            module.projection_path_violations(malformed),
            [
                "docs/architecture/CineWatch_TV_V1_Brand_and_Streaming_Signature_Authority_001.md",
                "docs/progress/activity/engineering-events.jsonl",
            ],
        )


if __name__ == "__main__":
    unittest.main()
