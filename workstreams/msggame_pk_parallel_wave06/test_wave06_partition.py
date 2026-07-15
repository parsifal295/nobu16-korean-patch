from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "build_wave06_partition_for_test", ROOT / "build_wave06_partition.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load wave06 partition builder")
partition = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(partition)


class Wave06PartitionTests(unittest.TestCase):
    def test_checked_partition_is_the_exact_rebuild(self) -> None:
        expected = partition.encode_json(partition.make_partition())
        actual = partition.PARTITION_PATH.read_bytes()
        self.assertEqual(expected, actual)

    def test_eight_batches_are_disjoint_and_cover_all_4760(self) -> None:
        payload = json.loads(partition.PARTITION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(8, payload["batch_count"])
        union = set()
        for batch in payload["batches"]:
            coordinates = {tuple(item) for item in batch["coordinates"]}
            self.assertEqual(batch["coordinate_count"], len(coordinates))
            self.assertEqual(
                batch["coordinates_sha256"],
                partition.canonical_hash([list(item) for item in sorted(coordinates)]),
            )
            self.assertFalse(union & coordinates)
            union.update(coordinates)
        self.assertEqual(4_760, len(union))
        self.assertEqual(
            partition.REMAINING_COORDINATES_SHA256,
            partition.canonical_hash([list(item) for item in sorted(union)]),
        )

    def test_registration_suffix_does_not_feed_partition(self) -> None:
        targets = partition.target_coordinates()
        prefix, coordinates, suffix = partition.registered_prefix(targets)
        self.assertEqual(partition.PREFIX_PATTERN_COUNT, len(prefix))
        self.assertEqual(partition.PREFIX_COORDINATE_COUNT, len(coordinates))
        self.assertIsInstance(suffix, list)

    def test_public_workstream_has_no_binary_or_commercial_source_script(self) -> None:
        forbidden = {".bin", ".zip", ".g1n", ".ttf", ".otf", ".pixels"}
        for path in ROOT.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            self.assertNotIn(path.suffix.lower(), forbidden, path)
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(partition.CJK_RE.search(text), path)
            self.assertIsNone(partition.KANA_RE.search(text), path)

    def test_private_export_rejects_paths_outside_tmp_before_loading_sources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(partition.PartitionError, "repository tmp"):
                partition.export_private_context(Path(directory))


if __name__ == "__main__":
    unittest.main()
