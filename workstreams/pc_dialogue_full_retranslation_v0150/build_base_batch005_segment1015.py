#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1015 decisions."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch004_segment1013 as EVIDENCE
import build_base_batch004_segment1014 as PRIOR


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
GRAPH = EVIDENCE.GRAPH
FIXED = EVIDENCE.FIXED
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B005_S1015.private.v1.jsonl"
)
SEGMENT = 1015
QUEUE_BATCH_ID = "base_msggame-B005"
BLOCK_ID = 0
TARGET_RECORD_IDS = tuple(range(2014, 2083))
HIDDEN_RECORD_IDS = (2079, 2081)
VISIBLE_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in HIDDEN_RECORD_IDS
)
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in TARGET_RECORD_IDS)
VISIBLE_RECORD_KEYS = tuple(
    (BLOCK_ID, record_id) for record_id in VISIBLE_RECORD_IDS
)
FULL_RECORD_IDS = tuple(range(2009, 2086))

# These are the actual Base 014A roots and their complete seven-leaf groups.
FULL_TERMINAL_GROUPS = {
    664: tuple(range(2009, 2016)),
    670: tuple(range(2016, 2023)),
    676: tuple(range(2023, 2030)),
    682: tuple(range(2030, 2037)),
    688: tuple(range(2037, 2044)),
    694: tuple(range(2044, 2051)),
    700: tuple(range(2051, 2058)),
    706: tuple(range(2058, 2065)),
    712: tuple(range(2065, 2072)),
    718: tuple(range(2072, 2079)),
    724: tuple(range(2079, 2086)),
}

