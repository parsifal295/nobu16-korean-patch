#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1019 decisions."""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch005_segment1016 as AUDIT
import build_base_batch005_segment1017 as PRIOR


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
GRAPH = PRIOR.GRAPH
FIXED = PRIOR.FIXED
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B006_S1019.private.v1.jsonl"
)
SEGMENT = 1019
QUEUE_BATCH_ID = "base_msggame-B006"
BLOCK_ID = 0
HIDDEN_RECORD_IDS = (2338, 2342)
RECORD_IDS = tuple(
    record_id
    for record_id in range(2284, 2353)
    if record_id not in HIDDEN_RECORD_IDS
)
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
FULL_RECORD_IDS = tuple(range(2282, 2359))
HIDDEN_EMPTY_RAW_SHA256 = (
    "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"
)

# Root 526 is a genuine nonordinal topology transition. The later roots
# return to the ordinary six-record progression.
FULL_TERMINAL_GROUPS = {
    526: tuple(range(2282, 2289)),
    892: tuple(range(2289, 2296)),
    898: tuple(range(2296, 2303)),
    904: tuple(range(2303, 2310)),
    910: tuple(range(2310, 2317)),
    916: tuple(range(2317, 2324)),
    922: tuple(range(2324, 2331)),
    928: tuple(range(2331, 2338)),
    934: tuple(range(2338, 2345)),
    940: tuple(range(2345, 2352)),
    946: tuple(range(2352, 2359)),
}

# Every PK tuple below was found by a separate exact seven-literal reverse
# search. The uniform +68 record delta is a result, not a mapping premise.
PK_FULL_TERMINAL_GROUPS = {
    532: tuple(range(2350, 2357)),
    904: tuple(range(2357, 2364)),
    910: tuple(range(2364, 2371)),
    916: tuple(range(2371, 2378)),
    922: tuple(range(2378, 2385)),
    928: tuple(range(2385, 2392)),
    934: tuple(range(2392, 2399)),
    940: tuple(range(2399, 2406)),
    946: tuple(range(2406, 2413)),
    952: tuple(range(2413, 2420)),
    958: tuple(range(2420, 2427)),
}
PK_ROOT_BY_BASE = {
    526: 532,
    892: 904,
    898: 910,
    904: 916,
    910: 922,
    916: 928,
    922: 934,
    928: 940,
    934: 946,
    940: 952,
    946: 958,
}
PK_RECORD_MAP = {
    base_record_id: pk_record_id
    for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items()
    for base_record_id, pk_record_id in zip(
        base_record_ids,
        PK_FULL_TERMINAL_GROUPS[PK_ROOT_BY_BASE[base_root]],
        strict=True,
    )
}

SOURCE_MATRICES = {
    526: (
        "ください",
        "参れ",
        "くださいませ",
        "くださりませ",
        "ください",
        "くだされ",
        "参れ",
    ),
    892: (
        "お任せを",
        "任せてくれ",
        "お任せください",
        "お任せください",
        "お任せを",
        "お任せを",
        "任せろ",
    ),
    898: (
        "お待ちください",
        "待ってくれ",
        "お待ちを",
        "お待ちくだされ",
        "待ってください",
        "待っていただきたい",
        "待ってくれ",
    ),
    904: (
        "待ちなさい",
        "待て",
        "待ちなさい",
        "待ちなされ",
        "待ってください",
        "待て",
        "待て",
    ),
    910: (
        "お待ちください",
        "お待ちあれ",
        "お待ちなさりますよう",
        "お待ちくだされ",
        "お待ちください",
        "お待ちあれ",
        "待っておれ",
    ),
    916: (
        "みません",
        "まぬ",
        "みませぬ",
        "みませぬ",
        "みません",
        "みません",
        "まぬ",
    ),
    922: (
        "お見事",
        "見事",
        "お見事でございます",
        "お見事にございます",
        "お見事です",
        "お見事",
        "見事",
    ),
    928: (
        "みます",
        "む",
        "みます",
        "みまする",
        "みます",
        "みます",
        "む",
    ),
    934: ("", "め", "め", "風情が", "", "め", "め"),
    940: (
        "みなさい",
        "め",
        "みなされ",
        "みなさい",
        "みなさい",
        "みなさい",
        "むがよい",
    ),
    946: (
        "お命じください",
        "命じてくれ",
        "お命じください",
        "お命じくだされ",
        "命じてください",
        "命じてくだされ",
        "命じてくれ",
    ),
}
EXPECTED_FULL_BASE_JP = {
    record_id: source
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, source in zip(
        record_ids,
        SOURCE_MATRICES[root],
        strict=True,
    )
}

