#!/usr/bin/env python3
"""Regression contracts for the PC-only private Wave 29 NPC-name candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_npc_name_quality_wave29_v1.py")
SPEC = importlib.util.spec_from_file_location("pc_npc_name_quality_wave29", BUILDER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
WAVE29 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = WAVE29
SPEC.loader.exec_module(WAVE29)


EXPECTED_COMPONENTS = (
    (87, "남자의", "남자의", "사내"),
    (89, "여자의", "여자의", "여자"),
    (93, "가상", "가공", "가공 "),
    (147, "고", "고", "호"),
    (174, "자비", "자비", "하비"),
    (182, "시게", "시게", "중"),
    (185, "오시", "오시", "닌"),
    (194, "시로", "시로", "흰"),
    (195, "시로", "시로", "흰"),
    (209, "오이와", "오이와", "다이간 "),
    (327, "마을", "마을", "성읍 "),
    (349, "무라", "무라", "마을 "),
    (445, "가문", "가문", "가"),
    (757, "나가", "초 ", "부족"),
    (774, "철포", "철포", "철포 "),
    (2164, "가시라", "가시라", "장"),
    (2168, "노", "노", "로"),
    (2175, "에루", "에루", "에르"),
    (2180, "스케무", "스케무", "유무"),
    (2181, "딸", "딸", "처녀"),
    (2182, "딸", "딸", "처녀"),
    (2184, "쓰카사", "쓰카사", " 대표"),
    (2187, "자", "자", "장"),
)
EXPECTED_STATIC = (
    (2832, "우에무라 요리카도", "우에무라 라이렌"),
    (2874, "다테 히사무네", "다테 나오무네"),
    (2883, "나가노 미치후지", "나가노 미치히사"),
    (2892, "후쿠시마 마사노부", "쿠시마 마사노부"),
    (2910, "미즈노 다다치카", "미즈노 다다와케"),
    (2916, "야마나 무네토요", "야마나 오키토요"),
)


class Wave29NpcNameQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        WAVE29.assert_spec()
        WAVE29.require_predecessor_root(WAVE29.PREDECESSOR_ROOT)
        cls.before = {
            path: (WAVE29.PREDECESSOR_ROOT / path).read_bytes()
            for path in WAVE29.CHANGED_PATHS
        }
        cls.output, cls.audit = WAVE29.prepare_candidate()

    def test_exact_58_slot_spec_with_directional_spaces(self) -> None:
        self.assertEqual(
            tuple(
                (fix.entry_id, fix.base_before, fix.pk_before, fix.after)
                for fix in WAVE29.COMPONENT_FIXES
            ),
            EXPECTED_COMPONENTS,
        )
        self.assertEqual(
            tuple((fix.entry_id, fix.before, fix.after) for fix in WAVE29.STATIC_FIXES),
            EXPECTED_STATIC,
        )
        self.assertEqual(len(WAVE29.COMPONENT_FIXES), 23)
        self.assertEqual(len(WAVE29.STATIC_FIXES), 6)
        self.assertEqual(len(WAVE29.COMPONENT_FIXES) * 2 + len(WAVE29.STATIC_FIXES) * 2, 58)
        self.assertEqual(WAVE29.COMPONENT_FIXES[2].after, "가공 ")
        self.assertEqual(WAVE29.COMPONENT_FIXES[9].after, "다이간 ")
        self.assertEqual(WAVE29.COMPONENT_FIXES[21].after, " 대표")

    def test_exact_wave27_eleven_file_predecessor_and_target_profile(self) -> None:
        hashes, sizes = WAVE29.profile(WAVE29.PREDECESSOR_ROOT)
        self.assertEqual(hashes, WAVE29.INPUT_SHA256)
        self.assertEqual(sizes, WAVE29.INPUT_SIZES)
        self.assertEqual(tuple(WAVE29.INPUT_SHA256), WAVE29.PROFILE_PATHS)
        self.assertEqual(tuple(WAVE29.TARGET_SHA256), WAVE29.PROFILE_PATHS)
        actual_hashes = {
            **WAVE29.INPUT_SHA256,
            **{path: WAVE29.sha256_bytes(data) for path, data in self.output.items()},
        }
        actual_sizes = {
            **WAVE29.INPUT_SIZES,
            **{path: len(data) for path, data in self.output.items()},
        }
        self.assertEqual(actual_hashes, WAVE29.TARGET_SHA256)
        self.assertEqual(actual_sizes, WAVE29.TARGET_SIZES)

    def test_only_the_exact_slots_change_and_all_other_record_bytes_match(self) -> None:
        source_base_texts, source_base_table, source_base_archive = WAVE29.parse_component_texts(
            WAVE29.BASE_STRDATA, self.before[WAVE29.BASE_STRDATA]
        )
        candidate_base_texts, candidate_base_table, candidate_base_archive = WAVE29.parse_component_texts(
            WAVE29.BASE_STRDATA, self.output[WAVE29.BASE_STRDATA]
        )
        source_pk_texts, source_pk_table, _ = WAVE29.parse_component_texts(
            WAVE29.PK_MSGDATA, self.before[WAVE29.PK_MSGDATA]
        )
        candidate_pk_texts, candidate_pk_table, _ = WAVE29.parse_component_texts(
            WAVE29.PK_MSGDATA, self.output[WAVE29.PK_MSGDATA]
        )
        assert source_base_table and candidate_base_table and source_base_archive and candidate_base_archive
        assert source_pk_table and candidate_pk_table
        expected_components = {fix.entry_id for fix in WAVE29.COMPONENT_FIXES}
        self.assertEqual(
            {i for i, (before, after) in enumerate(zip(source_base_texts, candidate_base_texts, strict=True)) if before != after},
            expected_components,
        )
        self.assertEqual(
            {i for i, (before, after) in enumerate(zip(source_pk_texts, candidate_pk_texts, strict=True)) if before != after},
            expected_components,
        )
        for before_block, after_block in zip(source_base_archive.blocks[1:], candidate_base_archive.blocks[1:], strict=True):
            self.assertEqual(before_block.table.blob, after_block.table.blob)
        for before_table, after_table, label in (
            (source_base_table, candidate_base_table, "Base strdata"),
            (source_pk_table, candidate_pk_table, "PK msgdata"),
        ):
            for entry_id in range(before_table.string_count):
                if entry_id not in expected_components:
                    with self.subTest(table=label, entry_id=entry_id):
                        self.assertEqual(
                            WAVE29.slot_bytes(before_table, entry_id),
                            WAVE29.slot_bytes(after_table, entry_id),
                        )
        for resource in (WAVE29.BASE_EV, WAVE29.PK_MSEV):
            before_texts, before_table = WAVE29.parse_static_texts(resource, self.before[resource])
            after_texts, after_table = WAVE29.parse_static_texts(resource, self.output[resource])
            expected_static = {fix.entry_id for fix in WAVE29.STATIC_FIXES}
            self.assertEqual(
                {i for i, (before, after) in enumerate(zip(before_texts, after_texts, strict=True)) if before != after},
                expected_static,
            )
            for entry_id in range(before_table.string_count):
                if entry_id not in expected_static:
                    with self.subTest(table=resource, entry_id=entry_id):
                        self.assertEqual(
                            WAVE29.slot_bytes(before_table, entry_id),
                            WAVE29.slot_bytes(after_table, entry_id),
                        )
        issue61 = WAVE29.assert_issue61_policy_unchanged(
            source_base_table,
            candidate_base_table,
            source_pk_table,
            candidate_pk_table,
        )
        self.assertEqual(issue61["shared_slot_count"], 39)
        self.assertEqual(issue61["pk_id_count"], 49)
        self.assertTrue(issue61["literal_tokens_byte_identical"])
        self.assertTrue(self.audit["changes"]["non_target_record_bytes_identical"])

    def test_pc_only_anchor_guard_and_no_alternate_platform_input(self) -> None:
        anchors = WAVE29.validate_pc_anchors()
        self.assertEqual(set(anchors), set(WAVE29.PC_REFERENCE_SPECS))
        self.assertTrue(self.audit["source_policy"]["pc_jp_predecessor_read"])
        self.assertTrue(self.audit["source_policy"]["pc_en_sc_tc_anchor_read"])
        self.assertFalse(self.audit["source_policy"]["switch_korean_read"])
        for relative, _digest, _kind, _category in WAVE29.PC_REFERENCE_SPECS.values():
            self.assertNotIn("switch", relative.casefold())
        with self.assertRaises(WAVE29.Wave29Error):
            WAVE29.reject_switch_path(Path(r"F:\Games\NOBU16\switch-korean-fixture"), "test guard")

    def test_build_and_verify_private_candidate_flow_is_deterministic(self) -> None:
        second, second_audit = WAVE29.prepare_candidate()
        self.assertEqual(self.output, second)
        self.assertEqual(
            json.dumps(self.audit, ensure_ascii=False, sort_keys=True),
            json.dumps(second_audit, ensure_ascii=False, sort_keys=True),
        )
        WAVE29.TMP_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".wave29-test-", dir=WAVE29.TMP_ROOT) as temp:
            root = Path(temp)
            output_root = root / "candidate"
            audit_path = root / "audit.v1.json"
            manifest_path = root / "build_manifest.v1.json"
            manifest = WAVE29.build_candidate(
                WAVE29.PREDECESSOR_ROOT, output_root, audit_path, manifest_path
            )
            self.assertTrue(manifest["candidate_only"])
            self.assertEqual(manifest["changed_slot_count"], 58)
            self.assertTrue(manifest["non_target_record_bytes_identical"])
            self.assertTrue(manifest["issue61_percent_policy_unchanged"])
            self.assertEqual(
                json.loads(manifest_path.read_text(encoding="utf-8"))["output_sha256"],
                WAVE29.TARGET_SHA256,
            )
            report = WAVE29.verify_private_candidate(output_root)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["changed_slot_count"], 58)
            self.assertTrue(report["non_target_record_bytes_identical"])
            self.assertTrue(report["issue61_percent_policy"]["literal_tokens_byte_identical"])
        with self.assertRaises(WAVE29.Wave29Error):
            WAVE29.require_tmp(WAVE29.PC_REFERENCE_ROOT, "external output")


if __name__ == "__main__":
    unittest.main(verbosity=2)