# Each PK tuple below is independently verified by exact seven-literal reverse
# search.  The resulting +68 record delta and +12 root delta prove that the
# two earlier PK-only terminal-family insertions still account for the mapping;
# no additional insertion occurs in this segment.
PK_FULL_TERMINAL_GROUPS = {
    676: tuple(range(2077, 2084)),
    682: tuple(range(2084, 2091)),
    688: tuple(range(2091, 2098)),
    694: tuple(range(2098, 2105)),
    700: tuple(range(2105, 2112)),
    706: tuple(range(2112, 2119)),
    712: tuple(range(2119, 2126)),
    718: tuple(range(2126, 2133)),
    724: tuple(range(2133, 2140)),
    730: tuple(range(2140, 2147)),
    736: tuple(range(2147, 2154)),
}
PK_ROOT_BY_BASE = {
    664: 676,
    670: 682,
    676: 688,
    682: 694,
    688: 700,
    694: 706,
    700: 712,
    706: 718,
    712: 724,
    718: 730,
    724: 736,
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

SOURCE_JP_BY_ROOT = {
    664: (
        "では",
        "では",
        "それでは",
        "ならば",
        "じゃあ",
        "では",
        "じゃあ",
    ),
    670: (
        "では",
        "では",
        "では",
        "では",
        "では",
        "では",
        "じゃ",
    ),
    676: (
        "ではない",
        "ならざる",
        "ではない",
        "ならざる",
        "ではない",
        "でない",
        "じゃない",
    ),
    682: (
        "ではありません",
        "ではない",
        "ではございませぬ",
        "ではございませぬ",
        "ではありません",
        "ではござらぬ",
        "じゃねえ",
    ),
    688: (
        "どう",
        "どう",
        "いかが",
        "いかが",
        "どう",
        "いかが",
        "どう",
    ),
    694: (
        "どきなさい",
        "どけ",
        "おどきなされ",
        "どいてくだされ",
        "どいてください",
        "どきなされ",
        "どけ",
    ),
    700: (
        "とのこと",
        "とのこと",
        "との話",
        "との話",
        "ということ",
        "との由",
        "って話",
    ),
    706: (
        "ね",
        "な",
        "ですね",
        "な",
        "わね",
        "な",
        "な",
    ),
    712: (
        "わ",
        "な",
        "ね",
        "な",
        "わね",
        "な",
        "な",
    ),
    718: (
        "ね",
        "な",
        "ね",
        "な",
        "ね",
        "な",
        "な",
    ),
    724: (
        "",
        "な",
        "",
        "な",
        "",
        "な",
        "な",
    ),
}

# Full matrices are retained even when this segment owns only part of a
# boundary group.  The 664 matrix is imported and asserted against S1014.
TRANSLATION_POLICY_BY_ROOT = {
    664: (
        "그러면",
        "그러면",
        "그렇다면",
        "그렇다면",
        "그럼",
        "그러면",
        "그럼",
    ),
    # In the only live PK caller, はずでは… is an unfinished contrast
    # ("...일 터인데…"), not the discourse transition "그럼".
    670: (
        "인데",
        "인데",
        "인데",
        "인데",
        "인데",
        "인데",
        "인데",
    ),
    676: (
        "이 아니다",
        "아닌",
        "이 아니다",
        "아닌",
        "이 아니다",
        "아니다",
        "이 아니다",
    ),
    682: (
        "이 아닙니다",
        "이 아니다",
        "이 아니옵니다",
        "이 아니옵니다",
        "이 아닙니다",
        "이 아니오",
        "아니다",
    ),
    # どう／いかが here is the predicate of a proposal question.  Adverbial
    # "어떻게" loses that function, so each voice receives a complete ending.
    688: (
        "어떻습니까",
        "어떠한가",
        "어떠하옵니까",
        "어떠하옵니까",
        "어떻습니까",
        "어떠하오",
        "어떠한가",
    ),
    694: (
        "비키시오",
        "비켜라",
        "비키시오",
        "비켜 주시오",
        "비켜 주십시오",
        "비키시오",
        "비켜라",
    ),
    # と is quotative in these forms; it does not mean accompaniment.
    700: (
        "라는 소식",
        "라는 소식",
        "라는 이야기",
        "라는 이야기",
        "라는 것",
        "라는 소식",
        "라는 이야기",
    ),
    706: (
        "지요",
        "군",
        "이지요",
        "군",
        "네요",
        "군",
        "군",
    ),
    712: (
        "네요",
        "군",
        "지요",
        "군",
        "네요",
        "군",
        "군",
    ),
    718: (
        "지요",
        "군",
        "지요",
        "군",
        "지요",
        "군",
        "군",
    ),
    724: (
        "",
        "군",
        "",
        "군",
        "",
        "군",
        "군",
    ),
}

EXPECTED_FULL_BASE_JP = {
    record_id: source
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, source in zip(
        record_ids,
        SOURCE_JP_BY_ROOT[root],
        strict=True,
    )
}
FULL_TRANSLATION_POLICY = {
    record_id: translation
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, translation in zip(
        record_ids,
        TRANSLATION_POLICY_BY_ROOT[root],
        strict=True,
    )
}
TRANSLATIONS_BY_RECORD = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in VISIBLE_RECORD_IDS
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

TARGET_ARCHIVE_DIGESTS = {
    "base_jp": "C891E2A486027EBD9D465F278A48E0CB95BD625025DE7843E5EB03BA7B624211",
    "base_current": "23771A96D85DCA48E40932AEA5D67B1107146AE3F07F1FE60729F78D5EEAF7C1",
    "base_sc": "A1F338430931FAD3E4695561104F0302AFECFA030E982D025A7784DA0C4FEF77",
    "base_tc": "A1F338430931FAD3E4695561104F0302AFECFA030E982D025A7784DA0C4FEF77",
    "pk_jp": "495FEF1F0B3ED95E6F465527F9E9A645BACC91C5D0486F7409C7168F760FB4DA",
    "pk_current": "18AC2024B8523AF39775D43125087DEE04E2A302A0666EBDB37528FAA7C0806B",
    "pk_sc": "5B15D45D8A17F676D4A5AF547FAFCF7836B5D67DE26E50CC042D1933DDB0146D",
    "pk_tc": "5B15D45D8A17F676D4A5AF547FAFCF7836B5D67DE26E50CC042D1933DDB0146D",
    "pk_en": "5B15D45D8A17F676D4A5AF547FAFCF7836B5D67DE26E50CC042D1933DDB0146D",
}
FULL_ARCHIVE_DIGESTS = {
    "base_jp": "714EFDF03A860AF4712D99FF0D794502DB49749C1E70630BB21DC586802031AC",
    "base_current": "D27AF829CF6E32C3AA036E9E180F8E2DCE128625B91F283522BE84B922A52499",
    "base_sc": "952D340A8C4C795F9EC94E59E9AFF4803D63C9F7997ECB1EB04FA74D6B3A008E",
    "base_tc": "952D340A8C4C795F9EC94E59E9AFF4803D63C9F7997ECB1EB04FA74D6B3A008E",
    "pk_jp": "D137B92A40D85BB5E7539C77F54102AE451D3C8292B54E95567ECF8799A070AC",
    "pk_current": "8A154D1A875C79B5D933EBB74B1616C4639D57E30D8D0351EC7E6DC29B7BF491",
    "pk_sc": "D171D8E3F333845640C1CB43EC7C675E0CDD406E9C22F04720456540BE986481",
    "pk_tc": "D171D8E3F333845640C1CB43EC7C675E0CDD406E9C22F04720456540BE986481",
    "pk_en": "D171D8E3F333845640C1CB43EC7C675E0CDD406E9C22F04720456540BE986481",
}

JUMP_EVIDENCE = {
    "base_jp": {
        "target": (69, "E2E9C630127A3A8EB52BC64E5B172A103CEEA0F3FD44C5B6D5BDA2D491CF603A"),
        "full": (77, "111F41F1F347F8FCAED6723BD198837A6DC5D07BBAE332F47A9F61939DE30C25"),
    },
    "base_current": {
        "target": (69, "E2E9C630127A3A8EB52BC64E5B172A103CEEA0F3FD44C5B6D5BDA2D491CF603A"),
        "full": (77, "111F41F1F347F8FCAED6723BD198837A6DC5D07BBAE332F47A9F61939DE30C25"),
    },
    "pk_jp": {
        "target": (69, "BADD8ECD6BA8CAF433C4F8357D9B078B2803A34C1FC07A88FE147F97D53D84D3"),
        "full": (77, "AC916E20D82FEBF20F843638932EDEA5F6AE2DED84C0CE7002515FECA897283B"),
    },
    "pk_current": {
        "target": (69, "BADD8ECD6BA8CAF433C4F8357D9B078B2803A34C1FC07A88FE147F97D53D84D3"),
        "full": (77, "AC916E20D82FEBF20F843638932EDEA5F6AE2DED84C0CE7002515FECA897283B"),
    },
}

EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EMPTY_EVIDENCE = (0, EMPTY_SHA256)
CALLER_ROW_EVIDENCE = {
    "base_jp": (137, "49ED7A1459EB3A1CF30BC5DC2246DEBC0116A580654C57370FFD7128475C4448"),
    "base_current": (125, "66707453163FB1BDCDC759E01138C22334EB4B97A6ADFCD7F74E8DCDAF19DF04"),
    "pk_jp": (205, "9BDD7A70185E556FDCADF054AA9C3AEFD412B1B82E5209A7C12ADC883D3D1FB7"),
    "pk_current": (191, "B369802F21623CDCBD340765ED25452F9C383E9A26639BED6AC52B4A30949983"),
}
CALL_EVIDENCE = {
    "base_jp": {
        682: (1, "B8A1A3BF8CA96C25A783C0AE1A6AF5C003FC0F0F651BCDC2B4448FE0754264A4"),
        688: (77, "1E38A5B09A44BEBB2A2C3F4B7F43561C11D61088EFC2978ED414FB11948C6329"),
        694: (1, "7495707CA822333A04E40B34DA34FB89E1FDD516DC277D8A2BD37C830BFAA3B0"),
        700: (8, "E49995C3882BBF69AC59E71F32BE382BF50B05056E346EA64C15C7946974E6EE"),
        706: (7, "07EF2E23CD9C616B80D79878D64C56F72C931612E7E84760CDD8312AC6BF2DDE"),
        712: (31, "9CF1A56A93D89D59446CB0C4FC9D613B02C0F1607926224F27C9B9F4786B90B7"),
        718: (9, "CE5C532CCE1DE24720CEEA5D59EB39FB43F5564B01C822EA37A13EC0B03A6F70"),
        724: (3, "AB93F4C33B23A605E62FA3F284BF083AA9C0128191C82F6D51A0A9B4283FEC77"),
    },
    "base_current": {
        682: (1, "B8A1A3BF8CA96C25A783C0AE1A6AF5C003FC0F0F651BCDC2B4448FE0754264A4"),
        688: (74, "8D8446F9833A20CCD1C29C456A5678867DCF60651BFE795B0B83B345A3FB4115"),
        694: (1, "7495707CA822333A04E40B34DA34FB89E1FDD516DC277D8A2BD37C830BFAA3B0"),
        700: (8, "E49995C3882BBF69AC59E71F32BE382BF50B05056E346EA64C15C7946974E6EE"),
        706: (5, "A2E873A0D2DAE438EC9129738F8F3A2C0F040E0BE81D7674D58BF485DDBE0D9D"),
        712: (28, "FB3FDCDC92DD58F1371A7F7600A82F33209AE6AFDC51B4FFDB47D2E44AE4AF63"),
        718: (5, "157F7EC4497100F26301EEEC63FEF966E18D3A8BD6F73CED070070FC15650FEB"),
        724: (3, "AB93F4C33B23A605E62FA3F284BF083AA9C0128191C82F6D51A0A9B4283FEC77"),
    },
    "pk_jp": {
        664: (1, "41B87A47A8C2C49A35E07822EF9D9F3B77089FF2BEF6EAC3E6E7F767EB6FA315"),
        670: (1, "BC8586A55249A5D465E6DE0B0689B718E942C1F40A1D2BA3572126FBB43AFFE0"),
        682: (2, "35F7B9EAF5E595D5B0AB0A0D4A3437F5658912EBE40C7972CFC3E4424A551EFB"),
        688: (82, "8250A596ACD0146C6E12341C3D9564A11438400E5D5E6ADC8ACDC6F4C604CFF5"),
        694: (1, "7495707CA822333A04E40B34DA34FB89E1FDD516DC277D8A2BD37C830BFAA3B0"),
        700: (17, "0437360DDCAD202FE243DB33D3A4BBFCBE5486E80C2FF8DF5266D4DC939F70F0"),
        706: (5, "370113EDBFC0535CC8D2A60751C9C9520346190916749BA14D58262881C9DEFF"),
        712: (33, "D2C6FE696B7833C84DEE689506F1561E7E059E3FBDA7CEA95E8ED0726E81FC05"),
        718: (46, "C69AC1D5E9BCC9FDC5733E2A0D96F57B82C92B0B8D2BE1BBC1972E95DE728280"),
        724: (17, "40C04B6B875A70DF08569BEE4F89E2AFC298B678F8D6F8C36DA28DC5EF26502D"),
    },
    "pk_current": {
        664: (1, "41B87A47A8C2C49A35E07822EF9D9F3B77089FF2BEF6EAC3E6E7F767EB6FA315"),
        670: (1, "BC8586A55249A5D465E6DE0B0689B718E942C1F40A1D2BA3572126FBB43AFFE0"),
        682: (2, "35F7B9EAF5E595D5B0AB0A0D4A3437F5658912EBE40C7972CFC3E4424A551EFB"),
        688: (78, "C8851854CEC84F3D1FAFC31BE009330C2D58A4C95D8E4002A589E5C50D8BB473"),
        694: (1, "7495707CA822333A04E40B34DA34FB89E1FDD516DC277D8A2BD37C830BFAA3B0"),
        700: (17, "0437360DDCAD202FE243DB33D3A4BBFCBE5486E80C2FF8DF5266D4DC939F70F0"),
        706: (3, "F8B5E6D26F3CE6581F992B68CFE9BA55CD928500240868562A5EF134569EF364"),
        712: (30, "3F80B31CE275E4FF38ED0471F88A421ADD8C16508CA808066DD7B1BE3BD33E1A"),
        718: (41, "1B3D50BB1C47C6C093F9A6A64532111463AD02E2C18BB96E18FE7B3C60B10694"),
        724: (17, "40C04B6B875A70DF08569BEE4F89E2AFC298B678F8D6F8C36DA28DC5EF26502D"),
    },
}
FIXED_FOLLOWING_EVIDENCE = {
    "base_jp": {
        688: (77, "DC9ABEC61963802E4F4F93DB223D73CAB56AE748A0B7A6FF203D44F40C8DFB52"),
        700: (1, "65A91F138806A8F87422B0FF25BDE3471F8EFCA53304C759B2575E835CC44CB2"),
    },
    "base_current": {
        688: (74, "3BF476B814FB9ADBB56925A0AEA71C9BFA0826D1D5A26F60FE3E875B70BAA908"),
        700: (1, "65A91F138806A8F87422B0FF25BDE3471F8EFCA53304C759B2575E835CC44CB2"),
    },
    "pk_jp": {
        664: (1, "E3B541C7617AC178499A323EA328BE0557F1ECE5A31F89C565F1E6E24DE678A6"),
        682: (1, "5250FFEDFDE03DAE7A812E32759ED287272248B2F6D02AC583B0140D529C02EA"),
        688: (82, "63FB6FE3F70C1DAFDEBBB60FA88982D0248340961E394D6024CA175A5B94C71B"),
        700: (1, "0CEF8425C772184E93DD344DBFD867D677700C59177821DA0F0D6BF148DC73F6"),
    },
    "pk_current": {
        664: (1, "E3B541C7617AC178499A323EA328BE0557F1ECE5A31F89C565F1E6E24DE678A6"),
        682: (1, "5250FFEDFDE03DAE7A812E32759ED287272248B2F6D02AC583B0140D529C02EA"),
        688: (77, "AB3B1BE2C33843C4042CB280F47E72DD4A65E57B88CBBBB456229D7B6C025699"),
        700: (1, "0CEF8425C772184E93DD344DBFD867D677700C59177821DA0F0D6BF148DC73F6"),
        724: (1, "F30C384CD12042D6F322A90F8479D2121D168FC4BCAEECD057705F1BEB870F94"),
    },
}
FLATTEN_EVIDENCE = {
    "base": {
        688: (3, "9FDA36597C689588F2CCAFC12582155D9BFDE7BC9B4DF7AA6A155E8567DAB947"),
        706: (2, "340DA74AA1E5CD85292E10C278747BB102B8F3222EB7207EA420C8850BA0EC94"),
        712: (3, "3FB7514D6FE6442E149125D6C20F012627AA4D23CF4C3B148051DEFFB8F7E46A"),
        718: (4, "91AA6D900BFDCDBAB0693052C6012497360777B51F8C205F633242A0D60AF23D"),
    },
    "pk": {
        688: (4, "1FFF5B11C30A7220DF61D2BB412CE259BE248FF2A8BA78AA6262B1610532706B"),
        706: (2, "340DA74AA1E5CD85292E10C278747BB102B8F3222EB7207EA420C8850BA0EC94"),
        712: (3, "6E783636DCF4F155831E748967C93FF8407D7FA0F1E89C6FF830F9D5CA291E95"),
        718: (5, "A1FA1443A8605C8642C1825189E74991BA2ADBDB8E678EBFC0EDA29BB6DBEDCD"),
    },
}
HIDDEN_RECORD_SHA256 = (
    "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"
)

BASIS = (
    "review_queue_base_msggame_B005_C_pristine_base_pc_jp_authoritative_"
    "block0_runtime_terminal_records2014_2082_visible67_hidden2079_2081_"
    "imported_S1014_root664_boundary_policy_2014_then_2015_casual_then_"
    "actual_full_seven_voice_014a_closures_unique_exact_tuple_pk_reverse_"
    "mapping_plus68_after_two_pk_only_insertions_root_shift_plus12_no_new_"
    "insertion_jp_current_sc_tc_exact_pk_en_empty_target_and_full_archive_"
    "digests_0143_caller_rows_source_current_flattening_fixed_following_"
    "and_standalone014c_evidence_contrast_copula_proposal_question_"
    "honorific_imperative_quotative_report_and_terminal_particle_matrices_"
    "hidden_records_exact_one_line_skeleton_reverse_overlay_exact_runtime_"
    "caller_rewrite_pending_no_historic_or_switch_korean_authority"
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


def expected_evidence(
    evidence: dict[str, dict[int, tuple[int, str]]],
    label: str,
    root: int,
) -> tuple[int, str]:
    return evidence.get(label, {}).get(root, EMPTY_EVIDENCE)


def assert_prior_boundary() -> None:
    if (
        PRIOR.SOURCE_JP_BY_ROOT[664] != SOURCE_JP_BY_ROOT[664]
        or PRIOR.TRANSLATION_POLICY_BY_ROOT[664]
        != TRANSLATION_POLICY_BY_ROOT[664]
        or PRIOR.CROSS_SEGMENT_SOURCE_JP[2014] != "では"
        or PRIOR.CROSS_SEGMENT_SOURCE_JP[2015] != "じゃあ"
        or PRIOR.CROSS_SEGMENT_CURRENT_KO[2014] != "그럼"
        or PRIOR.CROSS_SEGMENT_CURRENT_KO[2015] != "그럼"
        or PRIOR.CROSS_SEGMENT_TRANSLATION_POLICY[2014] != "그러면"
        or PRIOR.CROSS_SEGMENT_TRANSLATION_POLICY[2015] != "그럼"
        or FULL_TRANSLATION_POLICY[2014] != "그러면"
        or FULL_TRANSLATION_POLICY[2015] != "그럼"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} imported S1014 boundary drifted"
        )


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    assert_prior_boundary()
    labels = (
        "base_jp",
        "base_current",
        "base_sc",
        "base_tc",
        "pk_jp",
        "pk_current",
        "pk_sc",
        "pk_tc",
        "pk_en",
    )
    for label in labels:
        target_keys = (
            tuple((BLOCK_ID, PK_RECORD_MAP[value]) for value in TARGET_RECORD_IDS)
            if label.startswith("pk_")
            else RECORD_KEYS
        )
        full_keys = (
            tuple((BLOCK_ID, PK_RECORD_MAP[value]) for value in FULL_RECORD_IDS)
            if label.startswith("pk_")
            else tuple((BLOCK_ID, value) for value in FULL_RECORD_IDS)
        )
        if (
            GENERAL.subset_digest(records_by_label[label], target_keys)
            != TARGET_ARCHIVE_DIGESTS[label]
            or GENERAL.subset_digest(records_by_label[label], full_keys)
            != FULL_ARCHIVE_DIGESTS[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} corpus drifted"
            )

    for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items():
        expected_tuple = tuple(
            EXPECTED_FULL_BASE_JP[record_id]
            for record_id in base_record_ids
        )
        pk_root = PK_ROOT_BY_BASE[base_root]
        pk_record_ids = PK_FULL_TERMINAL_GROUPS[pk_root]
        starts = EVIDENCE.sequence_starts(
            records_by_label["pk_jp"],
            expected_tuple,
        )
        if starts != (pk_record_ids[0],):
            raise RuntimeError(
                f"segment {SEGMENT} unique PK tuple search drifted: "
                f"{base_root}/{starts}"
            )
        if tuple(
            PK_RECORD_MAP[record_id] for record_id in base_record_ids
        ) != pk_record_ids:
            raise RuntimeError(
                f"segment {SEGMENT} explicit PK mapping drifted: "
                f"{base_root}/{pk_root}"
            )

    if (
        {PK_RECORD_MAP[value] - value for value in FULL_RECORD_IDS}
        != {68}
        or {
            PK_ROOT_BY_BASE[root] - root
            for root in FULL_TERMINAL_GROUPS
        }
        != {12}
    ):
        raise RuntimeError(
            f"segment {SEGMENT} insertion/offset proof drifted"
        )

    for record_id in FULL_RECORD_IDS:
        base_key = (BLOCK_ID, record_id)
        pk_key = (BLOCK_ID, PK_RECORD_MAP[record_id])
        if literal_texts(records_by_label["base_jp"], base_key) != (
            EXPECTED_FULL_BASE_JP[record_id],
        ):
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
            if literal_texts(
                records_by_label[f"base_{language}"],
                base_key,
            ) != literal_texts(
                records_by_label[f"pk_{language}"],
                pk_key,
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base/PK literal drifted: "
                    f"{language}/{base_key}/{pk_key}"
                )
        if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {pk_key}"
            )

    for record_id in (*HIDDEN_RECORD_IDS, 2083):
        for label in labels:
            key = (
                (BLOCK_ID, PK_RECORD_MAP[record_id])
                if label.startswith("pk_")
                else (BLOCK_ID, record_id)
            )
            record = records_by_label[label][key]
            if (
                literal_texts(records_by_label[label], key) != ("",)
                or hashlib.sha256(record.data).hexdigest().upper()
                != HIDDEN_RECORD_SHA256
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
    target_base_ids = set(TARGET_RECORD_IDS)
    target_pk_ids = {PK_RECORD_MAP[value] for value in TARGET_RECORD_IDS}

    for label in ("base_jp", "base_current", "pk_jp", "pk_current"):
        edition = label.split("_", 1)[0]
        records = records_by_label[label]
        full_ids = full_pk_ids if edition == "pk" else full_base_ids
        target_ids = (
            target_pk_ids if edition == "pk" else target_base_ids
        )
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
                    f"segment {SEGMENT} {label} {scope} "
                    "incoming 014A drifted"
                )

        edges = GRAPH.graph_edges(records)
        for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items():
            actual_root = (
                PK_ROOT_BY_BASE[base_root]
                if edition == "pk"
                else base_root
            )
            expected_ids = (
                set(
                    PK_FULL_TERMINAL_GROUPS[
                        PK_ROOT_BY_BASE[base_root]
                    ]
                )
                if edition == "pk"
                else set(base_record_ids)
            )
            closure = GRAPH.graph_closure(edges, actual_root)
            if (
                len(closure) != 13
                or closure.intersection(full_ids) != expected_ids
            ):
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
            (
                PK_ROOT_BY_BASE[root]
                if edition == "pk"
                else root
            )
            for root in FULL_TERMINAL_GROUPS
            if expected_evidence(CALL_EVIDENCE, label, root)[0]
        }
        if set(caller_sites) != expected_roots:
            raise RuntimeError(
                f"segment {SEGMENT} {label} caller root universe drifted"
            )

        for root in FULL_TERMINAL_GROUPS:
            actual_root = (
                PK_ROOT_BY_BASE[root] if edition == "pk" else root
            )
            sites = caller_sites.get(actual_root, ())
            call_count, call_sha256 = expected_evidence(
                CALL_EVIDENCE,
                label,
                root,
            )
            if (
                len(sites) != call_count
                or digest_sites(sites) != call_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} caller sites drifted: "
                    f"{root}/{actual_root}"
                )
            blockers = FIXED.fixed_following_blockers(
                records,
                actual_root,
            )
            blocker_count, blocker_sha256 = expected_evidence(
                FIXED_FOLLOWING_EVIDENCE,
                label,
                root,
            )
            if (
                len(blockers) != blocker_count
                or digest_sites(blockers) != blocker_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} fixed-following "
                    f"drifted: {root}/{actual_root}"
                )

        if EVIDENCE.relevant_standalone_014c(records, full_ids):
            raise RuntimeError(
                f"segment {SEGMENT} {label} relevant standalone "
                "014C appeared"
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
        for root in FULL_TERMINAL_GROUPS:
            actual_root = (
                PK_ROOT_BY_BASE[root] if edition == "pk" else root
            )
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
            expected_count, expected_sha256 = expected_evidence(
                FLATTEN_EVIDENCE,
                edition,
                root,
            )
            if (
                current_only
                or len(flattened) != expected_count
                or digest_sites(flattened) != expected_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} source/current "
                    f"flattening drifted: {root}/{actual_root}"
                )