TRANSLATION_MATRICES = {
    526: (
        "주십시오",
        "오너라",
        "주시옵소서",
        "주시옵소서",
        "주십시오",
        "주시오",
        "오너라",
    ),
    892: (
        "맡겨 주십시오",
        "맡겨 다오",
        "맡겨 주십시오",
        "맡겨 주십시오",
        "맡겨 주십시오",
        "맡겨 주시오",
        "맡겨라",
    ),
    898: (
        "기다려 주십시오",
        "기다려 다오",
        "기다려 주십시오",
        "기다려 주시오",
        "기다려 주십시오",
        "기다려 주셨으면 하오",
        "기다려 다오",
    ),
    904: (
        "기다리십시오",
        "기다려라",
        "기다리십시오",
        "기다리시오",
        "기다려 주십시오",
        "기다려라",
        "기다려라",
    ),
    910: (
        "기다려 주십시오",
        "기다리시오",
        "기다려 주시옵소서",
        "기다려 주시오",
        "기다려 주십시오",
        "기다리시오",
        "기다리고 있거라",
    ),
    916: (
        "지 않습니다",
        "지 않는다",
        "지 않사옵니다",
        "지 않사옵니다",
        "지 않습니다",
        "지 않습니다",
        "지 않는다",
    ),
    922: (
        "훌륭합니다",
        "훌륭하다",
        "훌륭하옵니다",
        "훌륭하옵니다",
        "훌륭합니다",
        "훌륭하오",
        "훌륭하다",
    ),
    928: (
        "합니다",
        "한다",
        "합니다",
        "하옵니다",
        "합니다",
        "합니다",
        "한다",
    ),
    934: ("", "놈", "놈", "주제에", "", "놈", "놈"),
    940: (
        "힘써라",
        "힘써라",
        "힘쓰시오",
        "힘써라",
        "힘써라",
        "힘써라",
        "힘쓰도록 하라",
    ),
    946: (
        "명해 주십시오",
        "명해 다오",
        "명해 주십시오",
        "명해 주시오",
        "명해 주십시오",
        "명해 주시오",
        "명해 다오",
    ),
}
FULL_TRANSLATION_POLICY = {
    record_id: translation
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, translation in zip(
        record_ids,
        TRANSLATION_MATRICES[root],
        strict=True,
    )
}
TRANSLATIONS_BY_RECORD = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in RECORD_IDS
}
TRANSLATIONS = {
    f"0:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
BOUNDARY_TRANSLATION_POLICY = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in FULL_RECORD_IDS
    if record_id not in RECORD_IDS
}

TARGET_ARCHIVE_DIGESTS = {
    "base_jp": "46706B4FBA4C5A3CF2F58659985275B91CEBC484567FC3A98F1DBFB7ADF951C7",
    "base_current": "CA9B5AABF2E1F194D301AD252077DC813F02C331CF825E5072B65DDFE799435C",
    "base_sc": "A93B0573A1645511F0BF2446A2C2C78B4C0E6C333017CE800BB1DE51A64EC50A",
    "base_tc": "A93B0573A1645511F0BF2446A2C2C78B4C0E6C333017CE800BB1DE51A64EC50A",
    "pk_jp": "3F8653BE42887827DB711E936552C249357B479D0E58B7EF593BB9C4334AEB26",
    "pk_current": "A0777F0AFF2C8FB83FF7283258D0C1177F47EBA01F6F16CE3CB3878922842384",
    "pk_sc": "33C2C29BCC9D35927D554F9FB37E0D140BD7CA1737EF4002540854B24E0C950E",
    "pk_tc": "33C2C29BCC9D35927D554F9FB37E0D140BD7CA1737EF4002540854B24E0C950E",
    "pk_en": "33C2C29BCC9D35927D554F9FB37E0D140BD7CA1737EF4002540854B24E0C950E",
}
FULL_ARCHIVE_DIGESTS = {
    "base_jp": "C9405FA037E031EA5A3277025C95A30509218861644E5BAAA92EC770862E1FDA",
    "base_current": "B1176671D5534997F06B41AECB1E119BEBB8B55F0CA6B302945D502FB6907F22",
    "base_sc": "231679BBD3828708BEE8161F6DF0EB83A480E78E92FE7CABEB126FC00FD2102A",
    "base_tc": "231679BBD3828708BEE8161F6DF0EB83A480E78E92FE7CABEB126FC00FD2102A",
    "pk_jp": "3F18B4C68A3AA707AE09653CE73FB4BE1107C5F93077DC4757704256EE51ACAA",
    "pk_current": "2DD37851D5299A781CB5565AFC892FCB690ED15F0EF592C8CECB4143A5B83865",
    "pk_sc": "5E8461B97E705A4D7D3B80D5FD55A5416D61BF48F539E02966081DC412CF7610",
    "pk_tc": "5E8461B97E705A4D7D3B80D5FD55A5416D61BF48F539E02966081DC412CF7610",
    "pk_en": "5E8461B97E705A4D7D3B80D5FD55A5416D61BF48F539E02966081DC412CF7610",
}
JUMP_EVIDENCE = {
    "base_jp": {
        "target": (67, "A1B247DDFD537E43C120DE6BA549296E77D7D36BBA74D93CA0F4E88552BE0CDE"),
        "full": (77, "D21DDF882484A93E179D3B0C5B9D711B61E50193B4531D645BDE54E183E14E7E"),
    },
    "base_current": {
        "target": (67, "A1B247DDFD537E43C120DE6BA549296E77D7D36BBA74D93CA0F4E88552BE0CDE"),
        "full": (77, "D21DDF882484A93E179D3B0C5B9D711B61E50193B4531D645BDE54E183E14E7E"),
    },
    "pk_jp": {
        "target": (67, "054CFC95C6C06D32AF7AF5FBF6DE8979AF4F449A86691AC77E8C878385F4D9C0"),
        "full": (77, "EA988DFC8705B68D060FC8579709AC4CC4250E0F651C4FB21266AAB7540AC2C4"),
    },
    "pk_current": {
        "target": (67, "054CFC95C6C06D32AF7AF5FBF6DE8979AF4F449A86691AC77E8C878385F4D9C0"),
        "full": (77, "EA988DFC8705B68D060FC8579709AC4CC4250E0F651C4FB21266AAB7540AC2C4"),
    },
}

EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EMPTY_EVIDENCE = (0, EMPTY_SHA256)
EVIDENCE_ROOTS = tuple(FULL_TERMINAL_GROUPS)
ACTUAL_CALL_ROOT = {
    "base": {root: root for root in EVIDENCE_ROOTS},
    "pk": dict(PK_ROOT_BY_BASE),
}
CALLER_ROW_EVIDENCE = {
    "base_jp": (75, "3347D4ED04C544701F68F751CBADEFA1871A8975F0AC18963E6F9F21947E9242"),
    "base_current": (68, "411AC1715CD7D873E8F373AB8C7BFB2D1A657D6DC5D5720C812ABF1170BD24E4"),
    "pk_jp": (80, "7E14B161962773F6AD8B822E16E93FBA6E6D3EF5BBADCC33DF21AA60C4294E20"),
    "pk_current": (76, "CD184D16CFDE79DE0B6E0B47EE6D8D02F4A354736F77D4925FFA77806EEE7572"),
}


def evidence(
    overrides: dict[int, tuple[int, str]],
) -> dict[int, tuple[int, str]]:
    return {
        root: overrides.get(root, EMPTY_EVIDENCE)
        for root in EVIDENCE_ROOTS
    }


CALL_EVIDENCE = {
    "base_jp": evidence(
        {
            526: (1, "F43F97E56B81DDBFDEAD4A8B15DD9013C1305890CD21EA4A8A73529C89D8EFE8"),
            892: (42, "8CA1EB17B8CA906F0E2D0E97570B600DC7DEE3A6BC5B362C8D42E46D75FAFA27"),
            898: (6, "3FD4767F18CF7A7D9BA2D5B8F87D0375EF9271A9380954EB2A21932DF22333C5"),
            910: (1, "961FC02865A9CE0C7F032D9090C87EA24C9A46E8F7A65C82CC193F4C1CF070A6"),
            916: (4, "785442F65B5B7455F49A15C5BE59D5D56162AED57A15EE96A3E739BF83B3E9E9"),
            922: (1, "6D4E024AB08163C63C886D06CC1CA4A7398C10A4E60397F397CF9FDA3D4E7D0C"),
            928: (9, "629FABAC598351D85A7DEE54CF82E89C77D2FE5F8E2F430D4F5CD39695E98356"),
            940: (2, "8092A548C11FC022BA1FF3F3F43A7B160304977B47F8DD4B659AD6620282C7CC"),
            946: (9, "203A7FDD7BEE99D46611D6EAF5F8CBB6DE435CE84FCB56F2D2F4180C77733199"),
        }
    ),
    "base_current": evidence(
        {
            526: (1, "F43F97E56B81DDBFDEAD4A8B15DD9013C1305890CD21EA4A8A73529C89D8EFE8"),
            892: (39, "F64CE48E58103EA0F042C287B7603C70F8C65BB6756E9721B464FE6EAC96CB70"),
            898: (6, "3FD4767F18CF7A7D9BA2D5B8F87D0375EF9271A9380954EB2A21932DF22333C5"),
            916: (4, "785442F65B5B7455F49A15C5BE59D5D56162AED57A15EE96A3E739BF83B3E9E9"),
            922: (1, "6D4E024AB08163C63C886D06CC1CA4A7398C10A4E60397F397CF9FDA3D4E7D0C"),
            928: (6, "0B057780714D08C52E69962949D8CC931759D0018C53ADE08F44CCA7E02A60CD"),
            940: (2, "8092A548C11FC022BA1FF3F3F43A7B160304977B47F8DD4B659AD6620282C7CC"),
            946: (9, "203A7FDD7BEE99D46611D6EAF5F8CBB6DE435CE84FCB56F2D2F4180C77733199"),
        }
    ),
    "pk_jp": evidence(
        {
            526: (1, "F43F97E56B81DDBFDEAD4A8B15DD9013C1305890CD21EA4A8A73529C89D8EFE8"),
            892: (41, "0B620F6BB997F70E47DFE17CBE2A5FC5DD01B3593714834E9F6FAA5B7BDC52D3"),
            898: (6, "696ADCE4F953C0DB6A1CB04E5EA068BDB4C9715C1E0E8295F7DE305A480E8B37"),
            910: (1, "631EA892DFBED667A33EBFE223BA3812A825FC94088C969091513CE95394C6C9"),
            916: (7, "95A955DEB384EECE4CB05A067750A81C3DF2CAC27654F9D47368E3B4DF0CC0DB"),
            922: (1, "6D4E024AB08163C63C886D06CC1CA4A7398C10A4E60397F397CF9FDA3D4E7D0C"),
            928: (12, "BF1B4DD7EF9B485CDCC14FB4E68424133BBEF98F6B9526812664CADB1B9A8631"),
            940: (2, "43A3648CDFA96DE0537BB94586B5D74E8CA8A628C6F08B204C234B5A7E5ECC4A"),
            946: (9, "B0A32C3D8589611ECC14C17C314D5D887A7052B3531AA91F57150E7B7D474F9B"),
        }
    ),
    "pk_current": evidence(
        {
            526: (1, "F43F97E56B81DDBFDEAD4A8B15DD9013C1305890CD21EA4A8A73529C89D8EFE8"),
            892: (39, "D99DDECBEFA9408061BD775EA86B105815757CF38DD7A9C8E63B5FEA9B47E739"),
            898: (6, "696ADCE4F953C0DB6A1CB04E5EA068BDB4C9715C1E0E8295F7DE305A480E8B37"),
            916: (7, "95A955DEB384EECE4CB05A067750A81C3DF2CAC27654F9D47368E3B4DF0CC0DB"),
            922: (1, "6D4E024AB08163C63C886D06CC1CA4A7398C10A4E60397F397CF9FDA3D4E7D0C"),
            928: (11, "BA5A07688239A8A9BC2FB2E7C44E98003E027D789E19BA3311ED47929021A5D3"),
            940: (2, "43A3648CDFA96DE0537BB94586B5D74E8CA8A628C6F08B204C234B5A7E5ECC4A"),
            946: (9, "B0A32C3D8589611ECC14C17C314D5D887A7052B3531AA91F57150E7B7D474F9B"),
        }
    ),
}

