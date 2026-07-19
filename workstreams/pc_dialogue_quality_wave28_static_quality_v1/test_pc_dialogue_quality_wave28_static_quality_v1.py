#!/usr/bin/env python3
"""Regression contracts for the private PC-only Wave 28 candidate."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve()
BUILDER_PATH = SCRIPT.with_name("build_pc_dialogue_quality_wave28_static_quality_v1.py")


def load_builder():
    spec = importlib.util.spec_from_file_location("pc_dialogue_quality_wave28", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W28 = load_builder()


EXPECTED_PAIRS = (
    ((15, 219), (15, 222)), ((15, 221), (15, 224)),
    ((15, 222), (15, 225)), ((15, 223), (15, 226)),
    ((15, 226), (15, 229)), ((15, 243), (15, 246)),
    ((15, 245), (15, 248)), ((15, 246), (15, 249)),
    ((15, 247), (15, 250)), ((15, 250), (15, 253)),
    ((15, 255), (15, 258)), ((15, 257), (15, 260)),
    ((15, 260), (15, 263)), ((15, 262), (15, 265)),
    ((15, 263), (15, 266)), ((15, 271), (15, 274)),
    ((15, 276), (15, 279)), ((15, 278), (15, 281)),
    ((15, 282), (15, 285)), ((15, 1545), (15, 1575)),
)

EXPECTED_LITERAL_BOUNDARIES = {
    "half_chance": ("승산은 반반 정도", "입니다만\n시도해 볼 가치는 충분합니다."),
    "very_difficult": ("상당히 어려운 일입니다", "…\n도무지 기대할 수 없습니다."),
    "talent_assured": ("거의 틀림없이\n유망한 인재를 찾을 수 있습니다.",),
    "talent_chance": ("유망한 인재는 찾기 어려운 법…\n허나 이번에는 승산이 있어 보이니", "\n이 기회를 놓치지 마십시오."),
    "bad_wager": ("…솔직히, 승산 없는 도박입니다.", "\n그다지 권하고 싶지는 않습니다."),
    "proposal_easy": ("이번 안은\n무리 없이 진행될 것입니다.",),
    "proposal_try": ("아마 잘 될 것입니다.", "\n시도할 가치는 충분합니다."),
    "proposal_half": ("성공할 가능성은 반반입니다.", "\n신중히", " 판단하셔야 합니다."),
    "proposal_difficult": ("상당히 어려운 일입니다", "…\n누구 한 사람이라도 성공하면\n다행이라 하겠습니다."),
    "proposal_priority": ("그 건의도 나쁘지는 않습니다만\n이쪽 안이 우선 아닐는지요…?",),
    "destruction_ritual": ("파괴 의식에는 시간이 걸리지만\n간자를 써서 내부에서 무너뜨리겠습니다.", "\n성공할 가능성은 이쪽이 높습니다."),
    "ikki_agitation": ("요지에 집중해 선동하면\n잇키의 규모는 작아지지만\n더 빨리 일으킬 수 있습니다.",),
    "cannon_purchase": ("남만 상인에게서 카논포를 사들여\n적성 포격에 쓰시겠습니까?", "\n값은 비싸지만 위력은 절대적입니다."),
    "ninja_advice": ("끼어들어 죄송합니다", "!\n여기는 닌자가 솜씨를 보일 자리이니\n더욱 교묘한 계책을 아뢰겠습니다."),
    "merchant_advice": ("외람되오나 잠시 귀를 빌리겠소!\n여기서는 상인의 지혜를 빌려드리겠으니", "\n돈이 힘을 쓰는 것이 전국의 세상이지요."),
    "quick_scheme": ("효과는 다소 떨어지지만\n신속히 끝낼 수 있는 계책입니다.",),
    "focused_scheme": ("더 성공하기 쉬운 계책입니다.", "\n공격할 곳을 좁히는 만큼\n착실하게 진행할 수 있습니다."),
    "wide_scheme": ("채비에는 시간이 걸리지만\n넓은 범위에 손을 쓸 수 있습니다.",),
    "timely_proposal": ("그쪽 안이 채택될 줄이야…\n시의에 맞는", " 제안이었군요."),
    "unification_goal": ("천하 평정을 이루기 위해서는\n전국 과반수의 성을 다스리고\n기나이를 제압할 필요가 있습니다.",),
}
EXPECTED_BOUNDARY_REDUCTIONS = {
    "proposal_priority": 1,
    "destruction_ritual": 1,
    "ikki_agitation": 2,
}


class Wave28StaticQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        W28.require_predecessor_root(W28.PREDECESSOR_ROOT)
        W28.validate_wave27_evidence()
        cls.before = {
            resource: W28.records_by_coordinate((W28.PREDECESSOR_ROOT / resource).read_bytes())
            for resource in W28.CHANGED_PATHS
        }
        cls.output_a, cls.audit_a = W28.prepare_candidate()
        cls.output_b, cls.audit_b = W28.prepare_candidate()
        cls.after = {resource: W28.records_by_coordinate(data) for resource, data in cls.output_a.items()}
        cls.advance, cls.font = W28.W27.load_font_advance()

    def test_exact_wave27_eleven_file_preimage_and_evidence(self) -> None:
        hashes, sizes = W28.profile(W28.PREDECESSOR_ROOT)
        self.assertEqual(hashes, W28.INPUT_SHA256)
        self.assertEqual(sizes, W28.INPUT_SIZES)
        self.assertEqual(tuple(W28.INPUT_SHA256), W28.PROFILE_PATHS)
        for item in W28.WAVE27_EVIDENCE.values():
            path = Path(item["path"])
            self.assertEqual(path.stat().st_size, item["size"])
            self.assertEqual(W28.sha256_path(path), item["sha256"])
        self.assertEqual(W28.INPUT_SHA256[W28.BASE_MSGGAME], "4D6460F1B717FD8D424229ABD619DE4093C21929F6C42B061BAD62E163C5D3CB")
        self.assertEqual(W28.INPUT_SHA256[W28.PK_MSGGAME], "AD3F6DD64C0AD360C5A8C7A4747ABFCE9B2D72BFFDD3D44940781A68AC2DE8D1")

    def test_exact_twenty_pairs_literals_layout_and_structure(self) -> None:
        self.assertEqual(
            tuple((family.base_coordinate, family.pk_coordinate) for family in W28.FAMILIES),
            EXPECTED_PAIRS,
        )
        self.assertEqual({family.name: family.target_literals for family in W28.FAMILIES}, EXPECTED_LITERAL_BOUNDARIES)
        self.assertEqual(len(W28.FAMILIES), 20)
        self.assertEqual(set(W28.TARGET_RECORD_PINS), set(EXPECTED_LITERAL_BOUNDARIES))
        for family in W28.FAMILIES:
            target_hash, target_size, target_widths = W28.TARGET_RECORD_PINS[family.name]
            for resource, coordinate in ((W28.BASE_MSGGAME, family.base_coordinate), (W28.PK_MSGGAME, family.pk_coordinate)):
                with self.subTest(family=family.name, resource=resource):
                    before = self.before[resource][coordinate]
                    after = self.after[resource][coordinate]
                    self.assertNotEqual(before.data, after.data)
                    self.assertEqual(W28.sha256_bytes(after.data), target_hash)
                    self.assertEqual(len(after.data), target_size)
                    self.assertEqual(W28.literal_texts(after), EXPECTED_LITERAL_BOUNDARIES[family.name])
                    self.assertEqual(W28.opaque_spans(after), W28.expected_target_opaque_spans(before, family.target_literals))
                    self.assertTrue(before.data.endswith(W28.RECORD_TERMINATOR))
                    self.assertTrue(after.data.endswith(W28.RECORD_TERMINATOR))
                    self.assertTrue(W28.complete_0143_commands(W28.opaque_spans(before)))
                    self.assertEqual(W28.complete_0143_commands(W28.opaque_spans(after)), ())
                    topology = W28.marker_topology(after)
                    self.assertEqual(len(topology), len(family.target_literals))
                    self.assertTrue(all(start == W28.W27.LITERAL_START and end == W28.W27.LITERAL_END for start, end in topology))
                    self.assertEqual(
                        len(W28.literal_texts(before)) - len(W28.literal_texts(after)),
                        EXPECTED_BOUNDARY_REDUCTIONS.get(family.name, 0),
                    )
                    layout = W28.line_layout(W28.literal_texts(after), type(self).advance)
                    self.assertEqual(tuple(layout["line_widths_px"]), target_widths)
                    self.assertLessEqual(layout["line_count"], 3)
                    self.assertLessEqual(layout["max_width_px"], W28.DIALOGUE_MAX_LINE_PX)
                    self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_only_the_forty_specified_records_change(self) -> None:
        expected = W28.expected_coordinate_sets()
        for resource in W28.CHANGED_PATHS:
            with self.subTest(resource=resource):
                self.assertEqual(set(self.before[resource]), set(self.after[resource]))
                changed = {
                    coordinate for coordinate in self.before[resource]
                    if self.before[resource][coordinate].data != self.after[resource][coordinate].data
                }
                self.assertEqual(changed, expected[resource])
                self.assertEqual(len(changed), 20)
                for coordinate, record in self.before[resource].items():
                    if coordinate not in changed:
                        self.assertEqual(record.data, self.after[resource][coordinate].data)

    def test_packed_full_profile_and_roundtrip_are_pinned(self) -> None:
        hashes = {**W28.INPUT_SHA256, **{resource: W28.sha256_bytes(data) for resource, data in self.output_a.items()}}
        sizes = {**W28.INPUT_SIZES, **{resource: len(data) for resource, data in self.output_a.items()}}
        self.assertEqual(hashes, W28.TARGET_SHA256)
        self.assertEqual(sizes, W28.TARGET_SIZES)
        self.assertEqual(W28.TARGET_SHA256[W28.BASE_MSGGAME], "D70BA2EBE17CE056B9E348C610FE1F82B28285BAF1940F4450AE2D7D62B2E688")
        self.assertEqual(W28.TARGET_SHA256[W28.PK_MSGGAME], "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9")
        for resource, packed in self.output_a.items():
            W28.validate_raw_roundtrip(packed, f"test Wave 28 {resource}")

    def test_pc_only_jp_and_context_anchors(self) -> None:
        anchors = self.audit_a["pc_anchors"]
        self.assertEqual(set(anchors["reference_packed_sha256"]), {"BASE_JP", "PK_JP", "EN", "SC", "TC"})
        self.assertEqual(len(anchors["families"]), 20)
        for row in anchors["families"]:
            self.assertTrue(row["BASE_JP"]["record_sha256"])
            self.assertTrue(row["PK_JP"]["record_sha256"])
            self.assertEqual(set(row["contexts"]), {"EN", "SC", "TC"})
        policy = self.audit_a["source_policy"]
        self.assertTrue(policy["pc_base_pk_jp_and_en_sc_tc_anchors_read"])
        self.assertFalse(policy["switch_korean_read"])

    def test_deterministic_private_only_guards(self) -> None:
        self.assertEqual(self.output_a, self.output_b)
        self.assertEqual(
            json.dumps(self.audit_a, ensure_ascii=False, sort_keys=True),
            json.dumps(self.audit_b, ensure_ascii=False, sort_keys=True),
        )
        self.assertEqual(self.audit_a["changed_record_count"], 40)
        self.assertEqual(self.audit_a["changed_literal_count"], 68)
        self.assertFalse(self.audit_a["source_policy"]["steam_game_resource_written"])
        self.assertEqual(self.audit_a["source_policy"]["git_operation"], "absent")
        self.assertEqual(self.audit_a["source_policy"]["release_operation"], "absent")
        with self.assertRaises(W28.Wave28Error):
            W28.require_tmp(W28.W27.DEFAULT_STEAM_ROOT, "Steam path")
        with self.assertRaises(W28.Wave28Error):
            W28.require_predecessor_root(W28.W27.DEFAULT_STEAM_ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