def assert_semantics(
    current_records: dict[tuple[int, int], Any],
    translations: dict[str, str],
) -> None:
    if (
        len(TARGET_RECORD_IDS) != 69
        or len(VISIBLE_RECORD_IDS) != 67
        or set(HIDDEN_RECORD_IDS) != {2079, 2081}
        or set(TRANSLATIONS_BY_RECORD) != set(VISIBLE_RECORD_IDS)
        or translations != TRANSLATIONS
        or set(FULL_TRANSLATION_POLICY) != set(FULL_RECORD_IDS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
        )
    if any(FULL_TRANSLATION_POLICY[value] for value in HIDDEN_RECORD_IDS):
        raise RuntimeError(
            f"segment {SEGMENT} hidden policy became visible"
        )
    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        actual = tuple(
            FULL_TRANSLATION_POLICY[record_id]
            for record_id in record_ids
        )
        if actual != TRANSLATION_POLICY_BY_ROOT[root]:
            raise RuntimeError(
                f"segment {SEGMENT} register matrix drifted: {root}"
            )
    for coordinate, translation in translations.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(
            current_records,
            (BLOCK_ID, record_id),
        )[0]
        if (
            not ENGINE.is_visible_translation_candidate(current_text)
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
            or UTIL.layout_signature(translation)
            != UTIL.layout_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} visible text drifted: {coordinate}"
            )
    for record_id in HIDDEN_RECORD_IDS:
        if ENGINE.is_visible_translation_candidate(
            literal_texts(
                current_records,
                (BLOCK_ID, record_id),
            )[0]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} hidden record became visible: "
                f"{record_id}"
            )