FLATTEN_EVIDENCE = {
    "base": evidence(
        {
            892: (3, "94BE99BD7DED3FE4A4F077E54954F1A053AAEB1F78086E25E3EBC5C79C041BBF"),
            910: (1, "961FC02865A9CE0C7F032D9090C87EA24C9A46E8F7A65C82CC193F4C1CF070A6"),
            928: (3, "56D1D47FE1EE2F03C451335925B0E73D2D5127B420175BF3685F6982777403F0"),
        }
    ),
    "pk": evidence(
        {
            892: (2, "4BBE73AE877DB16C89F54B1243C5E19ED8406BFC1BC34BE1ADD9F06AC6FB6059"),
            910: (1, "631EA892DFBED667A33EBFE223BA3812A825FC94088C969091513CE95394C6C9"),
            928: (1, "6EF35144FE17D2B4BE33FF36051E8D5D839EC0E7D794E9198FC224A27C6E702C"),
        }
    ),
}

FIXED_FOLLOWING_EVIDENCE = {
    "base_jp": evidence(
        {
            916: (1, "A0FC10AE7BC60622232F2959CA077D98D630B6FA61D4A558F6DF7996F266C7F6"),
            928: (7, "6FF71029ECE5639E4F55E20B0BFDEA23E764F118F1560E1B5B625489F93E84CD"),
        }
    ),
    "base_current": evidence(
        {
            916: (1, "A0FC10AE7BC60622232F2959CA077D98D630B6FA61D4A558F6DF7996F266C7F6"),
            928: (5, "A0CF2E08C6049BBEBF1FDEF4A2F55B0E7E3CE4AE16F64F08EF70F4192CA66BC8"),
        }
    ),
    "pk_jp": evidence(
        {
            916: (3, "3329C073ECEDDCC991EBC24370778C2A6B92EEB33160EE8DC33C05DD16576CED"),
            928: (8, "958AB4A98C8C6A3994A695158189D2668DD84BC245DAD4763A895106558CB78B"),
        }
    ),
    "pk_current": evidence(
        {
            916: (3, "3329C073ECEDDCC991EBC24370778C2A6B92EEB33160EE8DC33C05DD16576CED"),
            928: (8, "958AB4A98C8C6A3994A695158189D2668DD84BC245DAD4763A895106558CB78B"),
        }
    ),
}

