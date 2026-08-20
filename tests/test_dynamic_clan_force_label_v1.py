from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "workstreams"
    / "dynamic_clan_force_label_v1"
    / "build_dynamic_clan_force_label_v1.py"
)
OVERLAY = SCRIPT.with_name("dynamic_clan_force_label.overlay.v1.json")


def load_builder():
    spec = importlib.util.spec_from_file_location("dynamic_clan_force_label_builder", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("builder module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DynamicClanForceLabelTests(unittest.TestCase):
    def test_overlay_contract(self) -> None:
        payload = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertEqual(payload["entry_count"], 1)
        self.assertEqual(payload["entries"][0]["id"], 1139)
        self.assertEqual(payload["entries"][0]["source_ko"], "%s 세력")
        self.assertEqual(payload["entries"][0]["ko"], "%s 가문")
        self.assertEqual(
            payload["runtime_contract"]["argument_normalization"],
            "trim_trailing_u0020_only",
        )
        self.assertTrue(payload["runtime_contract"]["preserve_source_surname_spacing"])

    def test_real_v0940_fixture_when_available(self) -> None:
        raw_root = os.environ.get("N16_V0940_RESOURCE_ROOT")
        if not raw_root:
            self.skipTest("N16_V0940_RESOURCE_ROOT is not set")
        builder = load_builder()
        with tempfile.TemporaryDirectory() as temporary:
            output_root = Path(temporary) / "candidate"
            report = builder.build_candidate(Path(raw_root), output_root)
            self.assertEqual(report["release"], "0.94.1")
            self.assertEqual(report["coordinate"], [1139])
            self.assertEqual(report["changed_text_count"], 1)
            self.assertTrue(report["all_other_texts_unchanged"])
            target = output_root / "MSG_PK" / "JP" / "msgui.bin"
            self.assertEqual(target.stat().st_size, builder.OUTPUT_SPEC["packed_size"])
            self.assertEqual(builder.sha256(target.read_bytes()), builder.OUTPUT_SPEC["packed_sha256"])


if __name__ == "__main__":
    unittest.main()
