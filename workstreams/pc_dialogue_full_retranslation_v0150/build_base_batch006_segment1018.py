#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1018 decisions."""

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
import build_base_batch005_segment1017 as PRIOR


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
    / "base_msggame_B006_S1018.private.v1.jsonl"
)
SEGMENT = 1018
QUEUE_BATCH_ID = "base_msggame-B006"
BLOCK_ID = 0
RECORD_IDS = tuple(range(2217, 2284))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
FULL_RECORD_IDS = tuple(range(2212, 2289))

# These keys are the actual Base 014A roots.  The final two families reuse
# roots 520 and 526; 892 and 898 would merely be ordinal guesses.
FULL_TERMINAL_GROUPS = {
    838: tuple(range(2212, 2219)),
    844: tuple(range(2219, 2226)),
    850: tuple(range(2226, 2233)),
    856: tuple(range(2233, 2240)),
    862: tuple(range(2240, 2247)),
    868: tuple(range(2247, 2254)),
    874: tuple(range(2254, 2261)),
    880: tuple(range(2261, 2268)),
    886: tuple(range(2268, 2275)),
    520: tuple(range(2275, 2282)),
    526: tuple(range(2282, 2289)),
}

# Each tuple was independently reverse-searched in pristine PK JP.  Record
# positions remain +68 after the same two earlier PK-only terminal-family
# insertions.  The reused final roots advance by +6 rather than +12.
PK_FULL_TERMINAL_GROUPS = {
    850: tuple(range(2280, 2287)),
    856: tuple(range(2287, 2294)),
    862: tuple(range(2294, 2301)),
    868: tuple(range(2301, 2308)),
    874: tuple(range(2308, 2315)),
    880: tuple(range(2315, 2322)),
    886: tuple(range(2322, 2329)),
    892: tuple(range(2329, 2336)),
    898: tuple(range(2336, 2343)),
    526: tuple(range(2343, 2350)),
    532: tuple(range(2350, 2357)),
}
PK_ROOT_BY_BASE = {
    838: 850,
    844: 856,
    850: 862,
    856: 868,
    862: 874,
    868: 880,
    874: 886,
    880: 892,
    886: 898,
    520: 526,
    526: 532,
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
    838: (
        "のです",
        "のだ",
        "のです",
        "のです",
        "のです",
        "のだ",
        "のじゃ",
    ),
    844: (
        "のです",
        "のだ",
        "のでございます",
        "のです",
        "んです",
        "のです",
        "んだ",
    ),
    850: (
        "はい",
        "はい",
        "はい",
        "ははっ",
        "はい",
        "はっ",
        "はっ",
    ),
    856: (
        "びません",
        "ばぬ",
        "びませぬ",
        "びませぬ",
        "びません",
        "びませぬ",
        "ばん",
    ),
    862: (
        "びなさい",
        "べ",
        "びなされ",
        "びなされ",
        "びなさい",
        "びなされ",
        "ぶがよい",
    ),
    868: (
        "べません",
        "べぬ",
        "べませぬ",
        "べませぬ",
        "べません",
        "べませぬ",
        "べん",
    ),
    874: (
        "まあ",
        "ほう",
        "なんと",
        "ほほう",
        "まあ",
        "ふむ",
        "ほほう",
    ),
    880: (
        "びましょう",
        "ぼう",
        "びましょう",
        "びましょうぞ",
        "びましょう",
        "びましょう",
        "ばん",
    ),
    886: (
        "ほしい",
        "ほしい",
        "いただきたい",
        "いただきたい",
        "ほしい",
        "ほしい",
        "ほしい",
    ),
    520: (
        "参りました",
        "参った",
        "参りました",
        "参りました",
        "参りました",
        "参った",
        "参った",
    ),
    526: (
        "ください",
        "参れ",
        "くださいませ",
        "くださりませ",
        "ください",
        "くだされ",
        "参れ",
    ),
}