INTEGRATION_NOTE_BY_ROOT = {
    526: (
        "live caller is tsuite plus the terminal; Korean caller must retain "
        "ttara and distinguish polite jusipsio from plain onerra"
    ),
    892: (
        "complete entrust-me request used by many callers; preserve standard, "
        "plain, and archaic request registers; te kure follows the approved "
        "project-wide hae dao request voice"
    ),
    898: (
        "complete wait request; no fixed following blocker, but caller spacing "
        "and register still require integrated review"
    ),
    904: (
        "no live Base or PK caller remains; literal wait-command semantics and "
        "the full seven-voice matrix are preserved"
    ),
    910: (
        "good-news wait formula; the sole source caller is flattened in both "
        "current corpora and must be restored during integration"
    ),
    916: (
        "Japanese mi/ma negative endings complete isomu, susumu, and nozomu; "
        "they do not mean see, so Korean callers keep their lexical stem and "
        "attach ji anseumnida variants"
    ),
    922: (
        "standalone praise before an exclamation; Korean forms must be complete "
        "predicates rather than the bare noun hullyung"
    ),
    928: (
        "Japanese mi/mu endings complete multiple verbs including susumu, "
        "tanomu, fukikomu, kasamu, nozomu, and isomu; callers must normalize "
        "to Korean verbal nouns before the generic hada register endings"
    ),
    934: (
        "hostile person suffix matrix; hidden voices remain empty, me is nom, "
        "and fuzei ga is the subject-marking insult jujee"
    ),
    940: (
        "both live callers are mina no mono yoku isomu; the source fragments "
        "complete that verb and must become full Korean exert-yourself commands"
    ),
    946: (
        "complete request to issue an order; preserve standard, plain, and "
        "archaic request registers across adjacent-segment boundary records"
    ),
}

BASIS = (
    "review_queue_base_msggame_B006_pristine_base_pc_jp_sole_authority_"
    "block0_visible_records2284_2352_hidden2338_2342_excluded_raw_exact_"
    "complete_eleven_seven_voice_groups2282_2358_nonordinal_base_root526_"
    "pk_root532_then_base_roots892_946_pk_roots904_958_unique_exact_seven_"
    "literal_tuple_reverse_search_without_fixed_offset_assumption_discovered_"
    "uniform_delta68_target_and_full_014a_closures_0143_caller_rows_source_"
    "current_flattening_fixed_following_digests_no_relevant_standalone_014c_"
    "follow_me_entrust_wait_negative_m_stem_praise_affirmative_m_stem_"
    "hostile_suffix_exert_yourself_and_order_request_semantics_runtime_"
    "caller_integration_pending_pc_pk_auxiliary_context_only_no_historic_or_"
    "switch_korean_authority_one_line_gap_skeleton_reverse_exact_no_steam"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return PRIOR.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return PRIOR.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return PRIOR.archive_records(prepared)


def digest_json(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, separators=(",", ":")).encode("ascii")
    ).hexdigest().upper()


