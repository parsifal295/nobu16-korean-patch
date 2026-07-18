#!/usr/bin/env python3
"""Regression contracts for the private Wave 24 event-layout candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_event_layout_wave24_v1.py"
SPEC = importlib.util.spec_from_file_location("wave24_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 24 builder")
wave24 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave24
SPEC.loader.exec_module(wave24)


class Wave24EventLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.files, cls.audit, cls.manifest = wave24.prepare_candidate()
        _source_files, cls.before = wave24.load_predecessor()
        _header, cls.after_raw = wave24.decompress_wrapper(cls.files[wave24.RESOURCE])
        cls.after = wave24.parse_message_table(cls.after_raw)

    def test_exact_five_id_scope_and_full_profile(self) -> None:
        self.assertEqual([change.entry_id for change in wave24.CHANGES], [3725, 4208, 4677, 4918, 5351])
        self.assertEqual(self.audit["changed_ids"], [3725, 4208, 4677, 4918, 5351])
        self.assertEqual(
            {relative: wave24.sha256_bytes(value) for relative, value in self.files.items()},
            wave24.TARGET_SHA256,
        )
        self.assertEqual({relative: len(value) for relative, value in self.files.items()}, wave24.TARGET_SIZES)
        changed = [
            identifier
            for identifier, (before, after) in enumerate(zip(self.before.table.texts, self.after.texts))
            if before != after
        ]
        self.assertEqual(changed, [3725, 4208, 4677, 4918, 5351])

    def test_pc_only_source_anchors_are_fail_closed(self) -> None:
        sources = wave24.load_sources()
        self.assertEqual(set(sources), {"JP", "EN", "SC", "TC"})
        for change in wave24.CHANGES:
            for language, source in sources.items():
                self.assertEqual(
                    wave24.text_hash(source.table.texts[change.entry_id]),
                    change.source_hashes[language],
                    f"{change.entry_id}:{language}",
                )
        policy = self.audit["source_policy"]
        self.assertTrue(policy["pristine_pc_japanese_read"])
        self.assertTrue(policy["pc_pk_en_sc_tc_context_read"])
        self.assertFalse(policy["switch_korean_read"])
        self.assertEqual(policy["steam_apply_capability"], "absent")

    def test_exact_reflow_text_and_real_font_widths(self) -> None:
        expected = {
            3725: ("이 난세에는 힘없는 자는\n멸망할 뿐이다…… 너와 함께\n검술을 배우는 것도 그 때문이다.", (552, 648, 744)),
            4208: ("(영리한 두 아우에게 가려 있었지만,\n그는 착실히 당주로서의 자질을\n보이고 있었다……)", (816, 696, 432)),
            4677: ("어디의 누군지도 모를 자에게\n넘어갈 바에는,\n자네 같은 사내에게 넘기고 싶군.", (648, 336, 744)),
            4918: ("계책이 많으면 이기고, 적으면\n진다…… 인가. 아버님, 못난 아들을\n용서해 주십시오……", (672, 816, 456)),
            5351: ("그의 약진에는 미카와 무사들의\n강인함과 동족 의식에서 나온 결속이\n크게 이바지했다.", (696, 816, 384)),
        }
        advance, _font = wave24.load_font()
        for change in wave24.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                text, widths = expected[change.entry_id]
                self.assertEqual(change.target, text)
                self.assertEqual(change.widths_px, widths)
                self.assertEqual(wave24.line_widths(text, advance), widths)
                self.assertLessEqual(max(widths), wave24.MAX_LINE_PX)
                self.assertLessEqual(len(widths), wave24.MAX_LINES)
                self.assertEqual(wave24.text_hash(self.after.texts[change.entry_id]), change.target_sha256)

    def test_manual_break_token_and_whitespace_signatures_are_preserved(self) -> None:
        for change in wave24.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                before = self.before.table.texts[change.entry_id]
                after = self.after.texts[change.entry_id]
                self.assertEqual(wave24.text_signature(before), wave24.text_signature(after))
                self.assertNotIn("\ufffd", after)
                self.assertIsNone(wave24.FOREIGN_CJK_RE.search(after))

    def test_wave18_labels_and_unmodified_table_roundtrip_are_retained(self) -> None:
        for identifier in wave24.RETAINED_WAVE18_IDS:
            self.assertEqual(self.before.table.texts[identifier], self.after.texts[identifier])
        self.assertEqual(wave24.rebuild_message_table(self.after, self.after.texts), self.after_raw)

    def test_private_path_guards_reject_non_tmp_output(self) -> None:
        with self.assertRaises(wave24.Wave24Error):
            wave24.require_tmp(wave24.REPO / "outside-wave24", "test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
