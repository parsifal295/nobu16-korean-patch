#!/usr/bin/env python3
"""Build source-redacted PK B099 segment 1301 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch097_segment1296.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B099_S1301.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B098_S1300.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B099_S1302.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1301
SEGMENT_NAME = "pk_msggame_B099_S1301"
QUEUE_BATCH_ID = "pk_msggame-B099"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_RECORD_COUNT = 140
QUEUE_VISIBLE_COUNT = 200
QUEUE_VISIBLE_FIRST = "9:3943:0"
QUEUE_VISIBLE_LAST = "9:4079:0"
SLICE_VISIBLE_COUNT = 67
SLICE_FIRST = "9:3943:0"
SLICE_LAST = "9:3970:0"
PREFILL_COUNT = 26
RESIDUAL_COUNT = 41
BLOCK_ID = 9
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "9:3943:1",
    "9:3944:1",
    "9:3948:1",
    "9:3948:4",
    "9:3949:1",
    "9:3950:3",
    "9:3951:0",
    "9:3951:1",
    "9:3951:2",
    "9:3953:3",
    "9:3954:0",
    "9:3954:1",
    "9:3955:0",
    "9:3955:1",
    "9:3956:0",
    "9:3956:1",
    "9:3957:0",
    "9:3957:1",
    "9:3958:0",
    "9:3958:1",
    "9:3959:0",
    "9:3959:1",
    "9:3960:0",
    "9:3960:1",
    "9:3961:0",
    "9:3961:1",
    "9:3962:0",
    "9:3962:1",
    "9:3963:0",
    "9:3963:1",
    "9:3964:0",
    "9:3964:1",
    "9:3965:0",
    "9:3965:1",
    "9:3966:0",
    "9:3966:1",
    "9:3967:0",
    "9:3967:1",
    "9:3968:0",
    "9:3969:0",
    "9:3970:0",
)
_SIEGE_ADVANTAGE_OPENING = (
    "적군은 성하에서 방어 태세를 갖추고 있습니다"
)
_SIEGE_ADVANTAGE_PLAN = (
    "\n병력의 우위를 살려 적의 설비를 제압해 나가며\n"
    "착실히 적의 성으로 다가갑시다"
)
TRANSLATIONS = {
    "9:3943:1": "\n적장 「",
    "9:3944:1": "\n적장 「",
    "9:3948:1": ", 하지만\n적진에는 맹장·",
    "9:3948:4": "도록 하십시오",
    "9:3949:1": ", 지장·",
    "9:3950:3": "…",
    "9:3951:0": "아군은 상당히 열세",
    "9:3951:1": "\n게다가 적진에는 맹장·",
    "9:3951:2": "까지 출진했다니…\n",
    "9:3953:3": "군",
    **{
        f"9:{record_id}:{literal_id}": translation
        for record_id in range(3954, 3966)
        for literal_id, translation in enumerate(
            (_SIEGE_ADVANTAGE_OPENING, _SIEGE_ADVANTAGE_PLAN)
        )
    },
    "9:3966:0": "공성전을 치르기에는 병력이 다소 부족합니다",
    "9:3966:1": (
        "\n어떻게든 수비의 허점을 찔러\n"
        "피해를 최소화해 성문을 돌파해야 합니다…"
    ),
    "9:3967:0": (
        "출진한 뒤 여러 날이 흘러 병사들이 지쳐 보입니다"
    ),
    "9:3967:1": (
        "\n장졸의 사기를 유지하기 위해서라도\n"
        "서둘러 진격해 성과를 거두어야 합니다"
    ),
    "9:3968:0": (
        "우리의 공격을 예상하지 못했나 보군\n"
        "성하의 방비가 아직 갖춰지지 않은 모양이다…\n"
        "수비가 허술한 쪽으로 가면 쉽게 성문에 다가설 수 있겠군"
    ),
    "9:3969:0": (
        "성의 방비까지는 손이 미치지 못한 듯합니다\n"
        "성하의 방비가 아직 갖춰지지 않은 모양입니다…\n"
        "수비가 허술한 쪽으로 가면 쉽게 성문에 다가설 수 있겠습니다"
    ),
    "9:3970:0": _SIEGE_ADVANTAGE_OPENING,
}
TARGET_RECORD_IDS = (
    3943,
    3944,
    3948,
    3949,
    3950,
    3951,
    3953,
    *range(3954, 3971),
)
STATIC_RECORD_IDS = (3968, 3969)
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in STATIC_RECORD_IDS
)
STATIC_COORDINATES = {
    coordinate
    for coordinate in TARGET_COORDINATES
    if int(coordinate.split(":")[1]) in STATIC_RECORD_IDS
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
EXPECTED_ARITY = {
    3943: 3,
    3944: 3,
    3948: 5,
    3949: 3,
    3950: 4,
    3951: 4,
    3953: 4,
    **{record_id: 2 for record_id in range(3954, 3968)},
    3968: 1,
    3969: 1,
    3970: 6,
}
PREFILL_COMPANION_COORDINATES = (
    "9:3943:0",
    "9:3943:2",
    "9:3944:0",
    "9:3944:2",
    "9:3948:0",
    "9:3948:2",
    "9:3948:3",
    "9:3949:0",
    "9:3949:2",
    "9:3950:0",
    "9:3950:1",
    "9:3950:2",
    "9:3951:3",
    "9:3953:0",
    "9:3953:1",
    "9:3953:2",
)
CROSS_SEGMENT_DONOR_COMPANION_COORDINATES = (
    "9:3970:2",
    "9:3970:3",
    "9:3970:4",
    "9:3970:5",
)
HIDDEN_CURRENT_COMPANION_COORDINATES = ("9:3970:1",)
MANUAL_CROSS_SEGMENT_TRANSLATIONS = {
    "9:3970:2": "이(가) 지키는 저 「",
    "9:3970:3": "」…\n강력한 설비로 보이니",
    "9:3970:4": ",",
    "9:3970:5": "주의하십시오",
}
MANUAL_HIDDEN_COMPANION_TRANSLATIONS = {"9:3970:1": "\n"}
EXACT_BASE_DONOR = {
    3943: (9, 3671),
    3944: (9, 3672),
    3948: (9, 3676),
    3949: (9, 3677),
    3950: (9, 3678),
    3953: (9, 3681),
}
_SIEGE_ADVANTAGE_CONTEXT = ("14:55:1", "9:3683:0")
SEMANTIC_BASE_CONTEXT = {
    3951: (
        "9:3679:0",
        "9:3679:1",
        "9:3679:2",
        "9:3679:3",
    ),
    **{
        record_id: _SIEGE_ADVANTAGE_CONTEXT
        for record_id in range(3954, 3966)
    },
    3966: ("15:899:0", "15:900:0", "14:55:1"),
    3967: ("9:2477:0", "15:1823:0"),
    3968: ("14:55:1", "9:2894:0"),
    3969: ("14:55:1", "9:2957:0"),
    3970: ("14:55:1", "9:1063:0"),
}
EXPECTED_BASE_RAW_MATCHES = {
    record_id: () for record_id in TARGET_RECORD_IDS
}
EXPECTED_BASE_LITERAL_MATCHES = {
    **{record_id: () for record_id in TARGET_RECORD_IDS},
    3943: ((9, 3671),),
    3944: ((9, 3672),),
    3948: ((9, 3676),),
    3949: ((9, 3677),),
    3950: ((9, 3678),),
    3953: ((9, 3681),),
}
EXPECTED_BASE_MASKED_MATCHES = EXPECTED_BASE_LITERAL_MATCHES
BOUNDARY_RECORD_KEYS = tuple(
    (9, record_id) for record_id in range(3940, 3974)
)
SOURCE_CALL_ROOTS = (
    29,
    88,
    160,
    376,
    514,
    550,
    562,
    568,
    574,
    616,
    730,
    748,
    1066,
    1096,
    1114,
    1126,
    1144,
    1162,
    1174,
)
CURRENT_CALL_ROOTS = SOURCE_CALL_ROOTS
EXPECTED_CONTROLS_BY_RECORD = {
    3943: ((616,), ("024833",)),
    3944: ((616, 1066), ("024833",)),
    3948: ((568, 1174, 1114), ("024833",)),
    3949: ((574, 568, 514), ("024833",)),
    3950: ((550, 1162, 1144), ()),
    3951: ((376, 730, 29, 748), ("024833",)),
    3953: ((568, 160, 88), ()),
    **{
        record_id: ((562, 1126), ())
        for record_id in range(3954, 3966)
    },
    3966: ((562,), ()),
    3967: ((1096,), ()),
    3968: ((), ()),
    3969: ((), ()),
    3970: ((562, 1096, 1174), ("024833",)),
}
EXPECTED_SOURCE_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
EXPECTED_CURRENT_CONTROLS_BY_RECORD = EXPECTED_CONTROLS_BY_RECORD
SOURCE_CURRENT_GAP_MISMATCH_RECORDS: tuple[int, ...] = ()
SPEAKER_STYLE = (
    (3943, "formal_skilled_enemy_assessment"),
    (3944, "formal_fierce_enemy_assessment"),
    (3948, "formal_superior_but_fierce_enemy_warning"),
    (3949, "formal_strategist_warning"),
    (3950, "disadvantaged_tactical_advice"),
    (3951, "disadvantaged_fierce_enemy_warning"),
    (3953, "calm_disadvantaged_assessment"),
    *(
        (record_id, "formal_siege_advantage_plan")
        for record_id in range(3954, 3966)
    ),
    (3966, "formal_understrength_siege_plan"),
    (3967, "formal_fatigue_and_morale_advice"),
    (3968, "plain_opportunistic_siege_assessment"),
    (3969, "polite_opportunistic_siege_assessment"),
    (3970, "formal_guarded_facility_warning"),
)
TERMINOLOGY_POLICY = (
    ("castle town", "성하"),
    ("siege battle", "공성전"),
    ("defensive facility", "설비"),
    ("enemy castle", "적의 성"),
    ("castle gate", "성문"),
    ("officers and soldiers", "장졸"),
    ("fierce and cerebral officers", "맹장/지장"),
    ("ellipsis", "…"),
)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "62B1664F152F3E326B2586BA11931EC17A0B4B7D27F0C7C4F0926C945B94B6F1"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "D28F8C665E90C2665D94BDDA4A3937654E95C95928980A956B6DCCD9849334C8"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "6BD8613F68F8E2892CFFF8AE345CCEFD1AB25F5A0CE4C6BB26B6D170D258777A"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "0B1912627B1EF85BFE6A0FA57BB990B14580295DE2DA52DA88AB67AC4DCBA0D3"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "C2083FB612B64C150C741B7D4368CFB76457A7E7D017D46811E57A835F306C1A"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "E8218DC3E2B31902E0F4981D0317890A0274C048D7A5C2DE9539177DD6BEA40C"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "B57A9DA38A778F6CE4009D16C30C82AA4DC377ABAB9F8032824434D46F1FEE5C"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "849833B4ECD7AF90786293309DEF5DEA1F4971191DA3A0A46C8730220B7B3997"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "4D463AA3890F0183BBE65A83622ED1089ED18FBC9F079B48E28436EE795A605F"
)
EXPECTED_BOUNDARY_SHA256 = (
    "AE29585F6457E34584F70A35F560A4B3BA80DCA454BEEF18FDB3E0DCEEFA977D"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "E21CB9FC832E8C5A2BCAC5710ED1AFDD8DF8005B59B9327837F9E94664929E0C"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "C9617DC8EF9F4DB7BF3F82FBE17361BC5C7EC0BE0392F114D4ABB50C2274DD4A"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "400EB80310DAC00625D4D54DB8F94C499529D1E146F28435F68CE64975F989C5"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "12D2EFF07F110DB2434AB3FA0CCEE77462D7986AA705355EF9695A39F0125D2F"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "305C9A73A823A4CDC8CAF5528EC71DE29B701618CC9558D5CDB2D215179D446F"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "29AD2FF8B01FABFA3A009D61FAC5519590A5FFADA7C0C2F969F07EAA494A8E98"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "F7E4D628F77775FAE3C04E749492984D6889706A36579DE2A54A8A430F1F74E3"
)
EXPECTED_CANDIDATE_SHA256 = (
    "926E2D6F7254998F9E712EF43B2619F3C53EA89AD4890953F5F80F4756ED68EB"
)
EXPECTED_COMBINED_SLICE_CANDIDATE_SHA256 = (
    "9762409E1D980A632BC6906ABED809D04BAA02163050D09C834CD1819AF27461"
)
EXPECTED_CHANGED_LITERAL_COUNT = 39
EXPECTED_COMBINED_CHANGED_LITERAL_COUNT = 64

DISCOVERED_PINS: dict[str, str] = {}
BASIS = (
    "pristine PK PC Japanese is authoritative and every populated PK "
    "English, Simplified Chinese and Traditional Chinese auxiliary line "
    "was reviewed for the strength assessment and siege planning records; "
    "the six complete assessment records with exact completed Base donors "
    "reuse their approved Korean assemblies, while the remaining eighteen "
    "complete records use completed Base battle, siege, facility, morale "
    "and officer-warning rows only as semantic and terminology context; "
    "성하, 공성전, 설비, 적의 성, 성문, 장졸, 맹장 and 지장 wording, "
    "plain and polite registers, dynamic officer and facility tokens, all "
    "calls, gaps, line shapes and protected outer whitespace are preserved; "
    "split record 3970 is fully assembled with its identity hidden newline "
    "and four manually reviewed S1302 cross-segment companions, and any "
    "present neighbor decision must match that assembly exactly; all "
    "twenty-six slice prefills, both overlay orders, byte-exact reversal, "
    "two-run reproduction, tamper rejection, outside-scope identity and "
    "Steam read-only state are guarded; all records remain PK runtime "
    "pending and discovered pins are immutable"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1301_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
CORE = BASE.CORE
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
OVERRIDES = BASE.OVERRIDES
literal_texts = CORE.literal_texts
gap_bytes = CORE.gap_bytes


def read_jsonl(path: Path) -> tuple[dict[str, Any], ...]:
    return tuple(
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    """Guard exact donors plus the manual split-record semantic assembly."""
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    neighbor_rows: dict[str, dict[str, Any]] = {}
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            for row in read_jsonl(path):
                neighbor_rows[str(row["coordinate"])] = row

    target_set = set(TARGET_COORDINATES)
    companion_set = set(PREFILL_COMPANION_COORDINATES)
    cross_set = set(CROSS_SEGMENT_DONOR_COMPANION_COORDINATES)
    hidden_set = set(HIDDEN_CURRENT_COMPANION_COORDINATES)
    if (
        cross_set != set(MANUAL_CROSS_SEGMENT_TRANSLATIONS)
        or hidden_set != set(MANUAL_HIDDEN_COMPANION_TRANSLATIONS)
    ):
        raise RuntimeError(f"segment {SEGMENT} manual companion scope drifted")

    seen_target: set[str] = set()
    seen_companion: set[str] = set()
    seen_cross: set[str] = set()
    seen_hidden: set[str] = set()
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []

    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        current = records_by_label["current"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if record.data == source.data
        )
        literal_matches = tuple(
            coordinate
            for coordinate in base_source
            if literal_texts(base_source, coordinate) == source_literals
        )
        masked_matches = tuple(
            coordinate
            for coordinate, record in base_source.items()
            if (
                literal_texts(base_source, coordinate) == source_literals
                and CORE.mask_call_operands(record)
                == CORE.mask_call_operands(source)
            )
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or raw_matches != EXPECTED_BASE_RAW_MATCHES[record_id]
            or literal_matches != EXPECTED_BASE_LITERAL_MATCHES[record_id]
            or masked_matches != EXPECTED_BASE_MASKED_MATCHES[record_id]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base donor drifted: {record_id}"
            )

        exact = record_id in EXACT_BASE_DONOR
        donor_rows: list[dict[str, Any]] = []
        if exact:
            donor_key = EXACT_BASE_DONOR[record_id]
            donor_coordinates = tuple(
                f"{donor_key[0]}:{donor_key[1]}:{literal_id}"
                for literal_id in range(EXPECTED_ARITY[record_id])
            )
        else:
            donor_coordinates = SEMANTIC_BASE_CONTEXT[record_id]
        for donor_coordinate in donor_coordinates:
            donor = base_rows.get(donor_coordinate)
            if (
                donor is None
                or donor.get("semantic_review") != "approved"
                or donor.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base context drifted: "
                    f"{donor_coordinate}"
                )
            donor_rows.append(donor)

        assembled: list[str] = []
        donor_assembled: list[str] = []
        owners: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"{BLOCK_ID}:{record_id}:{literal_id}"
            if exact:
                donor_translation = str(donor_rows[literal_id]["translation"])
                donor_assembled.append(donor_translation)
                if coordinate in target_set:
                    if TRANSLATIONS[coordinate] != donor_translation:
                        raise RuntimeError(
                            f"segment {SEGMENT} target donor drifted: "
                            f"{coordinate}"
                        )
                    seen_target.add(coordinate)
                    assembled.append(TRANSLATIONS[coordinate])
                    owners.append("segment_exact")
                    continue
                companion = prefill_rows.get(coordinate)
                if (
                    coordinate not in companion_set
                    or companion is None
                    or companion.get("semantic_review") != "approved"
                    or companion.get("runtime_review") != "pending"
                    or companion["base_exact_reuse_prefill"][
                        "runtime_promotion_authorized"
                    ]
                    is not False
                    or str(companion["translation"]) != donor_translation
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} exact companion drifted: "
                        f"{coordinate}"
                    )
                seen_companion.add(coordinate)
                assembled.append(str(companion["translation"]))
                owners.append("base_exact_prefill_runtime_pending")
                continue

            if coordinate in target_set:
                seen_target.add(coordinate)
                assembled.append(TRANSLATIONS[coordinate])
                donor_assembled.append("manual_multilingual_selection")
                owners.append("segment_manual")
                continue
            if coordinate in hidden_set:
                translation = MANUAL_HIDDEN_COMPANION_TRANSLATIONS[coordinate]
                if (
                    source_literals[literal_id] != "\n"
                    or current_literals[literal_id] != "\n"
                    or translation != "\n"
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} hidden newline drifted: "
                        f"{coordinate}"
                    )
                seen_hidden.add(coordinate)
                assembled.append(translation)
                donor_assembled.append("hidden_current_identity")
                owners.append("hidden_newline_identity")
                continue
            if coordinate in cross_set:
                translation = MANUAL_CROSS_SEGMENT_TRANSLATIONS[coordinate]
                neighbor = neighbor_rows.get(coordinate)
                if neighbor is not None and (
                    neighbor.get("semantic_review") != "approved"
                    or neighbor.get("runtime_review") != "pending"
                    or str(neighbor.get("translation")) != translation
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} manual neighbor drifted: "
                        f"{coordinate}"
                    )
                source_signature = ENGINE.protected_signature(
                    source_literals[literal_id]
                )
                current_signature = ENGINE.protected_signature(
                    current_literals[literal_id]
                )
                target_signature = ENGINE.protected_signature(translation)
                for field in ("leading_whitespace", "trailing_whitespace"):
                    if (
                        source_signature[field] != current_signature[field]
                        or target_signature[field] != current_signature[field]
                    ):
                        raise RuntimeError(
                            f"segment {SEGMENT} manual neighbor whitespace "
                            f"drifted: {coordinate}:{field}"
                        )
                seen_cross.add(coordinate)
                assembled.append(translation)
                donor_assembled.append("manual_cross_segment_selection")
                owners.append("neighbor_manual_semantic")
                continue
            companion = prefill_rows.get(coordinate)
            if (
                coordinate not in companion_set
                or companion is None
                or companion.get("semantic_review") != "approved"
                or companion.get("runtime_review") != "pending"
                or companion["base_exact_reuse_prefill"][
                    "runtime_promotion_authorized"
                ]
                is not False
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete manual record: "
                    f"{coordinate}"
                )
            seen_companion.add(coordinate)
            assembled.append(str(companion["translation"]))
            donor_assembled.append("base_exact_prefill_semantic_companion")
            owners.append("base_exact_prefill_runtime_pending")

        if exact and tuple(assembled) != tuple(donor_assembled):
            raise RuntimeError(
                f"segment {SEGMENT} exact assembly drifted: {record_id}"
            )
        if gap_bytes(source) != gap_bytes(current):
            raise RuntimeError(
                f"segment {SEGMENT} source/current gap drifted: {record_id}"
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(value.hex().upper() for value in gap_bytes(source)),
                raw_matches,
                literal_matches,
                masked_matches,
                donor_coordinates,
                tuple(
                    (
                        str(row["coordinate"]),
                        str(row["translation"]),
                        str(row["semantic_review"]),
                        str(row["runtime_review"]),
                    )
                    for row in donor_rows
                ),
                tuple(
                    coordinate
                    for coordinate in CROSS_SEGMENT_DONOR_COMPANION_COORDINATES
                    if coordinate.startswith(f"{BLOCK_ID}:{record_id}:")
                ),
                "complete_exact" if exact else "semantic_context_only",
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(assembled),
                tuple(donor_assembled),
                CORE.runtime_controls(source),
                CORE.runtime_controls(current),
                (
                    "complete_translation_equals_completed_base_donor"
                    if exact
                    else "manual_pk_semantic_adaptation_with_companions"
                ),
                "base_runtime_state_not_inherited",
            )
        )

    if (
        seen_target != target_set
        or seen_companion != companion_set
        or seen_cross != cross_set
        or seen_hidden != hidden_set
    ):
        raise RuntimeError(f"segment {SEGMENT} complete assembly scope drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = CORE.runtime_controls(source)
    current_controls = CORE.runtime_controls(current)
    exact = record_id in EXACT_BASE_DONOR
    references = (
        tuple(
            f"{EXACT_BASE_DONOR[record_id][0]}:"
            f"{EXACT_BASE_DONOR[record_id][1]}:{literal_id}"
            for literal_id in range(EXPECTED_ARITY[record_id])
        )
        if exact
        else SEMANTIC_BASE_CONTEXT[record_id]
    )
    prefix = f"{BLOCK_ID}:{record_id}:"
    return {
        "runtime_category": dict(SPEAKER_STYLE)[record_id],
        "source_record_gap_sha256": CORE.canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": CORE.canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "base_complete_record_match_kind": (
            "raw_literal_and_operand_exact"
            if EXPECTED_BASE_RAW_MATCHES[record_id]
            else "literal_and_masked_call_graph_exact"
            if exact
            else "none_semantic_context_only"
        ),
        "base_context_reference_coordinates": references,
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companion_reviewed": any(
            coordinate.startswith(prefix)
            for coordinate in PREFILL_COMPANION_COORDINATES
        ),
        "manual_cross_segment_companion_reviewed": any(
            coordinate.startswith(prefix)
            for coordinate in CROSS_SEGMENT_DONOR_COMPANION_COORDINATES
        ),
        "hidden_newline_companion_reviewed": any(
            coordinate.startswith(prefix)
            for coordinate in HIDDEN_CURRENT_COMPANION_COORDINATES
        ),
        "manual_multilingual_context_reviewed": True,
        "completed_base_donor_reviewed": True,
        "historical_terminology_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def install_base_globals() -> None:
    for name in OVERRIDES:
        if name in globals():
            setattr(BASE, name, globals()[name])
    module = BASE
    seen: set[int] = set()
    while id(module) not in seen:
        seen.add(id(module))
        if hasattr(module, "base_and_assembly_evidence"):
            module.base_and_assembly_evidence = base_and_assembly_evidence
        if hasattr(module, "runtime_evidence"):
            module.runtime_evidence = runtime_evidence
        if not hasattr(module, "BASE"):
            break
        module = module.BASE


def build_rows() -> tuple[Any, ...]:
    install_base_globals()
    return BASE.build_rows()


def main() -> int:
    install_base_globals()
    return BASE.main()


if __name__ == "__main__":
    raise SystemExit(main())
