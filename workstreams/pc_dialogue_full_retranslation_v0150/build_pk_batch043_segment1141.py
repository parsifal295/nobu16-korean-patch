#!/usr/bin/env python3
"""Build source-redacted PK B043 segment 1141 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter, deque
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
BASE_PATH = WORKSTREAM / "build_pk_batch042_segment1138.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B043_S1141.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B042_S1139.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B043_S1140.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B043_S1142.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B044_S1143.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1141
QUEUE_BATCH_ID = "pk_msggame-B043"
QUEUE_START = 67
QUEUE_STOP = 134
QUEUE_FIRST_RECORD = 4156
QUEUE_LAST_RECORD = 4262
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:4184:0",
    "6:4185:0",
    "6:4186:0",
    "6:4187:0",
    "6:4188:0",
    "6:4189:0",
    "6:4190:0",
    "6:4190:1",
    "6:4191:0",
    "6:4191:1",
    "6:4192:0",
    "6:4192:1",
    "6:4193:0",
    "6:4193:1",
    "6:4194:0",
    "6:4194:1",
    "6:4195:0",
    "6:4195:1",
    "6:4196:0",
    "6:4198:1",
    "6:4204:1",
    "6:4205:3",
    "6:4208:0",
    "6:4209:0",
    "6:4211:2",
    "6:4212:2",
)
TRANSLATIONS = {
    "6:4184:0": "와(과) 함께\n",
    "6:4185:0": "와(과) 함께\n",
    "6:4186:0": "와(과) 함께\n",
    "6:4187:0": "와(과) 함께\n",
    "6:4188:0": "와(과) 함께\n",
    "6:4189:0": "와(과) 함께\n",
    "6:4190:0": "와(과) 함께\n",
    "6:4190:1": "의",
    "6:4191:0": "와(과) 함께\n",
    "6:4191:1": "의",
    "6:4192:0": "와(과) 함께\n",
    "6:4192:1": "의",
    "6:4193:0": "와(과) 함께\n",
    "6:4193:1": "의",
    "6:4194:0": "와(과) 함께\n",
    "6:4194:1": "의",
    "6:4195:0": "와(과) 함께\n",
    "6:4195:1": "의",
    "6:4196:0": "의\n",
    "6:4198:1": "을(를) 포함한\n",
    "6:4204:1": "…",
    "6:4205:3": "…",
    "6:4208:0": "알겠습니다.",
    "6:4209:0": "알겠습니다.",
    "6:4211:2": " 지시해 주십시오.",
    "6:4212:2": "지시해 주",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    4184,
    4185,
    4186,
    4187,
    4188,
    4189,
    4190,
    4191,
    4192,
    4193,
    4194,
    4195,
    4196,
    4198,
    4204,
    4205,
    4208,
    4209,
    4211,
    4212,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4184: 2,
    4185: 2,
    4186: 2,
    4187: 2,
    4188: 2,
    4189: 2,
    4190: 3,
    4191: 3,
    4192: 3,
    4193: 3,
    4194: 3,
    4195: 3,
    4196: 2,
    4198: 3,
    4204: 2,
    4205: 4,
    4208: 2,
    4209: 2,
    4211: 3,
    4212: 3,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 30 for record_id in TARGET_RECORD_IDS
}
OPERAND_MASKED_BASE_RECORD_IDS = TARGET_RECORD_IDS
SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS = (4208, 4209, 4211)
CONTEXT_ADAPTED_COORDINATES = (
    "6:4208:0",
    "6:4209:0",
    "6:4211:2",
)
RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS = (
    4196,
    4204,
    4205,
    4208,
    4209,
    4211,
    4212,
)
PREFILL_COMPANION_COORDINATES = tuple(
    f"6:{record_id}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
    if f"6:{record_id}:{literal_id}" not in TARGET_COORDINATES
)
BASE_DONOR_COORDINATES = {
    f"6:{record_id}:{literal_id}":
    f"6:{BASE_RECORD_MAPPING[record_id]}:{literal_id}"
    for record_id in TARGET_RECORD_IDS
    for literal_id in range(EXPECTED_ARITY[record_id])
}
BASE_CONTEXT_REFERENCES = {
    coordinate: BASE_DONOR_COORDINATES[coordinate]
    for coordinate in TARGET_COORDINATES
}
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = (
    4183,
    4184,
    4197,
    4199,
    4203,
    4206,
    4207,
    4210,
    4212,
    4213,
    4214,
)
EXPECTED_SOURCE_CONTROLS_BY_RECORD = {
    4184: ((568,), ("025A32", "026432")),
    4185: ((568,), ("025A32", "029632")),
    4186: ((568,), ("025A32", "026E32")),
    4187: ((568,), ("025A32", "026432")),
    4188: ((568,), ("025A32", "029632")),
    4189: ((568,), ("025A32", "026E32")),
    4190: ((568,), ("025A32", "025032", "026432")),
    4191: ((568,), ("025A32", "025032", "029632")),
    4192: ((568,), ("025A32", "025032", "026E32")),
    4193: ((568,), ("025A32", "025032", "026432")),
    4194: ((568,), ("025A32", "025032", "029632")),
    4195: ((568,), ("025A32", "025032", "026E32")),
    4196: ((1096,), ("025A32", "026432")),
    4198: ((568,), ("025A32", "024833", "0232")),
    4204: ((772,), ()),
    4205: ((628, 766, 550), ()),
    4208: ((628, 1162), ()),
    4209: ((862, 538, 442), ()),
    4211: ((538, 1174, 190), ()),
    4212: ((538, 1174, 190), ()),
}
EXPECTED_CURRENT_CONTROLS_BY_RECORD = {
    **EXPECTED_SOURCE_CONTROLS_BY_RECORD,
    4208: ((), ()),
    4209: ((), ()),
    4211: ((), ()),
}
EXPECTED_CALL_ROOTS = (
    190,
    442,
    538,
    550,
    568,
    628,
    766,
    772,
    862,
    1096,
    1162,
    1174,
)
EXPECTED_TERMINAL_SETS = {
    190: {"으", "있습니다", "있사옵니다"},
    442: {"하", "하옵니다", "합니다"},
    538: {"다", "했습니다"},
    550: {"다", "이니라", "이오", "이옵니다", "입니다"},
    568: {"다", "이오", "입니다"},
    628: {"었다", "했습니다"},
    766: {"아니었사옵니다", "아니었습니다", "없었다", "없었습니다"},
    772: {"못했습니다", "않았습니다", "없었다"},
    862: {"예"},
    1096: {"다", "하옵니다", "합니다"},
    1162: {"그렇군", "합시다"},
    1174: {"", "고"},
}

SPEAKER_STYLE = {
    4184: "neutral_system_joint_march_castle",
    4185: "neutral_system_joint_march_domain",
    4186: "neutral_system_joint_march_force",
    4187: "neutral_system_joint_multi_march_castle",
    4188: "neutral_system_joint_multi_march_domain",
    4189: "neutral_system_joint_multi_march_force",
    4190: "neutral_system_joint_clan_castle_march",
    4191: "neutral_system_joint_clan_domain_march",
    4192: "neutral_system_joint_clan_force_march",
    4193: "neutral_system_joint_clan_multi_castle_march",
    4194: "neutral_system_joint_clan_multi_domain_march",
    4195: "neutral_system_joint_clan_multi_force_march",
    4196: "formal_frontline_support_preparation_status",
    4198: "formal_domestic_support_completion_status",
    4204: "formal_retainer_no_suitable_proposal_report",
    4205: "formal_retainer_unworkable_proposals_apology",
    4208: "formal_retainer_order_acceptance",
    4209: "formal_retainer_clan_order_acceptance",
    4211: "formal_retainer_enemy_castle_scheme_selection",
    4212: "formal_retainer_domain_measure_selection",
}
TERMINOLOGY_POLICY = (
    ("march", "진군"),
    ("joint_force", "함께"),
    ("multiple_fronts", "여러 방면"),
    ("capture", "공략"),
    ("front_line", "전선"),
    ("military_preparation", "군비"),
    ("domestic_affairs", "내정"),
    ("fief", "지행지"),
    ("lord_order", "주명"),
    ("retainers", "가신"),
    ("scheme", "계책"),
    ("enemy_castle_strategy", "적성 조략"),
    ("castle_lord", "성주"),
    ("domain_measures", "영내 제책"),
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
    "A4D37420E8B388B5124EB805FAE2F898AD8315E3ABFA1301096EE76D65DB3413"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "70F14C09833FB37303BD83EF6D51C8255C64190DCE5ABCD434B16DE8E2B00610"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "158E3E21958D331CBD4F2963252E03F74C8516ECECBAD76D6F4037CF539D945E"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "294C62239FC3485A000543F40DD7D2FC21B17A5449830082C4997754721FDCC1"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "F570AE4D876479FF8796E6C4D33983AFCF3A55257F194C839AAEA69C678CC270"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "7C16CB5D9B56C0F737BC97009DC556235862757E265BE3B5A3BBDC525085CC80"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "24FCAEB4177095C95EE2B5A849E50A578DEEA91C4AFB8D8743211A36138DE5F1"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "9306A0765FEB55D7B845DAFB25D6A6C5E03A0EE6030A395ECE814A406B6CCF42"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "B9E5F26B9C197B7BF1587ABDA432A59E7FCA2D7864609D4F1A0230BE0C3FFBF1"
)
EXPECTED_BOUNDARY_SHA256 = (
    "A3C0907CA0CCA6128D63C5875CC68AAAC2A8DCB400B36D6AEA1FBE1663C23678"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "B48D68984FA85FAD6BAE81F665BDFAF05BD2B7481318923AE61E3208036A94FE"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "4750356F0F5D57BBFECF50004D31490C64CD4BF0F4731FEC4495AE21AA4834CC"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "B764575970936C036544BCA48868A599A2B97267845BB91217BD332DBE2AA03A"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "547CFB72C2D15C4B108F6572C86798F3A396D5069933D6EC64B04D94C5888D58"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "44E8F7AC1B169596F7815079559531744861E4A4324BB427FDDF537A555D26CF"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "CD54EF4D9897CB9E536B93B7239D04CBB485FBCA1F6B55C333D70BC6960A4D0B"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "B5B1FD02F003CDF24C3F582F133BBE50C5778272022B31D9B3F0159F21EAF642"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "DCA347FFE1BFD03FD938C42FDC30661A90BF1E6BDE7BB2C7C5AFABECF48C1B18"
)
EXPECTED_CANDIDATE_SHA256 = (
    "B1EC4E9D570016D86BD5B294A45B45612266B542B9EA105B53D356631E766414"
)
EXPECTED_CHANGED_LITERAL_COUNT = 15

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B043 queue universe and zero-based visible ordinal slice "
    "[67,134) are pinned before the twenty-six-row residual is derived "
    "against the immutable exact-reuse prefill and every available "
    "independent PK decision output. Twenty complete target records and "
    "their twenty-five same-record prefill companions are reviewed with "
    "both slice boundaries, pristine PK source, current Korean, PC English, "
    "Simplified Chinese, Traditional Chinese, and canonical Base donors. "
    "Every target source record preserves the corresponding Base literal "
    "sequence and masked runtime-gap shape at the stable PK-minus-thirty "
    "mapping, while direct call operands differ. Base wording supplies "
    "semantic context only; Base runtime state and VM verification are not "
    "inherited. Three PK current records intentionally removed source call "
    "gaps, so their target literals are adapted to complete current Korean "
    "forms instead of copying Base stems. Complete-record review also finds "
    "irreducible pre-existing morphology defects in seven records: exact "
    "reuse companion stems meet incompatible full terminal branches, or "
    "removed PK calls leave companion stems incomplete. These rows remain "
    "runtime pending and are not promoted. Token-safe particles, preserved "
    "line breaks and outer spaces, speaker register, historical terms, live "
    "call graphs, reverse overlay and restoration, outside-scope identity, "
    "two-run reproduction, tamper rejection, and Steam read-only state are "
    "guarded; all new neighboring outputs remain optional."
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1141_base",
        BASE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {BASE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
ENGINE = BASE.ENGINE
sha256_bytes = BASE.sha256_bytes
canonical_sha256 = BASE.canonical_sha256
coordinate_key = BASE.coordinate_key
literal_texts = BASE.literal_texts
gap_bytes = BASE.gap_bytes
read_jsonl = BASE.read_jsonl
context_records = BASE.context_records


def patch_base_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_CHANGED_LITERAL_COUNT":
        EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256":
        EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(BASE, name, value)
    BASE.patch_template_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    return BASE.runtime_controls(record)


def mask_call_operands(record: Any) -> tuple[str, ...]:
    return BASE.mask_call_operands(record)


def all_existing_decisions(
    prepared: Any,
) -> dict[str, dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    owner: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = owner.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
            existing[coordinate] = row
    return existing


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 107
        or len(visible) != 200
        or visible[0] != "6:4156:0"
        or visible[-1] != "6:4262:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B043 queue universe drifted")
    guarded_digest(
        "queue universe",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4184:0"
        or queue_slice[-1] != "6:4213:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if len(prefilled) != 41:
        raise RuntimeError(f"segment {SEGMENT} prefill count drifted")
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "pk_source_gap_template_sha256"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
        )
        for coordinate in prefilled
    )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing = all_existing_decisions(prepared)
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    source_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["jp"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    current_target = tuple(
        (
            coordinate,
            literal_texts(
                records_by_label["current"],
                coordinate_key(coordinate)[:2],
            )[coordinate_key(coordinate)[2]],
        )
        for coordinate in TARGET_COORDINATES
    )
    corpus = tuple(
        (
            label,
            record_id,
            sha256_bytes(records[(BLOCK_ID, record_id)].data),
            literal_texts(records, (BLOCK_ID, record_id)),
        )
        for label, records in records_by_label.items()
        for record_id in CONTEXT_RECORD_IDS
    )
    gaps = tuple(
        (
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["jp"][(BLOCK_ID, record_id)]
                )
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label["current"][(BLOCK_ID, record_id)]
                )
            ),
        )
        for record_id in TARGET_RECORD_IDS
    )
    boundary = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][(BLOCK_ID, record_id)].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][(BLOCK_ID, record_id)]
                )
            ),
        )
        for label in ("jp", "current", "en", "sc", "tc")
        for record_id in BOUNDARY_RECORD_IDS
    )
    controls = tuple(
        (
            label,
            record_id,
            runtime_controls(
                records_by_label[label][(BLOCK_ID, record_id)]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        ("source target", source_target, EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", current_target, EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", corpus, EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", gaps, EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", boundary, EXPECTED_BOUNDARY_SHA256),
        ("runtime control", controls, EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    if (
        any(
            runtime != (
                EXPECTED_SOURCE_CONTROLS_BY_RECORD
                if label == "jp"
                else EXPECTED_CURRENT_CONTROLS_BY_RECORD
            )[record_id]
            for label, record_id, runtime in controls
        )
        or any(
            (
                source == current
                and record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS
            )
            or (
                source != current
                and record_id not in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS
            )
            for record_id, source, current in gaps
        )
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_row_is_approved(
    row: dict[str, Any] | None,
) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") == "verified"
    )


def donor_translation(
    coordinate: str,
    base_rows: dict[str, dict[str, Any]],
) -> str:
    reference = BASE_DONOR_COORDINATES[coordinate]
    row = base_rows.get(reference)
    if not base_row_is_approved(row):
        raise RuntimeError(
            f"segment {SEGMENT} missing verified Base row: {reference}"
        )
    assert row is not None
    return str(row["translation"])


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_record = records_by_label["jp"][(BLOCK_ID, record_id)]
        base_record = base_source[(BLOCK_ID, base_record_id)]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        base_literals = literal_texts(
            base_source,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current,
            (BLOCK_ID, base_record_id),
        )
        if (
            len(pk_literals) != EXPECTED_ARITY[record_id]
            or len(base_literals) != EXPECTED_ARITY[record_id]
            or pk_record.data == base_record.data
            or pk_literals != base_literals
            or mask_call_operands(pk_record)
            != mask_call_operands(base_record)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} operand-masked Base drifted: "
                f"{record_id}"
            )
        donor_rows: list[tuple[Any, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            reference = BASE_DONOR_COORDINATES[coordinate]
            row = base_rows.get(reference)
            if not base_row_is_approved(row):
                raise RuntimeError(
                    f"segment {SEGMENT} missing verified Base row: "
                    f"{reference}"
                )
            assert row is not None
            donor_rows.append(
                (
                    coordinate,
                    reference,
                    str(row["translation"]),
                    str(row["runtime_review"]),
                )
            )
        base_evidence.append(
            (
                record_id,
                base_record_id,
                "operand_masked",
                sha256_bytes(pk_record.data),
                sha256_bytes(base_record.data),
                pk_literals,
                base_literals,
                base_current_literals,
                tuple(
                    value.hex().upper() for value in gap_bytes(pk_record)
                ),
                tuple(
                    value.hex().upper() for value in gap_bytes(base_record)
                ),
                mask_call_operands(pk_record),
                mask_call_operands(base_record),
                tuple(donor_rows),
                record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
            )
        )
        owners: list[str] = []
        translations: list[str] = []
        references: list[str] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            reference = BASE_DONOR_COORDINATES[coordinate]
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                expected = (
                    actual
                    if coordinate in CONTEXT_ADAPTED_COORDINATES
                    else donor_translation(coordinate, base_rows)
                )
                owner = "segment_adapted" if (
                    coordinate in CONTEXT_ADAPTED_COORDINATES
                ) else "segment"
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                row = prefill_rows.get(coordinate)
                if row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                prefill_evidence = row.get("base_exact_reuse_prefill")
                if not isinstance(prefill_evidence, dict):
                    raise RuntimeError(
                        f"segment {SEGMENT} malformed prefill companion: "
                        f"{coordinate}"
                    )
                prefill_reference = str(
                    prefill_evidence["base_coordinate"]
                )
                donor_row = base_rows.get(prefill_reference)
                if (
                    prefill_reference != reference
                    or not base_row_is_approved(donor_row)
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} invalid prefill donor: "
                        f"{coordinate}"
                    )
                assert donor_row is not None
                actual = str(row["translation"])
                expected = str(donor_row["translation"])
                owner = "prefill"
                seen_prefill.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record owner: "
                    f"{coordinate}"
                )
            if actual != expected:
                raise RuntimeError(
                    f"segment {SEGMENT} Base assembly drifted: "
                    f"{coordinate}"
                )
            owners.append(owner)
            translations.append(actual)
            references.append(reference)
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                tuple(references),
                EXPECTED_SOURCE_CONTROLS_BY_RECORD[record_id],
                EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id],
                record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or set(OPERAND_MASKED_BASE_RECORD_IDS)
        != set(TARGET_RECORD_IDS)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "complete assembly",
        tuple(assembly_evidence),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def reachable_call_graph(
    records: dict[tuple[int, int], Any],
    root: tuple[int, int],
) -> tuple[tuple[Any, ...], tuple[tuple[int, int], ...]]:
    pending: deque[tuple[int, int]] = deque([root])
    visited: set[tuple[int, int]] = set()
    edges: list[tuple[Any, ...]] = []
    terminals: list[tuple[int, int]] = []
    while pending:
        coordinate = pending.popleft()
        if coordinate in visited:
            continue
        if coordinate not in records:
            raise RuntimeError(
                f"segment {SEGMENT} missing call target: {coordinate}"
            )
        visited.add(coordinate)
        joined = b"".join(gap_bytes(records[coordinate]))
        next_coordinates: list[tuple[int, int]] = []
        for opcode in (b"\x01\x43", b"\x01\x4A"):
            for match in re.finditer(
                re.escape(opcode) + b"(.{4})",
                joined,
                re.DOTALL,
            ):
                operand = int.from_bytes(match.group(1), "little")
                target = (operand // 10_000, operand % 10_000)
                edges.append(
                    (
                        coordinate,
                        opcode.hex().upper(),
                        operand,
                        target,
                    )
                )
                next_coordinates.append(target)
                pending.append(target)
        if not next_coordinates:
            terminals.append(coordinate)
    graph = tuple(
        (
            coordinate,
            sha256_bytes(records[coordinate].data),
            literal_texts(records, coordinate),
            tuple(
                value.hex().upper()
                for value in gap_bytes(records[coordinate])
            ),
        )
        for coordinate in sorted(visited)
    ) + (("edges", tuple(sorted(edges))),)
    return graph, tuple(sorted(terminals))


def assert_call_graphs(prepared: Any) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    for operand in EXPECTED_CALL_ROOTS:
        graph, terminals = reachable_call_graph(
            current_records,
            (0, operand),
        )
        terminal_literals = tuple(
            literal_texts(current_records, coordinate)
            for coordinate in terminals
        )
        if (
            not graph
            or not terminals
            or any(len(values) > 1 for values in terminal_literals)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: {operand}"
            )
        terminal_set = {
            values[0]
            for values in terminal_literals
            if values
        }
        if terminal_set != EXPECTED_TERMINAL_SETS[operand]:
            raise RuntimeError(
                f"segment {SEGMENT} terminal set drifted: {operand}"
            )
        evidence.append(
            (operand, graph, terminals, terminal_literals)
        )
    guarded_digest(
        "call graph",
        tuple(evidence),
        EXPECTED_CALL_GRAPH_SHA256,
    )
    conflict_summary = (
        RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS,
        (
            4196,
            (1096,),
            "prefill_existential_stem_plus_full_terminal_conflict",
        ),
        (
            4204,
            (772,),
            "one_negative_terminal_branch_cannot_follow_prefill_stem",
        ),
        (
            4205,
            (628, 766, 550),
            "proposal_prefill_stems_and_full_terminals_conflict",
        ),
        (
            (4208, 4209, 4211),
            "source_calls_removed_from_current_record",
            "adapted_target_complete_but_prefill_companions_incomplete",
        ),
        (
            4212,
            (538, 1174, 190),
            "prefill_stems_optional_honorific_and_target_suffix_conflict",
        ),
        False,
    )
    guarded_digest(
        "runtime conflict",
        conflict_summary,
        EXPECTED_RUNTIME_CONFLICT_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "speaker style",
        tuple(SPEAKER_STYLE.items()),
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or TRANSLATIONS["6:4184:0"] != "와(과) 함께\n"
        or TRANSLATIONS["6:4198:1"] != "을(를) 포함한\n"
        or TRANSLATIONS["6:4208:0"] != "알겠습니다."
        or TRANSLATIONS["6:4209:0"] != "알겠습니다."
        or TRANSLATIONS["6:4211:2"] != " 지시해 주십시오."
        or TRANSLATIONS["6:4212:2"] != "지시해 주"
        or len(PREFILL_COMPANION_COORDINATES) != 25
        or len(OPERAND_MASKED_BASE_RECORD_IDS) != 20
        or len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS) != 7
        or "당가" in "\n".join(TRANSLATIONS.values())
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            "runtime_pending",
            coordinate,
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_base_globals()
    return BASE.build_candidate(prepared, records_by_label)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source_record = records_by_label["jp"][
        (BLOCK_ID, record_id)
    ]
    current_record = records_by_label["current"][
        (BLOCK_ID, record_id)
    ]
    source_controls = runtime_controls(source_record)
    current_controls = runtime_controls(current_record)
    if (
        source_controls != EXPECTED_SOURCE_CONTROLS_BY_RECORD[record_id]
        or current_controls != EXPECTED_CURRENT_CONTROLS_BY_RECORD[record_id]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted"
        )
    conflict = (
        record_id in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
    )
    return {
        "runtime_category": (
            "pk_current_gap_variant_morphology_conflict"
            if record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS
            else (
                "pk_live_morphology_conflict"
                if conflict
                else "pk_calls_and_dynamic_tokens_base_semantic_donor"
            )
        ),
        "speaker_style": SPEAKER_STYLE[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(source_record)
            )
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(
                value.hex().upper()
                for value in gap_bytes(current_record)
            )
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source_record) == gap_bytes(current_record),
        "source_calls_removed_from_current":
        record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
        "base_record_coordinate":
        f"6:{BASE_RECORD_MAPPING[record_id]}",
        "base_match_kind": "operand_masked",
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "live_pk_call_graphs_reviewed": True,
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical": not conflict,
        "base_runtime_state_inherited": False,
        "base_vm_verification_inherited": False,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    tuple[str, ...],
]:
    patch_base_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(prepared, records_by_label)
    assert_base_and_complete_assembly(prepared, records_by_label)
    assert_call_graphs(prepared)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records_by_label,
    )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "pk_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256":
                target["source_record_raw_sha256"],
                "current_ko_utf16le_sha256":
                target["current_ko_utf16le_sha256"],
                "translation": TRANSLATIONS[coordinate],
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present": True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companions_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "source_current_gap_variant_reviewed":
                record_id in SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS,
                "base_wording_contextually_adapted":
                coordinate in CONTEXT_ADAPTED_COORDINATES,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "speaker_style": SPEAKER_STYLE[record_id],
                "line_count_before": current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(records_by_label, record_id),
            }
        )
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_base_globals()
    BASE.assert_tamper_rejection(prepared, rows, candidate)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    if DISCOVERED_PINS:
        print(
            json.dumps(
                {
                    **DISCOVERED_PINS,
                    "candidate": candidate_sha256,
                    "changed literal count": changed,
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 26
        or len(validated) != 26
        or counts != Counter({"runtime_fragment_pending": 26})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_assembly_evidence"][
                "runtime_morphology_conflict_detected"
            ]
            is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
            if coordinate_key(str(row["coordinate"]))[1]
            in RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B043_S1141",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "slice_first_coordinate": "6:4184:0",
                "slice_last_coordinate": "6:4213:0",
                "first_residual_coordinate": TARGET_COORDINATES[0],
                "last_residual_coordinate": TARGET_COORDINATES[-1],
                "queue_record_count": 107,
                "queue_visible_count": 200,
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 41,
                "residual_count": 26,
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "context_adapted_target_count":
                len(CONTEXT_ADAPTED_COORDINATES),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
                "source_current_gap_variant_record_count":
                len(SOURCE_CURRENT_GAP_VARIANT_RECORD_IDS),
                "runtime_morphology_conflict_record_count":
                len(RUNTIME_MORPHOLOGY_CONFLICT_RECORD_IDS),
                "optional_neighbors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "speaker_style_sha256":
                EXPECTED_SPEAKER_STYLE_SHA256,
                "terminology_policy_sha256":
                EXPECTED_TERMINOLOGY_POLICY_SHA256,
                "call_graph_sha256":
                EXPECTED_CALL_GRAPH_SHA256,
                "runtime_conflict_sha256":
                EXPECTED_RUNTIME_CONFLICT_SHA256,
                "decision_sha256":
                sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256":
                sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "full_queue_universe_guarded": True,
                "slice_prefill_context_guarded": True,
                "canonical_base_donors_pinned": True,
                "complete_record_assembly_guarded": True,
                "source_current_gap_variants_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "runtime_morphology_conflicts_guarded": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "runtime_promotion_authorized": False,
                "speaker_registers_reviewed": True,
                "historical_terminology_reviewed": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
