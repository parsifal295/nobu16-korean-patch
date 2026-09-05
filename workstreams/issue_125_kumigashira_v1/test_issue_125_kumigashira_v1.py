from __future__ import annotations

import importlib.util
import os
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MODULE_PATH = HERE / "build_issue_125_kumigashira_v1.py"
SPEC = importlib.util.spec_from_file_location("issue125_builder", MODULE_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)

WORKSPACE = Path(os.environ.get("NOBU16_TEST_WORKSPACE", str(next(
    (parent for parent in (REPO, *REPO.parents) if (parent / "workspace.paths.json").is_file()),
    REPO,
))))
INPUT_ROOT = WORKSPACE / "scratch/scenario-title-mugen-v0950-release-20260823-01/generator-b/target"
JP_ROOT = WORKSPACE / "private-inputs/rust-patcher-v0151/stock"


class Issue125KumigashiraTests(unittest.TestCase):
    def test_policy_has_exact_gameplay_scope(self) -> None:
        counts = [
            len(policy.get("coordinates", policy.get("ids", ())))
            for policy in builder.FILES.values()
        ]
        self.assertEqual(counts, [13, 19, 3])
        self.assertEqual(sum(counts), 35)
        self.assertEqual(builder.BEFORE, "조두")
        self.assertEqual(builder.AFTER, "조장")

    def test_pinned_candidate_builds_with_only_35_changes(self) -> None:
        if not INPUT_ROOT.is_dir() or not JP_ROOT.is_dir():
            self.skipTest("private pinned release inputs are unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "candidate"
            validation = Path(temporary) / "validation.v1.json"
            report = builder.build(INPUT_ROOT, JP_ROOT, output, validation)
            self.assertEqual(report["changed_count"], 35)
            self.assertEqual(
                [item["changed_count"] for item in report["resources"]],
                [13, 19, 3],
            )
            self.assertTrue(validation.is_file())
            for relative, policy in builder.FILES.items():
                blob = (output / relative).read_bytes()
                self.assertEqual(len(blob), policy["output_size"])
                self.assertEqual(builder.sha256(blob), policy["output_sha256"])


if __name__ == "__main__":
    unittest.main()
