#!/usr/bin/env python3
"""Build PK block-0 runtime-terminal segment 1033 decisions."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch003_segment1011 as BASE_TAIL
import build_base_batch004_segment1012 as BASE_MIDDLE
import build_pk_batch001_segment1025 as HELPERS
import build_pk_batch003_segment1032 as LEFT_PK


ENGINE = BASE_MIDDLE.ENGINE
GENERAL = BASE_MIDDLE.GENERAL
UTIL = BASE_MIDDLE.UTIL
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "pk_msggame_B004_S1033.private.v1.jsonl"
)
BASE_DECISIONS = (
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B003_S1011.private.v1.jsonl",
        "075BE49C32854623B46955CC92AA939181B0AF802EF9322D54B528E62759FD34",
    ),
    (
        REPO
        / "tmp"
        / WORKSTREAM.name
        / "decisions"
        / "base_msggame_B004_S1012.private.v1.jsonl",
        "E528D51534565D355E6EADE80F4A0A15C499CFCC50E9CE04ABD2B7E6E2359FBC",
    ),
)
SEGMENT = 1033
QUEUE_BATCH_ID = "pk_msggame-B004"
BLOCK_ID = 0
QUEUE_VISIBLE_START = 0
QUEUE_VISIBLE_STOP = 67
OWNED_RECORD_IDS = tuple(range(1863, 1935))
HIDDEN_EMPTY_RECORD_IDS = (1888, 1889, 1895, 1897, 1899)
VISIBLE_RECORD_IDS = tuple(
    record_id
    for record_id in OWNED_RECORD_IDS
    if record_id not in HIDDEN_EMPTY_RECORD_IDS
)
OWNED_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in OWNED_RECORD_IDS
)
VISIBLE_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in VISIBLE_RECORD_IDS
)
HIDDEN_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in HIDDEN_EMPTY_RECORD_IDS
)
TARGET_COORDINATES = tuple(
    f"{BLOCK_ID}:{record_id}:0" for record_id in VISIBLE_RECORD_IDS
)
PK_RECORD_COUNT = 21751

EXPECTED_PK_JP_ALL = (
    "してくだされ",
    "してください",
    "してくだされ",
    "せ",
    "しません",
    "せぬ",
    "いたしません",
    "いたしませぬ",
    "しません",
    "いたさぬ",
    "せぬ",
    "しなければ",
    "せねば",
    "しなくては",
    "しなければ",
    "しなくては",
    "しなければ",
    "せねば",
    "してください",
    "せよ",
    "してくださいませ",
    "してくだされ",
    "してください",
    "してくだされ",
    "するがよい",
    "",
    "",
    "よ",
    "ぞ",
    "よ",
    "ぞ",
    "ぞ",
    "",
    "ぞ",
    "",
    "ぞ",
    "",
    "ぞ",
    "ぞ",
    "しましょう",
    "そう",
    "しましょう",
    "しましょう",
    "しましょう",
    "しましょう",
    "そう",
    "です",
    "ですぞ",
    "でございますよ",
    "でございますぞ",
    "ですよ",
    "でござるぞ",
    "だぞ",
    "ました",
    "た",
    "ました",
    "ました",
    "ました",
    "ました",
    "た",
    "きました",
    "いた",
    "きました",
    "きました",
    "きました",
    "きました",
    "いた",
    "です",
    "だ",
    "でございます",
    "にございます",
    "です",
)
TRANSLATION_POLICY_ALL = (
    "해 주시오",
    "해 주십시오",
    "해 주시오",
    "하라",
    "하지 않습니다",
    "하지 않는다",
    "하지 않사옵니다",
    "하지 않사옵니다",
    "하지 않습니다",
    "하지 않소",
    "하지 않는다",
    "하지 않으면",
    "해야만",
    "하지 않으면",
    "하지 않으면",
    "하지 않으면",
    "하지 않으면",
    "해야만",
    "해 주십시오",
    "하라",
    "해 주시옵소서",
    "해 주시오",
    "해 주십시오",
    "해 주시오",
    "하라",
    "",
    "",
    "여",
    "다",
    "여",
    "다",
    "다",
    "",
    "다",
    "",
    "다",
    "",
    "다",
    "다",
    "합시다",
    "하자",
    "합시다",
    "합시다",
    "합시다",
    "합시다",
    "하자",
    "입니다",
    "입니다",
    "이옵니다",
    "이옵니다",
    "입니다",
    "이오",
    "이다",
    "했습니다",
    "했다",
    "했습니다",
    "했습니다",
    "했습니다",
    "했습니다",
    "했다",
    "습니다",
    "다",
    "습니다",
    "습니다",
    "습니다",
    "습니다",
    "다",
    "입니다",
    "다",
    "이옵니다",
    "이옵니다",
    "입니다",
)
TRANSLATIONS_BY_RECORD = {
    record_id: TRANSLATION_POLICY_ALL[record_id - OWNED_RECORD_IDS[0]]
    for record_id in VISIBLE_RECORD_IDS
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

EXPECTED_SEQUENCE_EVIDENCE = {
    "tail7": (
        1863,
        7,
        (1802,),
        (1863,),
        "A6CB3A7B8240A967D4DCD7653250FBDCB49E4E3BC73B18B56C5660F4F0A73F8B",
    ),
    "middle53": (
        1870,
        53,
        (1809,),
        (1870,),
        "F97748F6B1A0A498290440E5EA8F6533210ECAB137188C684EA0EEE535DE1ABC",
    ),
    "insert7": (
        1923,
        7,
        (),
        (1923,),
        "19163AAF856590A09579CC3BB4746069E3B2B9C19E614B8522C74C3E008D5F36",
    ),
    "right_full7": (
        1930,
        7,
        (1862,),
        (1930,),
        "65D9A7F3E17282FF7BDD77E12641E00895502B0815ADB6CCD7DBD8F62FD76725",
    ),
}
EXPECTED_MAPPING_SHA256 = (
    "CAF292A12A9BE8F69716CE02F26C29067E5DC58771F3663F107BE07836C99A84"
)
EXPECTED_ALL_POLICY_SHA256 = (
    "19E8AB7CAA59A157C87AAD0D2BFBB2EA4F7EB7C573B94D12C0F5FABC29AF836D"
)
EXPECTED_VISIBLE_POLICY_SHA256 = (
    "B60A49FF79C4A5C37DA3BDDEC4814A95B68EC6DC89BDFCAF80CE293AE7C58DBB"
)
EXPECTED_CHANGED_LITERAL_COUNT = 18

PK_TARGET_ARCHIVE_DIGESTS = {
    "pk_jp": "83E49A8AA5956B15971E8BFBFEC8B7DA88AC3FD93E40957D9AC5D50BAF66311F",
    "pk_current": "7FD1A3BCCAEAB46AD8438C5F8699B9EBF1DBC119D332179AC2932B8013667F08",
    "pk_sc": "7A8720C4A72661B6B61F03FF1E91509828A10C1A1648FE34BE6B18262FDB118B",
    "pk_tc": "7A8720C4A72661B6B61F03FF1E91509828A10C1A1648FE34BE6B18262FDB118B",
    "pk_en": "7A8720C4A72661B6B61F03FF1E91509828A10C1A1648FE34BE6B18262FDB118B",
}
PK_FULL_ARCHIVE_DIGESTS = {
    "pk_jp": "C04D4E4358EECB64955C06D74904DC8228C853184A3A472AA9EEF18CF5DB00A7",
    "pk_current": "BA1F05481B80BA4C63DD419EB20E4DA11D8BF7A0F9307A9E2EC4468B787E6070",
    "pk_sc": "73D176F741AB40A75029C716AD8EC14766A25A3ABDA93782E4FF7E413B1F4190",
    "pk_tc": "73D176F741AB40A75029C716AD8EC14766A25A3ABDA93782E4FF7E413B1F4190",
    "pk_en": "73D176F741AB40A75029C716AD8EC14766A25A3ABDA93782E4FF7E413B1F4190",
}
PK_HIDDEN_ARCHIVE_DIGEST = (
    "7C92AA396FD11DEA1AB5FECF8FC749B514B356C3AA6A36E23D7720273CDACE53"
)

FULL_PK_GROUPS = {
    484: tuple(range(1860, 1867)),
    490: tuple(range(1867, 1874)),
    496: tuple(range(1874, 1881)),
    502: tuple(range(1881, 1888)),
    508: tuple(range(1888, 1895)),
    514: tuple(range(1895, 1902)),
    1162: tuple(range(1902, 1909)),
    520: tuple(range(1909, 1916)),
    538: tuple(range(1916, 1923)),
    544: tuple(range(1923, 1930)),
    550: tuple(range(1930, 1937)),
}
EXPECTED_ROOT_CLOSURES = {
    root: tuple(range(root, root + 6)) + record_ids
    for root, record_ids in FULL_PK_GROUPS.items()
}
RECORD_TO_ROOT = {
    record_id: root
    for root, record_ids in FULL_PK_GROUPS.items()
    for record_id in record_ids
    if record_id in OWNED_RECORD_IDS
}
EMPTY_CANONICAL_SHA256 = (
    "4F53CDA18C2BAA0C0354BB5F9A3ECBE5ED12AB4D8E11BA873C2F11161202B945"
)
NO_CALL_EVIDENCE = (
    (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    (0, EMPTY_CANONICAL_SHA256, 0, EMPTY_CANONICAL_SHA256),
    (
        0,
        EMPTY_CANONICAL_SHA256,
        0,
        EMPTY_CANONICAL_SHA256,
    ),
)
EXPECTED_CALL_EVIDENCE = {
    484: NO_CALL_EVIDENCE,
    490: (
        (
            5,
            "57B15B841D20E29FE68AC5330F4F2B21022B299F02661F95C680F3AA98C59F56",
            2,
            "F2702461A894923FE043A04772F32655252BDFA60E91400637116B7E9D1D55C1",
        ),
        (
            4,
            "957E943F328D970916299DCED079440AB30C3FDD3BFA1CA8122FE03409520461",
            2,
            "F2702461A894923FE043A04772F32655252BDFA60E91400637116B7E9D1D55C1",
        ),
        (
            1,
            "58E461249C0EA771CF9097D1691AA72321AF7180C2000CC03ECB599CD2BA1B3B",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    496: (
        (
            32,
            "B66DEB0D617DC19D71FE01A1E6831B56E1014D7833131CB5B243564DE9F0642C",
            1,
            "0C7036C20B9349AEA15DC923038FE2847A3693DB8DB630F631ABD1397FB892AB",
        ),
        (
            18,
            "4EEE5D03185AFBC4B24D96BBDB4AD61E77C3343A332342368F9BFE08A9CEA5C3",
            1,
            "0C7036C20B9349AEA15DC923038FE2847A3693DB8DB630F631ABD1397FB892AB",
        ),
        (
            14,
            "23EED4A8292528CB6CF05E08B4024331B77B83D113CFEB063ECCAEC004668F43",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    502: (
        (
            6,
            "5233500046814B5DF0BCD7561D951CA31CB804660D7B8A7D299B39875A546A7B",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
        (
            5,
            "789990A4D9F2EFE99DE170DC654F41120D35DDDB19242AFAA37D4A8C4691C1D5",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
        (
            1,
            "3611259BB2D9CFAC4413A51DA832CB6CBC7595DCA92F847DA419629D39C91A30",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    508: (
        (
            81,
            "239C6AEECF89179CE52E20A4E8EA5A275D97E6887660DCF728F9C9E39E006845",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
        (
            74,
            "1E438EB37822CD77DB22FFF95CBBFB7B767D1F5EC352FCD6D9231BD9C5806675",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
        (
            7,
            "4336EAC6252CE97413AA26CE9208ECEDE70284FB4A00787637FCDCA7B6371EB2",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    514: (
        (
            86,
            "A540ADF91590712BF0371AEB09E81C89A3791D9F7019BC464C10AD2FE2C5DBAE",
            2,
            "ED3BCAABD4FD6A3B070BF8E57DF97D00C8D4002DFD9267CE57632EC72F4CF3CF",
        ),
        (
            56,
            "BCEEC3DCA1FC93A4FA75ABBF7A83A1840A20FE19991E1BBF9B5C680AE1A95508",
            1,
            "E2D2BBEAAC66C3A78734AACA9EC51A53CC18B9A779F7E3EF83CC32AD00EB0F58",
        ),
        (
            30,
            "1988D80F412D02BFAE8AA009F0BEAD3D45F9E66FC5BCFE0520865F13F1331409",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    1162: (
        (
            66,
            "19009DAF513A7F7012C7C36F6119C66D3B29BF5CD41E837ED567960219C49B0C",
            7,
            "686D6958D5835BD9BC7FFEB61420D8447F3865978FE9C03469B9FB1A793CE220",
        ),
        (
            61,
            "39FD2200CF7CBEE8A5A17D6CEACA565657CB986A9D225E550EFB1F5B71D10C01",
            7,
            "686D6958D5835BD9BC7FFEB61420D8447F3865978FE9C03469B9FB1A793CE220",
        ),
        (
            5,
            "FD5DB1CECCCE4F18014C127278B257215AD016C5C601A4591E65EEDF33C9CCF4",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    520: (
        (
            16,
            "FAB34EE9BD5975E4009AE25E0FC88DB7F5A668CA67614410DE58EF6257D8CC29",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
        (
            10,
            "157AB361D48459797D840072CCD9C14845FC7C9D641199285BEF96E2BFB0C253",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
        (
            6,
            "4A9F53D75AC143FE626C92C26B7D92CCB7FD6ABE843A273E742B79795025B779",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    538: (
        (
            338,
            "7DE5AB9890CD2D60FB35B0CF41B378C6FE11616E11CD6ACA472DBAF139D386B3",
            135,
            "A4DE31C47746C5B1B44AA39839286DFD6F1F26D5C51646A4B4A8A2B57310DE17",
        ),
        (
            277,
            "660642B917276DDA6ECF9285D488A3A718ED7AD8DD1066A486E2F0D13F99C946",
            97,
            "8A329767AC2C12E6BABE2700E35F4AEC70776FF6D63506E33CD9BB2A0E93E666",
        ),
        (
            61,
            "15207F8E943C38AC47C656728D1ECC3CDE486CD4899D5E37A8F0AD123D0912D5",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    544: (
        (
            4,
            "5E9C3ECAEB5769F450A2F1B1D62CBBE4FA973F1350AD808A058AAA9448BB3195",
            2,
            "6CCB548B92AE4885F17721D48216E022C52554A8FD0BEF969B9E270E67D516D4",
        ),
        (
            4,
            "5E9C3ECAEB5769F450A2F1B1D62CBBE4FA973F1350AD808A058AAA9448BB3195",
            2,
            "6CCB548B92AE4885F17721D48216E022C52554A8FD0BEF969B9E270E67D516D4",
        ),
        (
            0,
            EMPTY_CANONICAL_SHA256,
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
    550: (
        (
            177,
            "C09E1E720591004E18605570B5F72C14E16C2319545ED73A431C9F0279AFFF81",
            25,
            "8FC0F951532CDB6FE34EBB50C3E2BA9B32CEBCDDE0682066CFC3E73E843024E8",
        ),
        (
            169,
            "7E968264996B6C9117AB8D8D206B9F8AB267AD648063C87F57DD7EF0E53146C1",
            24,
            "25459FA80B093303165E6A8C6BE75D1033679FBA4DC2840CD5ADFE0D296115F8",
        ),
        (
            8,
            "25DCAAB071AE688936645475BCE57DF172918488A0E2D853B8E1A853EFE44068",
            0,
            EMPTY_CANONICAL_SHA256,
        ),
    ),
}
PK_TARGET_EDGE_EVIDENCE = (
    72,
    "70132EAE1E7F5B23EB672E245E68A9C2682773DB8CBE5535B84EBBD469DF7BE3",
)
PK_VISIBLE_EDGE_EVIDENCE = (
    67,
    "F9666BEF5F03E465BD284965FB7D8EB297D0F4BA94AB46500FD303295A9025D8",
)
PK_FULL_EDGE_EVIDENCE = (
    77,
    "14946816F38114BE7B28CDA9230DE9D0E4D442D1CECC29EF4AAA0786FCDF4164",
)
MORPHOLOGY_014C_RE = re.compile(b"\x01\x4C(.{4})", re.DOTALL)
EXPECTED_014C_OVERLAP = ((15, 25, 0, 65, 84213762),)

LEFT_ROOT484_FULL_IDS = FULL_PK_GROUPS[484]
LEFT_ROOT484_FULL_JP = (
    "してください",
    "せ",
    "してくださいませ",
    "してくだされ",
    "してください",
    "してくだされ",
    "せ",
)
LEFT_ROOT484_FULL_CURRENT = (
    "해 주십시오",
    "세",
    "해 주시옵소서",
    "해 주시오",
    "해 주십시오",
    "해 주시오",
    "세",
)
LEFT_ROOT484_FULL_POLICY = (
    "해 주십시오",
    "하라",
    "해 주시옵소서",
    "해 주시오",
    "해 주십시오",
    "해 주시오",
    "하라",
)
RIGHT_ROOT550_FULL_IDS = FULL_PK_GROUPS[550]
RIGHT_ROOT550_FULL_JP = (
    "です",
    "だ",
    "でございます",
    "にございます",
    "です",
    "でござる",
    "じゃ",
)
RIGHT_ROOT550_FULL_CURRENT = (
    "입니다",
    "다",
    "이옵니다",
    "이옵니다",
    "입니다",
    "이오",
    "이니라",
)
RIGHT_ROOT550_FULL_POLICY = RIGHT_ROOT550_FULL_CURRENT

INSERTED_ROOT = 544
INSERTED_RECORD_IDS = FULL_PK_GROUPS[INSERTED_ROOT]
INSERTED_JP = (
    "きました",
    "いた",
    "きました",
    "きました",
    "きました",
    "きました",
    "いた",
)
INSERTED_CURRENT = (
    "왔습니다",
    "있었다",
    "왔습니다",
    "왔습니다",
    "왔습니다",
    "왔습니다",
    "있었다",
)
INSERTED_POLICY = (
    "습니다",
    "다",
    "습니다",
    "습니다",
    "습니다",
    "습니다",
    "다",
)
INSERTED_CALL_SITES = (
    "6:4607:2:0",
    "6:4623:2:0",
    "6:4629:3:0",
    "15:2553:2:0",
)
INSERTED_CURRENT_CALLER_EVIDENCE = (
    (
        "6:4607:2:0",
        "2DDCE59CAC47BB19D037EDDA347CEB5959C82D95CA6DDB1DFAA29BFC932D09EA",
        "놀랍군",
        "놀랐",
        True,
    ),
    (
        "6:4623:2:0",
        "07AC34B1808256B915ABA5A0A07FA17E90DBF8B806973B7B003EF9A411095641",
        "들었",
        "들었",
        False,
    ),
    (
        "6:4629:3:0",
        "234EA1B500BC4101109397234C8AD7915CBCA4C71FC87E323643B9CEDAF9DA65",
        "들었",
        "들었",
        False,
    ),
    (
        "15:2553:2:0",
        "221E31E7180EB4603D275AA91F112B4D036AFC4D9F038AC9F1323A4BA6CE3A96",
        "두었습니다",
        "두었",
        True,
    ),
)

ROOT_ASSEMBLY_PLAN = {
    484: "caller action stem + respectful/plain request ending",
    490: "caller action predicate + complete negative ending",
    496: "caller action predicate + conditional/obligation ending",
    502: "caller action noun + imperative ending",
    508: "sentence-final or vocative particle",
    514: "emphatic sentence-final particle",
    1162: "caller action predicate + volitional ending",
    520: "caller nominal predicate + emphatic copular ending",
    538: "caller action predicate + complete past ending",
    544: "PK-only past allomorph; Korean caller carries past stem and root supplies polite/plain ending",
    550: "caller nominal predicate + copular ending",
}
BASIS = (
    "review_queue_pk_msggame_B004_zero_based_visible_ordinals0_66_"
    "pristine_pk_pc_jp_sole_translation_authority_block0_records1863_"
    "1934_72_records_67_visible_hidden_empty1888_1889_1895_1897_1899_"
    "raw_preserved_no_decisions_independent_unique_reverse_search_tail7_"
    "Base1802_middle53_Base1809_pk_only_inserted_root544_no_Base_hit_"
    "right_full7_Base1862_piecewise_plus61_plus68_mapping_exact_jp_"
    "current_sc_tc_full_records_blank_en_target_full_hidden_digests_"
    "left_root484_cross_S1032_right_root550_full_cross_next_actual_014a_"
    "0143_fixed_flatten_014c_guards_pk_only_kimashita_ita_past_allomorph_"
    "corrected_from_lexical_came_was_to_polite_plain_ending_matrix_"
    "source_free_current_caller_evidence_future_past_stem_rewrite_pending_"
    "negative_conditional_imperative_particle_"
    "volitional_copular_past_register_matrices_historic_and_switch_"
    "Korean_not_used_skeleton_outside_hidden_reverse_exact_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return tuple(
        literal.text for literal in ENGINE.parse_record_literals(records[key])
    )


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return HELPERS.record_gaps(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return BASE_MIDDLE.archive_records(prepared)


def record_signature(
    records: dict[tuple[int, int], Any],
    start: int,
    count: int,
) -> tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]:
    return tuple(
        (
            literal_texts(records, (BLOCK_ID, record_id)),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records[(BLOCK_ID, record_id)])
            ),
        )
        for record_id in range(start, start + count)
    )


def sequence_starts(
    records: dict[tuple[int, int], Any],
    sequence: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...],
) -> tuple[int, ...]:
    maximum = max(
        record_id
        for block_id, record_id in records
        if block_id == BLOCK_ID
    )
    count = len(sequence)
    return tuple(
        start
        for start in range(maximum - count + 2)
        if all(
            (BLOCK_ID, start + ordinal) in records
            for ordinal in range(count)
        )
        and record_signature(records, start, count) == sequence
    )


def assert_queue_contract(prepared: Any) -> None:
    rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        target["coordinate"]
        for row in rows
        for target in row["target_literals"]
        if target["visible"]
    )
    hidden = tuple(
        target["coordinate"]
        for row in rows
        for target in row["target_literals"]
        if not target["visible"]
    )
    if (
        len(rows) != 205
        or rows[0]["record_coordinate"] != "0:1863"
        or rows[-1]["record_coordinate"] != "0:2067"
        or len(visible) != 200
        or visible[QUEUE_VISIBLE_START:QUEUE_VISIBLE_STOP]
        != TARGET_COORDINATES
        or hidden
        != tuple(
            f"{BLOCK_ID}:{record_id}:0"
            for record_id in HIDDEN_EMPTY_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} private queue ordinal contract drifted"
        )


def discover_mapping(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[int, int | None]:
    pk_jp = records_by_label["pk_jp"]
    base_jp = records_by_label["base_jp"]
    for name, evidence in EXPECTED_SEQUENCE_EVIDENCE.items():
        pk_start, count, expected_base_hits, expected_pk_hits, digest = evidence
        sequence = record_signature(pk_jp, pk_start, count)
        if (
            HELPERS.canonical_sha256(sequence) != digest
            or sequence_starts(base_jp, sequence) != expected_base_hits
            or sequence_starts(pk_jp, sequence) != expected_pk_hits
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent reverse search "
                f"drifted: {name}"
            )

    mapping: dict[int, int | None] = {}
    for pk_record_id in OWNED_RECORD_IDS:
        if pk_record_id <= 1922:
            mapping[pk_record_id] = pk_record_id - 61
        elif pk_record_id <= 1929:
            mapping[pk_record_id] = None
        else:
            mapping[pk_record_id] = pk_record_id - 68
    if (
        HELPERS.canonical_sha256(
            [
                [pk_record_id, base_record_id]
                for pk_record_id, base_record_id in mapping.items()
            ]
        )
        != EXPECTED_MAPPING_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} mapping digest drifted")
    return mapping


def assert_sources_and_mapping(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    mapping: dict[int, int | None],
) -> None:
    full_keys = tuple(
        (BLOCK_ID, record_id) for record_id in range(1860, 1937)
    )
    for label, expected_digest in PK_TARGET_ARCHIVE_DIGESTS.items():
        if (
            GENERAL.subset_digest(
                records_by_label[label],
                OWNED_RECORD_KEYS,
            )
            != expected_digest
            or GENERAL.subset_digest(
                records_by_label[label],
                full_keys,
            )
            != PK_FULL_ARCHIVE_DIGESTS[label]
            or GENERAL.subset_digest(
                records_by_label[label],
                HIDDEN_RECORD_KEYS,
            )
            != PK_HIDDEN_ARCHIVE_DIGEST
        ):
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} digest drifted"
            )

    for ordinal, pk_record_id in enumerate(OWNED_RECORD_IDS):
        pk_key = (BLOCK_ID, pk_record_id)
        if (
            literal_texts(records_by_label["pk_jp"], pk_key)
            != (EXPECTED_PK_JP_ALL[ordinal],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine PK source drifted: {pk_key}"
            )
        for label in PK_TARGET_ARCHIVE_DIGESTS:
            if (
                len(literal_texts(records_by_label[label], pk_key)) != 1
                or gap_bytes(records_by_label[label][pk_key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} PK skeleton drifted: "
                    f"{label}/{pk_key}"
                )
        if any(
            literal_texts(records_by_label[label], pk_key) != ("",)
            for label in ("pk_sc", "pk_tc", "pk_en")
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK context drifted: {pk_key}"
            )

        base_record_id = mapping[pk_record_id]
        if base_record_id is None:
            continue
        base_key = (BLOCK_ID, base_record_id)
        for language in ("jp", "current", "sc", "tc"):
            if (
                records_by_label[f"pk_{language}"][pk_key].data
                != records_by_label[f"base_{language}"][base_key].data
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} exact PK/Base {language} "
                    f"mapping drifted: {pk_key}/{base_key}"
                )

    for record_id in HIDDEN_EMPTY_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        if (
            any(
                literal_texts(records_by_label[label], key) != ("",)
                for label in PK_TARGET_ARCHIVE_DIGESTS
            )
            or ("pk_msggame", BLOCK_ID, record_id, 0)
            in prepared.visible_targets
            or ENGINE.is_visible_translation_candidate("")
        ):
            raise RuntimeError(
                f"segment {SEGMENT} hidden empty drifted: {record_id}"
            )

    actual_inserted_jp = tuple(
        literal_texts(
            records_by_label["pk_jp"],
            (BLOCK_ID, record_id),
        )[0]
        for record_id in INSERTED_RECORD_IDS
    )
    actual_inserted_current = tuple(
        literal_texts(
            records_by_label["pk_current"],
            (BLOCK_ID, record_id),
        )[0]
        for record_id in INSERTED_RECORD_IDS
    )
    if (
        actual_inserted_jp != INSERTED_JP
        or actual_inserted_current != INSERTED_CURRENT
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK-only insertion drifted"
        )


def assert_runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    target_ids = set(OWNED_RECORD_IDS)
    visible_ids = set(VISIBLE_RECORD_IDS)
    full_ids = set(range(1860, 1937))
    if {
        record_id
        for record_ids in FULL_PK_GROUPS.values()
        for record_id in record_ids
    } != full_ids:
        raise RuntimeError(
            f"segment {SEGMENT} full runtime universe drifted"
        )

    for label in ("pk_jp", "pk_current"):
        records = records_by_label[label]
        for name, ids, evidence in (
            ("target", target_ids, PK_TARGET_EDGE_EVIDENCE),
            ("visible", visible_ids, PK_VISIBLE_EDGE_EVIDENCE),
            ("full", full_ids, PK_FULL_EDGE_EVIDENCE),
        ):
            rows = BASE_MIDDLE.GRAPH.incoming_jump_rows(records, ids)
            if (
                len(rows) != evidence[0]
                or BASE_MIDDLE.digest_rows(rows) != evidence[1]
                or {row[4] for row in rows} != ids
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} independent {label} "
                    f"{name} 014A evidence drifted"
                )
        graph = HELPERS.graph_edges(records)
        for root, expected_closure in EXPECTED_ROOT_CLOSURES.items():
            if (
                tuple(sorted(HELPERS.graph_closure(graph, root)))
                != expected_closure
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} independent {label} "
                    f"closure drifted: {root}"
                )

    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    for root, expected in EXPECTED_CALL_EVIDENCE.items():
        source_calls = HELPERS.root_call_sites(source, root)
        current_calls = HELPERS.root_call_sites(current, root)
        source_fixed = HELPERS.fixed_following_blockers(source, root)
        current_fixed = HELPERS.fixed_following_blockers(current, root)
        source_only = tuple(
            sorted(set(source_calls) - set(current_calls))
        )
        current_only = tuple(
            sorted(set(current_calls) - set(source_calls))
        )
        actual = (
            (
                len(source_calls),
                HELPERS.canonical_sha256(source_calls),
                len(source_fixed),
                HELPERS.canonical_sha256(source_fixed),
            ),
            (
                len(current_calls),
                HELPERS.canonical_sha256(current_calls),
                len(current_fixed),
                HELPERS.canonical_sha256(current_fixed),
            ),
            (
                len(source_only),
                HELPERS.canonical_sha256(source_only),
                len(current_only),
                HELPERS.canonical_sha256(current_only),
            ),
        )
        if actual != expected:
            raise RuntimeError(
                f"segment {SEGMENT} root {root} "
                "0143/fixed/flatten evidence drifted"
            )

    for label in ("pk_jp", "pk_current"):
        valid: list[tuple[int, int, int, int, int]] = []
        overlapped: list[tuple[int, int, int, int, int]] = []
        for (block_id, record_id), record in sorted(
            records_by_label[label].items()
        ):
            for gap_id, gap in enumerate(gap_bytes(record)):
                jump_spans = [
                    range(match.start(), match.end())
                    for match in (
                        BASE_MIDDLE.GRAPH.MORPHOLOGY_JUMP_RE.finditer(gap)
                    )
                ]
                for match in MORPHOLOGY_014C_RE.finditer(gap):
                    row = (
                        block_id,
                        record_id,
                        gap_id,
                        match.start(),
                        struct.unpack("<I", match.group(1))[0],
                    )
                    if any(
                        match.start() in span for span in jump_spans
                    ):
                        overlapped.append(row)
                    else:
                        valid.append(row)
        if valid or tuple(overlapped) != EXPECTED_014C_OVERLAP:
            raise RuntimeError(
                f"segment {SEGMENT} independent {label} "
                "014C evidence drifted"
            )


def assert_boundaries(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    actual_left_jp = tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_ROOT484_FULL_IDS
    )
    actual_left_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in LEFT_ROOT484_FULL_IDS
    )
    actual_right_jp = tuple(
        literal_texts(source, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_ROOT550_FULL_IDS
    )
    actual_right_current = tuple(
        literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in RIGHT_ROOT550_FULL_IDS
    )
    if (
        actual_left_jp != LEFT_ROOT484_FULL_JP
        or actual_left_current != LEFT_ROOT484_FULL_CURRENT
        or LEFT_PK.RIGHT_BOUNDARY_IDS != LEFT_ROOT484_FULL_IDS
        or LEFT_PK.RIGHT_BOUNDARY_JP != LEFT_ROOT484_FULL_JP
        or LEFT_PK.RIGHT_BOUNDARY_CURRENT
        != LEFT_ROOT484_FULL_CURRENT
        or LEFT_PK.RIGHT_BOUNDARY_POLICY
        != LEFT_ROOT484_FULL_POLICY
        or set(LEFT_PK.RECORD_IDS).intersection(OWNED_RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1032/root484 boundary drifted"
        )
    if (
        actual_right_jp != RIGHT_ROOT550_FULL_JP
        or actual_right_current != RIGHT_ROOT550_FULL_CURRENT
        or RIGHT_ROOT550_FULL_POLICY
        != BASE_MIDDLE.TRANSLATION_POLICY_BY_ROOT[538]
        or set(RIGHT_ROOT550_FULL_IDS).intersection(OWNED_RECORD_IDS)
        != set(range(1930, 1935))
    ):
        raise RuntimeError(
            f"segment {SEGMENT} right root550 boundary drifted"
        )


def assert_completed_base_policy(
    prepared: Any,
    mapping: dict[int, int | None],
) -> None:
    rows_by_coordinate: dict[str, dict[str, object]] = {}
    for path, expected_sha256 in BASE_DECISIONS:
        if (
            not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest().upper()
            != expected_sha256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base decision drifted: "
                f"{path.name}"
            )
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
        )
        for line in path.read_text(encoding="utf-8").splitlines():
            if line:
                row = json.loads(line)
                rows_by_coordinate[str(row["coordinate"])] = row

    for pk_record_id in VISIBLE_RECORD_IDS:
        base_record_id = mapping[pk_record_id]
        if base_record_id is None:
            continue
        coordinate = f"{BLOCK_ID}:{base_record_id}:0"
        row = rows_by_coordinate.get(coordinate)
        if (
            row is None
            or row["resource"] != "base_msggame"
            or row["semantic_review"] != "approved"
            or row["translation"]
            != TRANSLATIONS_BY_RECORD[pk_record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} completed Base semantic "
                f"policy drifted: {coordinate}"
            )


def assert_inserted_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source = records_by_label["pk_jp"]
    current = records_by_label["pk_current"]
    if (
        tuple(HELPERS.root_call_sites(source, INSERTED_ROOT))
        != INSERTED_CALL_SITES
        or tuple(HELPERS.root_call_sites(current, INSERTED_ROOT))
        != INSERTED_CALL_SITES
        or INSERTED_POLICY
        != (
            "습니다",
            "다",
            "습니다",
            "습니다",
            "습니다",
            "습니다",
            "다",
        )
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in INSERTED_RECORD_IDS
        )
        != INSERTED_POLICY
    ):
        raise RuntimeError(
            f"segment {SEGMENT} PK-only past policy drifted"
        )
    for (
        call_site,
        expected_sha256,
        current_suffix,
        future_stem,
        rewrite_required,
    ) in INSERTED_CURRENT_CALLER_EVIDENCE:
        block_id, record_id, gap_id, _ = (
            int(value) for value in call_site.split(":")
        )
        literals = ENGINE.parse_record_literals(
            current[(block_id, record_id)]
        )
        if gap_id == 0:
            raise RuntimeError(
                f"segment {SEGMENT} PK-only current caller "
                f"position drifted: {call_site}"
            )
        current_left = literals[gap_id - 1].text
        if (
            hashlib.sha256(
                current_left.encode("utf-16le")
            ).hexdigest().upper()
            != expected_sha256
            or not current_left.endswith(current_suffix)
            or rewrite_required != (current_suffix != future_stem)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} PK-only current caller evidence "
                f"drifted: {call_site}"
            )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        len(OWNED_RECORD_IDS) != 72
        or len(VISIBLE_RECORD_IDS) != 67
        or len(HIDDEN_EMPTY_RECORD_IDS) != 5
        or set(VISIBLE_RECORD_IDS)
        != set(OWNED_RECORD_IDS) - set(HIDDEN_EMPTY_RECORD_IDS)
        or len(EXPECTED_PK_JP_ALL) != 72
        or len(TRANSLATION_POLICY_ALL) != 72
        or HELPERS.canonical_sha256(TRANSLATION_POLICY_ALL)
        != EXPECTED_ALL_POLICY_SHA256
        or HELPERS.canonical_sha256(
            tuple(
                TRANSLATIONS_BY_RECORD[record_id]
                for record_id in VISIBLE_RECORD_IDS
            )
        )
        != EXPECTED_VISIBLE_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )
    BASE_TAIL.assert_semantics(dict(BASE_TAIL.RAW_TRANSLATIONS))
    BASE_MIDDLE.assert_semantics(dict(BASE_MIDDLE.RAW_TRANSLATIONS))
    assert_inserted_semantics(records_by_label)
    for record_id in HIDDEN_EMPTY_RECORD_IDS:
        if (
            TRANSLATION_POLICY_ALL[
                record_id - OWNED_RECORD_IDS[0]
            ]
            != ""
        ):
            raise RuntimeError(
                f"segment {SEGMENT} hidden policy drifted: {record_id}"
            )
    for coordinate, translation in TRANSLATIONS.items():
        if (
            "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str]:
    pk = prepared.resources["pk_msggame"]
    current = records_by_label["pk_current"]
    replacements = {
        (BLOCK_ID, record_id, 0): TRANSLATIONS_BY_RECORD[record_id]
        for record_id in VISIBLE_RECORD_IDS
    }
    reverse = {
        key: literal_texts(current, key[:2])[key[2]]
        for key in replacements
    }
    candidate = ENGINE.rebuild_packed_with_literals(
        pk.current_blob,
        replacements,
    )
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(candidate).archive
    )
    if (
        len(current) != PK_RECORD_COUNT
        or len(candidate_records) != PK_RECORD_COUNT
        or set(replacements)
        != {
            (BLOCK_ID, record_id, 0)
            for record_id in VISIBLE_RECORD_IDS
        }
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate universe drifted"
        )
    target_keys = set(VISIBLE_RECORD_KEYS)
    for key, record in current.items():
        if (
            key not in target_keys
            and candidate_records[key].data != record.data
        ):
            raise RuntimeError(
                f"segment {SEGMENT} changed out-of-scope record: {key}"
            )
    for record_id in VISIBLE_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        if (
            gap_bytes(candidate_records[key]) != gap_bytes(current[key])
            or literal_texts(candidate_records, key)
            != (TRANSLATIONS_BY_RECORD[record_id],)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} candidate terminal drifted: {key}"
            )
    for key in HIDDEN_RECORD_KEYS:
        if candidate_records[key].data != current[key].data:
            raise RuntimeError(
                f"segment {SEGMENT} hidden raw record changed: {key}"
            )
    reversed_blob = ENGINE.rebuild_packed_with_literals(
        candidate,
        reverse,
    )
    if reversed_blob != pk.current_blob:
        raise RuntimeError(
            f"segment {SEGMENT} reverse overlay is not byte-exact"
        )
    return (
        candidate,
        hashlib.sha256(candidate).hexdigest().upper(),
    )


def build_rows() -> tuple[
    Any,
    list[dict[str, object]],
    bytes,
    str,
    dict[int, int | None],
    int,
]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    assert_queue_contract(prepared)
    records_by_label = archive_records(prepared)
    mapping = discover_mapping(records_by_label)
    assert_sources_and_mapping(prepared, records_by_label, mapping)
    assert_runtime_evidence(records_by_label)
    assert_boundaries(records_by_label)
    assert_completed_base_policy(prepared, mapping)
    assert_semantics(records_by_label)

    current = records_by_label["pk_current"]
    for coordinate, translation in TRANSLATIONS.items():
        _, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        current_text = literal_texts(
            current,
            (BLOCK_ID, record_id),
        )[literal_id]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} protected line drifted: "
                f"{coordinate}"
            )

    candidate, candidate_sha256 = build_candidate(
        prepared,
        records_by_label,
    )
    rows: list[dict[str, object]] = []
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        root = RECORD_TO_ROOT[record_id]
        calls = EXPECTED_CALL_EVIDENCE[root]
        base_record_id = mapping[record_id]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target[
                    "source_record_raw_sha256"
                ],
                "current_ko_utf16le_sha256": target[
                    "current_ko_utf16le_sha256"
                ],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "runtime_assembly_evidence": {
                    "root": root,
                    "full_terminal_record_ids": list(
                        FULL_PK_GROUPS[root]
                    ),
                    "owned_terminal_record_ids": [
                        value
                        for value in FULL_PK_GROUPS[root]
                        if value in OWNED_RECORD_IDS
                    ],
                    "full_graph_closure_record_ids": list(
                        EXPECTED_ROOT_CLOSURES[root]
                    ),
                    "base_semantic_record_id": base_record_id,
                    "mapping_class": (
                        "pk_only_inserted_past_allomorph"
                        if base_record_id is None
                        else (
                            "unique_reverse_plus61"
                            if record_id <= 1922
                            else "unique_reverse_plus68"
                        )
                    ),
                    "source_call_count": calls[0][0],
                    "current_call_count": calls[1][0],
                    "source_fixed_following_count": calls[0][2],
                    "current_fixed_following_count": calls[1][2],
                    "source_calls_flattened_in_current": calls[2][0],
                    "current_only_calls": calls[2][2],
                    "incoming_jump_graph_guarded": True,
                    "valid_incoming_014c_count": 0,
                    "hidden_empty_records_preserved": list(
                        HIDDEN_EMPTY_RECORD_IDS
                    ),
                    "assembly_plan": ROOT_ASSEMBLY_PLAN[root],
                    **(
                        {
                            "translation_rationale":
                            "root544 supplies only the polite/plain "
                            "ending; the Korean caller must carry the "
                            "past stem",
                            "source_free_current_caller_evidence": [
                                {
                                    "call_site": call_site,
                                    "current_left_context_utf16le_sha256":
                                    context_sha256,
                                    "current_left_suffix": current_suffix,
                                    "future_caller_past_stem": future_stem,
                                    "rewrite_required": rewrite_required,
                                }
                                for (
                                    call_site,
                                    context_sha256,
                                    current_suffix,
                                    future_stem,
                                    rewrite_required,
                                ) in INSERTED_CURRENT_CALLER_EVIDENCE
                            ],
                            "future_caller_rewrite_required_before_"
                            "runtime_approval": True,
                            "future_caller_rewrite_note":
                            "놀랍군→놀랐, 두었습니다→두었; 들었 2곳은 "
                            "유지. 결합 결과는 놀랐습니다/놀랐다, "
                            "들었습니다/들었다, 두었습니다/두었다.",
                        }
                        if root == INSERTED_ROOT
                        else {}
                    ),
                    "automatic_space_inserted": False,
                    "runtime_integration_required": True,
                },
            }
        )
    changed = sum(
        TRANSLATIONS_BY_RECORD[record_id]
        != literal_texts(current, (BLOCK_ID, record_id))[0]
        for record_id in VISIBLE_RECORD_IDS
    )
    if changed != EXPECTED_CHANGED_LITERAL_COUNT:
        raise RuntimeError(
            f"segment {SEGMENT} changed count drifted"
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        mapping,
        changed,
    )


def main() -> int:
    first = build_rows()
    second = build_rows()
    prepared, rows, candidate, candidate_sha256, mapping, changed = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or mapping != second[4]
        or changed != second[5]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if (
        len(validated) != 67
        or len(rows) != 67
        or any(
            row["scope_classification"] != "runtime_fragment_pending"
            or row["runtime_review"] != "pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B004_S1033",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_visible_ordinals": [0, 66],
                "owned_record_range": [
                    OWNED_RECORD_IDS[0],
                    OWNED_RECORD_IDS[-1],
                ],
                "owned_record_count": len(OWNED_RECORD_IDS),
                "source_literal_count": len(VISIBLE_RECORD_IDS),
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "hidden_empty_record_ids": list(
                    HIDDEN_EMPTY_RECORD_IDS
                ),
                "hidden_empty_record_count": len(
                    HIDDEN_EMPTY_RECORD_IDS
                ),
                "changed_literal_count": changed,
                "mapping_segments": {
                    "1863..1869": "Base1802..1808/+61",
                    "1870..1922": "Base1809..1861/+61",
                    "1923..1929": "PK-only inserted root544",
                    "1930..1934": "Base1862..1866/+68",
                },
                "mapping_sha256": EXPECTED_MAPPING_SHA256,
                "source_sequence_evidence": (
                    EXPECTED_SEQUENCE_EVIDENCE
                ),
                "visible_translation_policy_sha256":
                EXPECTED_VISIBLE_POLICY_SHA256,
                "inserted_root": INSERTED_ROOT,
                "inserted_record_ids": list(INSERTED_RECORD_IDS),
                "inserted_source_jp": list(INSERTED_JP),
                "inserted_legacy_current": list(INSERTED_CURRENT),
                "inserted_translation_policy": list(INSERTED_POLICY),
                "inserted_semantic_class":
                "Japanese past allomorph; Korean root supplies only "
                "polite/plain ending, not lexical come/exist",
                "inserted_call_sites": list(INSERTED_CALL_SITES),
                "inserted_source_free_current_caller_evidence": [
                    {
                        "call_site": call_site,
                        "current_left_context_utf16le_sha256":
                        context_sha256,
                        "current_left_suffix": current_suffix,
                        "future_caller_past_stem": future_stem,
                        "rewrite_required": rewrite_required,
                    }
                    for (
                        call_site,
                        context_sha256,
                        current_suffix,
                        future_stem,
                        rewrite_required,
                    ) in INSERTED_CURRENT_CALLER_EVIDENCE
                ],
                "inserted_future_caller_rewrite_note":
                "놀랍군→놀랐, 두었습니다→두었; 들었 2곳은 유지",
                "left_root484_full_policy": list(
                    LEFT_ROOT484_FULL_POLICY
                ),
                "right_root550_full_record_ids": list(
                    RIGHT_ROOT550_FULL_IDS
                ),
                "right_root550_full_policy": list(
                    RIGHT_ROOT550_FULL_POLICY
                ),
                "pk_target_incoming_sha256":
                PK_TARGET_EDGE_EVIDENCE[1],
                "pk_full_incoming_sha256":
                PK_FULL_EDGE_EVIDENCE[1],
                "valid_incoming_014c_count": 0,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "hidden_empty_records_raw_exact": True,
                "full_graph_closures_exact": True,
                "call_fixed_flatten_evidence_exact": True,
                "s1032_root484_boundary_cross_assert_exact": True,
                "right_root550_cross_next_full_assert_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