def digest_sites(sites: tuple[str, ...]) -> str:
    return hashlib.sha256(
        "\n".join(sites).encode("ascii")
    ).hexdigest().upper()


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    target_base_keys = tuple((BLOCK_ID, value) for value in RECORD_IDS)
    target_pk_keys = tuple(
        (BLOCK_ID, PK_RECORD_MAP[value]) for value in RECORD_IDS
    )
    full_base_keys = tuple((BLOCK_ID, value) for value in FULL_RECORD_IDS)
    full_pk_keys = tuple(
        (BLOCK_ID, PK_RECORD_MAP[value]) for value in FULL_RECORD_IDS
    )
    for label, records in records_by_label.items():
        target_keys = (
            target_pk_keys if label.startswith("pk_") else target_base_keys
        )
        full_keys = (
            full_pk_keys if label.startswith("pk_") else full_base_keys
        )
        if (
            GENERAL.subset_digest(records, target_keys)
            != TARGET_ARCHIVE_DIGESTS[label]
            or GENERAL.subset_digest(records, full_keys)
            != FULL_ARCHIVE_DIGESTS[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} target/full corpus drifted"
            )

    if (
        len(RECORD_IDS) != 67
        or set(PK_RECORD_MAP) != set(FULL_RECORD_IDS)
        or set(HIDDEN_RECORD_IDS).intersection(RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} record universe drifted")

    for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items():
        expected = SOURCE_MATRICES[base_root]
        pk_root = PK_ROOT_BY_BASE[base_root]
        pk_record_ids = PK_FULL_TERMINAL_GROUPS[pk_root]
        starts = AUDIT.sequence_starts(records_by_label["pk_jp"], expected)
        if starts != (pk_record_ids[0],):
            raise RuntimeError(
                f"segment {SEGMENT} unique PK tuple search drifted: "
                f"{base_root}/{starts}"
            )
        if tuple(
            PK_RECORD_MAP[record_id] for record_id in base_record_ids
        ) != pk_record_ids:
            raise RuntimeError(
                f"segment {SEGMENT} explicit PK map drifted: "
                f"{base_root}/{pk_root}"
            )

    for record_id in FULL_RECORD_IDS:
        base_key = (BLOCK_ID, record_id)
        pk_key = (BLOCK_ID, PK_RECORD_MAP[record_id])
        if literal_texts(
            records_by_label["base_jp"],
            base_key,
        ) != (EXPECTED_FULL_BASE_JP[record_id],):
            raise RuntimeError(
                f"segment {SEGMENT} pristine Base JP drifted: {base_key}"
            )
        for label, key in (
            ("base_jp", base_key),
            ("base_current", base_key),
            ("base_sc", base_key),
            ("base_tc", base_key),
            ("pk_jp", pk_key),
            ("pk_current", pk_key),
            ("pk_sc", pk_key),
            ("pk_tc", pk_key),
            ("pk_en", pk_key),
        ):
            if (
                len(literal_texts(records_by_label[label], key)) != 1
                or gap_bytes(records_by_label[label][key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} skeleton drifted: {label}/{key}"
                )
        for language in ("jp", "current", "sc", "tc"):
            if (
                literal_texts(
                    records_by_label[f"base_{language}"],
                    base_key,
                )
                != literal_texts(
                    records_by_label[f"pk_{language}"],
                    pk_key,
                )
                or gap_bytes(
                    records_by_label[f"base_{language}"][base_key]
                )
                != gap_bytes(
                    records_by_label[f"pk_{language}"][pk_key]
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base/PK auxiliary drifted: "
                    f"{language}/{base_key}/{pk_key}"
                )
        if (
            literal_texts(records_by_label["base_sc"], base_key) != ("",)
            or literal_texts(records_by_label["base_tc"], base_key) != ("",)
            or literal_texts(records_by_label["pk_en"], pk_key) != ("",)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} auxiliary text appeared: {record_id}"
            )

    for record_id in HIDDEN_RECORD_IDS:
        for label, records in records_by_label.items():
            actual_id = (
                PK_RECORD_MAP[record_id]
                if label.startswith("pk_")
                else record_id
            )
            key = (BLOCK_ID, actual_id)
            if (
                hashlib.sha256(records[key].data).hexdigest().upper()
                != HIDDEN_EMPTY_RAW_SHA256
                or literal_texts(records, key) != ("",)
                or gap_bytes(records[key]) != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} hidden record drifted: "
                    f"{label}/{key}"
                )


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    full_base_ids = set(FULL_RECORD_IDS)
    full_pk_ids = {PK_RECORD_MAP[value] for value in FULL_RECORD_IDS}
    target_base_ids = set(RECORD_IDS)
    target_pk_ids = {PK_RECORD_MAP[value] for value in RECORD_IDS}

    for label in ("base_jp", "base_current", "pk_jp", "pk_current"):
        edition = label.split("_", 1)[0]
        records = records_by_label[label]
        target_ids = target_pk_ids if edition == "pk" else target_base_ids
        full_ids = full_pk_ids if edition == "pk" else full_base_ids
        for scope, ids in (("target", target_ids), ("full", full_ids)):
            rows = GRAPH.incoming_jump_rows(records, ids)
            expected_count, expected_sha256 = JUMP_EVIDENCE[label][scope]
            if (
                len(rows) != expected_count
                or digest_json(rows) != expected_sha256
                or {row[4] for row in rows} != ids
                or any(
                    sum(row[4] == target for row in rows) != 1
                    for target in ids
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} {scope} 014A drifted"
                )

        edges = GRAPH.graph_edges(records)
        for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items():
            actual_root = ACTUAL_CALL_ROOT[edition][base_root]
            expected_ids = (
                set(PK_FULL_TERMINAL_GROUPS[PK_ROOT_BY_BASE[base_root]])
                if edition == "pk"
                else set(base_record_ids)
            )
            closure = GRAPH.graph_closure(edges, actual_root).intersection(
                full_ids
            )
            if closure != expected_ids:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} closure drifted: "
                    f"{base_root}/{actual_root}"
                )

        caller_rows, caller_sites = GRAPH.caller_rows(records, full_ids)
        expected_count, expected_sha256 = CALLER_ROW_EVIDENCE[label]
        if (
            len(caller_rows) != expected_count
            or digest_json(caller_rows) != expected_sha256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} 0143 caller rows drifted"
            )
        expected_roots = {
            ACTUAL_CALL_ROOT[edition][root]
            for root, (count, _) in CALL_EVIDENCE[label].items()
            if count
        }
        if set(caller_sites) != expected_roots:
            raise RuntimeError(
                f"segment {SEGMENT} {label} caller roots drifted"
            )
        for root in EVIDENCE_ROOTS:
            actual_root = ACTUAL_CALL_ROOT[edition][root]
            sites = caller_sites.get(actual_root, ())
            call_count, call_sha256 = CALL_EVIDENCE[label][root]
            if (
                len(sites) != call_count
                or digest_sites(sites) != call_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} calls drifted: "
                    f"{root}/{actual_root}"
                )
            blockers = FIXED.fixed_following_blockers(
                records,
                actual_root,
            )
            fixed_count, fixed_sha256 = FIXED_FOLLOWING_EVIDENCE[
                label
            ][root]
            if (
                len(blockers) != fixed_count
                or digest_sites(blockers) != fixed_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} fixed following "
                    f"drifted: {root}/{actual_root}"
                )

        if AUDIT.relevant_standalone_014c(records, full_ids):
            raise RuntimeError(
                f"segment {SEGMENT} {label} standalone 014C appeared"
            )

    for edition in ("base", "pk"):
        full_ids = full_pk_ids if edition == "pk" else full_base_ids
        _, source_sites = GRAPH.caller_rows(
            records_by_label[f"{edition}_jp"],
            full_ids,
        )
        _, current_sites = GRAPH.caller_rows(
            records_by_label[f"{edition}_current"],
            full_ids,
        )
        for root in EVIDENCE_ROOTS:
            actual_root = ACTUAL_CALL_ROOT[edition][root]
            flattened = tuple(
                sorted(
                    set(source_sites.get(actual_root, ()))
                    - set(current_sites.get(actual_root, ()))
                )
            )
            current_only = (
                set(current_sites.get(actual_root, ()))
                - set(source_sites.get(actual_root, ()))
            )
            expected_count, expected_sha256 = FLATTEN_EVIDENCE[
                edition
            ][root]
            if (
                current_only
                or len(flattened) != expected_count
                or digest_sites(flattened) != expected_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} flattening drifted: "
                    f"{root}/{actual_root}"
                )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != TRANSLATIONS
        or len(translations) != 67
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(FULL_TRANSLATION_POLICY) != set(FULL_RECORD_IDS)
        or set(SOURCE_MATRICES) != set(FULL_TERMINAL_GROUPS)
        or set(TRANSLATION_MATRICES) != set(FULL_TERMINAL_GROUPS)
        or set(INTEGRATION_NOTE_BY_ROOT) != set(FULL_TERMINAL_GROUPS)
    ):
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")

    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        actual = tuple(
            FULL_TRANSLATION_POLICY[record_id]
            for record_id in record_ids
        )
        if actual != TRANSLATION_MATRICES[root]:
            raise RuntimeError(
                f"segment {SEGMENT} register matrix drifted: {root}"
            )

    if (
        FULL_TRANSLATION_POLICY[2282] != "주십시오"
        or FULL_TRANSLATION_POLICY[2283] != "오너라"
        or TRANSLATIONS_BY_RECORD[2284] != "주시옵소서"
        or TRANSLATIONS_BY_RECORD[2288] != "오너라"
        or TRANSLATIONS_BY_RECORD[2289] != "맡겨 주십시오"
        or TRANSLATIONS_BY_RECORD[2290] != "맡겨 다오"
        or TRANSLATIONS_BY_RECORD[2312] != "기다려 주시옵소서"
        or TRANSLATIONS_BY_RECORD[2317] != "지 않습니다"
        or TRANSLATIONS_BY_RECORD[2325] != "훌륭하다"
        or TRANSLATIONS_BY_RECORD[2331] != "합니다"
        or FULL_TRANSLATION_POLICY[2338] != ""
        or TRANSLATIONS_BY_RECORD[2341] != "주제에"
        or TRANSLATIONS_BY_RECORD[2346] != "힘써라"
        or TRANSLATIONS_BY_RECORD[2351] != "힘쓰도록 하라"
        or TRANSLATIONS_BY_RECORD[2352] != "명해 주십시오"
        or FULL_TRANSLATION_POLICY[2358] != "명해 다오"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic correction contract drifted"
        )

    for coordinate, translation in translations.items():
        if (
            not translation
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: {coordinate}"
            )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]], str]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_corpora(records_by_label)
    assert_runtime_graph(records_by_label)

    current = records_by_label["base_current"]
    translations = dict(TRANSLATIONS)
    assert_semantics(translations)
    for coordinate, translation in translations.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(current, (BLOCK_ID, record_id))[0]
        if not ENGINE.is_visible_translation_candidate(current_text):
            raise RuntimeError(
                f"segment {SEGMENT} target became non-visible: "
                f"{coordinate}"
            )
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {SEGMENT} layout signature drifted: "
                f"{coordinate}"
            )

    candidate_sha256 = GENERAL.assert_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        target_records=set(RECORD_KEYS),
    )
    root_by_record = {
        record_id: root
        for root, record_ids in FULL_TERMINAL_GROUPS.items()
        for record_id in record_ids
        if record_id in RECORD_IDS
    }
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        root = root_by_record[record_id]
        pk_root = PK_ROOT_BY_BASE[root]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
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
                    "pk_mapping_method": (
                        "unique_exact_seven_literal_tuple_reverse_search"
                    ),
                    "base_root": root,
                    "pk_semantic_root": pk_root,
                    "base_record_id": record_id,
                    "pk_semantic_record_id": PK_RECORD_MAP[record_id],
                    "automatic_space_inserted": False,
                    "full_terminal_record_ids": list(
                        FULL_TERMINAL_GROUPS[root]
                    ),
                    "pk_full_terminal_record_ids": list(
                        PK_FULL_TERMINAL_GROUPS[pk_root]
                    ),
                    "base_source_call_count": CALL_EVIDENCE[
                        "base_jp"
                    ][root][0],
                    "base_current_call_count": CALL_EVIDENCE[
                        "base_current"
                    ][root][0],
                    "pk_source_call_count": CALL_EVIDENCE[
                        "pk_jp"
                    ][root][0],
                    "pk_current_call_count": CALL_EVIDENCE[
                        "pk_current"
                    ][root][0],
                    "base_source_only_flattened_call_count": (
                        FLATTEN_EVIDENCE["base"][root][0]
                    ),
                    "pk_source_only_flattened_call_count": (
                        FLATTEN_EVIDENCE["pk"][root][0]
                    ),
                    "base_current_fixed_following_count": (
                        FIXED_FOLLOWING_EVIDENCE["base_current"][
                            root
                        ][0]
                    ),
                    "pk_current_fixed_following_count": (
                        FIXED_FOLLOWING_EVIDENCE["pk_current"][
                            root
                        ][0]
                    ),
                    "integration_note": INTEGRATION_NOTE_BY_ROOT[root],
                    "relevant_valid_standalone_014c_count": 0,
                    "runtime_integration_required": True,
                },
            }
        )
    return prepared, translations, rows, candidate_sha256


