from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("build_pc_person_dialogue_template_lf_repair_v1.py")
SPEC = importlib.util.spec_from_file_location("person_dialogue_template_lf_repair", SCRIPT)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = BUILDER
SPEC.loader.exec_module(BUILDER)


class PersonDialogueTemplateLfRepairTests(unittest.TestCase):
    def test_exact_twenty_physical_targets(self) -> None:
        targets = BUILDER.TARGETS
        self.assertEqual(len(targets), 20)
        self.assertEqual(
            [(target.relative, target.block_id, target.record_id) for target in targets[:10]],
            [(BUILDER.BASE_RELATIVE, 8, record_id) for record_id in (*range(258, 263), *range(268, 273))],
        )
        self.assertEqual(
            [(target.relative, target.block_id, target.record_id) for target in targets[10:]],
            [(BUILDER.PK_RELATIVE, 8, record_id) for record_id in (*range(264, 269), *range(274, 279))],
        )

    def test_only_literal_zero_has_a_replacement(self) -> None:
        for relative in BUILDER.RESOURCE_ORDER:
            replacements = BUILDER.replacements_for(relative)
            self.assertEqual(len(replacements), 10)
            self.assertEqual({literal_id for _, _, literal_id in replacements}, {0})
            for target in BUILDER.targets_for(relative):
                self.assertEqual(
                    replacements[target.coordinate],
                    BUILDER.FAMILY_KO_LITERALS[target.family][0] + "\n",
                )

    def test_pinned_literal_and_control_contracts(self) -> None:
        for target in BUILDER.TARGETS:
            self.assertEqual(len(BUILDER.FAMILY_KO_LITERALS[target.family]), 3)
            self.assertEqual(len(BUILDER.FAMILY_JP_LITERALS[target.family]), 3)
            self.assertEqual(len(target.expected_opaque), 4)
            self.assertEqual(target.expected_opaque[1], b"\x02\x32")
            self.assertTrue(any(span.startswith(b"\x01\x43") for span in target.expected_opaque))
            self.assertTrue(target.expected_opaque[-1].endswith(b"\x05\x05\x05"))

    def test_input_output_pins_and_candidate_path(self) -> None:
        self.assertEqual(
            BUILDER.CONTRACTS[BUILDER.BASE_RELATIVE].source_sha256,
            "F7E3705E421556DCF0BBF1F99562762471FA8E7563E5DFDC0F53BDDC0E24E969",
        )
        self.assertEqual(
            BUILDER.CONTRACTS[BUILDER.PK_RELATIVE].source_sha256,
            "06EC887CB3772D765501A5C270E6301344799585BACB47834873580CEB975747",
        )
        self.assertEqual(
            BUILDER.CONTRACTS[BUILDER.BASE_RELATIVE].output_sha256,
            "4E74E5241485E6DEDD290B81781259010D9D49EA9F76DE7166B090657C535374",
        )
        self.assertEqual(
            BUILDER.CONTRACTS[BUILDER.PK_RELATIVE].output_sha256,
            "A8983770FF9026F018042D94F44AF7D0E67B6A7E01F42891B74386B32078791D",
        )
        self.assertEqual(
            BUILDER.CONTRACTS[BUILDER.BASE_RELATIVE].source_raw_sha256,
            "6B3777F916CBBC1138856B95BC26C21B9B746F7A6C579F47FB7083037FE13ED6",
        )
        self.assertEqual(
            BUILDER.CONTRACTS[BUILDER.PK_RELATIVE].source_raw_sha256,
            "ADD199EA6B378F5F408497FBC544FA573118C6A4F08734EF5E165D1338500876",
        )
        self.assertEqual(
            BUILDER.CONTRACTS[BUILDER.BASE_RELATIVE].output_raw_sha256,
            "51A0BE049FAA9A752F237AAA26355F68990EF8251E3373DF9301714C20112501",
        )
        self.assertEqual(
            BUILDER.CONTRACTS[BUILDER.PK_RELATIVE].output_raw_sha256,
            "A395885A2FC8CCDD1CF26F92D0B9F1C8B4D62EBE8ACE8D3B17B1DCE501C90CE8",
        )
        self.assertEqual(
            BUILDER.CONTRACTS[BUILDER.BASE_RELATIVE].output_raw_size
            - BUILDER.CONTRACTS[BUILDER.BASE_RELATIVE].source_raw_size,
            20,
        )
        self.assertEqual(
            BUILDER.CONTRACTS[BUILDER.PK_RELATIVE].output_raw_size
            - BUILDER.CONTRACTS[BUILDER.PK_RELATIVE].source_raw_size,
            20,
        )
        self.assertTrue(str(BUILDER.DEFAULT_OUTPUT_ROOT).endswith("candidate"))


if __name__ == "__main__":
    unittest.main()
