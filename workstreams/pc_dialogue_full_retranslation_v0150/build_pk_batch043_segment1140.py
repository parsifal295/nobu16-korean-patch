#!/usr/bin/env python3
"""Build source-redacted PK B043 segment 1140 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch042_segment1137.py"
CALL_GRAPH_PATH = (
    WORKSTREAM / "build_pk_batch040_segment1132.py"
)
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B043_S1140.private.v1.jsonl"
PREFILL = (
    DECISIONS_ROOT
    / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
)
BASE_PROMOTED = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B042_S1138.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B042_S1139.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B043_S1141.private.v1.jsonl",
)

SEGMENT = 1140
QUEUE_BATCH_ID = "pk_msggame-B043"
QUEUE_START = 0
QUEUE_STOP = 67
QUEUE_FIRST_RECORD = 4156
QUEUE_LAST_RECORD = 4262
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:4156:0",
    "6:4156:1",
    "6:4157:0",
    "6:4157:1",
    "6:4157:2",
    "6:4158:0",
    "6:4158:1",
    "6:4159:0",
    "6:4160:1",
    "6:4167:1",
    "6:4168:1",
    "6:4169:1",
    "6:4170:1",
    "6:4171:1",
    "6:4172:1",
    "6:4173:0",
    "6:4178:0",
    "6:4178:1",
    "6:4182:2",
    "6:4183:2",
)
TRANSLATIONS = {
    "6:4156:0": "「",
    "6:4156:1": "」이(가) 실패",
    "6:4157:0": "「",
    "6:4157:1": "」이(가) 실패,",
    "6:4157:2": "와(과)",
    "6:4158:0": "「",
    "6:4158:1": "」이(가) 중단",
    "6:4159:0": "「",
    "6:4160:1": "」이(가) 발생",
    "6:4167:1": "의",
    "6:4168:1": "의",
    "6:4169:1": "의",
    "6:4170:1": "의",
    "6:4171:1": "의",
    "6:4172:1": "의",
    "6:4173:0": "의",
    "6:4178:0":
    "적의 성을 공략하기에는\n전선의 병력만으로는 "
    "역부족임이 틀림",
    "6:4178:1": "\n더 많은 병력이 필요한 상태",
    "6:4182:2": "면\n",
    "6:4183:2": "을(를) 포함한\n",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    4156,
    4157,
    4158,
    4159,
    4160,
    4167,
    4168,
    4169,
    4170,
    4171,
    4172,
    4173,
    4178,
    4182,
    4183,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
EXPECTED_ARITY = {
    4156: 2,
    4157: 4,
    4158: 2,
    4159: 2,
    4160: 2,
    4167: 3,
    4168: 3,
    4169: 3,
    4170: 3,
    4171: 3,
    4172: 3,
    4173: 3,
    4178: 2,
    4182: 4,
    4183: 4,
}
BASE_RECORD_MAPPING = {
    record_id: record_id - 30
    for record_id in TARGET_RECORD_IDS
    if record_id != 4178
}
RAW_EXACT_BASE_RECORD_IDS = (
    4156,
    4157,
    4158,
    4159,
    4160,
)
OPERAND_MASKED_BASE_RECORD_IDS = (
    4167,
    4168,
    4169,
    4170,
    4171,
    4172,
    4173,
    4182,
    4183,
)
MANUAL_CONTEXT_RECORD_IDS = (4178,)
SLICE_PREFILL_COORDINATES = (
    "6:4157:3",
    "6:4159:1",
    "6:4160:0",
    "6:4161:0",
    "6:4161:1",
    "6:4162:0",
    "6:4162:1",
    "6:4163:0",
    "6:4163:1",
    "6:4164:0",
    "6:4164:1",
    "6:4165:0",
    "6:4165:1",
    "6:4166:0",
    "6:4166:1",
    "6:4167:0",
    "6:4167:2",
    "6:4168:0",
    "6:4168:2",
    "6:4169:0",
    "6:4169:2",
    "6:4170:0",
    "6:4170:2",
    "6:4171:0",
    "6:4171:2",
    "6:4172:0",
    "6:4172:2",
    "6:4173:1",
    "6:4173:2",
    "6:4174:0",
    "6:4174:1",
    "6:4175:0",
    "6:4175:1",
    "6:4176:0",
    "6:4177:0",
    "6:4177:1",
    "6:4179:0",
    "6:4179:1",
    "6:4180:0",
    "6:4181:0",
    "6:4181:1",
    "6:4182:0",
    "6:4182:1",
    "6:4182:3",
    "6:4183:0",
    "6:4183:1",
    "6:4183:3",
)
PREFILL_COMPANION_COORDINATES = (
    "6:4157:3",
    "6:4159:1",
    "6:4160:0",
    "6:4167:0",
    "6:4167:2",
    "6:4168:0",
    "6:4168:2",
    "6:4169:0",
    "6:4169:2",
    "6:4170:0",
    "6:4170:2",
    "6:4171:0",
    "6:4171:2",
    "6:4172:0",
    "6:4172:2",
    "6:4173:1",
    "6:4173:2",
    "6:4182:0",
    "6:4182:1",
    "6:4182:3",
    "6:4183:0",
    "6:4183:1",
    "6:4183:3",
)
PREFILL_ONLY_COORDINATES = tuple(
    coordinate
    for coordinate in SLICE_PREFILL_COORDINATES
    if coordinate not in PREFILL_COMPANION_COORDINATES
)
BASE_DONOR_COORDINATES = {
    f"6:{record_id}:{literal_id}":
    (f"6:{base_record_id}:{literal_id}",)
    for record_id, base_record_id
    in BASE_RECORD_MAPPING.items()
    for literal_id in range(EXPECTED_ARITY[record_id])
}
BASE_DONOR_COORDINATES.update(
    {
        "6:4178:0": ("6:4148:0", "6:4147:0"),
        "6:4178:1": ("6:4148:0", "6:4147:0"),
    }
)
BASE_CONTEXT_REFERENCES = {
    coordinate: BASE_DONOR_COORDINATES[coordinate][0]
    for coordinate in TARGET_COORDINATES
}
CONTEXT_RECORD_IDS = tuple(
    range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1)
)
BOUNDARY_RECORD_IDS = (
    4154,
    4155,
    4156,
    4160,
    4166,
    4167,
    4173,
    4174,
    4177,
    4178,
    4181,
    4182,
    4183,
    4184,
)
EXPECTED_CALL_ROOTS = (
    8,
    178,
    424,
    514,
    562,
    568,
    754,
    1186,
)
EXPECTED_CRITICAL_TERMINAL_SETS = {
    178: {"있다", "있사옵니다", "있습니다"},
    424: {"하겠다", "하겠습니다", "하자", "합시다"},
    514: {"", "다"},
    562: {"다", "이오", "이옵니다", "입니다"},
    568: {"다", "이오", "입니다"},
    754: {"없다", "없사옵니다", "없습니다"},
    1186: {"받으면", "주려무나", "주시오"},
}
SPEAKER_STYLE = {
    4156: "neutral_system_project_failure_notice",
    4157: "neutral_system_project_failure_relation_notice",
    4158: "neutral_system_project_cancellation_notice",
    4159: "neutral_system_expired_project_disposal_notice",
    4160: "neutral_system_domain_problem_notice",
    4167: "dynamic_corps_march_status",
    4168: "dynamic_corps_march_status",
    4169: "dynamic_corps_march_status",
    4170: "dynamic_multi_front_corps_march_status",
    4171: "dynamic_multi_front_corps_march_status",
    4172: "dynamic_multi_front_corps_march_status",
    4173: "dynamic_attack_preparation_advice",
    4178: "dynamic_enemy_castle_force_assessment",
    4182: "dynamic_corps_policy_support_advice",
    4183: "dynamic_domestic_progress_advice",
}
TERMINOLOGY_POLICY = (
    ("project_failure", "실패"),
    ("project_cancellation", "중단"),
    ("relation_deterioration", "관계 악화"),
    ("domain_problem", "영내 문제"),
    ("corps", "군단"),
    ("march", "진군"),
    ("military_preparations", "군비"),
    ("sortie", "출진"),
    ("front_line_troops", "전선의 병력"),
    ("odds", "승산"),
    ("castle_capture", "성 공략"),
    ("fief_control", "지행지 장악"),
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
    "A4D37420E8B388B5124EB805FAE2F898"
    "AD8315E3ABFA1301096EE76D65DB3413"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "DA9E11BDFDFC9943827D1F53EFA17820"
    "1E4419926D3479CB5BAA21E1E65268F6"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "E718F17CF8EB8E573E35BBABD0417D7EA"
    "443F5D16E6ACB2F307F40A5F6FF6C14"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "F5007AE0A70A5010807C135DF1F0FB4B"
    "5D16C621853D20563D7DD4E786D8F8B8"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "81962ECB7AA9848E6FFD9C38C1EBC275"
    "2977BEE87477D35E7553FE7DB21F9386"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "3A0F2EF9E30A41B5BB9824BE2B9074D3"
    "DCFF1BFA2E97E22EF1463078CFC74BAB"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "D062A9441A1063D792D90F267E1B30A2"
    "3391706C5684CED03B5221D2678BB2B2"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "9306A0765FEB55D7B845DAFB25D6A6C5"
    "E03A0EE6030A395ECE814A406B6CCF42"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "86F5B91DFC98061BD68C8EB280F2A0E8"
    "A2EC9F55EF8F927CFEC1433CD00A769E"
)
EXPECTED_BOUNDARY_SHA256 = (
    "2C258152E0C062BF4273367E297180080"
    "251CF5903D91F818F8651BD80E66BF1"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "558E72A1AA0128BD57B99FDA7417BF17"
    "3B26C5AAFAD01A9FFC50875818460051"
)
EXPECTED_BASE_CONTEXT_SHA256 = (
    "CBB3BD0D218B37D64C456A5E60A36E18"
    "DAC0F4E16B659B6B8F101390851CC1F5"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "BF008A4E5412DC66405D129ACF40F196"
    "9F554CCF39E7D85D5574BE3652F4C747"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "E9D012795C2DE5B18E5FFDC4A630E6BB"
    "6AAC121D3CB1C919269EC16B16356DEC"
)
EXPECTED_RUNTIME_CONFLICT_SHA256 = (
    "C1BA1B0C439D68AA38A215E8E73ACCCB"
    "6D6D7479A378FE4AF3DD4CEC5555C80E"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "8684CCF1C634446833E05BBC976DB15CD"
    "3A9B9C91D2AEFE766AFAE95139F7F85"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "F6CF071A16D423D81ECEB9ED9C0BEB51"
    "55643581D8FDA3024D22E6FD2A53552B"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "C23F68E5EEE0FD49EA29E45D791F578A"
    "30D09BB7A0475043F7B0790CABA623EC"
)
EXPECTED_CANDIDATE_SHA256 = (
    "A5BBA75B72E55F6C6F04423BD8F1F7CA"
    "0F29B5A5C0822B37CBE136AFC5F7FAC2"
)
EXPECTED_CHANGED_LITERAL_COUNT = 5

DISCOVERED_PINS: dict[str, str] = {}

BASIS = (
    "The complete B043 queue universe and zero-based visible ordinal "
    "slice [0,67) are pinned before the twenty-row residual is derived "
    "against the immutable forty-seven-row exact-reuse prefill and every "
    "available independent PK decision output. Fifteen complete target "
    "records are assembled with twenty-three same-record prefill "
    "companions, while all twenty-four fully-prefilled slice literals are "
    "also pinned and reviewed. Pristine PK Japanese, current Korean, PC "
    "English, Simplified Chinese, Traditional Chinese, adjacent records "
    "and completed Base semantic donors are reviewed together. Records "
    "4156-4160 are raw-exact Base copies; records 4167-4173 and 4182-4183 "
    "are literal-exact and operand-masked Base copies whose shifted PK "
    "call roots are preserved; record 4178 is PK-exclusive and is adapted "
    "from the verified Base front-line-force and odds terminology plus "
    "its complete multilingual context. Its two Korean fragments are "
    "rewritten as common stems that compose grammatically with every live "
    "PK ending branch. Other inherited completion fragments still expose "
    "known call-composition conflicts, so every row remains runtime "
    "pending and no Base VM state is inherited. Project status, relations, "
    "domain problems, corps movement, military preparations, sorties, "
    "front-line strength, castle capture and fief control terminology, "
    "speaker register, tokens, calls, whitespace, line counts, complete "
    "record assembly, reverse overlay, outside-scope identity, two-run "
    "reproduction, tamper rejection and read-only Steam input are guarded."
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_module(
    "pc_dialogue_full_retranslation_v0150_pk_s1140_template",
    TEMPLATE_PATH,
)
CALL_GRAPH = load_module(
    "pc_dialogue_full_retranslation_v0150_pk_s1140_call_graph",
    CALL_GRAPH_PATH,
)
ENGINE = TEMPLATE.ENGINE
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records
runtime_controls = TEMPLATE.runtime_controls
mask_call_operands = TEMPLATE.mask_call_operands


def patch_template_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
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
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_base_globals()


def guarded_digest(
    label: str, value: Any, expected: str
) -> str:
    actual = canonical_sha256(value)
    if expected == "TO_PIN":
        DISCOVERED_PINS[label] = actual
    elif actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def all_existing_decisions(
    prepared: Any,
) -> dict[str, dict[str, Any]]:
    existing: dict[str, dict[str, Any]] = {}
    owners: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(
            prepared, path, require_complete=False
        )
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = owners.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
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
        raise RuntimeError(f"segment {SEGMENT} source input drifted")
    ENGINE.validate_decisions(
        prepared, PREFILL, require_complete=False
    )
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line
        and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
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
        raise RuntimeError(f"segment {SEGMENT} queue universe drifted")
    guarded_digest(
        "EXPECTED_QUEUE_UNIVERSE_SHA256",
        visible,
        EXPECTED_QUEUE_UNIVERSE_SHA256,
    )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:4156:0"
        or queue_slice[-1] != "6:4183:3"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    guarded_digest(
        "EXPECTED_QUEUE_SLICE_SHA256",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_rows
    )
    if (
        len(prefilled) != 47
        or prefilled != SLICE_PREFILL_COORDINATES
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill drifted")
    guarded_digest(
        "EXPECTED_PREFILLED_COORDINATE_SHA256",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(
                prefill_rows[coordinate][
                    "source_record_raw_sha256"
                ]
            ),
            str(
                prefill_rows[coordinate][
                    "current_ko_utf16le_sha256"
                ]
            ),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate][
                    "base_exact_reuse_prefill"
                ]["base_coordinate"]
            ),
            str(
                prefill_rows[coordinate][
                    "base_exact_reuse_prefill"
                ]["pk_operand_masked_gap_template_sha256"]
            ),
            str(
                prefill_rows[coordinate][
                    "base_exact_reuse_prefill"
                ]["translation_utf16le_sha256"]
            ),
        )
        for coordinate in prefilled
    )
    guarded_digest(
        "EXPECTED_PREFILL_SLICE_CONTEXT_SHA256",
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
            f"segment {SEGMENT} residual drifted: {len(residual)}"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(
                prepared, path, require_complete=False
            )
            optional_present.append(path.name)
    return tuple(optional_present)


def assert_context_contracts(
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
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
            sha256_bytes(
                records[(BLOCK_ID, record_id)].data
            ),
            literal_texts(
                records, (BLOCK_ID, record_id)
            ),
        )
        for label, records in records_by_label.items()
        for record_id in CONTEXT_RECORD_IDS
    )
    gaps = tuple(
        (
            label,
            record_id,
            tuple(
                value.hex().upper()
                for value in gap_bytes(
                    records_by_label[label][
                        (BLOCK_ID, record_id)
                    ]
                )
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    boundaries = tuple(
        (
            label,
            record_id,
            sha256_bytes(
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
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
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ]
            ),
        )
        for label in ("jp", "current")
        for record_id in TARGET_RECORD_IDS
    )
    for label, value, expected in (
        (
            "EXPECTED_SOURCE_TARGET_SHA256",
            source_target,
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "EXPECTED_CURRENT_TARGET_SHA256",
            current_target,
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "EXPECTED_CONTEXT_CORPUS_SHA256",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "EXPECTED_GAP_CONTRACT_SHA256",
            gaps,
            EXPECTED_GAP_CONTRACT_SHA256,
        ),
        (
            "EXPECTED_BOUNDARY_SHA256",
            boundaries,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "EXPECTED_RUNTIME_CONTROL_SHA256",
            controls,
            EXPECTED_RUNTIME_CONTROL_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    for record_id in TARGET_RECORD_IDS:
        source = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        current = records_by_label["current"][
            (BLOCK_ID, record_id)
        ]
        if (
            gap_bytes(source) != gap_bytes(current)
            or runtime_controls(source)
            != runtime_controls(current)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} source/current runtime drifted: "
                f"{record_id}"
            )


def base_row_is_approved(
    row: dict[str, Any] | None,
) -> bool:
    return bool(
        row is not None
        and row.get("semantic_review") == "approved"
        and row.get("runtime_review") in ("verified", "not_required")
    )


def base_match_kind(record_id: int) -> str:
    if record_id in RAW_EXACT_BASE_RECORD_IDS:
        return "raw_exact"
    if record_id in OPERAND_MASKED_BASE_RECORD_IDS:
        return "operand_masked"
    if record_id in MANUAL_CONTEXT_RECORD_IDS:
        return "pk_exclusive_semantic_donor"
    raise RuntimeError(
        f"segment {SEGMENT} missing Base match kind: {record_id}"
    )


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} Base input drifted")
    base_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(PREFILL)
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
        pk_record = records_by_label["jp"][
            (BLOCK_ID, record_id)
        ]
        pk_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        if len(pk_literals) != EXPECTED_ARITY[record_id]:
            raise RuntimeError(
                f"segment {SEGMENT} arity drifted: {record_id}"
            )
        kind = base_match_kind(record_id)
        base_record_id = BASE_RECORD_MAPPING.get(record_id)
        base_record = (
            base_source[(BLOCK_ID, base_record_id)]
            if base_record_id is not None
            else None
        )
        if base_record is not None:
            base_literals = literal_texts(
                base_source, (BLOCK_ID, base_record_id)
            )
            raw_exact = pk_record.data == base_record.data
            literal_exact = pk_literals == base_literals
            masked_exact = (
                mask_call_operands(pk_record)
                == mask_call_operands(base_record)
            )
            if (
                (
                    kind == "raw_exact"
                    and not (raw_exact and literal_exact)
                )
                or (
                    kind == "operand_masked"
                    and (
                        raw_exact
                        or not literal_exact
                        or not masked_exact
                    )
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base match drifted: "
                    f"{record_id}"
                )
        owners: list[str] = []
        translations: list[str] = []
        references: list[tuple[str, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = (
                f"{BLOCK_ID}:{record_id}:{literal_id}"
            )
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "target"
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                actual = str(
                    prefill_rows[coordinate]["translation"]
                )
                owner = "prefill"
                seen_prefill.add(coordinate)
            else:
                raise RuntimeError(
                    f"segment {SEGMENT} incomplete record: "
                    f"{coordinate}"
                )
            refs = BASE_DONOR_COORDINATES[coordinate]
            if kind != "pk_exclusive_semantic_donor":
                row = base_rows.get(refs[0])
                if (
                    not base_row_is_approved(row)
                    or actual != str(row["translation"])
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} Base translation drifted: "
                        f"{coordinate}"
                    )
                assert row is not None
                base_current_text = literal_texts(
                    base_current,
                    (BLOCK_ID, int(refs[0].split(":")[1])),
                )[literal_id]
                base_evidence.append(
                    (
                        coordinate,
                        refs,
                        kind,
                        sha256_bytes(pk_record.data),
                        sha256_bytes(base_record.data),
                        pk_literals[literal_id],
                        base_current_text,
                        actual,
                        str(row["runtime_review"]),
                    )
                )
            else:
                donor_rows = [base_rows.get(ref) for ref in refs]
                if not all(
                    base_row_is_approved(row)
                    for row in donor_rows
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} manual donor drifted: "
                        f"{coordinate}"
                    )
                donor_values = tuple(
                    str(row["translation"])
                    for row in donor_rows
                    if row is not None
                )
                if donor_values != (
                    "적의 성을 공략하기에는\n"
                    "전선의 병력만으로는 부족하다\n"
                    "더 많은 병력이 필요하다",
                    "전선의 병력이 부족해\n"
                    "공략할 수 있는 세력이",
                ):
                    raise RuntimeError(
                        f"segment {SEGMENT} manual donor values drifted"
                    )
                base_evidence.append(
                    (
                        coordinate,
                        refs,
                        kind,
                        sha256_bytes(pk_record.data),
                        pk_literals[literal_id],
                        actual,
                        donor_values,
                    )
                )
            owners.append(owner)
            translations.append(actual)
            references.append(refs)
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                kind,
                tuple(owners),
                tuple(translations),
                tuple(references),
                runtime_controls(pk_record),
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or len(PREFILL_COMPANION_COORDINATES) != 23
        or len(PREFILL_ONLY_COORDINATES) != 24
    ):
        raise RuntimeError(
            f"segment {SEGMENT} assembly ownership drifted"
        )
    guarded_digest(
        "EXPECTED_BASE_CONTEXT_SHA256",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "EXPECTED_COMPLETE_ASSEMBLY_SHA256",
        tuple(assembly_evidence),
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def assert_call_graphs(prepared: Any) -> None:
    current_records = ENGINE.archive_records(
        prepared.resources["pk_msggame"].current_archive
    )
    evidence: list[tuple[Any, ...]] = []
    terminal_sets: dict[int, set[str]] = {}
    for operand in EXPECTED_CALL_ROOTS:
        graph, terminals = CALL_GRAPH.reachable_call_graph(
            current_records, (0, operand)
        )
        terminal_literals = tuple(
            literal_texts(current_records, coordinate)
            for coordinate in terminals
        )
        if (
            not graph
            or not terminals
            or any(
                len(values) > 1
                for values in terminal_literals
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} call graph drifted: "
                f"{operand}"
            )
        values = {
            value
            for literals in terminal_literals
            for value in literals
        }
        terminal_sets[operand] = values
        if (
            operand in EXPECTED_CRITICAL_TERMINAL_SETS
            and values
            != EXPECTED_CRITICAL_TERMINAL_SETS[operand]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} terminal set drifted: "
                f"{operand}"
            )
        if operand == 8 and (
            len(terminals) != 32 or len(values) != 23
        ):
            raise RuntimeError(
                f"segment {SEGMENT} dynamic name graph drifted"
            )
        evidence.append(
            (operand, graph, terminals, terminal_literals)
        )
    guarded_digest(
        "EXPECTED_CALL_GRAPH_SHA256",
        tuple(evidence),
        EXPECTED_CALL_GRAPH_SHA256,
    )
    literal_zero = TRANSLATIONS["6:4178:0"]
    literal_one = TRANSLATIONS["6:4178:1"]
    joined_zero = {
        literal_zero + ending
        for ending in terminal_sets[754]
    }
    joined_one = {
        literal_one + ending
        for ending in terminal_sets[562]
    }
    expected_zero = {
        "적의 성을 공략하기에는\n전선의 병력만으로는 "
        "역부족임이 틀림없다",
        "적의 성을 공략하기에는\n전선의 병력만으로는 "
        "역부족임이 틀림없사옵니다",
        "적의 성을 공략하기에는\n전선의 병력만으로는 "
        "역부족임이 틀림없습니다",
    }
    expected_one = {
        "\n더 많은 병력이 필요한 상태다",
        "\n더 많은 병력이 필요한 상태이오",
        "\n더 많은 병력이 필요한 상태이옵니다",
        "\n더 많은 병력이 필요한 상태입니다",
    }
    if joined_zero != expected_zero or joined_one != expected_one:
        raise RuntimeError(
            f"segment {SEGMENT} repaired branch grammar drifted"
        )
    conflict_summary = (
        (
            (4167, 4168, 4169, 4170, 4171, 4172),
            568,
            "prefill_nominal_status_plus_plain_da_branch",
        ),
        (
            (4182,),
            (754, 1186, 514),
            "immutable_prefill_and_conditional_branch_conflicts",
        ),
        (
            (4183,),
            754,
            "immutable_prefill_spacing_conflict",
        ),
        (
            (4178,),
            (754, 562),
            "all_korean_branches_grammatical_after_repair",
        ),
        tuple(sorted(joined_zero)),
        tuple(sorted(joined_one)),
        False,
    )
    guarded_digest(
        "EXPECTED_RUNTIME_CONFLICT_SHA256",
        conflict_summary,
        EXPECTED_RUNTIME_CONFLICT_SHA256,
    )


def assert_semantics(
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> None:
    guarded_digest(
        "EXPECTED_TARGET_COORDINATE_SHA256",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "EXPECTED_TRANSLATION_POLICY_SHA256",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "EXPECTED_SPEAKER_STYLE_SHA256",
        tuple(SPEAKER_STYLE.items()),
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "EXPECTED_TERMINOLOGY_POLICY_SHA256",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or len(TRANSLATIONS) != 20
        or len(TARGET_RECORD_IDS) != 15
        or len(SLICE_PREFILL_COORDINATES) != 47
        or TRANSLATIONS["6:4157:2"] != "와(과)"
        or TRANSLATIONS["6:4158:1"] != "」이(가) 중단"
        or TRANSLATIONS["6:4173:0"] != "의"
        or TRANSLATIONS["6:4182:2"] != "면\n"
        or TRANSLATIONS["6:4183:2"]
        != "을(를) 포함한\n"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic policy drifted"
        )
    for coordinate, translation in TRANSLATIONS.items():
        block_id, record_id, literal_id = coordinate_key(
            coordinate
        )
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
            translation.count("\n")
            != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def build_candidate(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
) -> tuple[bytes, str, int]:
    patch_template_globals()
    candidate, candidate_sha256, changed = (
        TEMPLATE.build_candidate(prepared, records_by_label)
    )
    if EXPECTED_CANDIDATE_SHA256 == "TO_PIN":
        DISCOVERED_PINS[
            "EXPECTED_CANDIDATE_SHA256"
        ] = candidate_sha256
    elif candidate_sha256 != EXPECTED_CANDIDATE_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} candidate drifted"
        )
    return candidate, candidate_sha256, changed


def runtime_evidence(
    prepared: Any,
    records_by_label: dict[
        str, dict[tuple[int, int], Any]
    ],
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
        source_controls != current_controls
        or gap_bytes(source_record) != gap_bytes(current_record)
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime evidence drifted: "
            f"{record_id}"
        )
    kind = base_match_kind(record_id)
    conflict = record_id in {
        4167,
        4168,
        4169,
        4170,
        4171,
        4172,
        4182,
        4183,
    }
    return {
        "runtime_category": (
            "pk_dynamic_branches_repaired"
            if record_id == 4178
            else (
                "pk_dynamic_branch_conflict"
                if conflict
                else "pk_dynamic_tokens_base_semantic_donor"
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
        "source_current_runtime_gap_equal": True,
        "base_record_coordinate": (
            f"{BLOCK_ID}:{BASE_RECORD_MAPPING[record_id]}"
            if record_id in BASE_RECORD_MAPPING
            else None
        ),
        "base_match_kind": kind,
        "complete_record_assembly_reviewed": True,
        "all_same_record_prefill_companions_reviewed": True,
        "all_slice_prefill_rows_reviewed": True,
        "manual_pc_english_simplified_traditional_review": True,
        "live_pk_call_graphs_reviewed":
        bool(source_controls[0]),
        "runtime_morphology_conflict_detected": conflict,
        "all_speaker_branches_grammatical":
        record_id == 4178 or not source_controls[0],
        "pk_exclusive_semantic_adaptation":
        record_id == 4178,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
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
    patch_template_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(
        prepared
    )
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_and_complete_assembly(
        prepared, records_by_label
    )
    assert_call_graphs(prepared)
    assert_semantics(records_by_label)
    candidate, candidate_sha256, changed = build_candidate(
        prepared, records_by_label
    )
    rows: list[dict[str, Any]] = []
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(
            coordinate
        )
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
                "scope_classification":
                "runtime_fragment_pending",
                "layout_review": "runtime_pending",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "base_exact_reuse_prefill_excluded": True,
                "all_available_predecessors_validated": True,
                "optional_neighbor_outputs_validated_if_present":
                True,
                "manual_multilingual_context_review": True,
                "adjacent_record_context_review": True,
                "complete_record_fragment_review": True,
                "prefill_companions_reviewed": True,
                "all_slice_prefill_rows_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted":
                record_id == 4178,
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_match_kind": base_match_kind(record_id),
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "speaker_style": SPEAKER_STYLE[record_id],
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_evidence(
                    prepared, records_by_label, record_id
                ),
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
    patch_template_globals()
    TEMPLATE.assert_tamper_rejection(
        prepared, rows, candidate
    )
    tampered_policy = dict(TRANSLATIONS)
    tampered_policy["6:4178:0"] += "X"
    if (
        canonical_sha256(tuple(tampered_policy.items()))
        == EXPECTED_TRANSLATION_POLICY_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} manual policy tamper accepted"
        )
    tampered_candidate = ENGINE.rebuild_packed_with_literals(
        prepared.resources["pk_msggame"].current_blob,
        {
            coordinate_key(coordinate): translation
            for coordinate, translation
            in tampered_policy.items()
        },
    )
    if (
        tampered_candidate == candidate
        or sha256_bytes(tampered_candidate)
        == EXPECTED_CANDIDATE_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} candidate tamper accepted"
        )


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
        or optional_present != second[5]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} second-run reproduction drifted"
        )
    if DISCOVERED_PINS:
        print(
            json.dumps(
                {
                    **DISCOVERED_PINS,
                    "changed_literal_count": changed,
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2
    resource = prepared.resources["pk_msggame"]
    steam_path = resource.current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: "
            f"{steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared, OUTPUT, require_complete=False
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 20
        or len(validated) != 20
        or counts
        != Counter({"runtime_fragment_pending": 20})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["base_vm_verification_inherited"] is not False
            or row["line_count_preserved"] is not True
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} decision validation drifted"
        )
    assert_tamper_rejection(prepared, rows, candidate)
    if sha256_bytes(steam_path.read_bytes()) != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B043_S1140",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "slice_first_coordinate": "6:4156:0",
                "slice_last_coordinate": "6:4183:3",
                "slice_visible_count": 67,
                "exact_reuse_prefill_count": 47,
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "prefill_only_count":
                len(PREFILL_ONLY_COORDINATES),
                "residual_count": len(rows),
                "scope_classification_counts": dict(counts),
                "reviewed_record_count": len(TARGET_RECORD_IDS),
                "raw_exact_base_record_count":
                len(RAW_EXACT_BASE_RECORD_IDS),
                "operand_masked_base_record_count":
                len(OPERAND_MASKED_BASE_RECORD_IDS),
                "pk_exclusive_semantic_record_count":
                len(MANUAL_CONTEXT_RECORD_IDS),
                "call_root_count": len(EXPECTED_CALL_ROOTS),
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
                "manual_pk_jp_pc_en_sc_tc_review": True,
                "complete_multi_literal_records_guarded": True,
                "raw_exact_and_operand_masked_donors_guarded":
                True,
                "pk_exclusive_semantic_donor_guarded": True,
                "live_pk_call_graphs_guarded": True,
                "all_4178_korean_branches_grammatical": True,
                "remaining_runtime_conflicts_explicit": True,
                "runtime_tokens_and_gaps_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "base_runtime_state_inherited": False,
                "base_vm_verification_inherited": False,
                "runtime_promotion_authorized": False,
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