def main() -> int:
    prepared, translations, rows, candidate_sha256 = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != 67 or len(rows) != 67:
        raise RuntimeError(f"segment {SEGMENT} validation count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime or authority flag drifted"
        )

    current = archive_records(prepared)["base_current"]
    changed = sum(
        translation
        != literal_texts(
            current,
            (BLOCK_ID, int(coordinate.split(":")[1])),
        )[0]
        for coordinate, translation in translations.items()
    )
    discovered_deltas = sorted(
        {
            PK_RECORD_MAP[record_id] - record_id
            for record_id in FULL_RECORD_IDS
        }
    )
    discovered_root_deltas = sorted(
        {
            PK_ROOT_BY_BASE[root] - root
            for root in FULL_TERMINAL_GROUPS
        }
    )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B006_S1019",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "hidden_record_ids_excluded_and_exact": list(
                    HIDDEN_RECORD_IDS
                ),
                "pk_mapping_method": (
                    "unique_exact_seven_literal_tuple_reverse_search"
                ),
                "discovered_base_pk_record_deltas": discovered_deltas,
                "discovered_base_pk_root_deltas": (
                    discovered_root_deltas
                ),
                "base_pk_literal_and_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in FULL_TERMINAL_GROUPS.items()
                },
                "pk_full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in PK_FULL_TERMINAL_GROUPS.items()
                },
                "pk_root_by_base": PK_ROOT_BY_BASE,
                "boundary_translation_policy": (
                    BOUNDARY_TRANSLATION_POLICY
                ),
                "jump_evidence": JUMP_EVIDENCE,
                "caller_row_evidence": CALLER_ROW_EVIDENCE,
                "call_evidence": CALL_EVIDENCE,
                "flatten_evidence": FLATTEN_EVIDENCE,
                "fixed_following_evidence": (
                    FIXED_FOLLOWING_EVIDENCE
                ),
                "relevant_valid_standalone_014c_count": 0,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "hidden_runtime_skeleton_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
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
