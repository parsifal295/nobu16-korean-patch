#!/usr/bin/env python3
"""Regression tests for the runtime Korean surface audit."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
AUDIT_PATH = WORKSTREAM / "audit_runtime_surface_v1.py"


def load_audit() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_runtime_surface_audit_v1",
        AUDIT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {AUDIT_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_audit()


class RuntimeSurfaceAuditTests(unittest.TestCase):
    def test_dual_particle_vocabulary_includes_both_direction_forms(self):
        self.assertIn("(으)로", AUDIT.DUAL_PARTICLES)
        self.assertIn("으로(로)", AUDIT.DUAL_PARTICLES)

    def test_duplicated_polite_ending_is_rejected(self):
        self.assertEqual(
            AUDIT.literal_orthography_artifact_reasons(
                "\uac10\uc0ac\ud574\uc694\uc624"
            ),
            ("duplicated_polite_ending_yo_o",),
        )
        self.assertEqual(
            AUDIT.literal_orthography_artifact_reasons(
                "\uac10\uc0ac\ud569\ub2c8\ub2e4"
            ),
            (),
        )

    def test_fixed_batchim_selector_contract(self):
        clan = {"group": 4, "property": 0x32}
        castle = {"group": 3, "property": 0x32}
        person = {"group": 2, "property": 0x33}
        self.assertTrue(AUDIT.selector_particle_is_safe(clan, "이"))
        self.assertTrue(AUDIT.selector_particle_is_safe(castle, "으로"))
        self.assertFalse(AUDIT.selector_particle_is_safe(clan, "가"))
        self.assertFalse(AUDIT.selector_particle_is_safe(person, "이"))

    def test_fixed_particle_variant_contract(self):
        self.assertTrue(
            AUDIT.fixed_particle_matches_variant("\uc740", "\uc8fc\uad70")
        )
        self.assertFalse(
            AUDIT.fixed_particle_matches_variant("\ub294", "\uc8fc\uad70")
        )
        self.assertTrue(
            AUDIT.fixed_particle_matches_variant("\ub85c", "\uc131\uc8fc")
        )
        self.assertTrue(
            AUDIT.fixed_particle_matches_variant("\ub85c", "\uc11c\uc6b8")
        )
        self.assertFalse(
            AUDIT.fixed_particle_matches_variant("\uc73c\ub85c", "\uc11c\uc6b8")
        )
        self.assertIsNone(
            AUDIT.fixed_particle_matches_variant("\uc774", "123")
        )

    def test_call_semantic_carrier_artifacts_are_rejected(self):
        self.assertEqual(
            AUDIT.call_semantic_carrier_artifact_reason(
                (0, 8),
                "\uaed8\uc11c \uc624\uc168\uc2b5\ub2c8\ub2e4",
            ),
            "mixed_register_call_followed_by_fixed_honorific_particle",
        )
        self.assertEqual(
            AUDIT.call_semantic_carrier_artifact_reason(
                (0, 1),
                "\uaed8 \uc5ec\ucb64\ubcf4\uaca0\uc2b5\ub2c8\ub2e4",
            ),
            "mixed_register_call_followed_by_fixed_honorific_particle",
        )
        self.assertIsNone(
            AUDIT.call_semantic_carrier_artifact_reason(
                (0, 1232),
                "\uaed8\uc11c \uc624\uc168\uc2b5\ub2c8\ub2e4",
            )
        )
        self.assertEqual(
            AUDIT.call_semantic_carrier_artifact_reason(
                (0, 8),
                " \ubcf8\uc778\uc774 \ub098\uc11c\uaca0\uc2b5\ub2c8\ub2e4",
            ),
            "mixed_register_call_followed_by_self_reference_carrier",
        )
        self.assertEqual(
            AUDIT.call_semantic_carrier_artifact_reason(
                (0, 1),
                "\uc790\uc2e0\uc774 \ub9e1\uaca0\uc2b5\ub2c8\ub2e4",
            ),
            "missing_space_before_reflexive_carrier",
        )
        self.assertIsNone(
            AUDIT.call_semantic_carrier_artifact_reason(
                (0, 1),
                " \uc790\uc2e0\uc774 \ub9e1\uaca0\uc2b5\ub2c8\ub2e4",
            )
        )
        self.assertEqual(
            AUDIT.call_semantic_carrier_artifact_reason(
                (0, 8),
                " \ubb34\uc7a5\uc774 \uc544\ub2cc\uac00",
            ),
            "address_term_followed_by_role_carrier",
        )
        self.assertEqual(
            AUDIT.call_semantic_carrier_artifact_reason(
                (0, 4),
                " \ubcf8\uc778\uc774 \ub098\uc11c\uaca0\ub2e4",
            ),
            "mixed_register_call_followed_by_self_reference_carrier",
        )
        self.assertIsNone(
            AUDIT.call_semantic_carrier_artifact_reason(
                (0, 29),
                "\uc758 \uacc1\uc744 \uc9c0\ud0a4\uaca0\ub2e4",
            )
        )

    def test_selector_semantic_carrier_artifacts_are_rejected(self):
        person = {
            "group": 2,
            "slot": 0,
            "property": 0x33,
            "raw_hex": "024633",
        }
        self.assertEqual(
            AUDIT.selector_semantic_carrier_artifact_reason(
                person,
                " \uc7a5\uc218\uac00 \ub098\uc12c\ub2c8\ub2e4",
            ),
            "dynamic_selector_followed_by_unreviewed_person_carrier",
        )
        self.assertEqual(
            AUDIT.selector_semantic_carrier_artifact_reason(
                person,
                " \uc778\ubb3c\uc744 \uc870\uc0ac\ud558\uac8c",
            ),
            "dynamic_selector_followed_by_unreviewed_person_carrier",
        )
        self.assertEqual(
            AUDIT.selector_semantic_carrier_artifact_reason(
                person,
                " \ubcf8\uc778\uc774 \uc9c0\ucf1c \ub0b4\uaca0\uc2b5\ub2c8\ub2e4",
            ),
            "dynamic_selector_followed_by_unreviewed_person_carrier",
        )
        self.assertEqual(
            AUDIT.selector_semantic_carrier_artifact_reason(
                {
                    "group": 10,
                    "slot": 0,
                    "property": 0x33,
                    "raw_hex": "025A33",
                },
                " \uce21\uc758 \ud64d\uc218 \ud53c\ud574",
            ),
            "location_selector_followed_by_faction_side_carrier",
        )
        self.assertIsNone(
            AUDIT.selector_semantic_carrier_artifact_reason(
                person,
                "\uc758 \uc81c\uc548\uc744 \ubc1b\uc544\ub4e4\uc600\ub2e4",
            )
        )
        self.assertIsNone(
            AUDIT.selector_semantic_carrier_artifact_reason(
                person,
                " \ucabd\uc73c\ub85c \ud5a5\ud588\ub2e4",
            )
        )

    def test_selector_left_boundary_spacing_is_rejected(self):
        clan = {
            "group": 4,
            "slot": 0,
            "property": 0x32,
            "raw_hex": "025032",
        }
        self.assertEqual(
            AUDIT.selector_left_boundary_spacing_reason(
                clan,
                "\ud6d7\ub0a0\uc5d0\ub294",
            ),
            "lexical_selector_concatenated_to_left_literal",
        )
        self.assertIsNone(
            AUDIT.selector_left_boundary_spacing_reason(
                clan,
                "\ud6d7\ub0a0 ",
            )
        )
        self.assertIsNone(
            AUDIT.selector_left_boundary_spacing_reason(
                clan,
                "\u300c",
            )
        )
        self.assertIsNone(
            AUDIT.selector_left_boundary_spacing_reason(
                clan,
                "\u2192",
            )
        )
        self.assertEqual(
            AUDIT.selector_left_boundary_spacing_reason(
                {
                    "group": 0,
                    "slot": 0,
                    "property": None,
                    "raw_hex": "0228",
                },
                "\uae08",
            ),
            "integer_selector_concatenated_to_left_literal",
        )
        self.assertIsNone(
            AUDIT.selector_left_boundary_spacing_reason(
                {
                    "group": 0,
                    "slot": 0,
                    "property": None,
                    "raw_hex": "0228",
                },
                "LV",
            )
        )
        self.assertIsNone(
            AUDIT.selector_left_boundary_spacing_reason(
                {
                    "group": 0,
                    "slot": 0,
                    "property": None,
                    "raw_hex": "0228",
                },
                "\uc5b4\ub290\ub367 \uc81c",
            )
        )

    def test_wrapped_particle_boundary_adjudication(self):
        wrapped = AUDIT.boundary_particle_match(
            "base_msggame",
            (2, 644),
            2,
            ")\uac00 \uc644\uc131\ub418\ub824\uba74",
        )
        self.assertIsNotNone(wrapped)
        assert wrapped is not None
        self.assertEqual(wrapped.group("particle"), "\uac00")

        demonstrative = AUDIT.boundary_particle_match(
            "base_msggame",
            (8, 1),
            0,
            "\n\uc774 \uac00\ubb38\uc740",
        )
        self.assertIsNone(demonstrative)

        adjudicated_i = AUDIT.boundary_particle_match(
            "base_msggame",
            (2, 645),
            2,
            ")\u300d\uc774 \ubc1c\ub839\ub418\ub824\uba74",
        )
        self.assertIsNotNone(adjudicated_i)
        assert adjudicated_i is not None
        self.assertEqual(adjudicated_i.group("particle"), "\uc774")

        terminal_literal_particle = AUDIT.boundary_particle_match(
            "pk_msggame",
            (6, 3350),
            0,
            "\uc774",
        )
        self.assertIsNotNone(terminal_literal_particle)
        assert terminal_literal_particle is not None
        self.assertEqual(terminal_literal_particle.group("particle"), "\uc774")

    @classmethod
    def setUpClass(cls) -> None:
        cls.base = AUDIT.audit_resource(
            "base_msggame",
            AUDIT.DEFAULT_BASE,
        )
        cls.pk = AUDIT.audit_resource(
            "pk_msggame",
            AUDIT.DEFAULT_PK,
        )

    def categories(
        self,
        audit: Any,
        coordinate: tuple[int, int, int],
    ) -> set[str]:
        block_id, record_id, literal_id = coordinate
        return {
            issue.category
            for issue in audit.issues
            if (
                issue.block_id,
                issue.record_id,
                issue.literal_id,
            )
            == (block_id, record_id, literal_id)
        }

    def test_full_archives_decode_without_gaps(self) -> None:
        self.assertEqual(
            self.base.record_count,
            self.base.decoded_record_count,
        )
        self.assertEqual(
            self.pk.record_count,
            self.pk.decoded_record_count,
        )

    def test_base_relation_log_placeholder_is_detected(self) -> None:
        self.assertIn(
            "unresolved_dual_particle",
            self.categories(self.base, (6, 3957, 0)),
        )
        self.assertIn(
            "unresolved_dual_particle",
            self.categories(self.base, (6, 3958, 0)),
        )

    def test_pk_siege_proposal_defects_are_detected(self) -> None:
        categories = self.categories(self.pk, (15, 1545, 0))
        self.assertIn("unresolved_dual_particle", categories)
        self.assertIn("duplicated_terminal_boundary", categories)
        self.assertIn(
            "selector_fixed_particle",
            self.categories(self.pk, (15, 1545, 2)),
        )

    def test_pk_illness_name_boundary_is_detected(self) -> None:
        self.assertIn(
            "selector_fixed_particle",
            self.categories(self.pk, (2, 148, 0)),
        )

    def test_base_called_pronoun_particle_boundary_is_detected(self) -> None:
        self.assertIn(
            "call_fixed_particle",
            self.categories(self.base, (2, 128, 1)),
        )

    def test_pk_called_pronoun_particle_boundary_is_detected(self) -> None:
        self.assertIn(
            "call_fixed_particle",
            self.categories(self.pk, (2, 140, 1)),
        )

    def test_user_reported_left_selector_boundaries_are_detected(self):
        self.assertIn(
            "selector_left_boundary_spacing",
            self.categories(self.base, (6, 3761, 0)),
        )
        self.assertIn(
            "selector_left_boundary_spacing",
            self.categories(self.pk, (6, 3768, 0)),
        )
        self.assertIn(
            "selector_left_boundary_spacing",
            self.categories(self.pk, (6, 4917, 0)),
        )


if __name__ == "__main__":
    unittest.main()