def assert_hidden_candidate_exact(
    prepared: Any,
    translations: dict[str, str],
    expected_sha256: str,
) -> None:
    base = prepared.resources["base_msggame"]
    replacements = {
        tuple(int(value) for value in coordinate.split(":")): translation
        for coordinate, translation in translations.items()
    }
    rebuilt = ENGINE.rebuild_packed_with_literals(
        base.current_blob,
        replacements,
    )
    if hashlib.sha256(rebuilt).hexdigest().upper() != expected_sha256:
        raise RuntimeError(
            f"segment {SEGMENT} candidate hash path drifted"
        )
    current_records = ENGINE.archive_records(base.current_archive)
    candidate_records = ENGINE.archive_records(
        ENGINE.parse_packed_msggame(rebuilt).archive
    )
    for record_id in HIDDEN_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        if candidate_records[key].data != current_records[key].data:
            raise RuntimeError(
                f"segment {SEGMENT} hidden candidate drifted: {key}"
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

    translations = dict(TRANSLATIONS)
    current = records_by_label["base_current"]
    assert_semantics(current, translations)
    candidate_sha256 = GENERAL.assert_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        target_records=set(RECORD_KEYS),
    )
    assert_hidden_candidate_exact(
        prepared,
        translations,
        candidate_sha256,
    )

    root_by_record = {
        record_id: root
        for root, record_ids in FULL_TERMINAL_GROUPS.items()
        for record_id in record_ids
        if record_id in VISIBLE_RECORD_IDS
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
                    "base_pk_record_offset": 68,
                    "base_pk_root_shift": 12,
                    "automatic_space_inserted": False,
                    "full_group_closure_node_count": 13,
                    "full_terminal_record_ids": list(
                        FULL_TERMINAL_GROUPS[root]
                    ),
                    "pk_full_terminal_record_ids": list(
                        PK_FULL_TERMINAL_GROUPS[pk_root]
                    ),
                    "base_source_call_count": expected_evidence(
                        CALL_EVIDENCE,
                        "base_jp",
                        root,
                    )[0],
                    "base_current_call_count": expected_evidence(
                        CALL_EVIDENCE,
                        "base_current",
                        root,
                    )[0],
                    "pk_source_call_count": expected_evidence(
                        CALL_EVIDENCE,
                        "pk_jp",
                        root,
                    )[0],
                    "pk_current_call_count": expected_evidence(
                        CALL_EVIDENCE,
                        "pk_current",
                        root,
                    )[0],
                    "base_source_only_flattened_call_count": (
                        expected_evidence(
                            FLATTEN_EVIDENCE,
                            "base",
                            root,
                        )[0]
                    ),
                    "base_source_only_flattened_call_sha256": (
                        expected_evidence(
                            FLATTEN_EVIDENCE,
                            "base",
                            root,
                        )[1]
                    ),
                    "pk_source_only_flattened_call_count": (
                        expected_evidence(
                            FLATTEN_EVIDENCE,
                            "pk",
                            root,
                        )[0]
                    ),
                    "pk_source_only_flattened_call_sha256": (
                        expected_evidence(
                            FLATTEN_EVIDENCE,
                            "pk",
                            root,
                        )[1]
                    ),
                    "base_current_fixed_following_count": (
                        expected_evidence(
                            FIXED_FOLLOWING_EVIDENCE,
                            "base_current",
                            root,
                        )[0]
                    ),
                    "base_current_fixed_following_sha256": (
                        expected_evidence(
                            FIXED_FOLLOWING_EVIDENCE,
                            "base_current",
                            root,
                        )[1]
                    ),
                    "pk_current_fixed_following_count": (
                        expected_evidence(
                            FIXED_FOLLOWING_EVIDENCE,
                            "pk_current",
                            root,
                        )[0]
                    ),
                    "pk_current_fixed_following_sha256": (
                        expected_evidence(
                            FIXED_FOLLOWING_EVIDENCE,
                            "pk_current",
                            root,
                        )[1]
                    ),
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
    if (
        len(rows) != 67
        or len(validated) != 67
        or len(translations) != 67
    ):
        raise RuntimeError(
            f"segment {SEGMENT} validation count drifted"
        )
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
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B005_S1015",
                "queue": QUEUE_BATCH_ID,
                "source_record_count": len(TARGET_RECORD_IDS),
                "source_literal_count": len(TARGET_RECORD_IDS),
                "visible_literal_count": len(VISIBLE_RECORD_IDS),
                "decision_count": len(rows),
                "hidden_non_display_count": len(HIDDEN_RECORD_IDS),
                "hidden_non_display_record_ids": list(HIDDEN_RECORD_IDS),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_semantic_record_offset": 68,
                "base_pk_root_shift": 12,
                "pk_only_terminal_family_insertions_before_segment": 2,
                "new_pk_insertion_in_segment": False,
                "base_pk_jp_current_sc_tc_literal_divergence_records": [],
                "base_pk_jp_current_sc_tc_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in FULL_TERMINAL_GROUPS.items()
                },
                "pk_full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids
                    in PK_FULL_TERMINAL_GROUPS.items()
                },
                "pk_root_by_base": PK_ROOT_BY_BASE,
                "imported_s1014_boundary_policy": {
                    "2014": FULL_TRANSLATION_POLICY[2014],
                    "2015": FULL_TRANSLATION_POLICY[2015],
                },
                "target_jump_evidence": {
                    label: evidence["target"]
                    for label, evidence in JUMP_EVIDENCE.items()
                },
                "full_jump_evidence": {
                    label: evidence["full"]
                    for label, evidence in JUMP_EVIDENCE.items()
                },
                "caller_row_evidence": CALLER_ROW_EVIDENCE,
                "call_evidence": CALL_EVIDENCE,
                "flatten_evidence": FLATTEN_EVIDENCE,
                "fixed_following_evidence": (
                    FIXED_FOLLOWING_EVIDENCE
                ),
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "hidden_candidate_records_exact": True,
                "target_runtime_skeleton_exact": True,
                "protected_signature_exact": True,
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