TRANSLATION_POLICY_BY_ROOT = {
    838: (
        "것입니다",
        "것이다",
        "것입니다",
        "것입니다",
        "것입니다",
        "것이다",
        "것이니라",
    ),
    844: (
        "것입니다",
        "것이다",
        "것이옵니다",
        "것입니다",
        "것입니다",
        "것입니다",
        "것이다",
    ),
    # Keep the military acknowledgement used by the already-approved
    # B002 matrix: ははっ/はっ are 옛, while neutral はい is 예.
    850: ("예", "예", "예", "옛", "예", "옛", "옛"),
    856: (
        "하지 않습니다",
        "하지 않는다",
        "하지 않사옵니다",
        "하지 않사옵니다",
        "하지 않습니다",
        "하지 않사옵니다",
        "하지 않는다",
    ),
    862: (
        "하시오",
        "하라",
        "하시오",
        "하시오",
        "하시오",
        "하시오",
        "하라",
    ),
    # 呼べません is assembled from the caller's verb stem plus this bound
    # inability suffix: 부르 + 지 못합니다.
    868: (
        "지 못합니다",
        "지 못한다",
        "지 못하옵니다",
        "지 못하옵니다",
        "지 못합니다",
        "지 못하옵니다",
        "지 못한다",
    ),
    874: (
        "어머",
        "호오",
        "이럴 수가",
        "호오",
        "어머",
        "흠",
        "호오",
    ),
    880: (
        "합시다",
        "하자",
        "합시다",
        "합시다",
        "합시다",
        "합시다",
        "하자",
    ),
    886: (
        "해 주었으면 합니다",
        "해 주었으면 한다",
        "해 주시기를 바라옵니다",
        "해 주시기를 바라옵니다",
        "해 주었으면 합니다",
        "해 주었으면 하오",
        "해 주었으면 한다",
    ),
    # These are the auxiliary て参る ("do and return") family, not the
    # standalone defeat idiom 参った.
    520: (
        "왔습니다",
        "왔다",
        "왔사옵니다",
        "왔사옵니다",
        "왔습니다",
        "왔소",
        "왔다",
    ),
    # In the only Base caller, ついて参れ means "follow/come along"; "가라"
    # reverses the direction.
    526: (
        "주십시오",
        "오너라",
        "주시옵소서",
        "주시옵소서",
        "주십시오",
        "주시오",
        "오너라",
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
    for record_id in RECORD_IDS
}
TRANSLATIONS = {
    f"{BLOCK_ID}:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

TARGET_ARCHIVE_DIGESTS = {
    "base_jp": "81E5D7580AABA206EC0699695E3023A129392B31006B6612061D42F0C99E7033",
    "base_current": "2E147F280F13EB6050F5D4CDBA6A179132B3A774BCEE971497AD0FAE7D4B3B03",
    "base_sc": "04B9DC4F762C338E993E451B27E454EB0249397F0F0B2C139D7E330FC29FFC9F",
    "base_tc": "04B9DC4F762C338E993E451B27E454EB0249397F0F0B2C139D7E330FC29FFC9F",
    "pk_jp": "2A402F68C536B49EBC051A526051C2BDAD99E117C28F0E1DD28F7431AF03858F",
    "pk_current": "13BA592C92CAD2923A829B2FB712E142BAC81A6A379FE35BE3FA410DCA742DC9",
    "pk_sc": "74C4FC5138333D0B9D933CF4F81A40E40661D03BC4517178CC24E4C8FFE810E9",
    "pk_tc": "74C4FC5138333D0B9D933CF4F81A40E40661D03BC4517178CC24E4C8FFE810E9",
    "pk_en": "74C4FC5138333D0B9D933CF4F81A40E40661D03BC4517178CC24E4C8FFE810E9",
}
FULL_ARCHIVE_DIGESTS = {
    "base_jp": "9D804C3742E656E3CD17DAB067049433E886B14A26BD9B64B37661E64893F50F",
    "base_current": "C6AC6AF79EB95D82EF2CBE1DABB5620EC3B986D7F0FCB63583C6212168B06854",
    "base_sc": "8D3F636E5F99A4304D1C4F81D9019806E5F843436416467BB5E5A1FCB972F933",
    "base_tc": "8D3F636E5F99A4304D1C4F81D9019806E5F843436416467BB5E5A1FCB972F933",
    "pk_jp": "183C85881C04F8B6CCD046EB2D9C299108F8606ACAE4972288C495B8D37B9DE8",
    "pk_current": "548CD11BE6C1365C690E4BA772280ED3A887CC736B6FCAF436E0C5C30F20BA19",
    "pk_sc": "14459A1575452A7834517EF7AB65BACDD717C4D8B3F35DB1D28B25734D3F4F21",
    "pk_tc": "14459A1575452A7834517EF7AB65BACDD717C4D8B3F35DB1D28B25734D3F4F21",
    "pk_en": "14459A1575452A7834517EF7AB65BACDD717C4D8B3F35DB1D28B25734D3F4F21",
}

JUMP_EVIDENCE = {
    "base_jp": {
        "target": (67, "F5461C690D06222238374B6636E96620DE294E0CC336460E578FD54EBD9B3622"),
        "full": (77, "8F14551F194FF1DB6ADCCFA1EDA8EB629DDC24DE4E353AD9666915E7C035CC65"),
    },
    "base_current": {
        "target": (67, "F5461C690D06222238374B6636E96620DE294E0CC336460E578FD54EBD9B3622"),
        "full": (77, "8F14551F194FF1DB6ADCCFA1EDA8EB629DDC24DE4E353AD9666915E7C035CC65"),
    },
    "pk_jp": {
        "target": (67, "1F030903644C1FF25880980E04EA16A7AC6FFE89A15FCC12221DFF3905095A37"),
        "full": (77, "E3B0CCCD19440E74877D283F2E05AE4EFEFA95908FBE972D6748811FC5EBA999"),
    },
    "pk_current": {
        "target": (67, "1F030903644C1FF25880980E04EA16A7AC6FFE89A15FCC12221DFF3905095A37"),
        "full": (77, "E3B0CCCD19440E74877D283F2E05AE4EFEFA95908FBE972D6748811FC5EBA999"),
    },
}

EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EMPTY_EVIDENCE = (0, EMPTY_SHA256)
CALLER_ROW_EVIDENCE = {
    "base_jp": (48, "9F0E1F9F7D4FA5FA5086EAB8810B26AEBC0D1EAEC2A02DCED2C58FDF3F2B1CB1"),
    "base_current": (45, "4E163A4536B02B1279400CFD7882EAFA3C16A88B3B3A50E2EBCD80FC51127BA5"),
    "pk_jp": (67, "A9FC2F3500ABAA8A17FA8524141FDA9E64F9FA8B9677B7B23FE05B134C2D1007"),
    "pk_current": (62, "4FBB337F5A24DD3C4A4D49298F01CAAA3FEFF59ADA56DB0120A31F7602268D53"),
}
CALL_EVIDENCE = {
    "base_jp": {
        838: (5, "386D75398802049CAF10967744E2F7794CFA83B4D159A1EC9A339E2D6855663A"),
        844: (2, "9612B25D8275416251220FD4E3A275109DFF344E0252FF154ABC1D84004139E0"),
        850: (28, "3DA046E7215A53894CB1DD39D32B918830229DB3792EFEB311717D08EB114E8B"),
        856: (1, "CC23C546163B2F0CB47B5A778CA16A1DE8F2F1C5C20ADE5029A8AC2BA1737095"),
        862: (1, "DD882868AFE4E7295EA550C0FEEB5E35079E13D860667EDD3B67306D1739D997"),
        868: (1, "E95508D6669595D406C1C134F5CC92E55D723036788851C14040F786334EFE74"),
        874: (1, "803FE9F264CD69EAE7FD3B99F8CEB5B67D58FAC710E7A47C77C48FD279F217CA"),
        880: (2, "45A213E234277A6077F9052D8F1E224076C9B193EFBF2CC2AF4260F0E0702DF7"),
        886: (3, "18D229560421312F89FB0CA7A637937B8B80DF613A5A391B8BE0323B5EF10D90"),
        520: (3, "7A0C37F2070F7E854619F536856E3A29EF42E63D0B1754FF2CC4E33E752EC238"),
        526: (1, "F43F97E56B81DDBFDEAD4A8B15DD9013C1305890CD21EA4A8A73529C89D8EFE8"),
    },
    "base_current": {
        838: (3, "068E76508CE9796416F511CA07DD7C1A3CADE9F514B7F736D1E32B8AA2D50641"),
        844: (2, "9612B25D8275416251220FD4E3A275109DFF344E0252FF154ABC1D84004139E0"),
        850: (27, "69543BC4D5999DE006554EC6B62B8230DDC756EC578EFF04880525ED882BE80C"),
        856: (1, "CC23C546163B2F0CB47B5A778CA16A1DE8F2F1C5C20ADE5029A8AC2BA1737095"),
        862: (1, "DD882868AFE4E7295EA550C0FEEB5E35079E13D860667EDD3B67306D1739D997"),
        868: (1, "E95508D6669595D406C1C134F5CC92E55D723036788851C14040F786334EFE74"),
        874: (1, "803FE9F264CD69EAE7FD3B99F8CEB5B67D58FAC710E7A47C77C48FD279F217CA"),
        880: (2, "45A213E234277A6077F9052D8F1E224076C9B193EFBF2CC2AF4260F0E0702DF7"),
        886: (3, "18D229560421312F89FB0CA7A637937B8B80DF613A5A391B8BE0323B5EF10D90"),
        520: (3, "7A0C37F2070F7E854619F536856E3A29EF42E63D0B1754FF2CC4E33E752EC238"),
        526: (1, "F43F97E56B81DDBFDEAD4A8B15DD9013C1305890CD21EA4A8A73529C89D8EFE8"),
    },
    "pk_jp": {
        838: (9, "C01254ABE9AA76291E9C7D8E5BDFDB75C02BE274F3CF77ACB530FC107B6AE68C"),
        844: (2, "6512CCBE1341B46A31ECED093D528EB76DDC17E85097E57DB66E1C53F4EC2C45"),
        850: (29, "631225C2F3CEC7F3AAB8D473840379F52BF8BE76BFEF8344351AC27D7CDAC5C9"),
        856: (1, "CC23C546163B2F0CB47B5A778CA16A1DE8F2F1C5C20ADE5029A8AC2BA1737095"),
        862: (1, "DD882868AFE4E7295EA550C0FEEB5E35079E13D860667EDD3B67306D1739D997"),
        868: (1, "E95508D6669595D406C1C134F5CC92E55D723036788851C14040F786334EFE74"),
        874: (7, "ED52DF7AA863F8E3628B434BA5DA7222AEECE552C30314FF9598BC80D5F989B4"),
        880: (2, "3A405FBBBB40A85E9AA58C7C08FBBD8D1B44591CCF1C1E986C6A2FE9A3D81F60"),
        886: (8, "89EB4A0C89DF644DC83865B36E255E3EFBFDD683AB2AE4C0CBE066DBBB16A197"),
        520: (6, "65FA55FD70C48B57F72896594D34DCD188C97B25CDCD85C1DF567CCA32B26021"),
        526: (1, "F43F97E56B81DDBFDEAD4A8B15DD9013C1305890CD21EA4A8A73529C89D8EFE8"),
    },
    "pk_current": {
        838: (5, "5494C321FC53014DFF330000FD6A67E6FE96A589E41A50778325C39B1ECCE2F3"),
        844: (2, "6512CCBE1341B46A31ECED093D528EB76DDC17E85097E57DB66E1C53F4EC2C45"),
        850: (28, "8523625F91D8CFBEB2015431CDF55DAEC89BBE6642A85A2EFC3F346E41F2E45C"),
        856: (1, "CC23C546163B2F0CB47B5A778CA16A1DE8F2F1C5C20ADE5029A8AC2BA1737095"),
        862: (1, "DD882868AFE4E7295EA550C0FEEB5E35079E13D860667EDD3B67306D1739D997"),
        868: (1, "E95508D6669595D406C1C134F5CC92E55D723036788851C14040F786334EFE74"),
        874: (7, "ED52DF7AA863F8E3628B434BA5DA7222AEECE552C30314FF9598BC80D5F989B4"),
        880: (2, "3A405FBBBB40A85E9AA58C7C08FBBD8D1B44591CCF1C1E986C6A2FE9A3D81F60"),
        886: (8, "89EB4A0C89DF644DC83865B36E255E3EFBFDD683AB2AE4C0CBE066DBBB16A197"),
        520: (6, "65FA55FD70C48B57F72896594D34DCD188C97B25CDCD85C1DF567CCA32B26021"),
        526: (1, "F43F97E56B81DDBFDEAD4A8B15DD9013C1305890CD21EA4A8A73529C89D8EFE8"),
    },
}

FIXED_FOLLOWING_EVIDENCE = {
    "base_jp": {
        844: (1, "CBDE29E6CE324C3C43CEF0E964C58A7702DF2D6F94D94D10A7EF7890A2EDB019"),
        868: (1, "05729897E44C56524FB8D53C2CBCBE7E65860E2C0A924C17DC00FBFBE531D4CB"),
        886: (1, "6EDFAB93DD466B3E715A0ED9A7FC1D7A87AF939DB35F87823DCBBDCB5FAC5ACC"),
    },
    "base_current": {
        844: (1, "CBDE29E6CE324C3C43CEF0E964C58A7702DF2D6F94D94D10A7EF7890A2EDB019"),
        868: (1, "05729897E44C56524FB8D53C2CBCBE7E65860E2C0A924C17DC00FBFBE531D4CB"),
        886: (1, "6EDFAB93DD466B3E715A0ED9A7FC1D7A87AF939DB35F87823DCBBDCB5FAC5ACC"),
    },
    "pk_jp": {
        838: (1, "E50386F0C222D4D13E20ABB0C4749D0BAFB15C2488879E3696219875AE9F9DD9"),
        844: (1, "A7FA28605E7177E55DEAA750E68E515827D58B2AA47497EFAAA519BB461225CD"),
        868: (1, "05729897E44C56524FB8D53C2CBCBE7E65860E2C0A924C17DC00FBFBE531D4CB"),
        886: (3, "E8E4525759056A78B26421C97E8969D08689756FB8FDCD86D3C065ADB61BF275"),
    },
    "pk_current": {
        838: (1, "E50386F0C222D4D13E20ABB0C4749D0BAFB15C2488879E3696219875AE9F9DD9"),
        844: (1, "A7FA28605E7177E55DEAA750E68E515827D58B2AA47497EFAAA519BB461225CD"),
        850: (4, "531431391F33E02FC05349DF70C30E19DDBD1DB81619EDCC6E579F7363DBB0D1"),
        868: (1, "05729897E44C56524FB8D53C2CBCBE7E65860E2C0A924C17DC00FBFBE531D4CB"),
        874: (1, "D4DBDB4F1A6FFEC1971BC499E9CA0C2A1FBA0CE9F1D4F70A8B0F3D0EB5AC04CC"),
        886: (3, "E8E4525759056A78B26421C97E8969D08689756FB8FDCD86D3C065ADB61BF275"),
    },
}
FLATTEN_EVIDENCE = {
    "base": {
        838: (2, "EE059B262904D450C3A9128F441B966037EC0451621DD96555B361FE136DCF42"),
        850: (1, "E2A55E2641C42DBE2FFCFD9F3DA0E35B362E99A4EC74C57609C46FF3B72FA3D0"),
    },
    "pk": {
        838: (4, "D35BB52A13CB747A566DB1016258370961982003CCEC3662AD2B67DFC012B347"),
        850: (1, "665F1C1BA3D77BAA25BCD0E8639C1CC99A91186F3352F0EA586477A29E5FE46A"),
    },
}

BASIS = (
    "review_queue_base_msggame_B006_C_pristine_base_pc_jp_authoritative_"
    "block0_runtime_terminal_records2217_2283_visible67_imported_S1017_"
    "root838_boundary_2217_explanatory_plain_2218_explanatory_archaic_"
    "full_seven_voice_groups_both_boundaries_unique_exact_pk_tuple_reverse_"
    "record_offset_plus68_after_two_pk_only_insertions_actual_reused_roots_"
    "520_526_to_pk526_532_not_ordinal_guesses_jp_current_sc_tc_exact_pk_en_"
    "empty_target_full_archive_digests_014a_closures_0143_callers_"
    "flattening_fixed_following_standalone014c_bound_inability_imperative_"
    "volitional_desire_auxiliary_return_and_directional_request_matrices_"
    "B002_acknowledgement_matrix_hai_ye_hahha_ha_yeot_consistency_"
    "one_line_skeleton_reverse_overlay_exact_runtime_caller_rewrite_pending_"
    "no_historic_or_switch_korean_authority"
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
        PRIOR.SOURCE_JP_BY_ROOT[838] != SOURCE_JP_BY_ROOT[838]
        or PRIOR.TRANSLATION_POLICY_BY_ROOT[838]
        != TRANSLATION_POLICY_BY_ROOT[838]
        or PRIOR.CROSS_SEGMENT_TRANSLATION_POLICY[2217] != "것이다"
        or PRIOR.CROSS_SEGMENT_TRANSLATION_POLICY[2218] != "것이니라"
        or PRIOR.FULL_TRANSLATION_POLICY[2217] != "것이다"
        or PRIOR.FULL_TRANSLATION_POLICY[2218] != "것이니라"
        or FULL_TRANSLATION_POLICY[2217] != "것이다"
        or FULL_TRANSLATION_POLICY[2218] != "것이니라"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} imported S1017 boundary drifted"
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
            tuple(
                (BLOCK_ID, PK_RECORD_MAP[value])
                for value in RECORD_IDS
            )
            if label.startswith("pk_")
            else RECORD_KEYS
        )
        full_keys = (
            tuple(
                (BLOCK_ID, PK_RECORD_MAP[value])
                for value in FULL_RECORD_IDS
            )
            if label.startswith("pk_")
            else tuple(
                (BLOCK_ID, value) for value in FULL_RECORD_IDS
            )
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
        != {6, 12}
        or PK_ROOT_BY_BASE[520] != 526
        or PK_ROOT_BY_BASE[526] != 532
    ):
        raise RuntimeError(
            f"segment {SEGMENT} insertion/actual-root proof drifted"
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
                    f"segment {SEGMENT} Base/PK mapping drifted: "
                    f"{language}/{base_key}/{pk_key}"
                )
        if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {pk_key}"
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
                set(PK_FULL_TERMINAL_GROUPS[PK_ROOT_BY_BASE[base_root]])
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
        len(RECORD_IDS) != 67
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or translations != TRANSLATIONS
        or set(FULL_TRANSLATION_POLICY) != set(FULL_RECORD_IDS)
        or set(TRANSLATION_POLICY_BY_ROOT) != set(FULL_TERMINAL_GROUPS)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} translation universe drifted"
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
    if (
        TRANSLATIONS_BY_RECORD[2217] != "것이다"
        or TRANSLATIONS_BY_RECORD[2218] != "것이니라"
        or TRANSLATIONS_BY_RECORD[2223] != "것입니다"
        or tuple(
            TRANSLATIONS_BY_RECORD[record_id]
            for record_id in range(2226, 2233)
        )
        != ("예", "예", "예", "옛", "예", "옛", "옛")
        or TRANSLATIONS_BY_RECORD[2239] != "하지 않는다"
        or TRANSLATIONS_BY_RECORD[2246] != "하라"
        or TRANSLATIONS_BY_RECORD[2253] != "지 못한다"
        or TRANSLATIONS_BY_RECORD[2254] != "어머"
        or TRANSLATIONS_BY_RECORD[2267] != "하자"
        or TRANSLATIONS_BY_RECORD[2270] != "해 주시기를 바라옵니다"
        or TRANSLATIONS_BY_RECORD[2275] != "왔습니다"
        or TRANSLATIONS_BY_RECORD[2281] != "왔다"
        or TRANSLATIONS_BY_RECORD[2283] != "오너라"
        or FULL_TRANSLATION_POLICY[2284] != "주시옵소서"
        or FULL_TRANSLATION_POLICY[2288] != "오너라"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic correction contract drifted"
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
                    "base_actual_root": root,
                    "pk_actual_root": pk_root,
                    "base_record_id": record_id,
                    "pk_semantic_record_id": PK_RECORD_MAP[record_id],
                    "base_pk_record_offset": 68,
                    "base_pk_root_delta": pk_root - root,
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
                "segment": "base_msggame_B006_S1018",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": len(RECORD_IDS),
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "base_pk_semantic_record_offset": 68,
                "pk_only_terminal_family_insertions_before_segment": 2,
                "new_pk_insertion_in_segment": False,
                "base_pk_actual_root_deltas": [6, 12],
                "reused_nonordinal_base_roots": {
                    "2275_2281": 520,
                    "2282_2288": 526,
                },
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
                "imported_s1017_boundary_policy": {
                    "2217": FULL_TRANSLATION_POLICY[2217],
                    "2218": FULL_TRANSLATION_POLICY[2218],
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
