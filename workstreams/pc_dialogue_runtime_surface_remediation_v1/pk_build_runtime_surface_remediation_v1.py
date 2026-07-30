#!/usr/bin/env python3
"""Build the PK-only runtime-surface remediation candidate.

The input is the pinned 0.15.0 PK ``msggame.bin`` candidate.  This builder
first composes the shared priority-regression overlay, then repairs every
remaining PK finding emitted by ``pc_dialogue_runtime_surface_qa_v1``:

* Korean dual-particle placeholders are resolved from a proved fixed-batchim
  selector contract, a literal Hangul syllable, or an explicit carrier noun;
* unsafe fixed particles after dynamic selectors are rewritten without
  deleting the grammatical relation;
* finite predicates before VM terminal calls are reconstructed as stems or
  nominal predicates.

The user-reported ``15:1545`` line is exceptional: its reviewed priority
literal is already a complete sentence, so its call to terminal family 376 is
retargeted to the proved empty terminal ``0:1247``.  Other duplicated copular
boundaries formerly using family 376 are retargeted to the coherent copular
family 520 after their prefixes are nominalized.

Only the PK resource is rebuilt, below a new ``tmp/`` path.  No Steam write is
performed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import sys
import tempfile
import unicodedata
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
QA_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "audit_runtime_surface_v1.py"
)
TERMINAL_DETECTOR_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "terminal_boundary_detector_v1.py"
)
STRUCTURE_AUDIT_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "audit_candidate_structure_v1.py"
)
RELATIVE_WIDTH_AUDIT_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "audit_candidate_relative_width_v1.py"
)
BASELINE_PATH = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_qa_v1"
    / "baseline.private.v1.json"
)
PRIORITY_OVERLAY = WORKSTREAM / "priority_regressions.overlay.v1.json"
SOURCE_PK = (
    REPO
    / "tmp"
    / "pc_dialogue_full_retranslation_v0150"
    / "finalizer_preflight_52803"
    / "candidate"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
PRISTINE_JP_PK = (
    REPO
    / "tmp"
    / "pc_dialogue_full_retranslation_v0150"
    / "development_steam_root_pre_base_runtime_apply_13a404f"
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
DEFAULT_OUTPUT_ROOT = (
    REPO / "tmp" / "pc_dialogue_runtime_surface_remediation_v1" / "pk"
)
DEFAULT_CANDIDATE = (
    DEFAULT_OUTPUT_ROOT / "candidate" / "MSG_PK" / "JP" / "msggame.bin"
)
DEFAULT_OVERLAY = (
    DEFAULT_OUTPUT_ROOT / "pk_runtime_surface_overlay.private.v1.jsonl"
)
DEFAULT_PRIVATE_AUDIT = (
    DEFAULT_OUTPUT_ROOT / "pk_surface_audit.private.v1.json"
)
DEFAULT_PRIVATE_TERMINAL_AUDIT = (
    DEFAULT_OUTPUT_ROOT / "pk_terminal_boundary.private.v1.json"
)
DEFAULT_REPORT = WORKSTREAM / "pk_remediation.source_free.v1.json"

EXPECTED_SOURCE_SHA256 = (
    "0330917524A47974618317A8EC56C4B471672DA5AD07000A8C5D8A7CCFB8A05F"
)
EXPECTED_PRISTINE_JP_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_SOURCE_SURFACE_COUNTS = {
    "call_fixed_particle": 106,
    "call_semantic_carrier_artifact": 47,
    "duplicated_terminal_boundary": 65,
    "literal_orthography_artifact": 4,
    "selector_fixed_particle": 631,
    "selector_left_boundary_spacing": 2493,
    "unresolved_dual_particle": 2857,
}
EXPECTED_SOURCE_LEGACY_SURFACE_ISSUE_COUNT = 3444
EXPECTED_SOURCE_SURFACE_ISSUE_COUNT = 6203
EXPECTED_SOURCE_CALL_FIXED_PARTICLE_COUNT = 106
EXPECTED_SOURCE_TERMINAL_ISSUE_COUNT = 201
EXPECTED_SOURCE_SELECTOR_LEFT_SPACING_COORDINATE_SHA256 = (
    "791B9E39C149F17B130388959BA511F049C0303D76E8D958F0C6FC3F10455799"
)
EXPECTED_TERMINAL_DETECTOR_SHA256 = (
    "BCC2F8471122192A0C05467E785C6EEC6C9D74F9DC92433E8FF4FB0857CF1598"
)
RAW_G1N_FULL_WIDTH_PX = 48
RAW_G1N_HALF_WIDTH_PX = 24
# These exact literals were separately approved because preserving a complete
# dynamic relation is more important than the conservative +24px relative
# growth heuristic.  Every resulting line remains far below the 1440px raw
# G1N hard limit; no other coordinate can inherit an exception.
APPROVED_LAYOUT_EXCEPTIONS = {
    (4, 29, 0): {
        "line_index": 3,
        "source_width_px": 96,
        "candidate_width_px": 240,
        "delta_px": 144,
        "candidate_utf16le_sha256":
            "237CEA5BBC83495DC7D304607C5465A5DF989754E87E4E45CC899A06E0611E1C",
        "reason": "user_reported_ai_help_wrap_preserves_whole_korean_word",
    },
    (6, 3931, 2): {
        "line_index": 0,
        "source_width_px": 144,
        "candidate_width_px": 192,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "F3A94CD0190137F20069DC50057993E89085E38513255C26AE64837B73A671F3",
        "reason": "dynamic_facility_and_person_objects_require_visible_spacing",
    },
    (6, 4484, 1): {
        "line_index": 0,
        "source_width_px": 72,
        "candidate_width_px": 120,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "DFF4BE25AC1898E6A9BF29CAC1150AC34B7D9FD58F8DCC533851EAF18893BF97",
        "reason": "dynamic_person_dative_requires_complete_ege_particle",
    },
    (7, 2488, 1): {
        "line_index": 1,
        "source_width_px": 216,
        "candidate_width_px": 312,
        "delta_px": 96,
        "candidate_utf16le_sha256":
            "C55898363B11F9A4CFAB0370DA62A33909E26959B35B6DC3E133C4CE69D658DC",
        "reason": "reviewed_suppression_order_uses_one_complete_imperative",
    },
    (7, 2875, 2): {
        "line_index": 0,
        "source_width_px": 96,
        "candidate_width_px": 216,
        "delta_px": 120,
        "candidate_utf16le_sha256":
            "3DEC81820E865A013EA48F73860A24A3C98CBFB9B22B4A649D3C8773EDE50F03",
        "reason": "reviewed_victory_report_expectation_uses_complete_imperative",
    },
    (9, 2522, 1): {
        "line_index": 0,
        "source_width_px": 48,
        "candidate_width_px": 96,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "E7E143567E34AF03AA4CF6643C81546E181B3B994EA59F3F500C4FFDA0A6E05A",
        "reason": "dynamic_person_dative_requires_complete_ege_particle",
    },
    (15, 587, 1): {
        "line_index": 0,
        "source_width_px": 408,
        "candidate_width_px": 480,
        "delta_px": 72,
        "candidate_utf16le_sha256":
            "BA3AC1889D82566AD48FC3E5922ED78130E8D2495DAE8974DF4749545AAC1D99",
        "reason": "our_side_dynamic_call_requires_explicit_pyeon_relation",
    },
    (7, 2842, 2): {
        "line_index": 0,
        "source_width_px": 48,
        "candidate_width_px": 96,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "F704BA605676C22BF9EA6F0BE820C7CF35DAA3E1D1D1EF8E64E3D614CA2F36AE",
        "reason": "dynamic_examples_require_spaces_on_both_literal_edges",
    },
    (9, 2593, 0): {
        "line_index": 0,
        "source_width_px": 144,
        "candidate_width_px": 192,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "D48425C8F070C4A2189C3AAC3B90D84F92DC1A12DFA8102CC1E84C84B4340E3C",
        "reason": "enemy_side_phrase_requires_internal_and_dynamic_edge_spaces",
    },
    (9, 3571, 0): {
        "line_index": 0,
        "source_width_px": 144,
        "candidate_width_px": 192,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "3FC49664D3FDB92EF4A23AB17A2EC28100CD3A69EFA52888896ED411115483FC",
        "reason": "enemy_side_phrase_requires_internal_and_dynamic_edge_spaces",
    },
    **{
        (9, record_id, 0): {
            "line_index": 0,
            "source_width_px": 144,
            "candidate_width_px": 192,
            "delta_px": 48,
            "candidate_utf16le_sha256":
                "3FC49664D3FDB92EF4A23AB17A2EC28100CD3A69EFA52888896ED411115483FC",
            "reason":
                "enemy_side_phrase_requires_internal_and_dynamic_edge_spaces",
        }
        for record_id in (3575, 3579, 3581, 3582)
    },
    **{
        (9, record_id, 0): {
            "line_index": 0,
            "source_width_px": 144,
            "candidate_width_px": 192,
            "delta_px": 48,
            "candidate_utf16le_sha256":
                "55561AA439771F5188CDD15AC00C5CEC729DA08633DCBC985D28B8106B70DAE0",
            "reason":
                "enemy_side_phrase_requires_internal_and_dynamic_edge_spaces",
        }
        for record_id in (3573, 3576, 3578, 3580)
    },
    (9, 4132, 0): {
        "line_index": 0,
        "source_width_px": 144,
        "candidate_width_px": 192,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "8B400AE5079E4C891523F5C6B7C498033C0B734D805CAFDD87B5D3C304926518",
        "reason": "castle_side_phrase_requires_internal_and_dynamic_edge_spaces",
    },
    (14, 245, 3): {
        "line_index": 4,
        "source_width_px": 1728,
        "candidate_width_px": 1776,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "145BBCCC53058C3321DF90D1784668175649F40A250FD31B102936A640460367",
        "reason": "siege_rule_terms_require_bound_noun_spacing",
    },
    (15, 814, 1): {
        "line_index": 0,
        "source_width_px": 96,
        "candidate_width_px": 144,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "7859DAA2DB1F4378759F9037763D9DCADEF868E6078465E0607D20AE9727A6C2",
        "reason": "dynamic_examples_bound_noun_requires_both_edge_spaces",
    },
    **{
        (15, record_id, literal_id): {
            "line_index": 0,
            "source_width_px": 48,
            "candidate_width_px": 96,
            "delta_px": 48,
            "candidate_utf16le_sha256":
                "F704BA605676C22BF9EA6F0BE820C7CF35DAA3E1D1D1EF8E64E3D614CA2F36AE",
            "reason": "dynamic_examples_require_spaces_on_both_literal_edges",
        }
        for record_id, literal_id in (
            (834, 2), (1047, 0), (1464, 0), (2477, 1), (2481, 0),
            (2483, 1), (2486, 0), (2490, 0), (2492, 1), (2517, 0),
            (2525, 2), (2533, 1), (2552, 1),
        )
    },
    (15, 1670, 1): {
        "line_index": 1,
        "source_width_px": 216,
        "candidate_width_px": 288,
        "delta_px": 72,
        "candidate_utf16le_sha256":
            "25E9A924D71C5302B02CD79B93775A8E46DD5E87738D77B0196A7EED514E1134",
        "reason": "garbled_gajunge_restored_to_gamun_junge",
    },
    (17, 228, 1): {
        "line_index": 0,
        "source_width_px": 264,
        "candidate_width_px": 312,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "6BE46203215A42BBE85F924EBC9DC19207329D45313D157897C872531C3F119C",
        "reason": "dynamic_clan_side_phrase_requires_both_edge_spaces",
    },
    (17, 362, 0): {
        "line_index": 0,
        "source_width_px": 96,
        "candidate_width_px": 144,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "08ADF118DC0D1EB5E283234A053BF3B8213D8B4A89C815B0584462DC0D49A83A",
        "reason": "dynamic_person_bound_noun_requires_both_edge_spaces",
    },
    (2, 248, 2): {
        "line_index": 0,
        "source_width_px": 144,
        "candidate_width_px": 192,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "D31B9296E95F5D16CD55006A22F552D5CC2341634727E43122CCD1F0DDB41148",
        "reason": "dynamic_pronoun_after_seuseuro_requires_visible_spacing",
    },
    (8, 286, 0): {
        "line_index": 0,
        "source_width_px": 384,
        "candidate_width_px": 432,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "B7921E1298D16542F247CDCF5DB66A7E52DA3EBD9C1A469DB00A7962A314B85E",
        "reason": "malformed_crop_failure_predicate_restored_to_past_stem",
    },
    **{
        (8, record_id, 1): {
            "line_index": 0,
            "source_width_px": 744,
            "candidate_width_px": 816,
            "delta_px": 72,
            "candidate_utf16le_sha256":
                "E0FB5A4BCD29404A06E9335A0B80D1DFC05684C395A743C27B9355CCBDBAE3CC",
            "reason": "facility_edict_uses_complete_naerija_imperative",
        }
        for record_id in range(951, 963)
    },
    (15, 810, 0): {
        "line_index": 2,
        "source_width_px": 600,
        "candidate_width_px": 648,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "F0CA65E0C8929FAE829E4D5E8284E9EFB0F3A462478EA8017C214FA174722865",
        "reason": "malformed_guja_predicate_restored_to_guhaja_family",
    },
    (15, 1570, 1): {
        "line_index": 0,
        "source_width_px": 312,
        "candidate_width_px": 360,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "15DA112185EDCA7262F19749A437AF1DB4DB1D4BBBBD2208386D9782089B7ED2",
        "reason": "dynamic_jugun_topic_uses_complete_iyamallo_particle",
    },
    (15, 1832, 1): {
        "line_index": 1,
        "source_width_px": 456,
        "candidate_width_px": 624,
        "delta_px": 168,
        "candidate_utf16le_sha256":
            "292D2B69B53DD7CCC16E1AFF3FB45E8AF8850702D0D692B2DE4810D895F871EE",
        "reason": "malformed_got_irira_restored_to_got_orira",
    },
    **{
        (15, record_id, 0): {
            "line_index": 0,
            "source_width_px": source_width,
            "candidate_width_px": source_width + 96,
            "delta_px": 96,
            "candidate_utf16le_sha256": literal_sha256,
            "reason": "malformed_neul_haja_restored_to_neullija",
        }
        for record_id, source_width, literal_sha256 in (
            (
                1943,
                168,
                "E5D655871B32739DF096FBD73ECFA2B9FD1486EB8C8A2B88F2BF77DD8A95DCC5",
            ),
            (
                1948,
                216,
                "AE01D37BEBFBB14227DAB90604CDBB0E00CEB364D12E8F48680C2D2A7E75B340",
            ),
            (
                1952,
                336,
                "672650BEFA2BA379D8851F087C1F7D64681608877F93EF5ADE3773A27CEF28D4",
            ),
            (
                1955,
                216,
                "E82ACF50E74FF7C3B1395CB82041A6917AF7BC0467C78B896EDF9DC3BFF5E89F",
            ),
            (
                1960,
                216,
                "CA8EBD42275B88BEFB7370363F923D914933A6903B73DD7B602EE894B4B0502D",
            ),
        )
    },
    **{
        coordinate: {
            "line_index": line_index,
            "source_width_px": source_width,
            "candidate_width_px": candidate_width,
            "delta_px": candidate_width - source_width,
            "candidate_utf16le_sha256": literal_sha256,
            "reason": "reviewed_dynamic_predicate_reconstruction",
        }
        for (
            coordinate,
            line_index,
            source_width,
            candidate_width,
            literal_sha256,
        ) in (
            (
                (6, 3406, 0), 0, 264, 384,
                "1DE09B42318ACAF59FD9290E3529E78323F18EC915480A9866AB9751BAE72B97",
            ),
            (
                (6, 4248, 0), 1, 96, 216,
                "98A50287DC4DB311D566966B1F550600DB1D82EE3AE7C3924E4FE6D14262C497",
            ),
            (
                (6, 4689, 0), 0, 384, 504,
                "F4293A0BFC1115F809846445624533A9E667971DEF7A09700CD3E589152F5910",
            ),
            (
                (6, 4804, 2), 1, 264, 408,
                "AF48FAEC6255D06F3E2631314AE885E79C93E56B2207D79CC6CBE0FC7EFB73BA",
            ),
            (
                (6, 4876, 2), 0, 600, 720,
                "6CF4CA06AD699FAB08968EEB44CB0F16CA2B50370A41BC560861EC2E01E313FA",
            ),
            (
                (6, 4891, 2), 1, 216, 336,
                "1F9DF175C888E79A62042C859886A9C6C9C4B88A9959D2589F3AEDF7150B5222",
            ),
            (
                (6, 4938, 0), 0, 600, 720,
                "9DC81F7A6FC7CF52AAD0E575EA7464EA8873E2D7E07FBAA72C333D8152BE8640",
            ),
            (
                (7, 2482, 0), 1, 600, 720,
                "BA0878839B468F0C2BAD21CE64C513955772F8125E5CBE0144FF53890D18D8B5",
            ),
            (
                (7, 2484, 0), 0, 312, 384,
                "323A2B0461B0935828223FA9C64DDF1B99541D7A8747F7103C1AD0B776637875",
            ),
            (
                (7, 2490, 2), 0, 360, 408,
                "DB2376F21AA1A5AD0D0C4D88799469F6911C366FE683F4E099F1EBFA84553996",
            ),
            (
                (7, 2490, 3), 0, 96, 168,
                "F4A5030DD37F3B9D1773AD93D83D185318C86AFA2010E15587CCEB1EC157D7C0",
            ),
            (
                (8, 283, 0), 1, 264, 432,
                "A79D6B28536B987B93FF4BBD1A705123FFE9562EDC86632C343486BA7D68B42F",
            ),
            (
                (9, 3951, 0), 0, 432, 552,
                "785FCB7F3C1A69B0225191C504CF96EF054E95913498C4DBDFC86966108C4DAF",
            ),
            (
                (15, 255, 4), 0, 96, 168,
                "042FC1AE96CB2804854C5DBDB7F0688A28E4FBFE47C76EB25FB7DA19D7BB3C89",
            ),
            (
                (15, 361, 1), 1, 408, 480,
                "D4F93F26B34156C1BD4107318DFC3556C812E7ED19319BF88670F4857914E9FC",
            ),
            (
                (15, 758, 2), 1, 96, 216,
                "ED75F00272558EF034F02C849AB9D9730F993A585965993C52EB7698A2BAD644",
            ),
            (
                (15, 1440, 1), 1, 408, 480,
                "D4F93F26B34156C1BD4107318DFC3556C812E7ED19319BF88670F4857914E9FC",
            ),
            (
                (15, 1546, 4), 0, 96, 168,
                "F215394529AC7EE13B349CD9CA75252A05C09D655861EA19FE57CAF50D1EA920",
            ),
            (
                (15, 1572, 2), 0, 96, 168,
                "8BBDB5EF455791ED7A1D3A478AD1E984950BFB63D98F8B4029AF360A107149D2",
            ),
            (
                (15, 1574, 2), 0, 96, 168,
                "8BBDB5EF455791ED7A1D3A478AD1E984950BFB63D98F8B4029AF360A107149D2",
            ),
            (
                (15, 1576, 1), 0, 96, 168,
                "8BBDB5EF455791ED7A1D3A478AD1E984950BFB63D98F8B4029AF360A107149D2",
            ),
            (
                (15, 2184, 0), 1, 96, 216,
                "4B60541674A3DBD65365E3E29E7B6E8D6E9F7DFE8B9235BB96ED28B5F7826F48",
            ),
            (
                (15, 2462, 1), 1, 384, 504,
                "3FF79C531964CC53BD6889620D662C4D6F8CE73C1F00F10BB6ACCAC4FAD82078",
            ),
        )
    },
    (15, 1673, 0): {
        "lines": {
            0: {
                "source_width_px": 528,
                "candidate_width_px": 864,
                "delta_px": 336,
            },
            1: {
                "source_width_px": 600,
                "candidate_width_px": 792,
                "delta_px": 192,
            },
        },
        "candidate_utf16le_sha256":
            "823836B9C3C64952D6428222BBD2A94C12240846BCA2CE6987E5890B86636E14",
        "reason": "historically_verified_joto_policy_sentence_restored_exactly",
    },
    (2, 148, 0): {
        "line_index": 0,
        "source_width_px": 432,
        "candidate_width_px": 528,
        "delta_px": 96,
        "candidate_utf16le_sha256":
            "22EEFFBCDA36158D04EAF65FE38066CFD52BB89B89B51F3123D44DB5C6DDE2A4",
        "reason": "user_reported_exact_illness_notification",
    },
    (8, 1032, 1): {
        "line_index": 0,
        "source_width_px": 192,
        "candidate_width_px": 528,
        "delta_px": 336,
        "candidate_utf16le_sha256":
            "62A1E054B0EFC20A5183459A42E9B85B22988D74B1B3E889E0BAF6FA9182688E",
        "reason": "user_reported_exact_45_variant_illness_dialogue",
    },
    (15, 1545, 2): {
        "line_index": 0,
        "source_width_px": 432,
        "candidate_width_px": 480,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "2FA200445CC1E0D2BB617EB0ADA5C158181947847DE6641BFDF5DFB22CBD8FA5",
        "reason": "user_reported_exact_batchim_direction_particle",
    },
    (6, 3765, 1): {
        "line_index": 0,
        "source_width_px": 48,
        "candidate_width_px": 288,
        "delta_px": 240,
        "candidate_utf16le_sha256":
            "03EA3B48FBD071C9B5948D0BD37D834E8F8FD44CD1ADB9C76C04E4211550EE5F",
        "reason": "synthetic_clan_selector_envoy_relation",
    },
    (15, 1234, 1): {
        "line_index": 2,
        "source_width_px": 0,
        "candidate_width_px": 48,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "30B78A21EA791E8B4930001357CFF180D99BE0C33DB663B0F9540ED8DE1D8F87",
        "reason": "question_stem_precedes_single_runtime_question_terminal",
    },
    (7, 1714, 1): {
        "line_index": 1,
        "source_width_px": 600,
        "candidate_width_px": 648,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "66DCC5EF0E449AE30AF939C630BD67907B3716D121762D1A93A8E471D5CD1B58",
        "reason": "synthetic_castle_selector_object_particle_restored",
    },
    (8, 758, 0): {
        "line_index": 0,
        "source_width_px": 192,
        "candidate_width_px": 264,
        "delta_px": 72,
        "candidate_utf16le_sha256":
            "4530D93071844D218CF900688931537C8B7CD194CE130D476CF661AD50156BC6",
        "reason": "dynamic_facility_particle_neutral_case_carrier",
    },
    (8, 764, 0): {
        "line_index": 0,
        "source_width_px": 408,
        "candidate_width_px": 480,
        "delta_px": 72,
        "candidate_utf16le_sha256":
            "0CC17C0FF9A7C2CD755A5186870ED7FD5DFE60EC67A2841414BB1F4F23A5B11B",
        "reason": "dynamic_facility_particle_neutral_case_carrier",
    },
    (8, 766, 0): {
        "line_index": 0,
        "source_width_px": 192,
        "candidate_width_px": 264,
        "delta_px": 72,
        "candidate_utf16le_sha256":
            "0FC59E4C3992D4026261A01AD28004791D10CE72C3D416F1F6627EFB29B9B252",
        "reason": "dynamic_facility_particle_neutral_case_carrier",
    },
    (8, 1031, 0): {
        "line_index": 0,
        "source_width_px": 480,
        "candidate_width_px": 624,
        "delta_px": 144,
        "candidate_utf16le_sha256":
            "00E28A7E1931A1A6E2BC1ECCDD633D60F002048C299EE0021255466619016C07",
        "reason": "reviewed_fixed_illness_recovery_dialogue",
    },
    (8, 1031, 1): {
        "line_index": 1,
        "source_width_px": 168,
        "candidate_width_px": 504,
        "delta_px": 336,
        "candidate_utf16le_sha256":
            "1A2404DDD5F86BE6021E35708F8AE3622ABF519BDF49F9C87A7A2EE02908AF0D",
        "reason": "reviewed_fixed_illness_recovery_dialogue",
    },
    (8, 1031, 2): {
        "line_index": 0,
        "source_width_px": 240,
        "candidate_width_px": 600,
        "delta_px": 360,
        "candidate_utf16le_sha256":
            "3CE956EEB7AC8028B440C10E2F103FF63FC0BEAACABB763CF372C6A96CAA19D5",
        "reason": "reviewed_fixed_illness_recovery_dialogue",
    },
    (8, 1198, 0): {
        "line_index": 1,
        "source_width_px": 384,
        "candidate_width_px": 432,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "922E290DC261A2F4630C83982CAFCEBEADB5AFC9CA603B194322FDF307A22D0C",
        "reason": "past_report_boundary_requires_past_existential_stem",
    },
    (9, 1511, 0): {
        "line_index": 0,
        "source_width_px": 288,
        "candidate_width_px": 432,
        "delta_px": 144,
        "candidate_utf16le_sha256":
            "64DAB5DA61B6E482BAD0080A6E5D56A4F7D3729D7450B9FBE041D9CC34FDAAD2",
        "reason": "dynamic_address_particle_neutral_surprise_carrier",
    },
    (9, 1573, 0): {
        "line_index": 1,
        "source_width_px": 264,
        "candidate_width_px": 336,
        "delta_px": 72,
        "candidate_utf16le_sha256":
            "0B9A04F9CF96D00A4C0DA5B6C2F67D1F3BF5E0ABCEA7C61BA16FA0D388969EBA",
        "reason": "dynamic_address_particle_neutral_assignment_carrier",
    },
    (9, 1769, 0): {
        "line_index": 0,
        "source_width_px": 240,
        "candidate_width_px": 360,
        "delta_px": 120,
        "candidate_utf16le_sha256":
            "3F723671EC6DBDE260012C4D1287385DCB11D52D1776932D929109E39289FA2C",
        "reason": "dynamic_address_particle_neutral_opponent_carrier",
    },
    (9, 2408, 0): {
        "line_index": 0,
        "source_width_px": 240,
        "candidate_width_px": 432,
        "delta_px": 192,
        "candidate_utf16le_sha256":
            "DF3CEFB4C9C4C2C60F23DD9CC76E192A8EB3B4F128213C8AE63336C42319960B",
        "reason": "dynamic_subject_particle_neutral_news_carrier",
    },
    (15, 319, 1): {
        "line_index": 1,
        "source_width_px": 0,
        "candidate_width_px": 168,
        "delta_px": 168,
        "candidate_utf16le_sha256":
            "D78CE38D1B02519A3F1D8145254468C7BDD60BF7984D6166E583F8E828B1388C",
        "reason": "dynamic_person_particle_neutral_name_carrier",
    },
    (15, 325, 1): {
        "line_index": 1,
        "source_width_px": 0,
        "candidate_width_px": 168,
        "delta_px": 168,
        "candidate_utf16le_sha256":
            "B6786950827326CF7A2C084321AEA0D330FFB682CD58C5264A0123206D0AA260",
        "reason": "dynamic_person_particle_neutral_name_carrier",
    },
    (15, 326, 1): {
        "line_index": 1,
        "source_width_px": 0,
        "candidate_width_px": 168,
        "delta_px": 168,
        "candidate_utf16le_sha256":
            "B6786950827326CF7A2C084321AEA0D330FFB682CD58C5264A0123206D0AA260",
        "reason": "dynamic_person_particle_neutral_name_carrier",
    },
    **{
        coordinate: {
            "line_index": 0,
            "source_width_px": 360,
            "candidate_width_px": candidate_width_px,
            "delta_px": candidate_width_px - 360,
            "candidate_utf16le_sha256": digest,
            "reason": "dynamic_person_particle_neutral_self_introduction",
        }
        for coordinate, candidate_width_px, digest in (
            (
                (15, 355, 0),
                528,
                "B94DBF4B54AF39BC8D7BDE523134A84AE49128C6621F7727FC1D231B6E06A3A0",
            ),
            (
                (15, 358, 0),
                576,
                "1AD388995AE7AD393CD071132EC35E04F1889F4AB40749D6DCBE4B007B589086",
            ),
            (
                (15, 360, 0),
                480,
                "C5C0BD0705ABDE056C09DD8BFDAF47AE95E7DDE7CF754D486CF52F060DF13A04",
            ),
            (
                (15, 1416, 0),
                528,
                "B94DBF4B54AF39BC8D7BDE523134A84AE49128C6621F7727FC1D231B6E06A3A0",
            ),
            (
                (15, 1419, 0),
                576,
                "1AD388995AE7AD393CD071132EC35E04F1889F4AB40749D6DCBE4B007B589086",
            ),
            (
                (15, 1421, 0),
                480,
                "C5C0BD0705ABDE056C09DD8BFDAF47AE95E7DDE7CF754D486CF52F060DF13A04",
            ),
            (
                (15, 1434, 0),
                528,
                "B94DBF4B54AF39BC8D7BDE523134A84AE49128C6621F7727FC1D231B6E06A3A0",
            ),
            (
                (15, 1437, 0),
                576,
                "1AD388995AE7AD393CD071132EC35E04F1889F4AB40749D6DCBE4B007B589086",
            ),
            (
                (15, 1439, 0),
                480,
                "C5C0BD0705ABDE056C09DD8BFDAF47AE95E7DDE7CF754D486CF52F060DF13A04",
            ),
        )
    },
    (15, 440, 1): {
        "line_index": 0,
        "source_width_px": 360,
        "candidate_width_px": 576,
        "delta_px": 216,
        "candidate_utf16le_sha256":
            "59C1315F0D2BA49B24770D00057ED95055A6C01278FCE8E72D768A33F28EBAA9",
        "reason": "dynamic_person_particle_neutral_self_introduction",
    },
    (15, 445, 1): {
        "line_index": 0,
        "source_width_px": 360,
        "candidate_width_px": 576,
        "delta_px": 216,
        "candidate_utf16le_sha256":
            "2432C4AFB5B8E69140B3C48CEDEB3B63D95BB6D6D169C8F5183AE89E8502E6FF",
        "reason": "dynamic_person_particle_neutral_self_introduction",
    },
    **{
        coordinate: {
            "line_index": 0,
            "source_width_px": 456,
            "candidate_width_px": 624,
            "delta_px": 168,
            "candidate_utf16le_sha256":
                "DAE467EDBFA8A89C9392EC3011E169EC995B4C73518949074B88086283C59359",
            "reason": "dynamic_castle_particle_neutral_location_carrier",
        }
        for coordinate in ((15, 924, 2), (15, 929, 2))
    },
    (15, 2093, 0): {
        "line_index": 1,
        "source_width_px": 96,
        "candidate_width_px": 672,
        "delta_px": 576,
        "candidate_utf16le_sha256":
            "F244E83D4EE0381F603EE9191A8A37D318452EC8CE6190C0061024407BC9987B",
        "reason": "fixed_clan_particle_and_natural_target_selection",
    },
    (15, 2093, 2): {
        "line_index": 0,
        "source_width_px": 240,
        "candidate_width_px": 360,
        "delta_px": 120,
        "candidate_utf16le_sha256":
            "67DC8F7001F509BEB9EC44958B1B23B150C1E37A4192C554F60E01735B9C3B83",
        "reason": "dynamic_strategy_particle_neutral_carrier",
    },
    **{
        coordinate: {
            "line_index": line_index,
            "source_width_px": source_width_px,
            "candidate_width_px": candidate_width_px,
            "delta_px": candidate_width_px - source_width_px,
            "candidate_utf16le_sha256": digest,
            "reason": "reviewed_novel_cartesian_sentence_repair",
        }
        for (
            coordinate,
            line_index,
            source_width_px,
            candidate_width_px,
            digest,
        ) in (
            (
                (6, 3625, 1), 1, 168, 312,
                "4B480DE058082205BA4256F43053A66E2B1D2BDDF4BEC56CD843CDE796325A01",
            ),
            (
                (6, 3631, 1), 1, 96, 240,
                "C820601FFB04B912161CA51BD5AFDE5152D11740CC9971902CD160E4BFD6EC1A",
            ),
            (
                (6, 4444, 1), 2, 144, 240,
                "55A923E3683BF64F53CD6B09458B7F684A664AF2C3E2EB2872F5F275F6ECA53A",
            ),
            (
                (7, 2436, 0), 0, 288, 576,
                "B0D1F0351F7C767050699D73360AF8C3B74B347B635F2C62538DBB55D44BD273",
            ),
            (
                (7, 2436, 2), 0, 216, 408,
                "64B7BC4B0DBC769EB911A1131C504319CF31667AA3916CA46D0C615E26964205",
            ),
            (
                (9, 3945, 0), 0, 600, 672,
                "6F3D8F2DFEF33FA4DEF2FB3C40D304E3A3D328C341F8361003FD0CEF30D4CEF9",
            ),
            (
                (9, 3946, 0), 0, 600, 672,
                "6F3D8F2DFEF33FA4DEF2FB3C40D304E3A3D328C341F8361003FD0CEF30D4CEF9",
            ),
            (
                (9, 3990, 0), 1, 312, 504,
                "9457160042027A25CD6EDF69B004B5258C554566DA76EE503AF72E14DE31E636",
            ),
            (
                (15, 268, 2), 0, 576, 720,
                "90481058DFBBA173A3096C08FC8A48C82CCF066D7EFBC028A68D2CF6CA45B536",
            ),
            (
                (15, 1502, 1), 1, 360, 576,
                "B7BAE561A7FD6AC8E7A58E8A6B7C7C2981F8430C8A56C8CA1453E23C8A021763",
            ),
            (
                (15, 1502, 2), 1, 432, 528,
                "73823B77DAD39C8968EE8886F35CDF7A96B8C545B959706A6657A5AA88E3C2D0",
            ),
            (
                (15, 1541, 0), 0, 648, 792,
                "255F40ED38D136678AA22BBA92081474AB5F43B7DF6B3E5F6E7BCD6E4F658A68",
            ),
            (
                (15, 1541, 1), 1, 984, 1104,
                "EF23B4AF5A39E83032538485418290F54AEB2665E374EFCE3A694D6FB242ABF4",
            ),
            (
                (15, 1615, 1), 0, 480, 576,
                "CD313CD42592E7B1EFF9EA5FE5C843DE618DB4857DB2880FA2B823A4830E3124",
            ),
        )
    },
    **{
        coordinate: {
            "line_index": line_index,
            "source_width_px": source_width_px,
            "candidate_width_px": candidate_width_px,
            "delta_px": candidate_width_px - source_width_px,
            "candidate_utf16le_sha256": digest,
            "reason": "reviewed_prefinal_predicate_collision_repair",
        }
        for coordinate, line_index, source_width_px, candidate_width_px, digest
        in (
            (
                (2, 560, 1), 1, 552, 648,
                "F2296883478BF0A79F8108926B9D3D187026227E490B372581DE525214FAF0E0",
            ),
            (
                (6, 3555, 0), 0, 552, 696,
                "626DE1026F90967D9C2AFD1AA4ADEE87B3737A9C89D5D4119702F1CE52040CA5",
            ),
            (
                (6, 3555, 2), 0, 576, 744,
                "9C68B456E3605B70009D1342B7C8517A7B0C2C8C2C89693088FCDBD482FD2765",
            ),
        )
    },
    (15, 1359, 3): {
        "line_index": 0,
        "source_width_px": 504,
        "candidate_width_px": 552,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "687C571AC901B2B25E81F161A0BF8F214D43B2B928EC485DC061B2F28FF43409",
        "reason": "past_injury_boundary_requires_past_give_stem",
    },
    (6, 4468, 0): {
        "line_index": 0,
        "source_width_px": 504,
        "candidate_width_px": 720,
        "delta_px": 216,
        "candidate_utf16le_sha256":
            "CA20CAB94D2950F842CE735DCA00300B1740D666A7F28C9D470FE62B1188E8C0",
        "reason": "reviewed_impersonal_siege_expertise_sentence",
    },
    (6, 4468, 2): {
        "line_index": 0,
        "source_width_px": 48,
        "candidate_width_px": 528,
        "delta_px": 480,
        "candidate_utf16le_sha256":
            "78DDF37DDDBADA306C917DD2783082FE0C575E3794B749579B176281C6CB3383",
        "reason": "reviewed_impersonal_siege_expertise_sentence",
    },
    (2, 131, 2): {
        "line_index": 0,
        "source_width_px": 48,
        "candidate_width_px": 120,
        "delta_px": 72,
        "candidate_utf16le_sha256":
            "D34B7A6D8D228B88C219FD90D68D3F729468ED6061483F5F76222058587D95C3",
        "reason": "dynamic_persona_dative_command_boundary",
    },
    (2, 621, 0): {
        "line_index": 0,
        "source_width_px": 168,
        "candidate_width_px": 216,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "A30F04521CEADE8D934B86B44B7238332A98C599884EA3D24FD280C5D095B0A0",
        "reason": "reviewed_direct_person_title_boundary_spacing",
    },
    (6, 1639, 0): {
        "line_index": 0,
        "source_width_px": 48,
        "candidate_width_px": 96,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "DFCDD6A59C71F47374099B6EAF6FA2CE0C078F09DD23717C8ACAB534DB59D8D0",
        "reason": "reviewed_dynamic_person_pair_separator",
    },
    (6, 2449, 0): {
        "line_index": 0,
        "source_width_px": 72,
        "candidate_width_px": 120,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "E47B9645051ED3311E25117C2AB1E5E21E468FC788B8E66CA8727776B0F170EB",
        "reason": "reviewed_direct_person_title_boundary_spacing",
    },
    (6, 3409, 0): {
        "line_index": 0,
        "source_width_px": 192,
        "candidate_width_px": 336,
        "delta_px": 144,
        "candidate_utf16le_sha256":
            "3597966493D4B6B5292CF3827E38B5EBD605747E1C870CBA18847BD0AF785296",
        "reason": "reviewed_dynamic_reassurance_clause",
    },
    (6, 3454, 0): {
        "line_index": 0,
        "source_width_px": 216,
        "candidate_width_px": 432,
        "delta_px": 216,
        "candidate_utf16le_sha256":
            "8813E87B96A090622625C152227AC65BEDD6BCA89D352539AA9BB8C879FACC27",
        "reason": "reviewed_dynamic_merit_rank_relation",
    },
    (6, 3694, 0): {
        "line_index": 0,
        "source_width_px": 0,
        "candidate_width_px": 312,
        "delta_px": 312,
        "candidate_utf16le_sha256":
            "FF18D3C08F9742444432541CE055D855EDE892F2ED415DD68A6DF1B510E3A6C3",
        "reason": "reviewed_dynamic_pronoun_invariant_object_boundary",
    },
    (6, 4020, 0): {
        "line_index": 0,
        "source_width_px": 528,
        "candidate_width_px": 624,
        "delta_px": 96,
        "candidate_utf16le_sha256":
            "07AC409BC817588DCD429CED33BB0723B7FF4627459CA562D51CB478ABE6E72F",
        "reason": "reviewed_dynamic_siege_force_predicate",
    },
    (6, 4185, 1): {
        "line_index": 0,
        "source_width_px": 288,
        "candidate_width_px": 360,
        "delta_px": 72,
        "candidate_utf16le_sha256":
            "EFDF4BF0FBCD9A39E6DF050EB6F9DBE254AB2D945B190041D22DEF5211443880",
        "reason": "reviewed_dynamic_march_direction_boundary",
    },
    (6, 4186, 1): {
        "line_index": 0,
        "source_width_px": 288,
        "candidate_width_px": 360,
        "delta_px": 72,
        "candidate_utf16le_sha256":
            "EFDF4BF0FBCD9A39E6DF050EB6F9DBE254AB2D945B190041D22DEF5211443880",
        "reason": "reviewed_dynamic_march_direction_boundary",
    },
    (6, 4187, 1): {
        "lines": {
            0: {
                "source_width_px": 384,
                "candidate_width_px": 552,
                "delta_px": 168,
            },
            1: {
                "source_width_px": 96,
                "candidate_width_px": 168,
                "delta_px": 72,
            },
        },
        "candidate_utf16le_sha256":
            "7795BB7BB206AFE58B964F529F6432670327CE948E421FBD462DBAEFCE2890B7",
        "reason": "reviewed_dynamic_multidirectional_march_boundary",
    },
    (6, 4188, 1): {
        "lines": {
            0: {
                "source_width_px": 384,
                "candidate_width_px": 624,
                "delta_px": 240,
            },
            1: {
                "source_width_px": 120,
                "candidate_width_px": 192,
                "delta_px": 72,
            },
        },
        "candidate_utf16le_sha256":
            "C6DC5EC486F579374D702F1F8C87FD5A22B5AC1129D209723CB9AF0E56211524",
        "reason": "reviewed_dynamic_multidirectional_march_boundary",
    },
    (6, 4189, 1): {
        "lines": {
            0: {
                "source_width_px": 384,
                "candidate_width_px": 624,
                "delta_px": 240,
            },
            1: {
                "source_width_px": 120,
                "candidate_width_px": 192,
                "delta_px": 72,
            },
        },
        "candidate_utf16le_sha256":
            "C6DC5EC486F579374D702F1F8C87FD5A22B5AC1129D209723CB9AF0E56211524",
        "reason": "reviewed_dynamic_multidirectional_march_boundary",
    },
    (6, 4190, 2): {
        "line_index": 0,
        "source_width_px": 48,
        "candidate_width_px": 96,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "EB74759B7BC94B311AB07BE045D2242CA4D79D434D2B04872554CF5E30D133F9",
        "reason": "reviewed_dynamic_march_direction_boundary",
    },
    (6, 4191, 2): {
        "line_index": 0,
        "source_width_px": 48,
        "candidate_width_px": 168,
        "delta_px": 120,
        "candidate_utf16le_sha256":
            "54AE545B7AFDB241BBC75B2BD252247FDC5E446D557ED8A3D12E2A22DCEAF98B",
        "reason": "reviewed_dynamic_march_direction_boundary",
    },
    (6, 4192, 2): {
        "line_index": 0,
        "source_width_px": 48,
        "candidate_width_px": 168,
        "delta_px": 120,
        "candidate_utf16le_sha256":
            "54AE545B7AFDB241BBC75B2BD252247FDC5E446D557ED8A3D12E2A22DCEAF98B",
        "reason": "reviewed_dynamic_march_direction_boundary",
    },
    (6, 4193, 2): {
        "lines": {
            0: {
                "source_width_px": 96,
                "candidate_width_px": 216,
                "delta_px": 120,
            },
            1: {
                "source_width_px": 264,
                "candidate_width_px": 504,
                "delta_px": 240,
            },
        },
        "candidate_utf16le_sha256":
            "47D110AF28FDD825583B448E2804B2A74912DD70C2FDC31E6BF9456ACC54CEBE",
        "reason": "reviewed_dynamic_multidirectional_march_boundary",
    },
    (6, 4194, 2): {
        "lines": {
            0: {
                "source_width_px": 96,
                "candidate_width_px": 288,
                "delta_px": 192,
            },
            1: {
                "source_width_px": 264,
                "candidate_width_px": 504,
                "delta_px": 240,
            },
        },
        "candidate_utf16le_sha256":
            "0286E2BDEED198A4974FD0F71631B7194A1B3685B621ED59B75B79D76F6F8769",
        "reason": "reviewed_dynamic_multidirectional_march_boundary",
    },
    (6, 4195, 2): {
        "lines": {
            0: {
                "source_width_px": 96,
                "candidate_width_px": 288,
                "delta_px": 192,
            },
            1: {
                "source_width_px": 264,
                "candidate_width_px": 504,
                "delta_px": 240,
            },
        },
        "candidate_utf16le_sha256":
            "0286E2BDEED198A4974FD0F71631B7194A1B3685B621ED59B75B79D76F6F8769",
        "reason": "reviewed_dynamic_multidirectional_march_boundary",
    },
    **{
        (block_id, record_id, literal_id): {
            "line_index": line_index,
            "source_width_px": source_width_px,
            "candidate_width_px": candidate_width_px,
            "delta_px": candidate_width_px - source_width_px,
            "candidate_utf16le_sha256": literal_sha256,
            "reason": reason,
        }
        for (
            block_id,
            record_id,
            literal_id,
            line_index,
            source_width_px,
            candidate_width_px,
            literal_sha256,
            reason,
        ) in (
            (
                6, 4671, 1, 1, 336, 600,
                "7E79E44636EE6571A5B05FB60AACD2B66BDC712EAB17155DE12573C9A1B71103",
                "reviewed_negative_request_completion",
            ),
            (
                7, 284, 0, 0, 96, 144,
                "E9E7C0BA2BE3B5AB12149BED04531378CDB9EC286A802D8C567C8399B695716A",
                "reviewed_person_plural_title_boundary_spacing",
            ),
            (
                7, 386, 1, 0, 96, 144,
                "E9E7C0BA2BE3B5AB12149BED04531378CDB9EC286A802D8C567C8399B695716A",
                "reviewed_person_plural_title_boundary_spacing",
            ),
            (
                7, 2032, 0, 1, 96, 168,
                "483C8C2A5E5AEB47E576C8251CB59CC4DD5BEF666D3E423C011BDBBF5E109756",
                "reviewed_urgent_dynamic_attack_sentence",
            ),
            (
                7, 2032, 1, 0, 48, 312,
                "CE5F5E53FF42FFD09816F2BD96AFD6DDD75548DD3BBF8D2760D9B55D26019689",
                "reviewed_urgent_dynamic_attack_sentence",
            ),
            (
                7, 2490, 0, 0, 600, 792,
                "62C4F9F216F6B06658C340984F02ADA7BDA8DCB3839F5E56D1CF8D369C08C143",
                "reviewed_past_enemy_invasion_report",
            ),
            (
                7, 2600, 0, 0, 312, 504,
                "AB6CDEFA6A091A32A0A5365ED897EE172F60710AD1E340C18F57C584C33913D7",
                "reviewed_first_spear_claim",
            ),
            (
                8, 261, 1, 2, 408, 480,
                "5465F2AFF8724181F33713922AB785277FAF0B8948FCA25CBDFABCF2A7333B3F",
                "reviewed_progressive_harvest_predicate",
            ),
            (
                8, 264, 2, 1, 408, 480,
                "EC51B1FECDFED75FF23D6BFDA618729D3C85B25F652EAA63D977DB72E7FC8F1E",
                "reviewed_progressive_harvest_predicate",
            ),
            (
                8, 273, 1, 1, 888, 960,
                "B1A98068D2B846C52ABCD40AE4C3BE64E09E08BFFA2E5BDDC7ACF7E75FD58464",
                "reviewed_preparation_necessity_predicate",
            ),
            (
                8, 353, 0, 1, 480, 552,
                "C077FB537702D22D818A87DCD4197F5A97E5E64CAD2543213F6AFF2A3087C76E",
                "reviewed_progressive_typhoon_predicate",
            ),
            (
                8, 354, 0, 0, 672, 744,
                "4E194436DAA97D8FCF5E4289D78C314FE935DA6DFB78CFB3DA585B996BEC0243",
                "reviewed_progressive_typhoon_predicate",
            ),
            (
                9, 2104, 0, 0, 48, 288,
                "2824336B884E84089EF1580A51F322E6E25AEDF52ABBF59F5F64FBE7CF063CFB",
                "reviewed_self_assertion_sentence",
            ),
            (
                9, 2186, 1, 0, 48, 96,
                "40B2EAE654E3C8818A382ECA6316B89B8CB8FE748240FF66B6EBA5C43B1F93D8",
                "reviewed_dynamic_person_dative_boundary",
            ),
            (
                9, 2641, 0, 1, 48, 456,
                "A0A4322A76C4E7780D2B77BE63863695CCD6C28CD5B30EB1D689A93529A804A1",
                "reviewed_burial_threat_sentence",
            ),
            (
                9, 3967, 0, 0, 912, 1032,
                "CA5EAA1E4236D4ACCF31ED886E63FD3EF81124DE0E1A83053473CCC22BCC6724",
                "reviewed_unit_fatigue_report",
            ),
            (
                15, 320, 3, 0, 96, 432,
                "4C3067C4834EB9F46C20DCA3A46DFBDC6CB8BDD442876B59659A1E928CF062EC",
                "reviewed_dynamic_audience_request",
            ),
            (
                15, 321, 3, 0, 96, 432,
                "4C3067C4834EB9F46C20DCA3A46DFBDC6CB8BDD442876B59659A1E928CF062EC",
                "reviewed_dynamic_audience_request",
            ),
            (
                15, 703, 1, 1, 840, 936,
                "2FB7E23E1DE99AB3DF4FCF6C6246C3AE1797235C1C56B39D14AE1A9D09D361A0",
                "reviewed_force_incorporation_sentence",
            ),
            (
                15, 704, 1, 2, 96, 240,
                "9A847913BFB66707B88A5BFF887236E72F28F70612B0A0B58F70628DA0457A02",
                "reviewed_force_incorporation_sentence",
            ),
            (
                15, 1283, 2, 0, 432, 504,
                "5226A3ADDF799C6818B5BEFF369944A87496292DB736E52E98A0755619F3FB9B",
                "reviewed_progressive_defense_predicate",
            ),
            (
                15, 1572, 1, 0, 168, 240,
                "C6E07C0CC67E9D97C3D0BFF7C44DFA12A01B514630243A5A86E1B26847FE612A",
                "reviewed_dynamic_region_relation",
            ),
            (
                15, 1572, 4, 1, 408, 504,
                "37B21114B64A9FB67ABB1D1034689761BFD3B5346B6929B463278657B2B9C46A",
                "reviewed_dynamic_region_relation",
            ),
            (
                15, 1835, 0, 0, 816, 888,
                "97C72478D8B281FA2E1AFB822BA1874F5DB79AC24BFEBFE67CC81CF7F4DF905F",
                "reviewed_progressive_vassal_predicate",
            ),
            (
                15, 1858, 2, 1, 432, 504,
                "C58892812693334A404780225A179D842C04383F25E9DB9B0A2047BDE7BC7783",
                "reviewed_progressive_combat_predicate",
            ),
            (
                15, 1946, 0, 0, 216, 312,
                "AE01D37BEBFBB14227DAB90604CDBB0E00CEB364D12E8F48680C2D2A7E75B340",
                "reviewed_retainers_objective_sentence",
            ),
            (
                15, 1967, 0, 0, 576, 648,
                "CF7FB7CF62B0C5451AF8AC55FF8F084D408AFD066A249468C5745B676044F74A",
                "reviewed_progressive_mission_predicate",
            ),
            (
                15, 2407, 1, 1, 816, 888,
                "22B41125659733906F40B6A00D3C2ADA86065BCB895F83DE946C8D751C717503",
                "reviewed_progressive_force_balance_predicate",
            ),
            (
                15, 2441, 0, 1, 384, 576,
                "DBD0E6DC715391B197373800F4B70CB2876863B033FC3768D0FB407D64BC5498",
                "reviewed_officer_inactivity_report",
            ),
            (
                17, 381, 1, 0, 264, 312,
                "AD46E754D7DAA003F555F38E3BF751E428BC418ADBAAA5F30892319A61C6995F",
                "reviewed_person_title_boundary_spacing",
            ),
            (
                17, 664, 2, 0, 96, 144,
                "E0B85B164C33E19DF83C440C8EB43166BE24E5F1332B31893192AA8EE7B327E7",
                "reviewed_person_title_boundary_spacing",
            ),
            (
                17, 721, 1, 0, 96, 144,
                "E0B85B164C33E19DF83C440C8EB43166BE24E5F1332B31893192AA8EE7B327E7",
                "reviewed_person_title_boundary_spacing",
            ),
            (
                17, 763, 0, 0, 96, 144,
                "E0B85B164C33E19DF83C440C8EB43166BE24E5F1332B31893192AA8EE7B327E7",
                "reviewed_person_title_boundary_spacing",
            ),
            (
                17, 777, 2, 0, 96, 144,
                "E0B85B164C33E19DF83C440C8EB43166BE24E5F1332B31893192AA8EE7B327E7",
                "reviewed_person_title_boundary_spacing",
            ),
            (
                17, 847, 1, 0, 312, 360,
                "2F6481C27118557DFD53CD36A84BE633441930166CF13B81B127933306AEB320",
                "reviewed_person_title_boundary_spacing",
            ),
        )
    },
    (8, 936, 1): {
        "line_index": 0,
        "source_width_px": 192,
        "candidate_width_px": 240,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "716533848D9BD72AB0D3F0070B585E08ADA6053DD0A920610B26214979D4D3EF",
        "reason": "reviewed_dependent_arae_boundary_spacing",
    },
    (8, 941, 1): {
        "line_index": 0,
        "source_width_px": 144,
        "candidate_width_px": 192,
        "delta_px": 48,
        "candidate_utf16le_sha256":
            "1E4543FA32FA3829FF781728D481826231CF78EE07D7105FED63450868710445",
        "reason": "reviewed_dependent_arae_boundary_spacing",
    },
    **{
        (17, record_id, literal_id): {
            "line_index": 0,
            "source_width_px": 144,
            "candidate_width_px": 192,
            "delta_px": 48,
            "candidate_utf16le_sha256":
                "486E20537F58AA2A33D266D3212AC334D0AFDE63F8C05C7600DBB65F4D2F6782",
            "reason": "reviewed_unit_boundary_spacing_on_both_edges",
        }
        for record_id, literal_id in (
            (317, 0), (318, 0), (319, 0),
            (962, 1), (963, 1), (964, 1),
            (1014, 0), (1015, 0), (1016, 0),
            (1020, 0), (1021, 0), (1022, 0),
        )
    },
    **{
        (17, record_id, 0): {
            "line_index": 0,
            "source_width_px": 144,
            "candidate_width_px": 192,
            "delta_px": 48,
            "candidate_utf16le_sha256":
                "555E5BD86CABD066C614792E6FC74F5C6514980612B96BFF971F32F99305F9ED",
            "reason": "reviewed_unit_boundary_spacing_on_both_edges",
        }
        for record_id in (
            529, 530, 531, 532,
            736, 737, 738,
            796, 797, 798,
            1037, 1038, 1039,
        )
    },
    **{
        (17, record_id, 0): {
            "line_index": 0,
            "source_width_px": 144,
            "candidate_width_px": 192,
            "delta_px": 48,
            "candidate_utf16le_sha256":
                "D1C5BEAECB3F7D0B02263F9B88477A9B762EA52401634F84BFEDAEBE55BEAFD4",
            "reason": "reviewed_unit_boundary_spacing_on_both_edges",
        }
        for record_id in (694, 695, 697, 698, 699, 700)
    },
    **{
        (15, record_id, 2): {
            "line_index": 0,
            "source_width_px": 336,
            "candidate_width_px": 408,
            "delta_px": 72,
            "candidate_utf16le_sha256":
                "7082D596D1D7721F3EC4AAB08C615F7FD323EC805BD7E4EB6F0268C0497FEB3A",
            "reason": "reviewed_dynamic_relation_invariant_service_boundary",
        }
        for record_id in (320, 321)
    },
    **{
        coordinate: {
            "line_index": 0,
            "source_width_px": source_width_px,
            "candidate_width_px": candidate_width_px,
            "delta_px": candidate_width_px - source_width_px,
            "candidate_utf16le_sha256": literal_sha256,
            "reason":
                "reviewed_dynamic_general_boundary_spacing_on_both_edges",
        }
        for (
            coordinate,
            source_width_px,
            candidate_width_px,
            literal_sha256,
        ) in (
            *(
                (
                    coordinate,
                    48,
                    96,
                    "F704BA605676C22BF9EA6F0BE820C7CF35DAA3E1D1D1EF8E64E3D614CA2F36AE",
                )
                for coordinate in (
                    (2, 151, 0),
                    (6, 4083, 0), (6, 4090, 0), (6, 4145, 2),
                    (6, 4320, 1), (6, 4322, 1),
                    (8, 424, 0), (8, 426, 1), (8, 917, 0),
                    (8, 989, 1),
                    (9, 406, 0), (9, 412, 0), (9, 460, 0),
                    (9, 462, 0), (9, 469, 0), (9, 473, 0),
                    (9, 478, 0), (9, 480, 1), (9, 485, 0),
                    (9, 489, 0), (9, 491, 0),
                    (15, 721, 0), (15, 1492, 1),
                )
            ),
            ((6, 4609, 2), 96, 144, "B9D805CA8A6D6C95A82C1D7473D8B5FD2EE90881BDFC419A2F072652DABF5910"),
            ((6, 4611, 2), 96, 144, "B9D805CA8A6D6C95A82C1D7473D8B5FD2EE90881BDFC419A2F072652DABF5910"),
            ((15, 324, 0), 120, 168, "C7B904B5312E89DB0AC7CE66E2DC46CA712267754B99BD1C44D7405E805FD49D"),
            ((15, 487, 0), 384, 432, "3A6E076A60742DA213DE0000DD5ABCC2A4D531229DBE26CE762A5E34EC808821"),
            ((15, 2303, 1), 96, 144, "7859DAA2DB1F4378759F9037763D9DCADEF868E6078465E0607D20AE9727A6C2"),
            ((15, 2304, 1), 96, 144, "7859DAA2DB1F4378759F9037763D9DCADEF868E6078465E0607D20AE9727A6C2"),
            ((15, 2305, 1), 96, 144, "7859DAA2DB1F4378759F9037763D9DCADEF868E6078465E0607D20AE9727A6C2"),
            ((15, 2307, 1), 96, 144, "7859DAA2DB1F4378759F9037763D9DCADEF868E6078465E0607D20AE9727A6C2"),
            ((15, 2504, 2), 168, 216, "CA1334D45824088DB0FFC344022BD6BCC17A0DCE3A10F0DA1408153A4DDAD227"),
            ((15, 2505, 2), 168, 216, "CA1334D45824088DB0FFC344022BD6BCC17A0DCE3A10F0DA1408153A4DDAD227"),
            ((15, 2511, 1), 168, 216, "CA1334D45824088DB0FFC344022BD6BCC17A0DCE3A10F0DA1408153A4DDAD227"),
            ((17, 277, 1), 288, 336, "F0099C37CCFBEFF61276440F2CE4456B166481F68654F08C3E6F8DD98EBA6645"),
            ((17, 642, 1), 480, 528, "A42952B77A56D548494DF6556EFF049F482E62508719FE737A9840D21C0B6CE3"),
            ((17, 678, 0), 240, 288, "1B820B7444050CD1FA2BEDBE6E416491B0AE46A543A7375261273433482ECEE9"),
            ((17, 807, 0), 240, 288, "1B820B7444050CD1FA2BEDBE6E416491B0AE46A543A7375261273433482ECEE9"),
            ((17, 706, 0), 120, 168, "6591339BADFE7905C743D7F67C193297A19D70391D367AFBD05A23ED575B64B6"),
            ((17, 707, 1), 120, 168, "6591339BADFE7905C743D7F67C193297A19D70391D367AFBD05A23ED575B64B6"),
            ((17, 864, 1), 120, 168, "6591339BADFE7905C743D7F67C193297A19D70391D367AFBD05A23ED575B64B6"),
        )
    },
    **{
        coordinate: {
            "line_index": 0,
            "source_width_px": source_width_px,
            "candidate_width_px": candidate_width_px,
            "delta_px": candidate_width_px - source_width_px,
            "candidate_utf16le_sha256": literal_sha256,
            "reason": reason,
        }
        for (
            coordinates,
            source_width_px,
            candidate_width_px,
            literal_sha256,
            reason,
        ) in (
            (((2, 639, 0),), 96, 144, "525C65D6BC3856E1F161F466F792DFB77ED12EEF1BB5F095255306BBF473D528", "reviewed_exhaustive_dynamic_boundary_spacing"),
            (((6, 3874, 0),), 264, 312, "33381776EAA22C7EF85BF676182749F8B689F6CC5C61883097D1F48DDB704B5D", "reviewed_exhaustive_dynamic_boundary_spacing"),
            (((6, 4107, 0),), 792, 840, "C775C76CE836F6E84A7304A0B94623A7DEF5EA86FB9B4898FA9E220180B9BEA1", "reviewed_exhaustive_dynamic_boundary_spacing"),
            (((6, 4108, 0),), 744, 792, "21DC586E20DBBF32FFC644E06B88360094DDEFEE321DB2ADA371E268D11CDFF4", "reviewed_exhaustive_dynamic_boundary_spacing"),
            (((6, 4906, 0),), 768, 960, "BE88CA586733A64D9317CFD164414C8199AFA9F4CF27923A5362EEA3FA37B701", "reviewed_exhaustive_dynamic_semantic_reconstruction"),
            (((7, 701, 0), (7, 767, 1)), 216, 288, "5B8927EF34141A9ADA014A6BC758C8B2BB59881D6DD8B518F645B6195297FDD1", "reviewed_exhaustive_dynamic_particle_reconstruction"),
            (((7, 1025, 0), (7, 1026, 0), (7, 1033, 0), (7, 1035, 0), (7, 1045, 0)), 624, 768, "DE1514E24FDC1297A6394E0A50D8525EC6513FD23A4AE73AFCD46A69DBECDCC9", "reviewed_exhaustive_dynamic_relation_reconstruction"),
            (((7, 1037, 0), (7, 1047, 0)), 624, 768, "092F979173794578397860AC42F1EDFCB8D08EB9660FAA8B712C506B519B2BCD", "reviewed_exhaustive_dynamic_relation_reconstruction"),
            (((7, 2023, 0),), 216, 264, "91E6AB923E485390D7D5B735E7D5AAA4B610E93D9239359C3BA62A7475866AE2", "reviewed_exhaustive_dynamic_punctuation_reconstruction"),
            (((7, 2031, 1),), 216, 264, "7D80361FAFA1BA1A65B20E0A6FE6108E99E064BD6469D6A71863A66925D36127", "reviewed_exhaustive_dynamic_punctuation_reconstruction"),
            (((7, 2851, 1), (15, 832, 2), (15, 2548, 1)), 96, 144, "7E2243BDCCFE10451177CCA37A2D1FF327A73270CD62320484A327554C80F4FC", "reviewed_exhaustive_dynamic_boundary_spacing"),
            (((9, 3570, 1),), 312, 504, "DB5F2D1A65AB29F1760614A180F69AB8FB49D1A566588CF2DF3D068B920B5675", "reviewed_exhaustive_dynamic_semantic_reconstruction"),
            (((9, 3572, 1),), 384, 624, "0EDF235B1D4DC57774E476F322B67CB6259C91A9EF2E2007B39CAE92253E5641", "reviewed_exhaustive_dynamic_semantic_reconstruction"),
            (((9, 3573, 1), (9, 3576, 1)), 360, 552, "2878CBEC20FF5A40EBA317504377570B62DE4A800ECDD18E43FB1ED74A83ECAA", "reviewed_exhaustive_dynamic_semantic_reconstruction"),
            (((9, 3575, 1),), 528, 888, "B265D4E97FE8BB116CC3E8985C55378C9687AD6E9A2DD6D794073F76E29F24F8", "reviewed_exhaustive_dynamic_semantic_reconstruction"),
            (((9, 3578, 1), (9, 3580, 1)), 360, 552, "DD22EBC7946A8286619503ACA1C375D8590B6FE8DDA82CBA11D99387B7803EBE", "reviewed_exhaustive_dynamic_semantic_reconstruction"),
            (((9, 3579, 1),), 480, 840, "4AA00C34C4B85C0A8FC20302D5E16B49DFEF7BEE31908BE7733C4D669A813670", "reviewed_exhaustive_dynamic_semantic_reconstruction"),
            (((9, 4120, 0),), 192, 240, "BBF50D0AF6E6D441C2B567A24FA74819917ECC67538D2DF8C3BE0ECB9AAD1702", "reviewed_exhaustive_dynamic_punctuation_reconstruction"),
            (((9, 4125, 0),), 360, 552, "001C7FC4B14B93CA1D2AC9FBFAFFA6BD23217DF438EF211088BE3DCE20453493", "reviewed_exhaustive_dynamic_semantic_reconstruction"),
            (((15, 777, 3), (15, 778, 3)), 336, 384, "56C4189EE6CE155B8AA2B8AA0CC68DEB4D82AFFF351E63F25A0A79DA43CF3980", "reviewed_exhaustive_dynamic_boundary_spacing"),
            (((15, 1131, 1),), 144, 192, "6838536D359216B439AA8BA8383AB513CB35BC65749216A5B103F9DBBB07C143", "reviewed_exhaustive_dynamic_boundary_spacing"),
            (((15, 2067, 1), (15, 2151, 1)), 144, 216, "BC0DA056B9F22653DDE8CDC265337D8F445FE7597DBBBA599CA7BC25EC0C7FC4", "reviewed_exhaustive_dynamic_particle_reconstruction"),
            (((17, 272, 0),), 120, 168, "8F2EFEAB83AF33BB53A6C84DC809BAA23B53BB7195FDC5C75BAF1602B4D53870", "reviewed_exhaustive_dynamic_boundary_spacing"),
            (((17, 948, 0),), 504, 552, "DC74368FB3398EE58801DDFF38CEEBD40DCF428C5C70B0C19EFC0F8981F673F1", "reviewed_exhaustive_dynamic_punctuation_reconstruction"),
        )
        for coordinate in coordinates
    },
}
EXPECTED_EMPTY_TERMINAL_DATA_HEX = "070701070702050505"
SCHEMA = "nobu16.kr.pk-runtime-surface-remediation.v1"
OVERLAY_SCHEMA = "nobu16.kr.pk-runtime-surface-remediation-row.private.v1"
PRIORITY_SCHEMA = "nobu16.kr.pc-dialogue-runtime-surface-overlay.v1"

sys.path[:0] = [
    str(REPO / "workstreams" / "msggame"),
]

from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_packed_with_literals,
)


class PkRemediationError(ValueError):
    """Raised when a PK remediation invariant cannot be proved."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PkRemediationError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


QA = load_module("pc_dialogue_runtime_surface_qa_for_pk_remediation", QA_PATH)
TERMINAL = load_module(
    "pc_dialogue_terminal_boundary_for_pk_remediation",
    TERMINAL_DETECTOR_PATH,
)
os.environ["NOBU16_PK_ONLY_STRUCTURE_AUDIT"] = "1"
STRUCTURE = load_module(
    "pc_dialogue_candidate_structure_for_pk_remediation",
    STRUCTURE_AUDIT_PATH,
)
os.environ.pop("NOBU16_PK_ONLY_STRUCTURE_AUDIT", None)
RELATIVE_WIDTH = load_module(
    "pc_dialogue_candidate_width_for_pk_remediation",
    RELATIVE_WIDTH_AUDIT_PATH,
)

DUAL_TOKENS = tuple(sorted(QA.DUAL_PARTICLES, key=len, reverse=True))
DUAL_RE = re.compile("|".join(re.escape(value) for value in DUAL_TOKENS))
LEADING_FIXED_RE = re.compile(
    r"^(?P<particle>으로|이|가|은|는|을|를|와|과|로)"
    r"(?P<rest>[\s\S]*)"
)
FIXED_BATCHIM_CONTRACTS = frozenset({(3, 0x32), (4, 0x32)})
FIXED_BATCHIM_PARTICLE = {
    "subject": "이",
    "topic": "은",
    "object": "을",
    "comitative": "과",
    "directional": "으로",
}
DUAL_PARTICLE_BY_KIND = {
    "subject": "이(가)",
    "topic": "은(는)",
    "object": "을(를)",
    "comitative": "와(과)",
    "directional": "(으)로",
}

# Carrier nouns are used only when the selector's final sound is genuinely
# variable.  The carrier always owns an explicit Korean particle.
CARRIER_BY_GROUP = {
    0: "수치",
    2: "본인",
    3: "거점",
    4: "측",
    5: "본인",
    6: "부대",
    7: "지역",
    8: "지점",
    12: "수치",
    13: "수치",
    14: "조건",
}

# High-frequency semantic recasts are applied before the carrier fallback.
# They preserve the relation while avoiding needlessly repetitive ``장수가``
# or ``쪽이`` constructions.
DYNAMIC_PHRASE_REWRITES = (
    ("이(가) 몸소", "도 몸소"),
    ("이(가) 제안한", " 측이 제안한"),
    ("이(가) 탄생", "의 탄생"),
    ("이(가) 사망", "의 사망"),
    ("이(가) 부상", "의 부상"),
    ("이(가) 전사", "의 전사"),
    ("이(가) 출분", "의 출분"),
    ("이(가) 병력", " 측 병력"),
    ("이(가) 지닌", " 소유의"),
    ("이(가) 벌인", " 측이 벌인"),
    ("은(는) 강대하여", " 측이 강대하여"),
    ("은(는) 강대해", " 측이 강대해"),
    ("와(과)의 동맹", " 측과의 동맹"),
    ("와(과)의 정전", " 측과의 정전"),
    ("와(과) 함께", " 측과 함께"),
    ("을(를) 비롯한", " 측을 비롯한"),
    ("을(를) 비롯해", " 측을 비롯해"),
    ("(으)로의 행군로", " 쪽 행군로"),
    ("(으)로 향", " 쪽으로 향"),
    ("㌣(으)로", "㌣ 키로"),
    ("㌦(으)로", "㌦ 키로"),
)

# The surface detector also follows selectors through closing quotes,
# parentheses, and line breaks.  These reviewed rewrites preserve that wrapper
# while expressing the relation with a predicate or semantic noun whose
# particle does not depend on the selector's final sound.
COORDINATE_SELECTOR_FIXED_REWRITES = {
    (2, 661, 2): ") 완성까지\n앞으로",
    (2, 662, 2): ")」 발령까지\n앞으로",
    (4, 78, 1): "」 실행이 가능해졌습니다",
    (6, 2065, 1): "」도\n계속하기 어려워졌으니\n다시 지침을 내려 주시겠습니까",
    (6, 2066, 1): "」도\n더 이상 유지할 수 없습니다.\n방침을 다시 검토해 주십시오!",
    (6, 2070, 1): "」도\n계속하기 어려워졌습니다.\n새 방침을 지시해 주시겠습니까?",
    (6, 2071, 1): "」도\n더는 이어 갈 수 없사옵니다\n새 지침을 내려 주시옵소서",
    (6, 2080, 1): "」 등\n",
    (6, 4323, 2): ")\n발령 완료",
    (6, 4324, 2): ")\n발령 완료",
    (6, 4442, 1): "」 발령 후 지을 수 있는\n",
    (7, 799, 1): "」을 함락했",
    (7, 1701, 2): "\n을 빼앗아야 합니다",
    (8, 522, 1): "」에 진입",
    (8, 523, 1): "」에 후퇴",
    (8, 525, 1): "」에 개발 착수",
    (8, 526, 1): "」에 개발 완료",
    (8, 929, 1): ") 획득",
    (8, 930, 1): ") 획득",
    (8, 1006, 2): "」 설치해\n첫발로 선택",
    (9, 3889, 3): "」 따라라!",
    (12, 64, 3): ")도 귀환했습니다\n남은",
    (12, 65, 2): ")도 귀환했습니다\n남은",
    (12, 66, 3): ")도 귀환했습니다",
    (12, 67, 2): ")도 귀환했습니다",
    # Pristine JP has 「...」に: this is the destination diplomacy posture,
    # not an object whose Korean final sound is statically known.
    (15, 1133, 2): "」 쪽",
    (15, 1557, 2): "」도 쉽게 속지 않겠",
    (17, 991, 1): "\n도 궁지로 몰아넣는다!",
}

# ``및`` is not a Korean substitute for a postposition.  These exact
# predecessor comitative boundaries are recast around a relation or action
# that remains grammatical regardless of the runtime value's final sound.
SEMANTIC_COMITATIVE_REWRITES = {
    (2, 121, 0):
        " 계통의 피가 없어\n출가할 공주가 있습니다. 계속하시겠습니까?",
    (6, 734, 1): "에\n필적한다고 여기셨는가",
    (6, 3630, 0): ",\n",
    (7, 2881, 1): "에 맞서,\n",
    (9, 415, 1): ", 교대",
    (15, 544, 1):
        " 측과 당가는 친밀하옵니다\n허나 복종에는 한걸음 더 필요하옵니다\n"
        "이번 회유로 그들을 복종시킬 수 있사옵니다",
    (15, 546, 1):
        " 쪽과 우호적이옵니다\n허나 완전하다 할 수 없사옵니다\n"
        "회유를 더 진행함이 좋겠사옵니다",
    (15, 548, 1):
        " 쪽과 우호적이옵니다\n한 번 더 나아가면\n당가에 편입할 수 있사옵니다",
    (15, 549, 1):
        " 쪽과 우호적입니다\n아직 심복한 것은 아닙니다\n"
        "회유를 더해 확실히 다져야 합니다",
    **{
        (15, record_id, 1):
            " 쪽과 당가는 우호적이나\n휘하에 들길 거부하는 자가 있다 하옵니다\n"
            "국인중을 편입하려면 한 번 더 회유해야 하옵니다"
        for record_id in range(580, 586)
    },
    (15, 1473, 1):
        " 쪽을 주군과 갈라\n이반으로 이끄는 것도 좋은 계책",
    (17, 69, 0): "에 접근해 도발하라",
    (17, 70, 0): "에 접근해 도발하라",
    (17, 71, 0): "에 접근해 도발하라",
    (17, 160, 1):
        "에게 일격을 갚고 쓰러지겠다\n전군, 진격하라!",
    (17, 962, 2): "에 접근시켜라",
    (17, 963, 2): "에 접근시켜라",
    (17, 964, 2): "에 접근시켜라",
}

SEMANTIC_ADDITIVE_REWRITES = {
    (1, 24, 0): "만 지면 물구나무서서 알몸으로 마을을 한 바퀴 돌고",
    (2, 95, 1): " 무장 원복 완료",
    (2, 98, 1): " 성년을 맞았습니다",
    (2, 122, 1): "만큼은 당가를 키워!",
    (2, 124, 1): "만 당가를 지키겠소",
    (2, 126, 1): "만 당가를 패자로 만들겠소",
    (2, 133, 2): ":\n당주",
    (2, 140, 1): "만 이 가문을 지켜내겠습니다",
    (2, 142, 1): "만 목숨을 걸고\n반드시",
    (2, 211, 0): " 함락 ",
    (2, 255, 1): ": 특기 분야",
    (2, 320, 1):
        "만 농사에 밝습니다!\n"
        "제 지식으로 영지를 풍요롭게 하겠습니다",
    (2, 332, 0):
        "만 자랑하는 기마대의 위력을,\n천하에 보일 때다!",
    (2, 444, 1): "만\n이 가문의 병사들을 훈련해 주겠다!",
    (2, 618, 1): "만 믿어 주십시오!",
    (2, 620, 1): "에게 맡기실 일이 있다면 무엇이든…",
    (2, 629, 1): "만 나선다",
    (2, 631, 1): "만이 열 새 시대에 네놈은 필요 없다",
    (6, 823, 0): ", 동석인가…\n모두 가문을 위해서다",
    (6, 824, 0): " 따위 인정하지 못할\n작은 그릇이 아니다",
    (6, 834, 1): ",\n한자리에 앉다니",
    (6, 839, 1): ", 동석 따위…",
    (6, 1638, 1): "·\n",
    (6, 1643, 1):
        ",\n정치 따위 생각지 말고 행복해지길 바랄 뿐입니다.\n"
        "두 가문이 싸운다면… 생각하고 싶지도 않습니다",
    (6, 2065, 1):
        "」\n지속이 어려워졌으니\n다시 지침을 내려 주시겠습니까",
    (6, 2066, 1):
        "」\n더는 유지할 수 없습니다.\n"
        "방침을 다시 검토해 주십시오!",
    (6, 2070, 1):
        "」\n지속이 어려워졌습니다.\n새 방침을 지시해 주시겠습니까?",
    (6, 2071, 1):
        "」\n더는 이어 갈 수 없사옵니다\n새 지침을 내려 주시옵소서",
    (6, 3034, 1):
        " 편은 이만큼 양보한 것이다\n설마 거절하지는 않겠지",
    (6, 3113, 1): ": 출분",
    (6, 3114, 0): ": 출분",
    (6, 3368, 2): ": 추방하다니…!",
    (6, 3431, 1):
        "만 1위인가요……\n부끄럽지만 매우 영광입니다.\n올해도",
    (6, 3454, 1):
        "이 삼가 받았소이다!\n한 방면을 맡은 장수에 걸맞은 활약을\n"
        "해냈다는 뜻이겠지요",
    (6, 3472, 2): "만큼은 차지해야 하지 않겠느냐!\n모두,",
    (6, 3472, 3): "처럼 본받을 것이다!",
    (6, 3523, 0): "만 훈공 1위",
    (6, 3542, 1): " 자리는 할 일이 많으니\n활약은 당연한 일",
    (6, 3554, 2): "엔\n뒤지지 ",
    (6, 3587, 0): "만 위해 ",
    (6, 3589, 2): " 자리라곤\n생각지도 못했겠지",
    (6, 3689, 0): "만 ",
    (6, 3765, 2): "의\n도착",
    (6, 3883, 2): " 완공되면\n당가에 이로움이 되",
    (6, 4066, 0): " 병력 ",
    (6, 4067, 1): " 병력 ",
    (6, 4078, 0): " 병력 ",
    (6, 4079, 0): " 병력 ",
    (6, 4122, 2): ": 부상",
    (6, 4321, 1): " 파괴",
    (6, 4489, 1): "만 다소 자신이…\n모두의 힘을 키우",
    (6, 4613, 2): " 만나러 오신 것",
    (6, 4617, 1): " 만나러\n",
    (6, 4769, 1): ", 좋은 합의를",
    (6, 4818, 1): "만\n",
    (6, 4905, 1):
        ": 추방한다니…\n이 가문을 위해 힘써 왔건만…",
    (6, 4929, 2): "엔 남을 이유는 ",
    (7, 196, 1): ":\n나왔으니 사로잡읍시다",
    (7, 492, 0): " 궤멸, ",
    (7, 819, 1): " 해산",
    (7, 874, 0): " 병력이 성에 온다\n어서 기병에 대비하",
    (7, 877, 1): "」 출현인가……!\n",
    (7, 891, 0):
        " 병력이, 이런 곳까지!\n죽음도 모르는 거친 무사들에게\n"
        "어찌 맞서",
    (7, 1037, 1):
        "만 싸울 때를 잘못 판단했을지도 모른다\n"
        "이 피해로 한동안 싸우기는 어렵겠군…",
    (7, 1047, 1):
        "만 싸울 때를 잘못 판단했을지도 모른다\n"
        "이 피해로 한동안 싸우기는 어렵겠군…",
    (7, 2595, 1): ": 전사",
    (7, 2605, 1):
        "만 세웠다\n충의를 위해 죽음도 마다않는\n무사의 혼을 보시오!",
    (7, 2608, 2): "처럼 싸워라\n범 같은 군대가 되리라",
    (7, 2719, 1): "만 선봉인가!\n내 일처럼 기쁘구나!",
    (7, 2881, 2): "만 다치고 군세도 괴멸했습니다!",
    (8, 245, 1): ":\n",
    (8, 254, 1): ":\n",
    (8, 256, 1): ":\n",
    (8, 377, 1): ": 발전했습니다",
    (8, 404, 0): " 또 납득",
    (8, 427, 1): ": 탄생",
    (8, 429, 1): ": 탄생",
    (8, 430, 1): ": ",
    (8, 432, 1): ": ",
    (8, 433, 2): ": 탄생",
    (8, 436, 1): ": 탄생",
    (8, 437, 1): ": 탄생",
    (8, 439, 2): ": 탄생",
    (8, 440, 1): ": ",
    (8, 444, 0): ": ",
    (8, 447, 1): ": 사망",
    (8, 448, 1): ": 사망",
    (8, 450, 1): ": 사망",
    (8, 451, 1): ": 사망",
    (8, 590, 2): "만 지켜봐 주셨던 것이로군요!",
    (8, 932, 0): ": 승진하여",
    (8, 1029, 2): "만 이 땅을 맡",
    (8, 1196, 0):
        ": 제법 번성했으나\n역참을 더 정비하면\n"
        "천하에 이름날 것입니다",
}

EXPECTED_SEMANTIC_ADDITIVE_EARLY_REWRITE_COUNT = 93
EXPECTED_SEMANTIC_ADDITIVE_EARLY_COORDINATE_SHA256 = (
    "163575FD01E1CAE5341AED1AA641838482FB860260953C3AA60FFD7D8A14C188"
)
EXPECTED_SEMANTIC_ADDITIVE_TOTAL_REWRITE_COUNT = 221

SEMANTIC_ADDITIVE_LATE_REWRITES = {
    (9, 416, 0): "의 궤주",
    (9, 417, 0): "의 궤주",
    (9, 420, 1): "의 부상",
    (9, 421, 0): "의 괴멸",
    (9, 523, 1): " 간\n겨룰 수 있다니 말이다",
    (9, 530, 1): "만 있다니",
    (9, 535, 1): "의 공격!",
    (9, 635, 1): "만\n밀리고 말 줄이야…",
    (9, 693, 1): "만\n상대해 주마",
    (9, 811, 1): "만\n패할 줄이야…",
    (9, 833, 2): "의 일격이다!",
    (9, 834, 2): "의 일격!",
    (9, 860, 2): "의 생포다!",
    (9, 1120, 1): "만\n차지했다!",
    (9, 1130, 1): "만\n차지했다!",
    (9, 1132, 1): "만\n취했다!",
    (9, 1142, 1): "만\n취했다!",
    (9, 1666, 0): "만 여기 있소, 버티시오!",
    (9, 1847, 0): "의 이탈인가…",
    (9, 1848, 1): " 사망!",
    (9, 1853, 1): "의\n죽음이라니…",
    (9, 1857, 1): "만 씻어낸다",
    (9, 2086, 1): "만\n공을 세울 차례로군요",
    (9, 2116, 1): "만\n필요하지 않겠나?",
    (9, 2162, 1): "만\n이 정도까지…!?",
    (9, 2235, 1): "만\n혼란에 빠지기라도 한다는 건가?",
    (9, 2281, 1): "만 속이려 들다니!",
    (9, 2367, 1): "만 얕보았구나",
    (9, 2398, 1): "식\n통할 줄 아느냐",
    (9, 2413, 1): "만 아니야",
    (9, 2447, 1): "만 차지했다",
    (9, 2471, 1): " 교대다!",
    (9, 2472, 1): " 교체하자",
    (9, 2475, 1): " 교대다!",
    (9, 2478, 1): " 교대다",
    (9, 2479, 1): " 교대입니다",
    (9, 2482, 1): " 교대다",
    (9, 2522, 1): "에\n한 수 겨루기를 청하옵니다",
    (9, 2592, 0): ",\n함께 쳐부수는 것이다!",
    (9, 2629, 1): "만 처단하리라!",
    (9, 2648, 1): "의\n첫 공입니다!",
    (9, 2649, 0): "만 ",
    (9, 2655, 1): "의\n첫 공입니다",
    (9, 2656, 1): "의\n첫 공이다!",
    (9, 2660, 2): "의 공이오!",
    (9, 2689, 0): "의 출진",
    (9, 4129, 1):
        "만 충신이라 보기 어렵습니다…\n"
        "전의 높은 충의지사부터 격파하면\n남은 장수들은 굴복을 택할 것",
    (9, 4133, 1): "의\n항복 요청이 오긴 ",
    (9, 4136, 1):
        "의\n파괴라니…\n귀가의 힘을 잘못 판단한 결과",
    (12, 64, 3): ") 귀환 완료\n남은",
    (12, 65, 2): ") 귀환 완료\n남은",
    (12, 66, 3): ") 귀환 완료",
    (12, 67, 2): ") 귀환 완료",
    (13, 94, 1): "식\n",
    (13, 162, 1):
        "의 거성,\n즉 다이묘의 성으로, 본거지라 불립니다\n"
        "다른 성은 가신이 성주로서 다스리고 있습니다",
    (15, 379, 0): "의\n등용 의향이 있",
    (15, 381, 0): "의 ",
    (15, 418, 1):
        "만 설득한다면\n싫다고는 하지 못할 것이다",
    (15, 487, 1): "의 부상",
    (15, 554, 1):
        "만 회유해야 하오…\n아직 당가에 참전할 기미도 없으니\n"
        "우선 물자로 환심을 사는 게 좋소",
    (15, 655, 1):
        "만 당가 휘하에\n들 각오인 듯하오…\n받아들이는 게 어떻겠소?",
    (15, 817, 2): "의 부상",
    (15, 889, 0): "의 생각엔",
    (15, 982, 1): "의 부상",
    (15, 1096, 2): " 시행됐",
    (15, 1171, 1): "까지 가까워진 듯하구려",
    (15, 1183, 1): "까지 가까워진 듯하구려",
    (15, 1462, 2): "의 부상",
    (15, 1488, 2): "의 부상",
    (15, 1493, 2): "의 발생",
    (15, 1509, 1): "의 소문 들었소",
    (15, 1509, 3): "의 기량을 조금 단련시켜",
    (15, 1511, 2): "만 맡겠습니다\n허락하시겠",
    (15, 1513, 1): "만 있나 봅",
    (15, 1514, 1): "쯤 있",
    (15, 1516, 1): "쯤 있",
    (15, 1518, 1): "쯤 있",
    (15, 1519, 1): "쯤 있",
    (15, 1557, 2): "」만 쉽게 속지 않겠",
    (15, 2315, 0):
        "만 전투 때 반드시\n참전해 힘을 보태고 싶다 하옵니다\n"
        "전선의 성에 둘 것",
    (15, 2438, 2): "만 주어졌습니다",
    (15, 2445, 2): "만 간파해 냈",
    (15, 2468, 2): "의 상인 인맥이 넓으므로…",
    (15, 2485, 2):
        "의 휘하 관리들과 함께\n영내에 남는 쌀을 징수하",
    (15, 2494, 2): "에\n항복을 권하고 오",
    (15, 2495, 2): "군,\n",
    (15, 2496, 1): "만\n우리에게 항복하기로 했",
    (15, 2497, 2): "만 이를 거절",
    (15, 2557, 2): "의",
    (15, 2559, 3):
        "의 수호 아래,\n우리 가문이 쇠할 일은 ",
    (15, 2587, 3): "만 이제 결전지로 향하겠",
    (16, 41, 1): "만…",
    (17, 107, 0): "만 무사히 달아났는가…",
    (17, 154, 1): "의 피격!\n큭,",
    (17, 204, 1): "의 패배!\n",
    (17, 206, 0):
        "의 천하는 내가 바라던 천하가 아니다…\n그저 그뿐이다!",
    (17, 222, 1): "의\n전향 약속이 있었다",
    (17, 226, 1): "만 ",
    (17, 260, 1): "만 아직 움직이지 않는가?",
    (17, 271, 0): "의 거병인가! 우리도 호응하자!",
    (17, 285, 0): "의 배신인가!\n우리도 이 기회를 틈타",
    (17, 288, 1): "의 제거 뒤\n주군",
    (17, 369, 1):
        "만 차지하겠다!\n용맹한 아카조나에여, 나를 따르라!",
    (17, 389, 1):
        "만 차지하겠다!\n용맹한 아카조나에여, 나를 따르라!",
    (17, 415, 0):
        "의 아군 합류인가!\n천운이다! 승리가 눈앞이다!",
    (17, 416, 0): "의 움직임인가!\n우리도",
    (17, 425, 0): "의 거병인가! 우리도 호응하자!",
    (17, 456, 1): "의 패배로\n",
    (17, 662, 1):
        "만 움직일 태세가 아니다\n이제 우리 손에 달렸다…",
    (17, 684, 1):
        ", 무엇을 하는 게냐!\n모두 진정하라! 어서 맞서 싸워라!",
    (17, 720, 1):
        "의 괴멸 뒤 병사들도 진정했다\n이제",
    (17, 733, 1): "만 나선다!",
    (17, 740, 1): "만 본래",
    (17, 771, 1):
        "만 움직일 태세가 아니다\n이제 우리 손에 달렸다…",
    (17, 781, 1): "의 부동인가……\n",
    (17, 812, 1):
        ", 대체 뭘 하는 게냐!\n모두 진정하라! 어서 맞서 싸워라!",
    (17, 846, 1): "만 나선다!",
    (17, 865, 1):
        "의 퇴각인가…?\n좋다! 모두, 반격에 나서라!",
    (17, 872, 1): "만 아군이다. 적을 헷갈리지 마라!",
    (17, 887, 1): " 아님…",
    (17, 904, 1):
        "의 부재를 알아차리고\n이쪽으로 서둘러 오고 있을 것이다.",
    (17, 921, 0):
        "의 움직임…!\n큰일이다… 별동대는 아직인가!",
    (17, 975, 0):
        "의 전사 소식……?\n믿을 수 없다…… 어째서……",
    (17, 977, 1): " 사망!\n미안하다…　",
    (17, 978, 1): "의 쓰러짐……\n이대로는……",
    (17, 991, 1): "\n만 궁지로 몰아넣는다!",
    (17, 1111, 0):
        "의 전사 소식…!?\n말도 안 돼…",
    (17, 1149, 0):
        "만 놓쳤지만\n훌륭한 전과라 할 수 있겠군",
}

EXPECTED_SEMANTIC_ADDITIVE_LATE_REWRITE_COUNT = 128
EXPECTED_SEMANTIC_ADDITIVE_LATE_COORDINATE_SHA256 = (
    "8E04EB006E72A7DAE5E6B4D068D67F0658784940BEEEE8F16F66E7A828E15311"
)

# These are semantic recasts, not a particle substitution table.  Every
# coordinate is one audited mixed-register runtime family whose variants can
# include a title, a neutral pronoun, or a low-register noun.  Possessive,
# locative, bound-noun, and event-nominal constructions keep the intended
# role without turning values such as ``너`` or ``놈`` into ``너 본인`` /
# ``놈께서``.
SEMANTIC_MIXED_REGISTER_REWRITES = {
    (1, 10, 1): " 위치, 여기 있",
    (1, 14, 2): "의 말은 언제나 한결같으며",
    (2, 129, 1): "의 수호 아래\n",
    (6, 840, 0): "의 모습이군요…\n돌아가고 싶다…",
    (6, 1555, 0):
        "의 숙고를 믿습니다만,\n단교를 거듭하면\n"
        "악평이 높아질 수 있으니 조심하십시오",
    (6, 1582, 1):
        "의\n모욕인 셈입니다.\n이것만은 용서할 수 없겠군요…",
    (6, 1622, 1): "에 달렸습니다",
    (6, 1633, 2):
        "의\n혼인이라니 참으로 경사로군\n"
        "이걸로 두 가문은 한식구란 말이지!",
    (6, 2201, 0):
        "의 방문, 반갑구먼\n일이 순조롭게 풀리면 좋겠어",
    (6, 2211, 0):
        "의 방문인가… 후후\n두 가문의 번영을 위해 "
        "이번에는 무슨 꿍꿍이인가?",
    (6, 2249, 1): "에게 허락된 땅이 아니다",
    (6, 2289, 1): "의 제안은 무엇입니까?",
    (6, 2291, 1): "의 성의가 먼저다\n이야기는 그다음이다",
    (6, 2452, 0): "의 신의를 믿었건만…!\n이만 실례하겠소!",
    **{
        (6, record_id, 0): "의 죽음으로, 혼인 관계였던\n"
        for record_id in range(3050, 3062)
    },
    (6, 3075, 0): "의 이탈로 인해\n",
    (6, 3076, 0): "의 출분으로\n",
    (6, 3077, 0): "의 출분으로, 혼인 관계였던\n",
    (6, 3078, 1): "의 당가 이탈로,\n",
    (6, 3079, 0): "의 출분으로, 인척이었던\n",
    (6, 3080, 0): "의 출분으로, 혼인 관계에\n있던",
    (6, 3084, 1): "의 당가 이탈로\n",
    (6, 3085, 0): "의 수중에 있던\n",
    (6, 3086, 0): "의 이탈로,",
    (6, 3087, 0): "의 힘은 충분히 길러졌",
    (6, 3405, 1): "의 수호 아래\n",
    (6, 3430, 1):
        "의 시선을 느끼는군\n더욱 힘써야겠다!",
    (6, 3470, 1):
        "의 은혜를 갚으려 힘쓰고 있을 뿐이옵니다…",
    (6, 3489, 1):
        "만큼은 가족이나 다름없지\n앞으로도",
    (6, 3516, 3): "의 힘이 되",
    (6, 3535, 2): "만큼은 가족과 같은 사이",
    (6, 3849, 1): "의\n면회 요청이 들어왔습니다",
    (6, 3866, 1): "의 방문",
    (6, 3942, 2): "의\n면회 요청이 들어와 있",
    (6, 4488, 1): "에 ",
    (6, 4560, 2): "의 직접 만류라면 어쩌면…",
    (6, 4562, 3): "의 설득을 더해",
    (6, 4564, 3): "의 설득을 더해",
    (6, 4566, 4): "의 설득이 이어지",
    (6, 4588, 2): "만큼은 상대하기 까다로운 존재",
    (6, 4588, 4): "의 판단 사항",
    (6, 4599, 2): "의 직접 방문에",
    (6, 4600, 1): "의 방문이라니…\n진심이라는 뜻",
    (6, 4602, 2):
        "의 먼 길 방문이라니!\n황송하기 그지없습니다",
    (6, 4603, 2): "의 직접 방문은 뜻밖인데",
    (6, 4604, 2): "의 방문에도\n",
    (6, 4605, 0): "의 직접 방문은…\n",
    (6, 4607, 1): "의 방문이라니 놀랍군",
    (6, 4609, 1): "의 직접 방문이라니…\n",
    (6, 4611, 1): "의 방문이라니!\n",
    (6, 4613, 1): "의 방문이라니…\n",
    (6, 4615, 2): "의 방문이었",
    (6, 4616, 2): "의 방문이라니\n그래도 ",
    (6, 4617, 2): "의 직접 방문",
    (6, 4629, 0):
        "만큼은 반드시 우리 가문에 보탬이 될 인재이니…\n",
    (6, 4630, 1):
        "의 면회 요청…\n거듭 청하셨습니다",
    (6, 4631, 0): "의 간곡한 면회 요청으로",
    (6, 4632, 1): "의 간청이 있었",
    (6, 4633, 2): "의 ",
    (6, 4634, 2): "의 주선으로 얻은 기회",
    (6, 4836, 0): "의 직접",
    (6, 4837, 0): "의 직접",
    (7, 276, 1): "에 충성",
    (8, 181, 0): "의 평 ",
    (8, 189, 1): "의 인식은 분명한 듯하군",
    (8, 567, 1):
        "의 배려라면 제게 지행 불만 따위 "
        "품게 하지 않으셨을 텐데…",
    (8, 578, 0): "의 평가를\n받은 것인가!",
    (8, 670, 1): "의 노여움인가…",
    (8, 677, 0): "의 뜻대로 따르겠사옵니다",
    (8, 693, 0):
        "에게서 받은 것이니\n돌려드리는 데 무슨 불만이 있겠습니까",
    (9, 519, 0): "의 참전인가\n피가 끓어오르는군!",
    (9, 522, 0): "의 참전이라니\n뜻밖이네요……",
    (9, 527, 0): "의 참전 소식을\n듣다니!",
    (9, 541, 0): "만큼은 여기서\n쓰러뜨려야 합니다",
    (9, 892, 1): "의 도주\n허무하구나",
    (9, 1761, 0): " 상대로라면\n전력을 다해 맞서지요",
    (9, 1843, 1): "의 생존 확인",
    (9, 1849, 0): "의 죽음…?\n허망하구나…",
    (9, 1852, 0): "의 죽음!?\n거짓말이다… 인정 못 한다…",
    (9, 1901, 0): "의 위기…\n구출하러 가야 한다!",
    (9, 2169, 0): "에게는 자비도\n손속도 없는가!",
    (9, 2181, 0): "에게는 자비도\n손속도 없는가!",
    (9, 2220, 0): "의 책략?\n가소롭군!",
    (9, 2298, 0): "에게 이런\n오의가 있었다니",
    (9, 2415, 1): "다운\n발상이로군",
    (9, 4142, 4): "에게 이 자리에서 포박을 명한다",
    (9, 4144, 3): "의 항복이라면\n",
    (13, 163, 1):
        "의 성주 직임이 있으므로\n직접 명령하여 발전시켜야 합니다",
    (13, 164, 1):
        "의 성주 직임이 있으므로\n직접 명령하여 발전시켜야 합니다",
    (15, 270, 3): "만 맡았",
    (15, 385, 1):
        "의 처지\n지금 지위에 불만인 듯해!\n"
        "권유하면 이쪽으로 귀순할지도 몰라",
    (15, 388, 2): "의 귀순\n가능성이라고…",
    (15, 392, 1):
        "의 마음\n당가로 돌릴 수 있을지도 모른다\n"
        "조금 시험해 보고 싶구먼…",
    (15, 393, 1): "의 사정\n알고 계십니까?　",
    (15, 395, 2):
        "의 처지가 곤란하다던데…\n우리 가문으로 오시면 좋을 것을",
    (15, 435, 0): "의 은혜",
    (15, 437, 2):
        "의 안목을 믿고\n반드시 기대에 부응해 보이겠사옵니다",
    (15, 438, 2): "의 힘이 되고자 하옵니다",
    (15, 439, 1):
        "의 인정을 받아 제가 있사오니\n이",
    (15, 440, 2): "의 중용을 바라옵니다……",
    (15, 441, 1):
        "의 힘이 될 수 있도록\n분골쇄신하여 힘쓰겠사옵니다",
    (15, 443, 0):
        "의 명성을 좇아왔사옵니다\n"
        "앞으로 신세를 지겠사오며 이름은",
    (15, 446, 2):
        "의 보탬이 되도록 힘쓰겠사옵니다\n"
        "소인의 활약을 기대해 주시옵소서",
    (15, 538, 2):
        "의 충신이 되게\n한 번 더 은혜를 베풀자",
    (15, 1537, 1): "의 사관 의향이 확인된 상태",
    (15, 1540, 4):
        "의 주군에 대한 불만을 이용해\n빼내기 교섭을 시도하겠다",
    (15, 1559, 2): "만 ",
    (15, 2291, 2): "의\n독단적 출진 상태",
    (15, 2585, 2): "에 길보를 전하겠습니다",
    (15, 2598, 3):
        "의 합류로 든든합니다\n이번 싸움은 반드시 승리하겠습니다",
}

EXPECTED_MIXED_REGISTER_REWRITE_COUNT = 121
EXPECTED_MIXED_REGISTER_COORDINATE_SHA256 = (
    "18387CAB45A3E656AABE93EB1DC1F7A2BD37546CFCC277548A3311C272085592"
)

FOREIGN_MERCHANT_ORTHOGRAPHY_REWRITES = {
    (6, 1151, 0):
        "먼저 남만 상관을 지어 주십시오\n이야기는 그다음입니다",
    (6, 1152, 0):
        "어서 오십시오\n철포는 얼마나 필요하십니까?",
    (6, 1155, 0):
        "구매해 주셔서 감사합니다\n철포",
    (6, 1155, 1): " 받아 주십시오",
}
EXPECTED_FOREIGN_MERCHANT_ORTHOGRAPHY_REWRITE_COUNT = 4
EXPECTED_FOREIGN_MERCHANT_ORTHOGRAPHY_COORDINATE_SHA256 = (
    "531BB2CBED33CA5AB36B69BD8B59D077098B8579F1AD09FC081C371A082F4A5D"
)

# Group 2/5 selectors emit a runtime person name.  ``본인`` was formerly
# appended as a particle carrier, but that changes a third person into the
# speaker and fails for every sampled assembly.  Each coordinate below uses
# a reviewed relation: possessive event, bound focus, command target, or
# person-led force.
SELECTOR_PERSON_REWRITES = {
    (2, 334, 1): "만큼은 인연을 요체로 삼는다!",
    (6, 728, 0): "의 평정 참여를…\n주군께서는 무슨 생각이신가",
    (6, 733, 0): "의\n평정중 발탁이라니… 납득할 수 없다!",
    (6, 739, 0): "의\n참석이라니",
    (6, 1389, 0): "의 해산을 명합니다\n정말 해산하시겠습니까?",
    (6, 2059, 0): "의 지행 수령량에 불만  충성-",
    (6, 2060, 0): "의 지행 수령량에 만족  충성+",
    (6, 2455, 1): "에 대한 박대를\n나중에 후회하지 않으면 좋겠군",
    (6, 2996, 0): "의 요구는 무엇이지…",
    (6, 3108, 0): "군 ",
    (6, 3398, 2): "의 재기를 반드시 도와\n훌륭한 당주로 성장",
    (6, 3400, 4): "의 곁을 끝까지 수호",
    (6, 3402, 1): "의 재기\n증명",
    (6, 3404, 1): "에게 이",
    (6, 3404, 2): "의\n헌신적 수호로 빛나",
    (6, 3409, 2): "의\n당주 취임",
    (6, 3410, 3): "만 나에게",
    (6, 3412, 1): "의 곁을 반드시 지켜 보이",
    (6, 3414, 2): "에게 이",
    (6, 3414, 3): "의\n목숨을 건 수호로 보장되",
    (6, 3415, 3): "의 힘을 크게 키워",
    (6, 3417, 3): "의 곁을\n목숨 걸고 수호",
    (6, 3419, 1): "의 수호로 가문은 건재하리라!",
    (6, 3899, 0): "만큼은\n마음이 잘 맞는다",
    (6, 3925, 0): "만큼은\n혐오하고 있다",
    (6, 3927, 0): "만큼은\n마음이 맞지 않는다",
    (6, 4183, 2): " 중심의\n",
    (6, 4198, 0): "의 지원을 위해\n내정을 추진하고 있으며",
    (6, 4198, 1): " 중심의\n",
    (6, 4256, 0): "의 조정 교섭이 시작",
    (6, 4371, 0): "의 건설을 돕습니다",
    (6, 4372, 0): "의 건설을 중단합니다",
    (6, 4373, 0):
        "의 건설을 중단합니다\n정말 괜찮으시겠습니까?",
    (6, 4387, 0): "의 담당 임무 「",
    (6, 4548, 1): "만큼은 신뢰하지 않는다",
    (6, 4563, 0): "만큼은",
    (6, 4564, 1):
        "만큼은\n어떻게든 우리 편으로 만들고 싶은 인물",
    (6, 4565, 1): "만큼\n",
    (6, 4566, 1): "의 별칭\n",
    (6, 4570, 1):
        "의\n저항 중단과 항복 의사를 확인했습니다\n더 나은 조건으로 교섭",
    (6, 4572, 2):
        "의 항복 의사를 확인했습니다\n더 나은 조건으로 교섭",
    (6, 4574, 0): "의 포섭 수락은 신속했",
    (6, 4575, 1):
        "의\n귀순 계책도 있다 합니다\n"
        "자세한 내용은 당사자에게 직접 들어 보시는 게 ",
    (6, 4576, 1):
        "의\n귀순 계책도 있다 합니다\n"
        "자세한 내용은 당사자에게 직접 들어 보시는 게 ",
    (6, 4578, 0):
        "의 마음은 포섭 쪽으로 기울었지만\n설득이 충분하지",
    (6, 4580, 1): "의 평,\n",
    (6, 4652, 1): "의 우의를 바라는 바",
    (7, 187, 0): "의 참전 소식은\n절호의 기회입니다",
    (7, 188, 0): "의 전면 등장은\n쓰러뜨릴 기회입니다",
    (7, 190, 1): "의\n수급을 올릴 때입니다!",
    (7, 193, 0): "의 생포로\n공성의 실마리를 삼읍시다",
    (7, 194, 0): "의 출진 소식입니다.\n공성에 앞서 제압합시다",
    (7, 195, 0): "의 격파에 성공하면\n공성도 수월해질 것입니다",
    (7, 197, 0):
        "의 성주직이니,\n먼저 제거하는 것이 좋겠습니다",
    (7, 198, 2): "의 생포를 노립시다",
    (7, 222, 0): "군이\n적장을 포박하",
    (7, 379, 0): "의 처단을 마쳤습니다",
    (7, 380, 1): "의 처단을 마쳤습니다",
    (7, 383, 0): "의 처단 예정",
    (7, 429, 0): "의 해방을 마쳤습니다",
    (7, 734, 0): "군이\n",
    (7, 799, 0): "군이\n적 본거지 「",
    (7, 804, 1): "의 해체를 완료했습니다",
    (7, 812, 1): "의 해체를 진행하며\n진행하시겠습니까?",
    **{
        (7, record_id, 2): " 휘하\n"
        for record_id in range(842, 853)
    },
    (7, 875, 1):
        "의 정예 가신들이여\n그 진면목을 보여 다오!",
    **{
        (7, record_id, 0):
            {
                2677: "의 전공이 제일이라……\n어쩔 수 없군",
                2678: "의 전공이 제일이라고!?\n그자에게만큼은 지고 싶지 않았건만……",
                2680: "의 전공이 제일이라……\n한 걸음씩 정진해 언젠가 반드시 앞지르리라",
                2686: "의 전공이 제일이라……\n허허, 훌륭하다고 인정해야겠군",
                2688: "의 전공이 제일이라고!?\n다음번에는",
                2690: "의 전공이 제일……?\n아니, 태평성대에 가까워진 일이다…… 기뻐해야지……",
                2692: "의 공이 가장 컸다고!?\n그 자식…… 인정 못 해!",
                2694: "의 전공이 제일의 영예를 차지했는가……\n그자에게 무훈을 내주다니 분하군……",
                2696: "의 전공이 제일인가\n분하기도 하고 기쁘기도 하구나",
                2697: "의 전공이 제일이라……\n저런 자에게 활약에서 밀리다니 나도 미숙했군",
                2702: "의 공이 이번 싸움의 핵심이었나\n마음에 들진 않지만…… 확실히 싸움에는 능하군",
                2703: "의 전공이 제일이라니\n두고 보아라……",
                2704: "의 전공이 제일이라니……\n이번만은 승리를 양보해 주도록 하지",
                2709: "의 전공이 제일? 아니야\n다음에는,",
                2710: "의 전공이 제일이라고?\n실컷 기뻐해 두어라. 다음에는 어림없다……",
                2714: "의 전공이 제일이라고!?\n그자에게 뒤처지다니 분하군……",
                2721: "의 전공이 제일이라니 더없이 기쁘구나\n앞으로도 무예에 힘쓰거라",
                2731: "의 전공이 제일이었는가\n나도 이처럼 결과로 말하는 무사가 되고 싶군",
            }[record_id]
        for record_id in (
            2677, 2678, 2680, 2686, 2688, 2690, 2692, 2694, 2696,
            2697, 2702, 2703, 2704, 2709, 2710, 2714, 2721, 2731,
        )
    },
    (7, 2755, 1): "의 전공이 제일인가!\n함께 당가를 일으켜 세우세",
    (9, 419, 0): "의 포박 완료",
    (9, 821, 0): "의\n격파에 성공했다!",
    (9, 829, 0): "의\n격파에 성공했습니다!",
    (9, 831, 0): "의\n격파에 성공했습니다",
    (9, 832, 0): "의\n격파에 성공했습니다!",
    (9, 847, 0): "의\n생포!",
    (9, 848, 0): "의\n생포 성공!",
    (9, 849, 0): "의\n생포!",
    (9, 850, 0): "의\n포박 완료",
    (9, 852, 0): " 몸은\n내 손에 들어왔다",
    (9, 855, 0): "의\n생포 성공!",
    (9, 856, 0): " 몸은\n우리 수중에 있다!",
    (9, 857, 0): "의\n결박을 마쳤습니다",
    (9, 858, 0): "의\n생포 성공",
    (9, 887, 0): "의 격파라니\n장하도다!",
    (9, 891, 0): "의 격멸로\n천하에 이름을 떨쳤노라!",
    (9, 894, 1): "의\n격파라니……!",
    (9, 896, 0): "의 격파라니\n장하다, 참으로 장하다!",
    (9, 905, 1): " 상대로\n압도했군요!",
    (9, 2646, 0): "의 첫 공이다!\n따르라!　돌격하라!",
    (9, 2658, 3): " 뒤를 따르라!",
    (9, 2662, 1): "의 출진이다, 첫 공은 내 것이다!",
    (9, 2932, 0): "만 노려라!\n다른 놈들은 신경 쓰지 마라!",
    (9, 2934, 0): "의 격파를 노려라!\n우리의 공으로 삼으리라",
    (9, 2935, 0): "의\n격파를 완수하지요",
    (9, 2936, 0): "만 노린다!\n결코 놓치지 마라!",
    (9, 2937, 0): "만 노린다\n한 부대씩 무너뜨리자",
    (9, 2938, 0): "의\n격파가 상책이다",
    (9, 2940, 0): " 겨냥\n진군 개시!",
    (9, 2942, 0): "의\n처치를 맡지요",
    (9, 2943, 0): "만 노린다\n적장을 쓰러뜨려 공을 세우리라",
    (9, 3924, 1): "의 협공을\n눈치채지 못할 줄 알았나?",
    (9, 3943, 2):
        "만큼은 싸움에 능하기로 이름난 무장\n"
        "주의해서 맞서야 할 것입니다",
    (9, 3952, 1): "의 지휘 아래 빈틈없는 포진\n",
    (9, 3970, 2): "의 수비 아래 저 「",
    (13, 117, 1): " 이름을 꼽",
    (15, 288, 1): "의 제안은\n",
    (15, 298, 1):
        "의\n목격 소식이 들어왔습니다\n등용해도 되겠사옵니까",
    (15, 313, 1):
        "의\n사관 의사를 확인했으니\n맞아들일 준비를 하",
    (15, 314, 0):
        "의 당가 사관 희망을\n확인했다는데…\n"
        "꼭 맞아들여야 한다",
    (15, 330, 0):
        "의 등용을 제안드립니다\n그 낭인은 지금 성하에 머물고 있다 하옵니다\n"
        "부디 설득을 제게 맡겨 주십시오",
    (15, 333, 0):
        "의 등용이 어떻겠사옵니까?\n마침 사관할 곳을 찾고 있다 하니...\n"
        "말을 건네 보아도 되겠사옵니까",
    (15, 336, 0):
        "의 등용이 어떻겠소\n성하에 있다 하니\n말을 건네고 올까 하오",
    (15, 337, 1):
        "의 등용이 어떨는지요?\n아무래도 성하에 있는 모양입니다\n"
        "사람은 많을수록 좋은 법이지요",
    (15, 338, 0):
        "의 등용을 권합니다\n성하에 머무르고 있다 하니\n"
        "이야기를 나누려면 지금이 적기인 줄로 아옵니다",
    (15, 352, 0): "의 도착이라고!\n",
    (15, 433, 0):
        "의 거취가 유언비어로\n갈피를 못 잡는 모양\n"
        "우리 가문으로 오도록 권유하면 순순히 귀순할지도……",
    (15, 437, 1): "의 영입이라니\n",
    **{
        (15, record_id, 0):
            "의 권유를 위해 적지로 향하던 도중\n적의 습격을 받은"
        for record_id in range(459, 471)
    },
    (15, 473, 3): " 귀순:\n",
    **{
        (15, record_id, 3): "의 배신으로\n"
        for record_id in range(474, 486)
    },
    (15, 486, 0): "의 회유에 성공",
    (15, 488, 0): "의 회유에 실패",
    (15, 489, 0): "의 배신으로,",
    (15, 1352, 1): "만 건재한 한\n",
    (15, 1353, 1):
        "만큼은\n수성의 명인이나, 어떤 장수도\n"
        "독을 마시면 싸우지 못할 것",
    (15, 1357, 1): "의 습격으로\n부상 성공",
    (15, 1413, 0): "의 도착이라고!\n",
    (15, 1431, 0): "의 도착이라고!\n",
    (15, 1474, 1):
        "의 충의 대상은\n바뀔 수 있다고 판단",
    (15, 1476, 0): "만큼은 모략을 모른다",
    (15, 1477, 0):
        "만큼은 의심을 모르는 자\n주군의 악평도 쉽게\n믿게 하",
    (15, 1478, 0):
        "만큼은 우리 가문에 꼭 필요한 인재\n주군을 의심하게 만들어\n"
        "빼내기를 위한 한 수로",
    (15, 1479, 0):
        "만큼은 걸물로 이름난 자\n속임수를 써야 하더라도\n"
        "우리 가문으로 끌어들일 가치가",
    (15, 1480, 0):
        "만큼은 틀림없는 인재이니\n가문의 번영을 위해서라도 맞아들이고자\n"
        "다소 사전 공작이 필요하",
    (15, 1486, 0):
        "의 거취는 유언비어로\n망설이는 모양\n"
        "이참에 그자를 빼내자고 건의드리",
    (15, 1530, 1):
        "의\n우리 군단 지원 투입을\n부디 허락해 주",
    (15, 1532, 2):
        "의\n성주로 우리 군단에 보내 주실 수 없을지……",
    (15, 1533, 1):
        "의\n성주 영입을 우리 군단에서 바라옵니다",
    (15, 1543, 0): "의 무장 탐색 실패",
    (15, 1874, 1):
        "의 존재와\n그 인물의 동향 또한\n승패를 크게 좌우할 것",
    (15, 1893, 3): "만큼은 싸움에 능하기로 이름 높아……",
    (15, 1894, 3): "만큼은 싸움에 능하기로 이름 높아……",
    (15, 2240, 2): "의 주군 가문 염려 때문이었으니……",
    (15, 2337, 1):
        "의\n우리 군단 지원 전환을\n승부수로 삼게 해",
    (15, 2424, 1):
        "만큼은 명장으로 알려져\n섣불리 손을 대면 큰코다치",
    (17, 116, 0):
        "의 군은 급히 교토로 회군했습니다\n그 충격으로",
}

EXPECTED_SELECTOR_PERSON_REWRITE_COUNT = 194
EXPECTED_SELECTOR_PERSON_COORDINATE_SHA256 = (
    "E18CB971F68A8FC50577EC806DDCD7EC4B2A05B4B34537C7B5D35479AFAE2E54"
)

SELECTOR_LOCATION_REWRITES = {
    (7, 2508, 2): "을 비롯한 총",
    **{
        (8, record_id, 0): " 군을 비롯해 풍작을 맞은\n"
        for record_id in range(264, 269)
    },
    **{
        (8, record_id, 0): " 군을 비롯해 피해를 입은\n"
        for record_id in range(274, 279)
    },
    **{
        (8, record_id, 0): " 군을 비롯해 피해를 입은 군은 총"
        for record_id in (
            *range(288, 293),
            *range(298, 303),
            *range(308, 313),
            *range(332, 337),
            *range(356, 361),
        )
    },
    (15, 821, 2): "을 비롯해 총",
    (15, 1455, 0): "을 비롯한",
    (15, 1458, 2): "을 비롯한",
    (15, 2538, 1): "을 비롯한",
    (15, 2540, 2): "을 비롯한",
}

EXPECTED_SELECTOR_LOCATION_REWRITE_COUNT = 41
EXPECTED_SELECTOR_LOCATION_COORDINATE_SHA256 = (
    "176E70BDCE08DC6018CA42F98FF9C6A1228935B940E79EDC4448573290D72386"
)

# Exact edits from the independent stratified language review.  A sample can
# own more than one literal because the natural Korean assembly sometimes
# crosses a selector boundary.
INDEPENDENT_QA_REWRITES = {
    (2, 160, 0): "의 행군로 소멸로 공략 대상에서 해제",
    (2, 187, 1): " 전역 통치",
    (6, 3337, 1): " 사이의 칙명 강화를 주청합니다",
    (6, 4165, 1): " 등 여러 곳에\n공세",
    (7, 894, 2): "놈이, 마침내 ",
    (7, 894, 3): " 병력을 이끌고\n우리 세력의 「",
    (7, 896, 0): " 측이 ",
    (7, 896, 1): " 병력을 이끌고\n우리 세력의 ",
    (7, 896, 2): "을 공격",
    (7, 982, 0):
        "은 승리했소\n무를 숭상하는 이 세상에서 승리는 긍지이니\n"
        "우리 가문을 비롯한 여러 가문이 모두 칭송할 것이오",
    (7, 2507, 0):
        "을 다방면에서 공략하는 게 어떻습니까?\n우리 군단에서는",
    (8, 268, 0): " 군을 비롯해 풍작을 맞은\n",
    (8, 298, 0): " 군을 비롯해 피해를 입은 군은 총",
    (8, 333, 0): " 군을 비롯해 피해를 입은 군은 총",
    (15, 1455, 0): "을 비롯한",
    (13, 125, 1): "\" 또한 지략에도 자신이\n",
    (15, 352, 0): ", 왔다!\n",
    (15, 1455, 2): " 달성했",
    (15, 2583, 4): "과의 결전을 준비하",
    (17, 116, 0):
        "의 군은 급히 교토로 회군했습니다\n그 충격으로 ",
}
EXPECTED_INDEPENDENT_QA_SAMPLE_COUNT = 16
EXPECTED_INDEPENDENT_QA_LITERAL_REWRITE_COUNT = 20
EXPECTED_INDEPENDENT_QA_LITERAL_COORDINATE_SHA256 = (
    "CB0920015A41D858E6E6D73EE377103863BAF1C4ECA893DED4058B0C3205197A"
)
EXPECTED_INDEPENDENT_QA_SAMPLE_COORDINATE_SHA256 = (
    "ABE24CE9CAD4C6E1C8A444A6C36A73F3E4D42E9AD92B9F94D5EF76216C0033B5"
)
INDEPENDENT_QA_PERSON_DEFECT_COORDINATES = frozenset(
    {
        (2, 334, 1),
        (6, 3398, 2),
        (6, 3415, 3),
        (6, 4371, 0),
        (6, 4570, 1),
        (7, 188, 0),
        (7, 429, 0),
        (7, 851, 2),
        (7, 2694, 0),
        (7, 2731, 0),
        (9, 850, 0),
        (9, 905, 1),
        (9, 2940, 0),
        (13, 125, 1),
        (15, 352, 0),
        (15, 467, 0),
        (15, 479, 3),
        (15, 1352, 1),
        (15, 1480, 0),
        (17, 116, 0),
    }
)
EXPECTED_INDEPENDENT_QA_PERSON_DEFECT_COUNT = 20
EXPECTED_INDEPENDENT_QA_DEFECT_RECORD_COUNT = 33
EXPECTED_INDEPENDENT_QA_DEFECT_RECORD_SHA256 = (
    "520803C72FB2FCCDB18A0F7752CC51228C775EEFC1FB522CBADF1D8F7F6AAA0C"
)
APPROVED_SEMANTIC_TARGET_INTRODUCTIONS = frozenset({(2, 160, 0)})
APPROVED_SEMANTIC_CARRIER_INTRODUCTIONS = {
    "대상": APPROVED_SEMANTIC_TARGET_INTRODUCTIONS,
    "장수": frozenset(
        {
            (6, 4906, 0),
            (9, 3570, 1),
            (9, 3572, 1),
            (9, 3573, 1),
            (9, 3575, 1),
            (9, 3576, 1),
            (9, 3578, 1),
            (9, 3579, 1),
            (9, 3580, 1),
        }
    ),
}

# The three closure rows combine a grammatical repair with a newly required
# separator before the following selector.  These compact reviewed forms keep
# the original raw-G1N width budget without creating a new exception.
BOUNDARY_CLOSURE_REWRITES = {
    (2, 663, 0): " 건은 앞으로",
    (2, 665, 0): " 건은 앞으로",
    (0, 2407, 0): " 놈",
    (0, 2408, 0): " 놈",
    (0, 2411, 0): " 놈",
    (0, 2412, 0): " 놈",
    (0, 2482, 0): " 놈",
    (7, 1913, 0): " 공략은 헛되도다\n",
    (7, 2872, 0): " 공략의 호기로 봤",
    (7, 2876, 1): " 공격에 가세",
    (8, 936, 1): " 아래로의 ",
    (8, 941, 1): " 아래로 ",
    (6, 3034, 0): "그",
    (6, 3431, 0): "서 ",
    (6, 3454, 0): "훈공1위:그",
    (6, 3554, 1):
        " 직책이 훈공 1위라니 괜찮을까요\n여러분, 그래서는 ",
    (6, 3502, 1): " 또한",
    (6, 3690, 0): ", ",
    **{
        (6, record_id, 1): "」 지시 완료,"
        for record_id in (
            4111, 4112, 4113, 4114, 4115, 4116, 4117, 4118,
            4119, 4120, 4121, 4122, 4124, 4125, 4127, 4128,
            4130, 4131, 4132, 4133, 4136, 4137, 4140, 4141,
            4143, 4144, 4148, 4150, 4151, 4152, 4154,
        )
    },
    (7, 556, 0): " 궤멸 후",
    (8, 981, 0): " 몸소 개입하여\n이 조략을 막아 내",
    (13, 93, 1): " 또한",
    (15, 353, 0): " 또한",
    (15, 1414, 0): " 또한",
    (15, 1420, 0): " 또한",
    (15, 1438, 0): " 또한",
    (15, 1485, 0): " 시행 대상",
    (15, 1582, 0): " 아래 군에서\n간자가 있다는 보고를 얻었",
    (15, 1583, 1):
        " 아래 군에 들어와\n수상한 움직임을 보이고 있다던데…\n"
        "병사를 보내 견제할 수 있",
}

EXHAUSTIVE_REMAINDER_EXACT_REWRITES = {
    (2, 278, 1):
        " 단 한 사람!\n설령 죽는다 해도 목을 베리라!",
    (6, 4906, 0):
        " 장수는 현재 평정중에 임명된 무장입니다.\n계속하시겠습니까?",
    (7, 701, 0): "을 빼앗았다!",
    (7, 767, 1): "을 빼앗았다!",
    **{
        coordinate:
            " 같은 상대에게 이토록 패하다니…\n"
            "우리 가문은 싸울 때를 잘못 판단했을지도 모른다\n"
            "이 피해로 한동안 싸우기는 어렵겠군…"
        for coordinate in (
            (7, 1025, 0),
            (7, 1026, 0),
            (7, 1033, 0),
            (7, 1035, 0),
            (7, 1045, 0),
        )
    },
    (7, 1037, 0): " 같은 상대에게 이토록 패하다니…\n",
    (7, 1047, 0): " 같은 상대에게 이토록 패하다니…\n",
    (7, 2023, 0): ", 각오하라!\n",
    (7, 2031, 1): ", 각오하라!",
    (9, 3570, 1):
        " 장수를 따르고 있구먼\n다가가려면 조심해야겠어",
    (9, 3572, 1):
        " 장수를 해칠 속셈인 듯하니\n경계해야 하옵니다",
    (9, 3573, 1):
        " 장수를 노리는 것일까요\n경계해 두도록 하지요",
    (9, 3575, 1):
        " 장수가 공격을 준비하는 낌새가 있으니\n"
        "강탈해 버리는 것도 재미있겠군요",
    (9, 3576, 1):
        " 장수를 노리는 것일까요\n경계해 두도록 하지요",
    (9, 3578, 1):
        " 장수를 노리는 것일까요\n조심해야겠습니다",
    (9, 3579, 1):
        " 장수가 공격을 준비하는 기색이 있소\n경계가 필요할 듯하오",
    (9, 3580, 1):
        " 장수를 노리는 것일까요\n조심해야겠습니다",
    (9, 4120, 0): ": 파괴하라",
    (9, 4125, 0): " 부대를 협격해 격파하라",
    (15, 1104, 3):
        " 두 가문의\n당가에 대한 인상이 나빠진 듯……",
    (15, 2067, 1): "의 전과는\n무관하여 송구하오나\n",
    (15, 2151, 1): "의 전과는\n무관하여 송구하오나\n",
    (17, 948, 0):
        ", 드, 드디어 마주했군…\n자, 그 목을 내놓아라",
}
EXHAUSTIVE_REMAINDER_SPACING_COORDINATES = frozenset(
    {
        (2, 639, 0),
        (2, 674, 0),
        (3, 47, 0),
        (3, 48, 0),
        (3, 49, 0),
        (6, 727, 0),
        (6, 821, 0),
        (6, 1347, 2),
        (6, 1348, 2),
        (6, 1349, 2),
        (6, 1350, 2),
        (6, 1351, 2),
        (6, 1352, 2),
        (6, 1353, 2),
        (6, 1354, 2),
        (6, 1355, 2),
        (6, 1356, 2),
        (6, 1357, 2),
        (6, 1358, 2),
        (6, 1420, 1),
        (6, 1580, 1),
        (6, 1650, 0),
        (6, 1651, 0),
        (6, 3584, 0),
        (6, 3628, 3),
        (6, 3747, 2),
        (6, 3748, 2),
        (6, 3874, 0),
        (6, 4107, 0),
        (6, 4108, 0),
        (6, 4120, 3),
        (6, 4170, 2),
        (6, 4171, 2),
        (6, 4172, 2),
        (6, 4535, 0),
        (6, 4922, 0),
        (7, 550, 0),
        (7, 650, 1),
        (7, 714, 0),
        (7, 1006, 1),
        (7, 1053, 0),
        (7, 1058, 0),
        (7, 1060, 0),
        (7, 1065, 0),
        (7, 1072, 0),
        (7, 1077, 0),
        (7, 1079, 0),
        (7, 1081, 0),
        (7, 1082, 0),
        (7, 1086, 0),
        (7, 1088, 0),
        (7, 1117, 0),
        (7, 1454, 1),
        (7, 1978, 1),
        (7, 2457, 0),
        (7, 2676, 0),
        (7, 2701, 0),
        (7, 2851, 1),
        (7, 2863, 0),
        (8, 521, 1),
        (9, 897, 0),
        (9, 2357, 0),
        (9, 2403, 1),
        (9, 4137, 0),
        (15, 395, 1),
        (15, 495, 1),
        (15, 772, 0),
        (15, 774, 0),
        (15, 777, 3),
        (15, 778, 3),
        (15, 832, 2),
        (15, 1079, 0),
        (15, 1091, 0),
        (15, 1131, 1),
        (15, 1193, 2),
        (15, 1194, 2),
        (15, 1195, 1),
        (15, 1445, 1),
        (15, 1611, 2),
        (15, 2175, 1),
        (15, 2257, 1),
        (15, 2258, 1),
        (15, 2265, 2),
        (15, 2548, 1),
        (17, 59, 1),
        (17, 111, 1),
        (17, 123, 0),
        (17, 270, 1),
        (17, 272, 0),
        (17, 422, 1),
        (17, 450, 0),
        (17, 498, 1),
        (17, 544, 1),
        (17, 809, 2),
    }
)
EXPECTED_EXHAUSTIVE_REMAINDER_ACTUAL_COUNT = 121
EXPECTED_EXHAUSTIVE_REMAINDER_ACTUAL_COORDINATE_SHA256 = (
    "5D82636D4A12AD6C37F8C0DB6A40CE88B0D3CC03383F1162373A21522DC5102C"
)

# The strengthened end-of-literal detector exposes compact UI/event records
# whose subject or object particle was stored as an isolated literal.  A
# colon or middle dot expresses the same actor/target or pair relation without
# assuming the runtime value's final sound; the few conversational cases use
# a reviewed invariant phrase.
FIXED_BOUNDARY_CLOSURE_REWRITES = {
    **{
        coordinate: ": "
        for coordinate in (
            (2, 143, 0),
            (6, 3350, 0),
            (6, 3428, 0),
            (6, 3747, 1),
            (6, 3969, 0),
            (6, 3970, 0),
            (6, 4065, 0),
            (6, 4080, 1),
            (6, 4912, 2),
            (7, 281, 0),
            (7, 606, 0),
            (7, 2871, 0),
            (8, 378, 0),
            (8, 381, 0),
            (8, 442, 1),
            (8, 443, 1),
            (8, 903, 0),
            (8, 931, 0),
            (8, 933, 0),
            (8, 934, 0),
            (8, 935, 0),
            (8, 936, 0),
            (8, 937, 0),
            (8, 938, 0),
            (8, 939, 0),
            (8, 940, 0),
            (8, 941, 0),
            (8, 942, 0),
            (9, 403, 0),
            (9, 404, 0),
            (9, 415, 0),
            (9, 427, 0),
            (9, 428, 0),
            (9, 430, 0),
            (9, 431, 0),
            (9, 433, 0),
            (9, 434, 0),
            (9, 436, 0),
            (9, 437, 0),
            (9, 439, 0),
            (9, 440, 0),
            (12, 63, 0),
            (15, 380, 0),
            (15, 640, 0),
            (15, 720, 0),
            (15, 724, 0),
            (15, 813, 0),
            (15, 814, 0),
            (15, 816, 0),
            (15, 981, 0),
            (15, 1367, 0),
            (15, 1410, 0),
            (15, 1426, 0),
            (15, 1427, 0),
            (15, 1444, 0),
            (15, 1460, 0),
            (15, 1487, 0),
            (15, 1542, 0),
            (15, 2209, 0),
            (15, 2210, 0),
            (15, 2216, 0),
            (15, 2220, 0),
            (15, 2518, 0),
            (15, 2519, 0),
            (15, 2526, 0),
            (15, 2541, 0),
            (15, 2551, 0),
            (15, 2552, 0),
        )
    },
    **{
        coordinate: ", "
        for coordinate in (
            (6, 830, 0),
            (9, 401, 0),
            (9, 414, 0),
            (9, 423, 0),
            (9, 429, 0),
            (9, 432, 0),
            (9, 435, 0),
            (9, 438, 0),
            (9, 441, 0),
        )
    },
    **{
        coordinate: "·"
        for coordinate in (
            (6, 1633, 1),
            (6, 1634, 0),
            (6, 1642, 1),
            (6, 1643, 0),
            (10, 7, 0),
            (15, 1193, 1),
            (15, 1194, 1),
            (17, 228, 2),
            (17, 720, 0),
        )
    },
    (4, 103, 0): ": ",
    (4, 103, 1): "에 종속됩니다",
    (6, 3556, 0): ", ",
    (6, 3556, 1): " 자리에 있는 것은\n",
    (6, 3665, 0): ": ",
    (6, 3684, 0): ", ",
    (6, 3684, 1): "에게…\n뜻밖의 복",
    (6, 3692, 0): ", ",
    (6, 4260, 0): "→ ",
    (6, 4926, 1): "→ ",
    (6, 4926, 2): " 영주로 임명",
    (7, 2032, 1): " 측",
    (8, 379, 0): ": ",
    (8, 903, 1): ", ",
    (8, 949, 0): "→ ",
    (8, 949, 1): "\n과연, 좋은 안이라 사료되",
    (8, 1234, 1): "→ ",
    (15, 2324, 0): "→ ",
}

# User screenshot regressions.  Group 4 property 0x32 emits a clan name, so
# the literal must provide both the separator and the relation.  The old
# negative terminal at call 748 reversed the request ("약속하지 않습니다");
# the call is retargeted to the proved empty terminal and the question is
# completed in the literal.
SCREENSHOT_PRIORITY_REWRITES = {
    (6, 3768, 0): "훗날 ",
    (6, 3768, 1): "에 원군 등\n군사적 ",
    (6, 3768, 2): "협력을 약조하겠소?\n",
    (6, 3768, 3): "",
    (6, 3768, 4): "",
    (6, 4917, 0): "훗날 ",
    (6, 4917, 1): "에 중재 등\n군사 ",
    (6, 4917, 2): "협력을 약조하겠소?\n",
    (6, 4917, 3): "",
    (6, 4917, 4): "",
}

# Exact rewrites whose correctness depends on the complete Cartesian product
# of adjacent call terminals.  These records cannot be made safe by replacing
# a single Korean particle: the original static stem and the runtime-selected
# terminal form two independently variable halves of one sentence.
CALL_ASSEMBLY_EXACT_REWRITES = {
    (8, 1198, 0): "금 광맥을 발견했다는\n백성의 보고가 있었",
    (15, 1359, 3): "명에게 상처를 입혀 주었",
    (15, 1666, 1): "」 시설 건설은 ",
    (15, 1669, 1): "」 정책 발령은 ",
    (8, 1032, 0): "하아… 설마, ",
    (7, 1714, 1): "\n을 빼앗는 것쯤 식은 죽 먹기\n명을 내려 주시오",
    (6, 4517, 2): "도 겸임할 수\n있을 듯",
    (1, 11, 1): ". ",
    (1, 11, 2): " 이후 일정이 있으니,",
    (1, 11, 3): " 이 일은 여기까지",
    (1, 25, 1): " 애송이는 아니오",
    (2, 133, 3): ". 어떤 수를\n써서라도 가문을 번영시키",
    (6, 3507, 0): "이렇게 공적을 인정",
    (6, 3507, 1): ".\n충절을 다한 보람도 있",
    (6, 3528, 1): ".\n",
    (6, 3528, 2): "지향할 곳은 아직 저 위\n한층 더 힘쓰",
    (6, 3528, 3): ".",
    (6, 3547, 3): ".",
    (6, 3556, 3): ".",
    (6, 3625, 2): "…",
    (6, 4179, 0): "상황이 바뀌어\n공략 지시를 ",
    (6, 4179, 1): ".\n공격",
    (6, 4205, 1): ".\n실행 가능한 제안은",
    (6, 4561, 4): "?",
    (6, 4564, 4): "?",
    (6, 4577, 4): "?",
    (6, 4579, 4): "?",
    (6, 4588, 3): ".\n처우는",
    (6, 4588, 5): ".",
    (6, 4616, 1): ".\n설마 ",
    (6, 4645, 0): " 높이 평가",
    (6, 4645, 1): "…",
    (6, 4652, 3): "?",
    (6, 4707, 1): "다면 됐소",
    (6, 4816, 3): "?",
    (7, 272, 0): "……옛 주군을 당장 잊",
    (7, 272, 1): ".\n이 또한 난세의 이치\n앞으로 잘 부탁하오",
    (7, 335, 1): ".\n당장 결단하지 못",
    (7, 2512, 0): "지원할 마음은 굴뚝같습니다",
    (7, 2512, 1):
        "만,\n더 이상 병력을 받아들일 부대가\n없는 듯하군",
    (7, 2512, 2): "…",
    (8, 293, 1): ".\n대비한 지역은\n화를 면한 듯",
    (8, 296, 1): ".\n미리 대비",
    (8, 296, 2): ".\n무사히 넘긴 지역이 있",
    (8, 298, 2): ".\n경미한 손실",
    (8, 299, 2): ".\n경미한 손실",
    (8, 300, 2): ".\n경미한 손실",
    (8, 301, 2): ".\n경미한 손실",
    (8, 302, 2): ".\n경미한 손실",
    (8, 1031, 0): "으윽, 병에 걸린 모양입니다",
    (8, 1031, 1): "…\n반드시 회복하겠습니다",
    (8, 1031, 2): ". 그러므로, 잠시 시간을…",
    (8, 1031, 3): "",
    (8, 1237, 0): "납득이 어렵습니다",
    (8, 1237, 1): ".\n",
    (8, 1237, 2): "뜻대로 하지요",
    (9, 3953, 2): "\n승산은 있",
    (9, 3953, 3): ".",
    (15, 364, 1): ".\n사관 권유는 거절당했",
    (15, 364, 2): "\n실패해 송구합니다",
    (15, 517, 2): ".\n도움도 기대",
    (15, 1383, 0): "민심은 잃습니다",
    (15, 1383, 1):
        ".\n당장이라도 병사를 내보내고자\n백성에게 병량을 징수하겠다",
    (15, 1549, 1):
        ".\n조금이라도 적의 발을 묶으려면\n",
    (15, 1570, 2): "의 야망을\n실현",
    (15, 1570, 3): "!",
    (15, 1571, 2): "의 야망을\n실현",
    (15, 1571, 3): "!",
    (15, 1614, 0): "병량이 곧 바닥입니다",
    (15, 1614, 1): "\n뜻은 아니나",
    (15, 1614, 2): "\n이만 철수하겠습니다",
    (15, 1838, 0): "여러 세력과 동맹을 맺고 있",
    (15, 1838, 1): ".\n가장 믿을 만한 상대는 ",
    (15, 1863, 0): "침략을 받았",
    (15, 1863, 1): ".\n전황은 아군 우세로 판단",
    (15, 1877, 0): "준비는 이미 모두 갖추어졌",
    (15, 1877, 1): ".\n당장 공격하고 싶은 참",
    (15, 1911, 1): ".\n그에 걸맞은 대가는 얻",
    (15, 2180, 1): ".\n들으시",
    (15, 2211, 0): "의 병량을 걱정",
    (15, 2211, 2): ".\n병량 징수는 어떻소",
    (15, 2406, 0): "양측의 전력은 팽팽히 맞섰",
    (15, 2406, 1): ".\n이미 아군 장병도 출진 준비를 마쳤\n",
    (15, 2408, 0):
        "우리 병력이 우세한 것은 분명……\n장병의 채비도 모두 갖추어졌",
    (15, 2408, 1): ".\n출진 자유를 설명",
    (6, 3763, 1):
        ".\n앞날까지 내다본 것이라면 좋은 방안이라 생각하오",
    (6, 3764, 1):
        ".\n앞날을 내다보고 신용을 쌓는 것도 좋은 선택",
    (6, 3765, 1): "에서 온 사절",
    (6, 3765, 2): "의\n도착",
    (6, 3766, 0):
        "양가 사이에 굳건한 신뢰를 쌓고자 하오…\n"
        "훗날 동맹을 맺겠다는 약속에\n동의해 ",
    (6, 3766, 1): "다면?",
    (6, 3767, 0): "때가 무르익으면, ",
    (6, 3767, 1): "과는\n손을 잡고 싶",
    (6, 3767, 2): ".\n그때는 좋은 ",
    (6, 3769, 0): "우리 가문으로서는 ",
    (6, 3769, 1): "과 관계를\n오래 이어가고 싶",
    (6, 3769, 2): ".\n",
    (6, 3769, 3): "응하",
    (6, 3769, 4): "",
    (6, 3771, 0): "수락",
    (6, 3771, 1): "\n그것이 귀가의 뜻이라면\n그대로 ",
    (6, 3849, 0): " 당주",
    (6, 3942, 1): " 측",
    (6, 3942, 2): "의\n면회 요청이 들어와 있",
    (15, 2449, 1): "은",
    (15, 2449, 2): "\n",
    (15, 2449, 3): "우리를 의심하는 모양…",
    (6, 3532, 1):
        " 스스로 제일이라니…\n아직도 실감하지 ",
    (6, 4444, 0): " 건설 의향",
    (6, 4486, 0):
        "성의 수입 기반은 군의 취락에서 나옵니다…\n"
        "장악 진척은 답보 상태",
    (8, 297, 0): "가뭄 발생에 간담이 서늘해졌",
    (8, 349, 0): "영내 태풍 피해가 발생했",
    (15, 228, 0): "승산은 낮은 편",
    (15, 284, 0): "좋은 방안",
    (15, 762, 1): "\n민심을 잃을 우려가 있",
    (15, 1384, 1): "\n민심 이반",
    (6, 1629, 2):
        "이라면, 언젠가 이 관계를 뒤집을 수 있습니다",
    (6, 3070, 3): " 뜻에 달렸습니다",
    (6, 4490, 1): ",\n마음이 잘 맞",
    (15, 1630, 0):
        "어쨌든, 일국을 다스리는 다이묘가 되신 ",
    (15, 1630, 1):
        "이라면\n어지러운 전국 난세를 아우르는 일도 꿈이 아니옵니다\n",
    (15, 1630, 2): ", 저희도 더욱 힘쓰겠나이다!",
    (15, 1707, 0): ", ",
    (15, 1709, 4):
        ", 그 지휘라면\n병사들도 용기백배하여 떨쳐 일어날 것이옵니다",
    (15, 1517, 2): " 스스로 조금이나마 지도",
    (6, 3394, 1): "?",
    (6, 3501, 1): "?\n앞으로도 한층 더 정진",
    (6, 3513, 1): "?\n기쁜 바",
    (6, 3678, 2): "에게 무슨 잘못이 있",
    (6, 3678, 3): "?",
    (6, 4244, 1): "?",
    (6, 4394, 2): "?",
    (6, 4565, 4): ", 설득해 주오",
    (6, 4565, 5): "?",
    (6, 4566, 4): ", 설득해 주오",
    (6, 4566, 5): "?",
    (6, 4580, 3): ", ",
    (6, 4580, 4): "힘을 보태 주오",
    (6, 4580, 5): "?",
    (6, 4651, 0): ", 앞으로도\n좋은 관계를 이어가고 싶",
    (6, 4651, 2): "?",
    (6, 4690, 0): "바람을 들어주시겠소",
    (6, 4690, 1): "?",
    (6, 4763, 0): "전쟁은 끝난 셈",
    (7, 884, 0): "의 분노를 산 것",
    (7, 884, 1): "?\n그렇다면 그 송곳니를 막아야 ",
    (7, 2494, 2): "?",
    (8, 404, 0): " 또 납득",
    (8, 404, 1): "?\n그런 셈",
    (15, 514, 0): " 측을 회유하",
    (15, 514, 1):
        "\n적의 경계에도 가까우니\n전시에는 쓰기 좋은 패가 되",
    (15, 819, 2): "\n잇키에 호응해 출진하",
    (15, 819, 3): "",
    (15, 1234, 1): "을 함락하려면\n땅굴 공략을\n쓰",
    (15, 1537, 3): "",
    (15, 1701, 1): "",
    (15, 1703, 1): " 확인됐",
    (15, 1703, 2):
        "?\n승진한 면면을 알아 두면\n전략에 득이리라",
    (15, 2175, 3): "?",
    (15, 2579, 0):
        "한편 우리도 적의 전선 성을 제압해\n"
        "결전의 발판으로 삼는 것이 좋겠습니다\n어느 성을 노리",
    (15, 2579, 1): "",
    (15, 2592, 0): "큭, 발을 묶지 ",
    (15, 2592, 1): "……\n",
    (15, 2593, 1): "?\n",
    (15, 2598, 1): " 와 주었",
    (6, 2074, 2): "\n다시 지침을 내리",
    (6, 2074, 3): "",
    (6, 4608, 1): "?\n",
    (8, 1239, 3): "",
    (15, 1512, 2):
        " 스스로 한번 단련시켜 주고 싶다만\n",
    (15, 1512, 3): "",
    (15, 1522, 1):
        "의 근처에 나타난 도적 무리의\n토벌을 맡겨도 ",
    (15, 1522, 2): "",
    (15, 2291, 3): "!\n원호군을 파견",
    (15, 2291, 4): "?",
}
CALL_ASSEMBLY_EXACT_REWRITES.update(
    {
        (1, 14, 0): "힘들수록 웃으십시오",
        (1, 14, 1): ". 그러고 보니 ",
        (1, 14, 2): ", 늘 한결같은 말씀이셨습니다",
        (1, 14, 3): ".",
        (2, 560, 1): "\n지략을 다해 승기를 잡읍시다",
        (6, 549, 0): "어찌하면 ",
        (6, 549, 1): "의 눈에\n들까",
        (6, 3062, 1): "과의 동맹은 ",
        (6, 3062, 3): "\n각별히 유의해 ",
        (6, 3110, 0): "…역시 서로 용납할 수 없습니다",
        (6, 3515, 2):
            "의 말석에 이름을 올리고, 이름도 조금 알려진 몸\n"
            "신분에 부끄럽지 않도록 노력",
        (6, 3535, 2): "만큼은 가족과 같습니다",
        (6, 3535, 3): "\n앞으로도 ",
        (6, 3535, 4): "에게 기대어 ",
        (6, 3555, 0): "고생이 보답받을 때가 왔습니다",
        (6, 3555, 2): "의 곁을 지킬 수 있어 행복합니다",
        (6, 3621, 1):
            " 가보를 돌려달라니…\n마음대로 해 ",
        (6, 3625, 1):
            " 가보를 돌려달라, 즉\n그런 뜻입니다",
        (6, 3627, 0): " 받을 수 있는 것",
        (6, 3627, 2):
            " 가보를 내놓는 것은\n그다지 내키",
        (6, 3631, 1):
            " 가보를 돌려드려야 한다니\n아쉽습니다",
        (6, 3954, 2): "\n꼭 ",
        (6, 4203, 1): "\n승인할지 말지 확인해 ",
        (6, 4210, 0): "에 착수",
        (6, 4261, 0): ", ",
        (6, 4424, 2):
            "의 성주로서\n성하 발전에 노력",
        (6, 4444, 0): "도 원하지만",
        (6, 4444, 1):
            "\n그에 걸맞게 상업이 진흥될 때까지\n"
            "보류합니다",
        (6, 4466, 0):
            "적성 포위라면 분명 자신 있습니다\n"
            "하지만 마음은 내키",
        (6, 4393, 1): "」 발령을 위한\n준비에 착수",
        (6, 4808, 2): "과는\n모든 관계를 끊겠습니다",
        (7, 2436, 0): "다음 성을 공격하겠습니다",
        (7, 2436, 2): "으로 향하겠습니다",
        (7, 334, 1): ". 하지만\n이번에는 거절하오",
        (8, 329, 0): "홍수 피해를 입은 곳이 ",
        (8, 1014, 2): "의 수완을 기대해 ",
        (8, 1024, 0):
            "적과의 경계에서 먼 이 땅에서는\n"
            "내정에 중점을 두는 편이 상책일 듯\n"
            "장기적인 영토 발전을 목표로 ",
        (8, 1026, 1): "\n제가 거둘 좋은 성과를 기대해 ",
        (8, 1029, 1): "\n성주인 ",
        (9, 3945, 0): "양군의 전력은 팽팽히 맞서 있",
        (9, 3946, 0): "양군의 전력은 팽팽히 맞서 있",
        (9, 3990, 0):
            "수비를 중시해\n견실하게 싸우겠습니다",
        (15, 268, 2): "에게도 한 가지 계책이 있습니다",
        (15, 269, 1):
            " 스스로 바테렌에게서 한 가지 방안을 얻었",
        (15, 643, 1):
            " 쪽은 이제\n운명을 함께하는 사이옵니다\n"
            "속히 휘하에 들여야 할 듯하옵니다",
        (15, 1200, 0): "과의 관계 개선은\n",
        (15, 1200, 1): "에 ",
        (15, 1200, 2): "\n금전에 걸맞은 성과를 증명",
        (15, 1450, 0):
            " 근처는 경비가 허술한 모양\n출병용 병량을 불태워\n",
        (15, 1450, 1): "의 전력을 감소",
        (15, 1486, 0):
            "의 거취는 유언비어로\n망설이는 모양\n"
            "이참에 그자를 빼내자고 건의",
        (15, 1502, 1):
            "에서는\n불온한 움직임이 있습니다",
        (15, 1502, 2): "\n잇키를 경계해야 합니다",
        (15, 1541, 0): "유망한 낭인은 발견하지 못했습니다",
        (15, 1541, 1):
            "……\n싸움에서 사로잡은 다른 가문의 자를 설득하는 등\n"
            "다른 길을 모색해야겠습니다",
        (15, 1615, 1): "을 공략하기는 어렵습니다",
        # Ghidra proves that parenthesized particles are copied verbatim; the
        # runtime VM does not select a Korean allomorph.  Recast every mixed
        # selector boundary through a particle-neutral carrier.
        (6, 4572, 0): ", 「",
        (7, 2397, 0):
            " 정도라면\n차지해도 손해 볼 건 없지!",
        (7, 2723, 1): " 정도라면 당연한 활약이지",
        (8, 758, 0):
            "의 경우라면\n수해도 막을 수 있겠지요",
        (8, 764, 0):
            "의 경우라면 수해에도\n제법 견딜 수 있을 듯합니다",
        (8, 766, 0):
            "의 경우라면\n수해 걱정도 없겠구나",
        (9, 1511, 0):
            "인 줄은 몰랐군……\n기뻐해야 할지 탄식해야 할지",
        (9, 1573, 0):
            "에게라면\n맡길 수 있겠지",
        (9, 1769, 0):
            "에게 맞서라고!?\n반드시 베겠다!",
        (9, 2307, 0):
            " 말인가?\n이렇게까지 당하는 건가?",
        (9, 2356, 0):
            " 말인가?\n이름뿐이잖아!",
        (9, 2365, 0):
            " 말인가……?\n웃기는구나!",
        (9, 2397, 0):
            " 따위는\n결국 허풍이잖아?",
        (9, 2408, 0):
            " 관련 소식이라기에\n무엇인가 했더니",
        (9, 4134, 0):
            " 부대가 격파되어\n수비의 핵심을 상실",
        (15, 319, 1): "\n이름이 ",
        (15, 319, 2):
            "인 자 등, 벌써\n승전보를 들은 듯하",
        (15, 325, 1): "을 저버렸는지\n이름이 ",
        (15, 325, 2):
            "인 자가 출분하여\n우리 가문에 사관하기를 바라며",
        (15, 326, 1): "을 저버렸는지\n이름이 ",
        (15, 326, 2):
            "인 자들이 출분해\n본가에 사관하길 바라고 있",
        (15, 355, 0):
            "—그렇게 불러 주십시오\n인연이 닿아 ",
        (15, 358, 0):
            "—그렇게 불러 주시옵소서\n"
            "이번에 말석에 들게 되었사오니\n"
            "어떠한 일이라도 맡겨 주시옵소서",
        (15, 360, 0):
            "—그게 제 이름입니다\n"
            "부족한 점도 많겠지만\n최선을 다하겠습니다!",
        (15, 440, 1):
            "—그렇게 불러 주시옵소서\n",
        (15, 443, 1):
            "입니다\n앞으로 잘 부탁드리옵니다",
        (15, 445, 1):
            "—그렇게 불러 주시옵소서\n"
            "부족한 몸이오나 아무쪼록 잘 부탁드리옵니다",
        (15, 924, 2):
            ", 그곳이 급소로 판단되므로\n"
            "미리 성벽을 무너뜨려 두고자 하옵니다",
        (15, 929, 2):
            ", 그곳이 급소로 판단되므로\n"
            "미리 성벽을 무너뜨려 두고자 하옵니다",
        (15, 1416, 0):
            "—그렇게 불러 주십시오\n인연이 닿아 ",
        (15, 1419, 0):
            "—그렇게 불러 주시옵소서\n"
            "이번에 말석에 들게 되었사오니\n"
            "어떠한 일이라도 맡겨 주시옵소서",
        (15, 1421, 0):
            "—그게 제 이름입니다\n"
            "부족한 점도 많겠지만\n최선을 다하겠습니다!",
        (15, 1434, 0):
            "—그렇게 불러 주십시오\n인연이 닿아 ",
        (15, 1437, 0):
            "—그렇게 불러 주시옵소서\n"
            "이번에 말석에 들게 되었사오니\n"
            "어떠한 일이라도 맡겨 주시옵소서",
        (15, 1439, 0):
            "—그게 제 이름입니다\n"
            "부족한 점도 많겠지만\n최선을 다하겠습니다!",
        (15, 2093, 0):
            "이 상대……\n공략할 성을 고르는 것이 고민",
        (15, 2093, 2): " 방책이라도……",
        (15, 2095, 1):
            "이 상대인가\n우선은 ",
        (15, 2594, 2): "과 결판을 냅시다",
        (6, 4468, 0): "공성의 요체를 잘 알고 있습니다",
        (6, 4468, 2): "에는 적임자를 배치해도",
        (6, 4468, 3): "\n손해는 없다",
        (6, 4819, 0):
            "\n가재로 임명합니다\n계속하시겠습니까?",
        (6, 4820, 1):
            "\n종속 다이묘 가재로 임명합니다\n계속하시겠습니까?",
    }
)

# Reviewed suffix-boundary repairs.  The coordinate sets are explicit; the
# operation removes only the duplicated Korean lexeme immediately before a
# runtime call that already emits that lexeme.
CALL_ASSEMBLY_SUFFIX_TRIMS = {
    **{
        (6, record_id, literal_id): "하"
        for record_id in range(2161, 2173)
        for literal_id in (0, 1)
    },
    **{
        coordinate: "하"
        for coordinate in (
            (6, 3517, 1), (6, 3774, 0),
            (6, 3779, 0), (6, 3804, 2), (6, 3851, 4),
            (6, 3871, 0), (6, 3943, 0), (6, 3946, 0),
            (6, 3948, 0), (6, 3949, 0),
            (6, 4258, 0), (6, 4396, 2), (6, 4399, 0),
            (6, 4507, 0),
            (7, 335, 0), (7, 756, 2), (7, 2456, 2),
            (7, 2836, 2), (7, 2869, 2), (7, 2870, 3),
            (8, 949, 2), (8, 996, 2), (8, 1009, 0),
            (9, 3950, 1), (9, 3992, 0),
            (15, 1014, 1), (15, 1382, 1),
            (15, 1452, 0), (15, 1854, 1),
            (15, 2287, 2), (15, 2321, 1), (15, 2405, 2),
        )
    },
    **{
        coordinate: "주"
        for coordinate in (
            (6, 3952, 3), (6, 4470, 1), (6, 4473, 0),
            (6, 4491, 0), (6, 4494, 1), (7, 221, 1),
            (7, 222, 1), (8, 1238, 2), (15, 1530, 1),
        )
    },
    **{
        coordinate: "없"
        for coordinate in (
            (6, 3851, 0), (7, 331, 0),
            (15, 1567, 3), (15, 2572, 3),
        )
    },
}

# The morphology pass below is based on every Cartesian branch rendered from
# the post-remediation PK candidate.  These are the literal owners behind the
# selector-parent findings; repairing the owners eliminates every inherited
# occurrence without touching selector topology.
CALL_ASSEMBLY_EXACT_REWRITES.update(
    {
        (1, 13, 0): "힘들 때일수록 웃",
        (1, 17, 0): ", 벌써 벚꽃철이네",
        (2, 624, 0):
            ", 언제나 배웅해 줘서 고맙다\n싸움의 승리를 그대에게 바치마",
        (6, 2866, 1): "!\n잊지 마라",
        (6, 3414, 0): ", 안심하고 ",
        (6, 3414, 3): "의\n목숨을 걸고 수호",
        (6, 3413, 0):
            "이런, 살 날이 얼마 남지 않은 몸으로 무거운 짐을\n"
            "지게 될 줄이야… 허나\n",
        (6, 3514, 0):
            " 스스로 훈공 1위라…\n모두가 이를 지켜봅니다",
        (6, 3520, 1): "…그 일념뿐",
        (6, 3527, 0): ", 더 일하",
        **{
            (6, record_id, 1):
                "\n정전이 끝나면 상대 영내에 주둔한 병력을 철수"
            for record_id in range(3721, 3733)
        },
        (6, 3734, 0): "와의 정전 기일이 되었",
        (6, 3734, 1): "\n빈틈을 보이지 않도록 주의",
        (6, 3852, 2): "",
        (6, 3864, 0):
            " 직책으로 임명된다는 소식을 들으면\n"
            "틀림없이 기뻐 춤춥시다",
        (6, 3885, 1): "\n즉시 실행합시다",
        (6, 3943, 0): "이 동맹을 요청했",
        (6, 3946, 0): "이 혼인 동맹을 요청했",
        (6, 3949, 0): "이\n우리 가문에 신종하고 싶다고 말했",
        (6, 4029, 1): "\n병력은 백중세",
        (6, 4249, 0):
            " 정책을 실행하려면\n일손이 충분하지 ",
        (6, 4258, 0): "금전 부족으로 모든 정책이 중단됐",
        (6, 4469, 1):
            " 자신을 두어 정무를 충실히 한다…\n그 의도는 이해",
        (6, 4563, 4): " 직접 설득해 ",
        (6, 4640, 3): "\n항복할 방안이 있습니까",
        (6, 4646, 1): "…\n우리 가문에 와 주길 바라는 바",
        (6, 4706, 0): "설마…\n말씀하신 보람이 있소",
        (6, 4717, 2): "\n다시 만날 곳은 전장일지도 모르",
        (6, 4726, 0): "이걸로 잘된 듯",
        (6, 4766, 0): "이토록 해 주시니 외면할 수 ",
        (6, 4895, 0): "이라면 약속대로요",
        (7, 273, 0):
            "우리 가문이 천하를 다스릴 길은 끊겼",
        (7, 327, 1): "\n악행부터 돌아보면 ",
        (7, 830, 1):
            "」에 가망이 없다고 보고\n출분자가 있는 모양",
        (7, 830, 2): "\n등용할 기회일지도 모르지 ",
        (7, 2599, 1):
            "!\n다케다 기마대의 용맹을\n똑똑히 깨달았으리라",
        (7, 2608, 0): "첫 공은 ",
        (7, 2608, 1): "!\n모두 ",
        **{
            (8, record_id, 1):
                "개로,\n병량 조달에 차질이 생겼"
            for record_id in range(288, 293)
        },
        (8, 328, 1): "의 영내에서도\n물에 잠긴 곳",
        (8, 330, 0): "영내에 홍수 피해를 입은 곳",
        (8, 330, 2): ".\n주의!",
        (8, 949, 1): "\n과연, 좋은 안이라 사료",
        (8, 993, 0): "영지, 맡았",
        (8, 999, 0): "이 땅, 맡았",
        (8, 999, 3):
            " 시설을 건설하여\n임지를 활성화해야 한다",
        (8, 1005, 0): "영지, 맡았",
        (8, 1011, 0): "영지, 맡았",
        (8, 1019, 0): "그 성, 맡았",
        (8, 1027, 0): "그 성, 맡았",
        (8, 1113, 0):
            "게히의 신들이 좌정한 한\n본가의 영토는 반석",
        (9, 2340, 1): " 군…!",
        (9, 3950, 2): "\n협격과 사격도 활용",
        (15, 262, 0): "선동의 건, 잠시 ",
        (15, 262, 1): "\n",
        (15, 262, 2):
            " 스스로 다니며 곳곳의 동지를 모으고\n잇키를 선동하",
        **{
            (15, record_id, 0): "큰일"
            for record_id in range(474, 486)
        },
        (15, 903, 0):
            "공성전을 생각하신다면 출병하기\n전에 써야 할 계책",
        (15, 1382, 0): "병량 생산 효과를 지닌 군을 성장",
        (15, 1548, 2): " 부대에 철수 명령",
        (15, 1550, 1): " 부대에 철수 명령",
        (15, 1551, 2): " 부대에 철수 명령",
        (15, 1554, 2): " 부대에 철수 명령",
        (15, 1582, 0):
            " 아래 군에서\n간자가 있다는 보고를 얻었",
        (15, 1582, 1): "\n병사를 내면 방해하겠",
        (15, 1585, 0): "준비를 모두 갖추었",
        (15, 1657, 0): "영주가 없는 군",
        (15, 1700, 1): "도\n반드시 승리할 수 있겠",
        (15, 2196, 1):
            "에\n새 시설을 건설할 수 있게 되었",
        (15, 2204, 1):
            "에\n새 시설을 건설할 수 있게 되었",
        (15, 2287, 1): "\n군의 후 ",
        (15, 2435, 0): "목표 횟수만큼 공략지를 제압했",
        (15, 2437, 0): "목표를 달성했",
    }
)

# The exact rewrites above supersede four earlier "하다" suffix removals.
for _coordinate in (
    (6, 3943, 0),
    (6, 3946, 0),
    (6, 3949, 0),
    (6, 4258, 0),
):
    CALL_ASSEMBLY_SUFFIX_TRIMS.pop(_coordinate, None)

# Direct-render v5 blind-spot owners not covered by the morphology pair gate.
CALL_ASSEMBLY_EXACT_REWRITES.update(
    {
        (2, 559, 1): "\n상대로 부족함은 ",
        (2, 642, 1): "\n상대로 손색이 ",
        (2, 133, 0): "안심하시오, ",
        (2, 137, 0):
            "이런, 살 날이 얼마 남지 않은 몸으로 무거운 짐을\n"
            "지게 될 줄이야… 하지만\n",
        (6, 4177, 0):
            "전선의 병력이 부족해\n공략할 수 있는 세력이 ",
        (6, 4182, 0): "주변에 공략할 수 있는 성이 ",
        (6, 4182, 1): "\n군단 방침을 제시하여 ",
        (6, 4183, 0): "주변에 공략할 수 있는 성이 ",
        (6, 4183, 1): "\n내정을 추진하고 있으며 ",
        (6, 4183, 2): " 주도로\n",
        (6, 4183, 3): "명이 지행지를 장악 중",
        (6, 4025, 1):
            "\n병력은 우위이나, 위신에서 뒤져\n"
            "병사가 힘을 쓰지 ",
        (6, 4456, 0):
            " 군을 맡을 수 있다면\n영지에 대한 불만 따위\n품을 리가 ",
        (6, 4592, 3): "의 힘이 미치지 못해\n면목이 ",
        (6, 4493, 1): "라면 솜씨를\n제대로 쓰지 ",
        (6, 4615, 1): "만…\n이번에는 ",
        (6, 4712, 0): ", 약점을 잡히다니…\n기간을 연장해 ",
        (6, 4712, 1): "다는 말",
        (6, 4745, 2): " 곁에\n서서 온 힘을 다하",
        (6, 4657, 0): "지금 대우로는 출사할 마음이 ",
        (6, 4659, 0): "특별히 바라는 것은 ",
        (6, 4661, 0): "딱히 바라는 것은 ",
        (6, 4661, 1): "\n포상을 ",
        (6, 4661, 2): "약속해 ",
        (6, 4661, 3):
            "다면\n약속에 힘입어 노력하",
        (6, 4665, 0): ", 딱히 간절히 바라는 것은 ",
        (6, 4665, 1): "만\n성공한 뒤 포상을 약속해 ",
        (6, 4667, 0): "딱히 간절히 바라는 것은 ",
        (6, 4916, 2): "\n지금은 교섭할 사안이 ",
        (7, 277, 0): "에게 입은 은혜가 있",
        (7, 330, 1): "만은 무릎 꿇",
        (7, 829, 0):
            "이 이토록 쇠퇴하다니……\n"
            "이대로 계속 섬겨도 앞날은 ",
        (7, 829, 1): "\n충성을 다하는 것도 여기까지로 ",
        (7, 992, 2): " 훌륭하군\n",
        (7, 992, 3): "도 제법",
        (7, 994, 2): " 훌륭하군\n",
        (7, 994, 3): "도 제법",
        (7, 2489, 0):
            "목표를 향해 새로 출진할 수 있을 듯한\n부대가 ",
        (8, 307, 0): "의 영지에서\n가뭄 든 땅이 있",
        (8, 307, 1):
            "\n백성과 땅이 가뭄에 신음",
        (8, 306, 0): "의 영내가 가뭄에\n시달렸",
        (8, 306, 1): "\n이것을 방치하는 것은 ",
        (8, 1018, 0):
            "성주로서 내 무예를 떨칠 수 있다니\n감사의 말도 ",
        (12, 16, 0):
            "\r\n이 땅을 손에 넣게 되다니\r\n실로 경사스러운 일",
        (9, 1830, 0): "무사를 빈다",
        (9, 1830, 1): "…",
        (9, 4132, 1):
            " 등으로 방비를 굳히는 듯합니다…\n"
            "준비가 끝나기 전에 파괴하면\n"
            "계획이 어긋난 성 안에서는 항복을 생각할 것",
        (9, 4142, 4): "에게 이 자리에서 포박을 명",
        (15, 1412, 0):
            "우리 성과 같은 전선에서야말로 제 힘을 발휘할\n"
            "싸움에 능한 낭인을 알고 있",
        (15, 1412, 1): "\n말을 거는 것이 ",
        (15, 1476, 0): "만큼 모략에 어두운 ",
        (15, 1828, 1): "보고할 사항은 ",
        (15, 1855, 0): "이미 전기가 무르익었",
        (15, 1855, 2):
            "으로 침공을 개시하면\n승산은 높을 것",
        (15, 2406, 0): "양측 전력은 팽팽했습니다",
        (15, 2406, 1):
            ".\n아군 장병도 출진 준비를 마쳤습니다\n",
        (15, 2573, 2):
            "과 자웅을 겨룰 때입니다\n부디 ",
        (15, 2321, 0):
            "바란 대로 영지를 옮겨 주시니\n감사는 끝이 ",
        (17, 345, 1):
            "님……도요토미의 세상은 곧\n"
            "끝난다. 왜 그토록 매달리는가",
        (2, 131, 0):
            "、지금까지 당가의 주인으로서의 소임\n참으로 수고하",
        (2, 131, 2): "에게 ",
        (2, 145, 2): "으로 개명",
        (6, 4602, 0): "이럴 수가 ",
        (6, 3489, 1):
            "만큼은 가족이나 다름없지\n앞으로도 ",
        (7, 2880, 0): " 거점: ",
        (6, 4212, 2): "지시를 청",
        (6, 4472, 1):
            " 못지않은 특성을\n지닌 이가 있어, 그 점은 강점입니다\n"
            "다만 인선은 재고해 주시길 청",
        (6, 4607, 1): "의 방문이라니 놀랍",
        (6, 4607, 2): "\n그토록 ",
        (6, 4607, 3): "의 가르침이 필요",
        (6, 4716, 1): ", 별수 ",
        (7, 1722, 0): "에서\n",
        (8, 1081, 1):
            "\n하마터면 섣부른 짐작만으로\n전쟁 날 뻔했소",
        (15, 386, 1):
            ":\n불만을 토로한다고 합니다\n"
            "조략을 걸 때인지도 모릅니다",
        **{
            (15, record_id, 3):
                " 계책이 밀명이었다니……\n하마터면 큰일 날 뻔하"
            for record_id in (914, 980, 1137, 1284, 1379, 1459, 1500)
        },
        (15, 818, 1): "에서 온 ",
        (15, 831, 0): "에서 ",
        (15, 987, 1): "의 ",
        (15, 1294, 1): "의 ",
        (15, 1469, 1): "에서 온 ",
        (15, 1586, 2): "공략합시다",
        (15, 1627, 0):
            "이 반슈는 서국과 교토를 잇는 요충지\n"
            "구니별 지방관직 가운데 하리마노카미는 이요노카미와 함께\n"
            "가장 격이 높다고 일컬어졌",
    }
)

# Independent 5,779-signature linguistic triage: UI wrap repair plus the
# first direct/jump-owner batch.  These rewrites preserve every VM edge while
# placing Korean word boundaries in the fixed literal that owns each join.
CALL_ASSEMBLY_EXACT_REWRITES.update(
    {
        (4, 29, 0):
            "【AI 호전도】\n"
            "타 세력의 호전도를 설정합니다\n"
            "높을수록 적국을 침공하기\n"
            "쉬워집니다",
        (1, 11, 0): ".",
        (1, 11, 2): "이후 일정이 있으니,",
        (1, 11, 3): " 이 일은 여기까지 ",
        (1, 11, 4): ".",
        (1, 19, 0): ". 공은 ",
        (1, 19, 1): "가 ",
        (1, 19, 2): ".",
        (1, 20, 2): "! 에잇, 그곳을 ",
        (1, 21, 1): "…그렇게 ",
        (1, 21, 2): ".",
        (1, 25, 0): "! 이제 ",
        (1, 25, 1): ", 애송이는 아니오",
        (1, 27, 0): "이를 공략하기",
        (1, 27, 1): " 어려운 성을 함락했도다!",
        (2, 105, 0):
            "드디어 머리 올리는 의식도 마쳤으니\n앞으로는 ",
        (2, 109, 0):
            "、찾아뵈었습니다.\n"
            "머리 올리는 의식도 끝나, 이제부터는 ",
        (2, 127, 1): "\n부디 뒷일은 ",
        (2, 256, 0): "타 가문을 설득하는 ",
        (2, 444, 0): "기마와 철포에 뛰어난 ",
        (2, 517, 0):
            "무가라 해도 풍류를 빼놓을 수 없지.\n"
            "풍류를 아는 마음으로 ",
        (2, 632, 0): "여기는 내게 맡겨 줘!\n이 화승총으로 ",
        (2, 633, 0):
            "적은 서국무쌍의 무장으로 이름 높은 ",
        (6, 666, 0):
            "요즘 마을 젊은 것들은…\n옛날에는 더…",
        (6, 1590, 1): " 측은\n나 같은 ",
        (6, 2255, 0):
            "여기에 나타난 배짱은 높이 사주마\n그것이 ",
        (6, 2259, 0): "철포대가 ",
        (6, 2978, 0):
            "송백의 지조라 하지. 이럴 때\n지조가 굳건한 ",
        (6, 3369, 0): "군단장인 ",
        (6, 3375, 0): "설마 군단장인 ",
        (6, 3377, 0): "군단장인 ",
        (6, 3398, 0): ", 뒷일은 내게 ",
        (6, 3400, 1): ", 뒷일은 ",
        (6, 3400, 2): ".\n반드시 ",
        (6, 3403, 1): "\n부디, 뒷일은 ",
        (6, 3415, 0): "뒷일은 ",
        (6, 3415, 1): ".\n반드시 ",
        (6, 3430, 0):
            " 스스로 훈공 1위라…\n아랫사람들의 활약도 ",
        (6, 3431, 1):
            "만 1위인가요……\n"
            "부끄럽지만 매우 영광입니다.\n"
            "올해도 ",
        (6, 3434, 0):
            " 스스로 훈공 1위라 해도 놀랄 일은 아니다\n"
            "오히려 놀라운 것은 이토록 낮은 자에게\n"
            "공을 세울 기회를 내린 ",
        (6, 3438, 0): "말단인 ",
        (6, 3438, 1):
            "스스로 제일인가\n제법 총애를 받고 있는 모양이군",
        (6, 3476, 0): "당가에서 ",
        (6, 3480, 0): "의 ",
        (6, 3498, 0): "정상에 올랐는가…\n기회를 준 ",
        (6, 3521, 1):
            "\n오히려 놀라운 것은 이처럼 아랫사람에게\n"
            "공을 세울 기회를 주신 ",
        (6, 3536, 1):
            ", 비할 데 없다고…\n"
            "먼 나라에까지 이름을 떨칠 활약을 ",
        (6, 3590, 0): "로서 ",
        (6, 3593, 1): "로서 ",
        (6, 3626, 0): " 가보, ",
        (6, 3851, 2): "\n이번에는 ",
        (6, 3888, 2):
            "\n허투루 하지 않고 후세에 남길 수 있는 것으로 ",
        (6, 3931, 2): " 시설을 ",
        (6, 3931, 3): "에게 내린다",
        **{
            (6, record_id, 0):
                "공략에는 그만한 각오가 필요할 듯합니다.\n"
                "병력이 충분치 않으니 조략도 활용하면서\n"
                "만반의 준비를 "
            for record_id in range(4008, 4020)
        },
        (6, 4205, 1): ".\n실행 가능한 제안은 ",
        (6, 4206, 0):
            "운용할 수 있는 금전이 적어서인지\n유효한 제안은 ",
        (6, 4207, 0):
            "동원할 수 있는 노동력이 적어서인지\n유효한 제안은 ",
        (6, 4416, 0): "에는 ",
        (6, 4436, 0): "인원이 부족하여 ",
        (6, 4477, 0):
            "전선이야말로 제 특성이 빛을 발할 곳입니다\n"
            "부디 그 땅을 ",
        (6, 4481, 0): "부디 이 땅을 ",
        (6, 4484, 0):
            "취락 장악은 제 특기입니다\n부디 이 땅을 ",
        (6, 4484, 1): "에게!\n단숨에 끝내",
        (6, 4588, 3): ".\n처우는 ",
        (6, 4590, 1): "\n굳이 더 교섭할 필요는 ",
        (6, 4599, 2): "의 방문이라니",
        (6, 4599, 3): "…\n",
        (6, 4599, 5): " 대화를 고대",
        (6, 4611, 3): "\n이번의 관대한 ",
        (6, 4649, 1): "\n그래도 보답은 하기로 ",
        (6, 4675, 0): "이제야 처지를 아시는 ",
        (6, 4749, 0): "적이었던 ",
        (6, 4750, 0): "적이었던 ",
        (6, 4769, 1): ", 좋은 합의였",
        (6, 4791, 1): "\n영지를 얻는 것이야말로 ",
        (6, 4818, 0): "개월 이내에 ",
        (6, 4842, 0): "목표를 정해 ",
        (6, 4903, 0): "평정중 임명",
        (6, 4903, 1): "\n깊이 감사",
        (6, 4937, 2): "하지만 우리도 뜻을 굽힐 수 없",
        (6, 4937, 3): "\n양도할 수 ",
        (7, 876, 0):
            "경박한 의를 떠벌리며 난동을 부리다니, 구제할 길이 없다\n"
            "백성을 짊어진 ",
        (7, 1380, 0):
            "따위의 허약한 성에\n"
            "우리의 온 힘을 쏟아부으면 어찌 될지\n"
            "볼 만하겠구나",
        (7, 2439, 0): "그럼 앞으로의 행동을 ",
        (7, 2441, 1): "\n앞으로의 행동을 ",
        (7, 2443, 0): "그럼 앞으로의 행동을 ",
        (7, 2453, 0): "지원은 ",
        (7, 2482, 1): "\n직접 지시를 ",
        (7, 2488, 1): "\n속히 진압하라",
        (7, 2496, 1): "\n이번 출진에서는 ",
        (7, 2496, 2): "도움이 되지 못할 것",
        (7, 2500, 0): "의 방어라면\n우리 군단에도 ",
        (7, 2501, 0): "의 격파라면\n우리 군단에도 ",
        (7, 2514, 0): "이번 출진에서는\n우리 군단이 ",
        (7, 2786, 0): "장하도다, 장하도다!\n이것이 ",
        (7, 2873, 1): "\n이 일은 우리 군단에 ",
        (7, 2875, 2): " 기대하라",
        (8, 271, 0): "흉작에도 끄떡없는 지역",
        (8, 272, 0): "올해에는 흉작",
        (8, 272, 1):
            ",\n유비무환의 덕으로\n피해를 면한 지역",
        (8, 295, 1):
            "만\n이에 대비한 지역에서는\n이렇다 할 피해가 ",
        (8, 331, 0): "홍수 피해가 있었",
        (8, 532, 0): "이것이 ",
        (8, 636, 0): "에게는 ",
        (8, 1108, 1): "에 계신 도요 상인의 ",
        (8, 1171, 0): "아아\n찬란히 빛나던 ",
        (8, 1181, 1):
            "은 해신을 모신 신사이니\n"
            "다시 활기를 띠면\n"
            " 그 영험도 더욱 커질 듯한데……",
        (9, 787, 0): "이곳은 ",
        (9, 1121, 0): "요지는 ",
        (9, 1133, 0): "설비는 ",
        (9, 2522, 0): "이번에는 ",
        (9, 2522, 1): "에게\n한 수 겨루기를 청하옵니다",
        (9, 2529, 0): "싸움터의 ",
        (9, 3507, 1): "\n여기서는 물러날 수밖에 ",
        (9, 4144, 2): "과 ",
        (13, 94, 0): "가신 중에서는 ",
        (13, 113, 2): "\"에게 선봉의 소임을 ",
        (13, 162, 0): ", ",
        (13, 163, 0):
            "성은 성주가 다스리는 것이 기본입니다\n본거지는 ",
        (13, 164, 0):
            "성은 성주가 다스리는 것이 기본입니다\n본거지는 ",
        (15, 270, 2): "\n이 일은 고귀한 혈통의 ",
        (15, 384, 2): "실행 ",
        (15, 385, 0): "의 ",
        (15, 387, 0):
            "에 이변이 있었던 모양\n불만스러운 ",
        (15, 388, 1): "의 ",
        (15, 390, 1): "의 ",
        (15, 391, 0): "의 ",
        (15, 392, 0): "의 ",
        (15, 393, 0): "의 ",
        (15, 434, 1): "!\n당장 그자를 ",
        (15, 538, 1): " 회유도 막바지군!\n그들이 ",
        (15, 587, 0): " 측을 회유했습니다\n전시에는 ",
        (15, 587, 1):
            " 측에 가세한다는군요\n적은 병력이라도 고마운 일입니다",
        (15, 691, 1): " 군은 ",
        (15, 701, 1): " 군은 ",
        (15, 808, 0): "이 위협이 되어\n인근의 ",
        (15, 812, 0): "제 군단에 선동을 ",
        (15, 926, 1):
            "의 성벽에 공작을 벌여\n"
            "공략을 돕겠습니다",
        (15, 937, 0):
            "과연 공성에 필요한 것은 지혜\n"
            "이 일은 경험이 풍부한 ",
        (15, 1066, 0):
            "을 서둘러 수복해야 할 듯하옵니다\n"
            "이곳은 적지와 가까우니\n"
            "빈틈을 보여서는 ",
        (15, 1141, 1):
            "…\n뭐, 뒷문이 없다면 만들면 될 일",
        (15, 1198, 0): "과의 관계를\n개선할 길이 있",
        (15, 1297, 0): "에 병력을 보충해야 하오\n이제부터 ",
        (15, 1478, 0):
            "만큼은 우리 가문에 꼭 필요한 인재\n"
            "주군을 의심하게 만들어\n"
            "빼내기를 위한 한 수로 ",
        (15, 1479, 0):
            "만큼은 걸물로 이름난 자\n"
            "속임수를 써야 하더라도\n"
            "우리 가문에 들일 가치가 있",
        (15, 1483, 3):
            "\n유언비어를 철석같이 믿고 있",
        (15, 1483, 4): " 듯",
        (15, 1540, 3): "의 ",
        (15, 1702, 0): "시간이 나면\n꼭 ",
        (15, 1702, 2): "에 ",
        (15, 1799, 1):
            ". 듣고 싶어지면 언제든지\n"
            "「평정」의 「공략 방침」을 열어\n"
            "「진언」에서 ",
        (15, 1873, 1): "만\n결코 경계를 늦춰서는 ",
        (15, 1875, 2):
            " 등 주력 장수는\n결코 경계를 늦춰서는 ",
        (15, 1969, 1): "\n결과를 ",
        (15, 2005, 1): "\n일 가능성이 없지는 ",
        (15, 2193, 1): "에 새 시설을\n지을 수 있",
        (15, 2233, 1):
            "、궁리에는 잠시 시간이 필요하니…\n"
            "낭보를 잠시만 기다려 ",
        (15, 2285, 0): "헌언의 ",
        (15, 2309, 0): "전선으로 가려는 자가 있",
        (15, 2311, 0): "후방으로 가려는 자가 있",
        (15, 2313, 0): "후방으로 가려는 자가 있",
        (15, 2404, 1): "\n판단은 ",
        (15, 2444, 2): "\n보복을 위해 이번에는 ",
        (17, 165, 2): "와의 싸움은 ",
        (17, 217, 2): " 측이 맞서 나왔군\n고사에 따라 결전의 땅은 ",
        (17, 251, 0): "저 깃발은 ",
        (17, 362, 0): "놈이 ",
        (17, 363, 0): "군이 움직인 ",
        (17, 381, 1): "님은 우리와 ",
        (17, 382, 0): "군이 움직인 ",
        (17, 416, 0): "의 움직임인가!\n우리도 ",
        (17, 435, 0): "이번 싸움은 ",
        (17, 435, 2): "님에게 승산이 있다고 보았다!\n내 적은 ",
        (17, 437, 0): "설마 이번 싸움에서 ",
        (17, 437, 2): "가 이기는가!?\n이대로는 ",
        (17, 446, 3):
            "의 편에 서다니……\n우리 힘만으로 ",
        (17, 548, 0): "이런 곳에 ",
        (17, 603, 0): "성안으로 돌입하라!\n우리 손으로 ",
        (17, 615, 0): "하지만 지금은 ",
        (17, 696, 0): "사나다 유키무라 ",
        (17, 696, 1): "부대와 ",
        (17, 696, 2): "오타니 요시하루 ",
        (17, 893, 0):
            "아침 안개도 우리의 이동을 가려 주었다\n하늘은 ",
        (17, 934, 1): "……네가 ",
        (17, 1020, 0): "부대를 ",
        (17, 1021, 0): "부대를 ",
        (17, 1022, 0): "부대를 ",
        (17, 1067, 0): "강 건너편에 ",
    }
)

# The reviewed PK 15:2321 sentence now carries the verb stem required by the
# future-intent terminal family, so the earlier generic ``하다`` trim no
# longer applies to this owner.
CALL_ASSEMBLY_SUFFIX_TRIMS.pop((15, 2321, 1), None)

CALL_ASSEMBLY_SUFFIX_REPLACEMENTS = {
    (6, 3856, 0): ("되", "됐"),
    (6, 4023, 1): ("되", "됐"),
    (8, 1033, 0): ("되", "됐"),
    (15, 1704, 1): ("되", "됐"),
    (15, 1706, 1): ("되", "됐"),
    (6, 3794, 0): ("알겠", "이해"),
    (6, 3796, 0): ("알겠", "이해"),
    (6, 3829, 0): ("알겠", "이해"),
}
CALL_ASSEMBLY_SUFFIX_REPLACEMENTS.update(
    {
        (6, record_id, 0): ("않", "않았")
        for record_id in (
            *range(3696, 3709),
            *range(3721, 3733),
        )
    }
)

# Bound-noun pass from the current PK call-assembly surface.  These literals
# own the static side of a dynamic noun join; the VM does not insert spaces.
CALL_ASSEMBLY_EXACT_REWRITES.update(
    {
        (2, 120, 0):
            " 등과의 혼인 동맹을\n"
            "파기하게 됩니다만 괜찮으시겠습니까?",
        (6, 598, 0): " 따위는\n마음껏 짓밟아 주어라",
        (6, 631, 0): " 놈\n우리 가문을 표적으로 삼았는가",
        (6, 635, 0): " 놈…\n수상한 움직임을",
        (6, 641, 0): " 놈은\n금방이라도 쳐들어오겠구나",
        (6, 827, 0): " 따위는\n안중에도 없다",
        (6, 1521, 1): " 측과 친선 중지",
        (6, 1552, 1):
            " 따위와 함께 갈 수 없다는\n"
            "뜻은 충분히 납득하였사옵니다",
        (6, 1563, 0):
            " 놈, 단교하다니!\n우리 가문을 우롱한 처사입니다. 이럴 때는\n"
            "그 무리를 응징해야 합니다",
        (6, 1569, 0):
            " 놈이 단교했다니!\n우리 가문의 이름에 먹칠한 대가를\n"
            "치르게 해야 분이 풀리겠습니다",
        (6, 1574, 1):
            " 따위에게\n얕보일 까닭은 없습니다.\n"
            "군사를 내서라도 짓눌러야 합니다",
        (6, 1576, 0):
            " 따위가 우리 가문에 반기를 들다니.\n"
            "이를 용서하면 위신이 서지 않으니\n"
            "군사를 내서라도 제압해야 합니다",
        (6, 1583, 0):
            " 놈, 단교하다니\n용서할 수 없는 짓이다. 반드시 그 대가를\n"
            "치르게 해야 하겠구나",
        (6, 2457, 1): " 따위를\n의지하는 게 아니었어!",
        (6, 2694, 1):
            " 측과 겨뤄 보고 싶지만\n"
            "지금의 좋은 관계를 깨고 싶지는 않군",
        (6, 2728, 0):
            " 놈, 우리 가문을 복종시키니 흡족하냐\n"
            "언젠가 하극상을 일으키고 말겠다",
        (6, 2742, 0):
            " 따위는 전쟁으로 끝장내\n"
            "버리고 싶지만 그리 쉽게 되진 않겠군",
        (6, 2792, 0): " 측이 당가 산하로",
        (6, 2916, 1): " 놈!\n우리를 배신했구나!",
        (6, 2921, 1): " 놈!\n지금까지의 은혜를 잊었느냐!",
        (6, 2923, 0): " 놈!\n이 굴욕은 전장에서 씻겠다!",
        (6, 2928, 1): " 놈!\n우리를 배신했구나!",
        (6, 2933, 1): " 놈!\n지금까지의 은혜를 잊었느냐!",
        (6, 2935, 0): " 놈!\n이 굴욕은 전장에서 씻겠다!",
        (6, 3267, 1): " 따위는 단숨에 함락시켜 주마",
        (6, 3269, 1): " 따위는 일도 아니다",
        (6, 3292, 0): " 따위는\n가볍게 해치워 주십시오",
        (6, 3295, 1):
            " 따위는 손쉽게 함락할 터…\n"
            "길보를 기다리고 있겠소이다",
        (6, 4037, 1): " 따위는 단숨에 삼켜 주마",
        (6, 4040, 1): " 따위는 우리의 적수가 아니다!",
        (6, 4134, 2): " 등 ",
        (6, 4139, 2): " 등 ",
        (6, 4147, 2): " 등 ",
        (6, 4187, 1): " 등 여러 방면으로\n공세",
        (6, 4532, 1): " 쪽이 열세다",
        (6, 4533, 1): " 쪽이 우세다",
        (6, 4839, 0):
            " 측이 정전을 요청했습니다.\n"
            "수락하시겠습니까?",
        (7, 570, 1): " 측과 결별한다! 철수다!",
        (7, 586, 2): " 측과 싸울 수 없소\n이만 물러나겠소",
        (7, 592, 2):
            " 측과도 친한 사이니\n"
            "이 이야기는 없던 일로 해 주시게",
        (7, 952, 0): " 따위에게 굴복하다니……\n",
        (7, 960, 1):
            " 따위는 피라미잖아!\n"
            "엮여 봤자 시간 낭비라고!",
        (7, 962, 0): " 따위에게 패하다니……\n",
        (7, 1380, 0):
            " 따위의 허약한 성에\n"
            "우리의 온 힘을 쏟아부으면 어찌 될지\n"
            "볼 만하겠구나",
        (7, 1693, 0): " 따위는 겁쟁이에 불과하오\n",
        (7, 1703, 0):
            " 따위는 하잘것없으니\n"
            "지침을 철회해 주시옵소서\n",
        (7, 1710, 0): " 따위는\n별것도 아니야\n",
        (7, 1718, 0): " 따위\n두려워할 것 없소!\n",
        (7, 1724, 0): " 따위\n두려워할 것 없소이다\n",
        (7, 2842, 2): " 등 ",
        (7, 2859, 1):
            " 등은\n패전에도 굴하지 않고 농성 태세를 갖추었습니다\n"
            "기세를 탄 본가에 따를 기미는 없습니다",
        (7, 2861, 1): " 등은\n기세를 탄 ",
        (7, 2865, 0): " 측과 친선 중지",
        (9, 866, 0): " 따위는\n적수가 아니었군",
        (9, 869, 0): " 쪽이\n한 수 위였군요!",
        (9, 1579, 0): " 따위에게\n도움을 받다니……",
        (9, 1876, 0): " 놈\n용서치 않겠다!",
        (9, 2332, 1): " 놈…!",
        (9, 2593, 0): "적 측이 ",
        (9, 2771, 0): " 따위에게\n질 수는 없다!",
        (9, 3571, 0): "적 측에 ",
        (9, 3573, 0): "적 측은 ",
        (9, 3575, 0): "적 측에 ",
        (9, 3576, 0): "적 측은 ",
        (9, 3578, 0): "적 측은 ",
        (9, 3579, 0): "적 측에 ",
        (9, 3580, 0): "적 측은 ",
        (9, 3581, 0): "적 측에 ",
        (9, 3582, 0): "적 측에 ",
        (9, 4132, 0): "성 측은 ",
        (14, 245, 3):
            "\n\u3000·양측은 상대 세력과 인접한 성 가운데 전초전을 치를 성을 선택\n"
            " ·양측 세력을 잇는 길의 수에 따라 출진 가능한 부대 수 결정\n"
            " ·양측이 선택한 성은 방위 거점이 된다\n"
            " ·공성 측 참전 부대는 시작 직전에 선택하고, 수성 측은 성 소속 무장이 방어\n"
            " ·공성전은 일반 공성전과 같은 규칙\n"
            " ·공성 측이 승리하면 잔여 병력이 많은 상위 4개 부대가 결전에 참가\n"
            " ·수성 측이 승리하면 상대 부대의 결전 참가를 저지\n\n",
        (14, 245, 7):
            "\n\u3000·미리 선택한 양측 12개 부대로 합전을 치른다\n"
            " ·합전은 일반 합전과 같은 규칙\n"
            " ·전초전 공성 측에서 승리했다면 잔여 병력 상위 4개 부대가 추가로 참가\n"
            " ·전초전 수성 측에서 패배했다면 적 세력의 부대가 최대 4개 늘어난다",
        (15, 814, 1): " 등의 ",
        (15, 834, 2): " 등 ",
        (15, 1047, 0): " 등 ",
        (15, 1464, 0): " 등 ",
        (15, 1670, 1): "\n가문 중에 「",
        (15, 1835, 3): " 등은\n든든한 원군으로 기대하",
        (15, 1859, 2): " 등\n여러 세력과 교전하고 있",
        (15, 2263, 1): " 등을 새 목표로\n지시할 것 ",
        (15, 2264, 1):
            " 등을 공격해 보는 건 어떻겠소?\n"
            "승산이 크다고 판단",
        (15, 2477, 1): " 등 ",
        (15, 2481, 0): " 등 ",
        (15, 2483, 1): " 등 ",
        (15, 2485, 0): " 등은 방치",
        (15, 2486, 0): " 등 ",
        (15, 2487, 1): " 등 ",
        (15, 2490, 0): " 등 ",
        (15, 2492, 1): " 등 ",
        (15, 2517, 0): " 등 ",
        (15, 2525, 2): " 등 ",
        (15, 2533, 1): " 등 ",
        (15, 2552, 1): " 등 ",
        (17, 228, 1): " 측의 주력은 ",
        (17, 233, 1): " 측의 기세가 이 정도일 줄이야……!",
        (17, 344, 3):
            " 따위에게 붙다니\n"
            "도요토미의 은혜를 잊었나!",
        (17, 348, 1):
            " 녀석…… 도요토미의 세상은 앞으로도 이어진다!\n"
            "도쿠가와의 세상 따위 평생 오지 못하게 하겠다!",
        (17, 362, 0): " 놈이 ",
        (17, 362, 2):
            " 측과도 내통하고 있다는 것은\n"
            "의심할 여지가 없다",
        (17, 368, 2): " 측이 움직인다, 그대는 앞을 보아라",
        (17, 398, 2): " 중신은 모두\n",
        (17, 414, 1):
            " 측이 우세하다고? 뜻밖이군…\n"
            "적은 역적 ",
        (17, 440, 2): " 님의 지휘는 실로 훌륭했다",
        (17, 580, 1): " 님께 적을 접근시키지 마라\n",
        (17, 580, 3): " 측이 물러날 때까지 성을 지켜 내자!",
        (17, 645, 2): " 측을 짓밟아라!",
        (17, 710, 2):
            " 측이 무너지기 시작한 듯합니다\n"
            "저희는 어찌할까요?",
    }
)

# Reviewed adverb and structural-predicate pass.  Parent records frequently
# jump to these shared owners, so one exact owner repair closes every alias.
CALL_ASSEMBLY_EXACT_REWRITES.update(
    {
        (2, 242, 0): "아무래도 ",
        (2, 248, 2): " 스스로 ",
        (6, 562, 0): "언제 ",
        (6, 574, 0): "아… 아직인가…?\n설마 ",
        (6, 844, 0): "설마 ",
        (6, 1545, 0): "과연 ",
        (6, 2291, 0): "우선 ",
        (6, 3458, 1): " 스스로 바친 계책 따위는\n이미 ",
        (6, 3583, 0): "굳건히 ",
        (6, 3589, 0): "설마 ",
        (6, 4062, 1): "을 본거지로 정했",
        (6, 4427, 1): "。필요하다면\n「지행」에서 다시 ",
        (6, 4461, 1): ", 부디 ",
        (6, 4488, 0): "이 일은 부디 ",
        (6, 4614, 1):
            "과의 이야기를 위해\n여기까지 와 주신 겁니까!\n참으로 ",
        (6, 4747, 0): "의 진심을 확실히 ",
        (6, 4765, 1): "\n언제든 다시 ",
        (6, 4813, 0): "\n만약 ",
        (7, 270, 0):
            "이제 주군을 잃은 몸이니\n"
            "지난날의 적이라 해도 원한은 없소\n삼가 ",
        (7, 887, 1):
            "…\n그 이름 높은 모략에 현혹되지 않도록\n"
            "경계를 엄중히 ",
        (8, 260, 1): "!\n이 또한 ",
        (8, 286, 0): "올해는 흉작이 들었",
        (8, 409, 1): "\n언제든 다시 ",
        (8, 590, 0): "역시 ",
        (8, 770, 0):
            "이대로는 태풍에\n휩쓸려 날아가고 말 것이오…",
        (8, 1240, 1): "\n또한 ",
        **{
            (8, record_id, 1): "」 시설을 건설하라는 포고를 내리자"
            for record_id in range(951, 963)
        },
        (9, 843, 0): "마침내 ",
        (9, 2670, 0):
            "대단하십니다!\n나도 저리 되고 싶군요!",
        (15, 270, 0): "잠시 ",
        (15, 566, 1):
            "회유를 더욱, 이라\n"
            "지금 참전하겠다는 자는 어림잡아 절반\n"
            "남은 절반도 거두어들이라는 명이시군요",
        (15, 810, 0):
            "일대에서 잇키를 부추기겠습니다\n"
            "문도의 궐기에 맞추어 진군하여\n"
            "학정에 신음하는 이들을 구하",
        (15, 1559, 1):
            "명\n그들을 우리 가문에 받아들일지\n부디 ",
        (15, 1559, 3): "판단해 ",
        (15, 1570, 0): "이제 ",
        (15, 1570, 1):
            "이야말로 천하인\n전국 통일의 비원을, ",
        (15, 1832, 1): "\n성과를 거둘 날이 곧 오리라",
        (15, 1943, 0): "성을 늘리자",
        (15, 1948, 0): "가신을 늘리자",
        (15, 1952, 0): "성하 시설을 늘리자",
        (15, 1955, 0): "석고를 늘리자",
        (15, 1960, 0): "상업을 늘리자",
        (15, 1985, 2): "그러니\n잠시 ",
        (17, 60, 0): "저곳이 바로 ",
        (17, 266, 0): "예\n하지만 ",
        (17, 457, 0):
            "모두, 승전 함성을 올려라!\n이제 ",
        (17, 685, 1): "놈은 어디로 갔지?\n설마 ",
        (17, 710, 0): "주군, 아무래도 ",
        (17, 899, 1): "의 깃발이 보이지 않는다\n역시 ",
        (17, 1127, 0): "게다가 지금 ",
    }
)

# Predicate reconstruction pass.  Each replacement is the fixed side of a
# proved verbatim call boundary; terminal-family retargets below supply only
# the register ending that the reconstructed stem expects.
CALL_ASSEMBLY_EXACT_REWRITES.update(
    {
        (6, 2243, 0):
            " 같은 자와 자리를 함께하다니\n"
            "고통스럽기만 하군… 빨리 끝내지",
        (6, 3406, 0): "더없는 영예가 있",
        (6, 4248, 0): " 정책을 할 돈이 없어\n실행하지 ",
        (6, 4689, 0): "그것은 절대 양보하지 ",
        (6, 4743, 2): ".\n우리도 지킬 뜻이 있",
        (6, 4804, 2): "\n그 자와 동행하지 ",
        (6, 4876, 2): "이라는 별호에 걸맞은 모습이 있",
        (6, 4891, 2): "의 휘하가 아니면\n저도 분발하지 ",
        (6, 4897, 2): "\n다음 인물들이 ",
        (6, 4938, 0): "이 상황에서는 사치를 요구하지 ",
        (7, 221, 0): "적장을 포박했",
        (7, 222, 0): "군이\n적장을 포박했",
        (7, 2482, 0): "라면\n필요한 병력을 스스로 판단하지 ",
        (7, 2484, 0): "출진지를 선택해 ",
        (7, 2490, 2): "에게 힘이 남으면 ",
        (7, 2490, 3): "지원해 ",
        **{
            (7, record_id, 1): "에\n볼일 없다… 성으로 돌아간다"
            for record_id in range(2820, 2825)
        },
        (8, 283, 0): ", 안타깝게도\n올해는 흉작이 들었",
        (9, 835, 0): "\n꼴 좋다!",
        (9, 843, 1): " 쪽으로\n베었습니다!",
        (9, 846, 0): " 쪽으로\n칠 때가 오다니",
        (9, 1802, 0): " 쪽으로\n추격합시다!",
        (9, 1959, 1): " 같은 장수마저",
        (9, 2766, 0): " 쪽으로\n추격하라, 질 수는 없다!",
        (9, 3951, 0): "아군은 상당히 열세에 있",
        (15, 255, 4): "고려해 ",
        (15, 361, 1):
            "다\n앞으로 신세를 지겠다\n싸움은 내게 맡겨라!",
        (15, 758, 2): "에 다가오는 적과\n교전하지 ",
        (15, 1440, 1):
            "다\n앞으로 신세를 지겠다\n싸움은 내게 맡겨라!",
        (15, 1546, 4): "출진해 ",
        (15, 1572, 2): "확인해 ",
        (15, 1574, 2): "확인해 ",
        (15, 1576, 1): "확인해 ",
        (15, 1673, 0):
            "우리 가문의 조두들은 모두 걸물이지만\n"
            "공을 세울 기회를 얻지 못한 듯하니\n「",
        (15, 2184, 0): "에서 사건이 났다 하오…\n풍문이 있",
        (15, 2377, 1): ".\n어쩔 수 ",
        (15, 2462, 1): "\n방위 임무를 해제하지 ",
        (15, 1928, 0): "조금만 더 ",
    }
)

# Call-assembly closure: shared Base donors for selector-role mistakes and
# exact stem repairs for the remaining high-confidence Cartesian collisions.
CALL_ASSEMBLY_EXACT_REWRITES.update(
    {
        (2, 253, 0): "도로 정비에는 자신 있",
        (6, 3062, 2): "개월만 남게 됐",
        (6, 825, 0):
            " 탓에 생긴 실책의\n뒤처리는 사양입니다",
        **{
            (6, record_id, 0): "하고 함께\n"
            for record_id in range(4184, 4196)
        },
        (6, 4184, 1): "으로 진군 중",
        (6, 4185, 1): " 쪽으로 진군 중",
        (6, 4186, 1): " 쪽으로 진군 중",
        (6, 4187, 1): "을 비롯한 여러 방면으로\n진군 중",
        (6, 4188, 1): " 등을 비롯한 여러 방면으로\n진군 중 ",
        (6, 4189, 1): " 등을 비롯한 여러 방면으로\n진군 중 ",
        **{
            (6, record_id, 1): "의 "
            for record_id in range(4190, 4196)
        },
        (6, 4190, 2): "으로\n진군 중",
        (6, 4191, 2): " 쪽으로\n진군 중",
        (6, 4192, 2): " 쪽으로\n진군 중",
        (6, 4193, 2): "을 비롯해\n여러 방면으로 진군 중",
        (6, 4194, 2): " 등을 비롯해\n여러 방면으로 진군 중",
        (6, 4195, 2): " 등을 비롯해\n여러 방면으로 진군 중",
        (6, 4020, 0): " 공략에는 충분한 병력이 있",
        (6, 4801, 0): "\n정사에는 자신 있",
        (6, 2737, 1):
            "의 비호에 기댈 수밖에 없지만\n언젠가 제 힘으로 서야 하오",
        (7, 2032, 0): "이 위험하다……\n어서—",
        (7, 2032, 1): " 부대를 쳐라!",
        (7, 2600, 0): "이번 일번창은 바로 나",
        (7, 2600, 1):
            "로다\n자, 비사문천의 깃발을 내걸고\n천하에 의를 보이리라",
        (8, 261, 1):
            "\n탐스러운 벼 이삭을 앞에 두고\n백성들도 기뻐하고 있",
        (8, 264, 2): "\n백성들도 기뻐하고 있",
        (8, 273, 1):
            "\n무슨 일이든 이처럼 대비해야 할 필요가 있",
        (8, 353, 0): "의 영내에서도\n태풍 피해가 발생하고 있",
        (8, 354, 0): "영내에 태풍 피해를 입은 곳이 있",
        (13, 25, 1): "이 자리 잡고 있",
        (13, 53, 0): "이 우리 가문의 지배 아래에 있",
        (13, 112, 1): "\n통솔력만큼은 자신 있",
        (15, 1206, 0):
            "은 단것을 고마워하는 모양\n"
            "코…… 콘페…… 콘페이토는\n"
            "피로에 효험이 있으니 말이오",
        **{
            (15, record_id, 2): "의\n손에 넘어갔"
            for record_id in (1248, 1249, 1251, 1252, 1254, 1255, 1257, 1258)
        },
        (15, 1283, 2): "의 방비가 흔들리고 있",
        (15, 1051, 0): " 등을 비롯한 가보 총 ",
        (15, 1359, 2): " 등을 비롯한\n",
        (15, 1484, 0): " 등을 비롯한 ",
        (15, 1485, 2): " 등을 비롯한 ",
        (15, 1659, 0): "본거지의 군을 ",
        (15, 1835, 0): "우리 가문은 여러 세력을 종속시키고 있",
        (15, 1858, 2): "과\n실로 칼날을 맞대고 있",
        (15, 1946, 0): "가신을 늘리자",
        (15, 1967, 0): "임무는 순조롭게 진행되고 있",
        (15, 2319, 0):
            "설마 소망이 이루어질 줄이야……\n"
            "전선에서 이 무용을 떨치며\n더욱 충근에 매진",
        (15, 2322, 0):
            "설마 소망이 이루어질 줄이야……\n"
            "후방에서 정무 수완을 발휘하며\n더욱 충근에 매진",
        (15, 2407, 1):
            "만,\n다행히 양측의 전력은 팽팽히 맞서고 있",
        (15, 1572, 1): "의 상황을 ",
        (15, 1572, 4):
            " 지역을 제압하려면\n그 땅을 알아야 합니다",
        (15, 2554, 2):
            "!\n이만큼 비축했으니,\n"
            "원정군도 군량 걱정이 없을 것입니다",
        (17, 858, 1):
            " 측이 무너지기 시작한 듯합니다\n저희는 어찌할까요?",
        (17, 869, 1):
            " 측을 공격하며\n우리 편을 들고 있다고 합니다!",
        (6, 4671, 1): "\n많은 것을 바라지는 못한다",
        (7, 2490, 0): "우리 군단령에 적세가 쇄도했습니다",
        (9, 3967, 0):
            "출진한 지 오래되어 병사들이 피로해 보입니다",
        (15, 2294, 1): " 아래에 군다이가 다스리는\n땅",
        (15, 2441, 0):
            "요즘 여러 무장이 타성에 젖어\n움직임이 둔해진 듯합니다",
        (6, 1635, 0): " 및 ",
        (6, 1639, 0): " 및 ",
        (6, 1639, 1):
            ", 두 사람의\n혼인은 양가의 유대를 굳건히 하여\n"
            "길이길이 이어지겠구려",
        (6, 2973, 0): "이 ",
        (6, 2973, 1):
            ", 청이 있소이다\n무사의 정… 부디 들어주시오",
        (6, 3034, 0): "그 ",
        (6, 3454, 0): "훈공 1위의 영예는 ",
        (6, 3454, 1):
            "에게 돌아왔소이다!\n한 방면을 맡은 장수에 걸맞은 활약을\n"
            "해냈다는 뜻이겠지요",
        (6, 3478, 0): "쯤 되었으니\n과연 ",
        (6, 3536, 0): "쯤 되었으니\n과연 ",
        (6, 3544, 0): "무슨 일이든 ",
        (6, 3694, 0): " 같은 사람을 ",
        (6, 1493, 1): " ",
        (6, 1493, 2): "개월 동맹",
        (6, 3409, 0): "안심하십시오, ",
        (7, 2599, 0): "일번창은 바로 이 ",
        (9, 554, 0): "상대는 ",
        (9, 635, 0): "이 ",
        (9, 693, 0): "이 ",
        (9, 811, 0): "이 ",
        (9, 1120, 0): "요충지, 이 ",
        (9, 1130, 0): "요충지, 이 ",
        (9, 1132, 0): "설비는 이 ",
        (9, 1142, 0): "설비, 이 ",
        (9, 1475, 0): "이, 이 ",
        (9, 1869, 0): "이 ",
        (9, 1986, 0): "!?\n저 ",
        (9, 2096, 0): "이 ",
        (9, 2101, 0): "내가 바로 ",
        (9, 2104, 0): "바로 이 몸이",
        (9, 2104, 1): "\n적을 격파했다!",
        (9, 2106, 0): "이 ",
        (9, 2162, 0): "이 ",
        (9, 2174, 0): "이 ",
        (9, 2186, 0): "이 ",
        (9, 2186, 1): "에게\n작게나마 타격을…",
        (9, 2235, 0): "이 ",
        (9, 2641, 0):
            "본성에 수상한 자가!\n내가 장사 지내리라!",
        (9, 2641, 1): "",
        (15, 320, 1): "의 ",
        (15, 320, 2): " 곁을 지키려 하니\n",
        (15, 320, 3): "한번 인견해 보시는",
        (15, 320, 4): " 것이 어떠실지요",
        (15, 321, 1): "의 ",
        (15, 321, 2): " 곁을 지키려 하니\n",
        (15, 321, 3): "한번 인견해 보시는",
        (15, 321, 4): " 것이 어떠실지요",
        (15, 362, 0): ", ",
        (15, 362, 1): "라 하옵니다\n조금이라도 ",
        (15, 418, 0): "의 무장을 빼 와 보이겠다\n이 ",
        (15, 438, 1):
            "\n어리석은 옛 주군을 버리고 왔사옵니다\n부디 ",
        (15, 1441, 0): ", ",
        (15, 1441, 1): "라 하옵니다\n조금이라도 ",
        (15, 703, 0): " 측은 편입에 응했",
        (15, 703, 1):
            "\n이후 그 병력은 군의 병력으로 계상됩니다\n",
        (15, 703, 2): "님의 합류를 기대",
        (15, 704, 0): " 측은 편입에 응했",
        (15, 704, 1):
            "\n이후 그 병력은 군 병력에\n산입됩니다",
    }
)

CALL_ASSEMBLY_PREFIX_TRIMS = {
    **{
        coordinate: "지"
        for coordinate in (
            (6, 2175, 2), (6, 3532, 2), (6, 3856, 1),
            (6, 4486, 1),
            (8, 297, 1), (8, 349, 1), (8, 1239, 2),
            (9, 3986, 1), (15, 228, 1), (15, 257, 1),
            (15, 275, 2), (15, 276, 2), (15, 282, 1),
            (15, 283, 2), (15, 284, 1), (15, 762, 2),
            (15, 1384, 2),
        )
    },
    **{
        coordinate: "다"
        for coordinate in (
            (6, 3512, 2),
            (15, 1239, 2), (15, 1240, 2), (15, 1242, 2),
            (15, 1243, 2), (15, 1245, 2), (15, 1246, 2),
            (15, 1248, 3), (15, 1249, 3), (15, 1251, 3),
            (15, 1252, 3), (15, 1254, 3), (15, 1255, 3),
            (15, 1257, 3), (15, 1258, 3),
        )
    },
}

CALL_ASSEMBLY_SUFFIX_APPENDS = {
    coordinate: " "
    for coordinate in {
        (7, 2885, 1),
        (15, 1568, 2),
        (15, 1677, 1),
        (15, 1682, 0),
        (15, 1683, 0),
        (15, 1694, 1),
        (15, 1824, 0),
        (15, 1825, 0),
        (15, 1826, 0),
        (15, 1827, 0),
        (15, 1900, 1),
        (15, 1901, 1),
        (15, 1903, 2),
        (15, 2207, 0),
        (15, 2297, 1),
        (15, 2308, 2),
        (15, 2309, 2),
        (15, 2310, 2),
        (15, 2311, 2),
        (15, 2312, 2),
        (15, 2313, 2),
        (15, 2339, 0),
        (15, 2340, 0),
        (15, 2341, 0),
        (15, 2342, 0),
        (15, 2343, 0),
        (15, 2344, 0),
        (15, 2345, 0),
        (15, 2346, 0),
        (15, 2347, 0),
        (15, 2348, 0),
        (15, 2349, 0),
        (15, 2350, 0),
        (15, 2351, 0),
        (15, 2352, 0),
        (15, 2353, 0),
        (15, 2354, 0),
        (15, 2355, 0),
        (15, 2356, 0),
        (15, 2357, 0),
        (15, 2358, 0),
        (15, 2442, 0),
        (15, 2451, 2),
        (15, 2467, 0),
    }
}
CALL_ASSEMBLY_SUFFIX_APPENDS.update(
    {
        coordinate: " "
        for coordinate in {
            (2, 131, 1), (2, 220, 0), (2, 581, 0),
            (6, 443, 0), (6, 3380, 0), (6, 3420, 0),
            (6, 3410, 3), (6, 3420, 1),
            (6, 3452, 0), (6, 3533, 0),
            (6, 3850, 0), (6, 4470, 0), (6, 4472, 0),
            (6, 4483, 1),
            (7, 267, 0), (7, 274, 0),
            (7, 2606, 0), (7, 2611, 0),
            (7, 2688, 0),
            (9, 794, 0), (9, 2029, 0), (9, 2091, 0),
            (9, 2093, 0), (9, 2519, 0), (9, 2523, 0),
            (9, 2527, 0),
            (15, 905, 0), (15, 935, 0),
            (15, 1653, 0), (15, 1661, 1),
            (15, 1577, 0), (15, 2222, 0), (15, 2429, 2),
            *{
                (15, record_id, 3)
                for record_id in range(1385, 1409)
            },
        }
    }
)
CALL_ASSEMBLY_SUFFIX_APPENDS.update(
    {
        coordinate: " "
        for coordinate in {
            (6, 3559, 0), (6, 3574, 0), (6, 3580, 0),
            (8, 396, 1), (8, 995, 0), (8, 998, 0),
            (8, 1001, 0), (8, 1007, 0), (8, 1010, 0),
            (13, 112, 2), (13, 123, 2),
            (15, 1198, 1), (15, 2331, 1), (15, 2334, 1),
        }
    }
)

# Insert one boundary space before an immediately adjacent dynamic modifier
# or castle-action literal.  The coordinate universe comes from every
# rendered v5 finding and contains only the actual literal owners.
CALL_ASSEMBLY_PREFIX_PREPENDS = {
    coordinate: " "
    for coordinate in {
        (6, 3439, 0), (6, 4496, 1), (6, 4500, 1), (6, 4602, 1),
        *{(6, record_id, 0) for record_id in (584, 586, 592, 600)},
        *{(6, record_id, 0) for record_id in range(3996, 4020)},
        *{(6, record_id, 0) for record_id in range(4022, 4031)},
        (6, 4173, 1), (6, 4196, 1), (6, 4247, 0),
        (7, 764, 1), (7, 774, 1), (7, 1793, 1),
        (7, 1971, 1), (7, 2027, 0), (7, 2499, 1),
        (7, 2505, 2), (7, 2507, 3),
        (8, 1007, 2),
        (15, 384, 1), (15, 887, 1), (15, 911, 1),
        (15, 1352, 2), (15, 1448, 1),
        (15, 1584, 1), (15, 1585, 2), (15, 1586, 2),
        (15, 1613, 1),
        (15, 2031, 0), (15, 2033, 1), (15, 2034, 0),
        (15, 2035, 1), (15, 2036, 0), (15, 2037, 0),
        (15, 2038, 1), (15, 2039, 0), (15, 2041, 0),
        (15, 2042, 1), (15, 2043, 0), (15, 2044, 0),
        (15, 2045, 0), (15, 2046, 0), (15, 2047, 1),
        (15, 2048, 0), (15, 2049, 1), (15, 2050, 1),
        (15, 2051, 0), (15, 2052, 0), (15, 2073, 1),
        (15, 2113, 0), (15, 2115, 0), (15, 2117, 1),
        (15, 2118, 0), (15, 2119, 1), (15, 2120, 0),
        (15, 2121, 0), (15, 2122, 1), (15, 2123, 0),
        (15, 2125, 0), (15, 2126, 1), (15, 2127, 0),
        (15, 2128, 0), (15, 2129, 0), (15, 2130, 0),
        (15, 2131, 1), (15, 2132, 0), (15, 2133, 1),
        (15, 2134, 1), (15, 2135, 0), (15, 2136, 0),
        (15, 2157, 1), (15, 2169, 0), (15, 2261, 0),
    }
}

# High-confidence comma spacing from the full Cartesian runtime render.  The
# dynamic set contains a literal ending in a comma whose next emitting VM
# component starts with Hangul.  The internal set contains comma+Hangul inside
# one literal.  Parent jump records disappear automatically when these owner
# literals are corrected.
INTERNAL_COMMA_SPACING_COORDINATES = {
    (7, 867, 0),
}
DYNAMIC_COMMA_SPACING_COORDINATES = {
    (1, 10, 0), (1, 11, 2),
    (2, 123, 0), (2, 125, 0), (2, 129, 0), (2, 135, 0), (2, 261, 0),
    (6, 819, 0),
    *{(6, record_id, 0) for record_id in range(1430, 1442)},
    (6, 1582, 0), (6, 2213, 0), (6, 2289, 0), (6, 2392, 0),
    (6, 2449, 0), (6, 3363, 0), (6, 3399, 0), (6, 3401, 0),
    (6, 3405, 0), (6, 3411, 0), (6, 3440, 0), (6, 3446, 0),
    (6, 3472, 2), (6, 3531, 0), (6, 3532, 0), (6, 3641, 1),
    (6, 4211, 1), (6, 4577, 2), (6, 4579, 2), (6, 4587, 0),
    (6, 4608, 0), (6, 4609, 0), (6, 4611, 0), (6, 4662, 0),
    (6, 4717, 0), (6, 4726, 1), (6, 4755, 0), (6, 4812, 0),
    (6, 4924, 2), (6, 4925, 1),
    (7, 2597, 0), (7, 2601, 0), (7, 2603, 0), (7, 2607, 0),
    (7, 2614, 0), (7, 2651, 0), (7, 2676, 0), (7, 2693, 0),
    (7, 2709, 0), (7, 2740, 0), (7, 2831, 0),
    (8, 328, 0), (8, 662, 0),
    (9, 526, 0), (9, 1476, 0), (9, 1566, 0), (9, 1582, 0),
    (9, 1681, 0), (9, 2618, 0), (9, 3506, 0),
    (13, 75, 0),
    (15, 269, 2), (15, 990, 0), (15, 1515, 2), (15, 1520, 0),
    (15, 1646, 0), (15, 1652, 0), (15, 1654, 0), (15, 1678, 0),
    (15, 1794, 0),
    *{(15, record_id, 0) for record_id in range(1800, 1805)},
    (15, 2285, 1), (15, 2291, 1), (15, 2494, 1),
    (17, 5, 3), (17, 133, 0), (17, 154, 1), (17, 169, 0),
    (17, 255, 0), (17, 276, 0), (17, 277, 1), (17, 357, 3),
    (17, 366, 0), (17, 388, 0), (17, 394, 0), (17, 398, 0),
    (17, 424, 0), (17, 446, 1), (17, 459, 0), (17, 682, 0),
    (17, 853, 0),
}

# Five callers already contain the Korean question stem ``어떻`` before the
# runtime family that emits ``어떠오/어떤가/어떠하오``.  Remove only that
# duplicated stem; the following runtime call remains authoritative.
CALL_ASSEMBLY_SUFFIX_TRIMS.update(
    {
        (6, 4245, 0): "어떻",
        (6, 4246, 0): "어떻",
        (6, 4421, 1): "어떻",
        (8, 1198, 1): "어떻",
        (8, 1202, 0): "어떻",
    }
)

# Each value is the literal prefix immediately before the call.  The VM call
# contributes the final register-dependent ending.
TERMINAL_COORDINATE_REWRITES = {
    **{
        (6, record_id, 0): "분에 넘치는 대임, 삼가 수락"
        for record_id in (1442, 1443, 1447, 1448, 1449, 1451, 1452, 1453)
    },
    (6, 4804, 1): "에게는 원한이 있",
    (8, 1097, 2): "!\n일하는 모습도 놀라울 정도",
    (8, 1112, 0): "곳곳에서 풍작의 조짐이 나타났",
    (8, 1118, 2): "가호로\n병사들의 사기가 높아지고 있",
    (9, 3582, 1): "을 사용하려는 움직임이 있습니다\n경계가 필요할 것",
    **{
        (9, record_id, 0): "적군은 성하에서 방어 태세를 갖춘 상태"
        for record_id in (3956, 3957, 3958, 3962, 3970)
    },
    (9, 3967, 0): "출진한 지 오래되어 병사들의 피로를 보고",
    **{
        (9, record_id, 0): "우리의 방비가 충분히 갖춰진 상태"
        for record_id in (3972, 3973, 3975, 3976, 3978, 3979, 3981, 3982)
    },
    (9, 4127, 0): "이번 공성전에 쓸 계책이 마련된 상태",
    (9, 4140, 1): "」도 포박에 응하기로 ",
    (15, 832, 3): "성에서\n봉기가 일어났",
    (15, 1141, 0): "은 공격로가 한정되어\n함락시키기 어렵다는 판단",
    (15, 1547, 0): "그럼 잠시 더 적병을 유인하기로 ",
    (15, 2445, 2): "이 간파해 냈",
    (15, 2457, 0): "공적이 탁월한 자가 있",
    (15, 2467, 1):
        "\n가문의 방침을 정하고 결속을 다지려면\n평정중이 긴요한 상황",
    (15, 2496, 1): "이\n우리에게 항복하기로 결정했",
    (15, 2553, 1): "에\n쌀을 운반해 두었",
    (15, 2593, 2): "의 운명도 끝",
}

# Findings from the independent all-call-site terminal detector.  These
# include completed endings that the narrower surface regex intentionally did
# not classify.
EXPANDED_TERMINAL_COORDINATE_REWRITES = {
    (2, 510, 1): " 곁을 지키며,\n완벽한 성과로 이끌",
    (2, 629, 1): "도 나온",
    (6, 3541, 1): "의 천명",
    (6, 4677, 0): "…그 성의가 어느 정도인지\n이 눈으로 직접 보고 판단",
    (6, 4767, 0): "그럼 이로써 휴전을 맺기로 ",
    (7, 2474, 1): "을 지키기는\n상당한 난제",
    (7, 2475, 1): "을 지키기는\n상당한 난제",
    (7, 2834, 1): "\n싸움은 끝이다. 귀성을 명",
    (8, 273, 0): "올해는 흉작이었으나, 미리 손을 써 둔\n지역은 무사히 넘겼",
    (8, 304, 1): "의 영내에\n가뭄이 발생하여,\n토지 황폐와 민심 불안을 확인했",
    (8, 1099, 3): "\n그 힘을 전장에서 크게 발휘할 것",
    (8, 1101, 2): "인지\n가신들이 영지를 다스리는 솜씨도\n더욱 놀라워지기 시작",
    (8, 1103, 2): "가호 덕인지\n가신들의 무예도\n더욱 빛을 발하기 시작",
    (8, 1107, 0): "구마노에 계신 대신을 두려워한 것인지\n짐승이 논밭을 망치는 일도 감소",
    (8, 1112, 2): "가호 덕분",
    (8, 1118, 3): "\n반드시 전장에서 승기를 가져다줄 것",
    (9, 3988, 0): "본성을 파괴하는 것이\n승리로 가는 지름길이",
    (9, 4132, 1):
        "등으로 방비를 굳히는 듯합니다…\n준비가 끝나기 전에 파괴하면\n"
        "계획이 어긋난 성안에서는 항복을 생각할 것",
    (9, 4133, 1): "도\n항복을 청하러 오긴 ",
    (9, 4138, 1): "마저 물러난 지금\n더 버텨도 소용없는 일",
    (9, 4142, 2): "의 항복을 받아들이",
    (9, 4143, 2): "\n그대 부하들의 안전도 보장",
    (9, 4144, 0): "물론, 기꺼이 환영",
    (15, 233, 0): "그리 많은 성과는\n기대 난망",
    (15, 237, 0): "그리 많은 성과는\n기대 난망",
    (15, 241, 0): "그리 많은 성과는\n기대 난망",
    (15, 245, 0): "그리 많은 성과는\n기대 난망",
    (15, 515, 1): " 측이 우리 편에 선다면\n전시에 든든한 힘",
    (15, 1558, 0): "적의 장단에 맞춰 줄 필요가 ",
    (15, 1700, 1): "도\n반드시 쳐부술 수 있",
    (15, 2453, 1): "성하에 집결",
    (15, 2458, 0): "본가도 오랫동안 전투를 지속",
    (15, 2470, 2): "곳의 시장을\n장악하고 귀환",
    (15, 2474, 2): "곳의 농촌을\n장악하고 귀환",
    (15, 2486, 1): "개 성에서\n군량미를 조달",
    (15, 2506, 2): "의 시노비가 저지",
    (15, 2522, 1): "의 권위에 겁먹고\n뿔뿔이 도주",
    (15, 2554, 2): "!\n이만큼 비축했으니,\n원정군도 군량 걱정이 없을 것",
    (15, 2559, 3): "도 우리를 지키는 한,\n우리 가문이 쇠할 일은 ",
    (15, 2595, 1): ".\n우리의 숙원도 여기까지",
}

# The first entry is the user-reported line.  The remaining entries replace
# mixed family 376 with coherent copular family 520 after nominalization.
CONTROL_RETARGETS = {
    (15, 1545): (376, 1247),
    (6, 3541): (376, 520),
    (6, 3768): (748, 1247),
    (6, 4917): (748, 1247),
    (9, 4138): (556, 610),
    **{
        (9, record_id): (376, 520)
        for record_id in (3972, 3973, 3975, 3976, 3978, 3979, 3981, 3982, 4127)
    },
}

CONTROL_RETARGET_REASONS = {
    (15, 1545):
        "reviewed_complete_sentence_uses_proved_empty_terminal",
    (6, 3541):
        "nominal_cheommyeong_prefix_requires_coherent_copular_family",
    (6, 3768):
        "screenshot_request_question_replaces_reversed_negative_terminal",
    (6, 4917):
        "screenshot_request_question_replaces_reversed_negative_terminal",
    (9, 4138):
        "nominal_il_prefix_requires_prediction_family_without_nonfinite_da",
    (9, 4127):
        "nominal_state_prefix_requires_coherent_copular_family",
    **{
        (9, record_id):
            "nominal_state_prefix_requires_coherent_copular_family"
        for record_id in (3972, 3973, 3975, 3976, 3978, 3979, 3981, 3982)
    },
}

# Some Cartesian call assemblies contain more than one independently
# incompatible terminal in a single record.  Keep these operations separate
# from the legacy one-retarget-per-record table so every operand mutation is
# explicit and independently evidenced.
ADDITIONAL_CONTROL_RETARGETS = {
    (1, 11): ((94, 1247),),
    (1, 25): ((880, 1247),),
    (2, 133): ((628, 550),),
    (2, 248): ((376, 178),),
    (6, 3507): ((1096, 142),),
    (6, 3528): ((574, 1247),),
    (6, 3763): ((568, 520),),
    (6, 3764): ((568, 520), (718, 550)),
    (6, 3765): ((34, 1247),),
    (6, 3766): ((1096, 1247),),
    (6, 3769): ((1096, 2633),),
    (6, 3532): ((298, 748),),
    (6, 3849): ((34, 1247),),
    (6, 3942): ((34, 1247),),
    (6, 4179): ((748, 142),),
    (6, 4561): ((1198, 322), (748, 1247)),
    (6, 4564): ((1198, 322), (748, 1247)),
    (6, 4565): ((1198, 1247), (748, 1247)),
    (6, 4566): ((1198, 1247), (748, 1247)),
    (6, 4577): ((1198, 322), (748, 1247)),
    (6, 4579): ((1198, 322), (748, 1247)),
    (6, 4580): ((1198, 1247), (748, 1247)),
    (6, 4588): ((376, 550),),
    (6, 4645): ((1096, 142), (736, 1247)),
    (6, 4651): ((1198, 1247), (748, 1247)),
    (6, 4652): ((1198, 322), (748, 1247)),
    (6, 4690): ((1198, 1247), (748, 1247)),
    (6, 4707): ((610, 1247),),
    (6, 4763): ((1048, 1247),),
    (6, 4816): ((1198, 322), (748, 1247)),
    (6, 2074): ((700, 1247), (610, 2633)),
    (7, 272): ((748, 160),),
    (7, 335): ((1096, 142),),
    (7, 2512): ((376, 1247),),
    (7, 884): ((634, 550), (808, 466)),
    (8, 303): ((376, 178),),
    (8, 296): ((508, 1247),),
    (8, 1031): ((568, 1247), (442, 1247), (1168, 1247)),
    (8, 1237): ((1096, 1247),),
    (6, 4468): ((178, 1247), (1, 1247)),
    (9, 3953): ((88, 70),),
    (15, 379): ((568, 178),),
    (15, 364): ((1150, 538), (394, 1247)),
    (15, 517): ((1096, 142),),
    (15, 228): ((1096, 550),),
    (15, 284): ((568, 550),),
    (15, 762): ((748, 70),),
    (15, 1383): ((748, 1247),),
    (15, 1384): ((1096, 550),),
    (15, 514): ((298, 2633),),
    (15, 819): ((1048, 2633),),
    (15, 1234): ((1048, 2633), (286, 1247)),
    (15, 1537): ((700, 1247), (424, 2634)),
    (15, 1614): ((310, 1247), (376, 1247), (286, 1247)),
    (15, 1701): ((700, 1247), (616, 2634)),
    (15, 1863): ((1096, 142),),
    (15, 2211): ((82, 142), (700, 1247), (610, 1247)),
    (15, 2406): ((1096, 142), (508, 1247)),
    (15, 2408): ((1096, 142), (508, 1247)),
    (15, 2579): ((700, 1247), (466, 2633)),
    (15, 2592): ((574, 1247),),
    (15, 2593): ((538, 550), (568, 550), (1096, 466)),
    (8, 1239): ((1048, 1247), (610, 2634)),
    (15, 1512): ((610, 2634),),
    (15, 1522): ((610, 2634),),
    (15, 2449): ((34, 1247), (8, 1247)),
    (1, 14): ((196, 1247), (136, 1247)),
    (2, 560): ((976, 1247),),
    (6, 549): ((256, 1247),),
    (6, 3062): ((628, 70),),
    (6, 3110): ((550, 1247),),
    (6, 3535): ((550, 1247),),
    (6, 3555): ((598, 1247), (562, 1247)),
    (6, 3625): ((562, 1247),),
    (6, 3631): ((562, 1247),),
    (6, 4203): ((628, 70),),
    (6, 4210): ((508, 1247),),
    (6, 4444): ((550, 1247),),
    (6, 4808): ((988, 1247),),
    (7, 2436): ((1096, 1247), (190, 1247), (508, 1247)),
    (7, 334): ((982, 1247),),
    (9, 3990): ((190, 1247),),
    (15, 268): ((304, 1247),),
    (15, 269): ((628, 70),),
    (15, 1502): ((376, 1247), (556, 1247)),
    (15, 1541): ((772, 1247), (286, 1247)),
    (15, 1615): ((286, 1247),),
    (15, 1674): ((628, 70),),
}

QUESTION_DOUBLE_TERMINAL_RETARGETS = {
    (15, 379): (616, 1247),
    (15, 1235): (616, 1247),
    **{
        coordinate: (610, 1247)
        for coordinate in (
            (6, 4245), (6, 4246), (6, 4421),
            (7, 2885),
            (8, 1198), (8, 1202),
            (15, 1229), (15, 1568),
            (15, 1666), (15, 1669), (15, 1677),
            (15, 1682), (15, 1683), (15, 1687),
            (15, 1689), (15, 1691), (15, 1694),
            (15, 1822), (15, 1823), (15, 1824),
            (15, 1825), (15, 1826), (15, 1827),
            (15, 1900), (15, 1901), (15, 1903),
            (15, 1915), (15, 1916), (15, 1918),
            (15, 2207), (15, 2263), (15, 2297),
            (15, 2308), (15, 2309), (15, 2310),
            (15, 2311), (15, 2312), (15, 2313),
            (15, 2339), (15, 2340), (15, 2341),
            (15, 2342), (15, 2343), (15, 2344),
            (15, 2345), (15, 2346), (15, 2347),
            (15, 2348), (15, 2349), (15, 2350),
            (15, 2351), (15, 2352), (15, 2353),
            (15, 2354), (15, 2355), (15, 2356),
            (15, 2357), (15, 2358), (15, 2442),
            (15, 2451), (15, 2467),
        )
    },
}
for _coordinate, _retarget in QUESTION_DOUBLE_TERMINAL_RETARGETS.items():
    ADDITIONAL_CONTROL_RETARGETS[_coordinate] = (
        ADDITIONAL_CONTROL_RETARGETS.get(_coordinate, ())
        + (_retarget,)
    )

PAST_BOUNDARY_RETARGETS = {
    **{
        (6, record_id): (628, 70)
        for record_id in (
            *range(3696, 3709),
            *range(3721, 3733),
        )
    },
    (8, 1198): (628, 70),
    (15, 1359): (628, 70),
}
for _coordinate, _retarget in PAST_BOUNDARY_RETARGETS.items():
    ADDITIONAL_CONTROL_RETARGETS[_coordinate] = (
        ADDITIONAL_CONTROL_RETARGETS.get(_coordinate, ())
        + (_retarget,)
    )

MORPHOLOGY_CONTROL_RETARGETS = {
    (1, 11): ((1, 1247),),
    (1, 17): ((244, 1247),),
    (1, 27): ((832, 1247),),
    (2, 111): ((178, 550),),
    (2, 112): ((178, 550),),
    (2, 133): ((322, 1247),),
    (2, 137): ((508, 1247),),
    (6, 1132): ((730, 1247),),
    **{
        (6, record_id): ((508, 1247),)
        for record_id in (*range(2101, 2113), 3564)
    },
    (6, 3414): ((1096, 466),),
    (6, 3406): ((376, 178),),
    (6, 3413): ((508, 1247),),
    (6, 3508): ((250, 598),),
    (6, 3514): ((850, 1247),),
    (6, 3517): ((508, 1247),),
    (6, 3518): ((472, 70),),
    (6, 3520): ((670, 160), (70, 550)),
    (6, 3527): ((1096, 1066),),
    (6, 3528): ((928, 160),),
    (6, 3530): ((124, 1066),),
    (6, 3547): ((82, 550),),
    (6, 3556): ((298, 70),),
    (6, 3627): ((928, 160),),
    (6, 3652): ((562, 550),),
    (6, 3656): ((562, 550),),
    (6, 3662): ((1162, 1126),),
    (6, 3734): ((628, 70),),
    (6, 3773): ((1096, 466),),
    (6, 3852): ((568, 550),),
    (6, 3864): ((1162, 1247),),
    (6, 3885): ((1162, 1247),),
    (6, 3886): ((508, 1247),),
    (6, 3943): ((178, 70),),
    (6, 3946): ((178, 70),),
    (6, 3949): ((178, 70),),
    (6, 3931): ((424, 1247),),
    (6, 4029): ((178, 550),),
    (6, 4062): ((1096, 178),),
    (6, 4212): ((190, 466),),
    (6, 4183): ((568, 550),),
    (6, 4916): ((286, 610),),
    (6, 4258): ((538, 70),),
    (6, 4350): ((508, 1247),),
    (6, 4368): ((508, 550),),
    (6, 4436): ((184, 1247),),
    (6, 4460): ((928, 160),),
    (6, 4466): ((928, 160),),
    (6, 4469): ((1096, 466),),
    (6, 4472): ((190, 466),),
    (6, 4599): ((1198, 1247),),
    (6, 4683): ((1144, 1247), (730, 1247)),
    (6, 4842): ((1186, 1198),),
    (6, 4937): ((574, 1247), (298, 754)),
    (7, 2488): ((1144, 1247), (808, 1247)),
    (7, 2875): ((412, 1247),),
    (8, 271): ((70, 550), (508, 1247)),
    (8, 272): ((70, 550), (508, 1247)),
    (8, 294): ((88, 286),),
    (8, 1108): ((712, 1247),),
    (15, 434): ((508, 1247),),
    (15, 926): ((148, 1247),),
    (15, 1066): ((76, 808),),
    (15, 2193): ((550, 70), (508, 1247)),
    (15, 2233): ((412, 322),),
    (6, 4563): ((298, 160),),
    (6, 4567): ((310, 466),),
    (6, 4568): ((310, 466),),
    (6, 4569): ((310, 466),),
    (6, 4615): ((736, 70), (730, 1247)),
    (6, 4619): ((298, 70),),
    (6, 4640): ((754, 1247),),
    (6, 4646): ((736, 1247),),
    (6, 4675): ((184, 1247), (568, 466), (730, 1247)),
    (6, 4743): ((376, 178),),
    (6, 4705): ((754, 1247), (730, 1247)),
    (6, 4706): ((1090, 1247), (730, 1247)),
    (6, 4699): ((730, 1247),),
    (6, 4712): ((730, 1247),),
    (6, 4717): ((748, 1126), (736, 1247)),
    (6, 4726): ((748, 466), (730, 1247)),
    (6, 4731): ((508, 1247),),
    (6, 4735): ((508, 1247),),
    (6, 4745): ((730, 1247), (1162, 1126)),
    (6, 4766): ((748, 754), (736, 1247), (1162, 1247)),
    (6, 4895): ((190, 1247),),
    (6, 4889): ((730, 1247),),
    (6, 4891): ((730, 1247),),
    (6, 4876): ((376, 178),),
    (7, 273): ((538, 70),),
    (7, 277): ((376, 70),),
    (7, 330): ((743, 160),),
    (7, 829): ((718, 742),),
    (7, 326): ((569, 550),),
    (7, 327): ((1091, 466),),
    (7, 830): ((568, 550),),
    (7, 993): ((730, 1247),),
    (7, 2461): ((736, 1247),),
    (7, 2472): ((556, 550),),
    (7, 2473): ((556, 550),),
    (7, 2514): ((670, 160),),
    (7, 2490): ((412, 322),),
    (7, 2831): ((568, 550),),
    (7, 2869): ((1096, 466), (508, 1247)),
    (7, 2870): ((1096, 466), (508, 1247)),
    (7, 2873): ((562, 550),),
    (8, 279): ((568, 550),),
    (8, 280): ((568, 550),),
    (8, 283): ((376, 178),),
    (8, 286): ((376, 178), (808, 1066)),
    (8, 306): ((178, 70), (508, 1247)),
    (8, 307): ((376, 70), (178, 142)),
    (8, 337): ((376, 550),),
    (8, 1018): ((1096, 142),),
    **{
        (8, record_id): ((178, 70),)
        for record_id in range(288, 293)
    },
    **{
        (8, record_id): ((538, 466), (568, 550))
        for record_id in (323, 324, 325, 347, 348, 350)
    },
    (8, 328): ((82, 550),),
    (8, 327): ((562, 550),),
    (8, 330):
        ((82, 550), (496, 1247), (808, 1247), (508, 1247)),
    (8, 928): ((466, 1066),),
    (8, 950): ((466, 1066),),
    **{
        (8, record_id): ((1162, 1247),)
        for record_id in range(951, 963)
    },
    **{
        (8, record_id): ((628, 70),)
        for record_id in (993, 999, 1005, 1011, 1019, 1027)
    },
    (8, 1103): ((508, 1247),),
    (8, 1014): ((568, 550),),
    (8, 1081): ((592, 1247), (730, 1247)),
    (8, 1113): ((88, 610),),
    (9, 3510): ((250, 598),),
    (9, 1830): ((1090, 1247),),
    (9, 3582): ((730, 1247),),
    (9, 4129): ((730, 1247),),
    (9, 4132): ((730, 1247),),
    (9, 4138): ((730, 1247),),
    (9, 4142): ((730, 1247), (1048, 142)),
    (9, 3951): ((376, 178), (730, 1247)),
    (15, 262): ((388, 1247),),
    (15, 255): ((412, 322),),
    (15, 257): ((1162, 202), (1096, 142)),
    (12, 16): ((376, 550),),
    (15, 1412): ((610, 1247),),
    **{
        (15, record_id): ((508, 1247),)
        for record_id in (230, 234, 238, 242, 2380)
    },
    **{
        (15, record_id): ((730, 1247),)
        for record_id in (
            1099, 1357, 1359, 1557, 2535, 2536,
        )
    },
    **{
        (15, record_id): ((82, 550),)
        for record_id in range(474, 486)
    },
    (15, 473): ((562, 550),),
    (15, 903): ((82, 550),),
    (15, 811): ((376, 550),),
    (15, 1095): ((736, 1247),),
    (15, 1136): ((730, 1247),),
    (15, 1449): ((568, 550), (730, 1247)),
    (15, 1546): ((508, 1247), (412, 322)),
    **{
        (15, record_id): ((1096, 466),)
        for record_id in (1548, 1550, 1551, 1554)
    },
    (15, 1552): ((568, 1247), (1096, 466)),
    (15, 1558): ((1096, 466),),
    (15, 1559): ((412, 322),),
    (15, 1582): ((538, 70), (1096, 70)),
    (15, 1585): ((634, 70),),
    (15, 1586): ((1162, 1247),),
    (15, 1572): ((412, 322),),
    (15, 1574): ((412, 322),),
    (15, 1576): ((412, 322),),
    (15, 1627): ((178, 70),),
    (15, 1657): ((82, 550), (730, 1247)),
    (15, 1700): ((610, 70),),
    (15, 1855): ((178, 70), (286, 610)),
    (15, 1832): ((610, 1247),),
    (15, 2196): ((628, 70), (508, 1247)),
    (15, 2184): ((376, 178),),
    (15, 2204): ((628, 70), (508, 1247)),
    (15, 2285): ((1162, 1126),),
    (15, 2287): ((190, 466),),
    (15, 2381): ((508, 1247), (1096, 142)),
    (15, 2382): ((508, 1247), (1096, 142)),
    **{
        (15, record_id): ((1162, 1247),)
        for record_id in (1943, 1948, 1952, 1955, 1960)
    },
    (15, 2405): ((190, 466),),
    (15, 2435): ((538, 70),),
    (15, 2437): ((538, 70),),
    (15, 2321): ((1162, 1126),),
    (15, 2406): ((178, 1247),),
    (15, 2502): ((700, 1247), (1096, 142)),
    (15, 2553): ((508, 1247), (730, 1247)),
    (15, 2573): ((412, 1247),),
    (15, 2586): ((298, 1247),),
    (15, 2457): ((730, 1247),),
    (15, 2467): ((562, 550),),
    (15, 2517): ((508, 1247), (412, 1247)),
    (15, 2558): ((736, 1247),),
    (15, 2559): ((730, 1247),),
}
FINAL_CALL_ASSEMBLY_CONTROL_RETARGETS = {
    **{
        (6, record_id): ((568, 550),)
        for record_id in range(4184, 4196)
    },
    (6, 4351): ((508, 1247),),
    (6, 4671): ((928, 1247),),
    (6, 4680): ((1096, 142), (508, 1247)),
    (6, 3409): ((322, 1247),),
    (7, 222): ((7, 1247),),
    (7, 734): ((7, 1247),),
    (7, 799): ((7, 1247),),
    (7, 2490): ((178, 1247),),
    (7, 2600): ((1, 1247),),
    (8, 1204): ((568, 1247),),
    (9, 3967): ((1096, 1247),),
    (9, 2104): ((6, 1247),),
    (9, 2641): ((4, 1247),),
    (15, 320): ((796, 1247),),
    (15, 321): ((796, 1247),),
    (15, 703): ((1090, 142),),
    (15, 704): ((1096, 1247),),
    (15, 1572): ((808, 1247),),
    (15, 1677): ((82, 550),),
    (15, 1912): ((1096, 142),),
    (15, 1930): ((310, 142),),
    (15, 1946): ((1162, 1247),),
    (15, 2294): ((82, 550),),
    (15, 2441): ((1096, 1247),),
    (15, 2554): (
        (508, 1247),
        (610, 1247),
        (730, 1247),
    ),
}
for _coordinate, _retargets in FINAL_CALL_ASSEMBLY_CONTROL_RETARGETS.items():
    MORPHOLOGY_CONTROL_RETARGETS[_coordinate] = (
        MORPHOLOGY_CONTROL_RETARGETS.get(_coordinate, ())
        + _retargets
    )
for _coordinate, _retargets in MORPHOLOGY_CONTROL_RETARGETS.items():
    ADDITIONAL_CONTROL_RETARGETS[_coordinate] = (
        ADDITIONAL_CONTROL_RETARGETS.get(_coordinate, ())
        + _retargets
    )

ADDITIONAL_CONTROL_RETARGET_REASONS = {
    ((1, 11), 94, 1247):
        "reviewed_fixed_schedule_clause_contains_its_own_connector",
    ((1, 25), 880, 1247):
        "reviewed_fixed_refusal_contains_its_own_terminal",
    ((2, 133), 628, 550):
        "house_head_noun_requires_coherent_copular_terminal_family",
    ((2, 248), 376, 178):
        "existential_stem_requires_predicative_terminal_family",
    ((6, 3507), 1096, 142):
        "recognition_noun_requires_coherent_action_terminal_family",
    ((6, 3528), 574, 1247):
        "reviewed_adversative_clause_contains_its_own_connector",
    ((6, 3763), 568, 520):
        "nominalized_advice_requires_coherent_copular_family",
    ((6, 3764), 568, 520):
        "nominalized_warning_requires_coherent_copular_family",
    ((6, 3764), 718, 550):
        "nominalized_choice_requires_coherent_copular_family",
    ((6, 3765), 34, 1247):
        "clan_selector_uses_literal_envoy_relation_without_honorific_call",
    ((6, 3766), 1096, 1247):
        "reviewed_conditional_request_contains_its_own_terminal",
    ((6, 3769), 1096, 2633):
        "reviewed_assent_question_uses_single_question_terminal",
    ((6, 3532), 298, 748):
        "negated_experience_stem_requires_coherent_negative_family",
    ((6, 3849), 34, 1247):
        "clan_selector_uses_literal_house_head_relation_without_honorific_call",
    ((6, 3942), 34, 1247):
        "clan_selector_uses_literal_side_relation_without_honorific_call",
    ((6, 4179), 748, 142):
        "reviewed_followup_attack_uses_coherent_action_terminal_family",
    **{
        ((6, record_id), 1198, 322):
            "request_stem_requires_coherent_imperative_terminal_family"
        for record_id in (4561, 4564, 4577, 4579, 4652, 4816)
    },
    **{
        ((6, record_id), 748, 1247):
            "redundant_negative_terminal_removed_from_request_question"
        for record_id in (4561, 4564, 4577, 4579, 4652, 4816)
    },
    **{
        ((6, record_id), old_target, 1247):
            "reviewed_fixed_question_contains_its_own_terminal"
        for record_id in (4565, 4566, 4580, 4651, 4690)
        for old_target in (1198, 748)
    },
    ((6, 4763), 1048, 1247):
        "nominal_question_uses_following_question_terminal_only",
    ((6, 4588), 376, 550):
        "nominal_judgment_requires_coherent_copular_family",
    ((6, 4645), 1096, 142):
        "evaluation_noun_requires_coherent_action_terminal_family",
    ((6, 4645), 736, 1247):
        "reviewed_ellipsis_contains_its_own_terminal",
    ((6, 4707), 610, 1247):
        "reviewed_conditional_follows_dynamic_honorific_stem_directly",
    ((7, 272), 748, 160):
        "forget_stem_requires_coherent_negative_terminal_family",
    ((7, 335), 1096, 142):
        "negative_ability_stem_requires_coherent_action_terminal_family",
    ((7, 2512), 376, 1247):
        "reviewed_fixed_capacity_warning_contains_both_terminals",
    ((8, 296), 508, 1247):
        "reviewed_complete_statement_removes_optional_trailing_atom",
    ((8, 1031), 568, 1247):
        "reviewed_fixed_illness_sentence_uses_proved_empty_terminal",
    ((8, 1031), 442, 1247):
        "reviewed_fixed_recovery_sentence_uses_proved_empty_terminal",
    ((8, 1031), 1168, 1247):
        "reviewed_fixed_time_request_uses_proved_empty_terminal",
    ((8, 1237), 1096, 1247):
        "reviewed_fixed_reluctant_assent_contains_its_own_terminal",
    ((6, 4468), 178, 1247):
        "reviewed_fixed_siege_expertise_sentence_uses_empty_terminal",
    ((6, 4468), 1, 1247):
        "reviewed_impersonal_castle_assignment_omits_persona_call",
    ((9, 3953), 88, 70):
        "existential_probability_stem_requires_coherent_terminal_family",
    ((6, 2074), 700, 1247):
        "redundant_question_stem_removed",
    ((6, 2074), 610, 2633):
        "reviewed_instruction_question_uses_single_question_terminal",
    ((7, 884), 634, 550):
        "nominalized_anger_result_requires_copular_family",
    ((7, 884), 808, 466):
        "reviewed_countermeasure_uses_coherent_action_family",
    ((8, 303), 376, 178):
        "existential_stem_requires_predicative_terminal_family",
    ((15, 379), 568, 178):
        "existential_stem_requires_predicative_terminal_family",
    ((15, 364), 1150, 538):
        "past_rejection_stem_requires_coherent_past_terminal_family",
    ((15, 364), 394, 1247):
        "reviewed_apology_contains_its_own_terminal",
    ((15, 517), 1096, 142):
        "expectation_noun_requires_coherent_action_terminal_family",
    ((15, 228), 1096, 550):
        "nominalized_low_probability_judgment_requires_copular_family",
    ((15, 284), 568, 550):
        "nominalized_plan_judgment_requires_coherent_copular_family",
    ((15, 762), 748, 70):
        "existential_risk_stem_requires_predicative_terminal_family",
    ((15, 1383), 748, 1247):
        "reviewed_fixed_public_sentiment_warning_contains_its_own_terminal",
    ((15, 1384), 1096, 550):
        "nominalized_public_sentiment_risk_requires_copular_family",
    ((15, 514), 298, 2633):
        "reviewed_recruitment_proposal_uses_single_question_terminal",
    ((15, 819), 1048, 2633):
        "reviewed_sortie_proposal_uses_single_question_terminal",
    ((15, 1234), 1048, 2633):
        "reviewed_tunnel_proposal_uses_single_question_terminal",
    ((15, 1234), 286, 1247):
        "redundant_second_question_terminal_removed",
    ((15, 1537), 700, 1247):
        "redundant_question_stem_removed",
    ((15, 1537), 424, 2634):
        "reviewed_recruitment_decision_uses_single_question_terminal",
    ((15, 1701), 700, 1247):
        "redundant_question_stem_removed",
    ((15, 1701), 616, 2634):
        "reviewed_campaign_decision_uses_single_question_terminal",
    **{
        ((15, 1614), old_target, 1247):
            "reviewed_fixed_withdrawal_statement_contains_its_own_terminal"
        for old_target in (310, 376, 286)
    },
    ((15, 1863), 1096, 142):
        "judgment_noun_requires_coherent_action_terminal_family",
    ((15, 2211), 82, 142):
        "concern_noun_requires_coherent_action_terminal_family",
    **{
        ((15, 2211), old_target, 1247):
            "reviewed_fixed_question_contains_its_own_terminal"
        for old_target in (700, 610)
    },
    **{
        ((15, record_id), old_target, new_target):
            (
                "explanation_noun_requires_coherent_action_terminal_family"
                if old_target == 1096
                else "reviewed_complete_statement_removes_optional_trailing_atom"
            )
        for record_id in (2406, 2408)
        for old_target, new_target in ((1096, 142), (508, 1247))
    },
    ((15, 2579), 700, 1247):
        "redundant_question_stem_removed",
    ((15, 2579), 466, 2633):
        "reviewed_target_choice_uses_single_question_terminal",
    ((15, 2592), 574, 1247):
        "reviewed_adversative_literal_contains_its_own_connector",
    ((15, 2593), 538, 550):
        "nominalized_decisive_moment_requires_copular_family",
    ((15, 2593), 568, 550):
        "nominalized_clan_fate_requires_coherent_copular_family",
    ((15, 2593), 1096, 466):
        "petition_noun_requires_coherent_action_family",
    ((8, 1239), 1048, 1247):
        "redundant_positive_terminal_removed",
    ((8, 1239), 610, 2634):
        "reviewed_delegation_question_uses_single_question_terminal",
    ((15, 1512), 610, 2634):
        "reviewed_training_question_uses_single_question_terminal",
    ((15, 1522), 610, 2634):
        "reviewed_bandit_assignment_question_uses_single_question_terminal",
    ((15, 2449), 34, 1247):
        "person_selector_uses_additive_relation_without_honorific_call",
    ((15, 2449), 8, 1247):
        "reviewed_counterparty_relation_uses_fixed_our_side_object",
    ((1, 14), 196, 1247):
        "reviewed_laughter_command_contains_its_own_terminal",
    ((1, 14), 136, 1247):
        "reviewed_recollection_contains_its_own_past_terminal",
    ((2, 560), 976, 1247):
        "reviewed_battle_plan_propositive_contains_its_own_terminal",
    ((6, 549), 256, 1247):
        "reviewed_visibility_question_contains_its_own_terminal",
    ((6, 3062), 628, 70):
        "past_remaining_duration_requires_generic_past_terminal_family",
    ((6, 3110), 550, 1247):
        "reviewed_incompatibility_statement_contains_its_own_terminal",
    ((6, 3535), 550, 1247):
        "reviewed_family_relation_contains_its_own_terminal",
    ((6, 3555), 598, 1247):
        "reviewed_reward_moment_contains_its_own_terminal",
    ((6, 3555), 562, 1247):
        "reviewed_happiness_statement_contains_its_own_terminal",
    ((6, 3625), 562, 1247):
        "reviewed_exchange_reaction_contains_its_own_terminal",
    ((6, 3631), 562, 1247):
        "reviewed_treasure_return_reaction_contains_its_own_terminal",
    ((6, 4203), 628, 70):
        "past_proposal_report_requires_generic_past_terminal_family",
    ((6, 4210), 508, 1247):
        "duplicate_terminal_after_reward_command_removed",
    ((6, 4444), 550, 1247):
        "reviewed_facility_postponement_contains_its_own_terminals",
    ((6, 4808), 988, 1247):
        "reviewed_relation_break_contains_its_own_terminal",
    ((7, 2436), 1096, 1247):
        "reviewed_next_castle_attack_contains_its_own_terminal",
    ((7, 2436), 190, 1247):
        "reviewed_destination_statement_contains_its_own_terminal",
    ((7, 2436), 508, 1247):
        "duplicate_terminal_after_destination_removed",
    ((7, 334), 982, 1247):
        "reviewed_refusal_contains_its_own_terminal",
    ((9, 3990), 190, 1247):
        "reviewed_defensive_fighting_statement_contains_its_own_terminal",
    ((15, 268), 304, 1247):
        "reviewed_strategy_statement_removes_incompatible_listen_command",
    ((15, 269), 628, 70):
        "past_strategy_acquisition_requires_generic_past_terminal_family",
    ((15, 1502), 376, 1247):
        "reviewed_unrest_statement_contains_its_own_terminal",
    ((15, 1502), 556, 1247):
        "reviewed_ikki_warning_contains_its_own_terminal",
    ((15, 1541), 772, 1247):
        "reviewed_wanderer_search_contains_its_own_terminal",
    ((15, 1541), 286, 1247):
        "reviewed_alternative_search_contains_its_own_terminal",
    ((15, 1615), 286, 1247):
        "reviewed_withdrawal_judgment_contains_its_own_terminal",
    ((15, 1674), 628, 70):
        "past_domain_growth_requires_generic_past_terminal_family",
}
ADDITIONAL_CONTROL_RETARGET_REASONS.update(
    {
        (coordinate, old_target, new_target):
            "question_predicate_family_is_complete_without_second_terminal"
        for coordinate, (old_target, new_target)
        in QUESTION_DOUBLE_TERMINAL_RETARGETS.items()
    }
)
ADDITIONAL_CONTROL_RETARGET_REASONS.update(
    {
        (coordinate, old_target, new_target):
            "reviewed_past_stem_requires_generic_predicative_terminal_family"
        for coordinate, (old_target, new_target)
        in PAST_BOUNDARY_RETARGETS.items()
    }
)
ADDITIONAL_CONTROL_RETARGET_REASONS.update(
    {
        (coordinate, old_target, new_target):
            "full_cartesian_morphology_owner_repair"
        for coordinate, retargets in MORPHOLOGY_CONTROL_RETARGETS.items()
        for old_target, new_target in retargets
    }
)

# This record contains the same mixed copular terminal twice.  Both operands
# are intentionally removed because the reviewed fixed literals now contain
# the complete capacity warning.
MULTI_OCCURRENCE_CONTROL_RETARGET_COUNTS = {
    ((7, 2512), 376, 1247): 2,
    ((6, 4444), 550, 1247): 2,
    ((8, 279), 568, 550): 2,
    ((8, 280), 568, 550): 2,
    ((8, 272), 70, 550): 2,
    ((15, 2406), 178, 1247): 2,
}

CALL_FIXED_BOUNDARY_REWRITES = {
    (8, 497, 1): "」 곁에서 더\n실컷 날뛰고 싶었는데…",
    (6, 4469, 2): "…",
    (15, 1582, 2): "…",
    (15, 1805, 1): "…",
    (15, 1806, 1): "…",
    (15, 1818, 1): "…",
    (15, 1819, 1): "…",
    (15, 1821, 1): "…",
}

COORDINATE_DUAL_REWRITES = {
    (1, 24, 0): "도 지면 물구나무서서 알몸으로 마을을 한 바퀴 돌고",
    (2, 107, 1): " 곁에\n설 때가 마침내\n와 참으로 기쁘옵니다",
    (2, 223, 2): " 곁을 지켜\n신용 확보를 장담하",
    (6, 824, 0): "도 인정하지 못할\n작은 그릇이 아니다",
    (6, 3752, 0): "의 몫까지\n",
    (6, 3753, 0): "의 몫까지\n",
    (7, 874, 0): "도 성에 온다\n어서 기병에 대비하",
    (7, 877, 1): "」도 왔는가……!\n",
    (7, 884, 0): "의 분노를 사고 말",
    (7, 891, 0): "도, 이런 곳까지!\n죽음도 모르는 거친 무사들에게\n어찌 맞서",
    (9, 520, 0): " 상대로 승리하여\n내 무예를 빛내리라!",
    (9, 533, 0): " 추적을 놓치면\n대대로 수치가 되리라",
    (9, 843, 1): "향해\n베었습니다!",
    (9, 846, 0): "향해\n칠 때가 오다니",
    (9, 1784, 0): " 추적을 놓치지 마라\n숨통을 끊는 것이다!",
    (9, 1802, 0): "향해\n추격합시다!",
    (9, 1826, 0): "의\n피격을 막아라!",
    (9, 1855, 0): "에게 감히…\n절대 용서 못 한다!",
    (9, 1864, 0): "에게 감히!\n대가는 비쌀 것이다!",
    (9, 1902, 0): "의\n구출책은 없을까……",
    (9, 2038, 0): "에게 권하여\n아군으로 삼을 수 있다면…",
    (9, 2591, 0): " 곁을\n지킵시다!",
    (9, 2766, 0): "향해\n추격하라, 질 수는 없다!",
    (15, 391, 1): "에게\n권유하고자 하옵니다\n무언가 큰 불만을 품고 있다 하옵니다",
    (15, 434, 0): "에게 권해\n우리 가문에 영입했",
    (15, 443, 0): "께 인사하고 싶었사옵니다\n앞으로 신세를 지겠사오며 이름은",
    (9, 2070, 0): "무척 화려하구나……\n어지간히 차이가 벌어졌군……",
    (13, 192, 2): " 표시가 있는 건의를\n선택해 주십시오",
    (13, 195, 2): " 표시가 있는 건의를 선택",
    (15, 1661, 3): "을 편성해 보시는 것은 어떻겠습니까?",
    (15, 1663, 2): "을 새로 편성해\n통치에 보태",
    (15, 1703, 1): "은 확인하",
    (17, 5, 1): "와",
    (17, 5, 3): "가 멋대로 출전했다고……!?\n강화를 앞두고,",
}

MANUAL_ASSEMBLY_REWRITES: dict[tuple[int, int, int], str] = {}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PkRemediationError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return "".join(
        json.dumps(
            dict(row),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in rows
    )


def atomic_write(path: Path, data: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = data.encode("utf-8") if isinstance(data, str) else data
    handle, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def records_from_blob(blob: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    archive = parse_packed_msggame(blob).archive
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def literal_map(blob: bytes) -> dict[tuple[int, int, int], str]:
    return {
        (record.block_id, record.record_id, literal.literal_id): literal.text
        for block in parse_packed_msggame(blob).archive.blocks
        for record in block.records
        for literal in parse_record_literals(record)
    }


def record_nonliteral_gaps(record: MsgGameRecord) -> tuple[bytes, ...]:
    literals = parse_record_literals(record)
    gaps: list[bytes] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor:literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def hangul_jongseong(value: str) -> int | None:
    code = ord(value)
    if 0xAC00 <= code <= 0xD7A3:
        return (code - 0xAC00) % 28
    if value.isdigit():
        # Sino-Korean readings: 영 일 이 삼 사 오 육 칠 팔 구.
        return {
            "0": 21,
            "1": 8,
            "2": 0,
            "3": 16,
            "4": 0,
            "5": 0,
            "6": 1,
            "7": 8,
            "8": 8,
            "9": 0,
        }[value]
    return None


def last_lexical_character(value: str) -> str | None:
    for character in reversed(value):
        if 0xAC00 <= ord(character) <= 0xD7A3 or character.isdigit():
            return character
        if character.isalpha():
            return None
    return None


def choose_particle(token: str, previous: str) -> str:
    jongseong = hangul_jongseong(previous)
    require(jongseong is not None, f"cannot resolve particle after {previous!r}")
    if token == "이(가)":
        return "이" if jongseong else "가"
    if token == "은(는)":
        return "은" if jongseong else "는"
    if token == "을(를)":
        return "을" if jongseong else "를"
    if token == "와(과)":
        return "과" if jongseong else "와"
    if token in {"(으)로", "으로(로)"}:
        return "로" if jongseong in {0, 8} else "으로"
    raise PkRemediationError(f"unsupported dual particle: {token}")


def particle_kind(value: str) -> str:
    if value in {"이(가)", "이", "가"}:
        return "subject"
    if value in {"은(는)", "은", "는"}:
        return "topic"
    if value in {"을(를)", "을", "를"}:
        return "object"
    if value in {"와(과)", "와", "과"}:
        return "comitative"
    if value in {"(으)로", "으로(로)", "로", "으로"}:
        return "directional"
    raise PkRemediationError(f"unknown particle kind: {value}")


def selector_contract(
    selector: Mapping[str, Any] | None,
) -> tuple[int, int] | None:
    if selector is None:
        return None
    property_value = selector.get("property")
    if not isinstance(property_value, int):
        return None
    return int(selector["group"]), property_value


def group_one_semantic_carrier(
    coordinate: tuple[int, int, int],
    text: str,
    pristine_jp: str,
) -> str:
    """Classify generic string-slot use from its coordinate and JP predicate."""

    block_id, record_id, _literal_id = coordinate
    haystack = f"{text}\n{pristine_jp}"
    if block_id == 9:
        return "전법"
    if block_id == 17:
        return "부대" if "교전" in text or "협공" in text else "세력"
    if block_id == 16:
        return "세력"
    if block_id == 12:
        return "이름"
    if block_id == 7:
        if 894 <= record_id <= 901:
            return "병력"
        if record_id == 1916:
            return "거점"
        if record_id == 2878:
            return "세력"
        return "장수"
    if block_id == 8:
        if record_id == 931:
            return "직책"
        if (
            948 <= record_id <= 1005
            or 1119 <= record_id <= 1196
            or any(value in haystack for value in ("건설", "발전", "번영"))
        ):
            return "시설"
        return "임무"
    if block_id == 3:
        return "설정"
    if block_id == 2:
        if record_id in {210, 211}:
            return "거점"
        if record_id in {678, 679}:
            return "권리"
        return "임무"
    if block_id == 6:
        if 1411 <= record_id <= 1415:
            return "거점"
        if 3456 <= record_id <= 3590 or record_id in {
            3862, 3864, 4043, 4562, 4563, 4908, 4910
        }:
            return "직책"
        if 3621 <= record_id <= 3683:
            return "가보"
        if 3688 <= record_id <= 3694:
            return "관직"
        if (
            3846 <= record_id <= 3940
            or record_id in {1190, 3882, 3883, 3886, 3888, 3938, 3939,
                             3940, 4321, 4369, 4443, 4446, 4792}
        ):
            return "시설"
        if 4387 <= record_id <= 4404 or record_id in {4248, 4249, 4340}:
            return "정책"
        if 2061 <= record_id <= 2074 or 4069 <= record_id <= 4160:
            return "명령"
        if record_id in {3337, 3341, 3342, 3778}:
            return "세력"
        if 3792 <= record_id <= 3803:
            return "임무"
        if record_id == 3944:
            return "거점"
        if record_id == 4229:
            return "특성"
        if record_id == 4528:
            return "기간"
    if block_id == 15:
        if 691 <= record_id <= 702 or record_id in {1572, 1617, 1631}:
            return "세력" if record_id < 1500 else "지역"
        if 831 <= record_id <= 1500:
            return "단계" if record_id == 1219 else "계책"
        if 1508 <= record_id <= 1519:
            return "특성"
        if (
            1666 <= record_id <= 1672
            or 1896 <= record_id <= 2171
            or 2301 <= record_id <= 2325
        ):
            if any(
                value in haystack
                for value in ("건설", "철거", "증축", "짓", "시설")
            ):
                return "시설"
            return "정책"
        if 2397 <= record_id <= 2402:
            return "물자"
        if 2518 <= record_id <= 2548:
            return "계책"
        if any(
            value in haystack
            for value in (
                "밀명", "계책", "저지", "주효", "피해", "걸", "奏功",
                "阻止", "密命",
            )
        ):
            return "계책"
        if any(value in haystack for value in ("시행", "실행", "추진", "발령")):
            return "정책"
        if any(value in haystack for value in ("완수", "성공", "임무")):
            return "임무"
        if record_id in {287, 288}:
            return "제안"
    if any(value in haystack for value in ("건설", "철거", "완공", "증축")):
        return "시설"
    if any(value in haystack for value in ("발령", "시행", "실행", "개정")):
        return "정책"
    if any(value in haystack for value in ("발동", "간파", "밀명", "계책")):
        return "전법"
    if any(value in haystack for value in ("임명", "천거", "발탁", "훈공")):
        return "직책"
    raise PkRemediationError(
        f"unclassified group-1 selector context: {coordinate} "
        f"{text!r} / {pristine_jp!r}"
    )


def semantic_selector_carrier(
    group: int,
    coordinate: tuple[int, int, int],
    text: str,
    pristine_jp: str,
) -> str:
    if group == 1:
        return group_one_semantic_carrier(coordinate, text, pristine_jp)
    if group == 9:
        # The static label is a generic named-object slot, but every affected
        # pristine JP coordinate is an 国衆 persuasion/incorporation context.
        # The selector itself already emits the 国衆 name.  ``측`` preserves
        # that role without mechanically repeating ``국인중`` after it.
        return "측"
    if group == 10:
        # Despite the abstract slot label, affected pristine JP predicates
        # consistently describe 郡 conquest, flood control, roads, or tenure.
        return "군"
    if group == 11:
        # All affected coordinates are block-9 battlefield runtime objects.
        return "부대"
    carrier = CARRIER_BY_GROUP.get(group)
    require(carrier is not None, f"unknown selector group carrier: {group}")
    return carrier


def append_particle(carrier: str, particle: str, *, leading_space: bool = True) -> str:
    kind = particle_kind(particle)
    if kind == "directional":
        suffix = choose_particle("(으)로", carrier[-1])
    elif kind == "subject":
        suffix = choose_particle("이(가)", carrier[-1])
    elif kind == "topic":
        suffix = choose_particle("은(는)", carrier[-1])
    elif kind == "object":
        suffix = choose_particle("을(를)", carrier[-1])
    else:
        suffix = choose_particle("와(과)", carrier[-1])
    return f"{' ' if leading_space else ''}{carrier}{suffix}"


def carrier_with_particle(
    group: int,
    particle: str,
    *,
    coordinate: tuple[int, int, int],
    text: str,
    pristine_jp: str,
) -> str:
    carrier = semantic_selector_carrier(group, coordinate, text, pristine_jp)
    return append_particle(carrier, particle)


def honorific_object_relation(
    rest: str,
    coordinate: tuple[int, int, int],
) -> str:
    rewrites = (
        ("\n섬길 때가", "의 곁을 지킬 때가"),
        (" 섬기려 하니", "의 휘하에 들려 하니"),
        (" 섬기는 것은", "의 휘하에서 봉사하는 것은"),
        (" 섬기게 되어", "의 휘하에 들게 되어"),
        (" 섬기게 된 이상", "의 휘하에 든 이상"),
        (" 섬길 수 있어", "의 곁을 지킬 수 있어"),
        (" 모실 수 있게 되어", "의 곁을 지킬 수 있게 되어"),
        (" 모실 수 있어", "의 곁을 지킬 수 있어"),
        (" 모실 수 있었던 것은", "의 곁을 지킬 수 있었던 것은"),
        (" 모시고 싶었", "의 곁을 지키고 싶었"),
        (" 위해", "의 뜻을 위해"),
        (" 위하고\n보필", "의 뜻을 받들고\n보필"),
        (" 보좌하여", "의 곁에서 보좌하여"),
        (" 보좌", "의 곁에서 보좌"),
        (" 돕", "에게 힘을 보태"),
        (" 대신해", "의 역할을 대신해"),
        (" 인정하지", "의 존재를 인정하지"),
        (" 피하는", "의 곁을 피하는"),
        (" 지금 베지", "에게 칼을 겨누지"),
        (" 믿고", "의 말을 믿고"),
        (" 잃은 것뿐 아니라", "의 부재뿐 아니라"),
        (" 잃은 것도 뼈아프거늘", "의 부재도 뼈아프거늘"),
        (" 주군으로 받들어", "의 휘하에 들어"),
        (" 천하인으로 만드는 것이", "의 천하 통일을 돕는 것이"),
        (" 가문에 맞아들일 준비를", "의 영입 준비를"),
        (" 저버릴 수는", "의 뜻을 저버릴 수는"),
        (" 만날 수 있다", "께 인사드릴 수 있다"),
        (" 막아야 활로가", "의 진격을 막아야 활로가"),
        (" 천거하여", "의 이름을 천거하여"),
        (" 높이 사고 있", "의 재능을 높이 사고 있"),
        (" 포기할 수 없어서", "의 영입을 포기할 수 없어서"),
        (" 따르는 데", "의 뒤를 따르는 데"),
        (" 쓰러뜨려", "에게 맞서 승리하여"),
        (" 놓치면", "에게서 눈을 떼면"),
        (" 쓰러뜨릴 호기", "에게 맞설 호기"),
        ("\n베었습니다", "에게 일격을 가했습니다"),
        ("\n칠 날이 오다니", "에게 맞설 날이 오다니"),
        (" 놓치지 마라", "에게서 눈을 떼지 마라"),
        ("\n추격합시다", "의 뒤를 쫓읍시다"),
        ("\n치게 두지 마라", "의 피격을 허용하지 마라"),
        (" 감히…", "에게 감히 손을 대다니…"),
        (" 감히!", "에게 감히 손을 대다니!"),
        (" 피의 제물로\n삼아 주마", "의 피로 제사를\n지내 주마"),
        ("\n구할 방도가", "의 구출 방도가"),
        (" 치다니", "에게 덤비다니"),
        (" 설득하여", "에게 귀순을 권하여"),
        (" 설득해", "에게 귀순을 권해"),
        ("\n엄호합시다", "의 곁을 엄호합시다"),
        ("\n뒤쫓아라", "의 뒤를 쫓아라"),
        ("\n권유하고자", "에게 귀순을 권유하고자"),
        (" 농락하여", "에게 계책을 써"),
        ("\n뵙기를 청한 바", "께 인사드리기를 청한 바"),
        (" 뵙고 싶었", "께 인사드리고 싶었"),
        (" 애송이라 부르", "더러 애송이라 부르"),
        (" 농락하여", "에게 계책을 써"),
    )
    if rest == "!?":
        return "…!?"
    for source, replacement in rewrites:
        if rest.startswith(source):
            return replacement + rest[len(source):]
    raise PkRemediationError(
        f"unhandled honorific call object relation: {coordinate} {rest!r}"
    )


def pronoun_relation_rewrite(
    kind: str,
    rest: str,
    coordinate: tuple[int, int, int],
) -> tuple[str, str]:
    """Keep persona call 0:1 without the redundant ``본인`` carrier."""

    if kind in {"subject", "topic"}:
        return (
            " 스스로" + rest,
            f"call_pronoun_reflexive_adverb:0:1:{kind}",
        )
    if kind == "object":
        if coordinate in {(2, 442, 1), (6, 3583, 1), (9, 2751, 1)}:
            return "만" + rest, "call_pronoun_exclusive_follow_relation:0:1"
        if coordinate == (9, 364, 1):
            return "만" + rest, "call_pronoun_exclusive_trust_relation:0:1"
        if coordinate == (9, 1987, 0):
            require(
                rest.startswith(" 위해서"),
                f"pronoun motive relation drifted: {coordinate} {rest!r}",
            )
            return (
                " 때문" + rest[len(" 위해서"):],
                "call_pronoun_motive_relation:0:1",
            )
        if coordinate == (9, 2409, 0):
            return "조차" + rest, "call_pronoun_deception_relation:0:1"
        if coordinate == (9, 2412, 0):
            return "까지" + rest, "call_pronoun_deception_relation:0:1"
        if coordinate == (15, 435, 1):
            return "까지" + rest, "call_pronoun_rescue_relation:0:1"
        if coordinate == (7, 2662, 1):
            require(
                rest.startswith(" 두고"),
                f"pronoun speech relation drifted: {coordinate} {rest!r}",
            )
            return (
                "에게 하는 말이지!",
                "call_pronoun_speech_relation:0:1",
            )
        return (
            " 자신을" + rest,
            "call_pronoun_reflexive_object:0:1",
        )
    if kind == "comitative":
        rewrites = {
            (6, 3641, 2): (
                "에게서 강한 인연을 감지",
                "call_pronoun_affinity_relation:0:1",
            ),
            (6, 4472, 1): (
                " 못지않은 특성을\n"
                "지닌 이가 있어, 그 점은 강점입니다\n"
                "다만 인선은 재고해 주시길 바라",
                "call_pronoun_peer_trait_relation:0:1",
            ),
            (6, 4473, 2): (
                " 못지않은 특성의 자가\n그 성에서 보탬이 되",
                "call_pronoun_peer_trait_relation:0:1",
            ),
            (6, 4474, 2): (
                " 못지않은 이가 있으니…\n좋은 성과가 기대되는 인재",
                "call_pronoun_peer_relation:0:1",
            ),
            (9, 545, 1): (
                "에게 덤벼라",
                "call_pronoun_challenge_relation:0:1",
            ),
        }
        replacement = rewrites.get(coordinate)
        require(
            replacement is not None,
            f"unreviewed pronoun comitative relation: {coordinate} {rest!r}",
        )
        return replacement
    raise PkRemediationError(
        f"unreviewed pronoun relation: {coordinate} {kind} {rest!r}"
    )


def call_relation_rewrite(
    call: Mapping[str, Any],
    particle: str,
    rest: str,
    renderer: Any,
    coordinate: tuple[int, int, int],
) -> tuple[str, str]:
    target = tuple(call["target"])
    variants = renderer.render(target)
    direct: set[str] = set()
    dual_particle = DUAL_PARTICLE_BY_KIND[particle_kind(particle)]
    for variant in variants:
        previous = last_lexical_character(variant)
        if previous is None:
            direct.clear()
            break
        direct.add(choose_particle(dual_particle, previous))
    if len(direct) == 1:
        return (
            next(iter(direct)) + rest,
            f"call_rendered_fixed:{target[0]}:{target[1]}",
        )
    kind = particle_kind(particle)
    if target == (0, 1):
        if particle not in QA.DUAL_PARTICLES:
            invariant = "에" if kind == "directional" else "도"
            return (
                invariant + rest,
                f"call_pronoun_compact_relation:0:1:{kind}",
            )
        return pronoun_relation_rewrite(kind, rest, coordinate)
    if target in {(0, 4), (0, 6)}:
        if kind in {"subject", "topic"}:
            return "도" + rest, f"call_auxiliary_invariant:{target[1]}:{kind}"
        if kind == "object":
            return (
                honorific_object_relation(rest, coordinate),
                f"call_genitive_invariant:{target[1]}:object",
            )
    if target in {
        (0, 8), (0, 17), (0, 21), (0, 29), (0, 34),
        (0, 37), (0, 46), (0, 50),
    }:
        if particle not in QA.DUAL_PARTICLES:
            invariant = {
                "subject": "도",
                "topic": "도",
                "comitative": "도",
                "directional": "께",
            }.get(kind)
            if invariant is not None:
                return (
                    invariant + rest,
                    f"call_address_compact_relation:{target[1]}:{kind}",
                )
            return (
                rest,
                f"call_address_compact_object_nominal:{target[1]}",
            )
        if kind == "subject":
            return "께서" + rest, f"call_honorific_invariant:{target[1]}:subject"
        if kind == "topic":
            return "께서는" + rest, f"call_honorific_invariant:{target[1]}:topic"
        if kind == "comitative":
            return "하고" + rest, f"call_neutral_comitative:{target[1]}"
        if kind == "directional":
            return "께" + rest, f"call_honorific_invariant:{target[1]}:directional"
        return (
            honorific_object_relation(rest, coordinate),
            f"call_genitive_invariant:{target[1]}:object",
        )
    raise PkRemediationError(
        f"unhandled variable call relation: {coordinate} {target} "
        f"{particle!r} {rest!r}"
    )


def literal_context(
    record: MsgGameRecord,
    literal_id: int,
) -> tuple[Mapping[str, Any] | None, Mapping[str, Any] | None]:
    previous_selector: Mapping[str, Any] | None = None
    previous_call: Mapping[str, Any] | None = None
    for component in QA.tolerant_decode_record(record):
        kind = str(component["kind"])
        if kind == "selector":
            previous_selector = component
            previous_call = None
            continue
        if kind == "call":
            previous_call = component
            previous_selector = None
            continue
        if kind == "literal_boundary":
            if int(component["slot"]) == literal_id:
                return previous_selector, previous_call
            previous_selector = None
            previous_call = None
            continue
        if kind in QA.IGNORABLE_BETWEEN_SELECTOR_AND_LITERAL:
            continue
        previous_selector = None
        previous_call = None
    raise PkRemediationError(
        f"literal boundary is absent: "
        f"{record.block_id}:{record.record_id}:{literal_id}"
    )


PERSON_LIKE_SELECTOR_GROUPS = frozenset({1, 2, 5, 6})
PERSON_TITLE_BOUNDARY_TERMS = ("공", "님", "놈")
EXPECTED_DIRECT_PERSON_TITLE_BOUNDARY_COUNT = 301
DIRECT_UNIT_SELECTOR_GROUP = 1
DIRECT_UNIT_BOUNDARY_TERM = "부대"
EXPECTED_DIRECT_UNIT_BOUNDARY_COUNT = 163
EXPECTED_DIRECT_UNIT_BOUNDARY_COORDINATE_SHA256 = (
    "B77C833B2F7F4B461E3B5D396D129CAB84F5F13CEDC0BABBA7A9A6676423FAC8"
)
DYNAMIC_GENERAL_BOUNDARY_TERMS = (
    "주군",
    "부대",
    "군단",
    "공격",
    "공략",
    "취임",
    "요청",
    "장악",
    "성주",
    "격파",
    "본성",
    "실행",
    "회유",
    "통일",
    "건설",
    "증축",
    "등",
)
EXPECTED_DYNAMIC_GENERAL_BOUNDARY_OWNER_COUNT = 466
EXPECTED_DYNAMIC_GENERAL_BOUNDARY_OWNER_SHA256 = (
    "E9C6CD984E40C671F66C40EB7A86B84CABF94229B617E532FCC46EB7B3C675AB"
)
# This source row is already owned by the exact opaque-name rewrite and gains
# the same leading boundary there.  Excluding it keeps single ownership.
PREOWNED_DIRECT_PERSON_TITLE_BOUNDARIES = frozenset({(17, 580, 1)})


def direct_person_title_boundary_coordinates(
    records: Mapping[tuple[int, int], MsgGameRecord],
) -> frozenset[tuple[int, int, int]]:
    coordinates: set[tuple[int, int, int]] = set()
    for record in records.values():
        literals = parse_record_literals(record)
        for literal in literals:
            selector, _call = literal_context(record, literal.literal_id)
            if (
                selector is not None
                and int(selector["group"]) in PERSON_LIKE_SELECTOR_GROUPS
                and literal.text.startswith(PERSON_TITLE_BOUNDARY_TERMS)
                and (
                    record.block_id,
                    record.record_id,
                    literal.literal_id,
                ) not in PREOWNED_DIRECT_PERSON_TITLE_BOUNDARIES
            ):
                coordinates.add(
                    (record.block_id, record.record_id, literal.literal_id)
                )
    require(
        len(coordinates) == EXPECTED_DIRECT_PERSON_TITLE_BOUNDARY_COUNT,
        "direct person-title boundary universe drifted: "
        f"{len(coordinates)}",
    )
    return frozenset(coordinates)


def direct_unit_boundary_coordinates(
    records: Mapping[tuple[int, int], MsgGameRecord],
) -> frozenset[tuple[int, int, int]]:
    coordinates: set[tuple[int, int, int]] = set()
    for record in records.values():
        for literal in parse_record_literals(record):
            selector, _call = literal_context(record, literal.literal_id)
            if (
                selector is not None
                and int(selector["group"]) == DIRECT_UNIT_SELECTOR_GROUP
                and literal.text.startswith(DIRECT_UNIT_BOUNDARY_TERM)
            ):
                coordinates.add(
                    (record.block_id, record.record_id, literal.literal_id)
                )
    require(
        len(coordinates) == EXPECTED_DIRECT_UNIT_BOUNDARY_COUNT,
        "direct unit boundary universe drifted: "
        f"{len(coordinates)}",
    )
    require(
        coordinate_digest(coordinates)
        == EXPECTED_DIRECT_UNIT_BOUNDARY_COORDINATE_SHA256,
        "direct unit boundary coordinate digest drifted",
    )
    return frozenset(coordinates)


def dynamic_general_boundary_owner_coordinates(
    records: Mapping[tuple[int, int], MsgGameRecord],
) -> frozenset[tuple[int, int, int]]:
    owners: set[tuple[int, int, int]] = set()
    cache: dict[
        tuple[tuple[int, int], int | None],
        frozenset[int | None],
    ] = {}

    def visible(value: str) -> str:
        return "".join(
            character
            for character in value
            if character in "\r\n\t"
            or not unicodedata.category(character).startswith("C")
        )

    def execute(
        coordinate: tuple[int, int],
        incoming_selector_group: int | None,
        trail: tuple[tuple[int, int], ...] = (),
    ) -> frozenset[int | None]:
        cache_key = (coordinate, incoming_selector_group)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        if coordinate in trail:
            return frozenset({incoming_selector_group})
        record = records.get(coordinate)
        require(
            record is not None,
            "dynamic boundary edge target is absent: "
            f"{coordinate[0]}:{coordinate[1]}",
        )
        components = tuple(QA.tolerant_decode_record(record))
        literals = tuple(
            literal.text for literal in parse_record_literals(record)
        )
        jump_targets = tuple(
            tuple(component["target"])
            for component in components
            if component["kind"] == "jump"
        )
        if jump_targets:
            jump_states: set[int | None] = set()
            for target in jump_targets:
                jump_states.update(
                    execute(
                        target,
                        incoming_selector_group,
                        trail + (coordinate,),
                    )
                )
            result = frozenset(jump_states)
            cache[cache_key] = result
            return result

        states: set[int | None] = {incoming_selector_group}
        for component in components:
            kind = str(component["kind"])
            if kind == "selector":
                states = {int(component["group"])}
                continue
            if kind == "call":
                called_states: set[int | None] = set()
                for state in states:
                    called_states.update(
                        execute(
                            tuple(component["target"]),
                            state,
                            trail + (coordinate,),
                        )
                    )
                states = called_states
                continue
            if kind != "literal_boundary":
                continue
            literal_id = int(component["slot"])
            text = visible(literals[literal_id])
            if not text:
                continue
            for state in states:
                if state is None:
                    continue
                for term in DYNAMIC_GENERAL_BOUNDARY_TERMS:
                    if not text.startswith(term):
                        continue
                    if term == DIRECT_UNIT_BOUNDARY_TERM and state not in {
                        1,
                        2,
                    }:
                        continue
                    owners.add(
                        (
                            coordinate[0],
                            coordinate[1],
                            literal_id,
                        )
                    )
            states = {None}
        result = frozenset(states)
        cache[cache_key] = result
        return result

    for coordinate in records:
        execute(coordinate, None)
    require(
        len(owners) == EXPECTED_DYNAMIC_GENERAL_BOUNDARY_OWNER_COUNT,
        "dynamic general boundary owner universe drifted: "
        f"{len(owners)}",
    )
    require(
        coordinate_digest(owners)
        == EXPECTED_DYNAMIC_GENERAL_BOUNDARY_OWNER_SHA256,
        "dynamic general boundary owner coordinate digest drifted",
    )
    return frozenset(owners)


def only_boundary_wrappers(value: str) -> bool:
    return not any(
        0xAC00 <= ord(character) <= 0xD7A3 or character.isalnum()
        for character in value
    )


def apply_dynamic_phrase_rewrites(
    text: str,
) -> tuple[str, tuple[str, ...]]:
    changed = text
    methods: list[str] = []
    for source, target in DYNAMIC_PHRASE_REWRITES:
        if source not in changed:
            continue
        changed = changed.replace(source, target)
        methods.append(f"phrase:{utf16le_sha256(source)[:16]}")
    return changed, tuple(methods)


def neutralize_semantic_boundary_artifacts(
    before: str,
    after: str,
    *,
    coordinate: tuple[int, int, int],
    call: Mapping[str, Any] | None,
) -> tuple[str, tuple[str, ...]]:
    """Remove mechanical register/additive/conjunction substitutions."""

    changed = after
    methods: list[str] = []

    if (
        call is not None
        and tuple(call["target"]) in QA.MIXED_REGISTER_CALL_TARGETS
        and QA.CALL_FIXED_HONORIFIC_RE.match(changed)
    ):
        explicit = SEMANTIC_MIXED_REGISTER_REWRITES.get(coordinate)
        require(
            explicit is not None,
            f"unreviewed mixed-register invariant: {coordinate} {changed!r}",
        )
        return explicit, ("coordinate_invariant_mixed_register_recast",)

    predecessor_marker = STRUCTURE.semantic_boundary_marker(before)
    candidate_marker = STRUCTURE.semantic_boundary_marker(changed)
    if predecessor_marker is None and candidate_marker is not None:
        wrapper_length = 0
        while (
            wrapper_length < len(changed)
            and changed[wrapper_length]
            in STRUCTURE.SEMANTIC_BOUNDARY_WRAPPERS
        ):
            wrapper_length += 1
        wrappers = changed[:wrapper_length]
        payload = changed[wrapper_length:]
        if candidate_marker == "conjunction_mit":
            replacement = SEMANTIC_COMITATIVE_REWRITES.get(coordinate)
            require(
                replacement is not None,
                f"unreviewed conjunction invariant: {coordinate} {changed!r}",
            )
            changed = replacement
            methods.append("coordinate_invariant_comitative_relation")
        else:
            require(
                payload.startswith("도"),
                f"semantic marker payload drifted: {coordinate} {payload!r}",
            )
            explicit = SEMANTIC_ADDITIVE_REWRITES.get(coordinate)
            if explicit is None:
                explicit = SEMANTIC_ADDITIVE_LATE_REWRITES.get(coordinate)
            require(
                explicit is not None,
                f"unreviewed additive invariant: "
                f"{coordinate} {changed!r}",
            )
            changed = explicit
            methods.append("coordinate_invariant_predicate_recast")
            return changed, tuple(methods)

    return changed, tuple(methods)


def resolve_dual_particles(
    text: str,
    *,
    coordinate: tuple[int, int, int],
    selector: Mapping[str, Any] | None,
    call: Mapping[str, Any] | None,
    renderer: Any,
    pristine_jp: str,
) -> tuple[str, tuple[str, ...]]:
    person_recast = SELECTOR_PERSON_REWRITES.get(coordinate)
    if person_recast is not None:
        return person_recast, ("coordinate_person_relation_recast",)
    location_recast = SELECTOR_LOCATION_REWRITES.get(coordinate)
    if location_recast is not None:
        return location_recast, ("coordinate_location_relation_recast",)
    explicit = COORDINATE_DUAL_REWRITES.get(coordinate)
    if explicit is not None:
        return explicit, ("coordinate_semantic_dual_rewrite",)
    changed, phrase_methods = apply_dynamic_phrase_rewrites(text)
    methods = list(phrase_methods)
    cursor = 0
    output: list[str] = []
    for match in DUAL_RE.finditer(changed):
        output.append(changed[cursor:match.start()])
        prefix = "".join(output)
        token = match.group(0)
        previous = last_lexical_character(prefix)
        marker_prefix = changed[:match.start()]
        contract = selector_contract(selector)
        if (
            (selector is not None or call is not None)
            and only_boundary_wrappers(marker_prefix)
        ):
            if contract in FIXED_BATCHIM_CONTRACTS:
                replacement = FIXED_BATCHIM_PARTICLE[particle_kind(token)]
                methods.append(
                    f"fixed_batchim:g{contract[0]}:p{contract[1]:02X}:"
                    f"{particle_kind(token)}"
                )
            elif selector is not None:
                group = int(selector["group"])
                replacement = carrier_with_particle(
                    group,
                    token,
                    coordinate=coordinate,
                    text=changed,
                    pristine_jp=pristine_jp,
                )
                methods.append(
                    f"dynamic_carrier:"
                    f"g{group}:"
                    f"{particle_kind(token)}"
                )
            else:
                require(call is not None, "dynamic call context disappeared")
                replacement, method = call_relation_rewrite(
                    call,
                    token,
                    changed[match.end():],
                    renderer,
                    coordinate,
                )
                methods.append(method)
                output.append(replacement)
                cursor = len(changed)
                break
        elif previous is not None:
            replacement = choose_particle(token, previous)
            methods.append(f"literal_jongseong:{particle_kind(token)}")
        elif re.search(r"Cs\d+\.CsName$", marker_prefix):
            replacement = FIXED_BATCHIM_PARTICLE[particle_kind(token)]
            methods.append(
                f"textual_castle_name_fixed_batchim:{particle_kind(token)}"
            )
        else:
            raise PkRemediationError(
                f"unresolved particle lacks lexical/dynamic context: "
                f"{coordinate} {changed!r}"
            )
        output.append(replacement)
        cursor = match.end()
    output.append(changed[cursor:])
    result = "".join(output)
    require(not DUAL_RE.search(result), "dual particle survived resolution")
    return result, tuple(methods)


def repair_group_zero_numeric(
    particle: str,
    rest: str,
    *,
    coordinate: tuple[int, int, int],
    text: str,
    pristine_jp: str,
) -> tuple[str, str]:
    if rest.startswith((" 상승", " 하락")):
        return f"만큼{rest}", "selector_numeric:delta"
    if rest.startswith(" 목표로"):
        return f"의 수치를{rest}", "selector_numeric:target_value"
    if rest.startswith(" 유지"):
        return f"의 수치를{rest}", "selector_numeric:maintained_value"
    if rest.startswith(" 모았"):
        return f"명을{rest}", "selector_numeric:person_count"
    if rest.startswith((" 접수", " 이송", " 받아")):
        return f"만큼을{rest}", "selector_numeric:quantity"
    if rest.startswith(" 상회"):
        return f"보다{rest}", "selector_numeric:comparison"
    if rest.startswith(" 주어졌"):
        return f"만큼이{rest}", "selector_numeric:awarded_amount"
    return (
        carrier_with_particle(
            0,
            particle,
            coordinate=coordinate,
            text=text,
            pristine_jp=pristine_jp,
        ) + rest,
        f"selector_carrier:g0:{particle_kind(particle)}",
    )


def repair_selector_fixed_particle(
    text: str,
    selector: Mapping[str, Any],
    *,
    coordinate: tuple[int, int, int],
    pristine_jp: str,
) -> tuple[str, str | None]:
    explicit = COORDINATE_SELECTOR_FIXED_REWRITES.get(coordinate)
    if explicit is not None:
        return explicit, "selector_wrapped_boundary_semantic_rewrite"
    match = LEADING_FIXED_RE.match(text)
    if match is None or QA.SELECTOR_PARTICLE_RE.search(text) is None:
        return text, None
    particle = match.group("particle")
    rest = match.group("rest")
    group = int(selector["group"])
    contract = selector_contract(selector)
    if contract in FIXED_BATCHIM_CONTRACTS:
        kind = particle_kind(particle)
        replacement = FIXED_BATCHIM_PARTICLE[kind]
        if kind == "directional" and len(replacement) > len(particle):
            replacement = "에"
        return replacement + rest, (
            f"selector_fixed_batchim:g{group}:p{contract[1]:02X}:{kind}"
        )
    kind = particle_kind(particle)
    if kind in {"subject", "topic"}:
        return "도" + rest, f"selector_compact_invariant:g{group}:{kind}"
    if kind == "comitative":
        return " 및" + rest, f"selector_compact_invariant:g{group}:{kind}"
    if kind == "directional":
        return "에" + rest, f"selector_compact_invariant:g{group}:{kind}"
    # In command, log, and status surfaces the selected proper name followed
    # by the action noun is the compact Korean UI form (``○○ 공격``,
    # ``○○ 등용``).  It avoids inventing a role noun after the selector.
    return rest, f"selector_compact_action_nominal:g{group}:object"


def repair_call_fixed_particle(
    text: str,
    call: Mapping[str, Any],
    renderer: Any,
    coordinate: tuple[int, int, int],
) -> tuple[str, str]:
    explicit = CALL_FIXED_BOUNDARY_REWRITES.get(coordinate)
    if explicit is not None:
        return explicit, "call_terminal_boundary_semantic_rewrite"
    match = QA.SELECTOR_PARTICLE_RE.search(text)
    require(match is not None, f"call particle vanished: {coordinate} {text!r}")
    replacement, method = call_relation_rewrite(
        call,
        match.group("particle"),
        text[match.end():],
        renderer,
        coordinate,
    )
    return replacement, method


def load_baseline() -> dict[str, Any]:
    require(BASELINE_PATH.is_file(), f"surface baseline is absent: {BASELINE_PATH}")
    value = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "surface baseline root is not an object")
    resource = value.get("resources", {}).get("pk_msggame")
    require(isinstance(resource, dict), "surface baseline has no PK resource")
    require(
        resource.get("sha256") == EXPECTED_SOURCE_SHA256,
        "surface baseline PK hash drifted",
    )
    return value


def load_priority_entries() -> dict[tuple[int, int, int], dict[str, Any]]:
    payload = json.loads(PRIORITY_OVERLAY.read_text(encoding="utf-8"))
    require(
        payload.get("schema") == PRIORITY_SCHEMA,
        "priority overlay schema drifted",
    )
    result: dict[tuple[int, int, int], dict[str, Any]] = {}
    for entry in payload.get("entries", []):
        if entry.get("resource") != "pk_msggame":
            continue
        coordinate = (
            int(entry["block_id"]),
            int(entry["record_id"]),
            int(entry["literal_id"]),
        )
        require(coordinate not in result, f"duplicate priority row: {coordinate}")
        result[coordinate] = dict(entry)
    require(
        set(result)
        == {
            (2, 148, 0),
            (8, 1032, 1),
            (8, 1032, 3),
            (15, 1545, 0),
            (15, 1545, 2),
        },
        f"priority PK coordinate drift: {sorted(result)}",
    )
    return result


def apply_priority_overlay(
    source_blob: bytes,
) -> tuple[bytes, dict[tuple[int, int, int], dict[str, Any]]]:
    entries = load_priority_entries()
    literals = literal_map(source_blob)
    replacements: dict[tuple[int, int, int], str] = {}
    for coordinate, entry in entries.items():
        require(coordinate in literals, f"priority coordinate absent: {coordinate}")
        observed = utf16le_sha256(literals[coordinate])
        require(
            observed == entry["source_text_utf16le_sha256"],
            f"priority source hash drift: {coordinate}",
        )
        replacements[coordinate] = str(entry["ko"])
    return rebuild_packed_with_literals(source_blob, replacements), entries


def audit_blob(blob: bytes, name: str) -> tuple[Any, dict[str, Any], str]:
    path = DEFAULT_OUTPUT_ROOT / f".{name}.audit-input.bin"
    atomic_write(path, blob)
    audited = QA.audit_resource("pk_msggame", path, include_text=True)
    report = QA.report((audited,))
    content = QA.canonical_json(report)
    return audited, report, content


def detect_terminal_blob(
    blob: bytes,
    name: str,
) -> tuple[Any, dict[str, Any], str]:
    path = DEFAULT_OUTPUT_ROOT / f".{name}.terminal-input.bin"
    atomic_write(path, blob)
    detected = TERMINAL.detect_resource(
        "pk_msggame",
        path,
        include_text=True,
    )
    report = TERMINAL.build_report((detected,), include_text=True)
    content = TERMINAL.canonical_json(report)
    return detected, report, content


def audit_candidate_guardrails(candidate_blob: bytes) -> dict[str, Any]:
    candidate_path = DEFAULT_OUTPUT_ROOT / ".candidate.guardrail-input.bin"
    atomic_write(candidate_path, candidate_blob)
    STRUCTURE.register_pk_call_retargets(
        SOURCE_PK,
        MORPHOLOGY_CONTROL_RETARGETS,
        MULTI_OCCURRENCE_CONTROL_RETARGET_COUNTS,
    )
    structure = STRUCTURE.audit_pair(
        "pk_msggame",
        SOURCE_PK,
        candidate_path,
    )
    relative_width = RELATIVE_WIDTH.audit_pair(
        "pk_msggame",
        SOURCE_PK,
        candidate_path,
    )
    require(
        structure["status"] == "PASS"
        and structure["issue_count"] == 0,
        f"independent structure guardrail failed: {structure['category_counts']}",
    )
    require(
        structure["allowed_mutation_count"]
        == control_retarget_mutation_count(),
        "independent structure guardrail did not bind all retargets",
    )
    require(
        relative_width["status"] == "PASS"
        and relative_width["issue_count"] == 0,
        "independent relative-width guardrail failed: "
        f"{relative_width['category_counts']}",
    )
    require(
        relative_width["approved_growth_exception_count"]
        == sum(
            len(exception.get("lines", {0: None}))
            for exception in APPROVED_LAYOUT_EXCEPTIONS.values()
        ),
        "independent width guardrail exception count drifted",
    )
    return {
        "structure": {
            "audit_sha256": sha256_bytes(STRUCTURE_AUDIT_PATH.read_bytes()),
            "status": structure["status"],
            "issue_count": structure["issue_count"],
            "literal_changed_count": structure["literal_changed_count"],
            "component_changed_record_count":
                structure["component_changed_record_count"],
            "allowed_mutation_count": structure["allowed_mutation_count"],
            "category_counts": structure["category_counts"],
        },
        "relative_width": {
            "audit_sha256":
                sha256_bytes(RELATIVE_WIDTH_AUDIT_PATH.read_bytes()),
            "status": relative_width["status"],
            "issue_count": relative_width["issue_count"],
            "changed_literal_count":
                relative_width["changed_literal_count"],
            "positive_line_delta_count":
                relative_width["positive_line_delta_count"],
            "maximum_positive_delta_px":
                relative_width["maximum_positive_delta_px"],
            "line_count_reduced_count":
                relative_width["line_count_reduced_count"],
            "approved_growth_exception_count":
                relative_width["approved_growth_exception_count"],
            "category_counts": relative_width["category_counts"],
        },
    }


def build_overlay(
    priority_blob: bytes,
    priority_report: Mapping[str, Any],
    priority_coordinates: frozenset[tuple[int, int, int]],
    pristine_jp_literals: Mapping[tuple[int, int, int], str],
) -> tuple[
    dict[tuple[int, int, int], str],
    list[dict[str, Any]],
    dict[str, Any],
]:
    records = records_from_blob(priority_blob)
    renderer = QA.TerminalRenderer(records)
    issues_by_coordinate: dict[tuple[int, int, int], set[str]] = defaultdict(set)
    for value in priority_report["issues"]:
        literal_id = value.get("literal_id")
        require(isinstance(literal_id, int), "PK issue has no literal coordinate")
        coordinate = (
            int(value["block_id"]),
            int(value["record_id"]),
            literal_id,
        )
        issues_by_coordinate[coordinate].add(str(value["category"]))
    for coordinate in EXPANDED_TERMINAL_COORDINATE_REWRITES:
        issues_by_coordinate[coordinate].add(
            "completed_prefix_terminal_suffix"
        )
    for coordinate in MANUAL_ASSEMBLY_REWRITES:
        issues_by_coordinate[coordinate].add("manual_runtime_assembly")
    for coordinate in INDEPENDENT_QA_REWRITES:
        issues_by_coordinate[coordinate].add("independent_language_qa")
    for coordinate in BOUNDARY_CLOSURE_REWRITES:
        issues_by_coordinate[coordinate].add("boundary_closure_review")
    for coordinate in FIXED_BOUNDARY_CLOSURE_REWRITES:
        issues_by_coordinate[coordinate].add("fixed_boundary_closure_review")
    for coordinate in SCREENSHOT_PRIORITY_REWRITES:
        issues_by_coordinate[coordinate].add("screenshot_priority_regression")
    for coordinate in CALL_ASSEMBLY_EXACT_REWRITES:
        issues_by_coordinate[coordinate].add("call_assembly_cartesian_review")
    for coordinate in CALL_ASSEMBLY_SUFFIX_TRIMS:
        issues_by_coordinate[coordinate].add("call_assembly_suffix_trim")
    for coordinate in CALL_ASSEMBLY_SUFFIX_REPLACEMENTS:
        issues_by_coordinate[coordinate].add("call_assembly_suffix_replacement")
    for coordinate in CALL_ASSEMBLY_PREFIX_TRIMS:
        issues_by_coordinate[coordinate].add("call_assembly_prefix_trim")
    for coordinate in CALL_ASSEMBLY_SUFFIX_APPENDS:
        issues_by_coordinate[coordinate].add("call_assembly_suffix_append")
    for coordinate in CALL_ASSEMBLY_PREFIX_PREPENDS:
        issues_by_coordinate[coordinate].add("call_assembly_prefix_prepend")
    for coordinate in INTERNAL_COMMA_SPACING_COORDINATES:
        issues_by_coordinate[coordinate].add("internal_comma_spacing")
    for coordinate in DYNAMIC_COMMA_SPACING_COORDINATES:
        issues_by_coordinate[coordinate].add("dynamic_comma_boundary_spacing")
    for coordinate in direct_person_title_boundary_coordinates(records):
        issues_by_coordinate[coordinate].add(
            "direct_person_title_boundary_spacing"
        )
    for coordinate in direct_unit_boundary_coordinates(records):
        issues_by_coordinate[coordinate].add(
            "direct_unit_boundary_spacing"
        )
    for coordinate in dynamic_general_boundary_owner_coordinates(records):
        issues_by_coordinate[coordinate].add(
            "dynamic_general_boundary_spacing"
        )
    exhaustive_remainder_coordinates = (
        frozenset(EXHAUSTIVE_REMAINDER_EXACT_REWRITES)
        | EXHAUSTIVE_REMAINDER_SPACING_COORDINATES
    )
    require(
        not (
            frozenset(EXHAUSTIVE_REMAINDER_EXACT_REWRITES)
            & EXHAUSTIVE_REMAINDER_SPACING_COORDINATES
        ),
        "exhaustive remainder exact/spacing ownership overlaps",
    )
    require(
        not (
            frozenset(EXHAUSTIVE_REMAINDER_EXACT_REWRITES)
            & frozenset(BOUNDARY_CLOSURE_REWRITES)
        ),
        "exhaustive remainder/boundary closure ownership overlaps",
    )
    require(
        len(exhaustive_remainder_coordinates)
        == EXPECTED_EXHAUSTIVE_REMAINDER_ACTUAL_COUNT,
        "exhaustive remainder coordinate count drifted",
    )
    require(
        coordinate_digest(exhaustive_remainder_coordinates)
        == EXPECTED_EXHAUSTIVE_REMAINDER_ACTUAL_COORDINATE_SHA256,
        "exhaustive remainder coordinate digest drifted",
    )
    for coordinate in EXHAUSTIVE_REMAINDER_EXACT_REWRITES:
        issues_by_coordinate[coordinate].add(
            "exhaustive_remainder_exact_rewrite"
        )
    for coordinate in EXHAUSTIVE_REMAINDER_SPACING_COORDINATES:
        issues_by_coordinate[coordinate].add(
            "exhaustive_remainder_spacing"
        )

    # 15:1545:0 is owned by the priority overlay.  Its only remaining issue is
    # eliminated by the explicit call retarget, not by a second literal row.
    protected_control_coordinate = (15, 1545, 0)
    require(
        issues_by_coordinate.get(protected_control_coordinate)
        == {"duplicated_terminal_boundary"},
        "15:1545 priority/control remediation contract drifted",
    )

    replacements: dict[tuple[int, int, int], str] = {}
    overlay_rows: list[dict[str, Any]] = []
    method_counts: Counter[str] = Counter()
    category_coordinate_counts: Counter[str] = Counter()
    for coordinate, categories in sorted(issues_by_coordinate.items()):
        if coordinate == protected_control_coordinate:
            continue
        require(
            coordinate not in priority_coordinates,
            f"PK owned overlay overlaps priority coordinate: {coordinate}",
        )
        record = records[coordinate[:2]]
        literal_id = coordinate[2]
        before = parse_record_literals(record)[literal_id].text
        pristine_jp = pristine_jp_literals[coordinate]
        after = before
        methods: list[str] = []
        selector, call = literal_context(record, literal_id)

        if "manual_runtime_assembly" in categories:
            after = MANUAL_ASSEMBLY_REWRITES[coordinate]
            methods.append("manual_exact_runtime_assembly_rewrite")

        if "completed_prefix_terminal_suffix" in categories:
            replacement = EXPANDED_TERMINAL_COORDINATE_REWRITES.get(coordinate)
            require(
                replacement is not None,
                f"unhandled expanded terminal prefix: {coordinate} {before!r}",
            )
            after = replacement
            methods.append("expanded_terminal_call_stem_reconstruction")

        if "duplicated_terminal_boundary" in categories:
            replacement = TERMINAL_COORDINATE_REWRITES.get(coordinate)
            require(
                replacement is not None,
                f"unhandled terminal prefix: {coordinate} {before!r}",
            )
            after = replacement
            methods.append("terminal_call_stem_reconstruction")

        if "unresolved_dual_particle" in categories:
            after, dual_methods = resolve_dual_particles(
                after,
                coordinate=coordinate,
                selector=selector,
                call=call,
                renderer=renderer,
                pristine_jp=pristine_jp,
            )
            methods.extend(dual_methods)

        if "selector_fixed_particle" in categories:
            require(
                selector is not None,
                f"fixed-particle issue has no selector: {coordinate}",
            )
            after, method = repair_selector_fixed_particle(
                after,
                selector,
                coordinate=coordinate,
                pristine_jp=pristine_jp,
            )
            if method is None:
                require(
                    QA.SELECTOR_PARTICLE_RE.search(after) is None,
                    f"unhandled selector particle: {coordinate} {after!r}",
                )
                methods.append("selector_boundary_resolved_by_semantic_rewrite")
            else:
                methods.append(method)

        if "call_fixed_particle" in categories:
            require(
                call is not None,
                f"call-fixed issue has no call: {coordinate}",
            )
            after, method = repair_call_fixed_particle(
                after,
                call,
                renderer,
                coordinate,
            )
            methods.append(method)

        if "literal_orthography_artifact" in categories:
            replacement = FOREIGN_MERCHANT_ORTHOGRAPHY_REWRITES.get(
                coordinate
            )
            require(
                replacement is not None,
                f"unreviewed orthography artifact: {coordinate} {before!r}",
            )
            after = replacement
            methods.append("foreign_merchant_register_exact_rewrite")

        if "independent_language_qa" in categories:
            after = INDEPENDENT_QA_REWRITES[coordinate]
            methods.append("independent_language_qa_exact_rewrite")

        if "boundary_closure_review" in categories:
            after = BOUNDARY_CLOSURE_REWRITES[coordinate]
            methods.append("boundary_closure_exact_rewrite")

        if "fixed_boundary_closure_review" in categories:
            after = FIXED_BOUNDARY_CLOSURE_REWRITES[coordinate]
            methods.append("fixed_boundary_closure_exact_rewrite")

        if "screenshot_priority_regression" in categories:
            after = SCREENSHOT_PRIORITY_REWRITES[coordinate]
            methods.append("screenshot_priority_exact_rewrite")

        if "call_assembly_cartesian_review" in categories:
            after = CALL_ASSEMBLY_EXACT_REWRITES[coordinate]
            methods.append("call_assembly_cartesian_exact_rewrite")

        if "call_assembly_suffix_trim" in categories:
            suffix = CALL_ASSEMBLY_SUFFIX_TRIMS[coordinate]
            require(
                after.endswith(suffix),
                f"call-assembly suffix trim drifted: "
                f"{coordinate} {after!r} {suffix!r}",
            )
            after = after[:-len(suffix)]
            methods.append("call_assembly_exact_suffix_trim")

        if "call_assembly_suffix_replacement" in categories:
            source_suffix, replacement_suffix = (
                CALL_ASSEMBLY_SUFFIX_REPLACEMENTS[coordinate]
            )
            require(
                after.endswith(source_suffix),
                f"call-assembly suffix replacement drifted: "
                f"{coordinate} {after!r} {source_suffix!r}",
            )
            after = after[:-len(source_suffix)] + replacement_suffix
            methods.append("call_assembly_exact_suffix_replacement")

        if "call_assembly_prefix_trim" in categories:
            prefix = CALL_ASSEMBLY_PREFIX_TRIMS[coordinate]
            require(
                after.startswith(prefix),
                f"call-assembly prefix trim drifted: "
                f"{coordinate} {after!r} {prefix!r}",
            )
            after = after[len(prefix):]
            methods.append("call_assembly_exact_prefix_trim")

        if "call_assembly_suffix_append" in categories:
            suffix = CALL_ASSEMBLY_SUFFIX_APPENDS[coordinate]
            require(
                not after.endswith(suffix),
                f"call-assembly suffix append already present: "
                f"{coordinate} {after!r}",
            )
            after += suffix
            methods.append("call_assembly_exact_suffix_append")

        if "call_assembly_prefix_prepend" in categories:
            prefix = CALL_ASSEMBLY_PREFIX_PREPENDS[coordinate]
            require(
                not after.startswith(prefix),
                f"call-assembly prefix prepend already present: "
                f"{coordinate} {after!r}",
            )
            after = prefix + after
            methods.append("call_assembly_exact_prefix_prepend")

        if "exhaustive_remainder_exact_rewrite" in categories:
            after = EXHAUSTIVE_REMAINDER_EXACT_REWRITES[coordinate]
            methods.append("exhaustive_remainder_exact_rewrite")

        exact_review_categories = {
            "independent_language_qa",
            "boundary_closure_review",
            "fixed_boundary_closure_review",
            "screenshot_priority_regression",
            "call_assembly_cartesian_review",
            "call_assembly_suffix_trim",
            "call_assembly_suffix_replacement",
            "call_assembly_prefix_trim",
            "call_assembly_suffix_append",
            "call_assembly_prefix_prepend",
            "exhaustive_remainder_exact_rewrite",
        }
        if not (categories & exact_review_categories):
            after, semantic_methods = neutralize_semantic_boundary_artifacts(
                before,
                after,
                coordinate=coordinate,
                call=call,
            )
            methods.extend(semantic_methods)

        if "internal_comma_spacing" in categories:
            spaced = re.sub(r"([,，])(?=[가-힣])", r"\1 ", after)
            require(
                spaced != after,
                f"internal comma spacing drifted: {coordinate} {after!r}",
            )
            after = spaced
            methods.append("internal_comma_spacing")

        if "dynamic_comma_boundary_spacing" in categories:
            require(
                after.endswith((",", "，")),
                f"dynamic comma boundary drifted: {coordinate} {after!r}",
            )
            after += " "
            methods.append("dynamic_comma_boundary_spacing")

        if "direct_person_title_boundary_spacing" in categories:
            require(
                after.startswith(PERSON_TITLE_BOUNDARY_TERMS),
                "direct person-title boundary payload drifted: "
                f"{coordinate} {after!r}",
            )
            after = " " + after
            methods.append("direct_person_title_boundary_space")

        if "direct_unit_boundary_spacing" in categories:
            require(
                after.startswith(DIRECT_UNIT_BOUNDARY_TERM),
                "direct unit boundary payload drifted: "
                f"{coordinate} {after!r}",
            )
            after = " " + after
            methods.append("direct_unit_boundary_space")

        if "dynamic_general_boundary_spacing" in categories:
            if after.startswith(DYNAMIC_GENERAL_BOUNDARY_TERMS):
                after = " " + after
                methods.append("dynamic_general_boundary_space")
            else:
                require(
                    not after.startswith(DYNAMIC_GENERAL_BOUNDARY_TERMS),
                    "dynamic general boundary payload drifted: "
                    f"{coordinate} {after!r}",
                )
                methods.append(
                    "dynamic_general_boundary_owned_by_prior_rewrite"
                )

        if "exhaustive_remainder_spacing" in categories:
            if not after[:1].isspace():
                after = " " + after
                methods.append("exhaustive_remainder_boundary_space")
            else:
                methods.append(
                    "exhaustive_remainder_spacing_owned_by_prior_rewrite"
                )

        if "selector_left_boundary_spacing" in categories:
            if not after:
                methods.append("selector_left_boundary_removed")
            elif not after[-1].isspace():
                after += " "
                methods.append("selector_left_ascii_space")

        require(after != before, f"issue coordinate did not change: {coordinate}")
        require("\0" not in after, f"NUL introduced: {coordinate}")
        replacements[coordinate] = after
        category_coordinate_counts.update(categories)
        method_counts.update(methods)
        overlay_rows.append(
            {
                "schema": OVERLAY_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": ":".join(str(value) for value in coordinate),
                "source_literal_utf16le_sha256": utf16le_sha256(before),
                "replacement_literal_utf16le_sha256": utf16le_sha256(after),
                "source_record_raw_sha256": sha256_bytes(record.data),
                "pristine_jp_literal_utf16le_sha256":
                    utf16le_sha256(pristine_jp),
                "categories": sorted(categories),
                "selector": (
                    {
                        "group": int(selector["group"]),
                        "slot": int(selector["slot"]),
                        "property": selector.get("property"),
                        "raw_hex": str(selector["raw_hex"]),
                    }
                    if selector is not None
                    else None
                ),
                "call_target": (
                    ":".join(str(value) for value in call["target"])
                    if call is not None
                    else None
                ),
                "methods": methods,
                "translation": after,
                "control_bytes_preserved": True,
                "steam_write_performed": False,
            }
        )

    summary = {
        "priority_replacement_count": len(priority_coordinates),
        "owned_issue_coordinate_count": len(replacements),
        "owned_replacement_count": len(replacements),
        "category_coordinate_counts": dict(
            sorted(category_coordinate_counts.items())
        ),
        "method_counts": dict(sorted(method_counts.items())),
    }
    return replacements, overlay_rows, summary


def call_bytes(target: int) -> bytes:
    return b"\x01\x43" + struct.pack("<I", target)


def control_retarget_operations(
) -> tuple[tuple[tuple[int, int], int, int, str], ...]:
    operations: list[tuple[tuple[int, int], int, int, str]] = []
    for coordinate, (old_target, new_target) in CONTROL_RETARGETS.items():
        reason = CONTROL_RETARGET_REASONS.get(coordinate)
        require(reason is not None, f"retarget has no semantic reason: {coordinate}")
        operations.append((coordinate, old_target, new_target, reason))
    for coordinate, retargets in ADDITIONAL_CONTROL_RETARGETS.items():
        for old_target, new_target in retargets:
            reason = ADDITIONAL_CONTROL_RETARGET_REASONS.get(
                (coordinate, old_target, new_target)
            )
            require(
                reason is not None,
                f"additional retarget has no semantic reason: "
                f"{coordinate} {old_target}->{new_target}",
            )
            operations.append((coordinate, old_target, new_target, reason))
    return tuple(
        sorted(
            operations,
            key=lambda value: (value[0], value[1], value[2]),
        )
    )


def control_retarget_mutation_count() -> int:
    return sum(
        MULTI_OCCURRENCE_CONTROL_RETARGET_COUNTS.get(
            (coordinate, old_target, new_target),
            1,
        )
        for coordinate, old_target, new_target, _reason
        in control_retarget_operations()
    )


def apply_control_retargets(
    literal_candidate: bytes,
) -> tuple[bytes, list[dict[str, Any]]]:
    records = records_from_blob(literal_candidate)
    renderer = QA.TerminalRenderer(records)
    record_replacements: dict[tuple[int, int], bytes] = {}
    evidence: list[dict[str, Any]] = []
    empty = records[(0, 1247)]
    require(
        empty.data.hex().upper() == EXPECTED_EMPTY_TERMINAL_DATA_HEX.upper(),
        "empty terminal 0:1247 drifted",
    )
    require(
        QA.TerminalRenderer(records).render((0, 1247)) == ("",),
        "0:1247 is no longer a single empty terminal",
    )
    patched_by_coordinate: dict[tuple[int, int], bytes] = {}
    for coordinate, old_target, new_target, reason in control_retarget_operations():
        record = records[coordinate]
        old_variants = renderer.render((0, old_target))
        new_variants = renderer.render((0, new_target))
        old = call_bytes(old_target)
        new = call_bytes(new_target)
        current = patched_by_coordinate.get(coordinate, record.data)
        expected_occurrence_count = (
            MULTI_OCCURRENCE_CONTROL_RETARGET_COUNTS.get(
                (coordinate, old_target, new_target),
                1,
            )
        )
        require(
            current.count(old) == expected_occurrence_count,
            f"call target {old_target} occurrence count drifted in "
            f"{coordinate}: expected {expected_occurrence_count}, "
            f"observed {current.count(old)}",
        )
        require(old != new, f"retarget is a no-op in {coordinate}")
        patched = current.replace(old, new, expected_occurrence_count)
        require(len(patched) == len(current), "call retarget changed size")
        patched_by_coordinate[coordinate] = patched
        record_replacements[coordinate] = patched
        evidence.append(
            {
                "coordinate": f"{coordinate[0]}:{coordinate[1]}",
                "old_target": f"0:{old_target}",
                "new_target": f"0:{new_target}",
                "before_record_sha256": sha256_bytes(current),
                "after_record_sha256": sha256_bytes(patched),
                "old_call_hex": old.hex().upper(),
                "new_call_hex": new.hex().upper(),
                "mutated_call_count": expected_occurrence_count,
                "semantic_reason": reason,
                "literal_context_utf16le_sha256": [
                    utf16le_sha256(literal.text)
                    for literal in parse_record_literals(record)
                ],
                "old_terminal_variant_count": len(old_variants),
                "old_terminal_variant_sha256": [
                    utf16le_sha256(value) for value in old_variants
                ],
                "new_terminal_variant_count": len(new_variants),
                "new_terminal_variant_sha256": [
                    utf16le_sha256(value) for value in new_variants
                ],
                "old_family_contains_incoherent_variant": True,
                "new_family_all_variants_context_coherent": True,
                "record_size_preserved": True,
                "only_call_operand_changed": True,
            }
        )
    candidate = rebuild_packed_msggame(literal_candidate, record_replacements)
    after_records = records_from_blob(candidate)
    for coordinate, _old_target, new_target, _reason in (
        control_retarget_operations()
    ):
        components = QA.tolerant_decode_record(after_records[coordinate])
        targets = [
            tuple(component["target"])
            for component in components
            if component["kind"] == "call"
        ]
        require(
            (0, new_target) in targets,
            f"retarget did not decode at {coordinate}",
        )
    return candidate, evidence


def verify_preservation(
    before_blob: bytes,
    after_blob: bytes,
    changed_literals: frozenset[tuple[int, int, int]],
) -> None:
    before = records_from_blob(before_blob)
    after = records_from_blob(after_blob)
    require(before.keys() == after.keys(), "PK record universe changed")
    changed_records = {coordinate[:2] for coordinate in changed_literals}
    control_records = {
        coordinate
        for coordinate, _old, _new, _reason in control_retarget_operations()
    }
    changed_records.update(control_records)
    for coordinate in before:
        if coordinate not in changed_records:
            require(
                before[coordinate].data == after[coordinate].data,
                f"unaffected PK record changed: {coordinate}",
            )
            continue
        if coordinate not in control_records:
            require(
                record_nonliteral_gaps(before[coordinate])
                == record_nonliteral_gaps(after[coordinate]),
                f"VM/control bytes changed: {coordinate}",
            )


def coordinate_digest(values: Iterable[tuple[int, int, int]]) -> str:
    payload = "\n".join(
        ":".join(str(part) for part in value)
        for value in sorted(values)
    ).encode("ascii")
    return sha256_bytes(payload)


def raw_g1n_line_widths(text: str) -> tuple[int, ...]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    result: list[int] = []
    for line in normalized.split("\n"):
        width = 0
        for character in line:
            codepoint = ord(character)
            if codepoint < 0x20 or 0x7F <= codepoint < 0xA0:
                continue
            width += (
                RAW_G1N_FULL_WIDTH_PX
                if unicodedata.east_asian_width(character) in {"W", "F", "A"}
                else RAW_G1N_HALF_WIDTH_PX
            )
        result.append(width)
    return tuple(result)


def verify_quality_gates(
    source_blob: bytes,
    candidate_blob: bytes,
    changed_literals: frozenset[tuple[int, int, int]],
    overlay_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    source = literal_map(source_blob)
    candidate = literal_map(candidate_blob)
    require(source.keys() == candidate.keys(), "literal universe changed")

    introduced: dict[str, list[tuple[int, int, int]]] = {}
    for word in ("대상", "항목", "인물", "장수"):
        introduced[word] = [
            coordinate
            for coordinate in changed_literals
            if candidate[coordinate].count(word) > source[coordinate].count(word)
            and coordinate
            not in APPROVED_SEMANTIC_CARRIER_INTRODUCTIONS.get(
                word,
                frozenset(),
            )
        ]
        require(
            not introduced[word],
            f"new generic carrier {word!r} introduced at {introduced[word][:3]}",
        )

    source_target_coordinates = frozenset(
        coordinate for coordinate, text in source.items() if "대상" in text
    )
    candidate_target_coordinates = frozenset(
        coordinate for coordinate, text in candidate.items() if "대상" in text
    )
    require(
        len(source_target_coordinates) == 106,
        "predecessor legal 대상 coordinate count drifted",
    )
    require(
        candidate_target_coordinates
        == source_target_coordinates | APPROVED_SEMANTIC_TARGET_INTRODUCTIONS,
        "legal 대상 UI coordinate set changed",
    )
    source_target_count = sum(
        source[coordinate].count("대상")
        for coordinate in source_target_coordinates
    )
    candidate_target_count = sum(
        candidate[coordinate].count("대상")
        for coordinate in candidate_target_coordinates
    )
    require(
        candidate_target_count
        == source_target_count + len(APPROVED_SEMANTIC_TARGET_INTRODUCTIONS),
        "legal 대상 UI occurrence count changed",
    )

    block_predecessor_max: dict[int, int] = defaultdict(int)
    for coordinate, text in source.items():
        block_predecessor_max[coordinate[0]] = max(
            block_predecessor_max[coordinate[0]],
            *raw_g1n_line_widths(text),
        )

    layout_by_coordinate: dict[tuple[int, int, int], dict[str, Any]] = {}
    line_count_increase_coordinates: list[tuple[int, int, int]] = []
    ordinary_over_24: list[tuple[int, int, int, int]] = []
    ordinary_plus_24_over_block: list[tuple[int, int, int, int]] = []
    ordinary_plus_48_or_more: list[tuple[int, int, int, int]] = []
    observed_exceptions: dict[tuple[int, int, int], dict[str, Any]] = {}
    maximum_ordinary_delta = 0
    for coordinate in sorted(changed_literals):
        before_widths = raw_g1n_line_widths(source[coordinate])
        after_widths = raw_g1n_line_widths(candidate[coordinate])
        if len(after_widths) > len(before_widths):
            line_count_increase_coordinates.append(coordinate)
        require(
            len(after_widths) == len(before_widths),
            f"display line count changed: {coordinate}",
        )
        exception = APPROVED_LAYOUT_EXCEPTIONS.get(coordinate)
        line_rows: list[dict[str, Any]] = []
        for line_index, (source_width, candidate_width) in enumerate(
            zip(before_widths, after_widths)
        ):
            delta = candidate_width - source_width
            line_exception = None
            if exception is not None:
                if "lines" in exception:
                    line_exception = exception["lines"].get(line_index)
                elif line_index == int(exception["line_index"]):
                    line_exception = exception
            approved = line_exception is not None
            if approved:
                require(
                    source_width == int(line_exception["source_width_px"])
                    and candidate_width
                    == int(line_exception["candidate_width_px"])
                    and delta == int(line_exception["delta_px"])
                    and utf16le_sha256(candidate[coordinate])
                    == exception["candidate_utf16le_sha256"],
                    f"approved layout exception drifted: {coordinate}",
                )
                observed_exceptions[coordinate] = {
                    **exception,
                    "coordinate":
                        ":".join(str(value) for value in coordinate),
                    "source_utf16le_sha256":
                        utf16le_sha256(source[coordinate]),
                }
            else:
                maximum_ordinary_delta = max(maximum_ordinary_delta, delta)
                if delta > RAW_G1N_HALF_WIDTH_PX:
                    ordinary_over_24.append((*coordinate, line_index))
                if delta >= RAW_G1N_FULL_WIDTH_PX:
                    ordinary_plus_48_or_more.append(
                        (*coordinate, line_index)
                    )
                if (
                    delta == RAW_G1N_HALF_WIDTH_PX
                    and candidate_width
                    > block_predecessor_max[coordinate[0]]
                ):
                    ordinary_plus_24_over_block.append(
                        (*coordinate, line_index)
                    )
            line_rows.append(
                {
                    "line_index": line_index,
                    "source_width_px": source_width,
                    "candidate_width_px": candidate_width,
                    "delta_px": delta,
                    "block_predecessor_max_px":
                        block_predecessor_max[coordinate[0]],
                    "approved_exact_exception": approved,
                }
            )
        layout_by_coordinate[coordinate] = {
            "source_raw_g1n_line_widths_px": list(before_widths),
            "candidate_raw_g1n_line_widths_px": list(after_widths),
            "source_line_count": len(before_widths),
            "candidate_line_count": len(after_widths),
            "line_count_preserved": len(before_widths) == len(after_widths),
            "lines": line_rows,
        }
    require(
        not ordinary_over_24,
        f"ordinary raw G1N +24px violations remain: {ordinary_over_24[:3]}",
    )
    require(
        not ordinary_plus_24_over_block,
        "ordinary +24px line exceeds its block predecessor maximum: "
        f"{ordinary_plus_24_over_block[:3]}",
    )
    require(
        not ordinary_plus_48_or_more,
        "ordinary raw G1N +48px lines remain: "
        f"{ordinary_plus_48_or_more[:3]}",
    )
    require(
        frozenset(observed_exceptions) == frozenset(APPROVED_LAYOUT_EXCEPTIONS),
        "approved layout exception universe drifted",
    )

    for row in overlay_rows:
        coordinate = tuple(int(value) for value in row["coordinate"].split(":"))
        row["layout"] = layout_by_coordinate[coordinate]
        row["source_translation"] = source[coordinate]

    selector_rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in overlay_rows:
        selector = row.get("selector")
        if isinstance(selector, dict) and int(selector["group"]) in {9, 10, 11}:
            selector_rows[int(selector["group"])].append(row)
    selector_contracts = {
        "g9": {
            "static_label": "generic_named_object_slot",
            "coordinate_context": "pristine_JP_国衆_persuasion_or_incorporation",
            "semantic_carrier": "측 (selector emits the 国衆 name)",
            "coordinate_count": len(selector_rows[9]),
            "coordinate_sha256": coordinate_digest(
                tuple(
                    tuple(int(value) for value in row["coordinate"].split(":"))
                    for row in selector_rows[9]
                )
            ),
        },
        "g10": {
            "static_label": "tribe_slot",
            "coordinate_context": "pristine_JP_郡_conquest_flood_control_road_or_tenure",
            "semantic_carrier": "군",
            "coordinate_count": len(selector_rows[10]),
            "coordinate_sha256": coordinate_digest(
                tuple(
                    tuple(int(value) for value in row["coordinate"].split(":"))
                    for row in selector_rows[10]
                )
            ),
        },
        "g11": {
            "static_label": "runtime_object_slot",
            "coordinate_context": "PK_block9_battle_unit",
            "semantic_carrier": "부대",
            "coordinate_count": len(selector_rows[11]),
            "coordinate_sha256": coordinate_digest(
                tuple(
                    tuple(int(value) for value in row["coordinate"].split(":"))
                    for row in selector_rows[11]
                )
            ),
        },
    }
    return {
        "new_generic_carrier_count": 0,
        "new_generic_carrier_terms": ["대상", "항목", "인물", "장수"],
        "legal_target_ui": {
            "predecessor_coordinate_count": len(source_target_coordinates),
            "candidate_coordinate_count": len(candidate_target_coordinates),
            "coordinate_set_preserved": True,
            "occurrence_count": source_target_count,
            "wording_token_preserved": True,
        },
        "raw_g1n_relative_layout": {
            "method": "48px_fullwidth_24px_halfwidth_per_literal_line",
            "msgev_912px_absolute_gate_applied": False,
            "changed_coordinate_count": len(changed_literals),
            "line_count_increase_count":
                len(line_count_increase_coordinates),
            "ordinary_over_24px_count": len(ordinary_over_24),
            "ordinary_plus_24px_over_block_max_count":
                len(ordinary_plus_24_over_block),
            "ordinary_plus_48px_or_more_count":
                len(ordinary_plus_48_or_more),
            "maximum_ordinary_delta_px": maximum_ordinary_delta,
            "approved_exact_exception_count":
                len(observed_exceptions),
            "approved_exact_exceptions": [
                observed_exceptions[coordinate]
                for coordinate in sorted(observed_exceptions)
            ],
        },
        "selector_contract_context": selector_contracts,
    }


def verify_regressions(
    source_blob: bytes,
    candidate_blob: bytes,
) -> dict[str, Any]:
    source_records = records_from_blob(source_blob)
    records = records_from_blob(candidate_blob)
    renderer = QA.TerminalRenderer(records)
    illness = parse_record_literals(records[(2, 148)])[0].text
    require(
        illness == "에게 병환이 생겼습니다",
        "PK 2:148 illness regression changed",
    )
    illness_assembly_literals = tuple(
        literal.text for literal in parse_record_literals(records[(8, 1032)])
    )
    expected_illness_assembly_literals = (
        "하아… 설마, ",
        "에게도 병환이 들다니…\n…당분간 제 힘을 발휘하지 ",
        "\n",
        "폐를 끼쳐 ",
        "…",
    )
    require(
        illness_assembly_literals == expected_illness_assembly_literals,
        "PK 8:1032 reviewed literals changed",
    )
    illness_components = QA.tolerant_decode_record(records[(8, 1032)])
    illness_calls = [
        tuple(component["target"])
        for component in illness_components
        if component["kind"] == "call"
    ]
    require(
        illness_calls == [(0, 1), (0, 748), (0, 1174), (0, 460)],
        "PK 8:1032 call topology drifted",
    )
    pronouns = renderer.render((0, 1))
    negatives = renderer.render((0, 748))
    empty_terminals = renderer.render((0, 1174))
    apologies = renderer.render((0, 460))
    require(empty_terminals == ("",), "PK 0:1174 is no longer empty")
    expected_illness_assemblies = tuple(
        (
            illness_assembly_literals[0]
            + pronoun
            + illness_assembly_literals[1]
            + negative
            + illness_assembly_literals[2]
            + empty_terminal
            + illness_assembly_literals[3]
            + apology
            + illness_assembly_literals[4]
        )
        for pronoun, negative, empty_terminal, apology in product(
            pronouns,
            negatives,
            empty_terminals,
            apologies,
        )
    )
    illness_assemblies = renderer.render((8, 1032))
    require(
        len(illness_assemblies) == 45,
        "PK 8:1032 did not enumerate all 45 runtime assemblies",
    )
    require(
        illness_assemblies == expected_illness_assemblies,
        "PK 8:1032 runtime assembly differs from its four call families",
    )
    require(
        all(
            "에게도 병환이 들다니" in value
            and "설마, " in value
            and "발휘하지 않" in value
            and "폐를 끼쳐 " in value
            and "이(가)" not in value
            and "않습니다습니다" not in value
            for value in illness_assemblies
        ),
        "PK 8:1032 assembled grammar regression survived",
    )

    lure_literals = tuple(
        literal.text for literal in parse_record_literals(records[(15, 1545)])
    )
    require(
        lure_literals
        == (
            "을 공략할 계책이 있사옵니다",
            "\n",
            "으로 적병을 유인하면\n허술해진 성을 공략할 수 있을 것",
        ),
        "PK 15:1545 reviewed literals changed",
    )
    components = QA.tolerant_decode_record(records[(15, 1545)])
    calls = [
        tuple(component["target"])
        for component in components
        if component["kind"] == "call"
    ]
    require(calls == [(0, 1247), (0, 610)], "PK 15:1545 call topology drifted")
    assembled = renderer.render((15, 1545))
    require(len(assembled) == 3, "PK 15:1545 terminal variants drifted")
    require(
        all(
            "을(를)" not in value
            and "\n로 적병" not in value
            and "있사옵니다입니다" not in value
            and "있사옵니다있소" not in value
            and "있사옵니다있다" not in value
            for value in assembled
        ),
        "PK 15:1545 assembled regression survived",
    )
    for coordinate in ((6, 3957), (6, 3958)):
        require(
            tuple(
                literal.text
                for literal in parse_record_literals(records[coordinate])
            )
            == tuple(
                literal.text
                for literal in parse_record_literals(source_records[coordinate])
            ),
            f"PK {coordinate[0]}:{coordinate[1]} preserved dialogue drifted",
        )
    posture_literals = tuple(
        literal.text for literal in parse_record_literals(records[(15, 1133)])
    )
    require(
        posture_literals[2] == "」 쪽",
        "PK 15:1133 destination diplomacy posture relation drifted",
    )
    clan_request_evidence: dict[str, Any] = {}
    expected_clan_request_literals = {
        (6, 3768): (
            "훗날 ",
            "에 원군 등\n군사적 ",
            "협력을 약조하겠소?\n",
            "",
            "",
        ),
        (6, 4917): (
            "훗날 ",
            "에 중재 등\n군사 ",
            "협력을 약조하겠소?\n",
            "",
            "",
        ),
    }
    for coordinate, expected_literals in expected_clan_request_literals.items():
        actual_literals = tuple(
            literal.text for literal in parse_record_literals(records[coordinate])
        )
        require(
            actual_literals == expected_literals,
            f"PK {coordinate[0]}:{coordinate[1]} clan request drifted",
        )
        request_components = QA.tolerant_decode_record(records[coordinate])
        request_calls = [
            tuple(component["target"])
            for component in request_components
            if component["kind"] == "call"
        ]
        require(
            request_calls == [(0, 1174), (0, 1168), (0, 1247)],
            f"PK {coordinate[0]}:{coordinate[1]} request calls drifted",
        )
        request_assemblies = renderer.render(coordinate)
        require(
            len(request_assemblies) == 1
            and "협력" in request_assemblies[0]
            and "약조하겠소?\n" in request_assemblies[0]
            and "약속하지 않" not in request_assemblies[0],
            f"PK {coordinate[0]}:{coordinate[1]} request reversal survived",
        )
        key = f"{coordinate[0]}:{coordinate[1]}"
        clan_request_evidence[key] = {
            "literal_sha256": [
                utf16le_sha256(value) for value in actual_literals
            ],
            "call_targets": ["0:1174", "0:1168", "0:1247"],
            "assembled_variant_count": 1,
            "assembled_sha256": utf16le_sha256(request_assemblies[0]),
            "negative_terminal_removed": True,
            "question_mark_attached_before_trailing_line_break": True,
        }
    return {
        "2:148:0": {
            "literal_utf16le_sha256": utf16le_sha256(illness),
            "batchim_independent": True,
        },
        "8:1032": {
            "literal_sha256": [
                utf16le_sha256(value)
                for value in illness_assembly_literals
            ],
            "call_targets": ["0:1", "0:748", "0:1174", "0:460"],
            "call_variant_counts": {
                "0:1": len(pronouns),
                "0:748": len(negatives),
                "0:1174": len(empty_terminals),
                "0:460": len(apologies),
            },
            "cartesian_product_verified": True,
            "assembled_variant_count": len(illness_assemblies),
            "assembled_variant_set_sha256": sha256_bytes(
                "\0".join(illness_assemblies).encode("utf-16le")
            ),
            "assembled_sha256": [
                utf16le_sha256(value) for value in illness_assemblies
            ],
        },
        "15:1545": {
            "literal_sha256": [
                utf16le_sha256(value) for value in lure_literals
            ],
            "call_targets": ["0:1247", "0:610"],
            "assembled_variant_count": len(assembled),
            "assembled_sha256": [
                utf16le_sha256(value) for value in assembled
            ],
            "empty_terminal_verified": True,
        },
        "6:3957-3958": {
            "literal_sha256": {
                f"{block_id}:{record_id}:{literal.literal_id}":
                    utf16le_sha256(literal.text)
                for block_id, record_id in ((6, 3957), (6, 3958))
                for literal in parse_record_literals(
                    records[(block_id, record_id)]
                )
            },
            "preserved_from_input": True,
        },
        "15:1133": {
            "literal_sha256": [
                utf16le_sha256(value) for value in posture_literals
            ],
            "final_relation": "quoted_dynamic_diplomacy_posture_direction",
            "reviewed_suffix": "」 쪽",
        },
        "6:3768-4917": clan_request_evidence,
    }


def build() -> tuple[bytes, str, str, str, dict[str, Any]]:
    load_baseline()
    pinned_coordinate_maps = (
        (
            "early additive",
            SEMANTIC_ADDITIVE_REWRITES,
            EXPECTED_SEMANTIC_ADDITIVE_EARLY_REWRITE_COUNT,
            EXPECTED_SEMANTIC_ADDITIVE_EARLY_COORDINATE_SHA256,
        ),
        (
            "late additive",
            SEMANTIC_ADDITIVE_LATE_REWRITES,
            EXPECTED_SEMANTIC_ADDITIVE_LATE_REWRITE_COUNT,
            EXPECTED_SEMANTIC_ADDITIVE_LATE_COORDINATE_SHA256,
        ),
        (
            "mixed register",
            SEMANTIC_MIXED_REGISTER_REWRITES,
            EXPECTED_MIXED_REGISTER_REWRITE_COUNT,
            EXPECTED_MIXED_REGISTER_COORDINATE_SHA256,
        ),
        (
            "foreign merchant orthography",
            FOREIGN_MERCHANT_ORTHOGRAPHY_REWRITES,
            EXPECTED_FOREIGN_MERCHANT_ORTHOGRAPHY_REWRITE_COUNT,
            EXPECTED_FOREIGN_MERCHANT_ORTHOGRAPHY_COORDINATE_SHA256,
        ),
        (
            "selector person",
            SELECTOR_PERSON_REWRITES,
            EXPECTED_SELECTOR_PERSON_REWRITE_COUNT,
            EXPECTED_SELECTOR_PERSON_COORDINATE_SHA256,
        ),
        (
            "selector location",
            SELECTOR_LOCATION_REWRITES,
            EXPECTED_SELECTOR_LOCATION_REWRITE_COUNT,
            EXPECTED_SELECTOR_LOCATION_COORDINATE_SHA256,
        ),
        (
            "independent language QA literal",
            INDEPENDENT_QA_REWRITES,
            EXPECTED_INDEPENDENT_QA_LITERAL_REWRITE_COUNT,
            EXPECTED_INDEPENDENT_QA_LITERAL_COORDINATE_SHA256,
        ),
    )
    for label, coordinate_map, expected_count, expected_digest in (
        pinned_coordinate_maps
    ):
        require(
            len(coordinate_map) == expected_count
            and coordinate_digest(coordinate_map) == expected_digest,
            f"{label} coordinate universe drifted",
        )
    require(
        len(SEMANTIC_ADDITIVE_REWRITES)
        + len(SEMANTIC_ADDITIVE_LATE_REWRITES)
        == EXPECTED_SEMANTIC_ADDITIVE_TOTAL_REWRITE_COUNT,
        "complete additive coordinate universe drifted",
    )
    independent_sample_coordinates = frozenset(
        coordinate[:2] for coordinate in INDEPENDENT_QA_REWRITES
    )
    require(
        len(independent_sample_coordinates) == EXPECTED_INDEPENDENT_QA_SAMPLE_COUNT
        and coordinate_digest(independent_sample_coordinates)
        == EXPECTED_INDEPENDENT_QA_SAMPLE_COORDINATE_SHA256,
        "independent language QA sample universe drifted",
    )
    require(
        len(INDEPENDENT_QA_PERSON_DEFECT_COORDINATES)
        == EXPECTED_INDEPENDENT_QA_PERSON_DEFECT_COUNT,
        "independent person-defect universe drifted",
    )
    require(
        all(
            coordinate in SELECTOR_PERSON_REWRITES
            or coordinate in INDEPENDENT_QA_REWRITES
            for coordinate in INDEPENDENT_QA_PERSON_DEFECT_COORDINATES
        ),
        "independent person defect lacks an exact correction",
    )
    independent_defect_records = (
        independent_sample_coordinates
        | frozenset(
            coordinate[:2]
            for coordinate in INDEPENDENT_QA_PERSON_DEFECT_COORDINATES
        )
    )
    require(
        len(independent_defect_records)
        == EXPECTED_INDEPENDENT_QA_DEFECT_RECORD_COUNT
        and coordinate_digest(independent_defect_records)
        == EXPECTED_INDEPENDENT_QA_DEFECT_RECORD_SHA256,
        "independent 33-defect record universe drifted",
    )
    require(
        sha256_bytes(TERMINAL_DETECTOR_PATH.read_bytes())
        == EXPECTED_TERMINAL_DETECTOR_SHA256,
        "terminal detector implementation drifted",
    )
    require(SOURCE_PK.is_file(), f"PK candidate is absent: {SOURCE_PK}")
    source_blob = SOURCE_PK.read_bytes()
    source_sha256 = sha256_bytes(source_blob)
    require(
        source_sha256 == EXPECTED_SOURCE_SHA256,
        f"PK candidate hash drifted: {source_sha256}",
    )
    require(PRISTINE_JP_PK.is_file(), "pristine PK JP msggame is absent")
    pristine_jp_blob = PRISTINE_JP_PK.read_bytes()
    require(
        sha256_bytes(pristine_jp_blob) == EXPECTED_PRISTINE_JP_SHA256,
        "pristine PK JP msggame hash drifted",
    )
    pristine_jp_literals = literal_map(pristine_jp_blob)

    _source_audit, source_report, _source_content = audit_blob(
        source_blob,
        "source",
    )
    source_counts = dict(source_report["category_counts"])
    require(
        {
            key: source_counts.get(key, 0)
            for key in EXPECTED_SOURCE_SURFACE_COUNTS
        }
        == EXPECTED_SOURCE_SURFACE_COUNTS,
        f"source legacy surface counts drifted: {source_counts}",
    )
    require(
        sum(EXPECTED_SOURCE_SURFACE_COUNTS.values())
        == EXPECTED_SOURCE_SURFACE_ISSUE_COUNT,
        "source surface total constant is inconsistent",
    )
    require(
        source_counts.get("call_fixed_particle")
        == EXPECTED_SOURCE_CALL_FIXED_PARTICLE_COUNT,
        f"source call-fixed count drifted: {source_counts}",
    )
    require(
        source_counts.get("call_semantic_carrier_artifact", 0)
        == EXPECTED_SOURCE_SURFACE_COUNTS[
            "call_semantic_carrier_artifact"
        ],
        "pinned source mixed-register carrier count drifted",
    )
    require(
        source_counts.get("selector_semantic_carrier_artifact", 0) == 0,
        "pinned source unexpectedly contains an automatic selector carrier",
    )
    source_spacing_coordinates = frozenset(
        (
            int(value["block_id"]),
            int(value["record_id"]),
            int(value["literal_id"]),
        )
        for value in source_report["issues"]
        if value["category"] == "selector_left_boundary_spacing"
    )
    require(
        len(source_spacing_coordinates)
        == EXPECTED_SOURCE_SURFACE_COUNTS[
            "selector_left_boundary_spacing"
        ]
        and coordinate_digest(source_spacing_coordinates)
        == EXPECTED_SOURCE_SELECTOR_LEFT_SPACING_COORDINATE_SHA256,
        "pinned source selector-left coordinate universe drifted",
    )
    _source_terminal, source_terminal_report, _source_terminal_content = (
        detect_terminal_blob(source_blob, "source")
    )
    require(
        source_terminal_report["issue_count"]
        == EXPECTED_SOURCE_TERMINAL_ISSUE_COUNT,
        "source terminal detector count drifted",
    )

    priority_blob, priority_entries = apply_priority_overlay(source_blob)
    _priority_audit, priority_report, _priority_content = audit_blob(
        priority_blob,
        "priority",
    )
    replacements, overlay_rows, summary = build_overlay(
        priority_blob,
        priority_report,
        frozenset(priority_entries),
        pristine_jp_literals,
    )
    literal_candidate = rebuild_packed_with_literals(priority_blob, replacements)
    candidate_blob, control_evidence = apply_control_retargets(literal_candidate)

    changed_literals = frozenset(set(priority_entries) | set(replacements))
    verify_preservation(source_blob, candidate_blob, changed_literals)
    final_literals = literal_map(candidate_blob)
    for coordinate, row in priority_entries.items():
        require(
            final_literals[coordinate] == row["ko"],
            f"priority literal changed: {coordinate}",
        )
    for coordinate, replacement in replacements.items():
        require(
            final_literals[coordinate] == replacement,
            f"owned literal did not round-trip: {coordinate}",
        )

    candidate_audit, candidate_report, private_audit_content = audit_blob(
        candidate_blob,
        "candidate",
    )
    terminal_audit, terminal_report, private_terminal_content = (
        detect_terminal_blob(candidate_blob, "candidate")
    )
    require(
        candidate_report["category_counts"].get(
            "call_semantic_carrier_artifact",
            0,
        )
        == 0,
        "candidate contains a rejected automatic call carrier",
    )
    require(
        candidate_report["category_counts"].get(
            "selector_semantic_carrier_artifact",
            0,
        )
        == 0,
        "candidate contains a rejected automatic selector carrier",
    )
    regression_evidence = verify_regressions(source_blob, candidate_blob)
    quality_evidence = verify_quality_gates(
        source_blob,
        candidate_blob,
        changed_literals,
        overlay_rows,
    )
    guardrail_evidence = audit_candidate_guardrails(candidate_blob)
    overlay_content = canonical_jsonl(overlay_rows)
    source_records_for_review = records_from_blob(source_blob)
    candidate_records_for_review = records_from_blob(candidate_blob)
    independent_exact_records = frozenset(
        coordinate[:2] for coordinate in INDEPENDENT_QA_REWRITES
    )
    independent_person_records = frozenset(
        coordinate[:2]
        for coordinate in INDEPENDENT_QA_PERSON_DEFECT_COORDINATES
    )
    independent_defect_records = (
        independent_exact_records | independent_person_records
    )
    require(
        all(
            source_records_for_review[coordinate].data
            != candidate_records_for_review[coordinate].data
            for coordinate in independent_defect_records
        ),
        "an independently reported defect record remained byte-identical",
    )
    independent_review_evidence = {
        "status": "PASS",
        "source_private_review_schema":
            "nobu16.kr.pk-stratified-language-qa-b.private.v1",
        "reported_defect_record_count":
            EXPECTED_INDEPENDENT_QA_DEFECT_RECORD_COUNT,
        "reported_defect_record_coordinate_sha256":
            EXPECTED_INDEPENDENT_QA_DEFECT_RECORD_SHA256,
        "exact_language_review_record_count": len(independent_exact_records),
        "selector_person_relation_record_count":
            len(independent_person_records),
        "overlap_record_count":
            len(independent_exact_records & independent_person_records),
        "all_reported_records_changed": True,
        "candidate_record_sha256": {
            f"{coordinate[0]}:{coordinate[1]}":
                sha256_bytes(candidate_records_for_review[coordinate].data)
            for coordinate in sorted(independent_defect_records)
        },
        "correction_strategy": {
            f"{coordinate[0]}:{coordinate[1]}": (
                "exact_language_review_override"
                if coordinate in independent_exact_records
                else "coordinate_person_relation_recast"
            )
            for coordinate in sorted(independent_defect_records)
        },
        "literal_bodies_omitted": True,
    }
    report = {
        "schema": SCHEMA,
        "status": (
            "PASS"
            if (
                candidate_report["issue_count"] == 0
                and terminal_report["issue_count"] == 0
            )
            else "INCOMPLETE"
        ),
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "input": {
            "sha256": source_sha256,
            "baseline_file_sha256": sha256_bytes(BASELINE_PATH.read_bytes()),
            "pristine_jp_sha256": EXPECTED_PRISTINE_JP_SHA256,
            "legacy_surface_issue_count":
                EXPECTED_SOURCE_LEGACY_SURFACE_ISSUE_COUNT,
            "surface_issue_count": EXPECTED_SOURCE_SURFACE_ISSUE_COUNT,
            "surface_category_counts": EXPECTED_SOURCE_SURFACE_COUNTS,
            "call_fixed_particle_issue_count":
                EXPECTED_SOURCE_CALL_FIXED_PARTICLE_COUNT,
            "all_call_site_terminal_issue_count":
                EXPECTED_SOURCE_TERMINAL_ISSUE_COUNT,
            "terminal_detector_sha256":
                EXPECTED_TERMINAL_DETECTOR_SHA256,
            "surface_audit_sha256": sha256_bytes(QA_PATH.read_bytes()),
            "fresh_priority_audit_issue_count":
                priority_report["issue_count"],
            "fresh_priority_audit_category_counts":
                priority_report["category_counts"],
        },
        "overlay": {
            **summary,
            "total_literal_replacement_count": len(changed_literals),
            "coordinate_sha256": coordinate_digest(changed_literals),
            "private_overlay_sha256": sha256_bytes(
                overlay_content.encode("utf-8")
            ),
        },
        "control_retargets": {
            "count": len(control_evidence),
            "empty_terminal": {
                "coordinate": "0:1247",
                "record_data_hex": EXPECTED_EMPTY_TERMINAL_DATA_HEX.upper(),
                "rendered_variants": [""],
            },
            "entries": control_evidence,
        },
        "candidate": {
            "sha256": sha256_bytes(candidate_blob),
            "size": len(candidate_blob),
            "surface_issue_count": candidate_report["issue_count"],
            "surface_category_counts":
                candidate_report["category_counts"],
            "record_count": candidate_audit.record_count,
            "decoded_record_count": candidate_audit.decoded_record_count,
            "literal_count": candidate_audit.literal_count,
            "private_audit_sha256": sha256_bytes(
                private_audit_content.encode("utf-8")
            ),
        },
        "terminal_boundary_detector": {
            "schema": terminal_report["schema"],
            "status": terminal_report["status"],
            "issue_count": terminal_report["issue_count"],
            "call_site_count": terminal_audit.call_site_count,
            "terminal_suffix_variant_count":
                terminal_audit.terminal_suffix_variant_count,
            "private_audit_sha256": sha256_bytes(
                private_terminal_content.encode("utf-8")
            ),
        },
        "regressions": regression_evidence,
        "independent_language_review": independent_review_evidence,
        "quality_gates": quality_evidence,
        "independent_candidate_guardrails": guardrail_evidence,
        "call_carrier_rejection": {
            "rejected_predecessor_automatic_call_carrier_count": 416,
            "rejected_predecessor_detected_artifact_count": 176,
            "pinned_source_detected_artifact_count":
                EXPECTED_SOURCE_SURFACE_COUNTS[
                    "call_semantic_carrier_artifact"
                ],
            "candidate_detected_artifact_count": 0,
            "candidate_automatic_call_carrier_count": 0,
            "replacement_strategy":
                "coordinate_context_relation_or_reflexive_invariant",
        },
        "selector_carrier_rejection": {
            "rejected_predecessor_detected_artifact_count": 349,
            "pinned_source_detected_artifact_count": 0,
            "candidate_detected_artifact_count": 0,
            "automatic_person_role_carrier_terms": [
                "장수",
                "인물",
                "대상",
                "분",
            ],
            "candidate_new_automatic_person_role_carrier_count": 0,
            "replacement_strategy":
                "pristine_context_relation_or_compact_invariant_structure",
        },
        "ghidra_contract": {
            "literal_opcode_0x02":
                "0x140A013B0 copies UTF-16 code units verbatim",
            "selector_opcode_0x1B":
                "0x140A013B0 dispatches the selector property handler",
            "selector_property_0x32":
                "0x1409FDA70 invokes display-name accessor 0x1405F3C20",
            "automatic_korean_particle_selection_observed": False,
        },
        "invariants": {
            "pk_only": True,
            "base_resource_untouched": True,
            "legal_predecessor_target_ui_preserved": True,
            "priority_overlay_coordinates_not_duplicated": True,
            "dynamic_selector_bytes_preserved": True,
            "calls_and_jumps_preserved_except_listed_retargets": True,
            "listed_retargets_change_only_call_operands": True,
            "all_other_control_bytes_preserved": True,
            "new_generic_carrier_count": 0,
            "call_semantic_carrier_artifact_count": 0,
            "selector_semantic_carrier_artifact_count": 0,
            "raw_g1n_relative_layout_over_budget_count": 0,
            "steam_write_performed": False,
        },
    }
    return (
        candidate_blob,
        overlay_content,
        private_audit_content,
        private_terminal_content,
        report,
    )


def write_outputs(
    candidate_blob: bytes,
    overlay_content: str,
    private_audit_content: str,
    private_terminal_content: str,
    report: Mapping[str, Any],
    *,
    candidate_path: Path,
    overlay_path: Path,
    private_audit_path: Path,
    private_terminal_path: Path,
    report_path: Path,
) -> None:
    atomic_write(candidate_path, candidate_blob)
    atomic_write(overlay_path, overlay_content)
    atomic_write(private_audit_path, private_audit_content)
    atomic_write(private_terminal_path, private_terminal_content)
    atomic_write(report_path, canonical_json(report))
    require(
        candidate_path.read_bytes() == candidate_blob,
        f"candidate write drift: {candidate_path}",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-output", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--overlay-output", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument(
        "--private-audit-output",
        type=Path,
        default=DEFAULT_PRIVATE_AUDIT,
    )
    parser.add_argument(
        "--private-terminal-output",
        type=Path,
        default=DEFAULT_PRIVATE_TERMINAL_AUDIT,
    )
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args(argv)

    (
        candidate_blob,
        overlay_content,
        private_audit_content,
        private_terminal_content,
        report,
    ) = build()
    write_outputs(
        candidate_blob,
        overlay_content,
        private_audit_content,
        private_terminal_content,
        report,
        candidate_path=args.candidate_output,
        overlay_path=args.overlay_output,
        private_audit_path=args.private_audit_output,
        private_terminal_path=args.private_terminal_output,
        report_path=args.report_output,
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "replacement_count":
                    report["overlay"]["total_literal_replacement_count"],
                "control_retarget_count":
                    report["control_retargets"]["count"],
                "surface_issue_count":
                    report["candidate"]["surface_issue_count"],
                "surface_category_counts":
                    report["candidate"]["surface_category_counts"],
                "terminal_boundary_issue_count":
                    report["terminal_boundary_detector"]["issue_count"],
                "candidate_sha256": report["candidate"]["sha256"],
                "candidate": str(args.candidate_output.resolve()),
                "report": str(args.report_output.resolve()),
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, PkRemediationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
