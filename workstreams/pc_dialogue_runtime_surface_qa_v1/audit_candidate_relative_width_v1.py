#!/usr/bin/env python3
"""Audit msggame remediation with a conservative relative G1N width gate.

``msggame.bin`` has not been proven to use the PK event-dialogue 912px
widget, so this audit deliberately does not apply that absolute threshold.
It instead compares each changed literal with the already shipped predecessor:

* a changed literal may not add displayed lines;
* line-wise raw G1N growth may not exceed one half-width cell (24px);
* any positive growth must remain within the predecessor's widest literal
  line in the same block;
* when lines are removed/reflowed, every candidate line must still remain
  within that same empirical block maximum.

The raw comparison metric is 48px for non-ASCII visible characters and 24px
for ASCII/space/control characters.  It is a relative risk metric only, not a
claim about a msggame runtime widget.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
sys.path.insert(0, str(WORKSTREAM))

import audit_runtime_surface_v1 as SURFACE  # noqa: E402


SCHEMA = "nobu16.kr.pc-dialogue-candidate-relative-width-audit.v1"
DEFAULT_PREDECESSOR_ROOT = (
    REPO
    / "tmp"
    / "pc_dialogue_full_retranslation_v0150"
    / "finalizer_preflight_52803"
    / "candidate"
)
DEFAULT_BASE_SOURCE = (
    DEFAULT_PREDECESSOR_ROOT / "MSG" / "JP" / "msggame.bin"
)
DEFAULT_PK_SOURCE = (
    DEFAULT_PREDECESSOR_ROOT / "MSG_PK" / "JP" / "msggame.bin"
)
DEFAULT_REMEDIATION_ROOT = (
    REPO / "tmp" / "pc_dialogue_runtime_surface_remediation_v1"
)
DEFAULT_BASE_CANDIDATE = (
    DEFAULT_REMEDIATION_ROOT
    / "base"
    / "candidate"
    / "MSG"
    / "JP"
    / "msggame.bin"
)
DEFAULT_PK_CANDIDATE = (
    DEFAULT_REMEDIATION_ROOT
    / "pk"
    / "candidate"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)
MAX_LINE_DELTA_PX = 24
APPROVED_LINE_GROWTH_EXCEPTIONS = {
    (
        "pk_msggame",
        4,
        29,
        0,
        3,
    ): {
        "before_width_px": 96,
        "after_width_px": 240,
        "after_literal_sha256":
            "237CEA5BBC83495DC7D304607C5465A5DF989754E87E4E45CC899A06E0611E1C",
        "reason": "user_reported_ai_help_wrap_preserves_whole_korean_word",
    },
    (
        "pk_msggame",
        6,
        3931,
        2,
        0,
    ): {
        "before_width_px": 144,
        "after_width_px": 192,
        "after_literal_sha256":
            "F3A94CD0190137F20069DC50057993E89085E38513255C26AE64837B73A671F3",
        "reason": "dynamic_facility_and_person_objects_require_visible_spacing",
    },
    (
        "pk_msggame",
        6,
        4484,
        1,
        0,
    ): {
        "before_width_px": 72,
        "after_width_px": 120,
        "after_literal_sha256":
            "DFF4BE25AC1898E6A9BF29CAC1150AC34B7D9FD58F8DCC533851EAF18893BF97",
        "reason": "dynamic_person_dative_requires_complete_ege_particle",
    },
    (
        "pk_msggame",
        7,
        2488,
        1,
        1,
    ): {
        "before_width_px": 216,
        "after_width_px": 312,
        "after_literal_sha256":
            "C55898363B11F9A4CFAB0370DA62A33909E26959B35B6DC3E133C4CE69D658DC",
        "reason": "reviewed_suppression_order_uses_one_complete_imperative",
    },
    (
        "pk_msggame",
        7,
        2875,
        2,
        0,
    ): {
        "before_width_px": 96,
        "after_width_px": 216,
        "after_literal_sha256":
            "3DEC81820E865A013EA48F73860A24A3C98CBFB9B22B4A649D3C8773EDE50F03",
        "reason": "reviewed_victory_report_expectation_uses_complete_imperative",
    },
    (
        "pk_msggame",
        9,
        2522,
        1,
        0,
    ): {
        "before_width_px": 48,
        "after_width_px": 96,
        "after_literal_sha256":
            "E7E143567E34AF03AA4CF6643C81546E181B3B994EA59F3F500C4FFDA0A6E05A",
        "reason": "dynamic_person_dative_requires_complete_ege_particle",
    },
    (
        "pk_msggame",
        15,
        587,
        1,
        0,
    ): {
        "before_width_px": 408,
        "after_width_px": 480,
        "after_literal_sha256":
            "BA3AC1889D82566AD48FC3E5922ED78130E8D2495DAE8974DF4749545AAC1D99",
        "reason": "our_side_dynamic_call_requires_explicit_pyeon_relation",
    },
    (
        "pk_msggame",
        7,
        2842,
        2,
        0,
    ): {
        "before_width_px": 48,
        "after_width_px": 96,
        "after_literal_sha256":
            "F704BA605676C22BF9EA6F0BE820C7CF35DAA3E1D1D1EF8E64E3D614CA2F36AE",
        "reason": "dynamic_examples_require_spaces_on_both_literal_edges",
    },
    (
        "pk_msggame",
        9,
        2593,
        0,
        0,
    ): {
        "before_width_px": 144,
        "after_width_px": 192,
        "after_literal_sha256":
            "D48425C8F070C4A2189C3AAC3B90D84F92DC1A12DFA8102CC1E84C84B4340E3C",
        "reason": "enemy_side_phrase_requires_internal_and_dynamic_edge_spaces",
    },
    (
        "pk_msggame",
        9,
        3571,
        0,
        0,
    ): {
        "before_width_px": 144,
        "after_width_px": 192,
        "after_literal_sha256":
            "3FC49664D3FDB92EF4A23AB17A2EC28100CD3A69EFA52888896ED411115483FC",
        "reason": "enemy_side_phrase_requires_internal_and_dynamic_edge_spaces",
    },
    **{
        ("pk_msggame", 9, record_id, 0, 0): {
            "before_width_px": 144,
            "after_width_px": 192,
            "after_literal_sha256":
                "3FC49664D3FDB92EF4A23AB17A2EC28100CD3A69EFA52888896ED411115483FC",
            "reason":
                "enemy_side_phrase_requires_internal_and_dynamic_edge_spaces",
        }
        for record_id in (3575, 3579, 3581, 3582)
    },
    **{
        ("pk_msggame", 9, record_id, 0, 0): {
            "before_width_px": 144,
            "after_width_px": 192,
            "after_literal_sha256":
                "55561AA439771F5188CDD15AC00C5CEC729DA08633DCBC985D28B8106B70DAE0",
            "reason":
                "enemy_side_phrase_requires_internal_and_dynamic_edge_spaces",
        }
        for record_id in (3573, 3576, 3578, 3580)
    },
    (
        "pk_msggame",
        9,
        4132,
        0,
        0,
    ): {
        "before_width_px": 144,
        "after_width_px": 192,
        "after_literal_sha256":
            "8B400AE5079E4C891523F5C6B7C498033C0B734D805CAFDD87B5D3C304926518",
        "reason": "castle_side_phrase_requires_internal_and_dynamic_edge_spaces",
    },
    (
        "pk_msggame",
        14,
        245,
        3,
        4,
    ): {
        "before_width_px": 1728,
        "after_width_px": 1776,
        "after_literal_sha256":
            "145BBCCC53058C3321DF90D1784668175649F40A250FD31B102936A640460367",
        "reason": "siege_rule_terms_require_bound_noun_spacing",
    },
    (
        "pk_msggame",
        15,
        814,
        1,
        0,
    ): {
        "before_width_px": 96,
        "after_width_px": 144,
        "after_literal_sha256":
            "7859DAA2DB1F4378759F9037763D9DCADEF868E6078465E0607D20AE9727A6C2",
        "reason": "dynamic_examples_bound_noun_requires_both_edge_spaces",
    },
    **{
        ("pk_msggame", 15, record_id, literal_id, 0): {
            "before_width_px": 48,
            "after_width_px": 96,
            "after_literal_sha256":
                "F704BA605676C22BF9EA6F0BE820C7CF35DAA3E1D1D1EF8E64E3D614CA2F36AE",
            "reason": "dynamic_examples_require_spaces_on_both_literal_edges",
        }
        for record_id, literal_id in (
            (834, 2), (1047, 0), (1464, 0), (2477, 1), (2481, 0),
            (2483, 1), (2486, 0), (2490, 0), (2492, 1), (2517, 0),
            (2525, 2), (2533, 1), (2552, 1),
        )
    },
    (
        "pk_msggame",
        15,
        1670,
        1,
        1,
    ): {
        "before_width_px": 216,
        "after_width_px": 288,
        "after_literal_sha256":
            "25E9A924D71C5302B02CD79B93775A8E46DD5E87738D77B0196A7EED514E1134",
        "reason": "garbled_gajunge_restored_to_gamun_junge",
    },
    (
        "pk_msggame",
        17,
        228,
        1,
        0,
    ): {
        "before_width_px": 264,
        "after_width_px": 312,
        "after_literal_sha256":
            "6BE46203215A42BBE85F924EBC9DC19207329D45313D157897C872531C3F119C",
        "reason": "dynamic_clan_side_phrase_requires_both_edge_spaces",
    },
    (
        "pk_msggame",
        17,
        362,
        0,
        0,
    ): {
        "before_width_px": 96,
        "after_width_px": 144,
        "after_literal_sha256":
            "08ADF118DC0D1EB5E283234A053BF3B8213D8B4A89C815B0584462DC0D49A83A",
        "reason": "dynamic_person_bound_noun_requires_both_edge_spaces",
    },
    (
        "pk_msggame",
        2,
        248,
        2,
        0,
    ): {
        "before_width_px": 144,
        "after_width_px": 192,
        "after_literal_sha256":
            "D31B9296E95F5D16CD55006A22F552D5CC2341634727E43122CCD1F0DDB41148",
        "reason": "dynamic_pronoun_after_seuseuro_requires_visible_spacing",
    },
    (
        "pk_msggame",
        8,
        286,
        0,
        0,
    ): {
        "before_width_px": 384,
        "after_width_px": 432,
        "after_literal_sha256":
            "B7921E1298D16542F247CDCF5DB66A7E52DA3EBD9C1A469DB00A7962A314B85E",
        "reason": "malformed_crop_failure_predicate_restored_to_past_stem",
    },
    **{
        ("pk_msggame", 8, record_id, 1, 0): {
            "before_width_px": 744,
            "after_width_px": 816,
            "after_literal_sha256":
                "E0FB5A4BCD29404A06E9335A0B80D1DFC05684C395A743C27B9355CCBDBAE3CC",
            "reason": "facility_edict_uses_complete_naerija_imperative",
        }
        for record_id in range(951, 963)
    },
    (
        "pk_msggame",
        15,
        810,
        0,
        2,
    ): {
        "before_width_px": 600,
        "after_width_px": 648,
        "after_literal_sha256":
            "F0CA65E0C8929FAE829E4D5E8284E9EFB0F3A462478EA8017C214FA174722865",
        "reason": "malformed_guja_predicate_restored_to_guhaja_family",
    },
    (
        "pk_msggame",
        15,
        1570,
        1,
        0,
    ): {
        "before_width_px": 312,
        "after_width_px": 360,
        "after_literal_sha256":
            "15DA112185EDCA7262F19749A437AF1DB4DB1D4BBBBD2208386D9782089B7ED2",
        "reason": "dynamic_jugun_topic_uses_complete_iyamallo_particle",
    },
    (
        "pk_msggame",
        15,
        1832,
        1,
        1,
    ): {
        "before_width_px": 456,
        "after_width_px": 624,
        "after_literal_sha256":
            "292D2B69B53DD7CCC16E1AFF3FB45E8AF8850702D0D692B2DE4810D895F871EE",
        "reason": "malformed_got_irira_restored_to_got_orira",
    },
    **{
        ("pk_msggame", 15, record_id, 0, 0): {
            "before_width_px": source_width,
            "after_width_px": source_width + 96,
            "after_literal_sha256": literal_sha256,
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
        (
            "pk_msggame",
            coordinate[0],
            coordinate[1],
            coordinate[2],
            line_index,
        ): {
            "before_width_px": source_width,
            "after_width_px": candidate_width,
            "after_literal_sha256": literal_sha256,
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
                "FBF349839F8142DFD971207264ADB04A24503CAD72261A66CE5EC2265B25240B",
            ),
            (
                (15, 2462, 1), 1, 384, 504,
                "3FF79C531964CC53BD6889620D662C4D6F8CE73C1F00F10BB6ACCAC4FAD82078",
            ),
        )
    },
    (
        "pk_msggame",
        15,
        2175,
        2,
        1,
    ): {
        "before_width_px": 264,
        "after_width_px": 432,
        "after_literal_sha256":
            "AD22A79A09A68E57BD0E189038A5C479E786E7E795F697AE92427F2CB9512D80",
        "reason":
            "runtime_report_question_requires_complete_nominal_predicate",
    },
    (
        "pk_msggame",
        15,
        2176,
        1,
        0,
    ): {
        "before_width_px": 312,
        "after_width_px": 456,
        "after_literal_sha256":
            "9CC7936075457F7F2574720A2B47A47683BA0B9D56877FC08FB9D25CB619E70F",
        "reason":
            "dynamic_address_question_requires_complete_finite_clause",
    },
    (
        "pk_msggame",
        15,
        2180,
        1,
        1,
    ): {
        "before_width_px": 144,
        "after_width_px": 600,
        "after_literal_sha256":
            "CB63D03A31DFC425013234C9106250E581633885B5776E792008FD2BB34F6CCD",
        "reason":
            "runtime_rumor_question_requires_complete_nominal_predicate",
    },
    (
        "pk_msggame",
        15,
        2184,
        1,
        1,
    ): {
        "before_width_px": 96,
        "after_width_px": 480,
        "after_literal_sha256":
            "54DB8BE3AF763F53A754AEFD71FB89C36FAE00D340419CF9305855714D761FFC",
        "reason":
            "runtime_rumor_question_requires_complete_nominal_predicate",
    },
    **{
        ("pk_msggame", 15, 1673, 0, line_index): {
            "before_width_px": source_width,
            "after_width_px": candidate_width,
            "after_literal_sha256":
                "823836B9C3C64952D6428222BBD2A94C12240846BCA2CE6987E5890B86636E14",
            "reason":
                "historically_verified_joto_policy_sentence_restored_exactly",
        }
        for line_index, source_width, candidate_width in (
            (0, 528, 864),
            (1, 600, 792),
        )
    },
    (
        "base_msggame",
        2,
        142,
        0,
        0,
    ): {
        "before_width_px": 432,
        "after_width_px": 528,
        "after_literal_sha256":
            "22EEFFBCDA36158D04EAF65FE38066CFD52BB89B89B51F3123D44DB5C6DDE2A4",
        "reason": "user_reported_illness_notification_exact_regression",
    },
    (
        "base_msggame",
        8,
        1020,
        1,
        0,
    ): {
        "before_width_px": 192,
        "after_width_px": 528,
        "after_literal_sha256":
            "D4F2047E3AAEAC3D2C492435A00B7378B7489E709FCB2673A55561C71149C6FA",
        "reason": "user_reported_illness_dialogue_exact_regression",
    },
    (
        "pk_msggame",
        2,
        148,
        0,
        0,
    ): {
        "before_width_px": 432,
        "after_width_px": 528,
        "after_literal_sha256":
            "22EEFFBCDA36158D04EAF65FE38066CFD52BB89B89B51F3123D44DB5C6DDE2A4",
        "reason": "user_reported_illness_notification_exact_regression",
    },
    (
        "pk_msggame",
        8,
        1032,
        1,
        0,
    ): {
        "before_width_px": 192,
        "after_width_px": 528,
        "after_literal_sha256":
            "62A1E054B0EFC20A5183459A42E9B85B22988D74B1B3E889E0BAF6FA9182688E",
        "reason": "user_reported_illness_dialogue_exact_regression",
    },
    (
        "pk_msggame",
        15,
        1545,
        2,
        0,
    ): {
        "before_width_px": 432,
        "after_width_px": 480,
        "after_literal_sha256":
            "2FA200445CC1E0D2BB617EB0ADA5C158181947847DE6641BFDF5DFB22CBD8FA5",
        "reason": "user_reported_lure_plan_exact_particle_regression",
    },
    (
        "pk_msggame",
        6,
        3765,
        1,
        0,
    ): {
        "before_width_px": 48,
        "after_width_px": 288,
        "after_literal_sha256":
            "03EA3B48FBD071C9B5948D0BD37D834E8F8FD44CD1ADB9C76C04E4211550EE5F",
        "reason": "synthetic_clan_selector_envoy_relation",
    },
    (
        "pk_msggame",
        15,
        1234,
        1,
        2,
    ): {
        "before_width_px": 0,
        "after_width_px": 48,
        "after_literal_sha256":
            "30B78A21EA791E8B4930001357CFF180D99BE0C33DB663B0F9540ED8DE1D8F87",
        "reason": "question_stem_precedes_single_runtime_question_terminal",
    },
    (
        "pk_msggame",
        7,
        1714,
        1,
        1,
    ): {
        "before_width_px": 600,
        "after_width_px": 648,
        "after_literal_sha256":
            "66DCC5EF0E449AE30AF939C630BD67907B3716D121762D1A93A8E471D5CD1B58",
        "reason": "synthetic_castle_selector_object_particle_restored",
    },
    (
        "pk_msggame",
        8,
        758,
        0,
        0,
    ): {
        "before_width_px": 192,
        "after_width_px": 264,
        "after_literal_sha256":
            "4530D93071844D218CF900688931537C8B7CD194CE130D476CF661AD50156BC6",
        "reason": "dynamic_facility_particle_neutral_case_carrier",
    },
    (
        "pk_msggame",
        8,
        764,
        0,
        0,
    ): {
        "before_width_px": 408,
        "after_width_px": 480,
        "after_literal_sha256":
            "0CC17C0FF9A7C2CD755A5186870ED7FD5DFE60EC67A2841414BB1F4F23A5B11B",
        "reason": "dynamic_facility_particle_neutral_case_carrier",
    },
    (
        "pk_msggame",
        8,
        766,
        0,
        0,
    ): {
        "before_width_px": 192,
        "after_width_px": 264,
        "after_literal_sha256":
            "0FC59E4C3992D4026261A01AD28004791D10CE72C3D416F1F6627EFB29B9B252",
        "reason": "dynamic_facility_particle_neutral_case_carrier",
    },
    (
        "pk_msggame",
        8,
        1031,
        0,
        0,
    ): {
        "before_width_px": 480,
        "after_width_px": 624,
        "after_literal_sha256":
            "00E28A7E1931A1A6E2BC1ECCDD633D60F002048C299EE0021255466619016C07",
        "reason": "reviewed_fixed_illness_recovery_dialogue",
    },
    (
        "pk_msggame",
        8,
        1031,
        1,
        1,
    ): {
        "before_width_px": 168,
        "after_width_px": 504,
        "after_literal_sha256":
            "1A2404DDD5F86BE6021E35708F8AE3622ABF519BDF49F9C87A7A2EE02908AF0D",
        "reason": "reviewed_fixed_illness_recovery_dialogue",
    },
    (
        "pk_msggame",
        8,
        1031,
        2,
        0,
    ): {
        "before_width_px": 240,
        "after_width_px": 600,
        "after_literal_sha256":
            "3CE956EEB7AC8028B440C10E2F103FF63FC0BEAACABB763CF372C6A96CAA19D5",
        "reason": "reviewed_fixed_illness_recovery_dialogue",
    },
    (
        "pk_msggame",
        8,
        1198,
        0,
        1,
    ): {
        "before_width_px": 384,
        "after_width_px": 432,
        "after_literal_sha256":
            "922E290DC261A2F4630C83982CAFCEBEADB5AFC9CA603B194322FDF307A22D0C",
        "reason": "past_report_boundary_requires_past_existential_stem",
    },
    (
        "pk_msggame",
        9,
        1511,
        0,
        0,
    ): {
        "before_width_px": 288,
        "after_width_px": 432,
        "after_literal_sha256":
            "64DAB5DA61B6E482BAD0080A6E5D56A4F7D3729D7450B9FBE041D9CC34FDAAD2",
        "reason": "dynamic_address_particle_neutral_surprise_carrier",
    },
    (
        "pk_msggame",
        9,
        1573,
        0,
        1,
    ): {
        "before_width_px": 264,
        "after_width_px": 336,
        "after_literal_sha256":
            "0B9A04F9CF96D00A4C0DA5B6C2F67D1F3BF5E0ABCEA7C61BA16FA0D388969EBA",
        "reason": "dynamic_address_particle_neutral_assignment_carrier",
    },
    (
        "pk_msggame",
        9,
        1769,
        0,
        0,
    ): {
        "before_width_px": 240,
        "after_width_px": 360,
        "after_literal_sha256":
            "3F723671EC6DBDE260012C4D1287385DCB11D52D1776932D929109E39289FA2C",
        "reason": "dynamic_address_particle_neutral_opponent_carrier",
    },
    (
        "pk_msggame",
        9,
        2408,
        0,
        0,
    ): {
        "before_width_px": 240,
        "after_width_px": 432,
        "after_literal_sha256":
            "DF3CEFB4C9C4C2C60F23DD9CC76E192A8EB3B4F128213C8AE63336C42319960B",
        "reason": "dynamic_subject_particle_neutral_news_carrier",
    },
    (
        "pk_msggame",
        15,
        319,
        1,
        1,
    ): {
        "before_width_px": 0,
        "after_width_px": 168,
        "after_literal_sha256":
            "D78CE38D1B02519A3F1D8145254468C7BDD60BF7984D6166E583F8E828B1388C",
        "reason": "dynamic_person_particle_neutral_name_carrier",
    },
    (
        "pk_msggame",
        15,
        325,
        1,
        1,
    ): {
        "before_width_px": 0,
        "after_width_px": 168,
        "after_literal_sha256":
            "B6786950827326CF7A2C084321AEA0D330FFB682CD58C5264A0123206D0AA260",
        "reason": "dynamic_person_particle_neutral_name_carrier",
    },
    (
        "pk_msggame",
        15,
        326,
        1,
        1,
    ): {
        "before_width_px": 0,
        "after_width_px": 168,
        "after_literal_sha256":
            "B6786950827326CF7A2C084321AEA0D330FFB682CD58C5264A0123206D0AA260",
        "reason": "dynamic_person_particle_neutral_name_carrier",
    },
    **{
        ("pk_msggame", *coordinate, 0): {
            "before_width_px": 360,
            "after_width_px": candidate_width_px,
            "after_literal_sha256": digest,
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
    (
        "pk_msggame",
        15,
        440,
        1,
        0,
    ): {
        "before_width_px": 360,
        "after_width_px": 576,
        "after_literal_sha256":
            "59C1315F0D2BA49B24770D00057ED95055A6C01278FCE8E72D768A33F28EBAA9",
        "reason": "dynamic_person_particle_neutral_self_introduction",
    },
    (
        "pk_msggame",
        15,
        445,
        1,
        0,
    ): {
        "before_width_px": 360,
        "after_width_px": 576,
        "after_literal_sha256":
            "2432C4AFB5B8E69140B3C48CEDEB3B63D95BB6D6D169C8F5183AE89E8502E6FF",
        "reason": "dynamic_person_particle_neutral_self_introduction",
    },
    **{
        ("pk_msggame", *coordinate, 0): {
            "before_width_px": 456,
            "after_width_px": 624,
            "after_literal_sha256":
                "DAE467EDBFA8A89C9392EC3011E169EC995B4C73518949074B88086283C59359",
            "reason": "dynamic_castle_particle_neutral_location_carrier",
        }
        for coordinate in ((15, 924, 2), (15, 929, 2))
    },
    (
        "pk_msggame",
        15,
        2093,
        0,
        1,
    ): {
        "before_width_px": 96,
        "after_width_px": 672,
        "after_literal_sha256":
            "F244E83D4EE0381F603EE9191A8A37D318452EC8CE6190C0061024407BC9987B",
        "reason": "fixed_clan_particle_and_natural_target_selection",
    },
    (
        "pk_msggame",
        15,
        2093,
        2,
        0,
    ): {
        "before_width_px": 240,
        "after_width_px": 360,
        "after_literal_sha256":
            "67DC8F7001F509BEB9EC44958B1B23B150C1E37A4192C554F60E01735B9C3B83",
        "reason": "dynamic_strategy_particle_neutral_carrier",
    },
    **{
        ("pk_msggame", *coordinate, line_index): {
            "before_width_px": source_width_px,
            "after_width_px": candidate_width_px,
            "after_literal_sha256": digest,
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
        ("pk_msggame", *coordinate, line_index): {
            "before_width_px": source_width_px,
            "after_width_px": candidate_width_px,
            "after_literal_sha256": digest,
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
    (
        "pk_msggame",
        15,
        1359,
        3,
        0,
    ): {
        "before_width_px": 504,
        "after_width_px": 552,
        "after_literal_sha256":
            "687C571AC901B2B25E81F161A0BF8F214D43B2B928EC485DC061B2F28FF43409",
        "reason": "past_injury_boundary_requires_past_give_stem",
    },
    (
        "pk_msggame",
        6,
        4468,
        0,
        0,
    ): {
        "before_width_px": 504,
        "after_width_px": 720,
        "after_literal_sha256":
            "CA20CAB94D2950F842CE735DCA00300B1740D666A7F28C9D470FE62B1188E8C0",
        "reason": "reviewed_impersonal_siege_expertise_sentence",
    },
    (
        "pk_msggame",
        6,
        4468,
        2,
        0,
    ): {
        "before_width_px": 48,
        "after_width_px": 528,
        "after_literal_sha256":
            "78DDF37DDDBADA306C917DD2783082FE0C575E3794B749579B176281C6CB3383",
        "reason": "reviewed_impersonal_siege_expertise_sentence",
    },
    (
        "pk_msggame",
        2,
        131,
        2,
        0,
    ): {
        "before_width_px": 48,
        "after_width_px": 120,
        "after_literal_sha256":
            "D34B7A6D8D228B88C219FD90D68D3F729468ED6061483F5F76222058587D95C3",
        "reason": "dynamic_persona_dative_command_boundary",
    },
    (
        "pk_msggame",
        2,
        621,
        0,
        0,
    ): {
        "before_width_px": 168,
        "after_width_px": 216,
        "after_literal_sha256":
            "A30F04521CEADE8D934B86B44B7238332A98C599884EA3D24FD280C5D095B0A0",
        "reason": "reviewed_direct_person_title_boundary_spacing",
    },
    (
        "pk_msggame",
        6,
        1639,
        0,
        0,
    ): {
        "before_width_px": 48,
        "after_width_px": 96,
        "after_literal_sha256":
            "DFCDD6A59C71F47374099B6EAF6FA2CE0C078F09DD23717C8ACAB534DB59D8D0",
        "reason": "reviewed_dynamic_person_pair_separator",
    },
    (
        "pk_msggame",
        6,
        2449,
        0,
        0,
    ): {
        "before_width_px": 72,
        "after_width_px": 120,
        "after_literal_sha256":
            "E47B9645051ED3311E25117C2AB1E5E21E468FC788B8E66CA8727776B0F170EB",
        "reason": "reviewed_direct_person_title_boundary_spacing",
    },
    (
        "pk_msggame",
        6,
        3409,
        0,
        0,
    ): {
        "before_width_px": 192,
        "after_width_px": 336,
        "after_literal_sha256":
            "3597966493D4B6B5292CF3827E38B5EBD605747E1C870CBA18847BD0AF785296",
        "reason": "reviewed_dynamic_reassurance_clause",
    },
    (
        "pk_msggame",
        6,
        3454,
        0,
        0,
    ): {
        "before_width_px": 216,
        "after_width_px": 432,
        "after_literal_sha256":
            "8813E87B96A090622625C152227AC65BEDD6BCA89D352539AA9BB8C879FACC27",
        "reason": "reviewed_dynamic_merit_rank_relation",
    },
    (
        "pk_msggame",
        6,
        3694,
        0,
        0,
    ): {
        "before_width_px": 0,
        "after_width_px": 312,
        "after_literal_sha256":
            "FF18D3C08F9742444432541CE055D855EDE892F2ED415DD68A6DF1B510E3A6C3",
        "reason": "reviewed_dynamic_pronoun_invariant_object_boundary",
    },
    (
        "pk_msggame",
        6,
        4020,
        0,
        0,
    ): {
        "before_width_px": 528,
        "after_width_px": 624,
        "after_literal_sha256":
            "07AC409BC817588DCD429CED33BB0723B7FF4627459CA562D51CB478ABE6E72F",
        "reason": "reviewed_dynamic_siege_force_predicate",
    },
    (
        "pk_msggame",
        6,
        4185,
        1,
        0,
    ): {
        "before_width_px": 288,
        "after_width_px": 360,
        "after_literal_sha256":
            "EFDF4BF0FBCD9A39E6DF050EB6F9DBE254AB2D945B190041D22DEF5211443880",
        "reason": "reviewed_dynamic_march_direction_boundary",
    },
    (
        "pk_msggame",
        6,
        4186,
        1,
        0,
    ): {
        "before_width_px": 288,
        "after_width_px": 360,
        "after_literal_sha256":
            "EFDF4BF0FBCD9A39E6DF050EB6F9DBE254AB2D945B190041D22DEF5211443880",
        "reason": "reviewed_dynamic_march_direction_boundary",
    },
    **{
        ("pk_msggame", block_id, record_id, literal_id, line_index): {
            "before_width_px": before_width_px,
            "after_width_px": after_width_px,
            "after_literal_sha256": literal_sha256,
            "reason": reason,
        }
        for (
            block_id,
            record_id,
            literal_id,
            line_index,
            before_width_px,
            after_width_px,
            literal_sha256,
            reason,
        ) in (
            (
                6, 4187, 1, 0, 384, 552,
                "7795BB7BB206AFE58B964F529F6432670327CE948E421FBD462DBAEFCE2890B7",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4187, 1, 1, 96, 168,
                "7795BB7BB206AFE58B964F529F6432670327CE948E421FBD462DBAEFCE2890B7",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4188, 1, 0, 384, 624,
                "C6DC5EC486F579374D702F1F8C87FD5A22B5AC1129D209723CB9AF0E56211524",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4188, 1, 1, 120, 192,
                "C6DC5EC486F579374D702F1F8C87FD5A22B5AC1129D209723CB9AF0E56211524",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4189, 1, 0, 384, 624,
                "C6DC5EC486F579374D702F1F8C87FD5A22B5AC1129D209723CB9AF0E56211524",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4189, 1, 1, 120, 192,
                "C6DC5EC486F579374D702F1F8C87FD5A22B5AC1129D209723CB9AF0E56211524",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4190, 2, 0, 48, 96,
                "EB74759B7BC94B311AB07BE045D2242CA4D79D434D2B04872554CF5E30D133F9",
                "reviewed_dynamic_march_direction_boundary",
            ),
            (
                6, 4191, 2, 0, 48, 168,
                "54AE545B7AFDB241BBC75B2BD252247FDC5E446D557ED8A3D12E2A22DCEAF98B",
                "reviewed_dynamic_march_direction_boundary",
            ),
            (
                6, 4192, 2, 0, 48, 168,
                "54AE545B7AFDB241BBC75B2BD252247FDC5E446D557ED8A3D12E2A22DCEAF98B",
                "reviewed_dynamic_march_direction_boundary",
            ),
            (
                6, 4193, 2, 0, 96, 216,
                "47D110AF28FDD825583B448E2804B2A74912DD70C2FDC31E6BF9456ACC54CEBE",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4193, 2, 1, 264, 504,
                "47D110AF28FDD825583B448E2804B2A74912DD70C2FDC31E6BF9456ACC54CEBE",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4194, 2, 0, 96, 288,
                "0286E2BDEED198A4974FD0F71631B7194A1B3685B621ED59B75B79D76F6F8769",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4194, 2, 1, 264, 504,
                "0286E2BDEED198A4974FD0F71631B7194A1B3685B621ED59B75B79D76F6F8769",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4195, 2, 0, 96, 288,
                "0286E2BDEED198A4974FD0F71631B7194A1B3685B621ED59B75B79D76F6F8769",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
            (
                6, 4195, 2, 1, 264, 504,
                "0286E2BDEED198A4974FD0F71631B7194A1B3685B621ED59B75B79D76F6F8769",
                "reviewed_dynamic_multidirectional_march_boundary",
            ),
        )
    },
    **{
        ("pk_msggame", block_id, record_id, literal_id, line_index): {
            "before_width_px": before_width_px,
            "after_width_px": after_width_px,
            "after_literal_sha256": literal_sha256,
            "reason": "reviewed_runtime_assembly_semantic_or_boundary_repair",
        }
        for (
            block_id,
            record_id,
            literal_id,
            line_index,
            before_width_px,
            after_width_px,
            literal_sha256,
        ) in (
            (6, 4671, 1, 1, 336, 600, "7E79E44636EE6571A5B05FB60AACD2B66BDC712EAB17155DE12573C9A1B71103"),
            (7, 284, 0, 0, 96, 144, "E9E7C0BA2BE3B5AB12149BED04531378CDB9EC286A802D8C567C8399B695716A"),
            (7, 386, 1, 0, 96, 144, "E9E7C0BA2BE3B5AB12149BED04531378CDB9EC286A802D8C567C8399B695716A"),
            (7, 2032, 0, 1, 96, 168, "483C8C2A5E5AEB47E576C8251CB59CC4DD5BEF666D3E423C011BDBBF5E109756"),
            (7, 2032, 1, 0, 48, 312, "CE5F5E53FF42FFD09816F2BD96AFD6DDD75548DD3BBF8D2760D9B55D26019689"),
            (7, 2490, 0, 0, 600, 792, "62C4F9F216F6B06658C340984F02ADA7BDA8DCB3839F5E56D1CF8D369C08C143"),
            (7, 2600, 0, 0, 312, 504, "AB6CDEFA6A091A32A0A5365ED897EE172F60710AD1E340C18F57C584C33913D7"),
            (8, 261, 1, 2, 408, 480, "5465F2AFF8724181F33713922AB785277FAF0B8948FCA25CBDFABCF2A7333B3F"),
            (8, 264, 2, 1, 408, 480, "EC51B1FECDFED75FF23D6BFDA618729D3C85B25F652EAA63D977DB72E7FC8F1E"),
            (8, 273, 1, 1, 888, 960, "B1A98068D2B846C52ABCD40AE4C3BE64E09E08BFFA2E5BDDC7ACF7E75FD58464"),
            (8, 353, 0, 1, 480, 552, "C077FB537702D22D818A87DCD4197F5A97E5E64CAD2543213F6AFF2A3087C76E"),
            (8, 354, 0, 0, 672, 744, "4E194436DAA97D8FCF5E4289D78C314FE935DA6DFB78CFB3DA585B996BEC0243"),
            (9, 2104, 0, 0, 48, 288, "2824336B884E84089EF1580A51F322E6E25AEDF52ABBF59F5F64FBE7CF063CFB"),
            (9, 2186, 1, 0, 48, 96, "40B2EAE654E3C8818A382ECA6316B89B8CB8FE748240FF66B6EBA5C43B1F93D8"),
            (9, 2641, 0, 1, 48, 456, "A0A4322A76C4E7780D2B77BE63863695CCD6C28CD5B30EB1D689A93529A804A1"),
            (9, 3967, 0, 0, 912, 1032, "CA5EAA1E4236D4ACCF31ED886E63FD3EF81124DE0E1A83053473CCC22BCC6724"),
            (15, 320, 3, 0, 96, 432, "4C3067C4834EB9F46C20DCA3A46DFBDC6CB8BDD442876B59659A1E928CF062EC"),
            (15, 321, 3, 0, 96, 432, "4C3067C4834EB9F46C20DCA3A46DFBDC6CB8BDD442876B59659A1E928CF062EC"),
            (15, 703, 1, 1, 840, 936, "2FB7E23E1DE99AB3DF4FCF6C6246C3AE1797235C1C56B39D14AE1A9D09D361A0"),
            (15, 704, 1, 2, 96, 240, "9A847913BFB66707B88A5BFF887236E72F28F70612B0A0B58F70628DA0457A02"),
            (15, 1283, 2, 0, 432, 504, "5226A3ADDF799C6818B5BEFF369944A87496292DB736E52E98A0755619F3FB9B"),
            (15, 1572, 1, 0, 168, 240, "C6E07C0CC67E9D97C3D0BFF7C44DFA12A01B514630243A5A86E1B26847FE612A"),
            (15, 1572, 4, 1, 408, 504, "37B21114B64A9FB67ABB1D1034689761BFD3B5346B6929B463278657B2B9C46A"),
            (15, 1835, 0, 0, 816, 888, "97C72478D8B281FA2E1AFB822BA1874F5DB79AC24BFEBFE67CC81CF7F4DF905F"),
            (15, 1858, 2, 1, 432, 504, "C58892812693334A404780225A179D842C04383F25E9DB9B0A2047BDE7BC7783"),
            (15, 1946, 0, 0, 216, 312, "AE01D37BEBFBB14227DAB90604CDBB0E00CEB364D12E8F48680C2D2A7E75B340"),
            (15, 1967, 0, 0, 576, 648, "CF7FB7CF62B0C5451AF8AC55FF8F084D408AFD066A249468C5745B676044F74A"),
            (15, 2407, 1, 1, 816, 888, "22B41125659733906F40B6A00D3C2ADA86065BCB895F83DE946C8D751C717503"),
            (15, 2441, 0, 1, 384, 576, "DBD0E6DC715391B197373800F4B70CB2876863B033FC3768D0FB407D64BC5498"),
            (17, 381, 1, 0, 264, 312, "AD46E754D7DAA003F555F38E3BF751E428BC418ADBAAA5F30892319A61C6995F"),
            (17, 664, 2, 0, 96, 144, "E0B85B164C33E19DF83C440C8EB43166BE24E5F1332B31893192AA8EE7B327E7"),
            (17, 721, 1, 0, 96, 144, "E0B85B164C33E19DF83C440C8EB43166BE24E5F1332B31893192AA8EE7B327E7"),
            (17, 763, 0, 0, 96, 144, "E0B85B164C33E19DF83C440C8EB43166BE24E5F1332B31893192AA8EE7B327E7"),
            (17, 777, 2, 0, 96, 144, "E0B85B164C33E19DF83C440C8EB43166BE24E5F1332B31893192AA8EE7B327E7"),
            (17, 847, 1, 0, 312, 360, "2F6481C27118557DFD53CD36A84BE633441930166CF13B81B127933306AEB320"),
        )
    },
    (
        "pk_msggame",
        8,
        936,
        1,
        0,
    ): {
        "before_width_px": 192,
        "after_width_px": 240,
        "after_literal_sha256":
            "716533848D9BD72AB0D3F0070B585E08ADA6053DD0A920610B26214979D4D3EF",
        "reason": "reviewed_dependent_arae_boundary_spacing",
    },
    (
        "pk_msggame",
        8,
        941,
        1,
        0,
    ): {
        "before_width_px": 144,
        "after_width_px": 192,
        "after_literal_sha256":
            "1E4543FA32FA3829FF781728D481826231CF78EE07D7105FED63450868710445",
        "reason": "reviewed_dependent_arae_boundary_spacing",
    },
    **{
        ("pk_msggame", 17, record_id, literal_id, 0): {
            "before_width_px": 144,
            "after_width_px": 192,
            "after_literal_sha256":
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
        ("pk_msggame", 17, record_id, 0, 0): {
            "before_width_px": 144,
            "after_width_px": 192,
            "after_literal_sha256":
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
        ("pk_msggame", 17, record_id, 0, 0): {
            "before_width_px": 144,
            "after_width_px": 192,
            "after_literal_sha256":
                "D1C5BEAECB3F7D0B02263F9B88477A9B762EA52401634F84BFEDAEBE55BEAFD4",
            "reason": "reviewed_unit_boundary_spacing_on_both_edges",
        }
        for record_id in (694, 695, 697, 698, 699, 700)
    },
    **{
        ("pk_msggame", 15, record_id, 2, 0): {
            "before_width_px": 336,
            "after_width_px": 408,
            "after_literal_sha256":
                "7082D596D1D7721F3EC4AAB08C615F7FD323EC805BD7E4EB6F0268C0497FEB3A",
            "reason": "reviewed_dynamic_relation_invariant_service_boundary",
        }
        for record_id in (320, 321)
    },
    **{
        ("pk_msggame", *coordinate, 0): {
            "before_width_px": source_width_px,
            "after_width_px": candidate_width_px,
            "after_literal_sha256": literal_sha256,
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
        ("pk_msggame", *coordinate, 0): {
            "before_width_px": source_width_px,
            "after_width_px": candidate_width_px,
            "after_literal_sha256": literal_sha256,
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


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def raw_g1n_width_px(value: str) -> int:
    return sum(
        24 if ord(character) < 0x80 else 48
        for character in value
    )


def approved_growth_exception(
    resource: str,
    coordinate: tuple[int, int, int],
    line_index: int,
    before_width: int,
    after_width: int,
    after_literal: str,
) -> bool:
    expected = APPROVED_LINE_GROWTH_EXCEPTIONS.get(
        (
            resource,
            coordinate[0],
            coordinate[1],
            coordinate[2],
            line_index,
        )
    )
    return (
        expected is not None
        and before_width == expected["before_width_px"]
        and after_width == expected["after_width_px"]
        and sha256_bytes(after_literal.encode("utf-16le"))
        == expected["after_literal_sha256"]
    )


def literal_map(
    records: Mapping[tuple[int, int], Any],
) -> dict[tuple[int, int, int], str]:
    return {
        (
            coordinate[0],
            coordinate[1],
            literal.literal_id,
        ): literal.text
        for coordinate, record in records.items()
        for literal in SURFACE.parse_record_literals(record)
    }


def block_maxima(
    literals: Mapping[tuple[int, int, int], str],
) -> dict[int, int]:
    maxima: dict[int, int] = {}
    for (block_id, _record_id, _literal_id), text in literals.items():
        for line in text.split("\n"):
            maxima[block_id] = max(
                maxima.get(block_id, 0),
                raw_g1n_width_px(line),
            )
    return maxima


def audit_pair(
    resource: str,
    source_path: Path,
    candidate_path: Path,
) -> dict[str, Any]:
    source_records, source_sha256 = SURFACE.records_from_path(source_path)
    candidate_records, candidate_sha256 = SURFACE.records_from_path(
        candidate_path
    )
    source_literals = literal_map(source_records)
    candidate_literals = literal_map(candidate_records)
    issues: list[dict[str, Any]] = []
    if set(source_literals) != set(candidate_literals):
        issues.append(
            {
                "category": "literal_coordinate_set_changed",
                "source_count": len(source_literals),
                "candidate_count": len(candidate_literals),
            }
        )
    predecessor_block_max = block_maxima(source_literals)
    changed_literal_count = 0
    positive_line_delta_count = 0
    maximum_positive_delta_px = 0
    line_count_reduced_count = 0
    approved_growth_exception_count = 0

    for coordinate in sorted(set(source_literals) & set(candidate_literals)):
        before = source_literals[coordinate]
        after = candidate_literals[coordinate]
        if before == after:
            continue
        changed_literal_count += 1
        before_lines = before.split("\n")
        after_lines = after.split("\n")
        block_max = predecessor_block_max[coordinate[0]]
        if len(after_lines) > len(before_lines):
            issues.append(
                {
                    "category": "display_line_count_expanded",
                    "block_id": coordinate[0],
                    "record_id": coordinate[1],
                    "literal_id": coordinate[2],
                    "before": len(before_lines),
                    "after": len(after_lines),
                }
            )
        if len(after_lines) < len(before_lines):
            line_count_reduced_count += 1
        if len(after_lines) == len(before_lines):
            for line_index, (before_line, after_line) in enumerate(
                zip(before_lines, after_lines)
            ):
                before_width = raw_g1n_width_px(before_line)
                after_width = raw_g1n_width_px(after_line)
                delta = after_width - before_width
                if delta <= 0:
                    continue
                positive_line_delta_count += 1
                maximum_positive_delta_px = max(
                    maximum_positive_delta_px,
                    delta,
                )
                if delta > MAX_LINE_DELTA_PX:
                    if approved_growth_exception(
                        resource,
                        coordinate,
                        line_index,
                        before_width,
                        after_width,
                        after,
                    ):
                        approved_growth_exception_count += 1
                    else:
                        issues.append(
                            {
                                "category":
                                    "raw_g1n_delta_exceeds_24px",
                                "block_id": coordinate[0],
                                "record_id": coordinate[1],
                                "literal_id": coordinate[2],
                                "line_index": line_index,
                                "before_width_px": before_width,
                                "after_width_px": after_width,
                                "delta_px": delta,
                                "block_predecessor_max_px": block_max,
                            }
                        )
                if after_width > block_max:
                    issues.append(
                        {
                            "category": (
                                "positive_delta_exceeds_block_predecessor_max"
                            ),
                            "block_id": coordinate[0],
                            "record_id": coordinate[1],
                            "literal_id": coordinate[2],
                            "line_index": line_index,
                            "before_width_px": before_width,
                            "after_width_px": after_width,
                            "delta_px": delta,
                            "block_predecessor_max_px": block_max,
                        }
                    )
        else:
            for line_index, after_line in enumerate(after_lines):
                after_width = raw_g1n_width_px(after_line)
                if after_width <= block_max:
                    continue
                issues.append(
                    {
                        "category": (
                            "reflowed_line_exceeds_block_predecessor_max"
                        ),
                        "block_id": coordinate[0],
                        "record_id": coordinate[1],
                        "literal_id": coordinate[2],
                        "line_index": line_index,
                        "after_width_px": after_width,
                        "block_predecessor_max_px": block_max,
                    }
                )

    category_counts = Counter(issue["category"] for issue in issues)
    return {
        "resource": resource,
        "status": "PASS" if not issues else "FAIL",
        "source": {
            "path": str(source_path.resolve()),
            "size": source_path.stat().st_size,
            "sha256": source_sha256,
        },
        "candidate": {
            "path": str(candidate_path.resolve()),
            "size": candidate_path.stat().st_size,
            "sha256": candidate_sha256,
        },
        "changed_literal_count": changed_literal_count,
        "positive_line_delta_count": positive_line_delta_count,
        "maximum_positive_delta_px": maximum_positive_delta_px,
        "line_count_reduced_count": line_count_reduced_count,
        "approved_growth_exception_count":
            approved_growth_exception_count,
        "issue_count": len(issues),
        "category_counts": dict(sorted(category_counts.items())),
        "issues": issues,
    }


def build_report(
    base_source: Path,
    base_candidate: Path,
    pk_source: Path,
    pk_candidate: Path,
) -> dict[str, Any]:
    resources = {
        "MSG/JP/msggame.bin": audit_pair(
            "base_msggame",
            base_source,
            base_candidate,
        ),
        "MSG_PK/JP/msggame.bin": audit_pair(
            "pk_msggame",
            pk_source,
            pk_candidate,
        ),
    }
    issue_count = sum(
        resource["issue_count"] for resource in resources.values()
    )
    return {
        "schema": SCHEMA,
        "status": "PASS" if issue_count == 0 else "FAIL",
        "release_target": "0.15.0",
        "issue_count": issue_count,
        "contract": {
            "event_dialogue_912px_gate_applied": False,
            "raw_g1n_full_width_px": 48,
            "raw_g1n_half_width_px": 24,
            "maximum_allowed_line_growth_px": MAX_LINE_DELTA_PX,
            "display_line_count_expansion_allowed": False,
            "positive_growth_must_fit_block_predecessor_max": True,
            "approved_line_growth_exceptions": [
                {
                    "resource": key[0],
                    "block_id": key[1],
                    "record_id": key[2],
                    "literal_id": key[3],
                    "line_index": key[4],
                    **value,
                }
                for key, value in sorted(
                    APPROVED_LINE_GROWTH_EXCEPTIONS.items()
                )
            ],
        },
        "resources": resources,
        "literal_bodies_omitted": True,
        "steam_write_performed": False,
    }


def canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-source",
        type=Path,
        default=DEFAULT_BASE_SOURCE,
    )
    parser.add_argument(
        "--base-candidate",
        type=Path,
        default=DEFAULT_BASE_CANDIDATE,
    )
    parser.add_argument(
        "--pk-source",
        type=Path,
        default=DEFAULT_PK_SOURCE,
    )
    parser.add_argument(
        "--pk-candidate",
        type=Path,
        default=DEFAULT_PK_CANDIDATE,
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_report(
        args.base_source,
        args.base_candidate,
        args.pk_source,
        args.pk_candidate,
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(canonical_json(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "schema": payload["schema"],
                "status": payload["status"],
                "issue_count": payload["issue_count"],
                "resources": {
                    path: {
                        "candidate_sha256": resource["candidate"]["sha256"],
                        "changed_literal_count":
                            resource["changed_literal_count"],
                        "positive_line_delta_count":
                            resource["positive_line_delta_count"],
                        "maximum_positive_delta_px":
                            resource["maximum_positive_delta_px"],
                        "issue_count": resource["issue_count"],
                    }
                    for path, resource in payload["resources"].items()
                },
                "output": (
                    str(args.output.resolve())
                    if args.output is not None
                    else None
                ),
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 1 if args.strict and payload["issue_count"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, SURFACE.SurfaceAuditError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
