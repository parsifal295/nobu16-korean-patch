#!/usr/bin/env python3
"""Build source-redacted PK B035 segment 1117 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
COMMON_PATH = WORKSTREAM / "build_pk_batch034_segment1115.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B035_S1117.private.v1.jsonl"
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
    DECISIONS_ROOT / "pk_msggame_B034_S1115.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B035_S1116.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B035_S1118.private.v1.jsonl",
)

SEGMENT = 1117
QUEUE_BATCH_ID = "pk_msggame-B035"
QUEUE_START = 67
QUEUE_STOP = 134
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = (
    "6:3393:1",
    "6:3393:2",
    "6:3394:1",
    "6:3395:0",
    "6:3398:3",
    "6:3399:0",
    "6:3399:1",
    "6:3400:0",
    "6:3400:2",
    "6:3401:0",
    "6:3401:1",
    "6:3401:2",
    "6:3402:0",
    "6:3403:0",
    "6:3403:1",
    "6:3404:1",
    "6:3405:0",
    "6:3405:1",
    "6:3405:2",
    "6:3405:3",
    "6:3406:1",
    "6:3406:2",
    "6:3406:4",
    "6:3407:0",
    "6:3407:1",
    "6:3407:2",
    "6:3408:0",
    "6:3409:0",
    "6:3409:1",
    "6:3409:2",
)
TRANSLATIONS = {
    "6:3393:1": "!\n어찌하여",
    "6:3393:2": "이(가)…",
    "6:3394:1": "인가",
    "6:3395:0": "뭐라고…!?\n…언젠가 후회하게 될 것이다",
    "6:3398:3": "!",
    "6:3399:0": "내가 당주라…알겠어,",
    "6:3399:1": (
        "에게 지지 않는\n"
        "훌륭하고 대단한 다이묘가 되어 보이겠다!\n"
        "똑똑히 지켜봐 줘!"
    ),
    "6:3400:0": "알겠사옵",
    "6:3400:2": ".\n반드시",
    "6:3401:0": "잘 알겠사옵니다,",
    "6:3401:1": "에게 지지 않도록\n내 무용으로 반드시",
    "6:3401:2": "의 이름을\n천하에 떨쳐 보이겠",
    "6:3402:0": "이 판단이 틀리지 않았음을\n이 한 생을 걸고 ",
    "6:3403:0": (
        "의 이름은 무겁지만 자랑스럽기도 하여\n"
        "절로 자세가 바로 서는 기분"
    ),
    "6:3403:1": "\n부디, 뒷일은",
    "6:3404:1": "은(는) 이",
    "6:3405:0": "부디 안심하소서,",
    "6:3405:1": "이(가) 지켜 온\n",
    "6:3405:2": (
        ", 나의 지략과 용맹으로 존속을…\n"
        "아니, 더 큰 번영을"
    ),
    "6:3405:3": "약속",
    "6:3406:1": "!\n",
    "6:3406:2": "의",
    "6:3406:4": "!",
    "6:3407:0": (
        ", 지금까지 우리 가문의 당주로서 소임을 다하느라\n"
        "참으로 수고하였소"
    ),
    "6:3407:1": "\n뒷일은",
    "6:3407:2": "에게",
    "6:3408:0": "이",
    "6:3409:0": "안심하고",
    "6:3409:1": ", 이",
    "6:3409:2": "이(가)\n당주라니",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES)
STATIC_COORDINATES: set[str] = set()
TARGET_RECORD_IDS = (
    3393,
    3394,
    3395,
    3398,
    3399,
    3400,
    3401,
    3402,
    3403,
    3404,
    3405,
    3406,
    3407,
    3408,
    3409,
)
DYNAMIC_RECORD_IDS = TARGET_RECORD_IDS
BASE_RECORD_MAPPING = {
    record_id: record_id - 7
    for record_id in TARGET_RECORD_IDS
}
BASE_CONTEXT_REFERENCES = {
    coordinate: (
        f"6:{BASE_RECORD_MAPPING[int(coordinate.split(':')[1])]}:"
        f"{coordinate.split(':')[2]}"
    )
    for coordinate in TARGET_COORDINATES
}
PREFILL_COMPANION_COORDINATES = (
    "6:3393:0",
    "6:3394:0",
    "6:3398:0",
    "6:3398:1",
    "6:3398:2",
    "6:3400:1",
    "6:3400:3",
    "6:3400:4",
    "6:3402:1",
    "6:3404:0",
    "6:3404:2",
    "6:3406:0",
    "6:3406:3",
    "6:3408:1",
    "6:3408:2",
    "6:3408:3",
)
RIGHT_BOUNDARY_COMPANION = "6:3409:3"
BOUNDARY_RECORD_IDS = (
    3375,
    3376,
    3392,
    3396,
    3397,
    3410,
)
EXPECTED_GAPS_BY_RECORD = {
    3393: ("", "0143EC020000", "014301000000", "050505"),
    3394: ("", "014374020000", "050505"),
    3395: ("", "014362020000050505"),
    3398: (
        "014308000000",
        "014388030000",
        "02473E",
        "014348040000",
        "050505",
    ),
    3399: ("", "014308000000", "050505"),
    3400: (
        "",
        "01431A020000",
        "014388030000",
        "014308000000",
        "02473E",
        "014348040000050505",
    ),
    3401: (
        "",
        "014308000000",
        "024734",
        "01432A040000050505",
    ),
    3402: ("", "02473E", "014394000000050505"),
    3403: (
        "024734",
        "014326020000",
        "014388030000050505",
    ),
    3404: (
        "014308000000",
        "02473E",
        "024633",
        "01436C010000050505",
    ),
    3405: (
        "",
        "014308000000",
        "02473E",
        "014390040000",
        "01438E000000050505",
    ),
    3406: (
        "",
        "014378010000",
        "014308000000",
        "014396040000",
        "01438E000000",
        "050505",
    ),
    3407: (
        "014308000000",
        "01434A020000",
        "014301000000",
        "014388030000050505",
    ),
    3408: (
        "",
        "024635",
        "01430C010000",
        "014308000000",
        "0143360400000143FC010000050505",
    ),
    3409: (
        "",
        "014342010000014308000000",
        "024635",
        "014374020000",
        "01432A040000050505",
    ),
}
EXPECTED_CONTROLS_BY_RECORD = {
    3393: ((748, 1), ()),
    3394: ((628,), ()),
    3395: ((610,), ()),
    3398: ((8, 904, 1096), ("02473E",)),
    3399: ((8,), ()),
    3400: ((538, 904, 8, 1096), ("02473E",)),
    3401: ((8, 1066), ("024734",)),
    3402: ((148,), ("02473E",)),
    3403: ((550, 904), ("024734",)),
    3404: ((8, 364), ("02473E", "024633")),
    3405: ((8, 1168, 142), ("02473E",)),
    3406: ((376, 8, 1174, 142), ()),
    3407: ((8, 586, 1, 904), ()),
    3408: ((268, 8, 1078, 508), ("024635",)),
    3409: ((322, 8, 628, 1066), ("024635",)),
}

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
EXPECTED_TARGET_COORDINATE_SHA256 = "B5C2268FF3DEAC0AC4C015EF5D9F523748F4C55A15F6BFA6D5B11B7984A46D65"
EXPECTED_QUEUE_SLICE_SHA256 = "DFB23CB80D3200B3F7FFC18700B2A91F1C9F1622C2EABEABE1BEED726F23D57B"
EXPECTED_PREFILLED_COORDINATE_SHA256 = "29301132A22BD5E6B3354A8E9D35CA6795E9E37155C4D69CEC3FF7CE42E47948"
EXPECTED_SOURCE_TARGET_SHA256 = "0CE6DD448DEF29D5C9DE63C7B19DE890F9263FD78F2AACED4DBA3917D65FBD61"
EXPECTED_CURRENT_TARGET_SHA256 = "89F708E73E1A7074C30914B55344CB81FF07E064C4C6485D32B698C6C192771E"
EXPECTED_CONTEXT_CORPUS_SHA256 = "3BD331162A684661792728F129C7C73E8637113039EC381B7E6677DBDD472FF9"
EXPECTED_GAP_CONTRACT_SHA256 = "0A643263158548C4299134A5AC03B67760A9D461DE382BBC31F0DE3D813EA8BF"
EXPECTED_BOUNDARY_SHA256 = "9327F6D08DE41255BC40F648298825BD9DDF5B45D441C7A361F1F9C5F8D894CD"
EXPECTED_RUNTIME_OPERAND_SHA256 = "0549C2404287667130CB62797C20FFD4DE23A81F0F9395C83F3518FA8353C855"
EXPECTED_DYNAMIC_RECORD_SHA256 = "A6711B33F7654862DAD797C3F5E9556E9286D0227AA4A911C0D871B4A527AB3D"
EXPECTED_BASE_CONTEXT_SHA256 = "AA166F970473DFDF6D418F504ABE53C81476FB5A91FC7CE0544A1C3CAA1EBF7A"
EXPECTED_PREFILL_COMPANION_SHA256 = "2258B5DA3B8DC4F32B0B68655FBA82F1E20354268ADF5C76EF0474F02136CCC8"
EXPECTED_ASSEMBLY_POLICY_SHA256 = "7EB6543D3ECE2450FF6FC581B4C2EF160036AF2BFCE8384B444811FC14C289C6"
EXPECTED_TERMINOLOGY_POLICY_SHA256 = "836B325B7120DDD402E524B0018711047E5F10B9E581516D8D3F0EA46E2EF544"
EXPECTED_RUNTIME_CATEGORY_SHA256 = "9B7819AFCD6B54844A302907EC0AC83582B0561141B7676C7B0B6C319510BD8B"
EXPECTED_TRANSLATION_POLICY_SHA256 = "E99FD9B2AF9F6623738732ACEC1A9FE133B8F13DF175253328985B80BBF7C337"
EXPECTED_CANDIDATE_SHA256 = "78450EF03234195A2C8709D2E629AB3A2608B2F40EF0F0496D1CBFBD7FE2EF37"
EXPECTED_CHANGED_LITERAL_COUNT = 18

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete "
    "PC EN SC TC records are context only; completed Base records pin "
    "dismissal protest and succession dialogue semantics, historical "
    "register, house terminology and speaker voice; the lifelong-service "
    "fragment adapts its Base donor only by retaining the protected PK "
    "trailing space before a runtime house-name token; all other targets "
    "use completed Base wording; sixteen same-record prefilled companions "
    "and the unowned right-boundary companion complete fifteen assembled "
    "records; all 37 prefilled queue rows and concurrent neighbor outputs "
    "are optional validated inputs rather than execution dependencies; "
    "direct calls, name and house tokens, adjacent boundaries, protected "
    "outer whitespace, line counts, bytecode gaps, reverse overlay, "
    "two-run reproduction, tamper rejection and read-only inputs are "
    "guarded; Base runtime state is not inherited and every PK target "
    "remains runtime pending"
)

DIRECT_CALL_RE = re.compile(b"\x01\x43(.{4})")


def load_common() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1117_common",
        COMMON_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {COMMON_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COMMON = load_common()
ENGINE = COMMON.ENGINE
sha256_bytes = COMMON.sha256_bytes
canonical_sha256 = COMMON.canonical_sha256
coordinate_key = COMMON.coordinate_key
literal_texts = COMMON.literal_texts
gap_bytes = COMMON.gap_bytes
read_jsonl = COMMON.read_jsonl
context_records = COMMON.context_records


def patch_common_globals() -> None:
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
        setattr(COMMON, name, value)
    COMMON.patch_common_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(
            f"segment {SEGMENT} {label} drifted: {actual}"
        )
    return actual


def decision_map(resource: str) -> dict[str, dict[str, Any]]:
    paths = (
        (BASE_PROMOTED,)
        if resource == "base_msggame"
        else tuple(
            sorted(
                DECISIONS_ROOT.glob(
                    "pk_msggame_*.private.v1.jsonl"
                )
            )
        )
    )
    result: dict[str, dict[str, Any]] = {}
    for path in paths:
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") == resource
                and isinstance(coordinate, str)
            ):
                result[coordinate] = row
    return result


def assert_queue_and_residual_contract(
    prepared: Any,
) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} pinned source input drifted"
        )
    ENGINE.validate_decisions(
        prepared,
        PREFILL,
        require_complete=False,
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
        len(queue_rows) != 109
        or len(visible) != 200
        or visible[0] != "6:3332:0"
        or visible[-1] != "6:3440:1"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} B035 queue universe drifted"
        )
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 67
        or queue_slice[0] != "6:3376:0"
        or queue_slice[-1] != "6:3409:2"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} queue bounds drifted"
        )
    guarded_digest(
        "queue slice",
        queue_slice,
        EXPECTED_QUEUE_SLICE_SHA256,
    )
    prefill_coordinates = {
        str(row["coordinate"]) for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate in prefill_coordinates
    )
    if len(prefilled) != 37:
        raise RuntimeError(
            f"segment {SEGMENT} prefill slice count drifted"
        )
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )

    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(
            prepared,
            path,
            require_complete=False,
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
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: "
                    f"{coordinate}"
                )
    residual = tuple(
        coordinate
        for coordinate in queue_slice
        if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: "
            f"{len(residual)} rows"
        )

    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(
                prepared,
                path,
                require_complete=False,
            )
            optional_present.append(path.name)
    return tuple(optional_present)


def runtime_controls(
    record: Any,
) -> tuple[tuple[int, ...], tuple[str, ...]]:
    gaps = gap_bytes(record)
    direct_calls = tuple(
        int.from_bytes(match.group(1), "little")
        for value in gaps
        for match in DIRECT_CALL_RE.finditer(value)
    )
    inline_tokens = tuple(
        value.hex().upper()
        for value in gaps
        if value.startswith(b"\x02")
    )
    return direct_calls, inline_tokens


def assert_context_contracts(
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
        for record_id in TARGET_RECORD_IDS
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
                    records_by_label["current"][
                        (BLOCK_ID, record_id)
                    ]
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
                records_by_label[label][
                    (BLOCK_ID, record_id)
                ].data
            ),
            literal_texts(
                records_by_label[label],
                (BLOCK_ID, record_id),
            ),
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
        for record_id in BOUNDARY_RECORD_IDS
    )
    operand_evidence = tuple(
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
    actual_dynamic = tuple(
        record_id
        for record_id in TARGET_RECORD_IDS
        if any(
            runtime_controls(
                records_by_label["jp"][
                    (BLOCK_ID, record_id)
                ]
            )
        )
    )
    for label, value, expected in (
        (
            "source target",
            source_target,
            EXPECTED_SOURCE_TARGET_SHA256,
        ),
        (
            "current target",
            current_target,
            EXPECTED_CURRENT_TARGET_SHA256,
        ),
        (
            "multilingual context",
            corpus,
            EXPECTED_CONTEXT_CORPUS_SHA256,
        ),
        (
            "gap contract",
            gaps,
            EXPECTED_GAP_CONTRACT_SHA256,
        ),
        (
            "boundary",
            boundary,
            EXPECTED_BOUNDARY_SHA256,
        ),
        (
            "runtime operand",
            operand_evidence,
            EXPECTED_RUNTIME_OPERAND_SHA256,
        ),
        (
            "dynamic record",
            actual_dynamic,
            EXPECTED_DYNAMIC_RECORD_SHA256,
        ),
    ):
        guarded_digest(label, value, expected)
    if (
        actual_dynamic != DYNAMIC_RECORD_IDS
        or any(
            source != EXPECTED_GAPS_BY_RECORD[record_id]
            or current != source
            for record_id, source, current in gaps
        )
        or any(
            controls != EXPECTED_CONTROLS_BY_RECORD[record_id]
            for _, record_id, controls in operand_evidence
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime operand layout drifted"
        )


def assert_base_companions_and_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if (
        sha256_bytes(BASE_PROMOTED.read_bytes())
        != EXPECTED_BASE_PROMOTED_SHA256
    ):
        raise RuntimeError(
            f"segment {SEGMENT} Base promoted policy drifted"
        )
    base_rows = decision_map("base_msggame")
    prefill_rows = {
        str(row["coordinate"]): row
        for row in read_jsonl(PREFILL)
    }
    base_source_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_current_records = ENGINE.archive_records(
        prepared.resources["base_msggame"].current_archive
    )
    base_evidence: list[tuple[Any, ...]] = []
    companion_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_prefill: set[str] = set()
    seen_target: set[str] = set()
    seen_boundary: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        base_record_id = BASE_RECORD_MAPPING[record_id]
        pk_source = records_by_label["jp"][(BLOCK_ID, record_id)]
        base_source = base_source_records[
            (BLOCK_ID, base_record_id)
        ]
        pk_source_literals = literal_texts(
            records_by_label["jp"],
            (BLOCK_ID, record_id),
        )
        base_source_literals = literal_texts(
            base_source_records,
            (BLOCK_ID, base_record_id),
        )
        base_current_literals = literal_texts(
            base_current_records,
            (BLOCK_ID, base_record_id),
        )
        source_relation = (
            "orthographic_variant_same_meaning"
            if record_id == 3395
            else "literal_exact"
        )
        if (
            record_id != 3395
            and pk_source_literals != base_source_literals
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base source mapping drifted: "
                f"{record_id}"
            )
        if (
            record_id == 3395
            and (
                len(pk_source_literals) != 1
                or len(base_source_literals) != 1
                or pk_source_literals == base_source_literals
            )
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base source variant drifted"
            )
        base_evidence.append(
            (
                record_id,
                base_record_id,
                source_relation,
                sha256_bytes(pk_source.data),
                sha256_bytes(base_source.data),
                pk_source_literals,
                base_source_literals,
                base_current_literals,
            )
        )
        owners: list[str] = []
        translations: list[str] = []
        for literal_id in range(len(pk_source_literals)):
            coordinate = f"6:{record_id}:{literal_id}"
            base_coordinate = (
                f"6:{base_record_id}:{literal_id}"
            )
            base_row = base_rows.get(base_coordinate)
            if base_row is None:
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base decision: "
                    f"{base_coordinate}"
                )
            expected = str(base_row["translation"])
            if coordinate == "6:3402:0":
                expected += " "
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
            elif coordinate in PREFILL_COMPANION_COORDINATES:
                row = prefill_rows.get(coordinate)
                if row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                actual = str(row["translation"])
                owner = "prefill"
                seen_prefill.add(coordinate)
                companion_evidence.append(
                    (
                        coordinate,
                        base_coordinate,
                        actual,
                        str(row["source_record_raw_sha256"]),
                        str(row["current_ko_utf16le_sha256"]),
                    )
                )
            elif coordinate == RIGHT_BOUNDARY_COMPANION:
                actual = literal_texts(
                    records_by_label["current"],
                    (BLOCK_ID, record_id),
                )[literal_id]
                owner = "right_boundary_current"
                seen_boundary.add(coordinate)
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
        assembly_evidence.append(
            (
                record_id,
                base_record_id,
                tuple(owners),
                tuple(translations),
                runtime_controls(pk_source),
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
        or seen_boundary != {RIGHT_BOUNDARY_COMPANION}
    ):
        raise RuntimeError(
            f"segment {SEGMENT} assembly ownership drifted"
        )
    guarded_digest(
        "Base context",
        tuple(base_evidence),
        EXPECTED_BASE_CONTEXT_SHA256,
    )
    guarded_digest(
        "prefill companion",
        tuple(companion_evidence),
        EXPECTED_PREFILL_COMPANION_SHA256,
    )
    guarded_digest(
        "assembly policy",
        tuple(assembly_evidence),
        EXPECTED_ASSEMBLY_POLICY_SHA256,
    )


def runtime_category(record_id: int) -> str:
    return {
        3393: "dismissal_protest_shocked",
        3394: "dismissal_regret_formal",
        3395: "dismissal_future_warning",
        3398: "succession_young_male",
        3399: "succession_rough_male",
        3400: "succession_archaic_formal",
        3401: "succession_warrior_formal",
        3402: "succession_lifelong_service",
        3403: "succession_name_burden",
        3404: "succession_gratitude_formal",
        3405: "succession_wisdom_and_valor",
        3406: "succession_honor_repayment",
        3407: "succession_elder_acknowledgement",
        3408: "succession_incredulous_retainer",
        3409: "succession_ambitious_assurance",
    }[record_id]


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
    terminology_policy = (
        ("clan_head", "당주"),
        ("domain_lord", "다이묘"),
        ("martial_valor", "무용"),
        ("realm", "천하"),
        ("house", "가문"),
        ("strategy_and_valor", "지략과 용맹"),
        ("duty", "소임"),
        ("honor", "영예"),
        ("prosperity", "번영"),
        ("favor", "은혜"),
        ("formal_archaic_register", "사옵"),
    )
    guarded_digest(
        "terminology policy",
        terminology_policy,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    runtime_categories = tuple(
        (
            record_id,
            runtime_category(record_id),
            "runtime_fragment_pending",
            "pending",
            "runtime_pending",
            False,
        )
        for record_id in TARGET_RECORD_IDS
    )
    guarded_digest(
        "runtime category",
        runtime_categories,
        EXPECTED_RUNTIME_CATEGORY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES != set(TARGET_COORDINATES)
        or STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(
            SCRIPT.read_text(encoding="utf-8")
        )
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
    patch_common_globals()
    return COMMON.build_candidate(prepared, records_by_label)


def runtime_control_evidence(
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
        source_controls
        != EXPECTED_CONTROLS_BY_RECORD[record_id]
        or current_controls != source_controls
    ):
        raise RuntimeError(
            f"segment {SEGMENT} dynamic controls drifted"
        )
    return {
        "runtime_category": runtime_category(record_id),
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
        "complete_record_assembly_reviewed": True,
        "prefill_companions_reviewed": True,
        "right_boundary_companion_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "base_wording_contextually_adapted":
        record_id == 3402,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_semantic_donor_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
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
    patch_common_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records_by_label = context_records(prepared)
    assert_context_contracts(records_by_label)
    assert_base_companions_and_assembly(
        prepared,
        records_by_label,
    )
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
                "scope_classification":
                "runtime_fragment_pending",
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
                "right_boundary_companion_reviewed": True,
                "speaker_register_reviewed": True,
                "historical_terminology_reviewed": True,
                "protected_outer_whitespace_preserved": True,
                "base_wording_contextually_adapted":
                coordinate == "6:3402:0",
                "base_context_reference_coordinate":
                BASE_CONTEXT_REFERENCES[coordinate],
                "base_context_is_automatic_reuse": False,
                "base_runtime_state_inherited": False,
                "line_count_before":
                current_text.count("\n") + 1,
                "line_count_after":
                TRANSLATIONS[coordinate].count("\n") + 1,
                "line_count_preserved": True,
                "runtime_assembly_evidence":
                runtime_control_evidence(
                    records_by_label,
                    record_id,
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
    patch_common_globals()
    COMMON.assert_tamper_rejection(
        prepared,
        rows,
        candidate,
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
    steam_path = prepared.resources["pk_msggame"].current_path
    steam_before = sha256_bytes(steam_path.read_bytes())
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
        len(rows) != 30
        or len(validated) != 30
        or counts
        != Counter({"runtime_fragment_pending": 30})
        or any(
            row["semantic_review"] != "approved"
            or row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
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
    steam_after = sha256_bytes(steam_path.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(
            f"segment {SEGMENT} wrote to Steam input"
        )
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B035_S1117",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals": [
                    QUEUE_START,
                    QUEUE_STOP - 1,
                ],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "exact_reuse_prefill_count": 37,
                "base_semantic_reference_count": len(rows),
                "prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "right_boundary_companion_count": 1,
                "optional_neighbors_present":
                list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(
                    OUTPUT.read_bytes()
                ),
                "builder_sha256": sha256_bytes(
                    SCRIPT.read_bytes()
                ),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_new_outputs_only": True,
                "base_semantics_pinned": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "right_boundary_companion_guarded": True,
                "prefill_companions_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "direct_calls_and_tokens_guarded": True,
                "protected_outer_whitespace_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
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
