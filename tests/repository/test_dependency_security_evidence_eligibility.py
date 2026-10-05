from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


class DependencySecurityEvidenceEligibilityTest(unittest.TestCase):
    def test_external_security_evidence_requires_human_training_review(self):
        root = Path(__file__).resolve().parents[2]
        spec = importlib.util.spec_from_file_location("cwtv_security_corpus_generator", root / "scripts/build_nexvox_engineering_corpus.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        for name in ("advisory-github.json", "advisory-nextjs.json", "security-correction-evidence.json", "qualification-report.md", "002-reconciliation-plan.md"):
            with self.subTest(name=name):
                eligibility, _ = module.classify("docs/engineering/dependency-security/2026-10-05/" + name)
                self.assertEqual(eligibility, "TRAINING_REVIEW_REQUIRED")
        self.assertEqual(module.classify("apps/web/src/app/page.tsx")[0], "TRAINING_ELIGIBLE")
